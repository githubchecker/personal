# 03 — Prompt & Token Optimisation

> Phase 4 · Module 4.4 · Lesson 3 · `[OPTIONAL — 🟢 awareness; cut cost at scale]`

> ⚠️ Know these exist; implement only when burning real token spend.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** At scale, tokens = money. Four levers cut spend without quality loss: prompt
caching, batch inference, context compression, right-sizing.

## 🔑 New Terms
**Prompt caching** (`cache_control: ephemeral`, ~90% off repeated system prompts) · **Batch API** (~50%
off, async) · **LLMLingua-2** (3–5× context compression) · **right-sizing** (smallest model that passes
eval). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: buy in bulk (batch), reuse the boilerplate (prompt cache), trim filler (compress), don't overbuy (right-size). **Aha!:** big savings, ~same quality.

## ⚙️ Stage 2 — four levers (each a mini-reference)
- **Prompt caching** — mark a big repeated prefix `cache_control: {"type":"ephemeral"}`; ~90% off the cached
  tokens. **✅ Use when:** a large shared system prompt every call. **🚫 Avoid:** prompts that change each call. **⚠️:** cache window expires; structure prompt prefix-stable.
- **Batch API** — submit bulk requests async (OpenAI/Anthropic); ~50% off. **✅:** non-urgent volume. **🚫 → realtime:** user-facing. **⚠️:** results in hours, not seconds.
- **LLMLingua-2** — compress retrieved context 3–5× by dropping low-information tokens. **✅:** long contexts. **🚫:** already-tight prompts. **⚠️:** over-compress hurts quality — measure.
- **Right-sizing** — benchmark accuracy across model sizes; pick the cheapest that passes eval. **✅:** always. **⚠️:** re-check when models update.

> 🔬 Don't micro-optimise early — measure spend first, then apply the lever that hits the biggest bill.

## ⚖️ repeated prompt → cache · bulk → batch · long context → compress · always right-size. 🐛 over-compress→quality drop; batch≠realtime. 📌 cache + batch + compress + right-size; measure first.
## 🛑 Same 5k-token system prompt every call — cheapest cut? <details><summary>A</summary>**Prompt caching** (ephemeral) — ~90% off the repeated prefix; pair with right-sizing.</details>

⏭️ **Next:** 04 — Fine-tuning overview.
