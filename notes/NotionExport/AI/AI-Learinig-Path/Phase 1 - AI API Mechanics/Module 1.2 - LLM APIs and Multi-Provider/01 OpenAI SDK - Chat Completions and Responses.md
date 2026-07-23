# 01 — OpenAI SDK: Chat Completions + Responses API

> Phase 1 · Module 1.2 · Lesson 1 · `[JD VERIFIED — 90%]`

## 🗺️ Stage 0 — Concept Map

Module 1.1 gave you an API *shell* (FastAPI). Now you make it actually **talk to an LLM**. The
**OpenAI Python SDK** is named in ~90% of AI-engineer job posts, so it's where we start. It exposes
two ways to call a model: the newer **Responses API** (now the primary one) and the classic **Chat
Completions API** (still fully supported). This builds on Phase 0 async + the error handling
([03](../Module%201.1%20-%20AI%20Service%20Layer/03%20Error%20Handling%20and%20Resilience.md)) and
streaming ([04](../Module%201.1%20-%20AI%20Service%20Layer/04%20Streaming%20with%20SSE.md)) from
Module 1.1.

> 🔑 **Model names change fast.** Names like `gpt-5.5` / `gpt-4o` below are the current examples from
> OpenAI's docs (2026) — always check the provider's live model list; treat the names as illustrative.

## 🔑 New Terms (plain English)

- **SDK (Software Development Kit)** — the official Python library that wraps the provider's HTTP API.
- **Responses API** — OpenAI's current primary text-generation call: `client.responses.create(...)`.
- **Chat Completions API** — the older, still-supported call: `client.chat.completions.create(...)`.
- **Message / role** — a turn in the conversation; roles are `system`/`developer` (instructions),
  `user` (you), `assistant` (the model).
- **Token** — a chunk of text (~¾ of a word) the model reads/writes; you're billed per token.
- **`AsyncOpenAI`** — the async version of the client, for `await` inside FastAPI.
- **`max_output_tokens` / `max_tokens`** — the cap on the reply's length (your main cost/latency knob).
- **`usage`** — token counts on the response (`input`/`output`/`total`) for cost tracking.
- **Conversation state** — letting the API remember a thread via `previous_response_id` (Responses API).
- **Batch API** — asynchronous bulk processing at ~50% cost for non-urgent jobs.

## 🎈 Stage 1 — The Simple Idea (analogy: a phone call to an expert)

Calling an LLM is like **phoning an expert**: you dial (create a client), say your message (the
prompt), and get a spoken reply (the text). The **Responses API** is the new streamlined phone; **Chat
Completions** is the classic line that still works perfectly. Either way, you send text and get text
back — the SDK handles all the HTTP plumbing.

**The "Aha!":** an LLM call is *just a function call* that returns text. Everything else
(streaming, tools, vision) is an option on top of that one call.

**💢 Without the SDK (the old/painful way)** — you'd hand-build the HTTP call: set the auth header,
POST JSON to the REST endpoint, dig through the raw JSON reply, and write your own retry/timeout code:

```python
import requests
r = requests.post("https://api.openai.com/v1/responses",
                  headers={"Authorization": f"Bearer {key}"},
                  json={"model": "gpt-5.5", "input": "hi"})
text = r.json()["output"][0]["content"][0]["text"]   # fragile: dig through raw JSON by hand
```

The SDK gives you auth, serialisation (turning your Python objects into JSON to send), **typed**
parsing, retries, and streaming for free.

## ⚙️ Stage 2 — How It Actually Works

### 1.1 Install & set the key (never hardcode it)

```powershell
pip install openai python-dotenv
```

Put the key in a `.env` file (the settings pattern from Module 1.1 lesson 07) — **never in code**:

```
OPENAI_API_KEY=sk-...
```

### 1.2 The Responses API — features, syntax, reading the result

**Key features:** one call for text generation, with optional **multimodal input** (text + images),
**tools** (lesson 06), **structured outputs** (Module 1.3), **streaming**, and **built-in
conversation state** (continue a thread without resending it).

