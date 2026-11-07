# $\Huge\color{#0D47A1}{\textsf{25 — Milestone: Typed API CLI Tool}}$

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Curriculum](https://img.shields.io/badge/Roadmap-Phase%200.1-0288D1?style=for-the-badge&logo=compass&logoColor=white)](README.md)
[![Priority](https://img.shields.io/badge/Priority-MUST%20KNOW-D32F2F?style=for-the-badge&logo=target&logoColor=white)](../../AI%20Engineer%20Architect%20Road%20Map.md)
[![Status](https://img.shields.io/badge/Status-Foundational-2E7D32?style=for-the-badge&logo=checkmarx&logoColor=white)](#)

> $\color{#546E7A}\mathbf{Navigation:}$ **Phase 0** · **Module 0.1** · **Lesson 25 of 25** · [← Prev: 24 AI Essentials - NumPy and HTTP](24%20AI%20Essentials%20-%20NumPy%20and%20HTTP.md) · [Phase 0.1 — Python Index](README.md) · [Next: Phase 0.2 — PyTorch Index →](../Phase%200.2%20-%20PyTorch/README.md)

---

## 🎯 Goal

Combine the whole module into one small, professional program: a **command-line tool** that calls
an API, **validates** the response with Pydantic, handles **errors** with retries, and prints a
clean result. If you can build and explain this, you're ready for the AI-specific modules.

## 🧩 What it exercises
- Setup & running scripts (01) · variables/types (02) · strings (03)
- collections (04, 05) · control flow (06) · functions (07)
- error handling (10) · modules/files (11) · built-in functions (13)
- type hints & Pydantic (22) · async + HTTP (23, 24)

> [!IMPORTANT]
> ### $\color{#00C853}{\textsf{🔥 The 80/20 Core Rule: What Matters in Production}}$
> * $\color{#00C853}\blacktriangleright$ **Daily Core (90% of Real AI Work):** End-to-end integration of the core Python stack: CLI flags, type-safe request/response validation with Pydantic, robust error handling with specific exception traps, and structured terminal reporting.
> * $\color{#FFB300}\blacktriangleright$ **Occasional (Production Tuning):** Exponential backoff retries (`tenacity`), streaming HTTP responses, environment variable loading.
> * $\color{#757575}\blacktriangleright$ **Reference Only (CLI Polish):** Advanced subcommands, shell auto-completion.

---

## 🛠️ Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install httpx pydantic tenacity
pip freeze > requirements.txt
```

- **`httpx`** — async HTTP client (Lesson 24).
- **`pydantic`** — validation (Lesson 22).
- **`tenacity`** — retry-on-failure via a decorator (Lesson 09 decorators + Lesson 10 errors).

## 📄 `main.py` (fully commented)

```python
import asyncio
import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed

URL = "https://jsonplaceholder.typicode.com/todos/{id}"   # a free test API

# 1. The EXACT shape we expect back. Pydantic validates incoming JSON against this.
class Todo(BaseModel):
    userId: int
    id: int
    title: str
    completed: bool

# 2. A domain-specific error (Lesson 10) so callers can catch THIS failure precisely.
class TodoError(Exception):
    """Raised when a todo can't be fetched or validated."""

# 3. @retry (Lesson 09): if this coroutine raises, retry up to 3 times, 1s apart.
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch_todo(todo_id: int) -> Todo:
    async with httpx.AsyncClient(timeout=10) as client:   # context manager auto-closes
        response = await client.get(URL.format(id=todo_id))
        response.raise_for_status()                       # 4xx/5xx -> raise -> triggers retry
        return Todo(**response.json())                    # validate at the boundary

async def main() -> None:
    try:
        # asyncio.gather (Lesson 23) fetches several todos concurrently.
        todos = await asyncio.gather(*(fetch_todo(i) for i in range(1, 4)))
    except Exception as error:                            # last-resort guard
        raise TodoError(f"Failed to fetch todos: {error}") from error

    for todo in todos:                                    # loop + f-strings (Lessons 06, 03)
        status = "done" if todo.completed else "pending"  # conditional expression (Lesson 06)
        print(f"[{todo.id}] {todo.title[:40]:<40} — {status}")

if __name__ == "__main__":                                # script guard (Lesson 11)
    asyncio.run(main())
```

## ▶️ Run it

```powershell
python main.py
# [1] delectus aut autem                        — pending
# [2] quis ut nam facilis et officia qui        — pending
# [3] fugiat veniam minus                       — pending
```

## ✅ Done when you can…
- Run it and get three validated rows.
- **Explain each line** — what it does and which lesson it comes from.
- Break the URL (typo the host) and watch `tenacity` retry 3 times, then raise a `TodoError`.
- Change a `Todo` field type (e.g. `id: bool`) and see a Pydantic `ValidationError` at the boundary.

![Errors](https://img.shields.io/badge/DEBUGGING-COMMON%20ERRORS%20%26%20FIXES-C2185B?style=for-the-badge&logo=debug&logoColor=white)

## 🐛 $\color{#880E4F}\blacksquare\space\color{#AD1457}{\textsf{Common Errors and Fixes}}$ (running this milestone)

| What you see | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError` | venv not active / packages not installed | Activate the venv; `pip install httpx pydantic tenacity` |
| `ValidationError` | API JSON didn't match `Todo` | Compare the model fields to the actual response |
| Hangs, then fails | No network, or no timeout | Confirm the `timeout`; check your connection |
| `RetryError` after 3 tries | URL wrong / host down | Fix the URL; read the underlying error it wraps |

## 🛑 Reflection (module capstone)
Name the three "boundaries" in this program where things could go wrong, and which tool guards
each.

<details>
<summary><b>🔍 Click to Reveal the Answer</b></summary>

<br/>

1. **The network call** — guarded by `timeout` + `response.raise_for_status()` and retried by
   `@retry` (tenacity). 2. **The data shape** — guarded by the Pydantic `Todo` model at
   `Todo(**response.json())`, which rejects malformed/missing fields. 3. **Overall orchestration**
   — guarded by the `try/except` in `main`, which converts any failure into a clear domain-specific
   `TodoError`. Each boundary has an explicit guard, which is exactly the mindset AI systems need.
</details>

---

## 🎓 Module 0.1 complete
You've covered Python from "how it runs" through OOP, typing, concurrency, and the AI-essential
libraries. Combined with **Module 0.2 (PyTorch)** and **Module 0.3 (Core AI Constructs)**, **Phase
0 is now complete** — you can read AI code, reason about data, and make real API calls.
