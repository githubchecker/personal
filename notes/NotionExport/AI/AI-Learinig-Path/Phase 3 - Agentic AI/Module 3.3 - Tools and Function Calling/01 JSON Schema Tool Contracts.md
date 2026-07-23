# 01 — JSON-Schema Tool Contracts & Function Calling

> Phase 3 · Module 3.3 · Lesson 1 · `[JD VERIFIED — ~80%, the single highest-frequency agentic skill]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** An LLM only produces **text** — it can't query your database or call an API on its
own. So how does it "use a tool"? Through **function calling**: you hand the model a **menu** of tools
described as **JSON Schema** (name, what it does, parameters), the model replies with a structured
**tool call** (which tool + arguments), *your code* runs it, and you feed the result back. Get the
**contract** (the description + schema) right and the model picks the correct tool with correct args; get
it sloppy and it calls the wrong thing or invents arguments. This is the foundation of every agent.

**Where this sits.** Module 3.1 used tools casually; this is the deep dive. Lesson 02 covers the LangChain
helpers; Lesson 03 builds real tools. Tools are also what MCP standardises (Module 3.4).

**Why care.** ~80% of agentic JDs — the highest-frequency skill in the phase. Writing reliable tool
contracts *is* agent engineering.

---

## 🔑 New Terms (plain English)

- **Function calling** — the model emitting a structured request to run one of your tools.
- **Tool contract / schema** — the JSON description of a tool: `name`, `description`, `parameters`.
- **JSON Schema** — a standard way to describe a data shape (types, required, enums) the model fills.
- **Tool call** — the model's output: tool name + arguments. **Not** the model running code.
- **`ToolMessage`** — the tool's result sent back, tagged with the matching `tool_call_id`.
- **Parallel tool calls** — the model requesting several tools at once.
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: ordering from a menu)

A tool schema is a **menu**: dish names, descriptions, and options ("size: S/M/L"). The model **orders**
(emits a tool call) using exact menu names and valid options; the **kitchen** (your code) cooks and sends
the plate back (`ToolMessage`). A vague menu → wrong orders; a clear one → exactly what you meant. **Aha!:**
the model never cooks — it *orders*, you cook, you serve the result back. Quality of the **menu wording**
decides whether it orders right.

---

## ⚙️ Stage 2 — How It Works

### 2.1 A tool = function + schema (auto-generated)

```python
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get current weather for a city. Use when asked about weather."""  # -> description
    ...
# becomes: {"name":"get_weather","description":"...","parameters":{
#   "type":"object","properties":{"city":{"type":"string"},
#   "unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["city"]}}
```

The model sees the schema, emits `{"name":"get_weather","args":{"city":"Paris"}}`; you run it; return a
`ToolMessage`. Two are non-negotiable: a **description that says *when* to use it**, and **typed params**.

### 2.2 Parameters (each a real choice)
- **Required vs optional** — required = always needed (`city`); optional = has default (`unit`). ✅ keep
  required minimal 🚫 don't make everything required ⚠️ model omits required → validation error.
- **enum** — constrain to a fixed set. ✅ categories (`["S","M","L"]`) 🚫 not for open text ⚠️ off-list ⇒ reject.
- **anyOf** — allow several shapes. ✅ flexible inputs 🚫 adds confusion if overused ⚠️ keep tight.

### 2.3 Results: success / error / partial — and parallel
Return success normally; on failure return an **error string the model can read** (not a crash) so it
retries; partial = note what's missing. **Parallel:** model may request several tools at once → run, return
each with its `tool_call_id`.

> 🔬 Under hood: tools sent with the prompt; model emits JSON; framework runs + appends `ToolMessage`. A
> strong **description** matters more than param names — it's the trigger.

---

## 🚀 Stage 3 / ⚖️

Reliability comes from contracts: clear description, typed/enum params, error-as-text. | Param: minimal required · enum for sets · anyOf sparingly | Result: ok/err/partial | parallel for independent calls.

---

## 🐛 Errors

| Symptom | Cause | Fix |
|---|---|---|
| Wrong tool | weak description | say *when* to use |
| Bad args | loose params | types/enum/required |
| Crash on fail | raised exception | return error string |
| Dup parallel | wrong ids | match `tool_call_id` |

---

## 📌 Quick Reference
Tool=name+description+typed params; description says **when**; results ok/err/partial; parallel→ids.

## 🛑 STOP
Model ignores `search_db` despite DB questions — why? <details><summary>A</summary>Description doesn't say *when*; rewrite "Use for questions about orders/customers" + typed params. The **description is the trigger**.</details>

⏭️ **Next:** Lesson 02 — LangChain tool patterns.
