# 05 — Structure: APIRouter, Middleware & CORS

> Phase 1 · Module 1.1 · Lesson 5 · `[SHOULD — production structure]`

## 🗺️ Stage 0 — Concept Map

As an AI service grows past a couple of endpoints you need **structure**: split routes into files
(**APIRouter**), run shared logic on every request (**middleware** — logging, timing, token
tracking), and let a browser front-end call your API (**CORS**). These three turn the toy app from
[01](01%20FastAPI%20Basics%20for%20AI%20Services.md) into something maintainable and web-callable.

## 🔑 New Terms (plain English)

- **APIRouter** — a mini-FastAPI you define in its own file to group related endpoints, then plug
  into the main app.
- **Middleware** — code that runs on **every** request, *around* your endpoint (before and after).
- **CORS (Cross-Origin Resource Sharing)** — the browser security rule that decides which web pages
  (origins) are allowed to call your API.
- **Origin** — the `scheme://host:port` a request comes from (e.g. `http://localhost:3000`).
- **Preflight** — an automatic `OPTIONS` request the browser sends first to check CORS permission.
- **`BaseHTTPMiddleware`** — the class-based way to write reusable middleware.
- **Built-in middleware** — ready-made middleware like `GZipMiddleware`, `TrustedHostMiddleware`.
- **`allow_credentials`** — CORS flag for sending cookies/auth; can't combine with `allow_origins=["*"]`.

## 🎈 Stage 1 — The Simple Idea (analogy: an office building)

Think of your API as an **office building**:
- **APIRouter** = **departments on separate floors** — "chat" on one floor, "documents" on another —
  instead of cramming everyone into one room.
- **Middleware** = the **security desk in the lobby** everyone passes through on the way in *and* out
  (stamp the time, log the visitor, add a badge).
- **CORS** = the **guest list** saying which outside buildings (web origins) are allowed to call in.

**The "Aha!":** routers organize *your* code, middleware wraps *every* request, and CORS controls
*who from the browser* may call you — three separate concerns, three separate tools.

**💢 The old/painful way** — one giant `main.py` holding every route, plus hand-setting CORS headers on
each response. It grows unmaintainable and the browser *still* blocks your frontend. Routers,
middleware, and `CORSMiddleware` replace all of that cleanly.

## ⚙️ Stage 2 — How It Actually Works

### 2.1 APIRouter — split endpoints into files (and gate a whole feature)

```python
# routers/chat.py — a self-contained group of endpoints
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/chat",                       # every path here starts with /chat
    tags=["chat"],                        # groups them in the /docs page
    dependencies=[Depends(require_api_key)],   # gate EVERY route in this feature (lesson 06)
    responses={503: {"description": "LLM provider unavailable"}},   # shared error doc
)

@router.post("/")                         # becomes POST /chat/
async def chat():
    return {"reply": "..."}
```

```python
# main.py — plug routers into the app
from fastapi import FastAPI
from routers import chat, documents, admin

app = FastAPI()
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(admin.router)
```

A typical layout: a `routers/` package (one file per feature), `models/` (Pydantic), `services/`
(LLM/DB logic) — so each part grows independently. `prefix` adds a common path; `tags` group the docs.

### 2.2 Middleware — run on every request (two forms)

**Function form** (quick):

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)              # run the actual endpoint
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.3f}"
    return response                                  # MUST return the response
```

**Class form** (`BaseHTTPMiddleware`) — reusable/configurable across apps:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ...                                          # same logic, packaged as a class
app.add_middleware(TimingMiddleware)
```

FastAPI also ships **built-in middleware** you just add: `GZipMiddleware` (compress responses),
`TrustedHostMiddleware` (block bad Host headers). **Order matters:** middleware added **last runs
first** (outermost) — add CORS early so it wraps everything. In AI services this is where you **log
requests and tally tokens/cost per call**.

**Which middleware form? (function vs class vs raw ASGI):**
- **Function (`@app.middleware("http")`)**
  - **Key features:** quickest to write; lives right next to the app.
  - **✅ Use when:** a one-off shared concern (timing, a header) in a single app.
  - **🚫 Avoid when → use a class:** you want to reuse it across apps, or make it configurable.
  - **⚠️ Gotcha:** you **must** `return await call_next(request)` — forget it and the request hangs.
- **Class (`BaseHTTPMiddleware`)**
  - **Key features:** packaged and reusable; takes options via `__init__`.
  - **✅ Use when:** shared middleware across services, or it needs configuration.
  - **🚫 Avoid when → use a function:** a trivial one-off — a class is extra ceremony.
  - **⚠️ Gotcha:** `BaseHTTPMiddleware` adds a little overhead; for hot paths consider raw ASGI.
- **Raw ASGI middleware**
  - **Key features:** lowest-level and fastest; full control of the request/response cycle.
  - **✅ Use when:** performance-critical paths, or behaviour `BaseHTTPMiddleware` can't express.
  - **🚫 Avoid when → use function/class:** almost always — raw ASGI is verbose and easy to get wrong.
  - **⚠️ Gotcha:** you handle the ASGI `scope`/`receive`/`send` yourself — no FastAPI conveniences.

