# 02 — Plan, Create & Deploy a Foundry Service

> Phase 5 · Module 5.1 · Lesson 2 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Plan & Manage (20–25%)**
> *Provisioning a resource, deploying a model, and shipping it through CI/CD are the day-one mechanics in every
> Azure AI job — and a reliable source of exam marks.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** You've picked the service (Lesson 01). Now you have to *stand it up*: plan for
Responsible AI, create the resource, **deploy a model**, call it from code, and make it repeatable through a
pipeline — sometimes inside a **container** for edge or compliance. Skip the planning and you bolt on safety
later (expensive); skip CI/CD and every deploy is a risky manual click. The exam tests each of these steps.
*(Cost, keys, auth, and monitoring are the "run it safely" half — they're Lesson 03.)*

**Why care:** "plan, create and deploy a Foundry service" is an explicit exam objective and the literal first
hour of any Azure AI project.

## 🔑 New Terms (plain English)
- **Resource** — the Azure thing you create that gives you an **endpoint** (a URL) + access to models.
- **Deployment** — a specific model (e.g. GPT-4o) made callable under a name you choose.
- **Default endpoint** — the base URL your SDK/REST calls hit for that resource.
- **SDK vs REST** — a language library (Python/C#) vs raw HTTP calls; both reach the same endpoint.
- **CI/CD** — automated build/test/deploy pipeline (e.g. GitHub Actions) using infrastructure-as-code.
- **Container deployment** — running a service in a Docker container on-prem/edge instead of the cloud.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: opening a shop)
**Plan for Responsible AI** = the safety inspection before you open. **Create the resource** = rent the unit
and get the address (endpoint). **Deploy a model** = stock the product on the shelf. **SDK/REST** = the way
customers order. **CI/CD** = a standard opening checklist so every new branch opens identically. **Container**
= a pop-up stall you can set up *anywhere*, including off-grid. **Aha!:** the service is plumbing — you choose
which model to stock, where the door is, and how repeatably you open.

## ⚙️ Stage 2 — How It Works (the steps, each with when-to-use)

#### Plan for Responsible AI first
- **What & why:** decide content-safety, fairness, and governance needs *before* building, so they're designed
  in, not patched on. **✅ Always.** **⚠️ Gotcha:** retrofitting safety after launch is costly and risky (full controls in Lesson 04).

#### Create an Azure AI / Foundry resource (single vs multi-service — a real choice)
- **Single-service resource** — one key/endpoint for one service. **✅ Use when:** you want isolated billing
  per service. **Multi-service resource** — one key for many services. **✅ Use when:** you want one bill/key
  across Vision+Language+Speech. **⚠️:** note region availability and quota when you create it.

#### Choose & deploy the right model
- **What & why:** pick a model from the catalogue (GPT-4o, GPT-4.1, Phi, Llama…) and create a **named
  deployment**. **✅ Use when:** matching capability vs cost to the task. **🚫 Avoid → biggest model by default:**
  right-size it (cost). **⚠️:** the deployment *name* (not the model name) is what your code calls.

#### Install & use the SDK / REST API; find the default endpoint
- **What & why:** call the deployment from your app via the SDK or REST; the resource exposes a **default
  endpoint** + auth. **✅ SDK** for app code (typed, retries); **✅ REST** for quick tests/other languages. **⚠️:** match SDK version to the API version.

#### Integrate into a CI/CD pipeline
- **What & why:** define the resource + deployment as **infrastructure-as-code** (Bicep/Terraform) and deploy
  through a pipeline so environments are identical and repeatable. **✅ Use when:** anything beyond a one-off
  demo. **⚠️:** keep secrets out of the pipeline (use identity/Key Vault — Lesson 03).

#### Plan & implement a container deployment
- **What & why:** some Azure AI services ship as **Docker containers** you run on-prem/edge. **✅ Use when:**
  data can't leave your network (compliance) or you need low-latency/offline. **🚫 Avoid → cloud endpoint:**
  when the cloud is fine (simpler). **⚠️:** containers still need a billing connection back to Azure.

> 🔬 **Under the hood:** creating a resource provisions an **endpoint + auth** behind Azure's control plane.
> A **deployment** maps your chosen name to a model+version+capacity. Your SDK call = `POST {endpoint}/...`
> with the deployment name + an auth token. CI/CD just scripts the same `az`/Bicep steps you'd click in the portal.

### 💻 In code (Azure CLI)
```bash
# Create a MULTI-service resource (one key/endpoint for many services)
az cognitiveservices account create \
  --name myai --resource-group rg --kind AIServices \
  --sku S0 --location eastus

# Find the DEFAULT endpoint and keys
az cognitiveservices account show --name myai -g rg --query properties.endpoint
az cognitiveservices account keys list --name myai -g rg
```
Single-service kinds use `--kind ComputerVision | TextAnalytics | SpeechServices | FormRecognizer | OpenAI`.
For Azure OpenAI you then create a **model deployment** and call it by its **deployment name**.
> In production, define all of this as **Bicep/ARM/Terraform** and ship via CI/CD so every environment is identical.

### 📦 Provisioning quick reference
| Thing | Value |
|---|---|
| Multi-service kind | **`AIServices`** (one key/endpoint for many) |
| Single-service kinds | `ComputerVision` · `TextAnalytics` · `SpeechServices` · `FormRecognizer` · `OpenAI` |
| Default endpoint | `https://<name>.cognitiveservices.azure.com/` (OpenAI: `<name>.openai.azure.com`) |
| Your code calls | the **deployment name** (not the base model name) |
| Repeatable deploy | Bicep / ARM / Terraform via CI/CD |
| Container modes | **connected** (bills online) · **disconnected** (offline, special licensing) |

### 🎯 Exam facts to memorise
- **`AIServices` = multi-service** (one key/endpoint across Vision/Language/Speech…); single-service kinds isolate billing.
- The **default endpoint** is `https://<name>.cognitiveservices.azure.com/` (Azure OpenAI uses `<name>.openai.azure.com`).
- Your app calls the **deployment name** you chose, not the model name (a 404 = wrong name).
- **Containers:** **connected** still bills to Azure; **disconnected** runs offline under special licensing — both need a billing/EULA link.
- **CI/CD** = infrastructure-as-code (Bicep/ARM/Terraform); keep secrets in **Key Vault**, not the pipeline.
- Plan **Responsible AI** before building, not after.

## 🚀 Stage 3 — In Practice / Why It Matters
A real setup: plan Responsible AI → create a (often multi-service) Foundry resource via Bicep → deploy a
right-sized model → call it from the SDK using the default endpoint → wire it all into a GitHub Actions
pipeline → and, for a regulated client, run the service in a **container** inside their network. That
repeatable, safety-first path is exactly what "plan, create and deploy" means on the exam and on the job.

## ⚖️ Variations & When to Use
| Decision | Options | Pick |
|---|---|---|
| Resource type | single- vs multi-service | isolated billing → single · one key for many → multi |
| Calling style | SDK vs REST | app code → SDK · quick test/other lang → REST |
| Where it runs | cloud endpoint vs container | default → cloud · compliance/edge/offline → container |
| Model choice | frontier vs small | match capability to task; right-size for cost |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| 404 / model not found | calling the *model* name, not the *deployment* name | use your deployment name |
| Safety bolted on late | no Responsible-AI planning | plan content safety up front (Lesson 04) |
| "Works on my machine" deploys | manual portal clicks | infrastructure-as-code + CI/CD |
| Data-residency blocker | cloud-only deployment | run the service in a **container** on-prem |

## 📌 Quick Reference
- **Order:** plan Responsible AI → create resource (single/multi) → deploy a right-sized model → call via
  SDK/REST on the **default endpoint** → automate with CI/CD → container for edge/compliance.
- Your code calls the **deployment name**, not the model name.

## 🎯 Exam-style practice
**Q1.** One team wants a single key/endpoint covering Vision + Language + Speech. Which resource kind?
<details><summary>Answer</summary>A **multi-service** resource, `--kind AIServices`.</details>

**Q2.** Code gets 404 calling a deployed GPT-4o model. Most likely cause?
<details><summary>Answer</summary>It's calling the **base model name** instead of the **deployment name** you created.</details>

**Q3.** Data may not leave the network and the app must run with no internet. Which container mode?
<details><summary>Answer</summary>A **disconnected** container (offline, special licensing) — vs a **connected** container that still bills online.</details>

## 🛑 STOP — Self-Check
A bank wants an Azure OpenAI model, but its data **must not leave the bank's network**, and it wants every
environment built identically. Which **two** deployment choices address these?

<details><summary>Answer</summary>

1. **Container deployment** — run the service in a Docker container **inside the bank's network**, so data
   stays on-prem (compliance). (It still keeps a billing link to Azure.)
2. **CI/CD with infrastructure-as-code** — define the resource + deployment in Bicep/Terraform and ship via a
   pipeline so dev/test/prod are **identical and repeatable**, not hand-clicked.

(Plus: plan Responsible AI up front, and right-size the model for cost.)
</details>

⏭️ **Next:** 03 — Manage, Monitor & Secure a Foundry service.
