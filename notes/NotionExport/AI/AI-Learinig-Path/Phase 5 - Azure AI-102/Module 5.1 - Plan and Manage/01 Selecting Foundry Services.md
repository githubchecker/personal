# 01 — Selecting the Right Microsoft Foundry Service

> Phase 5 · Module 5.1 · Lesson 1 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Plan & Manage (20–25%)**
> *"Which Azure AI service should I use?" is the single most common exam question — and the first decision on
> every real project. Get this map solid and you bank easy marks.*

> 🔬 Microsoft rebranded "Azure AI Foundry" → **Microsoft Foundry**. Exam questions describe a need and ask
> you to pick the right service.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Azure has a dozen AI services with overlapping names — Vision, Custom Vision, Language,
Speech, OpenAI, AI Search, Document Intelligence, Content Understanding. The exam (and your first design
meeting) constantly asks *"a company needs X — which service?"* Choose **Custom Vision** when plain **Vision**
would do and you've added weeks of labelling for nothing; reach for **OpenAI** to detect sentiment and you've
overpaid for a job a cheap prebuilt model does. This lesson is the **decision map** for the whole portfolio.

**Why care:** "select the appropriate service" is an explicit exam objective across **six** categories
(generative AI, vision, NLP, speech, information extraction, knowledge mining) and it's the architect's
day-one call on every project.

## 🔑 New Terms (plain English)
- **Microsoft Foundry** — Azure's unified AI platform (the place you create resources, browse the model
  catalogue, and run projects).
- **Prebuilt vs custom** — call a ready-made model (no training) versus train one on **your own labelled
  data** when your categories/forms are unique.
- **Single-service vs multi-service resource** — one key/endpoint for one service, or one shared key for
  several (handy for billing simplicity).
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: pick the right power tool)
You wouldn't grab a sledgehammer to hang a picture hook. Each Azure service is a tool sized to a job:
**prebuilt** services for common needs (they "just work" via an endpoint), **custom** services when your data
is unique enough to need training, and **generative** models for open-ended language. **Aha!:** match the
service to the *shape of the task*, and **prefer prebuilt** unless the domain genuinely forces custom — it's
cheaper, faster, and exam-correct more often than not.

## ⚙️ Stage 2 — The decision map (one mini-reference per service category)

#### Generative AI → **Azure OpenAI / Foundry models**
- **What & why:** open-ended language — chat, summarise, draft, code, reason, and RAG.
- **✅ Use when:** the output is free-form text/answers grounded on your data. **🚫 Avoid → Language:** for a
  fixed label like sentiment (overkill/overpriced). **⚠️ Gotcha:** needs grounding + content filters for safety.

#### Computer vision → **Azure AI Vision** (and **Custom Vision** for your own classes)
- **What & why:** Azure AI Vision tags objects, captions images, and reads text (**Read** OCR + handwriting),
  all prebuilt. **Custom Vision** trains on *your* categories.
- **✅ Use when:** generic objects/text → **AI Vision**; your 5 proprietary product types → **Custom Vision**.
  **🚫 Avoid → Document Intelligence:** structured forms/invoices. **⚠️:** custom needs enough labelled images.

#### NLP → **Azure AI Language**
- **What & why:** prebuilt sentiment, key phrases, entities, PII, language detection — plus custom intents
  (**CLU**) and custom **question answering**.
- **✅ Use when:** classify/extract from text. **🚫 Avoid → OpenAI:** open-ended generation. **⚠️:** custom
  intent/QA needs training utterances.

#### Speech → **Azure AI Speech**
- **What & why:** speech-to-text, text-to-speech, SSML control, custom speech, and speech translation.
- **✅ Use when:** voice in/out or live translation. **🚫 Avoid → Translator:** text-only. **⚠️:** jargon/accents may need custom speech.

#### Information extraction → **Document Intelligence** (forms) / **Content Understanding** (multimodal)
- **What & why:** **Document Intelligence** pulls *structured fields* from forms/invoices/IDs; **Content
  Understanding** extracts from documents, images, video, audio.
- **✅ Use when:** structured fields → Document Intelligence; mixed media → Content Understanding. **🚫 Avoid →
  plain OCR:** you need *fields*, not just text. **⚠️:** custom forms need a few labelled samples.

#### Knowledge mining → **Azure AI Search**
- **What & why:** index a big corpus, enrich it, and search it (keyword + semantic + vector) — the **RAG
  backbone**.
- **✅ Use when:** search/ground over thousands of docs. **🚫 Avoid → Document Intelligence:** single-form
  extraction. **⚠️:** needs an indexer + skillset to enrich.

> 🔬 **Under the hood:** almost everything is reached through **one Foundry resource** via REST/SDK. **Prebuilt
> = call an endpoint** (no training); **custom = label → train → publish → consume**. That single distinction
> answers most "which service" questions: is the need *common* (prebuilt) or *yours alone* (custom)?

