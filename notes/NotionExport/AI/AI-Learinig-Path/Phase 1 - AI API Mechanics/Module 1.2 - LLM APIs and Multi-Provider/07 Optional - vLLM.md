# 07 — (Optional) vLLM: High-Throughput Self-Hosting

> Phase 1 · Module 1.2 · Lesson 7 · `[OPTIONAL — awareness]`

> 🟡 **Optional / awareness.** Appears in ~25–35% of JDs, mostly ML-platform/infra roles. Know **what
> it is and when you'd reach for it** — that's enough here. Deep serving/LLMOps is Phase 4.

## 🗺️ Stage 0 — Concept Map

Ollama (lesson 05) runs a model locally for **one user**. **vLLM** serves open models to **thousands
of concurrent users** with high throughput — the tool teams use to **self-host at production scale**.
It builds on the local-models idea and previews Phase 4 (LLMOps).

## 🔑 New Terms (plain English)

- **vLLM** — a high-performance **inference server** for open LLMs.
- **Inference server** — software dedicated to serving model predictions fast, to many callers.
- **Throughput** — how many requests/tokens per second you can serve.
- **Continuous batching / PagedAttention** — vLLM's tricks for packing many requests onto a GPU efficiently.
- **OpenAI-compatible server** — vLLM exposes the OpenAI API, so your existing code works.

## 🎈 Stage 1 — The Simple Idea (analogy: home kitchen vs industrial kitchen)

Ollama is a **home kitchen** — one cook, a few meals. **vLLM is an industrial kitchen** — built to
serve thousands of orders per hour without falling over. Same recipes (open models), totally different
scale of operation.

**The "Aha!":** when self-hosting needs to serve **real production traffic**, you move from
"run a model" (Ollama) to "serve a model at scale" (vLLM).

## ⚙️ Stage 2 — How It Actually Works (awareness)

```powershell
pip install vllm
# Serve an open model with an OpenAI-compatible API on port 8000:
vllm serve meta-llama/Llama-3.1-8B-Instruct
```

```python
from openai import OpenAI                      # reuse the lesson-01 client — just repoint it
client = OpenAI(base_url="http://localhost:8000/v1", api_key="vllm")
client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

- Because it's **OpenAI-compatible**, vLLM drops into your existing code (and **LiteLLM** via
  `hosted_vllm/...`) — same pattern as Ollama, built for scale.
- It needs **GPUs** and MLOps care (deployment, autoscaling, monitoring) — that's Phase 4 territory.

### When to use it
- **Self-hosting at scale:** high volume where per-token cloud cost is large, or data must stay
  in-house. Otherwise a cloud API (01–03) or Ollama (05) is simpler.

## 🧠 Common Misconceptions

- **"vLLM is just Ollama for servers."** → Related goal (run open models), but vLLM is engineered for
  **high concurrent throughput** on GPUs; Ollama targets easy local single-user use.
- **"Self-hosting is always cheaper."** → Only at **high, steady volume**; GPUs + ops have real fixed
  costs. At low/spiky volume, a cloud API is usually cheaper and simpler.

## 📌 Quick Reference

- **vLLM = high-throughput inference server** for open models, **OpenAI-compatible** (`vllm serve ...`).
- Reach for it when **self-hosting at production scale**; needs **GPUs + MLOps** (Phase 4).
- Low/medium volume → cloud APIs (01–03) or Ollama (05) instead.

## 🛑 STOP — Self-Check

You can already run a model locally with Ollama. Why would a company bring in **vLLM** instead — and
what's the main cost of doing so?

<details><summary>Answer</summary>

A company moves to **vLLM** when it must **serve an open model to many concurrent users at production
scale** — vLLM's continuous batching/PagedAttention give far higher **throughput** on GPUs than
Ollama's single-user focus. The main cost is **infrastructure and operations**: you need **GPUs** and
MLOps work (deployment, scaling, monitoring), so it only pays off at **high, steady volume** — for
low/spiky traffic a cloud API or Ollama is cheaper and simpler.
</details>

---
🎉 **Module 1.2 (LLM APIs & Multi-Provider) complete.** You can call OpenAI, Claude, and Azure, unify
them with LiteLLM, run models locally with Ollama, drive **tool calling**, and know when to self-host
with vLLM. Next: **Module 1.3 — Programmatic Prompting** (structured outputs, prompt templates,
CoT/ReAct, context-window engineering).
