# 01 — Azure AI Search (Knowledge Mining)

> Phase 5 · Module 5.6 · Lesson 1 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Knowledge Mining (15–20%)**
> *Azure AI Search is the RAG backbone — named in enterprise JDs and the heart of the exam's knowledge-mining
> domain. You built this pattern in Phase 2; here it's the Azure-managed version.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** A company has thousands of documents nobody can find anything in. **Knowledge mining**
turns that pile into something **searchable and enriched**: ingest it, extract/enrich content (OCR, entities,
embeddings), and serve fast keyword + **semantic** + **vector** search. **Azure AI Search** does this, and it's
the **retrieval half of RAG** — the index your Azure OpenAI app grounds on. The exam tests provisioning, indexes,
**skillsets**, indexers, custom skills, query syntax, knowledge store, and semantic/vector search.

**Why care:** explicit exam objective *and* the standard enterprise RAG backbone (Phase 2, Azure-managed).

## 🔑 New Terms (plain English)
- **Index** — the searchable schema (fields + their types) your documents are stored and queried in.
- **Indexer** — a connector that **automatically pulls** data from Blob/SQL/Cosmos and feeds the index.
- **Skillset** — an enrichment pipeline of **skills** (OCR → key phrases → entities → **embeddings**).
- **Custom skill** — your own enrichment step (a web API the skillset calls).
- **Knowledge store** — saving enriched output as **projections** (files/objects/tables) for other uses.
- **Semantic ranker** — re-ranks results by meaning (`queryType: semantic`).
- **Vector field / hybrid** — embeddings in the index for vector + keyword (hybrid) retrieval — native RAG.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a librarian with an enrichment assembly line)
A new shipment of books arrives unsorted. A **librarian** runs each through an **assembly line** (skillset):
scan covers for text (OCR), tag topics, pull out names, and add a "meaning fingerprint" (embedding). Then files
a **catalogue card** (index entry) so any query — by keyword *or* by meaning — instantly finds it. **Aha!:** the
**index** is the catalogue; the **skillset** is the enrichment line; the **indexer** is the conveyor that feeds it.

## ⚙️ Stage 2 — How It Works (each piece a mini-reference)

#### Provision, create an index & define a skillset
- **What & why:** create the Search resource, define the **index** schema, and a **skillset** that enriches
  content (OCR, entities, embeddings). **✅ Use when:** building any search/RAG backend. **⚠️ Gotcha:** design fields
  (searchable/filterable/retrievable) deliberately up front.

#### Data sources & indexers
- **What & why:** point an **indexer** at Blob/SQL/Cosmos to **auto-ingest** (and re-ingest on a schedule). **✅
  Use when:** content lives in Azure stores. **🚫 Avoid → manual push:** when you can automate. **⚠️:** map source fields to index fields.

#### Custom skills
- **What & why:** add your own enrichment step (a web API) into the skillset. **✅ Use when:** you need logic the
  built-in skills don't provide. **⚠️:** it must meet the skill input/output contract.

#### Query an index (syntax, sort, filter, wildcards)
- **What & why:** full-text search with filters, sorting, facets, and wildcards (simple or full Lucene syntax).
  **✅ Use when:** retrieving results for users or for RAG. **⚠️:** only **filterable/sortable** fields support those ops.

#### Knowledge store (projections)
- **What & why:** persist enriched output as **file/object/table projections** for analytics or downstream apps.
  **✅ Use when:** you want to reuse enrichment beyond search. **⚠️:** separate from the search index — it's storage.

#### Semantic & vector search
- **What & why:** **semantic ranker** re-orders by meaning; **vector fields** enable embedding (vector) and
  **hybrid** search — the native RAG retrieval you built in Phase 2.3. **✅ Use when:** meaning matters / RAG. **🚫
  Avoid → keyword-only:** when synonyms/paraphrases matter. **⚠️:** vectors need an embedding step (skillset).

> 🔬 **Under the hood:** indexer pulls data → skillset enriches it (incl. embeddings) → index stores it → queries
> run keyword + **semantic** + **vector** (hybrid) retrieval. Wire the index to **Azure OpenAI** ("on your data")
> and you have the standard enterprise RAG — the Phase 2 pipeline, Azure-managed.

### 💻 The SDK in code
Azure AI Search has **three** client classes — one to **query**, one to **manage indexes**, one for **indexers/skillsets**.

