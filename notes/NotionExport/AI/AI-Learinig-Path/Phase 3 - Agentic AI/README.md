# Phase 3 — Agentic AI & Stateful Multi-Agent Systems

> **The highest-signal phase for Lead / Architect roles.** This is where an LLM stops being a
> question-answerer and becomes a *worker* that plans, calls tools, remembers, and collaborates with
> other agents. Hiring decisions are made here — so this phase is built to the same reference-grade
> bar as Phase 2 (every real choice gets a per-variation mini-reference; every hard term glossed).

---

## 🔭 Topic & subtopic explorer (JD-verified + standard-course cross-checked)

**How this plan was built (research-first):** the Road Map is the anchor; I then ran a *fresh* scan
of the authoritative sources to validate currency and ordering before writing —

- **Official GitHub docs (mid-2026):** LangGraph `1.2.6`, MCP Python SDK `1.28.1` (FastMCP),
  CrewAI `1.15.1`, OpenAI Agents SDK `0.17.7`.
- **Standard course cross-check:** **LangChain Academy — *Introduction to LangGraph*** (the de-facto
  standard syllabus): Module 0 setup → Modules 1–5 build *progressively* (state → memory/persistence
  → human-in-the-loop → streaming → multi-agent) → Module 6 deploy. This **confirms** the Road Map's
  Module 3.1 ordering, so we teach in that order.
- **Currency drift folded in:** ① LangGraph is now **1.x** (production-grade, stable API). ② MCP's
  recommended transport is now **Streamable HTTP** (SSE is legacy/superseded); MCP **v2** is in alpha.
  ③ CrewAI now ships **Flows** (event-driven control) *alongside* Crews — added as a gap-fill.

| # | Lesson | Importance | JD signal | Why it matters |
|---|--------|-----------|-----------|----------------|
| **3.1** | **LangGraph & Stateful Orchestration** | | | *Named explicitly in the majority of agentic JDs* |
| 3.1.01 | LangGraph Fundamentals (graph, state, edges) | 🔴 MUST | ~75% | The framework you'll build everything on |
| 3.1.02 | Cyclical Agent Patterns (ReAct, tools, reflection) | 🔴 MUST | ~75% | The actual "agent loop" |
| 3.1.03 | Memory & Persistence (checkpointers, threads) | 🔴 MUST | ~60% | What makes an agent *stateful* |
| 3.1.04 | Supervisor–Worker Multi-Agent | 🔴 MUST | ~65% | The dominant production topology |
| 3.1.05 | Advanced LangGraph (subgraphs, platform, streaming) | 🟡 SHOULD | bonus | Architect-level patterns |
| 3.1.06 | 🏁 Milestone — Multi-Agent Enterprise Assistant | 🔴 MUST | — | Portfolio centrepiece |
| **3.2** | **The 2026 Agent Framework Landscape** | | | *JDs test "which framework when"* |
| 3.2.01 | Framework Decision Matrix | 🔴 MUST | ~70% | The architect's recommendation skill |
| 3.2.02 | CrewAI hands-on (Crews **+ Flows**) | 🔴 MUST | ~55–65% | Named in TCS/Infosys/Accenture JDs |
| 3.2.03 | Semantic Kernel / Microsoft Agent Framework | 🟡 SHOULD | ~48% | Azure/.NET enterprise standard |
| 3.2.04 | OpenAI Agents SDK | 🟢 AWARENESS | emerging | GPT-centric, lowest friction |
| **3.3** | **Tool Definition & Function Calling** | | | *The single highest-frequency agentic skill* |
| 3.3.01 | JSON-Schema Tool Contracts | 🔴 MUST | ~80% | How an LLM calls your code |
| 3.3.02 | LangChain Tool Patterns (`@tool`, `StructuredTool`, `BaseTool`) | 🔴 MUST | ~80% | The everyday way to define tools |
| 3.3.03 | Practical Tools (SQL, REST, filesystem, code-exec) | 🟡 SHOULD | high | Real enterprise tool-building |
| **3.4** | **Model Context Protocol (MCP)** | | | *Now "table stakes" — 200+ servers* |
| 3.4.01 | MCP Architecture (host/client/server, transports, primitives) | 🔴 MUST | ~58% | The USB-C of AI tools |
| 3.4.02 | Building MCP Servers (FastMCP) | 🔴 MUST | ~58% | Expose your data/tools to any agent |
| 3.4.03 | Enterprise MCP Integrations + Security | 🟡 SHOULD | ~58% | Postgres/Blob/SharePoint, safe handlers |
| 3.4.04 | MCP in Multi-Agent & the A2A protocol | 🟡 SHOULD | bonus | Decoupled data layers; agent-to-agent |
| 3.4.05 | 🏁 Milestone — MCP server + LangGraph agent | 🔴 MUST | — | Decoupling demonstrated |
| **3.5** | **Sandboxed Execution & Governance** | | | *Eval/governance = "hardest to fake"* |
| 3.5.01 | Sandboxed Code Execution (E2B + Docker) | 🟢 OPTIONAL | awareness | Why agents need a sandbox |
| 3.5.02 | Human-in-the-Loop (HITL) Design | 🔴 MUST | high | Approval gates for risky actions |
| **3.6** | **Workflow Automation Context** | | | |
| 3.6.01 | n8n for AI Workflow Orchestration | 🟢 OPTIONAL | awareness | Low-code vs code-first trade-off |

