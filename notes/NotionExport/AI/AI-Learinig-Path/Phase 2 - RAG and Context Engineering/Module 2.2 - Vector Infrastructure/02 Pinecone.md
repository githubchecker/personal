# 02 — Pinecone (Serverless Vector Database)

> Phase 2 · Module 2.2 · Lesson 2 · `[MUST KNOW — ~65% of RAG JDs]`

> 🔑 Model/SDK names move fast. Examples use the **Pinecone Python SDK v9** (2026) — check the live docs.

## 🗺️ Stage 0 — Concept Map

**The problem first.** [pgvector](01%20pgvector%20and%20HNSW%20Tuning.md) is perfect when you already run
Postgres — but *you* own the ops: building indexes, tuning `ef_search`, adding memory, sharding when it
outgrows one box. At very large scale, or when a small team just wants vectors to **work and scale by
themselves**, that's a burden. **Pinecone** is a **fully-managed, serverless vector database**: you
upsert vectors and query them; Pinecone handles the index, the scaling, and the servers.

**Where it sits.** Same **store** box as pgvector — a drop-in alternative. The retrieval code barely
changes; what changes is *who runs the infrastructure* (Pinecone, not you).

**Why care.** Pinecone is named in ~65% of RAG JDs — the most common *managed* vector DB, especially at
SaaS companies that don't want to operate a database.

## 🔑 New Terms (plain English)

- **Pinecone** — a hosted (cloud) vector database you call over an API; no servers to run yourself.
- **Index** — Pinecone's name for one vector collection (like a table of vectors).
- **Serverless index** — an index that scales automatically; you pay for what you use, no capacity to pick.
- **Pod-based index** — the older model where you rent fixed compute ("pods") and size it yourself.
- **Namespace** — a labelled partition *inside one index* — used to keep tenants/customers separate.
- **Upsert** — insert-or-update: add vectors, or overwrite ones with the same id.
- **`top_k`** — how many nearest matches to return.
- **Metadata filter** — restrict the search to vectors whose metadata matches (e.g. `department = HR`).
- **`ServerlessSpec`** — the object that says *where* (cloud + region) a serverless index lives.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: renting a self-scaling warehouse)

pgvector is **running your own stockroom** — you buy the shelving, organise it, and add space when it
fills. Pinecone is **renting a self-scaling warehouse**: you drop your boxes (vectors) at the door, and
the operator handles shelving, staff, and *automatically* adds room as you grow. You give up some
control and pay rent; in return you never tune an index or wake up to a full disk.

**The "Aha!":** Pinecone trades *control + lower cost* (pgvector) for *zero-ops + automatic scale*. The
*query* is the same idea — nearest vectors to your query — someone else just runs the machine.

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — self-host a vector store and, as it grows, hand-tune the index, add RAM,
and shard across machines yourself (real work for a small team). Pinecone removes all of that: you only
ever **upsert** and **query**.

### 2.1 Create a serverless index

```python
# pip install pinecone
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="...")                     # or set PINECONE_API_KEY

pc.indexes.create(
    name="docs",
    dimension=1536,                              # MUST match your embedding model (lesson 2.1.04)
    metric="cosine",                             # cosine | dotproduct | euclidean
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),   # where it lives
)
index = pc.index("docs")                         # connect to it
```

### 2.2 Upsert vectors (with metadata)

```python
index.upsert(
    vectors=[
        {"id": "chunk-1", "values": embedding_1, "metadata": {"dept": "HR", "page": 3}},
        {"id": "chunk-2", "values": embedding_2, "metadata": {"dept": "IT", "page": 9}},
    ],
    namespace="acme-corp",                       # keep this tenant's data separate (2.4)
    batch_size=100,                              # auto-splits large inputs into parallel batches
)
```

### 2.3 Query (top-k + metadata filter)

```python
res = index.query(
    vector=query_embedding,
    top_k=5,
    namespace="acme-corp",
    filter={"dept": {"$eq": "HR"}},              # pre-filter BEFORE the vector search
    include_metadata=True,                       # return the stored metadata too
)
for m in res.matches:
    print(m.id, m.score, m.metadata)             # id, similarity score, your metadata
```

### 2.4 Namespaces — multi-tenant RAG (one index, many customers)

A **namespace** partitions one index so each tenant only ever searches their own vectors:

```python
index.upsert(vectors=[...], namespace="customer-A")
index.query(vector=q, top_k=5, namespace="customer-A")   # never sees customer-B's data
```

- **Use when:** a SaaS app serving many customers from one index — cheaper and simpler than one index each.

### 2.5 Async (FastAPI)

