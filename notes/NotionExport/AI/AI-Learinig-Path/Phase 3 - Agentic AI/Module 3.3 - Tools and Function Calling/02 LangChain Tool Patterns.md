# 02 — LangChain Tool Patterns: `@tool`, StructuredTool, BaseTool

> Phase 3 · Module 3.3 · Lesson 2 · `[JD VERIFIED — ~80%, the everyday way to define tools]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Lesson 01 showed the *schema* a tool needs. Writing that JSON by hand is tedious
and error-prone. LangChain generates it from your Python — three ways, from one-liner to full class — and
you pick by complexity. Plus async tools (don't block) and tool errors (don't crash). Same `bind_tools`/
`ToolNode` from Module 3.1.

**Why care:** ~80% of JDs; the practical skill behind every LangGraph agent.

---

## 🔑 New Terms
- **`@tool`** — decorator turning a function into a tool (schema from signature + docstring).
- **`StructuredTool`** — tool from a function with a **Pydantic** arg schema (validation).
- **`BaseTool`** — subclass for complex/stateful tools. **`ToolException`** — tool error the agent can
  handle. **coroutine/async tool** — non-blocking. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

---

## 🎈 Stage 1 — Simple Idea (analogy: three ways to hire)
`@tool` = quick contractor (one job). `StructuredTool` = vetted hire (validated). `BaseTool` = full
employee (state, async, custom). **Aha!:** match ceremony to complexity — don't write a class for a one-liner.

---

## ⚙️ Stage 2 — The three patterns (each a mini-reference)

#### `@tool` decorator — the everyday one
- **Key features:** schema auto-built from signature + **docstring** (which becomes the description); fewest lines.
- **✅ Use when:** simple functions. **🚫 Avoid → StructuredTool:** rich/validated args. **⚠️:** docstring **is** the description — write *when* to use it.
```python
from langchain_core.tools import tool
@tool
def add(a: int, b: int) -> int:
    """Add two numbers. Use for arithmetic."""   # this line drives tool selection
    return a + b
```
#### `StructuredTool.from_function` — validated args
- **Key features:** explicit **Pydantic** arg schema; field descriptions; sync+async.
- **✅:** multi-field/validated inputs. **🚫→@tool:** trivial. **⚠️:** tight field descriptions.
```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
class Args(BaseModel): city: str = Field(description="city name"); unit: str = "C"
StructuredTool.from_function(func=get_weather, name="weather", args_schema=Args)
```
#### `BaseTool` subclass — stateful/complex
- **Key features:** holds state/config; custom `_run`/`_arun`; full control. **✅:** state, async, deps. **🚫→@tool:** stateless. **⚠️:** implement both `_run`+`_arun`.
- **Errors:** `@tool(handle_tool_error=True)` → returns the error to the model to retry instead of crashing; raise `ToolException` for clean messages. **Async:** `async def` / `_arun` (non-blocking). Bind with `llm.bind_tools(tools)`, run via `ToolNode(tools)` (Module 3.1).
> 🔬 All three compile to the same JSON schema (3.3.01); classes differ only in ceremony/state/validation.

## 🚀 Stage 3 — In Practice / Why It Matters
Every LangGraph agent you build runs on tools, and ~90% of them are a one-line `@tool` — you only climb to
`StructuredTool` when inputs need validation, or `BaseTool` when the tool holds state (a DB connection, an API
client) or must run async. The skill that separates a working agent from a flaky one is the **docstring**: it
*is* the tool's description, so it's what the model reads to decide when to call it. A vague docstring → the
model picks the wrong tool. The same `bind_tools` / `ToolNode` wiring from Module 3.1 runs all three patterns.

## ⚖️ Variations & When to Use
| Pattern | Use when | Avoid when → use instead | Gotcha |
|---|---|---|---|
| **`@tool`** | simple function, few args | rich/validated args → **StructuredTool** | docstring **is** the description |
| **`StructuredTool.from_function`** | multi-field / validated inputs | trivial one-liner → **`@tool`** | write tight field descriptions |
| **`BaseTool` subclass** | state, async deps, full control | stateless function → **`@tool`** | implement **both** `_run` + `_arun` |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Model never calls (or mis-calls) the tool | weak/missing docstring | write a clear docstring saying **when** to use it |
| Event loop blocks under load | sync tool in an async agent | provide an `async def` / `_arun` |
| Agent crashes on a tool error | exception propagates | `@tool(handle_tool_error=True)` / raise `ToolException` |
| Validation errors at call time | loose arg types | give `StructuredTool` a **Pydantic** `args_schema` |

## 📌 Quick Reference
- **`@tool`** (decorator, schema from signature + docstring) · **`StructuredTool.from_function(args_schema=)`**
  (Pydantic validation) · **`BaseTool`** (`_run` + `_arun`, state).
- **Docstring = description** (drives selection). **Async:** `_arun` / `async def`. **Errors:**
  `handle_tool_error=True` + `ToolException`. Bind with `llm.bind_tools`, run via `ToolNode` (3.1).

## 🛑 STOP — Self-Check
You need a tool that holds a **persistent DB connection**, runs **async**, and **validates** its inputs. Which
of the three patterns, and why not the others?

<details><summary>Answer</summary>

**`BaseTool`** (a subclass). It's the only one that can hold **state** (the persistent DB connection) as an
instance attribute, implement an **async** `_arun`, and take a **Pydantic** arg schema for validation. `@tool`
and `StructuredTool` are *stateless* function wrappers — they can validate (StructuredTool) and even run async,
but they can't carry a persistent connection across calls the way a `BaseTool` instance can.
</details>

⏭️ **Next:** Lesson 03 — Practical tools (SQL/REST/filesystem/code), secured.
