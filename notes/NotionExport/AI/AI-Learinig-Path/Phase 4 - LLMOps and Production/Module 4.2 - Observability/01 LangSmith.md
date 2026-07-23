# 01 — LangSmith: Tracing & Observability

> Phase 4 · Module 4.2 · Lesson 1 · `[JD VERIFIED — ~90% of observability needs]`

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** An agent makes dozens of LLM/tool calls; when an answer is wrong or slow, *which
step* failed? **LangSmith** records every run as a trace (runs/spans, inputs/outputs, tokens, latency) so
you can debug, filter (faithfulness<0.8), build datasets from real traffic, and version prompts.

**Why care:** "the most-named observability tool"; pairs natively with LangGraph (Phase 3).

## 🔑 New Terms
**Trace** (full run) · **Run/Span** (step) · **dataset/experiment** (eval over traces) · **annotation
queue** (human labels) · **Hub** (prompt versioning). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a flight recorder — every step logged with timing/cost; replay to find the failure. **Aha!:** a trace turns a black box into glass.

## ⚙️ Stage 2 — How It Works
```python
# Auto-trace any LangChain/LangGraph app — zero code changes, just env vars:
#   LANGSMITH_API_KEY=...  LANGCHAIN_TRACING_V2=true  LANGCHAIN_PROJECT=prod
# Trace your OWN functions:
from langsmith import traceable
@traceable                              # wraps function -> a span with inputs/outputs/tokens/latency
def answer(q): return rag(q)
# Evaluate over a saved dataset:
from langsmith import Client; from langsmith.evaluation import evaluate
evaluate(lambda x: rag(x["q"]), data="qa-set", evaluators=[faithfulness_eval])
```
- **Trace anatomy** — runs/spans, inputs/outputs, token counts, latency, cost per step. **Filter** traces (faithfulness<0.8, latency>2s) to find failures. **Datasets** — turn real traces into a test set; **experiments** compare prompt/model versions on it. **Annotation queue** — humans label traces → fine-tune/eval data. **Hub** — version + share prompts. Pairs with LangGraph (Phase 3) automatically.
> 🔬 SDK callbacks emit a span per component (LLM, tool, node); the tree = the trace. Same data feeds debugging, cost dashboards, and eval datasets.

## 🚀 Stage 3 — In Practice / Why It Matters
When a production agent gives a wrong or slow answer, the trace is where you live: open the run, walk the
span tree, and see exactly which LLM call hallucinated or which tool timed out — with tokens and cost per
step. Teams turn **real failing traces into a dataset**, run **experiments** to compare a fixed prompt/model
against it, and keep an **annotation queue** where humans label edge cases that become eval + fine-tune data.
Prompts are versioned in the **Hub** so a change is reviewable and reversible. Observability is what turns
"the bot feels flaky" into "span 3 (the reranker) adds 1.8 s on long queries."

## ⚖️ Variations & When to Use
| Your situation | Tool | Why |
|---|---|---|
| Hosted, on LangChain/LangGraph | **LangSmith** | ~90% of needs; zero-config auto-tracing |
| Must self-host / not on LangChain | **Phoenix** (next lesson) | open-source, framework-agnostic |
| Correlate AI with wider service traces | **OpenTelemetry** | vendor-neutral standard, export to Azure Monitor |
| Trace your own non-LLM functions | `@traceable` | adds a span around any function |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Nothing shows up | tracing not enabled | set `LANGCHAIN_TRACING_V2=true` + `LANGSMITH_API_KEY` |
| Trace volume explodes cost | logging every call | **sample** traces in high-traffic prod |
| PII captured in traces | raw inputs logged | **mask** before logging (Presidio, 4.3.02) |
| Can't compare versions | no saved dataset | build a **dataset** from traces, run **experiments** |

## 📌 Quick Reference
- **Turn on:** env vars (`LANGCHAIN_TRACING_V2=true`, `LANGSMITH_API_KEY`, `LANGCHAIN_PROJECT`) — auto-traces
  LangChain/LangGraph. **Custom:** `@traceable` on any function.
- **A trace** = runs/spans with inputs/outputs, tokens, latency, cost per step; **filter** to find failures.
- **Datasets + experiments** compare versions; **annotation queue** = human labels; **Hub** = prompt versions.
- Sample to control cost; mask PII before logging.

## 🛑 STOP — Self-Check
Your agent is occasionally slow, but only sometimes. How do you find which step is responsible?

<details><summary>Answer</summary>

Open the **traces** and inspect the **per-span latency** (and tokens). Each step — every LLM call, tool, and
graph node — is its own span with timing, so the slow one stands out. **Filter** to high-latency outliers
(e.g. latency > 2 s), find the recurring slow span (often retrieval/reranking or a tool call), and optimise
*that* step instead of guessing at the whole pipeline.
</details>

⏭️ **Next:** 02 — Phoenix & OpenTelemetry.
