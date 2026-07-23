# 05 — GraphRAG

> Phase 2 · Module 2.3 · Lesson 5 · `[OPTIONAL — awareness]`

> ⚠️ **Optional / mandatory architect *awareness*.** Know **what it is** and **when it wins** (multi-hop
> questions across scattered sources). Build it only if your target organisation explicitly uses
> graph-based retrieval. (Tool names are 2026 examples.)

## 🗺️ Stage 0 — Concept Map

**The problem first.** Standard RAG retrieves chunks **independently** by similarity. That's perfect for
"what's our refund policy?" — one chunk has the answer. It **fails** on two kinds of question:
1. **Multi-hop** — answers that require *connecting facts across several documents*: *"Which suppliers are
   affected if the Shenzhen plant that makes part P-12 goes offline?"* (plant → part → products →
   suppliers — no single chunk says all of it).
2. **Global / thematic** — *"What are the main themes across all 500 incident reports?"* — no single chunk
   summarises the whole corpus.

**GraphRAG** builds a **knowledge graph** (entities + how they relate) from your documents, so it can
*traverse* connections (multi-hop) and *summarise communities* of related entities (global questions).

**Where it sits.** An *alternative/complementary* retrieval architecture, kept as **architect awareness**
because it's powerful but expensive, and only wins for specific question types.

## 🔑 New Terms (plain English)

- **Knowledge graph** — data stored as **entities** (nodes) connected by **relationships** (edges):
  `(Shenzhen plant) —makes→ (part P-12) —used in→ (Product X)`.
- **Entity** — a thing the text mentions (a person, place, part, company).
- **Relationship** — how two entities connect ("makes", "reports to", "located in").
- **Multi-hop query** — a question whose answer requires following several relationships in a row.
- **Community detection** — grouping densely-connected entities into clusters, then summarising each
  cluster (for global questions).
- **NER (Named Entity Recognition)** — automatically pulling entities out of text (often via an LLM here).
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: a detective's evidence board)

Standard RAG is like grabbing the **three most relevant case files**. GraphRAG is the detective's
**string-and-pins evidence board**: every person, place, and object is a pin, and strings connect who knew
whom and what links to what. To answer *"how is the suspect connected to the warehouse?"* you **follow the
strings** across many files — something you can't do by reading three files in isolation.

**The "Aha!":** standard RAG retrieves *chunks*; GraphRAG retrieves *connections*. When the answer lives in
the **relationships between** facts (not in any one chunk), you need the graph.

## ⚙️ Stage 2 — How It Actually Works (overview)

1. **Build the graph (offline, LLM-heavy):** run each chunk through an LLM to extract **entities** and
   **relationships**, and merge them into one knowledge graph.
2. **Detect communities:** cluster densely-connected entities and generate a **summary** per cluster (this
   is what answers "global" questions).
3. **Query:** for a multi-hop question, **traverse** the graph from the question's entities along their
   relationships; for a global question, read the relevant **community summaries**. Often combined with
   normal vector retrieval (a hybrid of graph + chunks).

Tools you'd reach for: **Microsoft GraphRAG** (the well-known implementation), or **Neo4j** (a graph
database) **+ LangChain's** graph retriever.

> 🔬 **Under the hood:** the expensive part is **construction** — an LLM reads the *whole corpus* to extract
> entities/relationships, which costs many model calls and time. Once built, traversal is cheap and answers
> questions standard RAG simply can't, because the knowledge now lives in **edges between facts**, not just
> in the text of individual chunks.

## ⚖️ When GraphRAG wins (and when it doesn't)

| Question type | Best approach |
|---|---|
| Single-fact ("what's the refund policy?") | **Standard RAG** (cheaper, simpler) |
| Multi-hop across disparate sources | **GraphRAG** (follow relationships) |
| Global/thematic ("main themes across all docs?") | **GraphRAG** (community summaries) |
| Cost/latency-sensitive, simple Q&A | **Standard RAG** (graph construction is pricey) |

> Decision rule (awareness): **default to standard (hybrid) RAG; consider GraphRAG only when answers depend
> on connections across many documents (multi-hop) or on whole-corpus themes — and you can afford the
> graph-build cost.**

## 📌 Quick Reference

- **GraphRAG** = build a **knowledge graph** (entities + relationships) from docs, then traverse it.
- **Wins on:** multi-hop questions and global/thematic questions; **loses on:** simple single-fact Q&A (cost).
- Tools: **Microsoft GraphRAG**, **Neo4j + LangChain**. Construction is **LLM-heavy and expensive**.

## 🛑 STOP — Self-Check

Give one question your normal hybrid-RAG support bot would **fail**, and explain why **GraphRAG** would
answer it.

<details>
<summary>Answer</summary>

Example: *"If part **P-12** is recalled, which of our **products** and which **customers** are affected?"*
Normal RAG retrieves chunks by similarity, but **no single chunk** lists part → products → customers — the
answer lives in the **chain of relationships** spread across many documents. **GraphRAG** builds a
knowledge graph linking `part —used in→ product —bought by→ customer`, then **traverses** those edges to
assemble the full answer — a **multi-hop** path standard chunk-retrieval can't follow. (It's worth the
expensive graph build only when such connected questions are common.)
</details>
