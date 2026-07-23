# 03 — Qdrant (Open-Source Vector Database)

> Phase 2 · Module 2.2 · Lesson 3 · `[MUST KNOW — ~55% of RAG JDs]`

> 🔑 Examples use the **Qdrant Python client v1.18** (2026) — check the live docs for current details.

## 🗺️ Stage 0 — Concept Map

**The problem first.** [pgvector](01%20pgvector%20and%20HNSW%20Tuning.md) ties you to Postgres;
[Pinecone](02%20Pinecone.md) is managed-only (you can't run it yourself, and you pay for the service).
What if you want an **open-source** vector database you can **either self-host or rent as a cloud
service**, with **first-class metadata filtering** and a **memory-saving compression** trick for huge
datasets? That's **Qdrant** — purpose-built for vectors, with strong filtering and quantization.

**Where it sits.** Same **store** box again — the third common choice. The retrieval idea is identical;
Qdrant's edges are *open-source control*, *powerful payload (metadata) filtering*, and *quantization* to
fit more vectors in memory.

**Why care.** Qdrant appears in ~55% of RAG JDs — the leading open-source dedicated vector DB, picked
when teams want control plus rich filtering without being locked to one cloud.

## 🔑 New Terms (plain English)

- **Qdrant** — an open-source vector database; run it yourself (Docker) or use Qdrant Cloud.
- **Collection** — a named set of vectors (like a table). The equivalent of a Pinecone *index*.
- **Point** — one stored item: an `id` + a `vector` + a **payload**.
- **Payload** — the metadata attached to a point (Qdrant's word for it): `{"dept": "HR", "page": 3}`.
- **`VectorParams`** — the collection's vector settings: `size` (dimensions) + `distance` (cosine/…).
- **`query_points`** — the search call (returns the nearest points). *(Replaces the old `search`.)*
- **Payload index** — an index on a metadata field so filtering is fast.
- **Quantization** — compressing vectors (e.g. to 1 byte each) to cut memory ~4×, with tiny recall loss.
- **Local mode** — run the *same client* with no server (`:memory:` or a file) for dev and tests.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: a vector warehouse you own *or* rent)

Qdrant is a **purpose-built vector warehouse** with two superpowers: an excellent **filing system** —
you can say *"only search HR documents from 2026"* and it filters fast — and a **box-compression**
trick (quantization) that fits ~4× more boxes in the same room. And you choose whether to **own the
building** (self-host) or **rent it** (Qdrant Cloud) — unlike Pinecone, which is rent-only.

**The "Aha!":** Qdrant gives you Pinecone-style dedicated vector search **plus** open-source control and
strong metadata filtering — and it runs the *same code* locally (no server) for tests.

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — pick between "tied to Postgres" (pgvector) and "managed-only, pay-to-play"
(Pinecone), with no open-source middle ground that filters well. Qdrant is that middle ground: open
source, self-host or cloud, with filtering and quantization built in.

### 2.1 Connect & create a collection

```python
# pip install qdrant-client
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333", api_key="...")   # or QdrantClient(":memory:") for dev/tests

client.create_collection(
    collection_name="docs",
    vectors_config=models.VectorParams(
        size=1536,                                   # MUST match your embedding model (lesson 2.1.04)
        distance=models.Distance.COSINE,             # COSINE | DOT | EUCLID
    ),
)
```

### 2.2 Upsert points (vector + payload)

```python
client.upsert(
    collection_name="docs",
    points=[
        models.PointStruct(id=1, vector=embedding_1, payload={"dept": "HR", "page": 3}),
        models.PointStruct(id=2, vector=embedding_2, payload={"dept": "IT", "page": 9}),
    ],
)
```

### 2.3 Query (nearest points + payload filter)

```python
hits = client.query_points(
    collection_name="docs",
    query=query_embedding,
    limit=5,
    query_filter=models.Filter(                       # filter on payload BEFORE/with the vector search
        must=[models.FieldCondition(key="dept", match=models.MatchValue(value="HR"))]
    ),
).points                                              # -> list of scored points
for p in hits:
    print(p.id, p.score, p.payload)
```

### 2.4 Fast filtering — a payload index

Filtering on a field a lot? Index it so Qdrant doesn't scan payloads:

```python
client.create_payload_index(
    collection_name="docs", field_name="dept",
    field_schema=models.PayloadSchemaType.KEYWORD,    # exact-match field -> fast filters
)
```

### 2.5 Quantization — fit more vectors in memory

For large collections, compress vectors so the working set stays in RAM:

```python
client.create_collection(
    collection_name="big",
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    quantization_config=models.ScalarQuantization(    # ~4x smaller, minimal recall loss
        scalar=models.ScalarQuantizationConfig(type=models.ScalarType.INT8, always_ram=True)
    ),
)
```

**Quantization — on vs off (pick one):**
- **On (scalar quantization)**
  - **Key features:** ~4× less memory; Qdrant searches the compressed vectors, then re-checks the top few with the originals.
  - **✅ Use when:** large collections (millions of vectors) where memory/cost dominate.
  - **🚫 Avoid when → leave it off:** small collections that already fit comfortably in RAM.
  - **⚠️ Gotcha:** a small recall drop — measure it (lesson 2.1.05); keep `always_ram=True` so it stays fast.
- **Off (full vectors)**
  - **Key features:** full precision, best recall.
  - **✅ Use when:** small/medium collections, or when every bit of recall matters.
  - **🚫 Avoid when → turn it on:** the index no longer fits in memory and search slows or costs spike.
  - **⚠️ Gotcha:** memory grows linearly with vectors × dimensions — it adds up fast at scale.

### 2.6 Multi-tenancy — payload filter vs collection-per-tenant

- **One collection + a `tenant_id` payload filter**
  - **✅ Use when:** many tenants — cheapest and simplest; filter every query by `tenant_id`.
  - **🚫 Avoid when → use a collection per tenant:** a tenant needs hard isolation or very different config.
  - **⚠️ Gotcha:** you **must** add the `tenant_id` filter on *every* query — forget it and tenants leak.
- **A collection per tenant**
  - **✅ Use when:** strong isolation, per-tenant tuning, or wildly different sizes.
  - **🚫 Avoid when → use a payload filter:** you have thousands of small tenants (too many collections).
  - **⚠️ Gotcha:** more collections = more overhead to manage and monitor.

### 2.7 Async + local mode

```python
from qdrant_client import AsyncQdrantClient
client = AsyncQdrantClient(url="http://localhost:6333")     # await client.query_points(...)
# Local mode for tests — no server needed:  QdrantClient(":memory:")  or  QdrantClient(path="db/")
```

> 🔬 **Under the hood:** Qdrant uses an **HNSW** graph index like pgvector, but stores a rich **payload**
> per point and indexes payload fields so filters are fast even combined with vector search.
> **Quantization** stores a compressed copy of each vector (e.g. 1 byte per number) for the fast first
> pass, then re-ranks the top candidates with the full vectors — most of the memory saving, most of the
> recall. **Local mode** runs the same API in-process, which is why your test code matches production.

## 🚀 Stage 3 — In Practice / Why It Matters

Qdrant is the pick when a team wants **open-source** vectors (no lock-in), **rich metadata filtering**,
and the option to **self-host or use the cloud** — with **local mode** making tests trivial. It competes
directly with Pinecone on features while staying open. Same embeddings (2.1.04) and same recall
measurement (2.1.05); the store is just more controllable.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
|---|---|---|
| **Deploy** | self-host (Docker) vs **Qdrant Cloud** vs local mode | **self-host/cloud** for production · **local mode** (`:memory:`) for dev & tests |
| **Quantization** | on (scalar) vs off | **on** for millions of vectors (save memory) · **off** for small sets / max recall |
| **Multi-tenancy** | payload filter vs collection-per-tenant | **payload filter** (one collection) for many tenants · collection-per-tenant for hard isolation |
| **Store** | Qdrant vs pgvector vs Pinecone | **Qdrant** for open-source + filtering · pgvector if on Postgres · Pinecone for fully-managed |

> Decision rule: **Qdrant when you want open-source control with strong filtering — self-host or cloud, your choice.**

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
|---|---|---|
| `Wrong vector size` | Collection `size` ≠ embedding dims | Set `VectorParams(size=…)` to the model (lesson 2.1.04) |
| `AttributeError: search` | Old method name | Use **`query_points(...)`** (the current API) and read `.points` |
| Slow / wrong filtering | No payload index, or bad `Filter` | Add a **payload index**; use `models.Filter(must=[FieldCondition(...)])` |
| Upserts very slow | One-by-one inserts | Batch points (or `upload_collection`/`upload_points`) |
| A tenant sees another's data | Forgot the `tenant_id` filter | Add the tenant filter on **every** query |

## 📌 Quick Reference (cheat-sheet)

```python
from qdrant_client import QdrantClient, models
client = QdrantClient(url="http://localhost:6333")            # or ":memory:" for tests
client.create_collection("docs", vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE))
client.upsert("docs", points=[models.PointStruct(id=1, vector=emb, payload={"dept":"HR"})])
hits = client.query_points("docs", query=q, limit=5,
        query_filter=models.Filter(must=[models.FieldCondition(key="dept", match=models.MatchValue(value="HR"))])).points
```
- **Collection / point / payload** · **`query_points` → `.points`** · payload index for fast filters · quantization to save memory · `:memory:` for tests.

## 🛑 STOP — Self-Check

Your Qdrant collection has grown to **20 million** vectors and no longer fits in RAM, so search has
slowed and cost is climbing. What Qdrant feature would you turn on to shrink the memory footprint, how
does it keep answers accurate, and what must you check afterwards?

<details>
<summary>Answer</summary>

Turn on **scalar quantization** (`quantization_config=models.ScalarQuantization(...)`). It stores a
**compressed** copy of each vector (≈1 byte per number instead of 4), cutting memory ~**4×** so the
working set fits in RAM again. It stays accurate by doing the fast first pass on the compressed vectors,
then **re-ranking the top candidates with the original full vectors** — most of the saving, most of the
recall. Afterwards, **measure Recall@K** (lesson 2.1.05) to confirm the small accuracy drop is
acceptable, and keep `always_ram=True` so the quantized vectors stay fast.
</details>
