# 02 — Circuit Breakers & Model Fallbacks

> Phase 4 · Module 4.4 · Lesson 2 · `[JD VERIFIED — resilience + cost routing]`

> 🔬 LiteLLM `1.90` (router + budget). Builds on Phase 1 retries.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Providers rate-limit (429), error (500), go down. A single-provider app dies with
them. **Resilience:** retry with backoff, **circuit-break** a failing provider, **fall back** to another,
and **route by complexity** (cheap model for easy, frontier for hard) — with **budget caps**.

## 🔑 New Terms
**tenacity** (retry+backoff+jitter) · **pybreaker** (circuit breaker) · **fallback chain** (GPT-4o→mini→
Llama) · **LiteLLM router** (auto-fallback on 429/500) · **complexity router** · **budget_manager**. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: power fails over to a generator (fallback); a tripped breaker stops hammering a dead line; cheap jobs to junior, hard to senior. **Aha!:** never one provider.

## ⚙️ Stage 2 — the four layers (real code)
```python
from litellm import Router
router = Router(model_list=[
    {"model_name":"smart","litellm_params":{"model":"gpt-4o"}},
    {"model_name":"smart","litellm_params":{"model":"claude-sonnet-4"}},      # load-balance + failover
], fallbacks=[{"smart":["gpt-4o-mini","ollama/llama3.1"]}], num_retries=2)    # auto on 429/500
router.completion(model="smart", messages=[{"role":"user","content":"hi"}])
```
#### tenacity — retry with backoff
- **What & why:** retries **transient** failures (429, timeouts, 500s) with **exponential backoff + jitter**.
  **✅ Use when:** rate limits and blips. **🚫 Avoid → 4xx logic errors:** retrying a bad request just wastes calls.
  **⚠️ Gotcha:** always **cap attempts** — uncapped retries become a self-inflicted storm.

#### pybreaker — the circuit breaker
- **What & why:** after **N consecutive failures** it "opens" and **stops calling a dead provider** for a
  cooldown, failing fast instead of piling up. **✅ Use when:** a provider may go down. **🚫 Avoid → needless:** for
  a single stable call. **⚠️:** set a sensible **reset timeout** to probe recovery.

#### LiteLLM Router — multi-provider failover + load-balance
- **What & why:** one interface across providers with an automatic **fallback chain** (GPT-4o → 4o-mini → Ollama)
  on 429/500, plus load-balancing. **✅ Use when:** you can't afford a single-provider outage. **🚫 Avoid → single
  provider:** that *is* the outage. **⚠️:** tune `num_retries` and order the chain by cost/quality.

#### Complexity router — route by difficulty (cost)
- **What & why:** a cheap model handles easy requests; the frontier model only gets the hard ones. **✅ Use when:**
  cutting cost at scale. **🚫 Avoid → uniform routing:** when every request is genuinely hard. **⚠️:** a mis-route hurts quality — test the router.

**Also:** `budget_manager` enforces a **hard $ cap**; **Ollama** (local) is a free last-resort fallback.

> 🔬 **Under the hood:** the router tries providers **in order** on 429/500; the breaker **isolates** a dead
> provider so requests fail fast; backoff **smooths** spikes. Layered, they turn one provider's bad day into a
> transparent degradation instead of an outage.

## 🚀 Stage 3 — In Practice / Why It Matters
A single-provider app inherits every one of that provider's outages and rate limits. Production systems assume
failure: retry transient errors with backoff, **break** a failing provider, **fall back** across providers
(often ending at a local Ollama model), route easy work to cheap models, and **cap spend**. This is both a
**resilience** story (stay up when OpenAI 429s) and a **cost** story (don't pay frontier prices for "hello") —
which is why it's a recurring JD line.

## ⚖️ Variations & When to Use
| The problem is… | Use | Why |
|---|---|---|
| Transient 429 / timeout | **tenacity** retry + backoff | rides out blips |
| A provider is down | **pybreaker** | fail fast, stop hammering it |
| Need cross-provider failover | **LiteLLM Router** | automatic fallback chain |
| Cost too high at scale | **complexity router** | cheap model for easy work |
| Must not exceed a budget | **budget_manager** | hard $ cap |
| Free last resort | **Ollama** (local) | no per-call cost |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Retries become a request storm | no attempt cap | cap attempts; exponential backoff + jitter |
| Requests pile up on a dead provider | no breaker | **pybreaker** opens after N fails |
| Whole app dies with one provider | single provider | **LiteLLM** fallback chain |
| Frontier-model bill explodes | uniform routing | **complexity router**; budget cap |

## 📌 Quick Reference
- **Resilience stack:** backoff retry (**tenacity**) → **circuit breaker** (pybreaker) → **LiteLLM** fallback
  chain → **complexity router** → **budget cap**.
- Retry only **transient** errors, never 4xx logic errors. End the fallback chain at a **local model (Ollama)**.

## 🛑 STOP — Self-Check
Your primary GPT-4o deployment starts returning 429s under load. Describe the resilience chain that keeps the
app up *and* controls cost.

<details><summary>Answer</summary>

**Retry** the transient 429 with **exponential backoff + jitter** (capped). If failures persist, the **circuit
breaker** opens and stops hammering GPT-4o. The **LiteLLM Router** **falls back** GPT-4o → GPT-4o-mini → local
**Ollama/Llama**, so requests still succeed. Route **easy** requests to the cheap model (complexity routing) and
enforce a **budget cap** so failover spend can't run away. One provider's bad day becomes a transparent
degradation, not an outage.
</details>

⏭️ **Next:** 03 — Token optimisation.
