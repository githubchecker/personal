# 03 — Error Handling & Resilience

> Phase 1 · Module 1.1 · Lesson 3 · `[MUST — production error handling]`

## 🗺️ Stage 0 — Concept Map

Every real API meets bad input, missing resources, and — uniquely for AI — **slow, flaky, expensive
LLM calls** that time out, get rate-limited, or fail upstream. A production AI service must fail
**cleanly** (a clear error + the right status code, never a stack-trace crash) and **resiliently**
(time out, retry, or fall back). This builds on [01](01%20FastAPI%20Basics%20for%20AI%20Services.md)
(the automatic 422) and [02](02%20Dependency%20Injection.md), and underpins every later provider
call in Module 1.2.

## 🔑 New Terms (plain English)

- **`HTTPException`** — the exception you `raise` to return a proper HTTP error (status + message).
- **Status code** — the 3-digit result of a request: `2xx` ok, `4xx` *caller's* fault, `5xx`
  *server/upstream's* fault.
- **Exception handler** — a function (`@app.exception_handler(...)`) that turns a Python exception
  into a clean JSON error response.
- **Timeout** — giving up on a slow call after N seconds instead of hanging forever.
- **Retry / backoff** — re-attempting a failed call, waiting longer between tries (exponential).
- **Fallback / graceful degradation** — when plan A fails, do plan B (cheaper model, cached answer,
  polite error) instead of crashing.
- **`tenacity`** — a library for declarative retry/backoff policies via a decorator.
- **Jitter** — added randomness in backoff so many clients don't retry in lockstep.
- **Circuit breaker** — after repeated failures, stop calling a provider for a cooldown (fail fast).

## 🎈 Stage 1 — The Simple Idea (analogy: a good receptionist)

A bad receptionist, when something goes wrong, just stares blankly or faints (a 500 crash). A **good
receptionist** says exactly what's wrong and what happens next: *"That room doesn't exist"* (404),
*"You're not on the list"* (401), *"We're swamped, try again in a minute"* (429/503). For AI, the
"phone line to the model" is often busy or slow — the good receptionist **waits a sensible amount,
redials once or twice, and if it's still down, gives you a clear apology** instead of leaving you on
hold forever.

**The "Aha!":** errors are part of the API's *contract*. You **choose** the status code and message
for every failure — and for LLM calls you also decide **how hard to try** before giving up.

**💢 The old/painful way** — with no handling, an unexpected error just **travels up uncaught**: the
client gets a `500` with a raw Python **stack trace** (the error's internal trail — it leaks how your
code works), and a slow provider call hangs the request forever. The patterns below replace that with
clean status codes and bounded waits.

## ⚙️ Stage 2 — How It Actually Works

### 3.1 Raise `HTTPException` for expected errors

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/conversations/{cid}")
async def get_conversation(cid: str):
    convo = lookup(cid)                     # pretend this returns None if not found
    if convo is None:
        # Return a real 404 with a clear message — not a crash, not a 200 with null.
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo
```

### 3.2 The status codes that matter for an AI service

| Code | Meaning | Typical AI cause |
| --- | --- | --- |
| `400` | Bad request | malformed prompt / params |
| `401` / `403` | Not authenticated / not allowed | missing or wrong API key (lesson 06) |
| `404` | Not found | unknown conversation/model id |
| `422` | Validation failed (automatic) | body didn't match the Pydantic model |
| `429` | Too many requests | **provider rate limit**, or your own limit |
| `500` | Unhandled server error | a bug — don't leak details |
| `502` / `503` / `504` | Upstream failed / unavailable / timed out | **the LLM provider** errored or was too slow |

### 3.3 Custom exception handler — map domain errors to clean JSON

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ProviderError(Exception):             # your own error type for "the LLM call failed"
    pass

@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    # One place that turns ANY ProviderError into a consistent 503 response.
    return JSONResponse(status_code=503,
                        content={"error": "AI provider unavailable, please retry shortly"})
```

Now anywhere in your code `raise ProviderError(...)` produces the same tidy 503 — no duplicated
error formatting.

