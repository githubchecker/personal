# 04 — Weaviate

> Phase 2 · Module 2.2 · Lesson 4 · `[OPTIONAL — awareness]`

> ⚠️ **Optional / awareness only.** pgvector + **one** cloud vector DB (Pinecone *or* Qdrant) already
> cover ~85% of enterprise JDs. Weaviate knowledge is *additive*: know what it is and its two
> differentiators so you can speak to it — you don't need to build on it to be job-ready. (Syntax uses
> the Weaviate **v4** Python client; treat it as illustrative.)

## 🗺️ Stage 0 — Concept Map

**The problem first.** You already have three solid stores (pgvector, Pinecone, Qdrant). So why know a
fourth? Because **Weaviate** bundles two things into the database itself that you'd otherwise wire up by
hand: **native hybrid search** (keyword **and** vector in *one* query — Module 2.3) and a **generative
module** (retrieve *and* call an LLM in *one* hop). In an architecture discussion, knowing this saves you
from re-explaining "why not just use Weaviate?".

**Where it sits.** Same **store** box — a fourth option, kept as awareness because it overlaps heavily
with Qdrant/Pinecone and isn't usually a hard JD requirement.

## 🔑 New Terms (plain English)

- **Weaviate** — an open-source vector database (self-host or cloud) with built-in hybrid search and
  optional generation.
- **Collection** *(class)* — Weaviate's table of objects (each with properties + a vector).
- **Native hybrid search** — keyword (BM25) **and** vector search combined **inside one query** (you'll
  build this by hand in Module 2.3; Weaviate ships it).
- **Generative module** — "retrieve then ask an LLM" done in a single call from the database.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: a warehouse with a built-in clerk)

Pinecone/Qdrant are warehouses that hand you the boxes you asked for. **Weaviate** is a warehouse with a
**built-in clerk**: ask in plain words and it *both* keyword-matches and meaning-matches in one go
(hybrid), and can even **summarise the boxes for you** before handing them over (the generative module).
Convenient — but it's one more system, and you can assemble the same pieces yourself.

**The "Aha!":** Weaviate's pitch is *batteries-included* — hybrid search and generation built into the
DB. Its trade-off is *one more platform to run* when you may already have the pieces.

## ⚙️ Stage 2 — How It Actually Works (overview)

```python
# pip install weaviate-client     (v4)
import weaviate
client = weaviate.connect_to_local()                 # or connect_to_weaviate_cloud(...)

docs = client.collections.get("Doc")

# Native HYBRID search — keyword + vector in ONE query (alpha blends the two):
results = docs.query.hybrid(query="annual leave policy", alpha=0.5, limit=5)
#   alpha=1.0 -> pure vector · alpha=0.0 -> pure keyword (BM25) · 0.5 -> equal blend

# Generative module — retrieve AND have an LLM answer, in one call:
answer = docs.generate.near_text(query="vacation days?",
                                 grouped_task="Answer using the retrieved documents.")
```

- **Native hybrid search** is the headline: in Module 2.3 you'll build hybrid search + Reciprocal Rank
  Fusion yourself; Weaviate offers it as a single `hybrid(..., alpha=…)` call.
- The **generative module** collapses retrieve + generate into one hop — convenient, but it couples your
  database to your LLM choice.

> 🔬 **Under the hood:** Weaviate stores objects with both an inverted **keyword** index (for BM25) and a
> **vector** index (HNSW), so it can run both searches and fuse the scores in one query — that's what
> "native hybrid" means. The generative module just calls a configured LLM with the retrieved objects.

## ⚖️ Where Weaviate fits (vs the others)

| If you want… | Reach for |
|---|---|
| Vectors next to data you already run | **pgvector** (Postgres) |
| Fully-managed, auto-scaling, zero-ops | **Pinecone** |
| Open-source + rich filtering + quantization | **Qdrant** |
| **Built-in** hybrid search + generation in the DB | **Weaviate** |

> Decision rule (awareness): **default to pgvector + (Pinecone or Qdrant).** Choose Weaviate only when
> its built-in hybrid/generative features genuinely save you work *and* you're happy to run it. For
> learning, you'll build hybrid search yourself in **Module 2.3** — which is the more transferable skill.

## 📌 Quick Reference

- **Weaviate = open-source vector DB with built-in hybrid search (`alpha` blends keyword↔vector) + a generative module.**
- Differentiators: `query.hybrid(alpha=…)` and `generate.near_text(...)`.
- **When:** you want those batteries included; otherwise pgvector + Pinecone/Qdrant cover most JDs.

## 🛑 STOP — Self-Check

In one sentence: what is Weaviate's main *differentiator* versus Pinecone/Qdrant, and why is it
nonetheless **awareness-only** for this curriculum?

<details>
<summary>Answer</summary>

Weaviate's differentiator is **built-in native hybrid search** (keyword + vector in one query, via
`alpha`) **and a generative module** (retrieve + LLM answer in one hop) baked into the database. It's
awareness-only because **pgvector + one cloud vector DB (Pinecone/Qdrant) already cover ~85% of JDs**,
and you'll *build* hybrid search yourself in Module 2.3 — a more transferable skill than relying on one
vendor's built-in version.
</details>
