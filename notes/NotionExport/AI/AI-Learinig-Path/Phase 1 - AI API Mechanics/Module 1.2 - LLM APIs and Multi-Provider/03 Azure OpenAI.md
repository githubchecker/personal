# 03 — Azure OpenAI

> Phase 1 · Module 1.2 · Lesson 3 · `[JD VERIFIED — 85%]`

## 🗺️ Stage 0 — Concept Map

Enterprises rarely call `api.openai.com` directly — for **compliance, data residency** (keeping data
in a chosen country/region), **and security** they use **Azure OpenAI**: the *same* OpenAI models,
hosted inside Microsoft Azure. It's in ~85% of enterprise AI JDs. The code is almost identical to lesson 01 — only the **client** and **auth** change.
(Phase 5 / AI-102 goes deep; this is the working knowledge.)

> 🔑 This is the same SDK as lesson 01 — `pip install openai` — just a different client class.

## 🔑 New Terms (plain English)

- **Azure OpenAI** — OpenAI models served through your company's Azure subscription.
- **Deployment** — *your* named instance of a model in Azure (e.g. you deploy `gpt-4o` as
  `my-gpt4o`); you call the **deployment name**, not the raw model name.
- **`api_version`** — Azure's dated API version string, required on every call.
- **`azure_endpoint`** — your private Azure resource URL (`https://<name>.openai.azure.com`).
- **Entra ID** — Microsoft's identity system (formerly Azure AD); lets you authenticate with a
  **managed identity** instead of an API key.
- **`AsyncAzureOpenAI`** — the async Azure client (for `await` inside FastAPI).
- **Content filter** — Azure's built-in moderation that can block prompts/outputs by category & severity.
- **Azure AI Foundry** — Azure's portal for deploying and managing models.
- **Private endpoint / VNet** — keep Azure OpenAI traffic on your private network (off the public internet).

## 🎈 Stage 1 — The Simple Idea (analogy: hiring the expert through corporate HR)

Lesson 01 was phoning the expert directly. **Azure OpenAI** is reaching the *same expert* but **through
your company's HR department** for compliance: you dial an **internal extension** (your deployment
name) instead of the public number, and you **badge in with your corporate ID** (Entra ID managed
identity) instead of a personal key. Same expert, corporate wrapper.

**The "Aha!":** Azure OpenAI = OpenAI models + enterprise governance. Your call code barely changes;
**what changes is the client object and how you authenticate**.

**💢 The old/painful way** — every team wiring raw OpenAI keys into apps with no central governance,
no data-residency guarantee, and secrets sprinkled through configs. Azure OpenAI wraps the *same*
models in enterprise identity, networking, and compliance.

## ⚙️ Stage 2 — How It Actually Works

### 3.1 The Azure client (key difference: `AzureOpenAI` + deployment name)

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],   # https://<resource>.openai.azure.com
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-10-21",                             # required dated version
)

completion = client.chat.completions.create(
    model="my-gpt4o-deployment",     # <- the DEPLOYMENT name you created in Azure, NOT "gpt-4o"
    messages=[{"role": "user", "content": "Explain Azure OpenAI in one sentence."}],
)
print(completion.choices[0].message.content)
```

The interface (`chat.completions.create`, `messages`, response shape) is **identical to lesson 01** —
only `AzureOpenAI`, `api_version`, `azure_endpoint`, and **`model = deployment name`** differ. For
FastAPI, use the async client — **`AsyncAzureOpenAI`** — exactly like `AsyncOpenAI`:

```python
from openai import AsyncAzureOpenAI
client = AsyncAzureOpenAI(azure_endpoint=..., api_key=..., api_version="2024-10-21")
resp = await client.chat.completions.create(model="my-gpt4o-deployment", messages=[...])
```

### 3.2 Enterprise auth: Entra ID instead of a key (the preferred way)

Hardcoding keys is discouraged in enterprises. Instead, authenticate with a **managed identity** (an
identity Azure manages for your app, so there's no key in code or config):

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,   # <- identity-based auth, no API key
    api_version="2024-10-21",
)
```

`DefaultAzureCredential` tries several sources in order (env vars → managed identity → your `az login`),
so the **same code** works locally and in production. This is a big reason enterprises pick Azure:
**keyless** access with full audit trails.

**Auth — Entra ID managed identity vs API key (pick one):**
- **Entra ID managed identity** (preferred)
  - **✅ Use when:** production — keyless, audited, and the *same* code runs locally and in the cloud.
  - **🚫 Avoid when → use a key:** a quick local experiment where setting up identity is overkill.
  - **⚠️ Gotcha:** the identity needs the right **RBAC** role on the resource, or it works locally but `401`s in the cloud.
- **API key**
  - **✅ Use when:** quick local dev or a throwaway script.
  - **🚫 Avoid when → use managed identity:** production — keys leak, must be rotated, and lack per-identity audit.
  - **⚠️ Gotcha:** a key in env/config is a secret you must protect and rotate.

### 3.3 Content filters & moderation (Azure-specific)

Azure OpenAI runs **content filters** on prompts *and* responses (hate, sexual, violence, self-harm).
A fully blocked request raises a `BadRequestError` (400) with `code == "content_filter"`; a partially
filtered response carries `finish_reason == "content_filter"`. Handle it like any provider error
(Module 1.1 lesson 03):

