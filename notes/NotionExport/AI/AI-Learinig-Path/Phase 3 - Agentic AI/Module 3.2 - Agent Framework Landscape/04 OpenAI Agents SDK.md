# 04 — OpenAI Agents SDK

> Phase 3 · Module 3.2 · Lesson 4 · `[ARCHITECT AWARENESS — 🟢 know it, build only if GPT-centric]`

> ⚠️ **Awareness.** Understand the primitives and when to recommend it; build only for GPT-centric work.
> Currency: `openai-agents 0.17.x`.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** If you're already all-in on OpenAI, LangGraph can feel heavy. The **OpenAI Agents
SDK** is the low-friction option: agents, **handoffs**, tools, **guardrails**, **sessions**, and built-in
tracing — minimal setup. Provider-agnostic (100+ models via LiteLLM) but richest on OpenAI.

**Why care:** appears alongside LangGraph in JDs; the architect default for "GPT-only, keep it simple."

---

## 🔑 New Terms

- **Agent** — LLM + instructions + tools + guardrails + handoffs.
- **Runner** — runs an agent (`Runner.run_sync`).
- **Handoff** — delegate to another agent (simpler than a LangGraph supervisor).
- **Guardrail** — input/output safety check. **Session** — auto conversation history.
  (See [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — Simple Idea (analogy: a concierge)

A concierge handles your request or **hands off** to a specialist; remembers you (**sessions**); won't do
the off-limits (**guardrails**). Lowest friction — if you stay in their hotel (OpenAI). **Aha!:** speed +
simplicity, trading LangGraph's deep control.

---

## ⚙️ Stage 2 — How It Works

```python
# pip install openai-agents
from agents import Agent, Runner
spanish = Agent(name="ES", instructions="Reply in Spanish")
triage = Agent(name="Triage", instructions="Hand off if Spanish", handoffs=[spanish])
print(Runner.run_sync(triage, "Hola").final_output)
```

The pieces, with when each fits:
- **Agent** — an LLM plus instructions, tools, guardrails, and a list of agents it can hand off to. **✅
  Use when:** GPT-centric work that wants minimal setup. **🚫 Avoid → LangGraph:** you need explicit stateful
  control flow. **⚠️ Gotcha:** persistence is thinner than LangGraph's.
- **Handoff** — one agent delegates to another (`handoffs=[other]`); simpler than wiring a supervisor graph.
  **✅ Use when:** light routing between a few specialists. **🚫 Avoid → LangGraph supervisor:** when you need
  audit/checkpointing. **⚠️:** loops between agents need a cap.
- **Guardrails / sessions / tracing** — input/output safety checks, automatic conversation memory, and a
  built-in trace dashboard, all out of the box. Provider-agnostic via LiteLLM, but richest on OpenAI.

> 🔬 Tools and MCP are supported; sandbox and realtime (voice) agents were added in 2026.

---

## 🚀 Stage 3 / ⚖️

GPT-centric + simple → OpenAI SDK; stateful/multi-provider/control → LangGraph; fast roles → CrewAI.

---

## 📌 Quick Reference

`Agent(instructions,tools,handoffs,guardrails)` + `Runner.run_sync` → `.final_output`. Low friction, GPT-first.

## 🛑 STOP

When OpenAI SDK over LangGraph? <details><summary>A</summary>GPT-only, low complexity, want built-in tracing/handoffs fast. Switch to LangGraph for stateful control, audit, multi-provider.</details>

⏭️ **Next:** Module 3.3 — Tool Definition & Function Calling.
