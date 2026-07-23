# 03 — Jailbreak, Adversarial & RAG Security

> Phase 4 · Module 4.3 · Lesson 3 · `[ARCHITECT BONUS — 🟡 SHOULD; red-team + multi-tenant RAG]`

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Beyond injection: users **jailbreak** (coax unsafe output), and multi-tenant RAG
can **leak** one tenant's docs to another. Architects red-team their own system and lock down retrieval.

## 🔑 New Terms
**Jailbreak** · **Azure Content Safety** (`analyze_text` hate/violence/self-harm) · **garak** (LLM vuln
scanner) · **doc-level access control** (metadata filter) · **tenant isolation** · **EU AI Act**. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: hire pentesters (red-team) + give each tenant keys to only their vault (metadata filter). **Aha!:** attack yourself first; isolate data hard.

## ⚙️ Stage 2 — defences (each a mini-reference)
- **Azure Content Safety** — `analyze_text()` classifies hate/violence/self-harm. **✅ Use when:** moderate
  user input and model output. **⚠️ Gotcha:** a classifier, not a full fence — layer it.
- **Output validation** — check responses stay within allowed topics before returning. **✅:** restricted
  domains. **⚠️:** keep the allow-list current.
- **garak** — an LLM vulnerability scanner; red-team your own system. **✅:** awareness-level probing. **⚠️:** awareness, not a fix.
- **RAG isolation** — filter retrieval by tenant/ACL **before** searching, so an agent only sees its
  tenant's chunks. **✅ Use when:** multi-tenant RAG. **🚫 Avoid:** filtering *after* retrieval (too late).
  **⚠️:** poisoned docs are indirect injection (4.3.01); EU AI Act needs risk-class + technical docs.

> 🔬 Multi-tenant leakage is the headline risk: a pre-retrieval metadata filter is the hard boundary.

## 🚀 Stage 3 — In Practice / Why It Matters
Two architect-level risks live here. **Jailbreaks** coax the model past its safety rules (role-play, "DAN,"
encoded payloads) — you defend by moderating input *and* output and red-teaming yourself with a scanner like
**garak** before attackers do. The bigger production landmine is **multi-tenant RAG leakage**: if tenant A's
query can retrieve tenant B's chunks, you have a data breach. The hard boundary is a **pre-retrieval metadata
filter** on tenant/ACL — the search never even sees other tenants' data. Regulated systems add **EU AI Act**
risk-classification + technical documentation.

## ⚖️ Variations & When to Use
| The need is… | Use | Why |
|---|---|---|
| Moderate harmful in/out | **Azure Content Safety** | hate/violence/self-harm classifier |
| Find your own vulnerabilities | **garak** (red-team) | adversarial scanner, awareness-level |
| Stop cross-tenant data leaks | **pre-retrieval ACL filter** | hard boundary before search runs |
| Restrict to allowed topics | **output validation** | keeps responses in-domain |
| Regulated deployment | **EU AI Act docs** | risk class + technical documentation |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Tenant A sees tenant B's docs | no tenant filter | **metadata filter before retrieval** (tenant ID) + audit |
| Poisoned KB content obeyed | trusting the knowledge base | screen chunks (4.3.01); treat docs as untrusted |
| Unsafe output slips out | only input moderated | moderate **output** too (Content Safety) |
| Found vulnerable in prod | never red-teamed | probe with **garak** pre-launch |

## 📌 Quick Reference
- **Jailbreak defence:** moderate input **and** output (Content Safety) + red-team with **garak**.
- **Multi-tenant RAG:** a **pre-retrieval metadata/ACL filter** is the non-negotiable boundary; add audit logging.
- Poisoned docs = indirect injection (4.3.01). Regulated → EU AI Act risk class + technical docs.

## 🛑 STOP — Self-Check
A multi-tenant RAG app must never let one customer's query surface another customer's documents. What's the
single most important control?

<details><summary>Answer</summary>

A **metadata access filter applied *before* retrieval** — every search is scoped by the caller's **tenant ID /
ACL**, so the vector search only ever sees that tenant's chunks. Filtering *after* retrieval is too late (the
data was already fetched). Pair it with **audit logging** of who retrieved what.
</details>

⏭️ **Next:** Module 4.4 — Semantic Caching.
