# 03 — Chunking Strategies

> Phase 2 · Module 2.1 · Lesson 3 · `[MUST KNOW — JD VERIFIED]`

## 🗺️ Stage 0 — Concept Map

**The problem first.** You have clean text from Lesson 02. Now: embed a whole 50-page document as
**one** vector and it becomes mush — a single 1536-number summary can't represent 50 pages of distinct
topics, so retrieval matches nothing well. Embed every **sentence** alone and each chunk is too thin to
answer anything. **Chunking** is splitting documents into right-sized pieces so each vector captures
*one coherent idea* and retrieval returns precise, self-contained context.

**Chunking is the single biggest lever on RAG quality.** Most "our RAG gives vague answers" problems
are chunking problems, not model problems.

**Where it sits.** Step 2 of Phase A: load → **chunk** → embed → store. It decides *what a retrievable
unit even is*.

**Why care.** "Which chunking strategy for which document type" is explicitly called an **architect
decision** in the Road Map and shows up in interviews.

## 🔑 New Terms (plain English)

- **Chunk** — a small piece of a document; the unit you embed, store, and retrieve.
- **Chunk size** — how big each piece is (in **tokens** or characters).
- **Overlap** — repeating the last few tokens of one chunk at the start of the next, so an idea split
  across a boundary survives in at least one chunk.
- **Separator** — the character(s) a splitter prefers to break on (paragraph, line, space).
- **Recursive splitting** — try to split on the biggest separator first, fall back to smaller ones.
- **Semantic chunking** — split where the *meaning* shifts (detected via embeddings), not at a fixed size.
- **Document-aware (structure-aware)** — split on the document's own structure (headers, code blocks).
- **Parent-child (small-to-big)** — retrieve a small precise chunk but feed the LLM its larger parent.
  (Terms also in the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: cutting a film into scenes)

You wouldn't index a two-hour film as one blob, nor as 172,800 single frames. You cut it into
**scenes** — each a coherent, self-contained unit you can jump to. Chunking is cutting documents into
"scenes." Cut at fixed time and you slice mid-sentence-of-dialogue; cut at **scene boundaries** and
each piece makes sense on its own. **Overlap** is letting each scene start a second before the last one
ended, so a line spoken across the cut isn't lost.

**The "Aha!":** you're optimising for *"each chunk is one retrievable idea, understandable alone."*

## ⚙️ Stage 2 — How It Actually Works

**💢 The old/painful way** — `text[i:i+1000]` in a loop: split every 1000 characters blindly. It cuts
sentences, paragraphs, and tables in half, so half your chunks start mid-word and end mid-thought.
Retrieval then matches fragments and the LLM gets incoherent context. Every strategy below is a smarter
answer to "where do I cut?"

### 3.1 Fixed-size chunking (the baseline)

Split every *N* tokens/characters with overlap. Simple, predictable, structure-blind.

```python
# pip install langchain-text-splitters
from langchain_text_splitters import CharacterTextSplitter, TokenTextSplitter

splitter = TokenTextSplitter(chunk_size=400, chunk_overlap=40)   # count in TOKENS
chunks = splitter.split_text(text)
```

- **Key features:**
  - Deterministic, predictable chunk sizes — easy to budget tokens and cost.
  - Structure-blind — ignores sentence, paragraph, and table boundaries.
  - Token- or character-based (`TokenTextSplitter` vs `CharacterTextSplitter`).
- **✅ Use when:** uniform unstructured text; a fast baseline to beat; strict uniform token budgets.
- **🚫 Avoid when → use a sibling:** the text has real structure (paragraphs, headers, tables) → use
  **3.2 recursive** or **3.3 document-aware** instead.
- **⚠️ Gotcha:** with `chunk_overlap=0` it routinely slices sentences mid-thought — always set overlap.

### 3.2 Recursive character splitting — **the production default**

