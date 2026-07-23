# 01 — AI-102 Exam Preparation

> Phase 5 · Module 5.7 · Lesson 1 · **Importance: 🟡 STRATEGY · `[exam-readiness]`**
> *How to actually pass: weighting-aware focus, the standard study resources, and the high-frequency facts.*

---

## 🎯 What the exam is
**AI-102 — Designing and Implementing a Microsoft Azure AI Solution.** ~40–60 questions, **pass = 700/1000**,
mostly scenario-based ("a company needs X — which service / how do you configure it?"). You've **built** most of
it across Phases 1–4; Phase 5 filled the Azure-service gaps (Vision, Language, Speech, Search, Document
Intelligence, Foundry, Responsible AI). *(Note: the official study guide says exam AI-102 retires 30 Jun 2026 —
this is the final syllabus; check Microsoft Learn for the successor.)*

## 📊 Domain weighting → where to spend time
| Domain | Weight | Your readiness |
|---|---|---|
| Plan & manage an Azure AI solution | **20–25%** | Module 5.1 — drill service selection + responsible AI |
| Generative AI solutions | 15–20% | strong (Phases 1–4 + Module 5.2) |
| NLP solutions | 15–20% | Module 5.5 — **newer, drill it** |
| Knowledge mining & info extraction | 15–20% | Module 5.6 — **newer, drill it** |
| Computer vision | 10–15% | Module 5.4 — **newest, drill it** |
| Agentic solutions | 5–10% | strong (Phase 3 + Module 5.3) |

**Strongest (from prior phases):** generative AI, agentic. **Drill hardest (new Azure APIs):** Vision,
Language/Speech, AI Search, Document Intelligence — and the **"select the right service"** decision map (5.1.01).

## ✅ Study plan (resources + steps)
1. **Microsoft Learn AI-102 learning paths** (free, official) — do every module.
2. **MicrosoftLearning labs** (`mslearn-ai-vision`, `-ai-language`, `-ai-services`, `-knowledge-mining`,
   `-ai-agents`) — run each service hands-on **once**; muscle memory beats memorisation.
3. **Practice exams** (MeasureUp / Whizlabs, 2026) — repeat until consistently **≥85%**; review every wrong answer.
4. **Drill the decision maps:** service selection (5.1.01), prebuilt-vs-custom, and responsible-AI controls (5.1.04).
5. **Take the free Microsoft practice assessment** on the exam page before booking.

## 🧠 High-frequency facts to memorise
- **Pass score 700/1000.** Auth: **keys = dev, Entra ID + managed identity = prod**.
- **Prebuilt vs custom** is the key fork: common need → prebuilt; *your* categories/forms → custom (train).
- Vision: **Read** = OCR (printed + handwriting); **Custom Vision** = your image classes; **Spatial Analysis** =
  people movement; **Video Indexer** = video content.
- Language: sentiment/key-phrases/NER/**PII**/Translator = prebuilt; **CLU** = intents/entities; **custom QA** = FAQs.
- Search: **semantic** = rank by meaning; **vector/hybrid** = embeddings/RAG; **skillset** = enrichment; **indexer** = ingest.
- Doc extraction: **Document Intelligence** = form *fields* (prebuilt/custom/composed); **Content Understanding** = multimodal; OCR = text only.
- Responsible AI: **content filters** (output), **prompt shields** (jailbreak/injection), **blocklists**, **groundedness**.

## ⚖️ The one question type that repeats: "which service?"
Read the scenario keywords → map to the service (decision table in **Lesson 5.1.01**). This single skill covers
a large share of marks across every domain.

## 🎯 Exam-style practice (mixed, all domains)
**Q1.** Service to extract named fields from scanned invoices?
<details><summary>Answer</summary>**Document Intelligence** (`prebuilt-invoice`).</details>

**Q2.** Production auth for Azure OpenAI with no secret to leak?
<details><summary>Answer</summary>**Entra ID + managed identity** (`DefaultAzureCredential`).</details>

**Q3.** The four Content Safety harm categories and severity levels?
<details><summary>Answer</summary>Hate, Sexual, Violence, Self-Harm; severities **0, 2, 4, 6**.</details>

**Q4.** Rank search results by meaning, and retrieve by embeddings — two AI Search capabilities?
<details><summary>Answer</summary>**Semantic ranker** + **vector/hybrid** search.</details>

**Q5.** `client.analyze(...)` must return a caption and any text in one call — which features?
<details><summary>Answer</summary>`VisualFeatures.CAPTION` + `VisualFeatures.READ`.</details>

**Q6.** Route "book/cancel/check status" and extract a date — which Azure AI Language feature?
<details><summary>Answer</summary>**CLU** (intents + entities).</details>

**Q7.** Make a neural voice pronounce a brand name correctly and add pauses — which tool + method?
<details><summary>Answer</summary>**SSML** via `speak_ssml_async` (`<phoneme>`/`<lexicon>`, `<break>`).</details>

**Q8.** 404 DeploymentNotFound from Azure OpenAI though the model is deployed — fix?
<details><summary>Answer</summary>Call the **deployment name**, not the base model name.</details>

**Q9.** Run a custom image model offline on a device — what must you choose, and export to what?
<details><summary>Answer</summary>A **Compact** domain; export to **ONNX/TensorFlow/CoreML/Docker**.</details>

**Q10.** Reduce hallucination on a factual bot — grounding or fine-tuning?
<details><summary>Answer</summary>**Grounding (RAG)** — fine-tuning is for behaviour/format, not facts.</details>

**Q11.** Detect hidden "ignore your instructions" text in an uploaded document — which control?
<details><summary>Answer</summary>**Prompt shields** (indirect prompt-injection detection).</details>

**Q12.** Steady high-volume Azure OpenAI traffic needing predictable latency/cost — which option?
<details><summary>Answer</summary>**PTU** (provisioned throughput).</details>

## 🛑 STOP — Self-Check
Given the weighting and your background from Phases 1–4, which **three** domains deserve the most last-week
study, and what single cross-cutting skill should you over-practise?

<details><summary>Answer</summary>

**Three to drill:** **Computer Vision (10–15%), NLP/Speech (15–20%), and Knowledge Mining (15–20%)** — the newest
Azure-service APIs (Phases 1–4 already cover generative + agentic well). **Cross-cutting skill to over-practise:**
**"select the appropriate service"** (the decision map in 5.1.01) — it appears in every domain and is the single
highest-leverage exam skill. Also lock in the **700 pass score** and **keys-vs-managed-identity** auth rule.
</details>

🎓 **Phase 5 complete — and with it, the full AI Engineer/Architect Road Map (Phases 0→5).** See the
[Phase 5 README](../README.md).
