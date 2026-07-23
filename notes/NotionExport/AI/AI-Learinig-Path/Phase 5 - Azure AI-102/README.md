# Phase 5 — Azure AI Engineer Associate (AI-102)

> The capstone certification. You've **built** every system AI-102 tests; this phase fills the
> Azure-service gaps (Vision, Language, Speech, Search, Document Intelligence, Foundry) and maps each exam
> objective to a lesson. Pass mark **700/1000**. Built to the beginner reference bar — no .NET analogies.

> 🔬 Syllabus jotted from the **official Microsoft skills outline (as of 23 Dec 2025)** + the standard
> MicrosoftLearning labs. Microsoft rebranded "Azure AI Foundry" → **Microsoft Foundry**; lessons use that.

---

## 🔭 Topic & subtopic explorer (verified vs the official outline, 3×)

| Domain (exam weight) | Lesson | Official subtopics covered |
|---|---|---|
| **Plan & Manage 20–25%** | 5.1.01 Select Foundry services | genAI/vision/NLP/speech/info-extraction/knowledge-mining service choice |
| | 5.1.02 Create, deploy & secure | AI resource, model choice/deploy, SDKs, endpoint, CI/CD, containers, monitor, cost, keys, auth |
| | 5.1.03 Responsible AI & Content Safety | moderation, content filters, blocklists, prompt shields, harm detection, governance |
| **Generative AI 15–20%** | 5.2.01 GenAI on Foundry | hub/project, deploy model, prompt flow, **RAG grounding**, evaluate, SDK, prompt templates |
| | 5.2.02 Azure OpenAI + operationalise | provision, DALL-E, multimodal, params, monitoring, tracing, orchestration, fine-tune |
| **Agentic 5–10%** | 5.3.01 Agents on Foundry | Foundry Agent Service, Microsoft Agent Framework, multi-agent, deploy (→ Phase 3) |
| **Computer Vision 10–15%** | 5.4.01 Analyze images & OCR | visual features, objects/tags, Read OCR, handwriting |
| | 5.4.02 Custom Vision & Video | classify vs detect, label/train/evaluate/publish/consume, Video Indexer, Spatial Analysis |
| **NLP 15–20%** | 5.5.01 Text analytics & Translator | key phrases, entities, sentiment, language, PII, Translator |
| | 5.5.02 Speech | TTS/STT, SSML, custom speech, intent/keyword, speech translation |
| | 5.5.03 Custom language (CLU + QA) | intents/entities/utterances, custom QA knowledge base, multi-turn, custom translation |
| **Knowledge Mining 15–20%** | 5.6.01 Azure AI Search | index, skillset, indexers, custom skills, query syntax, knowledge store, semantic+vector |
| | 5.6.02 Document Intelligence & Content Understanding | prebuilt/custom/composed models; OCR; entities/tables; multimodal ingest |
| **Exam prep** | 5.7.01 AI-102 prep | study path, practice exams, focus areas |

All six skills-at-a-glance domains and every listed subtopic map to a lesson — verified three times against
the outline. None dropped.

## 🎯 JD-verified importance (real jobs vs exam weight)

> **Two lenses.** *Exam weight* = what AI-102 tests. *JD demand* = how often the skill appears in real **Azure
> AI Engineer / GenAI** postings (workspace Road Map JD scan, May 2026; re-validated Jun 2026 vs the Microsoft
> [Azure AI Engineer role page](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/)).
> Prioritise 🟢 **JD-Core** to *get hired*; cover 🔵 **Exam-forward** to *pass*. Niche ≠ skippable — every topic still has a lesson.

| Lesson | Exam weight | JD demand | Verdict |
|---|---|---|---|
| 5.6.01 Azure AI Search (RAG) | 15–20% | ★★★ ~90% (RAG) | 🟢 **JD-CORE** |
| 5.2.02 Azure OpenAI | 15–20% | ★★★ ~85% | 🟢 **JD-CORE** |
| 5.2.01 GenAI on Foundry (grounding/eval/prompt flow) | 15–20% | ★★★ high | 🟢 **JD-CORE** |
| 5.3.01 Agents on Foundry | 5–10% | ★★★ ~75% (rising) | 🟢 **JD-CORE (rising)** |
| 5.1.04 Responsible AI & Content Safety | 20–25% | ★★★ ~62% | 🟢 **JD-CORE** |
| 5.1.03 Manage, Monitor & Secure (auth/cost) | 20–25% | ★★★ ~60% | 🟢 **JD-CORE** |
| 5.1.01 Select the right service | 20–25% | ★★ architect call | 🟢 **JD-CORE (architect)** |
| 5.1.02 Create & Deploy (CI/CD, containers) | 20–25% | ★★ ~50% | 🟡 JD-Moderate |
| 5.2.03 Optimise & Operationalise | 15–20% | ★★ cost/ops | 🟡 JD-Moderate |
| 5.6.02 Document Intelligence | 15–20% | ★★ doc extraction | 🟡 JD-Moderate |
| 5.5.01 Text Analytics & Translator | 15–20% | ★★ NLP basics | 🟡 JD-Moderate |
| 5.4.01 Analyze Images & OCR | 10–15% | ★★ OCR common | 🟡 JD-Moderate |
| 5.5.02 Azure AI Speech | 15–20% | ★ voice-niche | 🔵 Exam-forward |
| 5.5.03 Custom Language (CLU & QA) | 15–20% | ★ bot-specific | 🔵 Exam-forward |
| 5.4.02 Custom Vision | 10–15% | ★ specialist | 🔵 Exam-forward |
| 5.6.03 Content Understanding | 15–20% | ★ new/niche | 🔵 Exam-forward |
| 5.4.03 Video (Indexer / Spatial Analysis) | 10–15% | ☆ niche | 🔵 Exam-only |

**How to read it:** 🟢 JD-Core = the exam *and* real jobs lean on it — master these (they're also your Phase 1–4
 strengths, Azure-mapped). 🟡 JD-Moderate = solid job value, know it well. 🔵 Exam-forward = tested but rarer in
 architect JDs — learn enough to pass, don't over-invest for the role.

## 📦 Modules
5.1 Plan & Manage · 5.2 Generative AI · 5.3 Agentic · 5.4 Vision · 5.5 NLP & Speech · 5.6 Knowledge Mining · 5.7 Exam Prep
> Terms → [AI Terms glossary](../AI%20Terms%20-%20Plain%20English%20Glossary.md).

## ✅ Status
**Complete & exam-ready** — all 18 lessons at the reference bar with runnable SDK code, 🎯 exam facts, and
exam-style practice MCQs; JD-verified importance mapped (above). Each lesson carries an `Importance:` header.