### 2.3 Middleware vs a dependency — which for shared, cross-cutting logic?

Both can run *shared* logic that applies across many routes (so-called *cross-cutting* logic), and
they overlap — so choose deliberately:

| Use **middleware** | Use a **dependency** (lesson 02) |
| --- | --- |
| Runs on **every** request, app-wide | Runs on **chosen** routes/routers |
| Logging, timing, GZip, request-id | Auth, rate-limit, per-route needs |
| Can't easily hand a value to the handler | **Injects a value** (the user, a client) |

Rule: **truly global + no value needed → middleware; specific routes or you need the value → dependency.**

### 2.4 CORS — let your web front-end call the API

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],   # EXPLICIT origins in production
    allow_credentials=True,                      # needed for cookies / Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Without this, a browser app calling your API gets **"blocked by CORS policy"** — even though `curl`
works fine (CORS is a *browser* rule, not a server one).

**Origins: an explicit list vs `["*"]` (pick one):**
- **Explicit list** (`["https://app.example.com"]`)
  - **Key features:** names exactly which web pages may call your API.
  - **✅ Use when:** production — and it's **required** when `allow_credentials=True` (cookies/auth).
  - **🚫 Avoid when:** never for production — an explicit list is the safe default.
  - **⚠️ Gotcha:** the origin must match scheme + host + port exactly (`https://app.example.com` ≠ `http://app.example.com`).
- **Wildcard `["*"]`** (allow any origin)
  - **Key features:** lets any web page call the API.
  - **✅ Use when:** a truly public, credential-less API (no cookies, no auth header).
  - **🚫 Avoid when → use an explicit list:** anything sending credentials — the browser forbids `*` with credentials.
  - **⚠️ Gotcha:** `allow_origins=["*"]` **cannot** be combined with `allow_credentials=True`.

> 🔬 **Under the hood:** an `APIRouter` is a mini-app whose routes are merged into the main routing
> table at `include_router(...)` (with its prefix applied). **Middleware** wraps every request like an
> onion — each layer runs code before *and* after your handler. `CORSMiddleware` answers the browser's
> preflight `OPTIONS` request and injects the `Access-Control-*` headers that unblock the frontend.

## 🚀 Stage 3 — In Practice / Why It Matters

Real AI gateways have a **router per feature** (chat, documents, admin), **middleware** that logs
every request and tallies token usage (you'll do this in the milestone), and **CORS** configured for
the product's web UI. This is the difference between a one-file demo and a service a team can grow.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Cross-cutting logic** | middleware vs dependency | **middleware** for every request (logging/timing/GZip) · **dependency** for specific routes or when you need a value (auth, rate-limit) |
| **Middleware form** | `@app.middleware` function vs `BaseHTTPMiddleware` class vs raw ASGI | **function** for a quick one-off · **class** for reusable/configurable · raw ASGI only for low-level/perf |
| **CORS origins** | `["*"]` vs explicit list | **explicit** in production (and **required** with `allow_credentials=True`); `*` only for public, credential-less APIs |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `Access to fetch ... blocked by CORS policy` | No/!wrong CORS config | Add `CORSMiddleware` with the front-end's exact origin |
| `curl` works but the browser fails | CORS is browser-only | Same fix — configure CORS (curl ignores it) |
| Request hangs / `None` response | Middleware didn't `return await call_next(...)` | Always `call_next(request)` and **return** the response |
| `allow_origins=["*"]` + cookies fails | Can't use `*` with `allow_credentials=True` | List explicit origins when sending credentials |
| Endpoint at wrong URL | Forgot the router `prefix` | Path = `prefix` + route (e.g. `/chat/`) |

## 📌 Quick Reference

```python
# Router (own file) + gate the whole feature:
router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(require_api_key)])
app.include_router(router)

# Middleware (every request) — function or BaseHTTPMiddleware class:
@app.middleware("http")
async def mw(request, call_next):
    resp = await call_next(request); return resp     # MUST return the response

# CORS (browser allow-list):
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```
- **Router** = organize + gate a feature · **middleware** = every request (no value) · **dependency** = chosen routes (+ value) · **CORS** = browser allow-list (explicit origins in prod).

> 🎯 **Interview angle:** "How do you structure a growing FastAPI service?" → `APIRouter`s per
> feature included into the app, middleware for cross-cutting concerns (logging, timing, token
> tracking), and `CORSMiddleware` for the web front-end.

## 🛑 STOP — Self-Check

Match each need to the right tool: (a) split chat and document endpoints into separate files;
(b) log and time **every** request; (c) let the React app at `http://localhost:3000` call the API.

<details><summary>Answer</summary>

(a) **APIRouter** — define each feature's endpoints in its own file and `include_router` them.
(b) **Middleware** (`@app.middleware("http")`) — it runs around every request, ideal for
logging/timing/token tracking. (c) **CORS** (`CORSMiddleware` with `allow_origins=["http://localhost:3000"]`) —
the browser blocks cross-origin calls unless you allow that origin. Three separate concerns, three
separate tools.
</details>
