# 03 — Multimodal Chunking Strategy

> Phase 2 · Module 2.4 · Lesson 3 · `[OPTIONAL — awareness]`

> ⚠️ **Optional.** Follows directly from ColPali (lesson 02) and vision RAG (lesson 01). Useful in
> architecture whiteboarding; worth a single read-through without hands-on unless you're building visual RAG.

## 🗺️ Stage 0 — Concept Map

**The problem first.** Text chunking (Module 2.1 lesson 03) splits *prose* into passages. But a visual
document also contains **figures, charts, and tables** that aren't prose — and a chart's meaning often lives
in the **caption and surrounding text**, not the image alone. **Multimodal chunking** decides *what the
retrievable units are* for a document that mixes text and pictures: page images, isolated figures, and the
text that explains them.

**Where it sits.** The *ingestion* step for multimodal RAG — the visual counterpart of Module 2.1's text
chunking, feeding the vision retrieval/generation in lessons 01–02.

## 🔑 New Terms (plain English)

- **Multimodal chunk** — a retrievable unit that may be an **image** (a page or a figure), not just text.
- **Figure extraction** — detecting and cutting out charts/diagrams/tables from a page as separate items.
- **Page image** — a whole page rendered to an image (for VLM/ColPali retrieval).
- **Caption-based metadata** — attaching the figure's caption and nearby text to the image chunk so it's
  searchable by *meaning*, not just pixels.
  (See the [glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

## 🎈 Stage 1 — The Simple Idea (analogy: scrapbooking a report)

Imagine cutting a report into a scrapbook. You don't just snip paragraphs — you also cut out **each chart**
and **paste its caption next to it**, so later you can find "the revenue chart" by its words *and* see the
picture. Multimodal chunking does that: keep **page images** and **figures** as units, and **staple the
surrounding text** to each so it's findable.

**The "Aha!":** a figure with no attached text is hard to retrieve by a text query — so you pair each
visual chunk with the words that describe it.

## ⚙️ Stage 2 — How It Actually Works (overview)

Three common moves:

1. **PDF → page images.** Render each page to an image for VLM/ColPali retrieval:
   ```python
   import fitz                                   # PyMuPDF (Module 2.1 lesson 02)
   pix = page.get_pixmap(dpi=200)               # page -> image
   ```
   (`pdf2image` is the other common tool.)
2. **Figure extraction.** Detect and isolate charts/diagrams/tables as their **own** chunks, so a query can
   retrieve *just the chart* rather than the whole page.
3. **Caption-based metadata.** Attach each figure's **caption + nearby paragraph** to the image chunk as
   searchable text — so "Q3 revenue chart" finds the image even though the image has no words to embed.

> 🔬 **Under the hood:** retrieval needs *something embeddable* per chunk. For a pure image you either embed
> it with an image-native model (ColPali, lesson 02) **or** give it **text to embed** — its caption and
> surrounding context. That's why caption-based metadata matters: it lets a normal text retriever find a
> figure by what it's *about*, and lets you mix image chunks and text chunks in one index.

## ⚖️ Choices (awareness)

| Decision | Options | Note |
|---|---|---|
| **Unit** | whole page image vs isolated figures | pages = simplest (pairs with ColPali) · figures = more precise, more work |
| **Make it findable** | image-native embedding (ColPali) vs caption text | ColPali embeds the image · captions let a **text** retriever find it |
| **Defer?** | build vs awareness | if **ColPali is deferred, defer this too** — it's the same use case |

> Decision rule (awareness): **page-as-image + caption metadata is the simplest multimodal chunking; isolate
> individual figures only when query precision over specific charts justifies the extra pipeline.**

## 📌 Quick Reference

- **Multimodal chunking** = decide the retrievable units for text+image docs: **page images**, **figures**,
  and the **text that describes them**.
- PDF → page images (`pymupdf`/`pdf2image`) · extract figures · attach **caption + nearby text** as metadata.
- Make visual chunks findable: **ColPali** (image-native) **or** **caption text** (normal text retriever).

## 🛑 STOP — Self-Check

You store each chart from a report as an image chunk, but text queries like "show the revenue trend" never
retrieve them. What did the chunking step miss, and what's the fix?

<details>
<summary>Answer</summary>

A bare **image has no text to embed**, so a normal text retriever has nothing to match "revenue trend"
against — the chart is effectively invisible to text search. The fix is **caption-based metadata**: attach
each figure's **caption and surrounding paragraph** to the image chunk so it's findable by *meaning*.
(Alternatively, use an **image-native retriever like ColPali**, lesson 02, which embeds the image itself —
but caption metadata is the simplest way to keep image chunks searchable in a normal text index.)
</details>
