# 04 — Embedding Model Selection

> Phase 2 · Module 2.1 · Lesson 4 · `[MUST KNOW — JD VERIFIED]`

## 🗺️ Stage 0 — Concept Map

**The problem first.** The embedding model is what decides that the query "vacation days" matches a
chunk saying "annual leave entitlement." Pick the wrong one — wrong dimensions for your DB, weak on
your domain, English-only for multilingual docs — and retrieval fails *no matter how good* your
chunking, vector DB, or reranker. It's also a **cost / speed / quality** trade-off: bigger vectors
cost more to store and query.

**Embedding model selection** is choosing the encoder that turns text into meaning-vectors, and the
dimension count, for your accuracy, language, privacy, and budget.

**Where it sits.** Step 3 of Phase A: load → chunk → **embed** → store. This is also where the
**embeddings API deferred from Phase 1** finally lands.

**Why care.** "Which embedding model and why" is a standard RAG interview question, and a wrong choice
is expensive to undo (you must re-embed the *entire* corpus to change it).

## 🔑 New Terms (plain English)

- **Embedding model** — a model that maps text → a fixed-length vector of meaning. It's a
  **bi-encoder**: it turns each text into a vector *on its own*, so you can embed millions of chunks
  ahead of time.
- **Dimensions** — how many numbers in each vector (e.g. 1536 or 3072). More = more nuance, more cost.
- **MTEB** — *Massive Text Embedding Benchmark*; a public leaderboard ranking embedding models per task.
- **Matryoshka embedding** — a model trained so you can **truncate** the vector (3072→256) and keep most
  of its quality (like nesting dolls — smaller versions live inside the big one).
- **Normalized vector** — scaled to length 1, so **cosine similarity = dot product**.
- **Context length (of an embedder)** — the max tokens it can embed at once (e.g. 8192).
- **Open vs closed** — run-it-yourself open-source weights vs a paid hosted API.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: choosing a translator)

Every embedding model is a **translator** that rewrites text into the universal language of
coordinates. Two translators place the *same* sentence at *different* points — and you must use the
**same translator** for your library and your questions, or "vacation" and "annual leave" end up in
different neighbourhoods and never meet. Choosing the model is choosing *which translator's map* your
whole system will speak.

**The "Aha!":** the embedding model defines the meaning-space; everything downstream just measures
distances **inside** it. Change the translator and you must re-translate the whole library.

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — reach for `text-embedding-ada-002` (the 2022 default) for everything, or
pick a model "because a blog liked it," with no regard for dimensions, domain, language, or the
DB column you'll store it in. Then discover retrieval is weak *after* embedding a million chunks. The
fix: choose deliberately on a few axes.

### 4.1 OpenAI `text-embedding-3-small` vs `text-embedding-3-large`

The default closed-API choice for most teams.

```python
from openai import OpenAI
client = OpenAI()

resp = client.embeddings.create(
    model="text-embedding-3-small",        # 1536 dims; strong + cheap (the default pick)
    input=["annual leave entitlement", "how many vacation days do I get?"],
)
vectors = [d.embedding for d in resp.data] # one 1536-float vector per input
```

| Model | Dims | MTEB (avg) | Relative cost | Pick when |
|---|---|---|---|---|
| `text-embedding-3-small` | 1536 | ~62.3% | 1× (cheap) | **default**; great quality/cost |
| `text-embedding-3-large` | 3072 | ~64.6% | ~6× | top accuracy needed; budget allows |
| `text-embedding-ada-002` | 1536 | ~61.0% | legacy | only existing indexes — don't start here |

- **`text-embedding-3-small`** (1536 dims) — the default.
  - **✅ Use when:** almost always — it's the best quality-for-cost for most RAG.
  - **🚫 Avoid when → use 3-large:** evaluation (Lesson 05) shows you need higher accuracy and the budget allows.
  - **⚠️ Gotcha:** 1536 dims — your DB column must be `vector(1536)` to match.
- **`text-embedding-3-large`** (3072 dims) — top accuracy.
  - **✅ Use when:** accuracy is critical and measurably better on *your* data.
  - **🚫 Avoid when → use 3-small (or truncate dims):** cost matters — it's ~6× the price.
  - **⚠️ Gotcha:** 3072 dims cost more to store/search — use the `dimensions` param (4.2) to shrink it.

### 4.2 The `dimensions` parameter (Matryoshka)

Shrink vectors to cut storage and speed up search, with minimal quality loss — no re-training.

```python
resp = client.embeddings.create(
    model="text-embedding-3-large",
    input=chunks,
    dimensions=256,          # truncate 3072 -> 256; ~4-12x smaller, small quality drop
)
```

- **Key feature:** one model serves many size/quality points. **Inline decision — pick dims by scale:**
  full dims for best recall (finding all the right chunks) on a *small* corpus; truncate (256–1024) when you have *millions* of vectors
  and storage/latency dominate. **Whatever you pick, the DB column dimension must match exactly.**

### 4.3 Open-source models (run them yourself)

For privacy (data never leaves your servers), cost at scale, or offline use.

```python
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")          # runs locally (CPU/GPU)
vectors = model.encode(chunks, normalize_embeddings=True)      # normalize -> cosine = dot
```

