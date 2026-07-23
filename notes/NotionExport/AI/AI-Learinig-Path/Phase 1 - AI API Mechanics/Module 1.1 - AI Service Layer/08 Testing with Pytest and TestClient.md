# 08 — Testing (pytest + TestClient)

> Phase 1 · Module 1.1 · Lesson 8 · `[SHOULD — JD-common for any backend role]`

## 🗺️ Stage 0 — Concept Map

A service you can't test is a service you can't safely change. **Automated tests** prove each
endpoint behaves and catch **regressions** (changes that break something that used to work) before
users do. FastAPI ships a **`TestClient`** that makes this easy, and it pairs perfectly with
[02 Dependency Injection](02%20Dependency%20Injection.md) to **fake the LLM** so tests are fast, free,
and **deterministic** (same input → same result every time). Testing appears in most backend JDs.

## 🔑 New Terms (plain English)

- **pytest** — the standard Python test runner; it finds and runs `test_*` functions.
- **`TestClient`** — a fake HTTP client that calls your FastAPI app **in-process** (no real server).
- **Fixture** — reusable test setup (pytest's `@pytest.fixture`).
- **`dependency_overrides`** — swap a real dependency (the LLM client) for a **fake** during tests.
- **`conftest.py`** — a file of shared pytest fixtures auto-discovered across your tests.
- **`monkeypatch` / `respx`** — other ways to fake: patch an attribute (`monkeypatch`) or mock HTTP calls (`respx`).
- **`parametrize`** — run one test over many input/expected pairs (`@pytest.mark.parametrize`).

## 🎈 Stage 1 — The Simple Idea (analogy: a pre-flight checklist)

Pilots don't *hope* the plane works — they run a **checklist** before every takeoff. Tests are that
checklist for your API: a set of automated checks that each endpoint returns the right status and
shape. Run them on every change and you catch breakage instantly.

**The "Aha!":** `TestClient` lets you call your endpoints like a user would, but in code — and by
**overriding the LLM dependency with a fake**, your tests never spend money or depend on the network.

**💢 The old/painful way** — start the server, fire `curl`/Postman by hand, eyeball the output, repeat.
Slow, manual, and nothing fails the build when a regression slips in. `TestClient` + pytest make it
automatic and repeatable.

## ⚙️ Stage 2 — How It Actually Works

### 8.1 A first test

```python
# pip install pytest httpx        (TestClient is powered by httpx)
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200          # check status FIRST
    assert response.json() == {"status": "ok"}  # then the body
```

Run it: `pytest -q`. Files are named `test_*.py`, functions `test_*`.

### 8.2 Fixtures — reusable setup in `conftest.py`

A **fixture** builds something tests need (the client, a fake LLM) once and injects it. Put shared
ones in `conftest.py` (auto-discovered):

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app, get_llm_client

@pytest.fixture
def client():
    app.dependency_overrides[get_llm_client] = lambda: (lambda prompt: "FAKE REPLY")  # fake the LLM
    yield TestClient(app)                  # hand the configured client to the test
    app.dependency_overrides.clear()       # cleanup -> no leak into other tests

# test_chat.py
def test_chat(client):                     # 'client' is injected by the fixture
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
```

The `yield` + `clear()` pattern guarantees the override doesn't leak between tests.

### 8.3 Fake the LLM — three ways (and when to use each)

Tests shouldn't call a real model (slow, costly, non-deterministic). Three ways to fake it:

```python
# 1) dependency_overrides (BEST when the client is injected via Depends — lesson 02):
app.dependency_overrides[get_llm_client] = lambda: fake_client

# 2) monkeypatch (when it's NOT injected — patch the function/attribute directly):
def test_x(monkeypatch):
    monkeypatch.setattr("app.services.call_llm", lambda p: "FAKE")

# 3) respx (mock at the HTTP layer — when you want to test the real client's parsing):
#    import respx;  respx.post("https://api.openai.com/...").respond(json={...})
```

**Use which** — pick by *how* the LLM client is wired into your code:

- **`dependency_overrides`** — swap the injected dependency for a fake.
  - **Key features:** cleanest; uses FastAPI's own machinery; no patching of import paths.
  - **✅ Use when:** the client is injected via `Depends` (lesson 02) — the recommended setup.
  - **🚫 Avoid when → use `monkeypatch`:** the client is *not* injected (a module global or direct call).
  - **⚠️ Gotcha:** clear it after each test (`dependency_overrides.clear()`) or it leaks into other tests.
- **`monkeypatch`** — replace a function/attribute by its import path for the test.
  - **Key features:** works on anything, even code that isn't injected; auto-undone after the test.
  - **✅ Use when:** the LLM call is a plain function or module global you can't inject.
  - **🚫 Avoid when → use `dependency_overrides`:** the client *is* injected — overrides are cleaner.
  - **⚠️ Gotcha:** patch the **exact import path the code calls**, not where the function is defined.
- **`respx`** — fake the HTTP response itself (a stand-in for the network layer).
  - **Key features:** exercises the *real* SDK's request building and response parsing.
  - **✅ Use when:** you specifically want to test the client's own HTTP/parse logic, not just your code.
  - **🚫 Avoid when → use `dependency_overrides`:** you only care about *your* routing/validation — faking HTTP is extra work.
  - **⚠️ Gotcha:** ties the test to the provider's wire format, so it's more brittle when the API changes.

### 8.4 Validation is testable too

```python
def test_chat_rejects_bad_body():
    r = client.post("/chat", json={"temperature": "hot"})   # invalid field
    assert r.status_code == 422                              # FastAPI/Pydantic rejected it
```

### 8.5 Testing a streaming endpoint (AI-specific)

For an SSE endpoint (lesson 04), read the streamed body and assert on the chunks:

```python
def test_stream():
    with client.stream("GET", "/stream?prompt=hi") as r:
        assert r.status_code == 200
        chunks = [line for line in r.iter_lines() if line]
        assert any("data:" in c for c in chunks)
```

### 8.6 Async tests (when you need them)

`TestClient` is synchronous and covers most endpoint tests. Reach for **`httpx.AsyncClient`** when you
test **async-only** helpers directly, or need true concurrency:

```python
import pytest, httpx
from httpx import ASGITransport
from main import app

@pytest.mark.anyio                          # pip install anyio (or pytest-asyncio)
async def test_async():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/chat", json={"message": "hi"})
        assert r.status_code == 200
```

> 🔬 **Under the hood:** `TestClient` (built on httpx) calls your ASGI app **in-process** — no real
> socket or running server — so tests are fast and deterministic. `app.dependency_overrides` swaps real
> dependencies (the live LLM client) for fakes, and pytest **fixtures** build and tear down shared
> setup around each test.

## 🚀 Stage 3 — In Practice / Why It Matters

Every endpoint in the Phase 1 gateway gets a test; **CI** (the automated build that runs on every
push) runs `pytest` (Phase 4 adds eval gates). Faking the LLM via `dependency_overrides` is the key
habit — it makes the whole suite fast,
free, and repeatable, which is exactly what interviewers probe ("how do you test code that calls an
LLM?").

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Fake the LLM** | `dependency_overrides` vs `monkeypatch` vs `respx` | **overrides** if the client is injected (cleanest) · **monkeypatch** for a plain function/global · **respx** to exercise the SDK's HTTP parsing |
| **Client** | sync `TestClient` vs async `httpx.AsyncClient` | **`TestClient`** for most endpoint tests · **`AsyncClient`** for async-only helpers or true concurrency |
| **Many cases** | repeated tests vs `@pytest.mark.parametrize` | **parametrize** one test over many input/expected pairs |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Tests are slow / cost money / flaky (random failures) | They call the real LLM | Override the client dependency with a fake (`dependency_overrides`) |
| `ModuleNotFoundError: httpx` | `TestClient` needs httpx | `pip install httpx` (or `fastapi[standard]`) |
| `pytest` finds no tests | Wrong names | Files `test_*.py`, functions `test_*` |
| Assertion on `.json()` fails confusingly | Checked body before status | Assert `status_code` **first**, then the body |
| Override leaks into other tests | Not cleared | `app.dependency_overrides.clear()` (or use a fixture) |

## 📌 Quick Reference

```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_x():
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json()["reply"]

app.dependency_overrides[get_llm_client] = lambda: fake   # fake the LLM in tests
```
- `pytest -q` · files `test_*.py` · **fixtures** in `conftest.py` · assert **status then body** · **fake the LLM** (overrides/monkeypatch/respx).

> 🎯 **Interview angle:** "How do you test an endpoint that calls an LLM?" → with `TestClient`, and
> `app.dependency_overrides` to swap the LLM client for a fake, so tests are deterministic, fast,
> and free.

## 🛑 STOP — Self-Check

Why override the LLM dependency with a fake in your tests instead of letting the test call the real
model?

<details><summary>Answer</summary>

Because calling the real model makes tests **slow, costly, and non-deterministic** (the same prompt
can return different text, and it needs network + an API key). Overriding the injected client with a
**fake** that returns a fixed reply makes the suite **fast, free, and repeatable**, so tests check
*your* code's behaviour (routing, validation, response shape) rather than the model's. This is only
possible because the client is **injected** (lesson 02) rather than created inside the handler.
</details>