**Legend:** 🔴 MUST (build hands-on) · 🟡 SHOULD (build, lighter) · 🟢 OPTIONAL/AWARENESS (read, labelled — never skipped).

---

## 📦 Modules

- **Module 3.1 — LangGraph & Stateful Orchestration** — the core framework. ✅ *complete*
  - [01 LangGraph Fundamentals](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/01%20LangGraph%20Fundamentals.md)
  - [02 Cyclical Agent Patterns](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/02%20Cyclical%20Agent%20Patterns.md)
  - [03 Memory and Persistence](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/03%20Memory%20and%20Persistence.md)
  - [04 Supervisor-Worker Multi-Agent](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/04%20Supervisor-Worker%20Multi-Agent.md)
  - [05 Advanced LangGraph Patterns](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/05%20Advanced%20LangGraph%20Patterns.md)
  - [06 Milestone - Multi-Agent Enterprise Assistant](Module%203.1%20-%20LangGraph%20and%20Stateful%20Orchestration/06%20Milestone%20-%20Multi-Agent%20Enterprise%20Assistant.md)
- **Module 3.2 — The 2026 Agent Framework Landscape** — what else exists and when to pick it. ✅
  - [01 Framework Decision Matrix](Module%203.2%20-%20Agent%20Framework%20Landscape/01%20Framework%20Decision%20Matrix.md)
  - [02 CrewAI Crews and Flows](Module%203.2%20-%20Agent%20Framework%20Landscape/02%20CrewAI%20Crews%20and%20Flows.md)
  - [03 Semantic Kernel and Microsoft Agent Framework](Module%203.2%20-%20Agent%20Framework%20Landscape/03%20Semantic%20Kernel%20and%20Microsoft%20Agent%20Framework.md)
  - [04 OpenAI Agents SDK](Module%203.2%20-%20Agent%20Framework%20Landscape/04%20OpenAI%20Agents%20SDK.md)
- **Module 3.3 — Tool Definition & Function Calling** — how agents *act* on the world. ✅
  - [01 JSON Schema Tool Contracts](Module%203.3%20-%20Tools%20and%20Function%20Calling/01%20JSON%20Schema%20Tool%20Contracts.md)
  - [02 LangChain Tool Patterns](Module%203.3%20-%20Tools%20and%20Function%20Calling/02%20LangChain%20Tool%20Patterns.md)
  - [03 Practical Tool Implementations](Module%203.3%20-%20Tools%20and%20Function%20Calling/03%20Practical%20Tool%20Implementations.md)
- **Module 3.4 — Model Context Protocol (MCP)** — the standard way to plug data/tools into any agent. ✅
  - [01 MCP Architecture](Module%203.4%20-%20Model%20Context%20Protocol/01%20MCP%20Architecture.md)
  - [02 Building MCP Servers](Module%203.4%20-%20Model%20Context%20Protocol/02%20Building%20MCP%20Servers.md)
  - [03 Enterprise MCP Integrations and Security](Module%203.4%20-%20Model%20Context%20Protocol/03%20Enterprise%20MCP%20Integrations%20and%20Security.md)
  - [04 MCP Multi-Agent and A2A](Module%203.4%20-%20Model%20Context%20Protocol/04%20MCP%20Multi-Agent%20and%20A2A.md)
  - [05 Milestone - MCP Server and LangGraph Agent](Module%203.4%20-%20Model%20Context%20Protocol/05%20Milestone%20-%20MCP%20Server%20and%20LangGraph%20Agent.md)
- **Module 3.5 — Sandboxed Execution & Governance** — running agent actions safely, with human gates. ✅
  - [01 Sandboxed Code Execution](Module%203.5%20-%20Sandboxed%20Execution%20and%20Governance/01%20Sandboxed%20Code%20Execution.md)
  - [02 Human-in-the-Loop Design](Module%203.5%20-%20Sandboxed%20Execution%20and%20Governance/02%20Human-in-the-Loop%20Design.md)
- **Module 3.6 — Workflow Automation Context (n8n)** — the low-code alternative, for awareness. ✅
  - [01 n8n for AI Workflow Orchestration](Module%203.6%20-%20Workflow%20Automation%20Context/01%20n8n%20for%20AI%20Workflow%20Orchestration.md)

> New terms are defined the first time they appear and collected in the root
> [AI Terms — Plain-English Glossary](../AI%20Terms%20-%20Plain%20English%20Glossary.md).

---

## ✅ Status

**Complete** — all 6 modules (22 lessons) built research-first to the Phase 2 reference-grade bar; all
files verified 0 corrupted characters. Next on the Road Map: Phase 4 (LLMOps, Eval, Security, Production).
