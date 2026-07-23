# 01 — Text Analytics & Translator

> Phase 5 · Module 5.5 · Lesson 1 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 NLP (15–20%)**
> *Prebuilt text analytics + Translator are exam staples and the first tool for any "understand text" task on Azure.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** You have piles of text — reviews, tickets, emails, documents — and need a machine to
*understand* it: how does the writer feel, what's it about, who/what is mentioned, is there personal data, what
language is it, and can we translate it? **Azure AI Language** does all of this **prebuilt** (no training), and
**Azure Translator** handles 100+ languages. Reach for custom training only when categories are unique (Lesson 03).

**Why care:** "analyze and translate text" is an explicit exam objective and the default first tool for text tasks.

## 🔑 New Terms (plain English)
- **Sentiment analysis** — positive / negative / neutral (with confidence), even per sentence.
- **Key phrase extraction** — the main topics/talking points in the text.
- **Named-entity recognition (NER)** — pulls out people, places, organisations, dates, quantities.
- **PII detection** — finds (and can redact) personal data: names, emails, SSNs, phone numbers.
- **Language detection** — identifies which language the text is in.
- **Azure Translator** — translates text and whole documents across 100+ languages.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a lightning-fast reading assistant)
Hand text to an assistant who instantly tells you the **mood** (sentiment), the **gist** (key phrases), the
**who/what** (entities), flags any **personal data** (PII), says **what language** it's in, and can **translate**
it. **Aha!:** prebuilt NLP = call an endpoint, get structured results back; no model to train.

## ⚙️ Stage 2 — How It Works (each feature a mini-reference)

#### Sentiment analysis
- **What & why:** scores text positive/negative/neutral (overall and per sentence). **✅ Use when:** review/feedback
  analysis, support triage. **🚫 Avoid → OpenAI:** for a simple label (overkill). **⚠️ Gotcha:** sarcasm/mixed sentiment can confuse it — read confidence.

#### Key phrase extraction
- **What & why:** returns the main topics. **✅ Use when:** summarising what a document/batch is about. **⚠️:** it's phrases, not a written summary (use OpenAI for that).

#### Named-entity recognition (NER)
- **What & why:** extracts people/places/orgs/dates/quantities (and links some to Wikipedia). **✅ Use when:** structuring
  unstructured text. **🚫 Avoid → Custom NER:** for your own proprietary entity types (Lesson 03). **⚠️:** check confidence per entity.

#### PII detection
- **What & why:** finds and optionally **redacts** personal data. **✅ Use when:** compliance, masking before storage/logging. **⚠️:** pair with Presidio (Phase 4.3) for defence in depth; recall isn't 100%.

#### Language detection
- **What & why:** detects the language (+ confidence). **✅ Use when:** routing multilingual input to the right pipeline. **⚠️:** very short text is harder to detect.

#### Azure Translator
- **What & why:** translates **text and whole documents** across 100+ languages, preserving format. **✅ Use when:**
  multilingual apps, document translation. **🚫 Avoid → custom translation:** until generic quality is insufficient for your jargon (Lesson 03). **⚠️:** Document Translation keeps layout; text API is for snippets.

> 🔬 **Under the hood:** one **Azure AI Language** resource (+ a Translator resource) exposes these as prebuilt
> REST/SDK calls returning labels + confidence. No training — you send text, you parse JSON.

