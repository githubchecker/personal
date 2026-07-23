# 08 — Milestone: Multi-Provider LLM Router

> Phase 1 · Module 1.2 · Capstone project · ties together lessons 01–06

## 🗺️ What you're building

A **multi-provider LLM router** built on **LiteLLM**: it **routes each request to the right model by
task type**, **fails over automatically** when a provider is down, and **logs the cost per call**.
This is the Road Map's Module 1.2 milestone, exercising the whole module:

- **Provider SDKs** (lessons 01–03) — the models you route between (OpenAI / Anthropic / Azure).
- **LiteLLM** (lesson 04) — the unified interface + `Router` with fallbacks.
- **Ollama** (lesson 05) — a free local model as the cheap tier.
- **Structured outputs** (Module 1.3 preview) — for the classification task.

## 🎯 The spec

1. A `route(task_type, prompt)` function that picks a model **by task** (e.g. cheap/local for
   classification, frontier for reasoning, a vision model for images).
2. **Automatic failover**: if the chosen provider errors, fall back to another — no code change at the
   call site.
3. **Cost logging** per call (LiteLLM reports response cost).

## ⚙️ Scaffold (fill in the task map + models)

```python
# pip install litellm
import os
from litellm import Router, completion_cost

os.environ["OPENAI_API_KEY"] = "..."          # each provider's standard env var (lesson 04)
os.environ["ANTHROPIC_API_KEY"] = "..."

# Map a TASK TYPE -> a model alias; each alias has primary + fallback backends.
router = Router(
    model_list=[
        # "cheap" tier: local first, cloud as backup
        {"model_name": "cheap",     "litellm_params": {"model": "ollama/llama3.2"}},
        {"model_name": "cheap",     "litellm_params": {"model": "openai/gpt-4o-mini"}},
        # "reasoning" tier: frontier model, cross-provider failover
        {"model_name": "reasoning", "litellm_params": {"model": "openai/gpt-4o"}},
        {"model_name": "reasoning", "litellm_params": {"model": "anthropic/claude-sonnet-4-20250514"}},
    ],
    fallbacks=[{"cheap": ["cheap"]}, {"reasoning": ["reasoning"]}],   # auto-failover within a tier
)

TASK_TO_ALIAS = {            # route BY TASK TYPE
    "classification": "cheap",
    "extraction":     "cheap",
    "reasoning":      "reasoning",
    "summarization":  "reasoning",
}

def route(task_type: str, prompt: str):
    alias = TASK_TO_ALIAS.get(task_type, "cheap")     # default to cheap
    resp = router.completion(                          # LiteLLM picks a healthy backend (lesson 04)
        model=alias,
        messages=[{"role": "user", "content": prompt}],
    )
    cost = completion_cost(completion_response=resp)   # cost logging
    print(f"[{task_type} -> {alias}] cost=${cost:.6f}")
    return resp.choices[0].message.content             # always OpenAI-format (lesson 04)

print(route("classification", "Is 'I want a refund' billing or technical?"))
print(route("reasoning", "Plan a 3-step migration from a monolith to microservices."))
```

## ✅ Success criteria

- [ ] Different `task_type`s route to **different model tiers** (cheap vs reasoning).
- [ ] Killing/blocking the **primary** backend → the call **still succeeds** via the fallback.
- [ ] Every call **logs its cost**; you can total cost per task type.
- [ ] The call site is **provider-agnostic** — it calls an alias, not a specific provider.

## 🚀 Stretch (toward the Phase 1 capstone)

- Add a **vision** tier and route image tasks to a vision-capable model (Module 1.2 lessons 01–02).
- Enforce a **budget** (stop routing to expensive tiers once a daily cost cap is hit).
- Drop this router **inside** the Module 1.1 gateway so the streaming service is multi-provider.

## 🛑 STOP — Self-Check

Why route **by task type** to model *aliases* (`"cheap"`, `"reasoning"`) with fallbacks, instead of
hard-coding a specific provider/model at each call site?

<details><summary>Answer</summary>

Routing to **aliases** keeps the **call site provider-agnostic**: the code says *what kind of task* it
is, and the router decides *which model* and *which provider* — so you can swap models, change the
cheap/reasoning mapping, or add providers **in one place** without touching callers. The **fallbacks**
give **automatic resilience**: if the primary backend for a tier is down or rate-limited, LiteLLM
rolls over to another **without any code change**. Hard-coding a provider at each call site loses both
the easy swapping and the failover, and scatters cost/model decisions across the codebase.
</details>

---
🎉 **Module 1.2 fully complete** (lessons 01–07 + this milestone). Combine this router with the Module
1.1 streaming gateway and Module 1.3 prompting for the **Phase 1 capstone**.