### 3.4 The AI-specific part: timeout + retry + fallback

LLM calls are the flaky, slow, costly part. Wrap them:

```python
import asyncio

async def call_llm_resilient(prompt: str):
    for attempt in range(3):                       # try up to 3 times
        try:
            # give up if the model takes more than 20s (don't hang the request forever)
            return await asyncio.wait_for(call_provider(prompt), timeout=20)
        except asyncio.TimeoutError:
            if attempt == 2:
                raise ProviderError("LLM timed out")     # out of retries -> clean 503
            await asyncio.sleep(2 ** attempt)            # backoff: 1s, 2s, 4s before retrying
```

- **Timeout** so one slow call can't tie up the worker.
- **Retry with backoff** for *transient* failures (a blip, a 429) — but **not** for a 400 (bad input
  won't get better by retrying).
- **Fallback**: on final failure, do plan B instead of crashing — a clear error, a cached answer, a
  cheaper model, or queue it for later (the options are compared below).

**Variation — `tenacity` instead of a manual loop** (you *state* the retry policy and the library runs
it for you, so there's far less hand-written code):

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=10))
async def call_llm(prompt):                 # auto-retries with exponential backoff + JITTER
    return await call_provider(prompt)
```

**Backoff strategy — the waiting pattern between retries (pick one).** *Backoff* just means *how long
you wait before the next try.*

- **Fixed** — wait the **same** gap each time (2s, 2s, 2s).
  - **✅ Use when:** simple scripts, or a provider that recovers in a steady, known time.
  - **🚫 Avoid when → use exponential:** real load — equal short waits keep hammering a struggling provider.
  - **⚠️ Gotcha:** too short a gap behaves like no backoff at all.
- **Exponential** — **double** the wait each try (1s → 2s → 4s). The provider-SDK default.
  - **✅ Use when:** almost always — it backs off a recovering provider quickly.
  - **🚫 Avoid when → add jitter:** many clients retry together and re-sync into waves of load.
  - **⚠️ Gotcha:** cap the longest wait (`max=`) so a user isn't stuck for minutes.
- **Exponential + jitter** — exponential plus a **random** wiggle on each wait, so clients don't all
  retry at the same instant.
  - **✅ Use when:** production with many clients at once — the safest default.
  - **🚫 Avoid when:** rarely — the randomness is almost always helpful, not harmful.
  - **⚠️ Gotcha:** total retry time now varies, so keep an overall request timeout too.

**Fallback strategy — what to do once all retries fail (pick per product need).**

- **Clean error** — return a clear `503` + friendly message.
  - **✅ Use when:** interactive chat, where a made-up answer is worse than no answer.
  - **🚫 Avoid when → use a cheaper model:** you could still give *some* useful answer.
  - **⚠️ Gotcha:** make the message actionable ("try again shortly"), never a raw trace.
- **Cached / previous answer** — serve a recent good answer.
  - **✅ Use when:** the same question repeats and a slightly stale answer is fine.
  - **🚫 Avoid when → clean error:** answers must be fresh or personalised.
  - **⚠️ Gotcha:** flag it as possibly-stale so users aren't misled.
- **Cheaper / smaller model** — fall back to a backup model.
  - **✅ Use when:** any answer beats no answer and a smaller model is "good enough."
  - **🚫 Avoid when → clean error:** quality is critical (legal/medical).
  - **⚠️ Gotcha:** the backup may format its output differently — validate it.
- **Queue for later** — accept the request now, process it when the provider recovers.
  - **✅ Use when:** bulk or non-urgent work (batch jobs, email replies).
  - **🚫 Avoid when → clean error:** a user is waiting live for the answer.
  - **⚠️ Gotcha:** needs a queue plus a way to deliver the result afterwards.

### 3.5 Never leak internals

```python
@app.exception_handler(Exception)               # catch-all for UNEXPECTED bugs
async def unhandled(request: Request, exc: Exception):
    log.exception("unhandled error")            # log the full detail for YOU
    return JSONResponse(status_code=500,
                        content={"error": "internal error"})   # generic message for the USER
