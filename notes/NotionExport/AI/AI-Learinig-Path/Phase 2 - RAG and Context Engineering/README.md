# Phase 2 — RAG & Context Engineering

> **The most JD-validated skill cluster for AI engineers in 2026** — Retrieval-Augmented
> Generation (RAG) appears in ~85–90% of postings. This phase builds the full enterprise RAG stack
> end to end: **ingest → chunk → embed → store → retrieve → rerank → generate**, then extends it to
> multimodal / vision documents.

Anchored on the Road Map's Phase 2 and validated against a fresh 2026 official-docs pass
(pgvector 0.8.3, OpenAI `text-embedding-3-*`, sentence-transformers retrieve-&-rerank, Cohere
`rerank-v3.5`). Importance weighting uses the Road Map's 2026 JD frequencies as the signal.

## How this phase is taught

Every lesson follows the workspace lesson format
([.github/instructions/lesson-format.instructions.md](../.github/instructions/lesson-format.instructions.md)):
🗺️ Concept Map (problem-first) → 🔑 New Terms → 🎈 Simple Idea (analogy) → ⚙️ How It Works
(commented code) → 🚀 In Practice → ⚖️ Variations & When to Use → 🐛 Errors / 🧠 Misconceptions →
📌 Quick Reference → 🛑 STOP self-check. New terms link the shared
[AI Terms — Plain-English Glossary](../AI%20Terms%20-%20Plain%20English%20Glossary.md).

## JD-verified plan (importance-ranked)

🔴 MUST · 🟡 SHOULD · ⚪ OPTIONAL (labelled, never skipped)

### Module 2.1 — RAG Pipeline Architecture
| # | Lesson | Importance | JD signal |
|---|--------|-----------|-----------|
| 01 | [RAG Pipeline Architecture](Module%202.1%20-%20RAG%20Pipeline%20Architecture/01%20RAG%20Pipeline%20Architecture.md) | 🔴 MUST | ~90% |
| 02 | [Document Ingestion Pipeline](Module%202.1%20-%20RAG%20Pipeline%20Architecture/02%20Document%20Ingestion%20Pipeline.md) | 🔴 MUST | JD-verified |
| 03 | [Chunking Strategies](Module%202.1%20-%20RAG%20Pipeline%20Architecture/03%20Chunking%20Strategies.md) | 🔴 MUST | JD-verified |
| 04 | [Embedding Model Selection](Module%202.1%20-%20RAG%20Pipeline%20Architecture/04%20Embedding%20Model%20Selection.md) | 🔴 MUST | JD-verified |
| 05 | [Retrieval Evaluation](Module%202.1%20-%20RAG%20Pipeline%20Architecture/05%20Retrieval%20Evaluation.md) | 🟡 SHOULD | architect-bonus |
| 06 | [Milestone — Enterprise Document Q&A](Module%202.1%20-%20RAG%20Pipeline%20Architecture/06%20Milestone%20-%20Enterprise%20Document%20Q%26A.md) | — | — |

### Module 2.2 — Vector Infrastructure
| # | Lesson | Importance | JD signal |
|---|--------|-----------|-----------|
| 01 | [pgvector + HNSW / IVFFlat tuning](Module%202.2%20-%20Vector%20Infrastructure/01%20pgvector%20and%20HNSW%20Tuning.md) | 🔴 MUST | ~80% |
| 02 | [Pinecone](Module%202.2%20-%20Vector%20Infrastructure/02%20Pinecone.md) | 🔴 MUST | ~65% |
| 03 | [Qdrant](Module%202.2%20-%20Vector%20Infrastructure/03%20Qdrant.md) | 🔴 MUST | ~55% |
| 04 | [Weaviate](Module%202.2%20-%20Vector%20Infrastructure/04%20Weaviate.md) | ⚪ OPTIONAL | ~40% (awareness) |
| 05 | [Egress & Cost Architecture](Module%202.2%20-%20Vector%20Infrastructure/05%20Egress%20and%20Cost%20Architecture.md) | 🟡 SHOULD | architect-bonus |

### Module 2.3 — Advanced Search & Fusion
| # | Lesson | Importance | JD signal |
|---|--------|-----------|-----------|
| 01 | [BM25 / Sparse Retrieval](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/01%20BM25%20Sparse%20Retrieval.md) | 🔴 MUST | JD-verified |
| 02 | [Hybrid Search + Reciprocal Rank Fusion](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/02%20Hybrid%20Search%20and%20RRF.md) | 🔴 MUST | ~72% |
| 03 | [Cross-Encoder Reranking](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/03%20Cross-Encoder%20Reranking.md) | 🔴 MUST | ~65% |
| 04 | [Contextual Compression (LLMLingua)](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/04%20Contextual%20Compression.md) | ⚪ OPTIONAL | awareness |
| 05 | [GraphRAG](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/05%20GraphRAG.md) | ⚪ OPTIONAL | ~40% (awareness) |
| 06 | [Milestone — Hybrid Enterprise Search](Module%202.3%20-%20Advanced%20Search%20and%20Fusion/06%20Milestone%20-%20Hybrid%20Enterprise%20Search.md) | — | — |

### Module 2.4 — Multimodal & Vision RAG
| # | Lesson | Importance | JD signal |
|---|--------|-----------|-----------|
| 01 | [Vision-Language Models for Documents](Module%202.4%20-%20Multimodal%20and%20Vision%20RAG/01%20Vision-Language%20Models%20for%20Documents.md) | 🔴 MUST | ~62% |
| 02 | [ColPali Architecture](Module%202.4%20-%20Multimodal%20and%20Vision%20RAG/02%20ColPali.md) | ⚪ OPTIONAL | ~30% (portfolio) |
| 03 | [Multimodal Chunking](Module%202.4%20-%20Multimodal%20and%20Vision%20RAG/03%20Multimodal%20Chunking.md) | ⚪ OPTIONAL | awareness |
| 04 | [Milestone — Financial Report Analyser (vision)](Module%202.4%20-%20Multimodal%20and%20Vision%20RAG/04%20Milestone%20-%20Financial%20Report%20Analyser.md) | — | — |

## Phase 2 Capstone — Integrative Project

Combine every module into one **enterprise document-intelligence platform**: ingest a mixed PDF
corpus → chunk → embed → store in a vector DB → hybrid search (BM25 + dense) → cross-encoder rerank
→ grounded answer with citations, plus a vision path for scanned/figure-heavy pages.

## Currency notes (2026 research pass)

- **pgvector 0.8.3** (Postgres 13–18): HNSW (`m`, `ef_construction`, `ef_search`) + IVFFlat
  (`lists`, `probes`); newer **binary quantization**, **`halfvec`**, and **iterative index scans**.
- **OpenAI embeddings**: `text-embedding-3-small` (1536D), `text-embedding-3-large` (3072D);
  `dimensions` param = Matryoshka truncation; vectors normalised → cosine = dot product.
- **Reranking**: two-stage retrieve (bi-encoder) → rerank (cross-encoder); Cohere `rerank-v3.5`,
  open-source `BAAI/bge-reranker-v2-m3`.
- **LangChain** reorganised into `langchain-text-splitters`; `RecursiveCharacterTextSplitter` stable.
- **Vision**: GPT-5.5 is the current OpenAI flagship; vision RAG uses GPT-5.5 / GPT-4o / Claude
  vision / Azure AI Document Intelligence. *Model names change — always check the provider's docs.*
