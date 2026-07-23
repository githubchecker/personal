# 02 — Arize Phoenix & OpenTelemetry

> Phase 4 · Module 4.2 · Lesson 2 · `[OPTIONAL — 🟢 awareness; self-host / framework-agnostic obs]`

> ⚠️ LangSmith covers ~90%. Know Phoenix + OTel for self-host / non-LangChain / cross-stack tracing.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** LangSmith is hosted + LangChain-centric. Some orgs need **self-hosted** or
**framework-agnostic** observability, or to merge AI traces with existing service traces. **Phoenix**
(self-host, OpenInference) and **OpenTelemetry** (the OTel standard) fill that.

## 🔑 New Terms
**Phoenix** (open-source, self-host, UMAP embedding viz, drift) · **OpenInference** · **OpenTelemetry**
(vendor-neutral tracing; export to Azure Monitor). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: Phoenix = run your own black box recorder; OTel = one trace standard across AI + services. **Aha!:** standardise spans, keep data in-house.

## ⚙️ Stage 2 — two complements to LangSmith (each a mini-reference)
- **Arize Phoenix** — open-source, self-hostable observability; framework-agnostic via OpenInference; can plot
  retrieved embeddings as a UMAP map and flag drift. **✅ Use when:** you must self-host or aren't on
  LangChain. **🚫 Avoid → LangSmith:** hosted + LangChain is fine. **⚠️ Gotcha:** you run and scale it yourself.
- **OpenTelemetry (OTel)** — the vendor-neutral tracing standard; `openinference-instrumentation-*` exports AI
  spans to Azure Monitor/App Insights so they sit beside your service traces. **✅ Use when:** correlating AI
  with a wider stack. **🚫 Avoid → LangSmith:** simplest path. **⚠️:** more wiring than a hosted tool.

> 🔬 Phoenix keeps data in-house; OTel keeps you vendor-neutral; LangSmith is the lowest-effort default.

## ⚖️ hosted/LangChain = LangSmith · self-host/agnostic = Phoenix · cross-stack = OTel. 🐛 vendor lock-in→OTel. 📌 Phoenix self-host + UMAP/drift; OTel cross-stack; LangSmith default.
## 🛑 Self-host obs across .NET + Python — pick? <details><summary>A</summary>**Phoenix** (self-host) + **OpenTelemetry** (one standard, export to Azure Monitor) to correlate both stacks.</details>

⏭️ **Next:** Module 4.3 — Prompt Injection Defence.
