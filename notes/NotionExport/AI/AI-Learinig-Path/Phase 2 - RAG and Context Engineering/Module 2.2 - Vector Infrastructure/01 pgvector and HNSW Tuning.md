# 01 — pgvector (Postgres) + HNSW / IVFFlat Tuning

> Phase 2 · Module 2.2 · Lesson 1 · `[MUST KNOW — ~80% of RAG JDs]`

## 🗺️ Stage 0 — Concept Map

**The problem first.** Lesson [2.1.01](../Module%202.1%20-%20RAG%20Pipeline%20Architecture/01%20RAG%20Pipeline%20Architecture.md)
stored vectors in a plain Python list and looped over **every** one to find the nearest. That's fine
for 100 chunks — but at 1,000,000 chunks it compares all million on *every* question (that's **O(n)** —
work grows with the number of rows): seconds per search, melting the CPU. You need a store built to
find the nearest vectors **fast, at scale**.

A **vector database** does exactly that. **pgvector** is the simplest one to reach for: it adds vector
search to **PostgreSQL** — the database you (or your company) almost certainly already run — so your
vectors sit right next to your normal data, with all of Postgres's reliability.

**Where it sits.** This is the **store** box of the pipeline (load → chunk → embed → **store** →
retrieve). It replaces the toy in-memory list from Module 2.1.

**Why care.** "pgvector + HNSW tuning" is named in ~80% of RAG job posts — the most common vector store,
because most shops already run Postgres and don't want a second database to babysit.

## 🔑 New Terms (plain English)

- **Vector database** — a store built to find the vectors *nearest* a query vector, fast, at scale.
- **pgvector** — a Postgres add-on that gives you a `vector` column type and nearest-neighbour search.
- **Nearest-neighbour search** — finding the stored vectors closest (most similar) to a query vector.
- **Exact vs approximate search** — exact checks *every* row (perfect, slow); approximate uses an
  **index** to check a smart subset (near-perfect, *much* faster).
- **ANN (Approximate Nearest Neighbour)** — approximate search; trades a tiny bit of accuracy for big speed.
- **Index** — a precomputed structure that lets the database skip most rows (here: **HNSW** or **IVFFlat**).
- **HNSW** — a multi-layer **graph** index: fast *and* accurate, but slower to build and heavier on memory.
- **IVFFlat** — a **buckets** index: groups vectors into lists and searches the nearest few buckets.
  Faster to build, lighter, slightly lower accuracy.
- **Distance operator** — pgvector's symbols for "how far apart": `<->` (L2), `<#>` (inner product), `<=>` (cosine).
- **Recall (of the search)** — of the *true* nearest neighbours, how many the approximate index actually found.
- **asyncpg** — an async Postgres driver, for `await` inside FastAPI.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: a library with vs without a catalogue)

Without an index, finding the most relevant book means **walking every shelf and reading every spine** —
fine for a tiny room, impossible for a national library. An **index is the catalogue**: **HNSW** is a
smart multi-level map that hops you from the front desk → the right aisle → the right shelf in a few
jumps; **IVFFlat** first sends you to the right *section* (bucket), then you scan only that section.
Both let you skip almost every shelf.

**The "Aha!":** at scale you don't search *all* the vectors — you let an index jump you to the right
neighbourhood and search only there. You trade a tiny bit of "did I find THE single nearest?" for being
hundreds of times faster.

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — keep vectors in a list (or a JSON column) and run a cosine loop over every
one on each query (**O(n)** — dies at scale). Or bolt on a *separate* vector database when your data
already lives in Postgres — now you have two systems to keep in sync. pgvector keeps the vectors **in
Postgres** and indexes them.

### 2.1 Setup — the extension, a vector column, inserting

```sql
CREATE EXTENSION vector;                       -- run once per database

CREATE TABLE chunks (
    id        bigserial PRIMARY KEY,
    text      text,
    embedding vector(1536)                      -- MUST match your embedding model's dims (lesson 2.1.04)
);

INSERT INTO chunks (text, embedding) VALUES ('annual leave policy…', '[0.01, -0.02, …]');
```

### 2.2 Search — the distance operators