```python
import openai
try:
    resp = client.chat.completions.create(model="my-gpt4o-deployment", messages=[...])
except openai.BadRequestError as e:
    if "content_filter" in str(e):
        ...   # show a polite "can't help with that" message
```

Enterprises can tune severity thresholds and add **custom blocklists** in the portal — something the
public API doesn't expose.

### 3.4 Deployments & Azure AI Foundry (awareness)

In Azure you first **deploy** a model (in the portal / **Azure AI Foundry**) under a name you choose,
then call that **deployment name**. One resource can host several deployments (e.g. `gpt-4o`,
`text-embedding-3-large`). `api_version` pins the request/response shape — keep it current.

### 3.5 Why enterprises use it

Data stays in **your** Azure tenant (your organisation's Azure account) and region (residency &
compliance), integrates with **VNets** and **private endpoints** (traffic never touches the public
internet), **RBAC** (role-based access control — who may call which deployment), and **managed
identity** (no keys), and bills through your existing Azure contract. The model quality is the same as
OpenAI's — sometimes a release or two behind.

**Provider — Azure OpenAI vs direct OpenAI (the core choice):**
- **Azure OpenAI**
  - **✅ Use when:** enterprise compliance, data residency, private networking (VNet), keyless identity, or billing through Azure.
  - **🚫 Avoid when → use direct OpenAI:** you want the newest models on day one, or a simple personal/startup setup.
  - **⚠️ Gotcha:** Azure is often a release or two behind, and you call the **deployment name**, not the model id.
- **Direct OpenAI** (`api.openai.com`, lesson 01)
  - **✅ Use when:** you want the newest models first and the simplest setup.
  - **🚫 Avoid when → use Azure:** enterprise compliance, data-residency, or private-network rules apply.
  - **⚠️ Gotcha:** keys and data go to the public endpoint — may not satisfy enterprise governance.

> 🔬 **Under the hood:** `AzureOpenAI` rewrites the request URL to
> `{azure_endpoint}/openai/deployments/{deployment}/chat/completions?api-version=...` — that's why you
> pass the **deployment name** and an **`api_version`**, not the public model id. With Entra ID, the
> `azure_ad_token_provider` fetches a **short-lived bearer token** (and silently refreshes it) instead
> of sending a static key.

## 🚀 Stage 3 — In Practice / Why It Matters

If you join an enterprise (banks, healthcare, government), you'll almost certainly use **Azure OpenAI**,
not the public API — for the governance above. The router in lesson 04 can fail **OpenAI → Azure**
(or vice-versa) for resilience, a very common production pattern. Deep Azure AI is Phase 5 (AI-102).

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Provider** | Azure OpenAI vs direct OpenAI | **Azure** for enterprise compliance, data residency, VNet/private endpoints, managed identity · **direct OpenAI** for the newest models first and the simplest setup |
| **Auth** | API key vs **Entra ID managed identity** | **managed identity** (keyless) in production · API key only for quick local dev |
| **Client** | `AzureOpenAI` vs `AsyncAzureOpenAI` | **async** inside FastAPI (concurrent calls) · sync for scripts |
| **`model=`** | model name vs **deployment name** | always the **deployment name** you created (not the base model id) |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| 404 / "deployment does not exist" | Passed the model name, not the deployment | `model="<your-deployment-name>"` |
| `api_version` errors | Missing/old version | Pass a current `api_version="YYYY-MM-DD"` |
| 401 / auth failure | Wrong endpoint or key/identity | Check `azure_endpoint`; use Entra ID provider |
| Works locally, fails in cloud | Managed identity not granted | Assign the resource RBAC role to the identity |
| Used `OpenAI(...)` class | Wrong client for Azure | Use `AzureOpenAI(...)` |

## 📌 Quick Reference

```python
from openai import AzureOpenAI          # or AsyncAzureOpenAI for FastAPI
client = AzureOpenAI(
    azure_endpoint="https://<resource>.openai.azure.com",
    api_key=...,                       # OR azure_ad_token_provider=... (Entra ID, preferred)
    api_version="2024-10-21",          # required
)
client.chat.completions.create(model="<DEPLOYMENT-name>", messages=[...])
```
- Same SDK, different client: **`AzureOpenAI`/`AsyncAzureOpenAI`** · **`api_version`** · **`azure_endpoint`** · **`model = deployment name`**.
- Prefer **Entra ID managed identity** over keys · handle **`content_filter`** errors · VNet/private endpoints for isolation.

> 🎯 **Interview angle:** "OpenAI vs Azure OpenAI in code?" → same SDK and call shape; you use the
> `AzureOpenAI` client with `api_version`/`azure_endpoint`, pass the **deployment name** as `model`,
> and typically auth via **Entra ID managed identity** (keyless) for compliance/data-residency.

## 🛑 STOP — Self-Check

Your Azure call fails with "deployment does not exist," even though `gpt-4o` is a real model. You
passed `model="gpt-4o"`. What's wrong, and what should `model` be?

<details><summary>Answer</summary>

With Azure OpenAI you don't pass the **model name** — you pass the **deployment name** you created in
your Azure resource (e.g. you deployed `gpt-4o` under the name `my-gpt4o`, so `model="my-gpt4o"`).
Azure routes by *deployment*, not by the underlying model id, so `model="gpt-4o"` doesn't match any
deployment and 404s. (Also make sure `api_version` and `azure_endpoint` are set.)
</details>
