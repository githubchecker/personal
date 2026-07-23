# 04 — MCP in Multi-Agent Systems & the A2A Protocol

> Phase 3 · Module 3.4 · Lesson 4 · `[ARCHITECT BONUS — 🟡 awareness; gateways, A2A]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** MCP connects an agent to **tools/data**. But how do *agents from different vendors*
talk to **each other**? That's **A2A (Agent-to-Agent)** — complementary to MCP. And with many servers, you
add a **gateway** so agents see one endpoint. Architect awareness: know MCP-vs-A2A and the gateway pattern.

**Why care:** "decouple data layers; let agents collaborate" — architecture-design questions.

## 🔑 New Terms
**A2A** — vendor-neutral agent↔agent protocol (ACP merged into A2A, Linux Foundation 2026). **MCP gateway**
— one proxy routing to many servers. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: MCP = staff↔tools; A2A = staff↔staff; gateway = front desk routing to back rooms. **Aha!:** MCP = agent→tool; A2A = agent→agent.

## ⚙️ Stage 2 — gateways, portability, and A2A
- **MCP gateway** — a single proxy that routes to many backend servers, so agents see one endpoint. **✅ Use
  when:** several servers behind one door, swappable. **🚫 Avoid → direct:** a single server. **⚠️ Gotcha:**
  the gateway is a single point of failure — run it highly-available.
- **Framework-agnostic** — LangGraph, CrewAI, Semantic Kernel, and the OpenAI SDK all speak MCP, so a server
  built once works with all of them.
- **A2A (Agent-to-Agent)** — a vendor-neutral protocol for agents to collaborate *with each other* (ACP
  merged into A2A under the Linux Foundation, 2026). **✅ Use when:** agents from different vendors must
  cooperate. **🚫 Avoid → MCP:** for plain tool/data access. **⚠️:** still maturing — track, don't bet the farm.
- **MCP vs A2A:** MCP is agent→tool/data; A2A is agent→agent. Complementary, not competing.

> 🔬 Both use JSON-RPC-style messaging; MCP standardises tool access, A2A standardises agent collaboration.

## 🚀 Stage 3 — In Practice / Why It Matters
As agent systems grow, two scaling questions appear — and they're common architecture-interview territory.
First, **many MCP servers** behind one **gateway** so agents hit a single endpoint (and you can swap backends).
Second, **agents from different vendors collaborating** — that's **A2A**, complementary to MCP. The clean mental
model: **MCP is agent→tool/data; A2A is agent→agent.** You'll often run both — MCP for the tools each agent
uses, A2A for those agents to coordinate.

## ⚖️ Variations & When to Use
| The connection is… | Use | Avoid when → use instead | Gotcha |
|---|---|---|---|
| Agent → tool / data | **MCP** | agent-to-agent → **A2A** | model-to-tool contract |
| Agent → another agent | **A2A** | tool/data access → **MCP** | still maturing — track it |
| Many servers, one door | **MCP gateway** | a single server → direct | gateway is a SPOF — run it HA |
| Mixed frameworks | any (all speak MCP) | — | a server built once works across LangGraph/CrewAI/SK/OpenAI |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Wrong protocol chosen | MCP vs A2A confusion | tool/data → MCP; agent↔agent → A2A |
| Gateway outage takes everything down | single gateway instance | run the gateway **highly available** |
| Locked to one framework | bespoke integration | expose via MCP — every framework speaks it |

## 📌 Quick Reference
- **MCP** = agent→tool/data · **A2A** = agent→agent (ACP merged into A2A, Linux Foundation 2026).
- **Gateway** = one proxy → many servers (run HA). Servers are **framework-agnostic**. Both use JSON-RPC-style messaging.

## 🛑 STOP — Self-Check
Which protocol: an agent reading from **Postgres**? An agent coordinating with **another vendor's agent**?

<details><summary>Answer</summary>

**Postgres → MCP** (agent-to-tool/data access). **Another vendor's agent → A2A** (agent-to-agent peer
collaboration). They're **complementary**, not competing — a real system uses MCP for each agent's tools and
A2A for the agents to talk to each other.
</details>

⏭️ **Next:** 05 — 🏁 Milestone.