### 📦 Service → SDK / package map
| Need | Service | Python package · client |
|---|---|---|
| Generate text/code/images | Azure OpenAI | `openai` · `AzureOpenAI` |
| Generic image analysis + OCR | AI Vision | `azure-ai-vision-imageanalysis` · `ImageAnalysisClient` |
| Your own image classes | Custom Vision | `azure-cognitiveservices-vision-customvision` |
| Sentiment/NER/PII/key phrases | AI Language | `azure-ai-textanalytics` · `TextAnalyticsClient` |
| Intents/entities / FAQ | CLU / custom QA | `azure-ai-language-conversations` / `-questionanswering` |
| Speech (STT/TTS/translate) | AI Speech | `azure-cognitiveservices-speech` |
| Translate text/documents | Translator | `azure-ai-translation-text` / `-document` |
| Fields from forms | Document Intelligence | `azure-ai-documentintelligence` · `DocumentIntelligenceClient` |
| Search a corpus / RAG | AI Search | `azure-search-documents` · `SearchClient` |
| Moderate content | Content Safety | `azure-ai-contentsafety` · `ContentSafetyClient` |
| Build on Foundry / agents | Foundry | `azure-ai-projects` · `AIProjectClient` |

### 🎯 Exam facts to memorise
- **Prefer prebuilt; go custom only for your own categories/forms** — the single biggest "which service" tell.
- **Generate** (free-form) → OpenAI; **fixed label** (sentiment/PII) → Language; never use OpenAI for a job a cheap prebuilt does.
- **OCR text** → AI Vision Read; **form fields** → Document Intelligence; **corpus search** → AI Search; **multimodal extract** → Content Understanding.
- **Your own image classes** → Custom Vision; **your own intents** → CLU; **your own forms** → custom Document Intelligence.
- A **multi-service `AIServices`** resource gives one key/endpoint across Vision+Language+Speech, etc.

## 🚀 Stage 3 — In Practice / Why It Matters
Real architectures mix these: AI Search + OpenAI for enterprise RAG; Document Intelligence feeding a Search
index; Vision OCR before Language entity extraction. On the exam, read the scenario's **keywords** — "our own
categories" → custom; "invoices/fields" → Document Intelligence; "search all our docs" → AI Search; "chat /
summarise / generate" → OpenAI; "sentiment / PII / key phrases" → Language.

## ⚖️ Variations & When to Use (the decision digest)
| The need is… | Pick | Tell-tale keyword |
|---|---|---|
| Open-ended text / chat / RAG answer | **Azure OpenAI** | generate, summarise, answer |
| Generic image tags / objects / text | **Azure AI Vision** | detect, OCR, caption |
| Our own image categories | **Custom Vision** | proprietary, train |
| Sentiment / entities / PII / intents | **Azure AI Language** | classify, extract |
| Voice in/out, SSML, translation | **Azure AI Speech** | speak, transcribe |
| Fields from forms/invoices | **Document Intelligence** | form, invoice, field |
| Multimodal extract (doc/img/video) | **Content Understanding** | multimodal |
| Search a big corpus | **Azure AI Search** | index, search, knowledge |

## 🐛 Common Errors & Fixes (exam traps)
| Trap | Wrong pick | Right pick |
|---|---|---|
| "Read text off scanned pages" | Custom Vision | **AI Vision Read (OCR)** |
| "Extract invoice totals/fields" | AI Vision OCR | **Document Intelligence** |
| "Detect sentiment of reviews" | Azure OpenAI | **Azure AI Language** |
| "Recognise our 5 product types in photos" | AI Vision | **Custom Vision** |
| "Answer questions over 10k docs" | OpenAI alone | **AI Search + OpenAI (RAG)** |

## 📌 Quick Reference
- **Prefer prebuilt; go custom only for your own categories/forms.**
- Generate → **OpenAI** · generic vision/OCR → **AI Vision** · own classes → **Custom Vision** · text labels →
  **Language** · voice → **Speech** · form fields → **Document Intelligence** · multimodal → **Content
  Understanding** · search corpus → **AI Search**.

## 🎯 Exam-style practice
**Q1.** "Detect the sentiment of 10,000 product reviews, cheaply." OpenAI or Language?
<details><summary>Answer</summary>**Azure AI Language** (`analyze_sentiment`) — a fixed label; OpenAI would be overkill/overpriced.</details>

**Q2.** "Read the totals and line-items off scanned invoices." AI Vision OCR or Document Intelligence?
<details><summary>Answer</summary>**Document Intelligence** (`prebuilt-invoice`) — you need **fields**, not just text. OCR gives text only.</details>

**Q3.** "Answer staff questions over 50,000 internal documents." Which two services combined?
<details><summary>Answer</summary>**Azure AI Search** (retrieval) **+ Azure OpenAI** (generation) — enterprise RAG.</details>

## 🛑 STOP — Self-Check
A logistics firm wants to (a) read the printed text off delivery labels, and (b) recognise its **own 5
package-damage categories** in photos. Which service for each — and why are they different?

<details><summary>Answer</summary>

- **(a) Read printed text → Azure AI Vision (Read / OCR)** — text extraction is a *generic, prebuilt*
  capability; no training needed.
- **(b) Own 5 damage categories → Custom Vision (image classification/object detection)** — these are
  *proprietary categories* the prebuilt model has never seen, so you must **label and train**.

The deciding question is always **common vs yours-alone**: common → prebuilt (AI Vision); your own categories
→ custom (Custom Vision).
</details>

⏭️ **Next:** 02 — Create & deploy a Foundry service.