Tries a hierarchy of separators `["\n\n", "\n", " ", ""]`: split on paragraphs; if a piece is still
too big, split on lines; then spaces; then characters. So it breaks at the **most natural boundary
that fits**.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# count length in TOKENS (aligns with the embedding model's budget), not characters:
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500,        # ~500 tokens per chunk
    chunk_overlap=75,      # ~15% overlap so ideas survive boundaries
)
chunks = splitter.split_text(text)        # -> list[str], each a coherent passage
```

- **Key features:**
  - Separator hierarchy `["\n\n","\n"," ",""]` — paragraph → line → word → character.
  - Token-aware via `from_tiktoken_encoder` (aligns chunks with the embedder's budget).
  - Custom separators for code/markdown when needed.
- **✅ Use when:** the default for almost all prose and mixed text — start here.
- **🚫 Avoid when → use a sibling:** the doc has explicit structure to preserve exactly (markdown
  headers, code) → use **3.3 document-aware**; or topic boundaries matter more than size → **3.4 semantic**.
- **⚠️ Gotcha:** set `chunk_size` in **tokens** (`from_tiktoken_encoder`), not characters, or chunks can
  overflow the embedding model's input limit.

### 3.3 Document-aware (structure-aware) splitting

Use the document's own structure as boundaries — headers, code blocks, HTML sections.

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)
chunks = splitter.split_text(markdown_text)   # each chunk tagged with its header path as metadata
```

- **Key features:**
  - Splits on the document's own markers (`#`/`##`, HTML tags, code syntax).
  - Stores the header trail as **metadata** — excellent for citations and filtering.
  - Sibling splitters for **HTML** and **code** (`RecursiveCharacterTextSplitter.from_language(...)`).
- **✅ Use when:** structured docs — markdown wikis, source code, HTML, anything with clear sections.
- **🚫 Avoid when → use a sibling:** flat prose with no markers (e.g. a novel) → fall back to
  **3.2 recursive**.
- **⚠️ Gotcha:** one giant section can still exceed `chunk_size` — chain a recursive split *inside* each
  section to cap it.

### 3.4 Semantic chunking

Split where the **embedding similarity drops** between consecutive sentences — i.e. where the topic
changes — instead of at a fixed size.

```python
# pip install langchain-experimental langchain-openai
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

chunker = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-small"))
chunks = chunker.split_text(prose)            # boundaries fall at topic shifts
```

- **Key features:**
  - Topic-coherent, **variable-size** chunks (boundaries fall at meaning shifts).
  - Uses an embedding model to detect breakpoints; threshold type configurable (percentile/std-dev).
- **✅ Use when:** long flowing prose where topics drift and fixed sizes split awkwardly, and quality
  matters more than ingestion cost.
- **🚫 Avoid when → use a sibling:** cost/latency-sensitive or huge corpora (it runs an embedding pass
  while splitting) → use **3.2 recursive**; already-structured docs → use **3.3 document-aware**.
- **⚠️ Gotcha:** it's experimental and adds an embedding cost — **measure** (Lesson 05) that it actually
  beats recursive on *your* data before adopting it.

### 3.5 Parent-child (small-to-big retrieval)

Retrieve on **small** chunks (precise matching) but give the LLM the **larger parent** (rich context).
Best of both.

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

retriever = ParentDocumentRetriever(
    vectorstore=vstore,                                  # stores the SMALL child vectors
    docstore=docstore,                                   # stores the BIG parent texts
    child_splitter=RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=150),
    parent_splitter=RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=800),
)
```

- **Key features:**
  - Decouples the **match unit** (small child chunk) from the **context unit** (big parent).
  - Precise retrieval *and* rich context for the LLM in one mechanism.
  - Needs two stores: a vectorstore (child vectors) + a docstore (parent texts).
- **✅ Use when:** answers need surrounding context (legal/technical/policy) but you still want sharp,
  precise matching.
- **🚫 Avoid when → use a sibling:** chunks are already self-contained, or you want minimal
  infrastructure → use **3.2 recursive**.
- **⚠️ Gotcha:** more moving parts, and parents that are too big blow the context budget — size the
  parent split deliberately (e.g. ~800 tokens).

### 3.6 Contextual Retrieval — give each chunk its context back `[reference technique]`

A chunk pulled out of a document often **loses its context**. A chunk that says *"the limit is 30 days"* —
30 days of *what*? Embedded alone, it won't match "refund window." **Contextual Retrieval** (popularised by
Anthropic, 2024) fixes this by **prepending a short context line to each chunk before embedding it**:

- **Contextual chunk headers (cheap version):** prepend the **document title + section heading** to every
  chunk (`"[2026 Employee Handbook → Refunds] The limit is 30 days…"`).
- **LLM-written context (Anthropic's version):** ask an LLM, *given the whole document*, to write a 1–2
  sentence situating note for each chunk (`"This chunk is from the refund policy; it states the return
  window is 30 days from delivery."`), prepend it, **then** embed. Anthropic reports it substantially cuts
  failed retrievals — more still when combined with **BM25** (2.3 L01) and **reranking** (2.3 L03).
  - **✅ Use when:** chunks are ambiguous out of context — legal, policy, technical, or financial docs.
  - **🚫 Avoid when → plain chunking:** documents are short/self-contained, or the per-chunk LLM cost is too high.
  - **⚠️ Gotcha:** it adds an LLM call **per chunk** at index time — use **prompt caching** (Phase 1) over the
    shared document so you don't re-pay for the full document on every chunk.

