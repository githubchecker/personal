# 01 — BM25 / Sparse Retrieval

> Phase 2 · Module 2.3 · Lesson 1 · `[MUST KNOW — JD VERIFIED]`

## 🗺️ Stage 0 — Concept Map

**The problem first.** The vector search you built in Module 2.2 matches by **meaning** — great for
"vacation days" ≈ "annual leave." But meaning-search has a blind spot: **exact strings**. Ask for error
code **`X1234`**, product SKU **`A-9920`**, the surname **`Featherstonehaugh`**, or an exact legal
citation, and embeddings blur them into something generic — the precise token gets lost. A 40-year-old
algorithm, **BM25**, nails exactly those: it ranks by the **words actually present**. Real RAG uses
**both**.

**Where it sits.** This is the first half of **Module 2.3 (advanced search)**. Dense (vector) search +
**sparse (BM25)** search are the two retrievers you'll **fuse** in lesson 02 (hybrid search) and sharpen
in lesson 03 (reranking).

**Why care.** "Hybrid search" is in ~72% of RAG JDs, and you can't build it without understanding its
sparse half. Knowing *why dense misses exact matches* is a classic interview point.

## 🔑 New Terms (plain English)

- **Dense retrieval** — search by **meaning**, using embeddings (Module 2.1–2.2). Vectors are "dense"
  (every number is filled in).
- **Sparse retrieval** — search by **exact words**. The vector is mostly zeros — one slot per vocabulary
  word, non-zero only for words present — hence "sparse."
- **Lexical / keyword search** — another name for matching the literal words.
- **BM25** — the standard keyword-ranking algorithm: scores a document by the query words it contains,
  weighted by how *rare* and how *frequent* each word is.
- **Term frequency (TF)** — how often a query word appears in a document (more = more relevant).
- **Inverse document frequency (IDF)** — how *rare* a word is across all documents (rare words count more).
- **Tokenize** — split text into words (the units BM25 counts).
- **`rank_bm25`** — a small Python library for standalone BM25.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: a precise clerk vs an intuitive one)

Two clerks help you find documents. The **intuitive** one (dense/vectors) understands what you *mean* —
ask for "time off" and they bring "annual leave." The **precise** one (BM25) matches the **exact words** —
ask for "`X1234`" and they find the *one* file containing that string, which the intuitive clerk waved
away as "some code." Neither is enough alone: you want the intuitive clerk for paraphrase and synonyms,
and the precise clerk for IDs, codes, and rare names.

**The "Aha!":** dense = meaning, sparse/BM25 = exact words. Their weaknesses are opposite, which is *why*
you combine them (lesson 02).

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — go **dense-only** because embeddings are exciting, then watch retrieval fail
on the queries that matter most in enterprise search: part numbers, error codes, acronyms, exact names,
and rare jargon — all of which embed to something vague and never surface.

### 2.1 What BM25 actually scores

BM25 ranks a document by the **query words it contains**, with three sensible adjustments:
- **More occurrences** of a query word → higher score (**term frequency**), but with *diminishing
  returns* (the 10th "invoice" adds little over the 2nd).
- **Rarer words count more** (**IDF**) — matching "`X1234`" matters far more than matching "the."
- **Shorter documents** that contain the words rank higher (length normalization), so a giant document
  doesn't win just by being big.

You don't need to memorise the formula — you need to know it's **exact-word matching with smart
weighting**, and *when* to reach for it.

### 2.2 Standalone BM25 with `rank_bm25`

```python
# pip install rank_bm25
from rank_bm25 import BM25Okapi

docs = ["Reset your password in settings", "Error X1234 means the disk is full", "Annual leave policy…"]
tokenized = [d.lower().split() for d in docs]      # tokenize: split into words
bm25 = BM25Okapi(tokenized)

query = "error X1234".lower().split()
top = bm25.get_top_n(query, docs, n=3)             # rank docs by keyword score
print(top[0])                                      # -> "Error X1234 means the disk is full"
```

A dense/embedding search would likely *miss* that `X1234` document; BM25 puts it first.

### 2.3 Dense vs sparse — when each wins (the core contrast)

- **Dense (vector) retrieval** — match by meaning.
  - **✅ Use when:** paraphrases, synonyms, natural-language questions ("how do I take time off?").
  - **🚫 Avoid relying on it alone → add BM25:** queries with exact IDs, codes, SKUs, rare names, or exact phrases.
  - **⚠️ Gotcha:** it silently blurs precise tokens — `X1234` and `X1235` look almost identical to an embedder.
