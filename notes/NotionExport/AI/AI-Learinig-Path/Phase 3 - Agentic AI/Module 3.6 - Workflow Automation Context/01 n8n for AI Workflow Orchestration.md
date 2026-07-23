# 01 — n8n for AI Workflow Orchestration

> Phase 3 · Module 3.6 · Lesson 1 · `[OPTIONAL — 🟢 architect awareness; n8n-vs-LangGraph + webhook integration]`

> ⚠️ **Awareness.** Know what n8n is, when it beats LangGraph, and how it plugs into a Python backend. A
> 2–3 hour quickstart is enough for any interview question.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Not every AI task needs a code-first agent. Lots of business automation is *connect
A to B with an LLM step in the middle* — "SharePoint upload → OCR → embed → pgvector." **n8n** is a
low-code, self-hostable automation platform for exactly that: drag-and-drop nodes, hundreds of connectors,
AI nodes. The architect call: **n8n for business-process automation, LangGraph for complex reasoning.**

## 🔑 New Terms
**n8n** — low-code automation (self-host on Azure Container Apps). **AI node** — LLM/vector/agent step.
**webhook** — HTTP trigger linking n8n ↔ FastAPI. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a conveyor with snap-in stations (email→OCR→LLM→DB). Wire boxes, no code. **Aha!:** glue/triggers, not deep reasoning.

## ⚙️ Stage 2 — when n8n, and how it joins your AI
- **n8n** — a low-code, self-hostable automation platform (drag-drop nodes + hundreds of connectors + AI
  nodes). **✅ Use when:** event-driven business glue ("on upload, OCR, embed, store"), many integrations,
  non-developers maintaining it. **🚫 Avoid → LangGraph:** complex stateful reasoning, audit, multi-agent.
  **⚠️ Gotcha:** heavy logic crammed into n8n gets unmaintainable — move that to code.
- **n8n + Python:** the bridge is a **webhook** — n8n calls your FastAPI endpoint for the hard AI step.
  E.g. *Azure Event Grid → n8n → your LLM service*; or *SharePoint upload → OCR → embed → pgvector*.

> 🔬 n8n orchestrates *services*; offload real reasoning to FastAPI/LangGraph via webhook — and secure that webhook.

## ⚖️ business-process automation = n8n · reasoning agents = LangGraph · combine via webhook. 🐛 complex logic in n8n→move to code; unauth webhook→lock it down. 📌 n8n = low-code glue; LangGraph = reasoning; bridge via FastAPI webhook.
## 🛑 "Daily: pull tickets → summarise → post to Slack" vs "multi-agent analyst" — tool each? <details><summary>A</summary>Scheduled glue = **n8n**; stateful multi-agent reasoning = **LangGraph**. Bridge them with a webhook.</details>

✅ **Phase 3 complete** — see the [Phase 3 README](../README.md).
