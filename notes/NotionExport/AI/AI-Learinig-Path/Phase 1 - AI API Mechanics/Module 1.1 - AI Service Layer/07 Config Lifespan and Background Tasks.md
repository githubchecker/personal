# 07 — Config, Lifespan & Background Tasks

> Phase 1 · Module 1.1 · Lesson 7 · `[SHOULD — app setup & lifecycle]`

## 🗺️ Stage 0 — Concept Map

Three pieces of "app plumbing" every real AI service needs: **load configuration/secrets** (without
hardcoding keys), **load the model/client once when the app starts** (not on every request), and
**do slow follow-up work after the response is sent**. They build on Phase 0.1 Pydantic Settings
(lesson 13) and [02 Dependency Injection](02%20Dependency%20Injection.md).

## 🔑 New Terms (plain English)

- **Settings** — typed configuration (model name, keys, limits) loaded from the environment via
  **`pydantic-settings`** (`BaseSettings`).
- **Environment variable / `.env`** — values supplied *outside* the code (e.g. `OPENAI_API_KEY`);
  a `.env` file holds them in development.
- **Lifespan** — a startup/shutdown hook: run code **once when the app boots** and **once when it
  stops**.
- **`BackgroundTasks`** — FastAPI's way to run a function **after** the response is returned
  (fire-and-forget — kick it off and don't wait for it).
- **`SecretStr`** — a Pydantic type that hides a secret's value in logs and debug printouts.
- **`@app.on_event("startup")`** — the older (deprecated) startup hook; `lifespan` replaces it.
- **Task queue (Celery/RQ/arq)** — durable background-job systems for long/retryable work.

## 🎈 Stage 1 — The Simple Idea (analogy: opening a shop)

Running an AI service is like opening a shop each morning. You **unlock the doors and warm up the
till once at opening** (lifespan — load the model/client), you read prices from a **config sheet**
(settings — not scribbled in the code), and when a customer leaves you say *"we'll post your receipt
later"* (background task — log it after responding).

**The "Aha!":** expensive setup (loading a model, opening a client) happens **once at startup via
lifespan**, config comes from the **environment**, and non-urgent work runs **after** the response.

**💢 The old/painful way** — reading `os.environ[...]` scattered across the code with no validation (a
missing var blows up mid-request), and opening the model client on every call. Typed settings,
`lifespan`, and background tasks fix each of those.

## ⚙️ Stage 2 — How It Actually Works

### 7.1 Settings from the environment (never hardcode secrets)

```python
# pip install pydantic-settings
from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")   # read a .env file in dev
    openai_api_key: SecretStr            # SecretStr -> value hidden in logs/printouts
    model: str = "gpt-4o-mini"           # has a default -> optional
    max_tokens: int = 512                # typed + validated (a bad value fails at startup)

@lru_cache                               # build once, reuse (inject via Depends(get_settings), lesson 02)
def get_settings() -> Settings:
    return Settings()                    # missing required key -> clear ValidationError, fail fast
```

**Precedence:** a real **environment variable wins over** the `.env` file — so dev uses `.env`, and
production sets real env vars (containers) with no file. Read a secret with `.get_secret_value()`.

**Where do the values come from? — `.env` vs real env vars vs a secrets manager (pick per environment):**
- **`.env` file** — a local file of `KEY=value` lines.
  - **Key features:** easy local dev; one file; kept out of git.
  - **✅ Use when:** development on your own machine.
  - **🚫 Avoid when → use real env vars:** production — a file full of secrets on a server is a risk.
  - **⚠️ Gotcha:** add `.env` to `.gitignore`, or you'll commit your keys.
- **Real environment variables** — set by the OS / container, no file.
  - **Key features:** the production standard; nothing on disk; set per deployment.
  - **✅ Use when:** production containers (Docker / Kubernetes), CI.
  - **🚫 Avoid when → use a secrets manager:** highly sensitive keys that need rotation and an audit trail.
  - **⚠️ Gotcha:** visible to anything in the process — never print the whole environment to logs.
- **Secrets manager** (Vault, Azure Key Vault, AWS Secrets Manager) — a dedicated secret store.
  - **Key features:** central storage, access control, automatic rotation, an audit trail.
  - **✅ Use when:** production with sensitive keys, compliance needs, or many services sharing secrets.
  - **🚫 Avoid when → use plain env vars:** a small app where env vars are already enough.
  - **⚠️ Gotcha:** adds a fetch-at-startup step — handle the manager being briefly unreachable.

### 7.2 Lifespan — load the model/client ONCE at startup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup: runs ONCE before the app serves requests ---
    app.state.llm = build_llm_client(get_settings())   # an OpenAI client / embedding model
    yield                                              # app serves requests here
    # --- shutdown: runs ONCE when the app stops ---
    await app.state.llm.aclose()                       # cleanup (close connections, free the model)

app = FastAPI(lifespan=lifespan)

@app.get("/chat")
async def chat():
    client = app.state.llm        # reuse the one client — not rebuilt per request
    ...
```

This matters most for AI: loading an embedding model or opening a client is slow/heavy — do it
**once**, not per request. Everything before `yield` is startup; everything after is shutdown.

> **Variation — the deprecated `@app.on_event`:** older code uses `@app.on_event("startup")` /
> `("shutdown")`. It still works but is **deprecated** — use `lifespan` in new code (and recognise
> the old form when you see it).

### 7.3 Background tasks — work after the response

```python
from fastapi import BackgroundTasks

def record_usage(user: str, tokens: int):
    ...                                  # write to a log/db (slow, not urgent)

@app.post("/chat")
async def chat(background_tasks: BackgroundTasks):
    reply = "..."                        # do the real work
    background_tasks.add_task(record_usage, user="ada", tokens=128)  # runs AFTER responding
    return {"reply": reply}              # user gets the answer immediately
```

Great for **token/cost logging**, notifications, cache writes — anything the user shouldn't wait for.

**Know the limits:** `BackgroundTasks` runs **in the same process**, **isn't durable** (a worker
restart loses it), and has **no retries**. So pick by the job:
- **`BackgroundTasks`** (built in)
  - **Key features:** zero setup; runs in-process right after the response is sent.
  - **✅ Use when:** short, best-effort work — log usage, send a notification, write a cache entry.
  - **🚫 Avoid when → use a task queue:** the job is long, must not be lost, or needs retries.
  - **⚠️ Gotcha:** a restart loses queued tasks and there are **no retries** — best-effort only.
- **Task queue (Celery / RQ / arq)**
  - **Key features:** durable (survives restarts), retryable, runs in separate worker processes.
  - **✅ Use when:** long or important jobs — batch processing, a slow pipeline, anything you can't lose.
  - **🚫 Avoid when → use `BackgroundTasks`:** a quick log write — a full queue is overkill.
  - **⚠️ Gotcha:** extra moving parts to run and monitor (a broker like Redis/RabbitMQ + workers). (Phase 4.)

> 🔬 **Under the hood:** `pydantic-settings` loads and **validates** env vars once into a typed object
> at startup, so bad config fails fast instead of mid-request. `lifespan` runs startup code *before*
> the server accepts traffic and shutdown code *after* the last request finishes. `BackgroundTasks`
> schedules work to run **after** the response is sent, on the same event loop.

## 🚀 Stage 3 — In Practice / Why It Matters

In the Phase 1 gateway you'll load the LLM/embedding client in **lifespan**, pull the model name and
keys from **settings**, and log **token usage** in a **background task**. This is the standard shape
of a production AI service — and keeps secrets out of code and slow setup off the request path.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Config source** | `.env` file vs real env vars vs secrets manager | **`.env`** in dev · **real env vars** in prod containers · a **secrets manager** (Vault, Azure Key Vault) for production secrets |
| **Startup hook** | `lifespan` vs `@app.on_event` (deprecated) | always **`lifespan`** in new code; recognise `on_event` in older code |
| **After-response work** | `BackgroundTasks` vs task queue (Celery/RQ/arq) | **`BackgroundTasks`** for quick, in-process, best-effort (logging) · a **queue** for long/durable/retryable jobs (Phase 4) |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Every request is slow / reloads the model | Building the client/model inside the handler | Load it once in **lifespan**, store on `app.state` |
| `ValidationError` on startup | Required setting (e.g. API key) not set | Set the env var / `.env`; that's the point — fail fast |
| Secret committed to git | Hardcoded key | Use `BaseSettings` + env vars; add `.env` to `.gitignore` |
| Background task blocks the response | Put slow work *before* returning | Add it via `background_tasks.add_task(...)` (runs after) |
| Long job times out as a background task | Background tasks aren't a queue | Use Celery/RQ for long/durable jobs (Phase 4) |

## 📌 Quick Reference

```python
class Settings(BaseSettings):                 # pip install pydantic-settings
    model_config = SettingsConfigDict(env_file=".env")
    openai_api_key: str

@asynccontextmanager
async def lifespan(app):
    app.state.llm = build_client()            # startup (once)
    yield
    await app.state.llm.aclose()              # shutdown
app = FastAPI(lifespan=lifespan)

@app.post("/x")
async def x(bg: BackgroundTasks):
    bg.add_task(log_usage, tokens=10)         # runs AFTER the response
```
- **Settings** = config from env (`SecretStr` for keys; env vars override `.env`) · **lifespan** = load model/client once ·
  **`BackgroundTasks`** = short after-response work; **Celery/RQ/arq** = long/durable jobs.

> 🎯 **Interview angle:** "Where do you load the embedding model in a FastAPI service?" → in a
> **lifespan** handler at startup, stored on `app.state`, so it's loaded once and reused — never
> per request.

## 🛑 STOP — Self-Check

You're loading a 400 MB embedding model. Where should that load happen, and why **not** inside the
endpoint function?

<details><summary>Answer</summary>

Load it **once at startup in a `lifespan` handler** (store it on `app.state`). If you loaded it
**inside the endpoint**, it would reload on **every request** — adding hundreds of milliseconds (or
seconds) and huge repeated memory churn to each call. Lifespan runs the expensive setup a single
time before any request is served, and every request reuses the already-loaded model.
</details>
