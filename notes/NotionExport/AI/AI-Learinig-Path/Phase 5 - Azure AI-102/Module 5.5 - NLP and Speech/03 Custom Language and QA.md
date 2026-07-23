# 03 — Custom Language (CLU) & Question Answering

> Phase 5 · Module 5.5 · Lesson 3 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 NLP (15–20%)**
> *"Implement custom language models" is an explicit exam objective — the answer when prebuilt text features
> can't capture *your* intents, entities, or FAQs.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Prebuilt Language (Lesson 01) handles *generic* text. But it doesn't know **your** app's
intents ("book / cancel / check status"), **your** entity types, or **your** FAQ answers. For those you **train**:
**Conversational Language Understanding (CLU)** for intents + entities, and **custom question answering** for an
FAQ knowledge base. The exam tests creating, training, deploying, testing, and consuming these — plus **custom
translation** for domain language.

**Why care:** explicit exam objective and the backbone of any task-oriented bot or assistant.

## 🔑 New Terms (plain English)
- **CLU (Conversational Language Understanding)** — classifies the user's **intent** and extracts **entities**.
- **Utterance** — an example sentence you give CLU to learn from ("I want to cancel my order").
- **Intent / entity** — what the user wants / the details in their request (order number, date).
- **Custom question answering** — a **knowledge base** of Q&A pairs built from docs/URLs.
- **Multi-turn** — follow-up questions that depend on the previous answer.
- **Custom translation** — train Azure Translator on your domain's bilingual pairs.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: training a receptionist + an FAQ binder)
You teach a new receptionist your **common requests** (intents) and the **key details** to note (entities) by
giving examples (utterances). Separately, you give them an **FAQ binder** (custom QA) so they can answer common
questions verbatim. **Aha!:** **intent = what the caller wants**, **entity = the details**, **QA = canned answers** —
and all three are *trained on your data*, then deployed.

## ⚙️ Stage 2 — How It Works (each a mini-reference)

#### CLU: create intents, entities & utterances → train → deploy → test → consume
- **What & why:** define intents + entity types, add **utterances**, train, evaluate, deploy to an endpoint, and
  call from your app. **✅ Use when:** routing task-oriented requests ("book/cancel/check"). **🚫 Avoid → prebuilt
  NER:** for generic entities. **⚠️ Gotcha:** few/imbalanced utterances = weak intent recognition.

#### Optimise, back up & recover a CLU model
- **What & why:** improve with more utterances, and **export/back up** projects so you can restore. **✅ Use when:**
  production governance. **⚠️:** version your deployments; test before swapping.

#### Custom question answering (knowledge base)
- **What & why:** build a KB from FAQ docs/URLs; add Q&A pairs, **alternate phrasing**, **chit-chat**, and
  **multi-turn** follow-ups; train → test → publish; supports **multi-language** and **export**. **✅ Use when:**
  an FAQ/help bot with stable answers. **🚫 Avoid → CLU:** when you need *intents*, not canned answers. **🚫 Avoid →
  OpenAI/RAG:** when answers are open-ended/large-corpus. **⚠️:** keep the KB curated and fresh.

#### Custom translation
- **What & why:** train Translator on your **domain bilingual pairs** for better jargon/terminology translation.
  **✅ Use when:** generic translation mangles your terms. **🚫 Avoid → generic Translator:** when it's already good. **⚠️:** needs quality parallel data.

> 🔬 **Under the hood:** CLU and custom QA train **small models** on your utterances / Q&A pairs and deploy as
> endpoints; custom translation fine-tunes Translator on your parallel corpus. All are "your data → trained model
> → deployed endpoint", the same loop as Custom Vision (5.4) but for language.