### 💻 The SDK in code
```python
# pip install azure-ai-textanalytics
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(
    endpoint="https://<resource>.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>"),
)
docs = ["The room was great but the food was terrible."]   # a BATCH of documents

s = client.analyze_sentiment(docs, show_opinion_mining=True)[0]
print(s.sentiment, s.confidence_scores)          # 'mixed' {positive, neutral, negative}

ents = client.recognize_entities(docs)[0].entities          # .text .category .confidence_score
pii  = client.recognize_pii_entities(docs)[0]               # .redacted_text + .entities
keys = client.extract_key_phrases(docs)[0].key_phrases      # ['room', 'food']
lang = client.detect_language(docs)[0].primary_language     # .name .iso6391_name .confidence_score
```
Translator is a **separate** resource/SDK:
```python
# pip install azure-ai-translation-text
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

tt = TextTranslationClient(credential=AzureKeyCredential("<key>"), region="<region>")
out = tt.translate(body=["Hello"], to_language=["fr", "de"])   # one call, many targets
print(out[0].translations[0].text)               # 'Bonjour'
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| Language pip package | `azure-ai-textanalytics` |
| Language client | `TextAnalyticsClient(endpoint, credential)` |
| Methods | `analyze_sentiment` (·`show_opinion_mining`) · `recognize_entities` · `recognize_linked_entities` · `recognize_pii_entities` · `extract_key_phrases` · `detect_language` |
| Sentiment values | positive · negative · neutral · **mixed** (+ per-sentence, opinion mining) |
| PII result | `.redacted_text` + `.entities[].category` |
| Language result | `.iso6391_name` + `.confidence_score` |
| Translator pip package | `azure-ai-translation-text` (docs: `azure-ai-translation-document`) |
| Translator ops | **translate · detect · transliterate**; `to_language` accepts many targets |

### 🎯 Exam facts to memorise
- **Language and Translator are SEPARATE resources** (Translator needs a **region**).
- `analyze_sentiment` returns positive/negative/neutral/**mixed** + per-sentence scores; `show_opinion_mining=True` adds **aspect-based** (opinion) analysis.
- `recognize_pii_entities` returns a ready **`redacted_text`** plus typed entities.
- **Translator has three operations:** translate, **detect**, **transliterate** (one `translate` call can target many languages).
- **Document Translation** (`azure-ai-translation-document`) is **async/batch** over Blob containers and **preserves layout**; the text API is for snippets.
- Inputs are **batched** documents (each with an id/language); check the per-item `confidence_score`.

## 🚀 Stage 3 — In Practice / Why It Matters
A support platform runs incoming tickets through **language detection** → **Translator** (to a common language)
→ **sentiment** (to prioritise angry customers) → **NER + key phrases** (to route/summarise) → **PII detection**
(to redact before storage). On the exam: "how do they feel" → sentiment; "what's it about" → key phrases;
"who/what" → NER; "mask personal data" → PII; "what language / translate" → language detection / Translator.

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Mood of text | **Sentiment** |
| Main topics | **Key phrases** |
| People/places/dates | **NER** |
| Find/redact personal data | **PII detection** |
| Which language | **Language detection** |
| Translate text/documents | **Translator** |
| Open-ended summary/generation | **Azure OpenAI** (not Language) |
| Your own intents/entities | **CLU / Custom NER** (Lesson 03) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Used OpenAI for sentiment | overkill | use prebuilt **sentiment** |
| Need your own entity types | generic NER misses them | train **Custom NER** (Lesson 03) |
| PII slips through | recall < 100% | layer Presidio (Phase 4.3) + review |
| Translation lost formatting | used text API on a doc | use **Document Translation** |

## 📌 Quick Reference
- **Prebuilt:** sentiment · key phrases · NER · PII · language detection · Translator (text + documents).
- Generation/summaries → **OpenAI**; your own intents/entities → **CLU/Custom NER**. Always check confidence.

## 🎯 Exam-style practice
**Q1.** A review says "Great location, awful service." What overall sentiment label, and how do you get the per-aspect detail?
<details><summary>Answer</summary>Overall **`mixed`**; pass **`show_opinion_mining=True`** to `analyze_sentiment` for aspect-based (opinion) breakdown ("location" positive, "service" negative).</details>

**Q2.** You must **mask SSNs/emails before storing** support text. Which method, and which property gives the masked text?
<details><summary>Answer</summary>`recognize_pii_entities(...)`; use the returned **`.redacted_text`** (plus `.entities` for categories).</details>

**Q3.** Translate one string into **French and German in a single call**, and separately **detect** an unknown language. Which service/ops?
<details><summary>Answer</summary>**Azure Translator**: `translate(body=[...], to_language=["fr","de"])` for the multi-target translation, and the **detect** operation for language identification.</details>

## 🛑 STOP — Self-Check
A multinational gets support emails in many languages and must (a) **redact personal data before storing them**,
and (b) **prioritise angry customers**. Which Azure AI Language features handle each, and what step comes first?

<details><summary>Answer</summary>

- **First step → language detection + Translator** to normalise the email to a common language for consistent processing.
- **(a) Redact personal data → PII detection** (detect + redact names/emails/SSNs before storage; layer Presidio
  for defence in depth).
- **(b) Prioritise angry customers → sentiment analysis** (route strongly-negative tickets to the front).

All prebuilt — no training — on the Azure AI Language resource.
</details>

⏭️ **Next:** 02 — Azure AI Speech (Branch 5.2).
