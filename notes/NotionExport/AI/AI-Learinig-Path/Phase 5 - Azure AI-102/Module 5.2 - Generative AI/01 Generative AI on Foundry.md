# 01 — Generative AI on Microsoft Foundry

> Phase 5 · Module 5.2 · Lesson 1 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Generative AI (15–20%)**
> *Building a grounded, evaluated genAI app on Foundry is the centre of gravity of the exam's generative-AI
> domain — and the everyday work in an Azure AI engineering role.*

> You built RAG and agents from scratch in Phases 1–4. This lesson maps those exact ideas to **Microsoft
> Foundry's** managed building blocks: hub/project → deploy → Prompt Flow → grounding → evaluation → SDK.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** A raw model in a playground isn't a solution. To ship one on Azure you must: set up a
**workspace** (hub + project), **deploy** a model, wire a **pipeline** (Prompt Flow), **ground** it on your
own data so it stops hallucinating (RAG via Azure AI Search), **evaluate** it so you know it's good, then
**integrate** it into an app via the SDK — with prompts kept as reusable **templates**. The exam walks through
exactly this lifecycle; skip grounding and it hallucinates, skip evaluation and quality silently regresses.

**Why care:** "build generative AI solutions with Microsoft Foundry" is a core exam objective and the literal
job description of an Azure AI engineer.

## 🔑 New Terms (plain English)
- **Hub** — the top-level Foundry workspace (shared resources, security, connections) for a team.
- **Project** — a scoped workspace inside a hub where you build one solution.
- **Prompt Flow** — Foundry's visual pipeline builder for chaining prompts, data lookups, and Python into a
  RAG/agent flow (with built-in evaluation).
- **Grounding (RAG)** — making the model answer **from your data** by retrieving relevant chunks (usually via
  an Azure AI Search index) and putting them in the prompt.
- **Evaluation run** — scoring a model/flow on metrics like groundedness, relevance, coherence (Azure's
  equivalent of RAGAS from Phase 4.1).
- **Prompt template** — a parameterised, versioned prompt you reuse instead of hard-coding strings.
- **Foundry SDK** — the library (`azure-ai-projects` / related) that calls your project's models/flows from app code.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a managed restaurant kitchen)
Foundry is a shared, managed kitchen. The **hub** is the building (utilities, security); a **project** is your
station; **Prompt Flow** is the recipe board that chains steps; **grounding** wires in your pantry (your data)
so dishes are made from *your* ingredients, not invented ones; **evaluation runs** are blind taste-tests; the
**SDK** is the hatch that serves the dish to the dining room (your app). **Aha!:** every piece of RAG you
hand-built in Phase 2 exists here as a managed, mostly-visual block — you assemble rather than wire from scratch.

## ⚙️ Stage 2 — How It Works (the lifecycle, each step a mini-reference)

#### Plan & prepare
- **What & why:** define the use case, data sources, success metrics, and Responsible-AI needs *before*
  building. **✅ Always.** **⚠️ Gotcha:** no defined eval metric = no way to know if it works.

#### Create a hub, project & resources
- **What & why:** a **hub** holds shared connections (Azure OpenAI, AI Search, storage) + security; a
  **project** is where you build. **✅ Use a shared hub when:** multiple teams/projects reuse connections.
  **🚫 Avoid → many disconnected resources:** harder to govern. **⚠️:** connections (to OpenAI, Search) live at the hub.

#### Deploy the right genAI model
- **What & why:** from the model catalogue, deploy GPT-4o / GPT-4.1 / Phi / Llama as a named deployment. **✅
  Use when:** matching capability vs cost. **🚫 Avoid → biggest by default:** right-size it. **⚠️:** your flow/app references the **deployment name**.

#### Implement a Prompt Flow
- **What & why:** a visual DAG chaining inputs → lookups → LLM nodes → outputs, with built-in evaluation and
  tracing. **✅ Use when:** low-code RAG/agent pipelines and quick iteration. **🚫 Avoid → hand-coded LangGraph
  (Phase 3):** when you need complex stateful control. **⚠️:** keep nodes small; use variants to A/B prompts.

#### Implement RAG by grounding on your data
- **What & why:** "Add your data" wires **Azure AI Search** (your indexed docs) into the flow so answers cite
  your sources. **✅ Use when:** factual Q&A over company docs. **🚫 Avoid → fine-tuning for facts:** RAG is the
  right tool for knowledge. **⚠️:** quality depends on the index (chunking, embeddings — Phase 2).

#### Evaluate models & flows
- **What & why:** run an evaluation over a dataset for **groundedness, relevance, coherence, fluency** (LLM-as-
  judge, like RAGAS). **✅ Use when:** picking a model or before/after a change. **🚫 Avoid → ship-and-hope:**
  no eval = silent regressions. **⚠️:** judge metrics cost calls and wobble — use a fixed test set.

#### Integrate via the Foundry SDK + use prompt templates
- **What & why:** call the deployed model/flow from your app with the SDK; keep prompts as **versioned
  templates** (with placeholders) rather than inline strings. **✅ Use when:** any real app. **⚠️:** template
  versioning makes prompt changes reviewable and reversible.

> 🔬 **Under the hood:** Foundry's "Add your data" provisions a RAG pattern = **Azure OpenAI + Azure AI Search**
> (retrieve top chunks → stuff into the prompt → generate with citations). Evaluation is an LLM-as-judge
> service scoring a dataset. Prompt Flow compiles your visual graph into a runnable pipeline you can deploy as
> an endpoint. It's the Phase 2 RAG pipeline and Phase 4 eval, productised behind a portal + SDK.

