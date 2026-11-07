# $\Huge\color{#0D47A1}{\textsf{22 — Type Hints and Pydantic}}$

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Curriculum](https://img.shields.io/badge/Roadmap-Phase%200.1-0288D1?style=for-the-badge&logo=compass&logoColor=white)](README.md)
[![Priority](https://img.shields.io/badge/Priority-MUST%20KNOW-D32F2F?style=for-the-badge&logo=target&logoColor=white)](../../AI%20Engineer%20Architect%20Road%20Map.md)
[![Status](https://img.shields.io/badge/Status-Foundational-2E7D32?style=for-the-badge&logo=checkmarx&logoColor=white)](#)

> $\color{#546E7A}\mathbf{Navigation:}$ **Phase 0** · **Module 0.1** · **Lesson 22 of 25** · [← Prev: 14 Advanced Python](14%20Advanced%20Python.md) · [Phase 0.1 — Python Index](README.md) · [Next: 23 Concurrency →](23%20Concurrency.md)

---

![Stage 0](https://img.shields.io/badge/STAGE%200-CONCEPT%20MAP-0288D1?style=for-the-badge&logo=gitbook&logoColor=white)

## 🗺️ $\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{Stage 0 — Concept Map}}$

Python lets you *optionally* label what type each value should be. These **type hints** make code
readable and catch mistakes early. **Pydantic** takes hints further: it actually **validates** data
against them at runtime — essential when data comes from the messy outside world (users, APIs,
LLMs). This lesson is the bridge from "plain Python" to "production AI plumbing."

![Key Terms](https://img.shields.io/badge/KEY%20TERMS-GLOSSARY-7B1FA2?style=for-the-badge&logo=book&logoColor=white)

## 🔑 $\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{New Terms (Plain English)}}$

- **Type hint** — an optional label of a value's expected type (not enforced at runtime).
- **`X | None`** — "an `X`, or nothing" — the optional-value pattern.
- **Pydantic model** — a class that *validates* incoming data against its fields.
- **Validation** — checking data is correct and rejecting bad values.
- **Coercion** — auto-converting a value where sensible (`"36"` → `36`).

![Stage 1](https://img.shields.io/badge/STAGE%201-THE%20SIMPLE%20IDEA-00897B?style=for-the-badge&logo=lightbulb&logoColor=white)

## 🎈 $\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{Stage 1 — The Simple Idea (analogy: labels on storage bins)}}$

Imagine labelling every storage bin: *"Screws (metal only)"*. The label doesn't physically stop you
from putting a sock in — but it documents intent, and a good inspector (your editor) warns you when
something looks wrong. **Type hints are those labels.** **Pydantic** is the strict inspector who
*actually checks* each bin's contents and rejects the sock.

**The "Aha!":** type hints alone are **documentation** (Python won't enforce them at runtime).
Pydantic uses the same hints to **enforce** correctness on real data.

![Stage 2](https://img.shields.io/badge/STAGE%202-HOW%20IT%20ACTUALLY%20WORKS-E65100?style=for-the-badge&logo=gear&logoColor=white)

## ⚙️ $\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{Stage 2 — How It Actually Works}}$

> [!IMPORTANT]
> ### $\color{#00C853}{\textsf{🔥 The 80/20 Core Rule: What Matters in Production}}$
> * $\color{#00C853}\blacktriangleright$ **Daily Core (90% of Real AI Work):** Standard type annotations (`int`, `str`, `float`, `bool`, `list[str]`, `dict[str, Any]`), `T | None` (or `Optional[T]`) for optional arguments, Pydantic `BaseModel` for defining structured LLM outputs, validating JSON via `model.model_validate_json()`, and dumping models via `model.model_dump()`.
> * $\color{#FFB300}\blacktriangleright$ **Occasional (Constrained and Validated Fields):** `Literal["gpt-4o", "claude-3-5-sonnet"]` (restricting model strings), `Field(ge=0, le=1)` (bounding temperature), custom `@field_validator`.
> * $\color{#757575}\blacktriangleright$ **Reference Only (Exhaustive Typing):** `TypeVar`, `Generic[T]`, `Protocol` (structural subtyping), `TypedDict` (superseded by Pydantic in modern AI stacks).

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{13.1 Basic type hints}}$

```python
name: str = "Ada"          # annotate a variable
age: int = 36
height: float = 1.7
active: bool = True

def greet(person: str) -> str:    # parameters and the "-> return type"
    return f"Hello, {person}"
```

Important: Python does **not** stop you from breaking a hint — `age: int = "oops"` still runs. The
value comes from tools (VS Code, type checkers like `mypy`) flagging the mismatch, and from humans
reading clearer code.

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{13.2 Collections and optional values}}$

```python
scores: list[int] = [90, 75]              # a list of ints
prices: dict[str, float] = {"apple": 3.0} # dict from str keys to float values
pair: tuple[int, int] = (1, 2)

# "X | None" means "an X, or nothing" — the optional value pattern:
email: str | None = None                  # might be a string, might be absent

def find_user(uid: int) -> dict | None:   # returns a dict, or None if not found
    ...
```

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{13.3 A couple of handy typing tools}}$

```python
from typing import Literal

# Literal restricts to specific allowed values (great for modes/roles):
def set_mode(mode: Literal["fast", "accurate"]) -> None:
    ...
set_mode("fast")        # ok
# set_mode("turbo")     # a type checker flags this — not an allowed value
```

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{13.4 Pydantic — validation at runtime}}$

Install: `pip install pydantic`. A **model** is a class describing the shape of your data;
Pydantic validates and (where sensible) converts incoming values.

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str                              # required text
    age: int = Field(ge=0, le=150)         # required int, must be 0..150
    email: str | None = None               # optional, defaults to None
    roles: list[str] = []                  # defaults to an empty list

    @field_validator("name")               # custom rule beyond the type
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v

# Valid data -> a clean, typed object:
u = User(name="Ada", age="36")             # note: "36" (str) is coerced to int 36
print(u.age, type(u.age))                  # 36 <class 'int'>

# Invalid data -> a clear ValidationError naming the offending field:
# User(name="", age=200)                   # name blank AND age > 150 -> errors
```

Useful model methods:

```python
print(u.model_dump())        # -> dict: {'name': 'Ada', 'age': 36, ...}
print(u.model_dump_json())   # -> JSON string (ready to send over an API)
restored = User(**u.model_dump())   # rebuild from a dict
```

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{13.5 Settings from environment variables}}$

```python
# pip install pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str            # auto-read from the OPENAI_API_KEY env var
    model: str = "gpt-4o-mini"     # default if not set

# settings = Settings()           # validates that required secrets are present
```

This is the clean, validated way to load configuration/secrets — no hardcoding keys.

![Stage 3](https://img.shields.io/badge/STAGE%203-IN%20PRACTICE%20%2F%20WHY%20IT%20MATTERS-1565C0?style=for-the-badge&logo=rocket&logoColor=white)

## 🚀 $\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{Stage 3 — In Practice / Why It Matters}}$

Pydantic is everywhere in AI Python: FastAPI uses it to validate web requests (Phase 1), the
`instructor` library uses it to force an LLM to return data matching your model (Phase 1), and tool
definitions for agents are Pydantic schemas (Phase 3). "Validate at the boundary, then trust the
data inside" is the habit that keeps AI systems robust.

**Common beginner mistakes (the reasoning):**
1. **Expecting type hints to enforce types at runtime** — they don't. Use **Pydantic** when you
   need real validation of external data.
2. **Skipping validation on LLM/API output** — then crashing deep in the code when a field is
   missing. Define a model and parse at the boundary.
3. **Confusing `dataclass` and Pydantic** — both model data; `dataclass` doesn't validate, Pydantic
   does. Use Pydantic for anything coming from outside your program.
4. **Hardcoding secrets** — load them via `BaseSettings`/environment variables instead.

### Try it yourself
Define a Pydantic `Product` model with `name: str`, `price: float` (must be `> 0`), and
`tags: list[str] = []`. Try creating one with `price=-5` and read the error message.

![Errors](https://img.shields.io/badge/DEBUGGING-COMMON%20ERRORS%20%26%20FIXES-C2185B?style=for-the-badge&logo=debug&logoColor=white)

## 🐛 $\color{#880E4F}\blacksquare\space\color{#AD1457}{\textsf{Common Errors and Fixes}}$

| What you see | Cause | Fix |
| --- | --- | --- |
| Bad value isn't caught | Plain type hints aren't enforced at runtime | Use a **Pydantic** model for real validation |
| `ValidationError` | Data didn't match the model | Read which field failed; fix the input |
| `ImportError: pydantic_settings` | Package not installed | `pip install pydantic-settings` |
| Secret sitting in source code | Hardcoded API key | Load via env var / `BaseSettings` |

![Quick Reference](https://img.shields.io/badge/CHEAT%20SHEET-QUICK%20REFERENCE-2E7D32?style=for-the-badge&logo=codeigniter&logoColor=white)

## 📌 $\color{#1B5E20}\blacksquare\space\color{#2E7D32}{\textsf{Quick Reference}}$

```python
name: str; age: int; email: str | None = None
scores: list[int] = []
from pydantic import BaseModel, Field
class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
u = User(name="Ada", age="36")     # validates + coerces "36" -> 36
u.model_dump(); u.model_dump_json()
```

![Stop Check](https://img.shields.io/badge/CHECKPOINT-STOP%20%26%20SELF%20CHECK-D32F2F?style=for-the-badge&logo=stop&logoColor=white)

## 🛑 $\color{#B71C1C}\blacksquare\space\color{#D32F2F}{\textsf{STOP — Self-Check}}$

What's the practical difference between a plain type hint (`age: int`) and a Pydantic field
(`age: int` inside a `BaseModel`) when bad data arrives at runtime?

<details>
<summary><b>🔍 Click to Reveal the Answer</b></summary>

<br/>

A plain type hint is **not enforced at runtime** — assigning `age = "oops"` still runs; the hint
only helps editors/type-checkers and human readers. Inside a **Pydantic `BaseModel`**, the same
annotation is **actively validated** when you create the object: a bad value raises a
`ValidationError` immediately (and convertible values like `"36"` are coerced to `36`). That's why
Pydantic is used at the boundaries where untrusted external data enters.
</details>
