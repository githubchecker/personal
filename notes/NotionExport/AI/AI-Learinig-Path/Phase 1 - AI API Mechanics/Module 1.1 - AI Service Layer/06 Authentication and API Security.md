# 06 — Authentication & API Security

> Phase 1 · Module 1.1 · Lesson 6 · `[SHOULD — securing the API]`

## 🗺️ Stage 0 — Concept Map

The moment your AI service is reachable, it's a **costly, abusable resource** — anyone who finds the
URL could run up your model bill. **Authentication** decides *who* is allowed to call it. This lesson
covers the two patterns that cover ~95% of real AI services: an **API key** (internal/service
gateways) and **Bearer tokens / OAuth2 + JWT** (user-facing apps). It uses
[02 Dependency Injection](02%20Dependency%20Injection.md) (the check is a dependency) and the
settings from [07 Config](07%20Config%20Lifespan%20and%20Background%20Tasks.md).

## 🔑 New Terms (plain English)

- **Authentication (authn)** — *who are you?* (proving identity).
- **Authorization (authz)** — *what are you allowed to do?* (permissions).
- **API key** — a single secret string a caller sends in a header to prove it's allowed.
- **Bearer token** — a token sent as `Authorization: Bearer <token>`; "whoever bears it, gets in."
- **OAuth2** — a standard *flow* for issuing tokens to users (login → token → use token).
- **JWT (JSON Web Token)** — a signed, self-contained token carrying claims (user id, expiry).
- **`401` vs `403`** — `401` = *not authenticated* (no/bad credential); `403` = *authenticated but
  not allowed*.
- **`APIKeyHeader`** — a FastAPI security helper that reads an API-key header and shows it in `/docs`.
- **Scope / role** — a permission attached to a token; checked for **authorization** (what you can do).

## 🎈 Stage 1 — The Simple Idea (analogy: a building pass)

Your AI endpoints are **expensive equipment in a locked lab**. An **API key** is a **swipe card**:
the guard at the door (a dependency) checks the card before letting anyone touch the machines. A
**JWT** is a fancier, time-stamped **photo badge** issued at reception (login) that proves *which
person* you are and *when it expires* — useful when many different users share the building.

**The "Aha!":** authentication is just *a check that runs before your endpoint* — and in FastAPI
that's exactly what a **dependency** is. So securing an endpoint = adding a dependency.

**💢 The old/painful way** — checking the key with `==` inside every handler: duplicated everywhere,
easy to forget on one route, and `==` leaks *timing information* (how long the compare takes can hint
at the secret — a **timing attack**). Wiring auth as a **dependency** centralises the check and runs
it before the handler.

## ⚙️ Stage 2 — How It Actually Works

### 6.1 API-key auth (the common pattern for AI gateways)

```python
import secrets
from fastapi import FastAPI, Depends, Header, HTTPException

app = FastAPI()

def require_api_key(x_api_key: str = Header()):        # read the "X-API-Key" request header
    # secrets.compare_digest = constant-time compare, avoids timing attacks (don't use ==)
    if not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    # (return a caller id here if you want it injected into the endpoint)

@app.post("/chat", dependencies=[Depends(require_api_key)])   # gate this endpoint
async def chat():
    return {"reply": "..."}
```

- `dependencies=[Depends(require_api_key)]` runs the check **before** the handler; fail → `401`, the
  handler never runs.
- Apply it to **one route**, a whole **router** (`APIRouter(dependencies=[...])`, lesson 05), or the
  **whole app** (`FastAPI(dependencies=[...])`).

**Cleaner variation — `APIKeyHeader`** (it appears in `/docs` and is easy to test):

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")   # declared once; shows up in Swagger UI

def require_api_key(key: str = Depends(api_key_header)):
    if not secrets.compare_digest(key, settings.api_key):
        raise HTTPException(401, "Invalid API key")
```

### 6.2 Bearer-token style (toward user auth)

FastAPI has built-in helpers that also make the lock show up in the `/docs` page:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")   # expects: Authorization: Bearer <token>

@app.get("/me")
async def me(token: str = Depends(oauth2_scheme)):
    user = decode_and_verify(token)         # verify a JWT here (signature + expiry)
    if user is None:
        raise HTTPException(status_code=401, detail="Bad token")
    return {"user": user}
```

### 6.3 OAuth2 + JWT — the full user-login flow `[awareness]`

For multi-user products the standard is: user logs in with username/password → server returns a
**signed JWT** → client sends that JWT as a Bearer token on every request → a dependency verifies the
signature and expiry. FastAPI's docs have a complete recipe (*OAuth2 with Password, Bearer with JWT*)
using `passlib` for password hashing and `pyjwt` for tokens. **Know the shape now; implement it when
a role needs user accounts** — for an internal AI gateway, the API key in 6.1 is usually enough.

### 6.4 Authorization — what you're allowed to do (roles/scopes)

Authentication says *who* you are; **authorization** says *what you may do*. Once you know the caller
(from the token), check their **role/scope** in a dependency:

```python
def require_admin(user = Depends(current_user)):     # current_user came from the token
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Admins only")   # 403 = known, but not allowed

@app.delete("/chats/{id}", dependencies=[Depends(require_admin)])
async def delete_chat(id: str): ...
```

This is the **`401` vs `403`** distinction in action: no/bad credential → `401`; valid identity
without permission → `403`. OAuth2 formalises this with **scopes** (`chat:read`, `chat:write`) —
awareness for now.

### 6.5 Security hygiene (the cheap wins)

- **Keep secrets in settings/env** (lesson 07), never in code or git; never **log** keys/tokens.
- **HTTPS only** in production — put **TLS** (the encryption behind HTTPS) in front (proxy/cloud,
  lesson 09) so keys aren't sent as readable text.
