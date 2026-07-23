# 01 — Framework Decision Matrix: Which Agent Framework, When

> Phase 3 · Module 3.2 · Lesson 1 · `[JD VERIFIED — ~70% of architect JDs test "which framework when"]`

> 🔬 **Currency (mid-2026):** LangGraph `1.2.x`, CrewAI `1.15.x`, OpenAI Agents SDK `0.17.x`,
> Microsoft Agent Framework (AutoGen + Semantic Kernel unified) GA, Google ADK. The landscape settled in
> 2026 around these five — knowing the *trade-offs* is the architect skill JDs probe.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** In Module 3.1 you learned LangGraph. But an *architect* is paid to **recommend
the right tool**, and 2026 has five serious agent frameworks. Pick wrong and you waste months: too much
ceremony for a quick demo, or too little control for a regulated system. Interviewers don't ask "can you
use LangGraph?" — they ask *"a team needs X; which framework and why?"* This lesson is that decision.

**Where this sits.** It opens Module 3.2: you know one framework deeply (3.1); now you map the rest so
you can *choose*. The next lessons go hands-on in the two that matter most beyond LangGraph (CrewAI,
Semantic Kernel) and give awareness of OpenAI's SDK.

**Why care.** "Framework landscape awareness" is ~70% of architect JDs. This is pure architect signal —
the ability to justify a choice with trade-offs is what the title pays for.

---

## 🔑 New Terms (plain English)

- **Agent framework** — a library that gives you the building blocks for agents (loops, tools, memory,
  multi-agent) so you don't hand-roll them.
- **Production readiness** — how much a framework gives you for *real* deployment: persistence,
  observability, control, recovery.
- **Token efficiency** — how few model tokens (and so how little money) a framework spends to do a task.
- **Role-based agents** — defining agents by a job description (role/goal) rather than a graph.
- **Control flow** — how explicitly you can dictate the order of steps (graph) vs let agents self-organise.
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: picking the right vehicle)

You wouldn't buy one vehicle for every job. **LangGraph** is a manual-transmission sports car: total
control, fastest on a hard track, but you shift every gear yourself. **CrewAI** is a minibus: pile a team
in and go *today* — perfect for a quick trip, less so for a precision race. **Microsoft Agent Framework**
is the corporate fleet vehicle: fits the company's fuel, depot, and compliance rules out of the box.
**OpenAI Agents SDK** is a rental from one chain: smooth and easy, but only their cars. **Google ADK** is
the vehicle tuned for one city's roads (GCP/Gemini).

**The "Aha!":** they're not better/worse — they trade **control vs speed-to-demo vs enterprise fit vs
provider lock-in**. The architect's job is matching the trade-off to the team and the stakes.

---

## ⚙️ Stage 2 — The frameworks (each as a mini-reference)

#### LangGraph — your primary
- **What & why:** low-level graph orchestration for complex, stateful agents needing explicit control,
  audit trails, and recovery. Highest production readiness.
- **Key features:** graph control flow, built-in checkpointing/persistence, streaming, LangSmith
  observability, human-in-the-loop, multi-agent.
- **✅ Use when:** complex/long-running agents; need control, audit, rollback; regulated or high-stakes.
- **🚫 Avoid when → use CrewAI:** you need a working multi-agent demo *today* and control matters less.
- **⚠️ Gotcha:** most verbose; you wire the graph yourself (worth it when control matters).

#### CrewAI — fastest role-based prototyping
- **What & why:** define agents by **role/goal/backstory** and let them collaborate. Idea → demo in
  2–4 hours. Named in TCS/Infosys/Accenture JDs.
- **Key features:** Agent/Task/Crew primitives; **Flows** for event-driven control; MCP support.
- **✅ Use when:** rapid prototyping, role clarity > control flow, content/research crews.
- **🚫 Avoid when → use LangGraph:** complex control flow, fine-grained recovery, top token efficiency.
- **⚠️ Gotcha:** less token-efficient on complex workflows; autonomy can wander (Flows help).

#### Microsoft Agent Framework (AutoGen + Semantic Kernel) — Azure/.NET enterprise
- **What & why:** unified MS framework, GA 2026; native Azure AD, compliance, Python **and** C#.
- **Key features:** plugin architecture, Azure-native connectors, OpenTelemetry, automatic planners.
- **✅ Use when:** Azure-native/regulated enterprises; teams wanting C# *or* Python; compliance-heavy.
- **🚫 Avoid when → use LangGraph:** non-Azure, want the richest open-source agent ecosystem.
- **⚠️ Gotcha:** best ROI inside Azure; less compelling on other clouds.

