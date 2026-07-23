# 02 — Building MCP Servers with FastMCP

> Phase 3 · Module 3.4 · Lesson 2 · `[JD VERIFIED — ~58%, expose your data/tools to any agent]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Lesson 01 explained *why* MCP. Now: build a server so any agent can use your data.
The `mcp` SDK's **FastMCP** turns Python functions into a compliant server — decorators auto-generate the
schema from your type hints. Write three decorators, run, done.

**Why care:** "build an MCP server" is the hands-on JD ask; the milestone (3.4.05) needs it.

---

## 🔑 New Terms
**FastMCP** — high-level server (`@mcp.tool/@mcp.resource/@mcp.prompt`). **Context** — injected obj for
logging/progress. **transport** — `stdio` (default) / `streamable-http` (prod). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea (analogy: labelling a shop)
FastMCP = shop signs: Tools = staff who *do*, Resources = shelves to *read*, Prompts = order forms.
Hang signs (decorators); any customer (agent) shops. **Aha!:** decorate functions → instant standard server.

## ⚙️ Stage 2 (fully commented)
```python
# pip install "mcp[cli]"
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("Demo")

@mcp.tool()                                   # ACTION (schema auto from hints+docstring)
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("doc://{name}")                 # DATA (GET-like)
def read_doc(name: str) -> str: return load(name)

@mcp.prompt()                                 # TEMPLATE
def review(code: str) -> str: return f"Review:\n{code}"

if __name__ == "__main__":
    mcp.run()                                 # stdio (local); prod: mcp.run(transport="streamable-http")
```
#### `@mcp.tool()` — an action (side effects)
- **What & why:** exposes a function the model can *call to do something*; the schema is auto-built from your
  **type hints + docstring**. **✅ Use when:** the agent should act (write, compute, trigger). **🚫 Avoid →
  `@resource`:** for a pure read. **⚠️ Gotcha:** missing type hints/docstring → a thin schema the model can't use well.

#### `@mcp.resource("uri://{param}")` — data to read (GET-like)
- **What & why:** exposes *data* the host fetches for context. **✅ Use when:** loading documents/records with
  no side effect. **🚫 Avoid → `@tool`:** when there's an action. **⚠️:** resources are app-controlled, not model-invoked actions.

#### `@mcp.prompt()` — a reusable template
- **What & why:** a user-selectable prompt template. **✅ Use when:** standardising a repeated instruction.

**Transport & Context:** run **stdio** for dev/desktop, **streamable-http** for production
(`FastMCP(stateless_http=True, json_response=True)`); the injected **`Context`** gives `ctx.info()` /
`ctx.report_progress()`. Iterate locally with `uv run mcp dev`.

> 🔬 **Under the hood:** your type hints → a JSON schema → JSON-RPC messages. The *same* server code works over
> any transport — you swap stdio for streamable-http without touching the tool functions.

## 🚀 Stage 3 — In Practice / Why It Matters
"Build an MCP server" is the hands-on agentic JD ask, and FastMCP makes it three decorators: tools for actions,
resources for data, prompts for templates. The win is reuse — the inventory/Postgres/ticketing server you write
once is consumed by *every* MCP-aware agent and the Phase 3 milestone. The design decision you'll be tested on
is **tool vs resource**: anything with a side effect is a tool; anything that's just read-for-context is a resource.

## ⚖️ Variations & When to Use
| Decorator | Use when | Avoid when → use instead | Gotcha |
|---|---|---|---|
| **`@mcp.tool()`** | the agent must *act* (side effect) | pure read → **`@mcp.resource`** | hints+docstring drive the schema |
| **`@mcp.resource()`** | expose data for context | an action → **`@mcp.tool`** | app-controlled, not an action |
| **`@mcp.prompt()`** | reusable instruction template | dynamic logic → **`@mcp.tool`** | user-controlled |
| **stdio** transport | local dev / desktop | production → **streamable-http** | same machine only |
| **streamable-http** | production / remote | local dev → **stdio** | the prod default |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Model uses the tool poorly | no type hints / weak docstring | add hints + a clear docstring (they become the schema) |
| Read-only data modelled as a tool | tool/resource confusion | use `@mcp.resource` for reads |
| Works locally, not in prod | running on stdio | run with `transport="streamable-http"` |
| Can't debug the server | no dev loop | iterate with `uv run mcp dev` |

## 📌 Quick Reference
- **FastMCP + three decorators:** `@mcp.tool` (act) · `@mcp.resource` (read) · `@mcp.prompt` (template).
- **Schema from type hints + docstring.** **Context:** `ctx.info` / `ctx.report_progress`.
- **Transport:** `stdio` (dev) → `streamable-http` (prod). Dev loop: `uv run mcp dev`.

## 🛑 STOP — Self-Check
You want to expose "current inventory level" to agents. Tool or resource — and why?

<details><summary>Answer</summary>

A **resource** (`@mcp.resource`). Reading the inventory level is **read-only context with no side effect**, which
is exactly what resources are for (GET-like, app-controlled). A **tool** is for *actions* — e.g. "place an order"
that *changes* inventory. Modelling a pure read as a tool blurs the actions/data line MCP is built on.
</details>

⏭️ **Next:** 03 — Enterprise integrations + security.
