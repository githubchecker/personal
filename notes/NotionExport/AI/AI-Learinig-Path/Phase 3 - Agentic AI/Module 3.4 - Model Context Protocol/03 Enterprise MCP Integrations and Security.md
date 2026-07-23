# 03 — Enterprise MCP Integrations & Security

> Phase 3 · Module 3.4 · Lesson 3 · `[JD VERIFIED — 🟡 SHOULD; Postgres/Blob/SharePoint + secure handlers]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** A demo MCP server is open and trusts every caller. An *enterprise* one exposes
Postgres, Azure Blob, SharePoint — so it must **authenticate**, **authorise**, and **validate** every
call, or you've handed agents a master key. This lesson: common enterprise servers + securing them.

**Why care:** enterprises want their data agent-accessible *safely*; secure MCP is the SHOULD bar.

## 🔑 New Terms
PostgreSQL/Blob/SharePoint MCP server · **TokenVerifier** (OAuth 2.1 RS) · authorisation · input validation.
([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a vault clerk checks ID, scope, and your slip before fetching. MCP server = clerk: auth + authz + validate. **Aha!:** every handler is a trust boundary.

## ⚙️ Stage 2 — common servers + securing them
**The three enterprise servers**, each a mini-reference:
- **PostgreSQL server** — exposes a business database for natural-language queries. **✅ Use when:** agents
  answer data questions. **⚠️ Gotcha:** read-only role + parameterised queries, never raw writes.
- **Azure Blob server** — exposes a document store. **✅:** doc Q&A. **⚠️:** scope to one container, not the account.
- **SharePoint / Microsoft Graph server** — enterprise files. **✅:** internal knowledge. **⚠️:** honour Azure AD scopes.

**Securing it (every handler is a trust boundary):**
```python
mcp = FastMCP("svc", token_verifier=Verifier(), auth=AuthSettings(required_scopes=["user"]))  # OAuth 2.1
```
Authenticate every caller (OAuth 2.1 `TokenVerifier`), require **scopes**, **validate inputs** in every
tool/resource handler, and run with **least-privilege** credentials. An open MCP server over prod data is a
master key handed to any agent.

> 🔬 The MCP server is an OAuth Resource Server; an Authorization Server issues tokens; each handler checks them.

## 🚀 Stage 3 — In Practice / Why It Matters
This is where MCP meets the enterprise security review. The same three servers — Postgres, Blob, SharePoint —
that make your data agent-accessible become a **master key** if exposed without controls. Every production MCP
server is an **OAuth 2.1 Resource Server**: it authenticates each caller with a `TokenVerifier`, requires
**scopes**, validates inputs in **every** handler, and runs on **least-privilege** (read-only, single-container,
AD-scoped) credentials. "Make our SharePoint/DB available to agents" is a real JD line — doing it *securely* is
the part that separates a SHOULD-level engineer.

## ⚖️ Variations & When to Use
| Enterprise server | Exposes | The security control |
|---|---|---|
| **PostgreSQL** | a business database | read-only role + **parameterised** queries (no raw writes) |
| **Azure Blob** | a document store | scope to **one container**, not the whole account |
| **SharePoint / MS Graph** | enterprise files | honour **Azure AD scopes** (don't bypass ACLs) |
| **Every handler** | (the trust boundary) | OAuth 2.1 `TokenVerifier` + **required scopes** + input validation |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Any caller can use the server | no authentication | OAuth 2.1 `TokenVerifier` + `required_scopes` |
| One leak exposes everything | broad credentials | **least-privilege** (read-only, single container/scope) |
| Injection through a handler | unvalidated inputs | validate in **every** tool/resource handler |
| Agent bypasses file permissions | ignoring AD scopes | enforce the user's **Azure AD scopes** |

## 📌 Quick Reference
- **Servers:** Postgres (data) · Blob (docs) · SharePoint/Graph (files).
- **Secure every server:** OAuth 2.1 **`TokenVerifier`** + **required scopes** + **input validation** + **least-privilege** creds.
- The MCP server is an **OAuth Resource Server**; each handler is a **trust boundary** — never anonymous over prod data.

## 🛑 STOP — Self-Check
You're exposing a **production Postgres** database via MCP. What are the first security controls you put in
place before any agent connects?

<details><summary>Answer</summary>

**Authentication + authorisation + least privilege.** Put an OAuth 2.1 **`TokenVerifier`** with **required
scopes** in front of the server so only authorised callers reach it; give the server a **read-only,
parameterised** database role (so even a successful injection can't write); and **validate inputs** in every
handler. Never expose an **anonymous** server with write access over production data — every handler is a
trust boundary.
</details>

⏭️ **Next:** 04 — MCP multi-agent & A2A.