- **Constant-time compare** (`secrets.compare_digest` — it always takes the same time, so it can't
  leak the secret) for keys; **hash** stored passwords (store a one-way scramble, never the plain text).
- Return **`401`** for missing/bad credentials, **`403`** for "valid identity but not permitted."

### 6.6 Which credential type? — API key vs OAuth2/JWT vs session cookie

The core architectural choice. Pick by *who* calls your API:

- **API key** — one shared secret string sent in a header.
  - **Key features:** dead simple; no login flow; perfect for server-to-server calls.
  - **✅ Use when:** an internal/service or business-to-business gateway, or your own backend calls it.
  - **🚫 Avoid when → use OAuth2/JWT:** end users log in individually and you need per-user identity.
  - **⚠️ Gotcha:** one key is the *same* identity for everyone holding it — you can't tell users apart, so rotate it the moment it leaks.
- **OAuth2 + JWT (Bearer token)** — each user logs in and gets a signed, expiring token.
  - **Key features:** per-user identity; built-in expiry; carries roles/scopes; verifies with no database lookup.
  - **✅ Use when:** user-facing apps with many separate customers, or different permissions per user.
  - **🚫 Avoid when → use an API key:** a simple internal service — full OAuth2 is overkill there.
  - **⚠️ Gotcha:** verify **both** the signature and the expiry on every request; a stolen token works until it expires.
- **Session cookie** — the server stores a session and hands the browser a cookie id.
  - **Key features:** automatic in browsers; easy server-side logout (just drop the session).
  - **✅ Use when:** a traditional, server-rendered website on a single domain.
  - **🚫 Avoid when → use JWT:** a separate front-end, mobile app, or cross-domain API (cookies get awkward).
  - **⚠️ Gotcha:** needs server-side session storage **and** CSRF protection (a guard against *cross-site request forgery* — another site tricking the browser into using your cookie).

> 🔬 **Under the hood:** a security dependency runs *before* your handler in the dependency graph; on
> failure it returns `401`/`403` and the handler never runs. `APIKeyHeader` / `OAuth2PasswordBearer`
> are dependencies that *also* register the scheme in the OpenAPI **security schema** (the 🔒 icon in
> `/docs`). A JWT is verified by recomputing its signature with your secret — no database lookup needed.

## 🚀 Stage 3 — In Practice / Why It Matters

The Phase 1 gateway will gate its endpoints with an **API-key dependency** (the realistic default for
an internal/service AI API), with settings-stored keys and HTTPS in front. Knowing the **OAuth2/JWT**
shape means you can step up to user accounts when a product needs them. "How do you secure this
endpoint?" and "401 vs 403?" are near-guaranteed interview questions.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Credential type** | API key vs OAuth2/JWT vs session cookie | **API key** for service/internal/business-to-business gateways · **OAuth2/JWT** for user-facing apps with many separate customers · session cookies for traditional server-rendered web |
| **Where to enforce** | per-route vs router vs global dependency | **global** when the whole API is private · **per-route/router** when some endpoints are public (e.g. `/health`) |
| **API-key delivery** | custom `Header()` vs `APIKeyHeader` helper | prefer **`APIKeyHeader`** so it appears in `/docs` and is testable |
| **authn vs authz** | identity check vs permission check | **authn** (`401`) proves who you are; add **authz** (`403`, roles/scopes) when actions differ by user |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Endpoint usable with no key | Forgot to attach the dependency | `dependencies=[Depends(require_api_key)]` on route/router/app |
| Used `if key == settings.api_key` | Timing-attack risk | `secrets.compare_digest(a, b)` |
| Returned `403` for a missing key | Wrong code | Missing/bad credential = **`401`**; `403` = authenticated-but-forbidden |
| Key leaked in logs / git | Logged or hardcoded the secret | Load from env (settings); scrub logs; rotate the key |
| Token works forever | JWT not checked for expiry | Verify signature **and** `exp` on every request |

## 📌 Quick Reference

```python
def require_api_key(x_api_key: str = Header()):
    if not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(401, "Invalid API key")

@app.post("/chat", dependencies=[Depends(require_api_key)])   # per-route
# APIRouter(dependencies=[Depends(require_api_key)])          # per-router
# FastAPI(dependencies=[Depends(require_api_key)])            # whole app

OAuth2PasswordBearer(tokenUrl="token")    # Bearer/JWT for user auth (await deeper impl)
```
- Auth = **a dependency that runs first** · API key for gateways · OAuth2/JWT for users ·
  `401` (who?) vs `403` (allowed?) · secrets in env, HTTPS in front, constant-time compare.

> 🎯 **Interview angle:** "How would you protect this AI endpoint?" → an auth **dependency** (API
> key via header for a service gateway, or OAuth2/JWT Bearer for users), keys in env not code,
> HTTPS in front, `secrets.compare_digest` for comparison, and the right `401`/`403` codes.

## 🛑 STOP — Self-Check

You add `dependencies=[Depends(require_api_key)]` to your `/chat` route. A request arrives with **no**
`X-API-Key` header — what status should come back, and does the `chat()` function run? And why use
`secrets.compare_digest` instead of `==`?

<details><summary>Answer</summary>

The dependency runs **before** `chat()`. With no key, `require_api_key` raises
`HTTPException(401)`, so the client gets a **`401 Unauthorized`** and `chat()` **never runs** — the
expensive model call is never reached. Use **`secrets.compare_digest`** instead of `==` because a
plain `==` can leak how many leading characters matched via tiny timing differences (a **timing
attack**); `compare_digest` always takes the same time, so it doesn't leak that information.
</details>
