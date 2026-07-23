# 02 — ColPali Architecture

> Phase 2 · Module 2.4 · Lesson 2 · `[OPTIONAL — portfolio differentiator]`

> ⚠️ **Optional.** High-signal for **Architect portfolios** (~30% of architect JDs), but rarely a hard
> interview requirement. **Understand the concept** (page-as-image retrieval, late interaction) and
> reference it confidently; **build** it only for a standout portfolio project. (Model names are 2026 examples.)

## 🗺️ Stage 0 — Concept Map

**The problem first.** Lesson 01 showed VLMs can *read* a page image. But how do you **retrieve** the
right page image for a query in the first place? The usual route is **OCR → embed the text → retrieve** —
which re-introduces the exact OCR fragility VLMs were meant to avoid (charts, layouts, scans all break at
the OCR step). **ColPali's insight:** skip OCR entirely for retrieval too — **embed the page as an image**
and match queries directly against it.

**Where it sits.** The *retrieval* half of multimodal RAG: an image-native alternative to "OCR-then-embed,"
so both retrieval **and** generation can be visual end-to-end.

## 🔑 New Terms (plain English)

- **ColPali** — a retrieval model that embeds **document pages as images** and matches text queries to them
  (no OCR). Built on a small VLM (**PaliGemma**).
- **Page-patch embeddings** — instead of one vector per page, ColPali keeps **many** vectors — one per
  image **patch** (a small square of the page).
- **Late interaction** — compare query and document at the **token/patch level at query time**, instead of
  squashing each into a single vector first.
- **MaxSim** — the late-interaction score: for **each query token**, take its **best-matching page patch**,
  then sum those best matches.
- **`byaldi`** — a small library that makes building a ColPali retriever easy.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: scanning a page with your finger)

A normal embedding squashes a whole page into **one** vector — like summarising a page in a single word,
then matching on that word. **ColPali** instead keeps a vector for **every little patch** of the page, and
when you ask a question, **each word of your question runs its finger across the page to find its
best-matching patch** (MaxSim). So "Q3 revenue" can land precisely on the *cell in the table* showing it —
even though no OCR ever read that cell.

**The "Aha!":** don't compress the page (or the query) into one vector before comparing. Keep both detailed
and match **token-to-patch at query time** — that's **late interaction**, and it's why ColPali nails
complex layouts.

## ⚙️ Stage 2 — How It Actually Works (overview)

1. **Index:** render each document page to an **image**, pass it through ColPali (PaliGemma), and store its
   **per-patch** embeddings (many vectors per page).
2. **Query:** embed the text query into per-token vectors.
3. **Score (MaxSim / late interaction):** for **each query token**, find its **most similar page patch**;
   **sum** those best similarities → the page's score. Rank pages by that score.
4. **Answer:** feed the top page image(s) to a VLM (lesson 01) to generate the answer.

```python
# Conceptual (byaldi):
from byaldi import RAGMultiModalModel
rag = RAGMultiModalModel.from_pretrained("vidore/colpali")
rag.index(input_path="reports/", index_name="reports")     # pages -> patch embeddings
results = rag.search("Q3 revenue by region", k=3)          # late-interaction retrieval -> page images
```

> 🔬 **Under the hood:** a single-vector embedding throws away *where* on the page the match was. ColPali
> keeps **one vector per image patch**, and **MaxSim** lets every query token attend to its **best** patch —
> so the match is **localised** (it can hit the exact table cell or chart bar). The cost is storage (many
> vectors per page) and a heavier scoring step — the classic *late-interaction* trade-off (more accurate,
> more expensive) that ColBERT pioneered for text and ColPali brings to document *images*.

## ⚖️ When ColPali wins (and when it doesn't)

| Documents | Best approach |
|---|---|
| Complex layouts, embedded charts, scanned/handwritten | **ColPali** (image-native retrieval, no OCR) |
| Clean digital text | **Text RAG** (cheaper, simpler) |
| Visual docs but cost-sensitive | **VLM-to-text** (lesson 01) — describe images once, then text RAG |

> Decision rule (awareness): **ColPali shines when the *layout itself* carries meaning and OCR mangles it;
> for clean text or tight budgets, text RAG or VLM-to-text is more practical.**

## 📌 Quick Reference

- **ColPali = retrieve document *pages as images*, no OCR.** Built on **PaliGemma**; library: **`byaldi`**.
- **Late interaction (MaxSim):** keep per-patch (page) and per-token (query) vectors; each query token
  matches its **best** patch, then sum — localised, accurate, heavier.
- **Wins on** complex/visual layouts; **costs** more storage + compute than single-vector retrieval.

## 🛑 STOP — Self-Check

In one or two sentences: how does ColPali's retrieval differ from normal "OCR → embed text → retrieve," and
*why* does that help on a page full of charts and tables?

<details>
<summary>Answer</summary>

Normal retrieval **OCRs** the page into text, then embeds that text — so anything OCR mangles (charts,
multi-column tables, scans) is broken *before* retrieval. **ColPali skips OCR**: it embeds the page **as an
image** into **many per-patch vectors**, and at query time uses **late interaction (MaxSim)** so each query
token matches its **best-matching patch** of the page. Because the match is **localised to regions of the
image**, "Q3 revenue" can land on the exact table cell or chart bar — detail a single OCR'd-text embedding
would have lost.
</details>