> Related awareness: **proposition chunking** (split into atomic factual statements) and **sentence-window**
> retrieval (embed single sentences, return them *with* their neighbours) are other ways to fix the
> "chunk lacks context" problem — reach for them when recursive + contextual retrieval still isn't enough.

> 🔬 **Under the hood:** **overlap** exists because a single idea ("…the refund window is **30 days**
> from delivery…") might land exactly on a cut; repeating a slice on both sides guarantees one whole
> copy survives. **Recursive** splitting works because natural-language boundaries are hierarchical
> (paragraph ⊃ sentence ⊃ word), so trying the biggest-that-fits keeps chunks coherent. Counting in
> **tokens** (not characters) matters because the embedding model has a token budget and retrieval
> cost is per token — so token-sized chunks are predictable in both.

## 🚀 Stage 3 — In Practice / Why It Matters

The fastest way to improve a mediocre RAG is usually to fix chunking: switch blind fixed-size to
**recursive**, set size ~300–800 tokens with ~10–15% overlap, and use **document-aware** splitting for
structured sources. You'll *measure* the improvement with Recall@K (Lesson 05) — chunking changes are
exactly what the Lesson 06 milestone benchmarks before/after.

## ⚖️ Variations & When to Use

| Strategy | Use when… | Trade-off |
|---|---|---|
| Fixed-size (token) | uniform text; quick baseline | ignores structure |
| **Recursive** (default) | most prose | none major — start here |
| Document-aware | markdown/HTML/code with clear structure | needs structured input |
| Semantic | long prose, topic shifts matter | slower + embedding cost |
| Parent-child | need precise match **and** rich context | more storage/plumbing |

> Decision rule: **default to recursive; go document-aware for structured docs; add parent-child when
> the LLM needs more surrounding context than the matched chunk; reach for semantic only when fixed
> sizes clearly hurt.**

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Vague/partial answers | Chunks too **big** (diluted meaning) | Smaller chunks (~300–500 tokens) |
| Retrieved chunk lacks context | Chunks too **small** | Bigger chunks or **parent-child** |
| Idea cut across boundary, never retrieved | **No overlap** | 10–15% overlap |
| Tables/code shredded | Generic splitter on structured text | Document-aware/code splitter |
| Chunk exceeds model input | Size set in chars, not tokens | Use `from_tiktoken_encoder` |

## 📌 Quick Reference (cheat-sheet)

```text
Default:        RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                    chunk_size=500, chunk_overlap=75)
Size guide:     ~300–800 tokens; Overlap: ~10–15% of chunk_size
Structured:     MarkdownHeaderTextSplitter / HTML / code splitters
Topic-coherent: SemanticChunker(embeddings)   (slower, costs $)
Match vs context: ParentDocumentRetriever (small child match -> big parent context)
```

- **Decision rule:** recursive by default; structure-aware for structured docs; parent-child for context.
- **Gotchas:** count tokens not chars; always set overlap; never blind fixed-size on tables/code.

## 🛑 STOP — Self-Check

**Question:** You're chunking (a) a markdown engineering wiki with clear `##` sections, and (b) a flat
prose novel. Which strategy for each, and why?

<details>
<summary>Answer</summary>

- **(a) Wiki → document-aware** (`MarkdownHeaderTextSplitter`): the `##` headers are *natural,
  meaningful* boundaries, and keeping each section intact (with its header path as metadata) gives
  coherent chunks and great citations.
- **(b) Novel → recursive** (token-based, with overlap): flat prose has no headers, so fall back to the
  natural paragraph→sentence hierarchy. (Semantic chunking is a reasonable upgrade if topic shifts are
  subtle, at extra cost.)

The principle: **split on the document's real structure when it has one; otherwise recurse on natural
language boundaries.**
</details>

## 🎯 Interview angle

Expect *"How would you choose a chunking strategy?"* Answer with the **decision rule** (recursive
default → document-aware for structure → parent-child for context → semantic when needed), name
**size ~300–800 tokens + ~10–15% overlap**, and stress that you'd **measure** the choice with Recall@K
rather than guess. That framing — *strategy by document type, validated by metrics* — is exactly the
"architect decision" signal.
