# 01 — Agents on Microsoft Foundry

> Phase 5 · Module 5.3 · Lesson 1 · **Importance: 🟡 SHOULD KNOW · `[JD VERIFIED]` · AI-102 Agentic (5–10%)**
> *"Implement an agentic solution" is a smaller exam domain, but agent-building on Azure is a fast-rising JD
> requirement. You already built agents deeply in Phase 3 — this is the Azure-native path.*

> You built agents from scratch in Phase 3 (LangGraph). The exam tests the **Azure-native** route: the
> **Foundry Agent Service** and the **Microsoft Agent Framework**. Same concepts, Azure hosting + governance.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** AI-102 wants you to stand up an agent the Azure way: understand what an agent is,
configure its resources, build a simple one with the **Foundry Agent Service**, build complex/multi-agent ones
with the **Microsoft Agent Framework**, then test and deploy. It's the managed, governed version of the agent
loop you hand-built in Phase 3.

**Why care:** it's an explicit (if small, 5–10%) exam objective, and "build agents on Azure" is increasingly in JDs.

## 🔑 New Terms (plain English)
- **Agent** — an LLM that runs in a loop, choosing tools/steps to reach a goal (Phase 3 recap).
- **Foundry Agent Service** — Azure's managed hosting for agents: define an agent + its tools + grounding, and
  Azure runs/scales it.
- **Microsoft Agent Framework** — the code-first framework (AutoGen + Semantic Kernel unified) for complex,
  multi-agent orchestration in Python/C# (Phase 3.2.03).
- **Multi-agent orchestration** — several specialised agents coordinated (supervisor/workers, Phase 3.1.04).
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: renting a managed garage)
Phase 3 was building a car from parts. The **Foundry Agent Service** is renting a **managed garage** that runs
and scales your car for you — you supply the design (instructions + tools), Azure handles hosting, identity,
and monitoring. The **Microsoft Agent Framework** is the full workshop for when you need to build a *fleet* that
coordinates. **Aha!:** same agent loop you know — Azure just hosts, secures, and scales it.

## ⚙️ Stage 2 — How It Works (each a mini-reference)

#### Understand the role & use cases of an agent
- **What & why:** an agent *acts* (calls tools, queries data, takes steps), unlike a one-shot chatbot. **✅ Use
  when:** the task needs tool use, multi-step reasoning, or autonomy. **🚫 Avoid → plain chat/RAG:** for simple Q&A.

#### Configure resources & build with the Foundry Agent Service
- **What & why:** define an agent in Foundry — instructions, **tools** (functions, code interpreter, your data),
  and grounding — and deploy it as a managed service. **✅ Use when:** a single managed agent with tools. **🚫
  Avoid → Microsoft Agent Framework:** for complex multi-agent control. **⚠️ Gotcha:** secure it with Entra ID
  identity and content safety (Module 5.1).

