# 03 — Manage, Monitor & Secure a Foundry Service

> Phase 5 · Module 5.1 · Lesson 3 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Plan & Manage (20–25%)**
> *Cost, keys, and identity show up in nearly every Azure AI job description and in the exam's biggest domain.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Once a service is live, the questions stop being "how do I call it?" and become "how
much is it costing, who's allowed to use it, and is it healthy?" The exam (and real ops teams) test exactly
these: **monitor**, **manage cost**, **protect keys**, and **manage authentication**. Get these wrong and you
get a surprise bill, a leaked key, or an outage you can't see.

**Why care:** "secure and monitor Azure AI resources" is a core JD line and a fat slice of the 20–25% domain.

## 🔑 New Terms (plain English)
- **Azure Monitor** — Azure's built-in dashboard for metrics (numbers over time) and logs (events).
- **PAYG vs PTU** — pay-as-you-go (per token) vs provisioned throughput units (reserved capacity).
- **Account key** — a secret string that unlocks a service (like a password).
- **Microsoft Entra ID** — Azure's identity system (formerly Azure AD).
- **Managed identity** — an automatic Azure identity for your app, so it never holds a key.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: running a shop after opening)
Opening the shop was Lesson 02. Now you run it: watch the **till** (cost), check the **security cameras**
(monitoring), control the **keys to the door** (auth), and rotate the locks if a key goes missing. **Aha!:**
the service works on day one; *managing* it is what keeps it cheap, safe, and reliable on day 100.

## ⚙️ Stage 2 — How It Works (the four jobs, each with when-to-use)

#### Monitor an Azure AI resource
- **What & why:** Azure Monitor shows call volume, latency, errors, and token usage; set **alerts** on
  thresholds. **✅ Use when:** always in production — you can't fix what you can't see. **⚠️ Gotcha:** turn on
  diagnostic settings to send logs to a Log Analytics workspace, or you only get short-lived metrics.

#### Manage cost (PAYG vs PTU — a real choice)
- **PAYG** — pay per token; **✅ use when:** spiky or low volume. **🚫 Avoid → PTU:** steady high volume where
  reserved capacity is cheaper and gives predictable latency. **⚠️:** set **budgets + alerts** so a runaway
  loop doesn't bankrupt the project; semantic caching (Phase 4.4) cuts spend too.

#### Manage & protect account keys
- **What & why:** services issue **two keys** so you can rotate one while the other stays live. Store them in
  **Azure Key Vault**, never in code. **✅:** when you must use keys (quick integrations). **⚠️ Gotcha:** a key
  in source control is a breach — rotate immediately if leaked.

#### Manage authentication (keys vs Entra ID — the key exam choice)
- **Keys** — simplest; **✅ use when:** dev, prototypes. **🚫 Avoid → Microsoft Entra ID + managed identity:**
  production, because there's **no secret to leak** — the app gets tokens automatically and you control access
  with role assignments (RBAC). **⚠️:** grant least-privilege roles, not Owner.

> 🔬 **Under the hood:** every Foundry service is a REST endpoint behind Azure's auth layer. A managed identity
> asks Entra ID for a short-lived token per call, so credentials never sit in your code or config.

### 💻 The SDK in code (auth — the exam's favourite)
```python
# DEV: key auth (a secret you must protect)
from azure.core.credentials import AzureKeyCredential
client = SomeClient(endpoint, AzureKeyCredential("<key>"))

# PROD: Entra ID + managed identity — NO secret to leak
from azure.identity import DefaultAzureCredential
client = SomeClient(endpoint, DefaultAzureCredential())   # app gets a short-lived token per call
```
`DefaultAzureCredential` tries managed identity / environment / CLI login in turn — same code in dev and prod.