```python
# pip install azure-search-documents
from azure.search.documents import SearchClient                  # query + upload documents
from azure.search.documents.indexes import (
    SearchIndexClient,     # create/manage INDEXES (schema, fields, vector + semantic config)
    SearchIndexerClient,   # create/manage DATA SOURCES, INDEXERS, SKILLSETS
)
from azure.search.documents.models import VectorizedQuery        # vector / hybrid search
from azure.core.credentials import AzureKeyCredential

search = SearchClient(
    endpoint="https://<service>.search.windows.net",
    index_name="contracts",
    credential=AzureKeyCredential("<query-key>"),
)

# --- Keyword + semantic query with filter & sort ---
results = search.search(
    search_text="early termination clause",   # full-text query
    query_type="semantic",                     # simple | full (Lucene) | semantic
    semantic_configuration_name="contracts-semantic",
    filter="region eq 'EU'",                   # OData $filter (filterable fields only)
    order_by=["effectiveDate desc"],           # sort (sortable fields only)
    select=["title", "effectiveDate"],         # projected fields (retrievable)
    top=5,
)
for r in results:
    print(r["title"], r["@search.score"], r.get("@search.reranker_score"))  # BM25 + semantic score

# --- Vector / hybrid query (RAG retrieval) ---
vq = VectorizedQuery(vector=embedding, k_nearest_neighbors=5, fields="contentVector")
hits = search.search(search_text="early termination", vector_queries=[vq])  # hybrid = text + vector
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `azure-search-documents` |
| Query client | `SearchClient(endpoint, index_name, credential).search(...)` |
| Index admin | `SearchIndexClient` — create_index, fields, vector + semantic config |
| Indexer admin | `SearchIndexerClient` — create_data_source_connection, create_indexer, create_skillset |
| Field attributes | searchable · filterable · sortable · facetable · retrievable · key |
| `query_type` | `simple` (default) · `full` (Lucene) · `semantic` |
| Built-in skills | `#Microsoft.Skills.Text.*` (KeyPhrase, EntityRecognition, Split, PIIDetection, AzureOpenAIEmbedding), `Vision.OcrSkill` |
| Custom skill | `#Microsoft.Skills.Custom.WebApiSkill` |
| Vector algorithm | **HNSW** (or exhaustive KNN); `VectorizedQuery(..., k_nearest_neighbors, fields)` |
| Score fields | `@search.score` (BM25) · `@search.reranker_score` (semantic, 0–4) |

### 🎯 Exam facts to memorise
- **Three clients:** `SearchClient` (query/upload) · `SearchIndexClient` (indexes) · `SearchIndexerClient` (data sources, indexers, skillsets).
- **Indexer pipeline:** data source → indexer → skillset (enrich) → index. Indexers can run on a **schedule** with change detection.
- **Field attributes are fixed at index design** — you can't filter/sort a field unless it's flagged `filterable`/`sortable`.
- **Knowledge store projections:** **file** (extracted images) · **object** (JSON) · **table** (relational rows).
- **Semantic ranker** adds `@search.reranker_score` (0–4) plus **captions** and **answers**.
- **Hybrid search** = keyword (BM25) + vector in one query, usually + semantic rerank — the strongest RAG retrieval.
- Azure OpenAI **"on your data"** wires this index in as the RAG source automatically.

## 🚀 Stage 3 — In Practice / Why It Matters
The canonical enterprise RAG: indexer ingests Blob PDFs → skillset runs **OCR + embeddings** → index with
**vector + semantic** → app queries **hybrid** and grounds **Azure OpenAI** on the results. On the exam: "auto-
ingest" → indexer; "enrich (OCR/entities/embeddings)" → skillset; "rank by meaning" → semantic; "embeddings/RAG"
→ vector/hybrid; "reuse enriched data" → knowledge store.

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Auto-ingest from Blob/SQL/Cosmos | **indexer + data source** |
| Enrich (OCR, entities, embeddings) | **skillset** (+ **custom skill**) |
| Rank by meaning | **semantic ranker** |
| Embedding / RAG retrieval | **vector + hybrid** |
| Reuse enriched output | **knowledge store** projections |
| Single form's fields | **Document Intelligence** (Lesson 02) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Only raw text, no enrichment | no skillset | add a **skillset** (OCR/entities/embeddings) |
| Poor relevance | keyword-only | enable **semantic** + **vector/hybrid** |
| Can't filter/sort a field | field not flagged | mark field filterable/sortable in the index |
| Manual re-uploads | no automation | use an **indexer** on a schedule |

## 📌 Quick Reference
- **Pipeline:** indexer → skillset (OCR/entities/**embeddings**) → index → query (keyword + **semantic** +
  **vector/hybrid**); **knowledge store** to reuse enrichment.
- Wire to **Azure OpenAI** for RAG. Single form → Document Intelligence; multimodal → Content Understanding.

## 🎯 Exam-style practice
**Q1.** You must create a **data source, an indexer, and a skillset** in code. Which client class?
<details><summary>Answer</summary>`SearchIndexerClient`. (`SearchIndexClient` manages the index schema; `SearchClient` queries/uploads documents.)</details>

**Q2.** A query must **filter on `category` and sort by `price`**, but the service rejects it. Most likely cause?
<details><summary>Answer</summary>Those fields aren't marked **filterable** / **sortable** in the index definition. Field attributes are fixed at index design — you'd recreate/update the index with the right attributes.</details>

**Q3.** You need retrieval that catches **paraphrases** (vector) *and* exact keywords, then **re-ranks by meaning**. What do you combine?
<details><summary>Answer</summary>**Hybrid search** (`search_text` + `vector_queries`) plus `query_type="semantic"` for the **semantic reranker** — keyword + vector + rerank.</details>

## 🛑 STOP — Self-Check
A firm wants to **search thousands of scanned PDF contracts by meaning** (not just keywords) and have an Azure
OpenAI bot answer from them. Outline the pipeline and the two search capabilities you must enable.

<details><summary>Answer</summary>

**Pipeline:** an **indexer** ingests the PDFs from Blob → a **skillset** runs **OCR** (to read the scans) and an
**embedding** skill → results land in an **index** with a **vector field** → the app queries and grounds **Azure
OpenAI** on the hits (RAG).

**Two capabilities to enable:** **vector search** (so "by meaning" works via embeddings, ideally **hybrid** with
keywords) and the **semantic ranker** (to re-order results by meaning). Keyword-only search would miss
paraphrases — exactly the Phase 2.3 hybrid+rerank pattern, Azure-managed.
</details>

⏭️ **Next:** 02 — Document Intelligence (Branch 6.2).