#### Implement complex agents with the Microsoft Agent Framework
- **What & why:** code-first (Python/C#) framework for **multi-agent orchestration**, custom control flow, and
  enterprise integration. **✅ Use when:** supervisor/worker topologies, multi-user, autonomous workflows. **🚫
  Avoid → Agent Service:** when a single managed agent suffices. **⚠️:** more code/ops to own.

#### Implement multi-agent workflows
- **What & why:** coordinate specialists — a supervisor routing to SQL/document/API agents (Phase 3.1.04) — with
  multi-user and autonomous capabilities. **✅ Use when:** the task spans domains. **⚠️:** add loop limits + HITL (Phase 3.5).

#### Test, optimise & deploy
- **What & why:** evaluate the agent (trajectory, tool use), tune, and deploy. **✅ Always before production.** **⚠️:** trace tool calls; gate risky actions with human approval.

> 🔬 **Under the hood:** it's the same ReAct loop + tools from Phase 3 — Azure adds managed hosting, Entra ID
> identity, content safety, and monitoring. The **Foundry Agent Service** is the low-friction managed path; the
> **Microsoft Agent Framework** is the code-first path for complex orchestration.

### 💻 The SDK in code
The **Foundry Agent Service** uses the project client: define an agent, then run threads/messages.
```python
# pip install azure-ai-projects azure-identity
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(endpoint="...", credential=DefaultAzureCredential())

agent = project.agents.create_agent(
    model="gpt-4o",                       # deployment name
    name="support-agent",
    instructions="You are a helpful support agent.",
    tools=[],                             # code interpreter, file search (RAG), function/OpenAPI tools
)
thread = project.agents.threads.create()                       # a conversation
project.agents.messages.create(thread.id, role="user", content="Where is my order?")
run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)  # runs the loop
```
For **complex multi-agent** orchestration you'd use the **Microsoft Agent Framework** (code-first, Python/C#).
> 🔎 Note: the Agents SDK surface evolves — memorise the objects (**agent · thread · message · run · tools**)
> and the managed-vs-framework choice over exact method signatures.

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| Managed agents pip | `azure-ai-projects` (+ `azure-identity`) |
| Build a single agent | **Foundry Agent Service** — `project.agents.create_agent(...)` |
| Core objects | **agent · thread · message · run** |
| Tools | code interpreter · **file search** (RAG) · function calling · OpenAPI · Bing grounding |
| Complex/multi-agent | **Microsoft Agent Framework** (code-first, AutoGen + Semantic Kernel) |
| Open-source alt | LangGraph (Phase 3) |
| Identity/safety | Entra ID + content safety + monitoring (Module 5.1) |

### 🎯 Exam facts to memorise
- **Single managed agent → Foundry Agent Service**; **complex/multi-agent → Microsoft Agent Framework**.
- Core objects: **agent** (model + instructions + tools), **thread** (conversation), **message**, **run** (executes the loop).
- Built-in tools: **code interpreter**, **file search** (grounding/RAG), **function calling**, **OpenAPI**, **Bing** grounding.
- It's the **same ReAct loop** as Phase 3 — Azure adds **hosting, Entra ID identity, content safety, monitoring**.
- Gate risky actions with **human-in-the-loop**; add **loop limits**; **test/evaluate** (trajectory, tool use) before deploy.
- Agentic is a **small exam domain (5–10%)** — know the two build paths and the object model.

## 🚀 Stage 3 — In Practice / Why It Matters
For a quick single agent with tools + your data, you'd reach for the **Foundry Agent Service**; for a coordinated
multi-agent enterprise assistant you'd use the **Microsoft Agent Framework** — both secured with identity and
content safety. (For deep agent *design* — ReAct, memory, supervisor/worker — see Phase 3; this lesson is the
Azure delivery layer the exam checks.)

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Single managed agent + tools | **Foundry Agent Service** |
| Complex / multi-agent orchestration | **Microsoft Agent Framework** |
| Deep custom control (open-source) | **LangGraph** (Phase 3) |
| Simple Q&A, no actions | plain chat / RAG (Module 5.2) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Over-built a simple bot | used multi-agent for Q&A | use grounded chat (5.2) |
| Single agent can't scale to many domains | one agent, too many tools | split into multi-agent (Agent Framework) |
| Unsafe agent actions | no guardrails | content safety + HITL approval (Phase 3.5 / 5.1) |
| No identity | key auth | Entra ID + managed identity |

## 📌 Quick Reference
- **Single managed agent → Foundry Agent Service.** **Complex/multi-agent → Microsoft Agent Framework.**
- Same ReAct loop as Phase 3; Azure adds hosting + identity + safety + monitoring. Test/evaluate before deploy.

## 🎯 Exam-style practice
**Q1.** A single managed agent must answer from your docs and call one API. Which service, and which tool gives the doc grounding?
<details><summary>Answer</summary>**Foundry Agent Service**; the **file search** tool provides document grounding (RAG), plus a **function**/OpenAPI tool for the API.</details>

**Q2.** Name the four core objects of the Agent Service in order of use.
<details><summary>Answer</summary>**agent** → **thread** → **message** → **run** (the run executes the tool-calling loop).</details>

**Q3.** You need coordinated specialist agents (SQL + docs + email) with custom control flow. Which option?
<details><summary>Answer</summary>The **Microsoft Agent Framework** (code-first multi-agent orchestration), not a single managed agent.</details>

## 🛑 STOP — Self-Check
A team wants a quick single agent that answers from company data and can call one API; another team needs a
coordinated set of specialist agents (SQL + docs + email) for an enterprise workflow. Which Azure option each?

<details><summary>Answer</summary>

- **Quick single agent → Foundry Agent Service** — a managed agent with tools + grounding, low friction.
- **Coordinated specialists → Microsoft Agent Framework** — code-first **multi-agent orchestration** (supervisor
  routing to workers).

Both are the same agent loop you mastered in Phase 3; Azure just hosts and governs them. (Deep design lives in Phase 3.)
</details>

⏭️ **Next:** Module 5.4 — Computer Vision (Branch 4.1).
