# 05 — Egress & Cost Architecture

> Phase 2 · Module 2.2 · Lesson 5 · `[SHOULD — architect-bonus]`

## 🗺️ Stage 0 — Concept Map

**The problem first.** A RAG system that *works* in a demo can quietly become *expensive* in production.
Vectors cost money in **three** ways — **storage**, **queries**, and **egress** (data leaving a cloud
region or provider). The classic mistake: put the vector DB in one cloud, the LLM API in another, and the
app in a third — now **every** retrieval ships data across boundaries, paying **egress** and adding
latency. Designing this away is an **architect-level** skill JDs reward.

**Where it sits.** This is the *cost & deployment* view of the **store** box — how you place and size your
vector infrastructure so it's fast *and* affordable at scale.

**Why care.** "Cost optimisation" and "data residency" show up in architect JDs; getting placement and
vector size right is often a bigger lever than the algorithm.

## 🔑 New Terms (plain English)

- **Egress** — the fee a cloud charges for data **leaving** a region or provider (ingress, coming in, is
  usually free).
- **Region** — a cloud's physical location (e.g. `us-east-1`). Same region = cheap, fast; across regions = costed.
- **Data gravity** — the principle that compute should sit **next to** the data it uses (keep them together).
- **Private endpoint** — a private network door into a cloud service so traffic never touches the public
  internet (no egress, more secure).
- **Storage / query / egress cost** — the three lines on a vector-DB bill: holding vectors, searching
  them, and moving data out.
- **Matryoshka truncation** — shortening embeddings (e.g. 3072 → 256) to cut storage *and* transfer size
  (lesson 2.1.04).
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: shipping costs)

Imagine a factory (your LLM/app) and a warehouse (your vector DB). If the warehouse is **across the
country**, every order pays **freight** (egress) and waits for delivery (latency). Put the warehouse
**next door** (same region) and freight ≈ £0 with instant delivery. And if you **shrink each box**
(smaller vectors), you store and ship more for less. Cost architecture is mostly *"keep things close and
small."*

**The "Aha!":** the cheapest, fastest byte is the one that **never crosses a boundary**. Co-locate your
vector DB with your LLM/app, and shrink vectors where recall allows.

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — vector DB in cloud A, LLM API in cloud B, app server in region C. Every
query embeds (cross-boundary), searches (cross-boundary), and returns chunks (cross-boundary) — paying
**egress** three times and stacking latency, all invisible until the bill arrives.

### 5.1 The three cost components

| Cost | What you pay for | Lever |
|---|---|---|
| **Storage** | holding vectors (per GB·month) | smaller vectors (Matryoshka), quantization |
| **Query** | each search (compute / per-request) | fewer/cheaper queries, caching, right index |
| **Egress** | data **leaving** the region/provider | **co-locate**; private endpoints |

### 5.2 Data gravity — co-locate the vector DB with the LLM & app

Keep the vector DB in the **same region** as the LLM endpoint and app. That removes cross-region egress
*and* cuts latency (no long-haul network hop per query). This single decision often saves more than any
algorithm tweak.

### 5.3 Private endpoints — eliminate egress for in-cloud DBs

For a cloud-hosted vector DB (e.g. Azure Database for PostgreSQL with pgvector, or a vector DB in your
VNet), route traffic through a **private endpoint** so it stays on the cloud's private network: **no
public-internet egress**, lower latency, and better security (the same VNet/private-endpoint idea from
Phase 1, Azure lesson).

### 5.4 Compression — Matryoshka dimensions cut storage *and* transfer

Smaller vectors are cheaper to store *and* to move. Truncating `text-embedding-3-large` from 3072 → 1024
(or 256) shrinks both the index and every byte transferred — at a small recall cost you **measure**
(lesson 2.1.05).

**Full dimensions vs truncated (Matryoshka) — pick one:**
- **Full dimensions** (e.g. 3072)
  - **✅ Use when:** a small/medium corpus where recall matters most and storage is cheap.
  - **🚫 Avoid when → truncate:** millions of vectors where storage/egress/latency dominate the bill.
  - **⚠️ Gotcha:** storage and transfer grow linearly with dimensions — at scale this is a big line item.
