# 02 — Azure Document Intelligence

> Phase 5 · Module 5.6 · Lesson 2 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Knowledge Mining (15–20%)**
> *Extracting structured fields from forms/invoices is a named exam objective and one of the highest-ROI
> enterprise AI tasks. (Multimodal extraction is its sibling — Lesson 03.)*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** OCR gives you *text*; businesses need **fields** — the invoice total, the due date, the
line-items table, the ID's expiry. **Azure Document Intelligence** extracts that **structure** from documents:
ready-made **prebuilt** models for common docs (invoices, receipts, IDs), **custom** models trained on *your*
form layout, and **composed** models that route between several. The exam tests provisioning and building each.

**Why care:** explicit exam objective and a daily enterprise task (AP automation, onboarding, claims).

## 🔑 New Terms (plain English)
- **Prebuilt model** — ready-trained extractors for common docs (invoice, receipt, ID, business card, layout).
- **Custom model** — trained on a few labelled examples of **your** form layout.
- **Composed model** — a bundle of custom models with automatic routing by document type.
- **Field / key-value / table** — the structured outputs (named values, pairs, tabular data).
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a data-entry clerk who reads any form)
Hand a clerk an invoice and they don't just read it aloud (that's OCR) — they **type the right values into the
right boxes**: vendor, total, date, each line item. **Document Intelligence** is that clerk: for standard forms
it already knows the layout (prebuilt); for your unique form you **show it a few labelled examples** (custom);
and a **composed** model lets one clerk handle several form types. **Aha!:** OCR = text; Document Intelligence = *fields*.

## ⚙️ Stage 2 — How It Works (each a mini-reference)

#### Provision the resource
- **What & why:** create the Document Intelligence resource → endpoint + access to models. **✅ Always first.** **⚠️ Gotcha:** check region/model availability.

#### Use prebuilt models
- **What & why:** call ready-made extractors for **invoices, receipts, IDs, business cards, and general layout**.
  **✅ Use when:** the document is a common, standard type. **🚫 Avoid → custom:** when prebuilt already fits (no training needed). **⚠️:** verify field confidence.

#### Build a custom model (train, test, publish)
- **What & why:** label a few examples of **your** form, train, test, and publish to extract *your* fields. **✅
  Use when:** a unique/proprietary layout prebuilt can't read. **🚫 Avoid → prebuilt:** for standard docs. **⚠️:**
  you need several representative samples; consistent layout trains better.

#### Create a composed model
- **What & why:** bundle multiple custom models so one endpoint **auto-routes** by document type. **✅ Use when:**
  you process several different forms through one pipeline. **⚠️:** each sub-model still needs its own training.

> 🔬 **Under the hood:** Document Intelligence combines a **layout** model (text + tables + positions) with field
> extraction. Prebuilt models are pretrained on common docs; custom models do transfer learning on *your* few
> labelled samples; composed models classify-then-extract. It's "your data → trained model → endpoint" like
> Custom Vision, but for documents.

### 💻 The SDK in code
```python
# pip install azure-ai-documentintelligence
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential

client = DocumentIntelligenceClient(
    endpoint="https://<resource>.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>"),
)

# Analyze with a PREBUILT model (ASYNC: returns a poller you wait on)
poller = client.begin_analyze_document(
    "prebuilt-invoice",                                  # model ID (see table below)
    AnalyzeDocumentRequest(url_source="https://.../invoice.pdf"),
    # OR: body=open("invoice.pdf", "rb"), content_type="application/octet-stream"
)
result = poller.result()                                 # AnalyzeResult

for doc in result.documents:                             # one per detected document
    fields = doc.fields
    print(fields["VendorName"].value_string)             # extracted field value
    print(fields["InvoiceTotal"].value_currency,         # typed value ...
          fields["InvoiceTotal"].confidence)             # ... + per-field confidence
```
> Older exam questions may show the **Form Recognizer** SDK: package `azure-ai-formrecognizer`, client
> `DocumentAnalysisClient`, same `begin_analyze_document(...)` pattern — recognise both names.

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `azure-ai-documentintelligence` (older: `azure-ai-formrecognizer`) |
| Client | `DocumentIntelligenceClient(endpoint, credential)` |
| Call | `begin_analyze_document(model_id, AnalyzeDocumentRequest(...))` → poller → `.result()` |
| Result paths | `result.documents[].fields[]`, `.pages`, `.tables`, `.key_value_pairs`, `.styles` |
| Field props | `.value_string` / `.value_currency` / `.value_date` · `.confidence` · `.bounding_regions` |
| Prebuilt IDs | `prebuilt-read`, `prebuilt-layout`, `prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-idDocument`, `prebuilt-businessCard`, `prebuilt-tax.us.w2` |
| Custom build modes | `template` (consistent layout, ~5 samples) · `neural` (varied layouts) |
| Train/compose | `DocumentIntelligenceAdministrationClient.begin_build_document_model` / `begin_compose_model` |

