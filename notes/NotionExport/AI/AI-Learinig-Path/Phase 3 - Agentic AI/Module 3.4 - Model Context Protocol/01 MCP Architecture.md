# 01 — MCP Architecture: Host, Client, Server

> Phase 3 · Module 3.4 · Lesson 1 · `[JD VERIFIED — ~58%, "table stakes" — 200+ servers by 2026]`

> 🔬 **Currency (mid-2026):** MCP Python SDK `1.28.x` (FastMCP). Recommended transport is now **Streamable
> HTTP** (SSE legacy). v2 in alpha — teach v1 now.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Every tool you built in Module 3.3 is glued to *one* framework. Connect 5 agents to
5 data sources and you write 25 bespoke integrations. **MCP (Model Context Protocol)** is the fix: a
**universal standard** for exposing tools/data to *any* agent. Build one MCP server for Postgres and
**every** MCP-aware agent (LangGraph, CrewAI, Claude Desktop) uses it — no custom glue. It's the **USB-C of
AI**: one connector, swappable both ends.

**Why care:** ~58% of JDs and rising; decouples agents from data — a core architecture pattern.

---

## 🔑 New Terms
- **MCP** — open protocol standardising how agents get tools/data. **Host** — the app the user uses
  (Claude Desktop, your agent). **Client** — connector inside the host, one per server. **Server** — exposes
  tools/data. **Transport** — connection: stdio/Streamable-HTTP/SSE. **JSON-RPC 2.0** — message format.
  Primitives: **Tools** (actions, model-controlled) · **Resources** (data, app-controlled) · **Prompts**
  (templates, user-controlled). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea (analogy: USB-C)
Pre-USB-C: a charger per device. USB-C: one port, any device. MCP = USB-C for AI: any agent ↔ any
tool/data via one standard. **Aha!:** standardise the **connector**, not the integration.

## ⚙️ Stage 2 — How It Works
**Shape:** a **host** runs one **client** per **server**; each client speaks a **transport** to its server.
#### stdio transport — local
- **What & why:** the client talks to a server running as a **local process** over stdin/stdout pipes (Claude
  Desktop, dev tooling). **✅ Use when:** the tool runs on the **same machine**. **🚫 Avoid → Streamable HTTP:**
  for anything remote. **⚠️ Gotcha:** same-machine only — it can't reach a networked server.

#### Streamable HTTP transport — remote / production
- **What & why:** the client reaches the server over HTTP (`FastMCP(stateless_http=True, json_response=True)`),
  so it scales across nodes. **✅ Use when:** remote or production servers. **🚫 Avoid → stdio:** for local dev.
  **⚠️:** this is the **recommended default now** (replaces SSE).

#### SSE transport — legacy
- **What & why:** the older Server-Sent-Events remote transport. **✅ Use when:** maintaining existing SSE
  servers. **🚫 Avoid → Streamable HTTP:** for anything new. **⚠️:** superseded — **migrate off it**.

**Three primitives (by who controls them):** **Tools** = actions, *model*-controlled (POST-like) · **Resources**
= data, *app*-controlled (GET-like) · **Prompts** = templates, *user*-controlled. All messages ride **JSON-RPC 2.0**.

> 🔬 **Under the hood:** build one server → every MCP-aware agent (LangGraph/CrewAI/Claude Desktop) reuses it,
> and you can swap either side freely. That's the decoupling: agents and tools agree on a **contract**, not on
> bespoke per-pair glue.

## 🚀 Stage 3 — In Practice / Why It Matters
MCP is what turns "I wired a tool into my agent" into "I built a tool the whole org's agents can use." A team
ships one MCP server for Postgres, one for SharePoint, one for the ticketing system — and every agent
(LangGraph, CrewAI, Claude Desktop) consumes them with no custom code. It collapses the **N×M integration
explosion** (5 agents × 5 sources = 25 bespoke connectors) into **N+M** (5 servers + 5 agents that all speak
MCP). That's why it appears in ~58% of agentic JDs and is treated as table-stakes architecture.

## ⚖️ Variations & When to Use
| Choice | Use when | Avoid when → use instead | Gotcha |
|---|---|---|---|
| **stdio** | local, same-machine tools | remote → **Streamable HTTP** | can't reach a networked server |
| **Streamable HTTP** | remote / production | local dev → **stdio** | the current recommended default |
| **SSE** | legacy servers only | anything new → **Streamable HTTP** | deprecated, migrate off |
| **Tools** primitive | the model should *act* | read-only data → **Resources** | model-controlled |
| **Resources** primitive | expose *data* to read | actions → **Tools** | app-controlled |
| **Prompts** primitive | reusable templates | dynamic actions → **Tools** | user-controlled |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Agent can't reach the server | remote server on **stdio** | use **Streamable HTTP** |
| New server uses deprecated transport | built on **SSE** | use **Streamable HTTP** |
| Re-writing the same integration per agent | bespoke glue | expose it **once** as an MCP server |
| Model "reads" via a Tool, mutates via a Resource | primitives mixed up | Tools = act, Resources = read |

## 📌 Quick Reference
- **Architecture:** **host** runs one **client** per **server**; client ↔ server over a **transport**.
- **Transports:** stdio (local) · **Streamable HTTP** (remote/prod, default) · SSE (legacy).
- **Primitives:** Tools (act, model) · Resources (read, app) · Prompts (template, user). All over **JSON-RPC 2.0**.
- One server → every MCP agent reuses it: **N+M**, not **N×M**.

## 🛑 STOP — Self-Check
You have **5 agents** that each need the **same 5 data sources**. Why does MCP turn 25 integrations into 10,
and what do you build?

<details><summary>Answer</summary>

You build **5 MCP servers** (one per data source). Because every agent speaks the **same MCP contract**, each
agent connects to each server with **no bespoke code** — so the work is **5 servers + 5 MCP-aware agents = 10**,
not **5 × 5 = 25** custom integrations. Either side is swappable: add a 6th agent and it instantly speaks to all
5 servers; replace a server and no agent changes. That decoupling (contract, not glue) is the whole point of MCP.
</details>

⏭️ **Next:** 02 — Building MCP servers (FastMCP).