```

Log the stack trace server-side; send the user a generic 500. Leaking tracebacks is an **OWASP**
information-disclosure risk.

> 🔬 **Under the hood:** when you `raise HTTPException`, FastAPI's built-in error-catching layer (its
> exception-handling *middleware* — code that wraps every request) catches it and writes a JSON response
> with that status; `@app.exception_handler` registers your own handler for a given exception type. The
> OpenAI/Anthropic SDKs wrap each HTTP call in their own retry loop, so a `429`/timeout is retried
> *before* it ever reaches your `except`.

## 🚀 Stage 3 — In Practice / Why It Matters

In the Phase 1 gateway you'll wrap every provider call (Module 1.2) with a timeout + retry, map
provider failures (OpenAI/Anthropic `RateLimitError`, `APITimeoutError`) to clean `429`/`503`
responses via exception handlers, and return a generic `500` for bugs. This is the difference
between a demo that crashes on the first hiccup and a service that stays up when the model provider
has a bad minute — and it's a guaranteed interview topic.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Retry mechanics** | manual `for` loop vs **`tenacity`** decorator | **tenacity** for real apps (declarative policies); manual loop only for a one-off |
| **Backoff** | fixed vs exponential vs exponential **+ jitter** | **exponential** by default; **+ jitter** under load (avoids synchronized retry storms) |
| **On final failure** | clear error · cached answer · cheaper/smaller model · queue for later | user-facing chat → cheaper model or a clean `503`; bulk/non-urgent → queue & retry later |
| **Provider keeps failing** | keep retrying vs **circuit breaker** | add a **circuit breaker** (stop calling a down provider for a cooldown) so you fail fast instead of piling up timeouts |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Client gets a 500 + stack trace | Let an exception bubble up raw | `raise HTTPException(...)` for expected cases; catch-all handler for the rest |
| Request hangs for minutes | No timeout on the LLM call | `asyncio.wait_for(call, timeout=…)` |
| Retrying a bad prompt forever | Retried a `4xx` (caller error) | Only retry **transient** `429`/`5xx`/timeouts, never `400`/`422` |
| Returned `200` with `null`/empty | Didn't signal the failure | Use the right status (`404`, `503`) so callers can react |
| Secrets/internals leaked in error | Echoed the exception text | Log server-side; return a **generic** message to the user |

## 📌 Quick Reference

```python
raise HTTPException(status_code=404, detail="not found")     # expected error

@app.exception_handler(ProviderError)                        # map a domain error -> clean JSON
async def h(request, exc): return JSONResponse(503, {"error": "..."})

await asyncio.wait_for(call_provider(p), timeout=20)         # don't hang forever
# retry transient (429/5xx/timeout) with backoff; NEVER retry 400/422; fallback on final failure
```
- `4xx` = caller's fault (don't retry) · `5xx`/timeout/`429` = transient (retry/fallback).
- One **exception handler** per error type = consistent responses. Log details; show users generic messages.

> 🎯 **Interview angle:** "How do you make an AI endpoint resilient to a flaky model provider?" →
> timeout each call, retry transient failures (`429`/`5xx`) with exponential backoff, map provider
> errors to clean `429`/`503` via exception handlers, and fall back (cheaper model/cached/clear
> error) on final failure — never hang or leak a stack trace.

## 🛑 STOP — Self-Check

A user sends a perfectly valid prompt, but the LLM provider returns a `429 (rate limited)`. Should
you retry? What if instead the user sent an invalid body and FastAPI raised a `422` — retry that?

<details><summary>Answer</summary>

**Retry the `429`** — it's a **transient** failure (the provider is briefly busy); wait with
exponential backoff and try again a couple of times, then fall back / return a clean `503` if it
keeps failing. **Do not retry the `422`** — that's a **caller error** (the request body is wrong);
retrying sends the same invalid data and will fail identically every time. Rule of thumb: retry
`5xx`/`429`/timeouts (server/transient), never `4xx` like `400`/`422` (caller must fix the request).
</details>