```python
from pinecone import AsyncPinecone

async def search(q):
    async with AsyncPinecone(api_key="...") as pc:
        desc = await pc.indexes.describe("docs")
        index = await pc.index(host=desc.host)
        async with index:
            res = await index.query(vector=q, top_k=5, namespace="acme-corp")
            return res.matches
```

### 2.6 Serverless vs pod-based (the index-type choice)

- **Serverless index** — scales automatically; pay per use.
  - **Key features:** no capacity planning; scales to zero when idle; usage-based billing.
  - **✅ Use when:** new projects, spiky/unpredictable traffic, or you simply don't want to size anything.
  - **🚫 Avoid when → use pod-based:** you have steady, very high volume and want fixed, predictable cost/latency.
  - **⚠️ Gotcha:** cost is usage-based, so a runaway query loop can run up the bill — monitor usage.
- **Pod-based index** — fixed rented compute you size yourself.
  - **Key features:** predictable cost and latency; you pick the pod size/replicas.
  - **✅ Use when:** steady high-throughput workloads where fixed capacity is cheaper and more predictable.
  - **🚫 Avoid when → use serverless:** variable or low traffic — you'd pay for idle pods.
  - **⚠️ Gotcha:** you must size and scale it yourself (back to capacity planning). **Serverless is the modern default.**

> 🔬 **Under the hood:** Pinecone is a managed service — your `upsert`/`query` are HTTPS calls to their
> API; they run and tune the index for you. **Serverless** decouples storage from compute, so it can add
> capacity on demand and bill per request instead of per rented machine. A **namespace** is just a
> partition key inside one index, so multi-tenant search stays isolated without a separate index per tenant.

## 🚀 Stage 3 — In Practice / Why It Matters

Pinecone is the go-to when a team wants vectors that **just scale** without running a database — common
at SaaS startups and anywhere ops headcount is scarce. The **namespace** pattern is how multi-tenant AI
products keep each customer's data separate in one index. You'll still embed (lesson 2.1.04) and measure
recall (lesson 2.1.05) exactly the same way — only the store changed.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
|---|---|---|
| **Index type** | **serverless** vs pod-based | **serverless** by default (auto-scale, pay-per-use) · pod-based only for steady high volume |
| **Multi-tenancy** | **namespaces** vs an index per tenant | **namespaces** (one index, isolated partitions) — cheaper/simpler · separate indexes only for hard isolation needs |
| **Store** | Pinecone vs pgvector vs Qdrant | **Pinecone** for zero-ops managed scale · pgvector if you run Postgres · Qdrant (next) for open-source + filtering |

> Decision rule: **Pinecone when you want managed, auto-scaling vectors and can pay for the service; pgvector when you already run Postgres.**

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
|---|---|---|
| `dimension mismatch` on upsert | Index dims ≠ embedding dims | Create the index with the model's dimension (lesson 2.1.04) |
| Query returns nothing | Wrong/empty **namespace** | Query the same namespace you upserted into |
| `metadata` is `None` in results | Forgot `include_metadata=True` | Pass `include_metadata=True` to `query` |
| Filter returns too few/odd results | Wrong filter operator | Use Pinecone filter syntax (`{"field": {"$eq": …}}`) |
| Surprise bill | Serverless usage-based cost | Monitor usage; cap query volume; batch upserts |

## 📌 Quick Reference (cheat-sheet)

```python
from pinecone import Pinecone, ServerlessSpec
pc = Pinecone(api_key="...")
pc.indexes.create(name="docs", dimension=1536, metric="cosine",
                  spec=ServerlessSpec(cloud="aws", region="us-east-1"))
index = pc.index("docs")
index.upsert(vectors=[{"id":"c1","values":emb,"metadata":{"dept":"HR"}}], namespace="acme")
res = index.query(vector=q, top_k=5, namespace="acme",
                  filter={"dept":{"$eq":"HR"}}, include_metadata=True)   # -> res.matches
```
- **Serverless** default · **namespaces** = multi-tenant isolation · **`filter` + `include_metadata`** for metadata · dims must match the model.

## 🛑 STOP — Self-Check

You're building a SaaS where 500 companies each upload their own private documents, and a company must
*never* see another's data. Do you create **500 indexes** or **one index with 500 namespaces** — and why?

<details>
<summary>Answer</summary>

**One index with 500 namespaces.** A **namespace** partitions a single index so each query
(`namespace="company-X"`) only ever searches that company's vectors — giving you per-tenant isolation
**without** the cost and management overhead of 500 separate indexes. It's cheaper, simpler to operate,
and the standard multi-tenant RAG pattern. (You'd only reach for separate indexes if a customer needs
*hard* physical isolation, e.g. a strict compliance/region requirement.)
</details>
