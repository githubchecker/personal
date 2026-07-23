# 03 — Practical Tool Implementations (SQL, REST, Files, Code)

> Phase 3 · Module 3.3 · Lesson 3 · `[JD VERIFIED — 🟡 SHOULD; the real tools enterprises build]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Demo tools return strings. Real tools touch databases, APIs, files, and run code —
where a careless tool becomes a **security hole** (an agent that runs *any* SQL or reads *any* file). This
lesson builds the four staples **safely**. Security is the lesson — agent tools are an OWASP attack surface.

**Why care:** these four cover most enterprise agent work; building them *securely* is the architect bar.

---

## 🔑 New Terms
SQL tool · REST tool · filesystem tool · code-exec tool · **parameterised query** · **path validation** ·
**sandbox**. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea (analogy: keys with limits)
Give a contractor keys to *one* room, not the building. Each tool = a scoped key: SQL read-only, files in
one folder, code in a sandbox. **Aha!:** capability + **constraint** — the constraint is the design.

---

## ⚙️ Stage 2 — Four tools, each a mini-reference (security-first)

#### SQL tool — natural language → query
- **What & why:** the agent turns a question into SQL against your schema and explains the result.
- **✅ Use when:** read-only data questions over a known schema. **🚫 Avoid → REST/SDK tool:** for writes or
  third-party systems. **⚠️ Gotcha — the big one:** **never** build SQL by f-stringing user text (injection);
  parameterise, use a **read-only** DB role, and allow-list tables.
```python
cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))   # parameterised — never f-string
```
#### REST tool — authenticated HTTP
- **What & why:** call an outside API with auth, timeout, and retry/backoff (Phase 1). **✅:** services with
  no SDK. **🚫 → official SDK:** when one exists. **⚠️:** keep secrets in env vars; validate the URL to
  prevent **SSRF** (agent tricked into hitting internal IPs).
#### Filesystem tool — scoped read/write
- **What & why:** read/write files for a task. **✅:** doc processing. **🚫 → database:** for records. **⚠️:**
  **validate the path** and confine to one root, or `../` traversal lets it read `/etc/passwd`.
#### Code-execution tool — run generated code
- **What & why:** let the model run Python for analysis. **✅:** data/report agents. **🚫 → fixed tools:**
  simple tasks. **⚠️:** **sandbox only** (E2B/Docker, Module 3.5); never `exec()` model code in-process.

> 🔬 Every tool runs with *your* program's privileges — so least-privilege creds, input validation, and
> sandboxing aren't extras, they're the design.

## 🚀 Stage 3 — In Practice / Why It Matters
These four tools — SQL, REST, filesystem, code — cover most enterprise agent work, and **every one is an attack
surface**. The architect's question isn't "can the agent query the DB?" but "can a *malicious prompt* make it
drop a table, read `/etc/passwd`, hit an internal IP, or run arbitrary code?" The answer is the same pattern
each time: **capability + constraint** — least-privilege credentials, validation at the boundary, and a sandbox
for anything that executes. Agent tools are an OWASP attack surface, so secure-by-construction is the bar.

## ⚖️ Variations & When to Use
| Tool | Use when | The security control (non-negotiable) |
|---|---|---|
| **SQL** | read-only questions over a known schema | **parameterised** queries + read-only role + table allow-list |
| **REST** | call an external service (no SDK) | timeout + retry/backoff + **URL validation (anti-SSRF)** + env secrets |
| **Filesystem** | read/write task files | **path validation**, confined to one root (block `../`) |
| **Code exec** | data analysis / report generation | **sandbox only** (E2B/Docker) — never `exec()` in-process |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Agent drops/exfiltrates data | SQL built by f-stringing user text | **parameterise**; read-only role; allow-list tables |
| Agent reads `/etc/passwd` | unvalidated file path (`../` traversal) | validate + confine to one root |
| Agent hits internal IPs | unvalidated REST URL (SSRF) | allow-list hosts; block private ranges |
| Host compromised by generated code | `exec()` in your process | run in a **sandbox** (Module 3.5) |

## 📌 Quick Reference
- **SQL** → parameterise + read-only + allow-list. **REST** → timeout + retry + URL allow-list + env secrets.
- **Files** → validate path, one root. **Code** → sandbox (E2B/Docker), never in-process `exec()`.
- The rule for all four: **least privilege + validate at the boundary**. Capability is easy; the **constraint is the design**.

## 🛑 STOP — Self-Check
Your SQL tool builds queries by inserting the user's text straight into the query string. What's the
vulnerability, and what are the three fixes?

<details><summary>Answer</summary>

It's **SQL injection** — a crafted prompt can make the agent drop tables or exfiltrate data. Three fixes:
(1) **parameterised queries** (bind values, never f-string user text), (2) a **read-only database role** so
even a successful injection can't write, and (3) a **table allow-list** so it can only touch intended data.
Validate at the boundary — capability plus constraint.
</details>

⏭️ **Next:** Module 3.4 — Model Context Protocol (MCP).