- **Sparse (BM25) retrieval** — match by exact words.
  - **✅ Use when:** exact terms matter — error codes, part numbers, names, legal citations, acronyms.
  - **🚫 Avoid relying on it alone → add dense:** the user's words differ from the document's ("time off" vs "annual leave").
  - **⚠️ Gotcha:** zero overlap of words = zero score — it can't match synonyms or paraphrases at all.

> The punchline: **their failure modes are opposite**, so production retrieval **combines** them — that's
> hybrid search (lesson 02).

### 2.4 BM25 in production (which tool)

| Scale / setting | Reach for |
|---|---|
| A prototype / small in-memory corpus | **`rank_bm25`** |
| Large-scale, real search infrastructure | **Elasticsearch / OpenSearch** (BM25 is their default) |
| Enterprise on Azure | **Azure AI Search** (BM25 + semantic ranker built in) |
| Already on Postgres | **Postgres full-text search** (`tsvector` / `ts_rank`) |

> 🔬 **Under the hood:** BM25 treats each document as a **bag of words** (counts, no order). The "sparse
> vector" view: imagine one slot per word in the whole vocabulary; a document's vector is mostly **zeros**,
> non-zero only for words it contains — the opposite of a dense embedding where every slot is filled.
> BM25 then scores the overlap, weighting by **TF** (how often) and **IDF** (how rare), normalised by
> document length. No model, no training — just counting, which is why it's fast and exact.

## 🚀 Stage 3 — In Practice / Why It Matters

Almost every serious RAG system is **hybrid**, and BM25 is the sparse half. Enterprise search is full of
exact-match queries — SKUs, ticket numbers, error codes, policy IDs, person names — where dense retrieval
quietly fails and BM25 shines. You'll fuse the two in lesson 02 (Reciprocal Rank Fusion) and then rerank
the merged list in lesson 03. Knowing **why** you need BM25 (not just *that* you do) is the JD-relevant
insight.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
|---|---|---|
| **Retriever** | dense vs sparse (BM25) vs **both** | **both** in production (hybrid, lesson 02) · dense alone only for pure paraphrase search · BM25 alone only for pure exact-match |
| **BM25 implementation** | `rank_bm25` vs Elasticsearch/OpenSearch vs Azure AI Search vs Postgres FTS | by scale: `rank_bm25` prototype · ES/OpenSearch big search · Azure AI Search on Azure · Postgres FTS if on Postgres |

> Decision rule: **never ship dense-only for enterprise search — add BM25 so exact IDs/codes/names are findable.**

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
|---|---|---|
| Exact codes/IDs never retrieved | Dense-only retrieval | Add BM25 (sparse) and fuse (lesson 02) |
| BM25 misses obvious synonyms | Sparse can't match meaning | Combine with dense retrieval |
| BM25 scores look random | Didn't tokenize consistently | Tokenize query **and** docs the same way (lowercase, split) |
| Common words dominate | Not using IDF / stopwords | BM25's IDF down-weights common words; optionally strip stopwords |

## 📌 Quick Reference (cheat-sheet)

```python
from rank_bm25 import BM25Okapi
bm25 = BM25Okapi([d.lower().split() for d in docs])     # tokenize the corpus
hits = bm25.get_top_n(query.lower().split(), docs, n=5) # exact-word ranking
```
- **Dense = meaning · Sparse/BM25 = exact words.** Opposite blind spots → **combine** (hybrid, lesson 02).
- BM25 weights by **TF** (how often) × **IDF** (how rare), length-normalised. Great for IDs/codes/names.

## 🛑 STOP — Self-Check

Your support-bot RAG works well for "how do I reset my password?" but completely fails when users paste an
exact error code like "`ORA-00942`". Why does dense (vector) retrieval miss it, and what do you add?

<details>
<summary>Answer</summary>

An embedding model maps `ORA-00942` to a **vague, generic** point in meaning-space — it has no real
"meaning," and similar codes (`ORA-00943`) look nearly identical — so dense retrieval can't pick out the
*exact* document mentioning it. You add **sparse retrieval (BM25)**, which matches the **literal token**
`ORA-00942` and ranks that document first. In production you run **both** and **fuse** the results
(hybrid search, lesson 02) so paraphrase queries *and* exact-code queries both work.
</details>