| Model | Notes | Pick when |
|---|---|---|
| `BAAI/bge-large-en-v1.5` | strong English; add a query *instruction* prefix for retrieval | on your own servers, English |
| `nomic-embed-text-v1.5` | long context, Matryoshka dims | long docs, flexible dims |
| `intfloat/e5-mistral-7b-instruct` | top accuracy, heavy (7B) | quality-first, have GPUs |

- **Gotcha:** some models (e.g. BGE) expect a **query prefix** like *"Represent this sentence for
  searching relevant passages:"* on the **query** side — check the model card or retrieval silently degrades.

### 4.4 Reading the MTEB leaderboard

The public benchmark to compare models — but read it like an engineer, not a scoreboard.

- Look at the **task type that matches yours** (Retrieval, not just the overall average).
- Balance **score vs dimensions vs model size** — a 7B model topping the chart may be impractical.
- Check **language** and **max sequence length** columns against your corpus.
- **Use when:** shortlisting candidates; then confirm on **your** data with Lesson 05.

### 4.5 Domain-specific fine-tuning (awareness)

`[OPTIONAL — awareness]` Off-the-shelf embedders can underperform on specialised jargon (legal,
medical, code). You can **fine-tune** an embedding model on in-domain (query, relevant-passage) pairs to
sharpen it. It needs labelled data and evaluation (Phase 4 territory) — know it *exists* and when it's
worth it; reach for it only after chunking, model choice, and reranking are exhausted.

> 🔬 **Under the hood:** an embedding model is the **encoder** half of a transformer (the part that
> *reads and understands* text): it reads a text once and emits one combined (*pooled*) vector,
> independently for each text — which is why you can embed millions of chunks offline and only embed
> the *query* at run time. It's trained with **contrastive learning** — pulling (question,
> correct-passage) pairs together and pushing mismatches apart — so paraphrases land nearby. Outputs
> are usually **normalized to length 1**, which is why cosine similarity becomes a fast **dot product**
> (multiply the matching numbers and add them up) — and why OpenAI says the distance function barely
> matters.

## 🚀 Stage 3 — In Practice / Why It Matters

The pragmatic default in 2026: **`text-embedding-3-small`** for most RAG, reach for **3-large** (or
truncated 3-large) when accuracy matters, and **bge/nomic** when data can't leave your infrastructure.
Lock the choice early — re-embedding a large corpus is the most expensive change in a RAG system —
and **measure** alternatives on your own data (Lesson 05) before committing.

## ⚖️ Variations & When to Use

| Option | Use when… | Trade-off |
|---|---|---|
| `text-embedding-3-small` | default; best quality/cost | not the absolute top accuracy |
| `text-embedding-3-large` (± `dimensions`) | accuracy-critical | ~6× cost (mitigate by truncating dims) |
| Open-source (bge/nomic/e5) | privacy, cost at scale, offline | you host/scale the GPUs |
| Fine-tuned domain model | specialised jargon, after other fixes | needs labelled data + eval |

> Decision rule: **start `3-small`; upgrade to `3-large`/OSS only when evaluation justifies it; go
> open-source for privacy/cost; fine-tune last.** Always embed **chunks and queries with the same model**.

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Retrieval quality collapses | Query & chunks embedded with **different models** | Use one model everywhere |
| DB insert error on vector size | Column dims ≠ model dims | Match `vector(N)` to the model (or `dimensions=`) |
| OSS retrieval mediocre | Missing required **query prefix/instruction** | Add the model's documented prefix |
| Truncation/empty for long chunks | Chunk exceeds embedder **context length** | Smaller chunks (Lesson 03) |
| Poor multilingual matches | English-only model on multilingual docs | Multilingual model (e.g. multilingual-e5) |

## 📌 Quick Reference (cheat-sheet)

```text
Default:    text-embedding-3-small (1536D)         resp.data[i].embedding
Accuracy:   text-embedding-3-large (3072D) [+ dimensions=256..1024 to shrink]
Open-source: SentenceTransformer("BAAI/bge-large-en-v1.5").encode(x, normalize_embeddings=True)
Compare:    MTEB leaderboard -> read the RETRIEVAL column, not the average
RULES:      same model for chunks + queries · DB dims must match · normalize -> cosine=dot
```

- **Decision rule:** 3-small default → 3-large/OSS when measured-better → fine-tune last.
- **Gotchas:** never mix models; match DB dimensions; OSS query prefixes; re-embedding is costly.

## 🛑 STOP — Self-Check

**Question:** Why must the **query** and the **document chunks** be embedded with the *same* model — and
what specifically breaks if a teammate embeds new documents with `3-large` while queries still use
`3-small`?

<details>
<summary>Answer</summary>

Each model defines its **own** meaning-space and (here) a **different dimension count** (3072 vs 1536).
Two concrete failures: (1) **dimension mismatch** — a 3072-d document vector can't even be compared
with a 1536-d query vector (the similarity/DB operation errors or is undefined); (2) even at equal
dims, the coordinate systems differ, so distances are **meaningless** and retrieval returns near-random
chunks. Fix: embed **everything** — chunks and queries — with one model; changing it means re-embedding
the whole corpus.
</details>

## 🎯 Interview angle

Common: *"How do you choose an embedding model?"* Win it by naming the **axes** (accuracy via MTEB-
retrieval, dimensions/cost, context length, language, privacy/open-vs-closed), giving a **default**
(`3-small`, upgrade when measured), and citing the two hard rules: **same model for chunks+queries**
and **dimensions must match the DB**. Mentioning **Matryoshka `dimensions`** to trade size for cost is
a strong senior signal.
