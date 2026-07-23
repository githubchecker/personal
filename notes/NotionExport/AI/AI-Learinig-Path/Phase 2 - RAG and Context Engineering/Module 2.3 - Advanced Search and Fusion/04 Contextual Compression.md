# 04 — Contextual Compression (LLMLingua)

> Phase 2 · Module 2.3 · Lesson 4 · `[OPTIONAL — awareness]`

> ⚠️ **Optional / awareness only.** Useful at depth for Principal/Staff work. At Lead/Architect level,
> know **what it is and when it helps**; build it only when an existing RAG system is hitting context
> limits or cost. (Tool/model names are 2026 examples.)

## 🗺️ Stage 0 — Concept Map

**The problem first.** Even after hybrid search and reranking, each retrieved chunk usually contains a few
**genuinely relevant sentences** wrapped in **filler** — boilerplate, tangents, repeated headers. You pay
for all of it (tokens), and the filler dilutes the signal and feeds **lost-in-the-middle** (Phase 1).
**Contextual compression** shrinks the retrieved context *before* it reaches the LLM — keeping the useful
parts, dropping the rest.

**Where it sits.** An *optional* polish step right before generation: retrieve → fuse → rerank →
**compress** → prompt. Reach for it only when context size or cost is the bottleneck.

## 🔑 New Terms (plain English)

- **Contextual compression** — shrinking retrieved chunks to just the parts relevant to the query.
- **Extractive compression** — *keep* only the relevant sentences from each chunk (delete the rest).
- **LLMLingua** — a tool that compresses a prompt by dropping low-information tokens, ~3–5× smaller, with
  little quality loss.
- **Lost-in-the-middle** — models attend worst to the middle of a long context (Phase 1) — compression
  shortens the context so there's less "middle."
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: highlighting before you hand over a report)

Instead of handing your boss a 20-page report, you **highlight the three relevant paragraphs** and hand
over just those. Same answer, a fraction of the reading. Contextual compression does that automatically to
retrieved chunks — keep what answers the query, drop the filler — so the LLM reads less, faster, cheaper,
and with the key facts not buried.

**The "Aha!":** retrieval finds the right *chunks*; compression trims them to the right *sentences/tokens*
— a second, finer filter that cuts cost and lost-in-the-middle.

## ⚙️ Stage 2 — How It Actually Works (overview)

Two flavours:

- **Extractive (sentence-level) compression** — score each sentence in each retrieved chunk against the
  query and keep only the relevant ones. (LangChain's `ContextualCompressionRetriever` wraps a base
  retriever with an extractor.)
- **Token-level compression (LLMLingua / LLMLingua-2)** — a *small* model estimates how much information
  each token carries and **drops the low-information ones**, compressing the prompt ~3–5× while preserving
  the meaning the big LLM needs.

```python
# Conceptual shape (LangChain extractive compression):
# retrieve chunks -> a compressor keeps only query-relevant sentences -> shorter context -> LLM
from langchain.retrievers import ContextualCompressionRetriever
compressed = ContextualCompressionRetriever(base_retriever=hybrid_retriever, base_compressor=extractor)
```

> 🔬 **Under the hood:** LLMLingua uses a **small language model** to measure each token's "surprise"
> (information content) and prunes the predictable/low-value ones — the big LLM can still reconstruct the
> meaning from what's left. Extractive compression is simpler: it's relevance-scoring at the *sentence*
> level instead of the *chunk* level. Either way, fewer tokens = lower cost + less lost-in-the-middle.

## ⚖️ When to use it (and when not)

| Situation | Compression? |
|---|---|
| RAG cost is high from large contexts | ✅ Yes — compress to cut tokens |
| Long contexts and lost-in-the-middle hurting answers | ✅ Yes — shorten the middle |
| Retrieval/rerank already return tight, small contexts | 🚫 No — little to gain, adds a step + latency |
| Early build, not yet optimising | 🚫 No — get retrieval + reranking right first |

> Decision rule (awareness): **optimise retrieval and reranking first; add contextual compression only
> when an existing RAG is hitting context-size or cost limits.**

## 📌 Quick Reference

- **Contextual compression** = trim retrieved chunks to the query-relevant parts before the LLM reads them.
- **Extractive** (keep relevant sentences) · **LLMLingua** (drop low-information tokens, ~3–5×).
- **When:** cost/context-limit problems on an already-built RAG; otherwise skip.

## 🛑 STOP — Self-Check

Your RAG already does hybrid search + reranking and returns a tight top-5 of short, on-topic chunks — but
someone suggests adding LLMLingua compression. Is it worth it here, and why or why not?

<details>
<summary>Answer</summary>

Probably **not** — and that's the point of it being optional. Contextual compression earns its keep when
contexts are **large** (high token cost) or **long enough to trigger lost-in-the-middle**. If reranking
already yields a **tight, small** top-5, there's little filler left to remove, so compression mostly adds
**latency and complexity** for marginal savings. Reach for it only when an existing RAG is genuinely
**hitting context-size or cost limits** — fix retrieval and reranking first.
</details>