### 🎯 Exam facts to memorise
- **OCR vs fields:** `prebuilt-read` = text only; `prebuilt-layout` = text **+ tables + selection marks + structure**; `prebuilt-invoice/receipt/idDocument` = **named fields**.
- **Async pattern:** `begin_analyze_document(...)` returns a **poller**; call `.result()` for the `AnalyzeResult`.
- **Custom training needs ≥ 5 labelled samples**; two build modes — **template** (fast, consistent layout) vs **neural** (varied/complex layouts).
- **Composed model** = several custom models behind one endpoint; a **classifier** routes each doc to the right sub-model.
- Every field carries a **`.confidence`** and **`.bounding_regions`** (where on the page it was found).
- Label & train visually in **Document Intelligence Studio**.

## 🚀 Stage 3 — In Practice / Why It Matters
Accounts-payable automation: a **prebuilt invoice** model extracts vendor/total/line-items; a **custom** model
reads the company's unique purchase-order form; a **composed** model routes a mixed inbox of both. Results flow
into the finance system (and can be indexed in **AI Search** for retrieval). On the exam: "standard invoice/
receipt/ID" → prebuilt; "our unique form" → custom; "several form types, one endpoint" → composed; "just the
text" → OCR; "mixed media" → Content Understanding (Lesson 03).

## ⚖️ Variations & When to Use
| The document is… | Use |
|---|---|
| A common type (invoice/receipt/ID) | **prebuilt model** |
| Your unique form layout | **custom model** |
| Several form types, one endpoint | **composed model** |
| Just text off an image | **AI Vision Read (OCR)** |
| Mixed media (docs/images/video/audio) | **Content Understanding** (Lesson 03) |
| A big corpus to search | **Azure AI Search** (Lesson 01) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Got text, needed fields | used OCR | use **Document Intelligence** field extraction |
| Custom model weak | too few/inconsistent samples | add more, consistent labelled forms |
| Reinvented invoice extraction | trained custom unnecessarily | use the **prebuilt invoice** model |
| Many form types, brittle routing | separate calls | use a **composed model** |

## 📌 Quick Reference
- **Prebuilt** (invoice/receipt/ID/layout) · **custom** (your form, train→test→publish) · **composed** (route
  many types).
- OCR gives text; Document Intelligence gives **fields/tables**. Multimodal → Content Understanding; search → AI Search.

## 🎯 Exam-style practice
**Q1.** You need **tables and selection marks** out of a form, but no named business fields. Which prebuilt model?
<details><summary>Answer</summary>`prebuilt-layout` — returns text, tables, selection marks and structure. (`prebuilt-read` is text only; `prebuilt-invoice` returns named invoice fields.)</details>

**Q2.** `begin_analyze_document(...)` returns immediately without results. Why, and what do you call?
<details><summary>Answer</summary>It's **asynchronous** and returns a **poller**; call `.result()` to wait for and get the `AnalyzeResult`.</details>

**Q3.** You must extract from **three different bespoke forms through one endpoint**. What do you build?
<details><summary>Answer</summary>Train a **custom model** per form (or one neural model), then a **composed model** that classifies each incoming doc and routes it to the right sub-model.</details>

## 🛑 STOP — Self-Check
A finance team processes (a) **standard supplier invoices**, and (b) the company's **own bespoke expense form**,
through one pipeline. Which Document Intelligence model(s) — and how do you handle both in one endpoint?

<details><summary>Answer</summary>

- **(a) Standard invoices → the prebuilt invoice model** (no training needed).
- **(b) Bespoke expense form → a custom model** trained on a few labelled examples of that form.
- **Both through one endpoint → a composed model** that bundles them and **auto-routes** each incoming document
  to the right sub-model.

(OCR alone would give text, not the vendor/total/line-item **fields** the finance system needs.)
</details>

⏭️ **Next:** 03 — Content Understanding (Branch 6.3).
