# 05 — 🏁 Milestone: MCP Server + LangGraph Agent

> Phase 3 · Module 3.4 · Lesson 5 · `[MILESTONE — decoupling demonstrated]`

> Project brief tying Module 3.4 together: build an MCP server exposing **PostgreSQL** and **Azure Blob
> Storage**, connect a **LangGraph agent** to it, and answer questions over docs + data with **no direct
> coupling** between agent and data.

---

## 🎯 Goal
A LangGraph agent reads documents (Blob) and queries data (Postgres) **only via MCP** — swap data sources
without touching agent code.

## 🧱 Build steps
1. **MCP server** *(3.4.02)* — FastMCP with a Postgres **tool** (NL→SQL) + a Blob **resource** (docs).
2. **Secure it** *(3.4.03)* — read-only DB role, parameterised queries, auth + scopes, validate handlers.
3. **Streamable HTTP** *(3.4.01)* — run remote (`stateless_http=True, json_response=True`).
4. **Connect LangGraph** *(3.1)* — load MCP tools, bind to a `create_react_agent`.
5. **Demonstrate decoupling** — swap Blob→S3 server: agent code unchanged.

## ✅ Done when
- [ ] Agent answers a doc question (Blob) and a data question (Postgres) via MCP.
- [ ] Multi-hop ("find policy, check status") uses both.
- [ ] DB is read-only + parameterised; server authenticated.
- [ ] Swapping a backend needs **no** agent change.

## 🚀 Stretch
HITL gate before writes (3.5) · multiple servers behind a gateway (3.4.04) · LangSmith tracing (Phase 4).

## 🧠 Proves
You can build the **decoupled data layer** ~58% of JDs want: agents and data swappable via MCP.

⏭️ **Next:** Module 3.5 — Sandboxed Execution & Governance.