**Syntax — the parameters that matter:**

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])   # or omit api_key — it's the default

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a concise assistant.",      # system-level guidance (persona / rules)
    input="Explain what an API is in one sentence.",  # a str, OR a list of typed content (see below)
    temperature=0.7,         # 0 = deterministic/repeatable … higher = more creative (range 0.0–2.0)
    max_output_tokens=300,   # cap the reply length — your main cost & latency control
    top_p=1.0,               # nucleus sampling (an alternate randomness control); tune temperature OR top_p (see 0.0.5)
)
print(response.output_text)  # the convenience accessor: the final text, ready to use
```

**Reading the result — three levels:**
- `response.output_text` — the text (what you use ~90% of the time).
- `response.output` — the structured list of output items (text, tool calls) for advanced handling.
- `response.usage` — token counts for cost tracking (see 1.6).

**Key feature — multimodal (vision) input:** pass a list of typed content instead of a string:

```python
response = client.responses.create(
    model="gpt-5.5",
    input=[{"role": "user", "content": [
        {"type": "input_text",  "text": "What's in this image?"},
        {"type": "input_image", "image_url": "https://…/cat.jpg"},   # or a base64 data: URL
    ]}],
)
```

**Key feature — conversation state:** continue a thread *without* resending the history by passing the
previous response's id:

```python
follow_up = client.responses.create(
    model="gpt-5.5",
    previous_response_id=response.id,   # the model "remembers" the prior turn — no manual history
    input="Now explain it to a five-year-old.",
)
```

### 1.3 The Chat Completions API — features, syntax, response shape

Still fully supported, and the **format other providers copy** (lessons 02–05). Same idea,
`messages`-based; *you* manage the conversation history.

**Syntax — the parameters that matter:**

```python
completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[                                   # a LIST of role/content turns you maintain
        {"role": "developer", "content": "You are a concise assistant."},  # "developer" = former "system"
        {"role": "user", "content": "Explain what an API is in one sentence."},
    ],
    temperature=0.7,
    max_tokens=300,          # NOTE: `max_tokens` here (Responses uses `max_output_tokens`)
    top_p=1.0,
    stop=["\n\n"],           # optional stop sequence(s): generation halts if one is produced
    seed=42,                 # best-effort reproducibility for identical inputs
    response_format={"type": "json_object"},   # JSON mode (full structured outputs in Module 1.3)
)
msg = completion.choices[0].message
print(msg.content)                              # the text
print(completion.choices[0].finish_reason)      # why it stopped: "stop" | "length" | "tool_calls"
```

**Response shape:** a list of `choices` (usually one), each with a `message` (`.content`, `.role`) and
a `finish_reason`. If `finish_reason == "length"`, you hit `max_tokens` — raise it.

**Which one? — Responses API vs Chat Completions (the core choice):**
- **Responses API** (`client.responses.create`)
  - **✅ Use when:** new OpenAI code — you want the simplest `output_text`, built-in conversation state, tools, or multimodal input.
  - **🚫 Avoid when → use Chat Completions:** you need code that ports across providers, or you're following the many tutorials/codebases built on `messages`.
  - **⚠️ Gotcha:** it's OpenAI-specific — other providers don't implement it, so a multi-provider layer (LiteLLM, lesson 04) targets Chat Completions instead.
- **Chat Completions** (`client.chat.completions.create`)
  - **✅ Use when:** you want the portable, de-facto-standard format other providers mimic, or you're matching existing examples.
  - **🚫 Avoid when → use Responses:** you want OpenAI's newest conveniences (thread memory via `previous_response_id`, the simplest output accessor).
  - **⚠️ Gotcha:** *you* manage the message history yourself, and the length cap is `max_tokens` here (Responses uses `max_output_tokens`).

### 1.4 Async (what you'll actually use inside FastAPI)

```python
from openai import AsyncOpenAI
client = AsyncOpenAI()

async def ask(prompt: str) -> str:
    resp = await client.responses.create(model="gpt-5.5", input=prompt)  # await the slow call
    return resp.output_text
```

`async` lets one FastAPI worker handle many slow LLM calls at once (Phase 0 async + Module 1.1).

### 1.5 Streaming — extracting the text deltas (pair with SSE)

`stream=True` yields **events** as the model writes. The real skill is pulling the **text delta** (the
new slice of text in each event) out and forwarding it (as SSE — Module 1.1 lesson 04), not just
printing the raw event:

```python
stream = client.responses.create(model="gpt-5.5", input="Write a haiku.", stream=True)
for event in stream:
    if event.type == "response.output_text.delta":   # the event carrying new text
        print(event.delta, end="", flush=True)        # forward as: f"data: {event.delta}\n\n"
```

**Chat Completions streams a different shape** — the text is at `chunk.choices[0].delta.content`:

```python
for chunk in client.chat.completions.create(model="gpt-5.5", messages=msgs, stream=True):
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)
```

### 1.6 Token usage tracking (cost control)

Every (non-streaming) response reports token counts — log them to track spend per user/call:

```python
resp = client.responses.create(model="gpt-5.5", input="hi")
u = resp.usage
print(u.input_tokens, u.output_tokens, u.total_tokens)
# Chat Completions names them: usage.prompt_tokens / completion_tokens / total_tokens
```

This is exactly what the Module 1.1 gateway logs per user. (To get usage *while streaming* on Chat
Completions, add `stream_options={"include_usage": True}`.)

### 1.7 Batch API awareness `[awareness]`

For **non-urgent, bulk** work (e.g. classify 100k records overnight), the **Batch API** runs jobs
asynchronously within ~24h at **~50% lower cost**. Use it when latency doesn't matter and volume is
high; use the normal call for anything interactive.

### 1.8 Built-in resilience (the SDK does a lot for you)

The SDK **auto-retries** transient failures (429, ≥500, timeouts) **twice** with backoff, and raises
typed errors you already know how to handle (Module 1.1 lesson 03):

```python
import openai
try:
    resp = client.responses.create(model="gpt-5.5", input="hi", timeout=20)