### 📦 Manage & secure quick reference
| Concern | Answer |
|---|---|
| Dev auth | `AzureKeyCredential(key)` (two keys — rotate one while other live) |
| Prod auth | **`DefaultAzureCredential()`** + **managed identity** (no secret) |
| Secrets | **Azure Key Vault** — never in code/source control |
| RBAC | least-privilege role (e.g. **Cognitive Services User**), not Owner |
| Monitoring | Azure Monitor metrics + **diagnostic settings → Log Analytics** |
| Cost | **PAYG** (spiky) vs **PTU** (steady); budgets + alerts; caching |

### 🎯 Exam facts to memorise
- **Dev → keys; prod → Entra ID + managed identity** (`DefaultAzureCredential`) — the single most-tested auth rule.
- Services issue **two keys** so you can **rotate** without downtime; store any key in **Key Vault**, never in code.
- A key in source control = a breach → **rotate immediately**.
- Metrics are short-lived unless you enable **diagnostic settings → Log Analytics**.
- **Cost:** PAYG for spiky/low volume, **PTU** for steady high volume; always set **budgets + alerts**.
- RBAC = **least privilege** (e.g. *Cognitive Services User*), not Owner/Contributor.

## 🚀 Stage 3 — In Practice
A production Azure AI app: **managed identity** for auth, **Key Vault** for any unavoidable secrets, **Azure
Monitor** alerts on errors/latency, and **budgets** with cost alerts — often PTU if traffic is steady. This is
the "operate it safely" half of the architect role.

## ⚖️ Variations & When to Use
| Decision | Pick | Because |
|---|---|---|
| Auth in dev | **keys** | fastest to wire up |
| Auth in prod | **Entra ID + managed identity** | no secret to leak; RBAC control |
| Spiky/low traffic | **PAYG** | pay only for what you use |
| Steady high traffic | **PTU** | cheaper + predictable latency |
| Any secret you must keep | **Key Vault** | central, rotatable, audited |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Surprise bill | no budget/alert | set Azure budget + cost alerts; cache |
| Key leaked in repo | key in code | move to Key Vault; rotate the key |
| Can't see past errors | no diagnostic settings | send logs to Log Analytics |
| 403 from the service | wrong role on the identity | assign the correct least-privilege RBAC role |

## 📌 Quick Reference
- **Monitor:** Azure Monitor + diagnostic settings + alerts.
- **Cost:** PAYG (spiky) vs PTU (steady); budgets + alerts; cache.
- **Keys:** two keys, rotate, store in **Key Vault**, never in code.
- **Auth:** dev → keys; **prod → Entra ID + managed identity** (least-privilege RBAC).

## 🎯 Exam-style practice
**Q1.** A prod app holds an API key in its config. Best-practice fix and exact mechanism?
<details><summary>Answer</summary>Switch to **Entra ID + managed identity** (`DefaultAzureCredential`) — no secret. If a key is unavoidable, put it in **Key Vault** and rotate.</details>

**Q2.** You can't see errors from yesterday, only live metrics. What was missing?
<details><summary>Answer</summary>**Diagnostic settings** sending logs to a **Log Analytics** workspace (metrics alone are short-lived).</details>

**Q3.** Steady 24/7 high traffic, surprise bills. Two cost levers?
<details><summary>Answer</summary>Move to **PTU** (predictable cost/latency) and set **budgets + cost alerts** (plus caching).</details>

## 🛑 STOP — Self-Check
A production app currently authenticates to Azure OpenAI with a key pasted in its config, and finance is
shocked by the monthly bill. Name the **two** fixes and the exact services.

<details><summary>Answer</summary>

1. **Authentication:** replace the key with **Microsoft Entra ID + a managed identity** (least-privilege RBAC)
   — no secret to leak. If a key is truly unavoidable, store it in **Azure Key Vault** and rotate it.
2. **Cost:** set an **Azure budget with cost alerts**, consider **PTU** if traffic is steady, and add
   **semantic caching** (Phase 4.4) to cut repeat spend. Use **Azure Monitor** to watch usage going forward.
</details>

⏭️ **Next:** 04 — Responsible AI & Content Safety.