#### OpenAI Agents SDK — GPT-centric, low friction
- **What & why:** lightweight agents, handoffs, guardrails, sessions. Lowest friction if you live on
  OpenAI; also supports 100+ models via LiteLLM.
- **✅ Use when:** GPT-centric, smaller agent complexity, want minimal setup + built-in tracing.
- **🚫 Avoid when → use LangGraph:** complex stateful control / multi-provider routing as a core need.
- **⚠️ Gotcha:** richest features are OpenAI-first; thinner persistence than LangGraph.

#### Google ADK — GCP/Gemini-native
- **What & why:** Google's agent SDK for GCP-first, Gemini-heavy multimodal stacks.
- **✅ Use when:** GCP-native, Gemini-centric. **🚫 Avoid when → LangGraph/CrewAI:** not on GCP.
- **⚠️ Gotcha:** least relevant outside Google's ecosystem.

> 🔬 **Under the hood — they converge.** All five do the same core loop (LLM + tools + state) and now
> speak **MCP** (Module 3.4) for tools and increasingly **A2A** between agents. So the *choice* is rarely
> capability — it's **control vs speed vs ecosystem vs lock-in**. You can mix: a LangGraph supervisor with
> a CrewAI worker, all sharing MCP tools.

---

## 🚀 Stage 3 — In Practice / Why It Matters

A typical recommendation: **LangGraph** as the backbone, **CrewAI** for a fast proof-of-concept,
**Microsoft Agent Framework** for an Azure/.NET client, **OpenAI Agents SDK** when locked to GPT. Deep in
one (LangGraph), conversant in the rest — exactly what 3.2 builds. Saying *"CrewAI to demo in a week, then
port the keeper to LangGraph for control and audit"* is the architect answer interviewers want.

---

## ⚖️ Decision Matrix (the at-a-glance digest)

| If the team needs… | Recommend | Because |
|---|---|---|
| Control, audit, long-running, regulated | **LangGraph** | graph control + checkpointing + observability |
| A multi-agent demo this week | **CrewAI** | role-based, fastest to working crew |
| Azure/.NET enterprise, compliance | **MS Agent Framework** | Azure AD, C#+Python, planners |
| GPT-only, minimal setup | **OpenAI Agents SDK** | low friction, built-in tracing |
| GCP/Gemini-first | **Google ADK** | native to that stack |

---

## 🧠 Common Misconceptions

| Myth | Reality |
|---|---|
| "One framework wins." | They trade control vs speed vs ecosystem; pick per project. |
| "Frameworks lock your tools in." | MCP makes tools portable across all of them. |
| "CrewAI can't do production." | Flows add control; it just trails LangGraph on complex flows. |
| "Pick the framework first." | Pick by stakes/cloud/provider/speed; the framework follows. |

---

## 📌 Quick Reference

- **LangGraph** control/audit · **CrewAI** speed/roles · **MS Agent Fwk** Azure/.NET · **OpenAI SDK**
  GPT-simple · **ADK** GCP.
- Choice = **control vs speed vs ecosystem vs lock-in**, not capability.
- **MCP** makes tools portable; you can **mix** frameworks.
- Architect answer: prototype CrewAI → productionise LangGraph; MS Agent Framework for Azure clients.

---

## 🛑 STOP — Self-Check

A regulated bank (Azure, mixed C#/Python, needs audit + approvals) wants an internal agent; a startup
wants a flashy multi-agent demo for investors next week. Which framework for each, and why?

<details>
<summary>Answer</summary>

- **Bank → Microsoft Agent Framework** (or **LangGraph**): Azure AD, compliance, C#+Python suit the bank;
  audit/approvals → MS Agent Framework if Azure-locked, LangGraph if they want richest open control +
  checkpointing/HITL. Both give the audit a regulator demands.
- **Startup → CrewAI**: role-based agents = a working multi-agent demo in days. Control/efficiency matter
  less than speed-to-show; port keepers to LangGraph later.

The skill: match **control/compliance** (bank) vs **speed-to-demo** (startup), not "best framework."
</details>

---

⏭️ **Next:** Lesson 02 — **CrewAI hands-on**: build a crew (Agent/Task/Crew) and add **Flows** control.
