# 03 — Semantic Kernel / Microsoft Agent Framework

> Phase 3 · Module 3.2 · Lesson 3 · `[JD VERIFIED — ~48%, 🟡 SHOULD; mandatory for Azure/enterprise clients]`

> 🔬 **Currency (mid-2026):** **Microsoft Agent Framework** is GA — **AutoGen + Semantic Kernel unified**,
> Python **and** C#, Azure-native. Semantic Kernel (SK) lives on as its plugin foundation. Taught here on
> its own terms (no .NET cross-mapping).

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Many enterprises run on Azure with strict identity, compliance, and telemetry
rules. A pure-Python open-source agent stack means bolting all that on by hand. **Microsoft Agent
Framework** is the Azure-native answer: agents with **Azure AD identity**, **compliance controls**, and
**OpenTelemetry** built in — usable from Python *or* C#. Its capability model is **plugins**: every skill
is a typed, injectable unit, so an agent is assembled from labelled capabilities, not raw prompts.

**Where this sits.** The framework you recommend for Azure/regulated clients; LangGraph/CrewAI remain
your defaults elsewhere. SHOULD-level: build a basic agent, know when to recommend it.

**Why care.** ~48% of JDs (more for enterprise/Azure) — and the natural recommendation when a client is
already Azure-committed.

---

## 🔑 New Terms (plain English)

- **Kernel** — the central object that holds your AI services + plugins and runs them (the "engine").
- **Plugin** — a bundle of related capabilities you register with the kernel.
- **KernelFunction** — one capability: native code or a prompt template, callable by the agent.
- **Planner** — auto-generates a multi-step plan from a goal (like a built-in supervisor).
- **Connector** — adapter to a model provider (e.g. Azure OpenAI).
- **Microsoft Agent Framework** — the unified Azure-native agent framework (AutoGen + SK).
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: head chef + labelled appliances)

The **Kernel** is a head chef. **Plugins** are labelled appliances (oven, mixer). **KernelFunctions** are
the buttons. The **Planner** writes the recipe order from "make dinner." Add new appliances as plug-ins;
the chef uses them without rewiring. **Aha!:** capability is **modular and typed** — assemble agents from
plugins, not giant prompts.

---

## ⚙️ Stage 2 — How It Works

```python
# pip install semantic-kernel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = Kernel()
kernel.add_service(AzureChatCompletion(deployment_name="gpt-4o", ...))  # Azure-native
kernel.add_plugin(parent_directory="plugins", plugin_name="Email")       # capabilities as plugins
result = await kernel.invoke_prompt("Summarise inbox and draft replies") # planner sequences plugins
```

- **Plugin (group of capabilities).** Each AI capability is a typed, registered plugin, so you assemble an
  agent from labelled parts. **✅ Use when:** Azure/.NET shops, capabilities reused across agents. **🚫 Avoid
  → LangGraph:** non-Azure or you want the richest open-source ecosystem. **⚠️ Gotcha:** the payoff is biggest
  inside Azure; elsewhere you carry Azure gravity for little gain.
- **Planner (goal → steps).** Give it a goal and it generates the multi-step plan automatically — like a
  built-in supervisor. **✅ Use when:** you want auto-decomposition. **🚫 Avoid → write steps explicitly:**
  when the order must be exact. **⚠️ Gotcha:** generated plans vary run-to-run, so pin/validate them for
  regulated work. Azure AD identity and OpenTelemetry tracing are built in.

> 🔬 **Under the hood:** the kernel is a dependency-injection container of plugins + connectors; the planner
> is an LLM emitting a plugin-call sequence; it speaks MCP. AutoGen adds multi-agent conversation on top.

---

## 🚀 Stage 3 — In Practice

Recommend for Azure-native/regulated clients wanting C#+Python, AD identity, OpenTelemetry. Conversant
beats deep here — pairs with the decision matrix (3.2.01).

---

## ⚖️ When to Use

| Need | Pick | Why |
|---|---|---|
| Azure/.NET, compliance | **MS Agent Fwk/SK** | AD, telemetry, plugins, C#+Python |
| Open control/audit | **LangGraph** | richest OSS control |
| Fast roles | **CrewAI** | speed |

---

## 🧠 Misconceptions

| Myth | Reality |
|---|---|
| "Only C#." | Python first-class. | 
| "Replaces LangGraph everywhere." | Shines in Azure; LangGraph leads OSS. |

---

## 📌 Quick Reference

`Kernel` + services + plugins; `KernelFunction` = capability; **Planner** = auto-plan; Azure-native + MCP.

---

## 🛑 STOP — Self-Check

Why is MS Agent Framework the natural pick for an Azure compliance-heavy bank but not a GCP startup?

<details><summary>Answer</summary>
It bakes in **Azure AD, compliance, OpenTelemetry, C#+Python** — the bank's world. On GCP it loses that
edge and adds Azure gravity → use **LangGraph/CrewAI** (or ADK). Match ecosystem to client.
</details>

---

⏭️ **Next:** Lesson 04 — **OpenAI Agents SDK** (awareness).