### 💻 The SDK in code
```python
# CLU runtime: pip install azure-ai-language-conversations
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential

clu = ConversationAnalysisClient("https://<resource>.cognitiveservices.azure.com/",
                                 AzureKeyCredential("<key>"))
result = clu.analyze_conversation(task={
    "kind": "Conversation",
    "analysisInput": {"conversationItem": {
        "id": "1", "participantId": "1",
        "text": "cancel my booking for the 5th"}},
    "parameters": {"projectName": "travel", "deploymentName": "production"},
})
pred = result["result"]["prediction"]
print(pred["topIntent"], pred["entities"])     # 'CancelBooking', [date entity ...]
```
Custom **question answering** is a different client:
```python
# pip install azure-ai-language-questionanswering
from azure.ai.language.questionanswering import QuestionAnsweringClient

qa = QuestionAnsweringClient("https://<resource>.cognitiveservices.azure.com/",
                             AzureKeyCredential("<key>"))
ans = qa.get_answers(question="How do I reset my password?",
                     project_name="faq", deployment_name="production")
for a in ans.answers:
    print(a.answer, a.confidence)
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| CLU pip package | `azure-ai-language-conversations` |
| CLU client/method | `ConversationAnalysisClient.analyze_conversation(task=...)` |
| CLU result path | `result["result"]["prediction"]["topIntent"]` / `["entities"]` |
| CLU project kinds | **Conversation** (intents+entities) · **Orchestration workflow** (route to CLU/QA/...) |
| QA pip package | `azure-ai-language-questionanswering` |
| QA client/method | `QuestionAnsweringClient.get_answers(question, project_name, deployment_name)` |
| Entity components | learned · list · prebuilt · regex |
| Lifecycle | author → train → **deploy (deploymentName)** → predict |

### 🎯 Exam facts to memorise
- **CLU replaces LUIS** (retired); **custom QA replaces QnA Maker** — both now live in **Azure AI Language**.
- CLU has **two project kinds:** **Conversation** (intents + entities) and **Orchestration workflow** (route an utterance to the right CLU/QA/other project).
- You always predict against a **`projectName` + `deploymentName`** — train, then **deploy** before predicting.
- CLU **entity components:** learned · list · prebuilt · regex (combine them).
- Custom QA features: **multi-turn** follow-up prompts, **alternate questions**, **chit-chat**, **synonyms**, a **confidence threshold**, and **active learning**.
- Custom QA sources = URLs, files, or manual Q&A pairs; the knowledge base can be **exported/imported**.

## 🚀 Stage 3 — In Practice / Why It Matters
A support assistant uses **CLU** to route "book / cancel / check status" (extracting order number + date as
entities), **custom QA** to answer the top 100 FAQs with multi-turn follow-ups, and **custom translation** for
its product terminology. On the exam: "route requests / extract details" → CLU; "answer FAQs" → custom QA;
"domain translation" → custom translation; "open-ended over many docs" → OpenAI + RAG (Module 5.2).

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Classify intent + extract entities | **CLU** |
| Answer a fixed set of FAQs (multi-turn) | **Custom question answering** |
| Generic entities (people/places) | **prebuilt NER** (Lesson 01) |
| Domain-specific translation | **Custom translation** |
| Open-ended answers over a big corpus | **OpenAI + RAG** (Module 5.2) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Wrong intent detected | too few/imbalanced utterances | add more, varied utterances; retrain |
| FAQ bot rigid on rephrasings | no alternate phrasing | add alternate phrasing + chit-chat |
| Used CLU for FAQs | wrong tool | use **custom QA** knowledge base |
| Used custom QA for open-ended | limited to KB pairs | use **OpenAI + RAG** |

## 📌 Quick Reference
- **CLU** = intents + entities (utterances → train → deploy → test → consume; back up/version).
- **Custom QA** = FAQ knowledge base (Q&A pairs, alternate phrasing, chit-chat, multi-turn, multi-language, export).
- **Custom translation** = domain Translator. Open-ended/large corpus → **OpenAI + RAG**.

## 🎯 Exam-style practice
**Q1.** One bot must decide whether an utterance goes to the **FAQ (QA)** project or the **booking (CLU)** project. What CLU project kind?
<details><summary>Answer</summary>An **Orchestration workflow** project — it routes each utterance to the appropriate connected CLU/QA project.</details>

**Q2.** `analyze_conversation` returns 200 but `topIntent` is wrong on every call. Likely cause?
<details><summary>Answer</summary>The model was trained but **not deployed**, or you passed the wrong **`deploymentName`/`projectName`** — predictions run against a **deployment**.</details>

**Q3.** Your FAQ bot must handle a **follow-up** that only makes sense after the previous answer. Which custom-QA feature?
<details><summary>Answer</summary>**Multi-turn** conversation (follow-up prompts) in the knowledge base.</details>

## 🛑 STOP — Self-Check
A travel app needs to (a) route messages like "**cancel my booking for the 5th**" (pulling out the action and
the date), and (b) answer its **top 50 FAQ questions, handling follow-ups**. Which custom-language feature for
each — and what data do you provide?

<details><summary>Answer</summary>

- **(a) Route "cancel… the 5th" → CLU** — define a `CancelBooking` **intent** and a date **entity**, provide
  example **utterances**, train, deploy, and consume. CLU classifies the intent and extracts the date.
- **(b) Top-50 FAQs with follow-ups → custom question answering** — build a **knowledge base** of Q&A pairs
  (with alternate phrasing and **multi-turn** follow-ups), train, test, publish.

Both are trained on *your* data then deployed as endpoints. (For open-ended answers over many documents you'd
use **OpenAI + RAG** from Module 5.2 instead.)
</details>

⏭️ **Next:** Module 5.6 — Knowledge Mining (Branch 6.1).
