# 01 — Semantic Caching

> Phase 4 · Module 4.4 · Lesson 1 · `[JD VERIFIED — 40–70% of LLM spend is cacheable]`

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Users ask the same thing worded differently — and you pay full price each time.
**Semantic caching** embeds the query, searches a cache, and returns a stored answer if similarity >
threshold. "Reset password?" hits "How do I reset my password?" — no LLM call. 40–70% of enterprise spend.

## 🔑 New Terms
**Semantic cache** (match by meaning, not exact text) · **GPTCache** · **similarity threshold** · **cache
key** = query-embedding + model + system-prompt hash. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a clerk who remembers the gist — "we answered this last week" — no rework. An exact cache misses paraphrases; a semantic one catches them. **Aha!:** cache on meaning, not exact text.

## ⚙️ Stage 2 — how it works
```python
from gptcache import cache; from gptcache.adapter import openai
cache.init(embedding_func=embed, similarity_threshold=0.95)   # tune: 0.95 high precision
# query "How do I reset my password?" -> embed -> vector-search cache ->
#   sim 0.97 vs cached "reset password?" > 0.95 -> RETURN cached answer (no LLM call, ~0 cost)
```
**Pipeline:** embed the query → vector-search the cache → if max similarity > threshold, **return the cached
answer** (no LLM call, ~$0); else call the LLM and **store** the new answer.

#### Cache key — what makes two queries "the same"
- **What & why:** the key is the **query embedding + model + system-prompt hash** — because a different model
  or prompt would produce a different answer. **✅ Use when:** always. **⚠️ Gotcha:** omit model/prompt and answers
  **bleed** across configs (you serve a GPT-4o answer to a mini request).

#### Similarity threshold — the precision dial
- **What & why:** how close a match must be to count as a hit. **✅ High (0.95+):** precise, fewer wrong hits.
  **🚫 Avoid → low threshold:** more hits but you start returning answers to *different* questions. **⚠️:** tune on real traffic.

#### TTL & what not to cache
- **What & why:** time-to-live keeps answers fresh; **never cache volatile or personalised** answers (prices,
  balances, "my orders"). **✅ Use when:** stable Q&A. **🚫 Avoid → caching volatile data:** stale/wrong answers. **⚠️:** short TTL for semi-fresh data.

**Backend:** GPTCache is a drop-in; for scale use **Redis / pgvector** with your own embedding step.

> 🔬 **Under the hood:** 40–70% of enterprise LLM spend is **repeat or paraphrased** queries; a cache hit is
> near-free and near-instant. The cache is just a vector store keyed by meaning — the same retrieval idea as RAG,
> applied to answers instead of documents.

## 🚀 Stage 3 — In Practice / Why It Matters
Semantic caching is usually the **single biggest cost lever** in a production LLM app: support bots, FAQ
assistants, and internal copilots get the same questions worded a hundred ways, and you only pay for the
answer once. Teams put it in front of the LLM, set a high threshold for precision, exclude personalised/
volatile responses, and watch 40–70% of spend (and latency) disappear on the cacheable slice. The discipline
is knowing **what not to cache** so you never serve a stale price or another user's data.

## ⚖️ Variations & When to Use
| The query is… | Decision | Why |
|---|---|---|
| Stable, repeated FAQ | **cache, high threshold** | cheap, safe hits |
| Semi-fresh (docs that update) | **cache + short TTL** | balance freshness vs cost |
| Volatile (price, balance) | **don't cache** | must be live |
| Personalised ("my orders") | **don't cache** (or per-user key) | avoid cross-user bleed |
| Small app / prototype | **GPTCache** drop-in | fastest to wire |
| High scale | **Redis / pgvector** | control + throughput |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Wrong answer to a similar-but-different question | threshold too low | raise threshold (0.95+) |
| GPT-4o answer served to a mini request | key omits model/prompt | key on embedding **+ model + prompt hash** |
| Stale prices/balances returned | caching volatile data | don't cache it (or short TTL) |
| One user sees another's data | shared key on personalised answers | per-user key, or don't cache |

## 📌 Quick Reference
- **Flow:** embed → vector-search cache → hit if sim > threshold (return, ~$0) → else call LLM + store.
- **Key = embedding + model + system-prompt hash.** Threshold high (0.95+). **TTL** for freshness.
- **Never cache** volatile/personalised answers. GPTCache to start; Redis/pgvector at scale.

## 🛑 STOP — Self-Check
Your cache starts returning **last week's prices**. What went wrong, and how do you fix it without losing the cost savings?

<details><summary>Answer</summary>

You **cached volatile data**. Prices change, but a cached answer doesn't — so it goes stale. Fix: **don't cache
volatile/personalised responses** at all (or give them a very short **TTL**), keep the semantic cache for
**stable Q&A** (policies, how-tos, definitions), and make sure the **key includes the model + prompt** so configs
don't bleed. You keep the 40–70% savings on the cacheable slice without serving stale facts.
</details>

⏭️ **Next:** 02 — Circuit breakers & fallbacks.