```sql
-- the 5 nearest chunks to a query vector, by COSINE distance:
SELECT id, text FROM chunks ORDER BY embedding <=> '[…]' LIMIT 5;
```

Pick the operator by your embedding model:
- **`<=>` cosine distance** — the default for text embeddings.
- **`<->` L2 (straight-line) distance** — when vectors aren't normalised.
- **`<#>` (negative) inner product** — fastest *if* vectors are normalised (OpenAI's are).

> **Inline decision:** OpenAI and most text embeddings are **normalised to length 1**, so cosine and
> inner product rank identically — use **`<=>` cosine** for clarity, or **`<#>`** for a touch more speed.

### 2.3 Indexes — HNSW vs IVFFlat (the core tuning choice)

With **no index**, pgvector does **exact** search: perfect recall, but it scans every row. Add an
**approximate** index for speed:

```sql
-- HNSW (the usual choice): graph index, best speed/recall
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);       -- build-time knobs
SET hnsw.ef_search = 100;                       -- QUERY-time: higher = better recall, slower

-- IVFFlat (alternative): bucket index — build it AFTER you have data
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);                         -- number of buckets
SET ivfflat.probes = 10;                        -- QUERY-time: higher = better recall, slower
```

> Match the **ops** to your operator: `vector_cosine_ops` for `<=>`, `vector_l2_ops` for `<->`,
> `vector_ip_ops` for `<#>`.

**The knobs that matter:**
- **HNSW:** `m` (links per node, default 16 — higher = better recall, more memory) · `ef_construction`
  (build effort, default 64 — higher = better recall, slower build) · `ef_search` (query effort, default
  40 — higher = better recall, slower query).
- **IVFFlat:** `lists` (number of buckets — start at `rows/1000` up to 1M rows, then `sqrt(rows)`) ·
  `probes` (buckets searched — higher = better recall, slower).

**HNSW vs IVFFlat (pick one):**
- **HNSW** — a multi-layer graph.
  - **Key features:** best speed-vs-recall trade-off; can be built on an empty table (no training step).
  - **✅ Use when:** you want top recall *and* speed — the default for most RAG.
  - **🚫 Avoid when → use IVFFlat:** memory is tight, or you rebuild the whole index constantly.
  - **⚠️ Gotcha:** slower to build and uses more RAM — give it `maintenance_work_mem` so the graph fits in memory.
- **IVFFlat** — vectors grouped into buckets.
  - **Key features:** fast to build, lighter on memory.
  - **✅ Use when:** build speed and memory matter more than squeezing out the last bit of recall.
  - **🚫 Avoid when → use HNSW:** you want the best speed-recall trade-off.
  - **⚠️ Gotcha:** **build it AFTER loading data** (it trains on the data), and a bad `lists` value tanks recall.

> **Exact (no index) vs approximate (index):** no index = perfect recall but O(n); an index = ~99%
> recall and hundreds of times faster. Use **exact** only for small tables (a few thousand rows).

### 2.4 Async with FastAPI (`asyncpg`)

```python
# pip install asyncpg pgvector
import asyncpg
from pgvector.asyncpg import register_vector

conn = await asyncpg.connect(dsn)
await register_vector(conn)                      # lets you pass/receive Python lists as vectors
rows = await conn.fetch(
    "SELECT id, text FROM chunks ORDER BY embedding <=> $1 LIMIT 5", query_vec)
```

### 2.5 Metadata filtering — the big Postgres win

Because it's SQL, you filter on **normal columns** *and* vector-search in **one** query:

```sql
SELECT id, text FROM chunks
WHERE department = 'HR' AND created_at > '2026-01-01'   -- pre-filter on metadata
ORDER BY embedding <=> '[…]' LIMIT 5;                    -- then nearest WITHIN that subset
```

This is **hybrid storage**: metadata in regular columns, vectors in the `vector` column — so joins,
transactions, and access control (who may see which rows) all come for free.

### 2.6 Scaling awareness — quantization & `halfvec` `[awareness]`

At millions of vectors the index can get large. Shrink it: **`halfvec`** (half-precision — half the
storage) or **binary quantization** (store bit-vectors, then re-rank the top candidates with the full
vectors) keep the index in RAM cheaply, with a small recall cost.

> 🔬 **Under the hood:** HNSW builds a multi-layer "small-world" graph — the top layers are sparse
> express lanes, the lower layers dense local streets. A search greedily hops toward the query, dropping
> down layers, visiting only a few hundred nodes instead of millions. **`ef_search`** caps how many
> candidates it keeps — that's the recall-vs-speed dial. The index is **approximate**: it can miss a true
> neighbour, which is why you tune `ef_search`/`probes` to your recall target (measure it with Recall@K,
> lesson [2.1.05](../Module%202.1%20-%20RAG%20Pipeline%20Architecture/05%20Retrieval%20Evaluation.md)).

## 🚀 Stage 3 — In Practice / Why It Matters

pgvector is the default **first** vector store because it reuses infrastructure you already run: one
database for app data *and* vectors, with ACID transactions, backups, joins, and metadata filtering —
no extra service to deploy or secure. Teams move to a dedicated vector DB (**Pinecone**/**Qdrant**, the
next lessons) only at very large scale or when they want fully-managed vector ops. The HNSW knobs here
(`m`, `ef_construction`, `ef_search`) are the exact "HNSW tuning" that JDs name.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
|---|---|---|
| **Index** | HNSW vs IVFFlat vs none (exact) | **HNSW** default · IVFFlat for fast builds / low memory · **none** only for tiny tables |
| **Distance operator** | `<=>` cosine vs `<#>` inner product vs `<->` L2 | **cosine** for text embeddings (or inner product for normalised vectors); L2 if not normalised |
| **Store** | **pgvector** vs dedicated vector DB | **pgvector** when data already lives in Postgres / moderate scale · dedicated DB (next lessons) at huge scale |

> Decision rule: **stay on pgvector + HNSW unless you have a specific scale or managed-ops reason to leave.**

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
|---|---|---|
| `expected N dimensions, got M` | Column dims ≠ embedding dims | Make `vector(N)` match the model (lesson 2.1.04) |
| Query still slow (index ignored) | No `ORDER BY <op> … LIMIT`, or ops mismatch | Use `ORDER BY embedding <=> q LIMIT k`; match `vector_cosine_ops` to `<=>` |
| IVFFlat recall is poor | Built before loading data, or too few `lists` | Build **after** inserting; size `lists` to the row count |
| Recall too low (misses answers) | `ef_search`/`probes` too low | Raise `hnsw.ef_search` / `ivfflat.probes` |
| Out-of-memory building HNSW | Graph bigger than `maintenance_work_mem` | Raise it, or use `halfvec`/quantization |

## 📌 Quick Reference (cheat-sheet)

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, text text, embedding vector(1536));
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);
SET hnsw.ef_search = 100;                                   -- recall/speed dial (query time)
SELECT id, text FROM chunks
  WHERE dept = 'HR'                                          -- metadata pre-filter (free in SQL)
  ORDER BY embedding <=> '[…]' LIMIT 5;                      -- nearest-neighbour search
```
- **HNSW** default index · **`<=>` cosine** for text · **dims must match** the model · **`ef_search`** = recall/speed dial.
- pgvector's superpower = **metadata filter + vector search + joins in one SQL query**.

## 🛑 STOP — Self-Check

You have **5 million** chunks. Search is slow, so you add an **HNSW** index — now it's fast, but answer
quality dips a little (the index occasionally misses the best chunk). Name the single **query-time** knob
you'd raise to recover recall, and the trade-off it costs.

<details>
<summary>Answer</summary>

Raise **`hnsw.ef_search`** (default 40 → e.g. 100–200). It tells the search to keep a **larger candidate
list** as it walks the graph, so it's less likely to miss the true nearest chunk — **higher recall**. The
trade-off is **speed**: a bigger candidate list means each query does more work, so latency goes up. You
tune `ef_search` to the **lowest** value that hits your target Recall@K (lesson 2.1.05) — fast *and*
accurate enough. (The HNSW index is **approximate** by design, which is why this dial exists at all.)
</details>