except openai.RateLimitError:      # 429 — back off / fall back
    ...
except openai.APITimeoutError:     # too slow
    ...
except openai.APIStatusError as e: # any other 4xx/5xx
    print(e.status_code)
```

> 🔬 **Under the hood:** the SDK serialises (turns into JSON) your params, POSTs them to the endpoint
> over **httpx**, and parses the reply into **typed Pydantic objects** (that's why `.output_text` and editor
> autocomplete work). `stream=True` switches the response to **SSE** and yields each event as it
> arrives; `AsyncOpenAI` does the same over `await`. The built-in retry just re-issues that POST on a
> `429`/timeout before raising.

## 🚀 Stage 3 — In Practice / Why It Matters

This `client.responses.create(...)` call is the line that goes **inside your FastAPI endpoint**: take
the validated request body (Module 1.1 lesson 01), call the model, stream the reply as SSE, and wrap
it in error handling. Everything in Phase 1 from here is variations on this one call — different
provider (02–05), tools (06), or structure (Module 1.3).

## ⚖️ Variations & When to Use

| Choice | Use | When |
| --- | --- | --- |
| **Responses API** | new OpenAI code | you want tools, conversation state, multimodal, simplest `output_text` |
| **Chat Completions** | portability / examples | other providers mimic it; most tutorials & codebases use it |
| **sync vs `AsyncOpenAI`** | **async** | always inside FastAPI (handle many slow calls at once) |
| **`stream=True` vs not** | **stream** | user-facing chat (low time-to-first-token); **off** for JSON you parse whole / batch |
| **normal vs Batch API** | **Batch** | huge, non-urgent volume (~50% cheaper, ~24h turnaround) |

- **`temperature` vs `top_p`:** tune **one**, not both — `temperature` for everyday use, `top_p` for fine nucleus control (0.0.5).

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `AuthenticationError` (401) | Key missing/wrong | Set `OPENAI_API_KEY` in `.env`; load via settings |
| `NotFoundError` (404) on model | Wrong/old model name | Use a current model id from OpenAI's list |
| `RateLimitError` (429) | Too many requests / quota | Back off, retry, or fall back (lesson 04 + 1.1 L03) |
| Coroutine (an async call's result) never runs | Used `AsyncOpenAI` without `await` | `await client.responses.create(...)` |
| Key leaked in git | Hardcoded the key | Use `.env` + settings (Module 1.1 lesson 07) |

## 📌 Quick Reference

```python
from openai import OpenAI, AsyncOpenAI
client = OpenAI()

# Responses API (primary):
r = client.responses.create(model="gpt-5.5", instructions="...", input="...",
                            temperature=0.7, max_output_tokens=300)
r.output_text          # text  ·  r.usage.total_tokens  ·  r.id (-> previous_response_id for state)

# Chat Completions (classic):
c = client.chat.completions.create(model="gpt-5.5", messages=[{"role":"user","content":"..."}],
                                   temperature=0.7, max_tokens=300)
c.choices[0].message.content    # text  ·  .finish_reason  ·  c.usage.total_tokens

# async: await AsyncOpenAI()…   ·   stream: stream=True (read .delta)   ·   bulk & cheap: Batch API
```
- **Responses** = `input`/`instructions` → `output_text` (+ state, multimodal). **Chat Completions** = `messages` → `choices[0].message.content`.
- Params that matter: `temperature` *or* `top_p`, `max_output_tokens`/`max_tokens` (cost), `stream`, `response_format`; track `usage`. Key in `.env`.

> 🎯 **Interview angle:** "Responses API vs Chat Completions?" → Responses is OpenAI's current
> primary API (simpler `input`/`output_text`, built for tools/state); Chat Completions is the older
> `messages`-based API, still supported and the de-facto format other providers mimic.

## 🛑 STOP — Self-Check

In the Responses API you read `response.output_text`. In Chat Completions, what's the equivalent path
to the model's text, and where do you put the "you are a concise assistant" instruction in each?

<details><summary>Answer</summary>

In **Chat Completions** the text is at **`completion.choices[0].message.content`** (a list of choices,
each with a `message`). The instruction goes in a **message** with role **`developer`** (formerly
`system`) at the start of the `messages` list. In the **Responses API**, the instruction goes in the
top-level **`instructions=`** parameter and the text comes back as **`response.output_text`** — fewer
layers to dig through.
</details>