- **Truncated dimensions** (e.g. 256–1024)
  - **✅ Use when:** large corpora where cost/latency dominate and a small recall dip is acceptable.
  - **🚫 Avoid when → keep full:** recall is critical and the corpus is small enough that cost is moot.
  - **⚠️ Gotcha:** measure the recall drop on *your* data first, and the DB column dimension must match.

### 5.5 The per-provider cost model

- **pgvector** — you pay your **Postgres** bill (storage + compute); no separate vector service or egress
  if it's co-located. Cheapest when you already run Postgres.
- **Pinecone (serverless)** — usage-based: storage + read/write units. No infra to run, but watch query
  volume.
- **Qdrant** — self-host (you pay the VM/compute) or Qdrant Cloud (managed pricing); quantization cuts
  the memory you pay for.

> 🔬 **Under the hood:** clouds bill **egress per GB** that crosses a region or provider boundary; data
> *within* one region is essentially free and fast. **Co-location** removes the boundary entirely, and a
> **private endpoint** keeps even cross-service traffic on the internal network (so it isn't egress).
> Smaller vectors mean fewer bytes to store *and* fewer to move — which is why dimension choice is a cost
> decision, not just an accuracy one.

## 🚀 Stage 3 — In Practice / Why It Matters

The architect's checklist: **co-locate** the vector DB with the LLM and app (same region), use **private
endpoints** to kill egress and harden security, **right-size dimensions** (Matryoshka) and **quantize** at
scale, and **model the bill** across storage/query/egress before committing. These decisions routinely
cut RAG running costs by large factors — and "I'd keep the vector DB in-region behind a private endpoint
and truncate embeddings" is exactly the answer architect interviews want.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
|---|---|---|
| **Placement** | co-locate (same region) vs cross-region/cloud | **co-locate** almost always (no egress, low latency) · cross-region only for compliance/model-availability reasons |
| **Network** | public endpoint vs **private endpoint** | **private endpoint** in production (no egress, secure) · public only for quick dev |
| **Dimensions** | full vs truncated (Matryoshka) | **full** for small corpora/max recall · **truncate** at scale to cut storage/egress |
| **Store cost model** | pgvector vs Pinecone vs Qdrant | pgvector if on Postgres · Pinecone for managed/usage-based · Qdrant for open-source/quantized |

> Decision rule: **keep data close (co-locate + private endpoint) and small (right-size dims + quantize); model storage/query/egress before scaling.**

## 🐛 Common Misconceptions

| Misconception | Why it's wrong | The right view |
|---|---|---|
| "The vector DB location doesn't matter." | Cross-region traffic pays **egress** + latency every query. | Co-locate with the LLM/app. |
| "Bigger embeddings are always better." | They cost more to store *and* move. | Right-size dims to your recall target. |
| "Egress is a rounding error." | At millions of queries it's a top line item. | Design it out with co-location/private endpoints. |
| "Managed = always cheaper." | Usage-based cost can exceed self-host at steady scale. | Model the bill for *your* volume. |

## 📌 Quick Reference (cheat-sheet)

```text
Three costs:   STORAGE (per GB) · QUERY (per search) · EGRESS (data leaving the region)
Cheapest byte = one that never crosses a boundary  ->  CO-LOCATE vector DB + LLM + app
Levers:        same region · private endpoint (no egress) · truncate dims (Matryoshka) · quantize
Model the bill across providers (pgvector = Postgres cost · Pinecone = usage · Qdrant = compute)
```

## 🛑 STOP — Self-Check

Your RAG app runs in `azure-eastus`, but the team put the vector DB in a different cloud's `us-west`
region "because it was easy." Costs and latency are both high. Name the **two** architecture changes that
would help most, and *why* each works.

<details>
<summary>Answer</summary>

1. **Co-locate the vector DB in `azure-eastus`** (same region as the app + LLM). This removes the
   cross-region/cross-cloud **egress** charge on every query *and* cuts latency (no long-haul network hop
   per retrieval) — usually the single biggest win (**data gravity**).
2. **Put it behind a private endpoint** so traffic stays on the cloud's private network — eliminating any
   remaining public-internet egress and improving security.

(Bonus: **truncate the embeddings** with Matryoshka dims to shrink storage *and* the bytes moved per
query, after checking the recall drop is acceptable.)
</details>