### 💻 The SDK in code
The **Foundry project** client exposes the project's connections (Azure OpenAI, AI Search) and evaluation.
```python
# pip install azure-ai-projects azure-identity
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),       # Entra ID — no keys
)
# An Azure OpenAI client already wired to the project's model connection:
client = project.inference.get_azure_openai_client(api_version="2024-10-21")
resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": "Hi"}])
```
**Evaluation** is its own package — score a dataset on RAG metrics:
```python
# pip install azure-ai-evaluation
from azure.ai.evaluation import evaluate, GroundednessEvaluator, RelevanceEvaluator

results = evaluate(
    data="qa_testset.jsonl",                   # rows of {query, context, response, ground_truth}
    evaluators={
        "groundedness": GroundednessEvaluator(model_config),
        "relevance":    RelevanceEvaluator(model_config),
    },
)
```
> 🔎 Note: the Foundry SDK surface evolves quickly — memorise the **workflow** (project → connections →
> evaluate) and the **evaluator names**, and confirm exact class/method names against current docs.

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| Project pip package | `azure-ai-projects` (+ `azure-identity`) |
| Project client | `AIProjectClient(endpoint, credential)` |
| Get model client | `project.inference.get_azure_openai_client(...)` / `get_chat_completions_client()` |
| Evaluation package | `azure-ai-evaluation` → `evaluate(data, evaluators={...})` |
| Built-in evaluators | Groundedness · Relevance · Coherence · Fluency · Similarity · F1 |
| Prompt templates | **`.prompty`** files (versioned) |
| RAG grounding | "Add your data" = Azure OpenAI + **AI Search** index |
| Workspace | **hub** (shared connections/security) → **project** (one solution) |

### 🎯 Exam facts to memorise
- **Hub vs project:** a **hub** holds shared connections (Azure OpenAI, AI Search, storage) + security; a **project** is one solution inside it.
- **Grounding (RAG)** fixes *facts* — wire an **AI Search** index via "Add your data"; **fine-tuning** is for behaviour/format, not knowledge.
- **Evaluation** uses LLM-as-judge metrics: **groundedness, relevance, coherence, fluency** (the Azure equivalent of RAGAS).
- **Prompt flow** = visual DAG (inputs → lookups → LLM nodes → outputs) with built-in evaluation + tracing; deploys as an endpoint.
- **Prompt templates** are versioned **`.prompty`** files — reviewable/reversible, not inline strings.
- The project client uses **Entra ID** (`DefaultAzureCredential`) and reuses the hub's **connections**.

## 🚀 Stage 3 — In Practice / Why It Matters
The standard enterprise build: hub + project → deploy GPT-4o → Prompt Flow that **grounds on an AI Search
index** of company docs → **evaluate** groundedness/relevance on a test set → deploy the flow as an endpoint →
call it from the app via the **SDK**, with prompts as templates. This is the exam's "build a genAI solution"
narrative end-to-end, and it reuses everything from Phases 2 and 4 — just Azure-managed.

## ⚖️ Variations & When to Use
| Decision | Options | Pick |
|---|---|---|
| Pipeline | Prompt Flow vs LangGraph (Phase 3) | low-code RAG → Prompt Flow · complex stateful control → LangGraph |
| Reduce hallucination | grounding (RAG) vs fine-tune | facts/knowledge → **grounding** · format/behaviour → fine-tune (Phase 4.4) |
| Workspace | shared hub vs isolated project | reuse connections across teams → hub · single solution → project |
| Pick a model | frontier vs small | right-size capability vs cost; confirm with eval runs |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Bot invents facts | no grounding | "Add your data" → ground on an **AI Search** index |
| Quality silently drops | no evaluation | run **evaluation** on a fixed test set before shipping |
| Poor retrieval | weak index | fix chunking/embeddings in AI Search (Phase 2) |
| Prompt change broke prod | inline prompt strings | use **versioned prompt templates** |
| 404 calling the model | used model name | reference the **deployment name** |

## 📌 Quick Reference
- **Lifecycle:** plan → hub/project → deploy model → Prompt Flow → **ground on AI Search** → **evaluate** →
  SDK + prompt templates.
- Grounding fixes facts; evaluation catches regressions; right-size the model; call the **deployment name**.

## 🎯 Exam-style practice
**Q1.** A chatbot invents facts. Grounding or fine-tuning — and which Azure service does grounding use?
<details><summary>Answer</summary>**Grounding (RAG)** via "Add your data", which uses an **Azure AI Search** index. Fine-tuning is for behaviour/format, not facts.</details>

**Q2.** You must catch quality regressions before shipping a prompt change. What do you run, and on what?
<details><summary>Answer</summary>An **evaluation** (`azure-ai-evaluation`'s `evaluate`) on a **fixed test set** with metrics like **groundedness/relevance**, ideally in CI.</details>

**Q3.** Where do shared connections (Azure OpenAI, AI Search) and security live — hub or project?
<details><summary>Answer</summary>The **hub** (shared); a **project** is a single solution that reuses them.</details>

## 🛑 STOP — Self-Check
Your Foundry chatbot answers company-policy questions but keeps **making things up**, and a prompt tweak last
week quietly **made answers worse** without anyone noticing. Which two Foundry features fix each problem?

<details><summary>Answer</summary>

1. **Hallucination → grounding (RAG) on your data.** Use "Add your data" to wire an **Azure AI Search** index
   of the policy docs into the flow so the model answers *from* your sources (with citations) — not invention.
   (Fine-tuning would be the wrong tool; that's for behaviour/format, not facts.)
2. **Silent quality drop → evaluation runs.** Score the flow on a **fixed test set** (groundedness, relevance)
   before/after every change, ideally in CI — so a regression fails the build instead of reaching users.
</details>

⏭️ **Next:** 02 — Azure OpenAI (Branch 2.2).
