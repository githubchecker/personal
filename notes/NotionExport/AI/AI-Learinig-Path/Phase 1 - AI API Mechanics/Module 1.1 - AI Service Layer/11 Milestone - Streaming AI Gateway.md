# 11 — Milestone: Streaming AI Gateway

> Phase 1 · Module 1.1 · Capstone project · ties together lessons 01–09

## 🗺️ What you're building

A **production FastAPI AI gateway**: it receives a chat request, **streams the LLM reply via SSE**,
**enforces a per-user rate limit**, and **logs token usage per user**. This is the Road Map's Module
1.1 milestone, and it exercises the whole module:

- **FastAPI + Pydantic** (lesson 01) — the typed `/chat` endpoint.
- **Dependency injection** (lesson 02) — inject the LLM client + the current user.
- **Error handling** (lesson 03) — clean failures when the provider is slow/down.
- **SSE streaming** (lesson 04) — token-by-token responses.
- **Auth** (lesson 06) — identify the user (API key).
- **Config + lifespan + background tasks** (lesson 07) — load the client once; log usage after responding.
- **Docker** (lesson 09) — ship it.

## 🎯 The spec

1. `POST /chat` accepts a validated request and **streams** the model's reply as Server-Sent Events.
2. Each caller is **identified** (API key) and **rate-limited per user**.
3. **Token usage is logged per user** *after* the response (a background task), never blocking the reply.
4. Provider failures return clean errors; the model client is loaded **once** at startup.

## ⚙️ Scaffold (fill in the provider call)

```python
# pip install "fastapi[standard]" openai slowapi
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import AsyncOpenAI

# --- lifespan: load the client ONCE (lesson 07) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = AsyncOpenAI()
    yield

limiter = Limiter(key_func=lambda r: r.headers.get("x-api-key", get_remote_address(r)))  # per-user key
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

class ChatRequest(BaseModel):                  # typed input (lesson 01)
    message: str

def current_user(x_api_key: str = Header()) -> str:      # auth (lesson 06)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="missing API key")
    return x_api_key                            # the "user" id for limits + logging

def log_usage(user: str, tokens: int):          # runs AFTER the response (lesson 07)
    ...                                         # write to your usage store

@app.post("/chat")
@limiter.limit("20/minute")                      # per-user rate limit (lesson 06/10)
async def chat(request: Request, body: ChatRequest,
               bg: BackgroundTasks, user: str = Depends(current_user)):

    async def event_stream():
        total = 0
        try:
            stream = await request.app.state.llm.responses.create(   # lesson 04 + Module 1.2
                model="gpt-4o-mini", input=body.message, stream=True)
            async for event in stream:
                # pull the text delta out of each event and forward it as SSE:
                text = getattr(event, "delta", "")
                if text:
                    total += 1
                    yield f"data: {text}\n\n"
        except Exception:
            yield 'data: {"error": "provider unavailable"}\n\n'      # clean failure (lesson 03)
        finally:
            bg.add_task(log_usage, user, total)                      # log usage per user, after streaming

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "ok"}
```

…then add the **Dockerfile** from lesson 09 to ship it.

## ✅ Success criteria

- [ ] `/chat` **streams** tokens (test with `curl -N`), not one blob at the end.
- [ ] A caller over **20/min** gets a `429`; different API keys are limited **independently**.
- [ ] **Token usage is recorded per user** and does **not** delay the response (background task).
- [ ] The client is built **once** (lifespan); provider errors return a clean message, not a stack trace.
- [ ] Builds and runs in **Docker** with a working `/health` check.

## 🚀 Stretch (toward the Phase 1 capstone)

- Swap the single provider for the **multi-provider router** from the Module 1.2 milestone (failover).
- Add **structured-output** validation / tools from Module 1.3.
- Persist usage to a real store and expose a `/usage` endpoint.

## 🛑 STOP — Self-Check

Why log the token usage in a **`BackgroundTasks`** task in the `finally` block rather than inside the
streaming loop or before returning the response?

<details><summary>Answer</summary>

Because usage logging is **not something the user should wait for**. Doing it inside the stream loop
would add work between tokens (slower streaming), and doing it before returning would delay the reply.
Putting it in a **background task** in `finally` means it runs **after the full response has streamed**
(and even if the stream errors), so the user gets their tokens at full speed and the usage write
happens off the critical path — exactly the lesson-07 pattern for non-urgent post-response work.
</details>

---
🎉 **Module 1.1 fully complete** (lessons 01–10 + this milestone). This gateway is the backbone you'll
extend with multi-provider routing (Module 1.2 milestone) and prompting (Module 1.3) in the Phase 1
capstone.
