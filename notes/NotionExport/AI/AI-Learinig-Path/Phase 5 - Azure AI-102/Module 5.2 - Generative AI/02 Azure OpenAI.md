# 02 — Azure OpenAI: Generate Content

> Phase 5 · Module 5.2 · Lesson 2 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Generative AI (15–20%)**
> *Provisioning Azure OpenAI and generating text, code, and images is the most-used skill in any Azure genAI
> role and a guaranteed cluster of exam questions.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Foundry (Lesson 01) is the workspace; **Azure OpenAI** is the engine inside it. The exam
tests the concrete generate-content tasks: **provision** the resource, **deploy** a model, send prompts for
**text and code**, generate **images with DALL-E**, use **multimodal** (image-in) models, and **integrate** it
all into an app. These are the same OpenAI models from Phase 1 — wrapped with Azure's auth, region, and quota.
*(Tuning, monitoring, and fine-tuning are the "operationalise" half — Lesson 03.)*

**Why care:** "use Azure OpenAI to generate content" is an explicit exam objective and the literal core of the job.

## 🔑 New Terms (plain English)
- **Provision** — create the Azure OpenAI resource (gets you an endpoint + access to models).
- **Deployment** — a named instance of a model (e.g. `gpt-4o`) you call from code.
- **DALL-E** — the image-generation model (text prompt → image).
- **Multimodal model** — accepts **image + text** as input (e.g. "what's wrong in this photo?").
- **Completion / chat** — the text the model generates from your prompt.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: hiring a versatile studio)
Azure OpenAI is a studio you commission: **provision** = sign the contract and get a studio key; **deploy a
model** = pick which artist (GPT-4o, DALL-E) is on call; then you send briefs — write this, code that, draw
this, "look at this photo and describe it." **Aha!:** it's the same OpenAI talent from Phase 1, but now badged,
metered, and access-controlled by Azure.

## ⚙️ Stage 2 — How It Works (each capability a mini-reference)

#### Provision the resource & select/deploy a model
- **What & why:** create an Azure OpenAI resource (region + quota), then deploy a model under a name. **✅ Use
  when:** starting any genAI app. **🚫 Avoid → biggest model by default:** right-size to the task. **⚠️ Gotcha:**
  model/region availability and quota vary; your code calls the **deployment name**, not the model name.

#### Generate text & code
- **What & why:** send chat prompts to draft, summarise, classify, answer, or write code. **✅ Use when:**
  open-ended language tasks. **🚫 Avoid → Azure AI Language:** for a fixed label like sentiment. **⚠️:** control
  output with parameters (Lesson 03) and ground it for facts (Lesson 01).

#### Generate images with DALL-E
- **What & why:** text prompt → image. **✅ Use when:** creating illustrations/marketing visuals. **🚫 Avoid →
  Custom Vision/AI Vision:** those *analyse* images, they don't *create* them. **⚠️:** content filters apply to image prompts too.

#### Use large multimodal models (image-in)
- **What & why:** models that take an **image plus text** — "describe this", "extract the table", "what's the
  defect?" **✅ Use when:** reasoning over screenshots, photos, charts. **🚫 Avoid → OCR/Document Intelligence:**
  when you need exact field extraction from forms (cheaper, structured). **⚠️:** image tokens add cost.

#### Integrate into your application
- **What & why:** call the deployment from app code via the SDK/REST using the endpoint + (ideally) a managed
  identity. **✅ Use when:** any real product. **⚠️:** add retries/timeouts (Phase 1) and content safety (Lesson 04).

> 🔬 **Under the hood:** Azure OpenAI is the OpenAI models hosted in *your* Azure region/tenant — so you get
> data-residency, Entra ID auth, quota, and monitoring that the public API doesn't give you. A "deployment"
> maps your chosen name → model + version + capacity; your call is `POST {endpoint}/openai/deployments/{name}/...`.

### 💻 The SDK in code
```python
# pip install openai
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://<resource>.openai.azure.com/",
    api_key="<key>",                       # OR azure_ad_token_provider=... for Entra ID
    api_version="2024-10-21",              # api_version is REQUIRED on Azure
)

# --- Text / code (chat) ---
resp = client.chat.completions.create(
    model="gpt-4o",                        # the DEPLOYMENT name (NOT the base model name)
    messages=[{"role": "user", "content": "Write a haiku about Azure."}],
    temperature=0.7, max_tokens=200,
)
print(resp.choices[0].message.content)

img = client.images.generate(model="dall-e-3", prompt="a fox in snow", size="1024x1024", n=1)
emb = client.embeddings.create(model="text-embedding-3-large", input="hello")  # for RAG
```
Production auth uses Entra ID instead of a key:
```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
provider = get_bearer_token_provider(DefaultAzureCredential(),
                                     "https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(azure_endpoint="...", azure_ad_token_provider=provider, api_version="2024-10-21")
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `openai` |
| Client | **`AzureOpenAI`**(azure_endpoint, api_key \| azure_ad_token_provider, **api_version**) |
| `model=` | the **deployment name** (not the base model name) |
| Chat | `client.chat.completions.create(...)` → `.choices[0].message.content` |
| Images | `client.images.generate(model="dall-e-3", ...)` |
| Embeddings | `client.embeddings.create(model="text-embedding-3-large", ...)` |
| Multimodal | image content parts in `messages` (GPT-4o vision) |
| Params | temperature · top_p · max_tokens · stop · frequency_penalty · presence_penalty · seed · response_format |

### 🎯 Exam facts to memorise
- Use the **`AzureOpenAI`** client (not `OpenAI`); **`azure_endpoint`, auth, and `api_version` are all required**.
- **`model=` is the DEPLOYMENT name** you chose — a 404 usually means you passed the base model name.
- **DALL-E** → `images.generate`; **embeddings** → `embeddings.create`; **chat/code** → `chat.completions.create`.
- **Multimodal (image-in)** = pass an image URL/bytes as content parts to a vision model (GPT-4o).
- `response_format={"type":"json_object"}` enables **JSON mode**; `seed` aids reproducibility.
- Prod auth = **Entra ID** via `azure_ad_token_provider` (no key); content filters apply to prompts *and* images.

## 🚀 Stage 3 — In Practice / Why It Matters
A real app: provision Azure OpenAI in the required region → deploy a right-sized GPT-4o → call it from the SDK
with a managed identity → use a multimodal model for screenshot Q&A and DALL-E for visuals → wrap it with
content safety. This is the generate-content backbone the exam keeps probing, and the daily reality of the role.

## ⚖️ Variations & When to Use
| The task is… | Use |
|---|---|
| Draft / summarise / answer / code | **chat/completions** (GPT-4o etc.) |
| Create an image | **DALL-E** |
| Reason over an image + text | **multimodal model** |
| Extract fields from a form | **Document Intelligence** (not OpenAI) |
| Fixed label (sentiment/PII) | **Azure AI Language** (not OpenAI) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| 404 model not found | called model name | call the **deployment name** |
| Model unavailable in region | region/quota | pick a supported region; request quota |
| Image prompt blocked | content filter | adjust prompt; filters apply to DALL-E too |
| Secrets in code | key auth in prod | use **Entra ID + managed identity** (Lesson 03) |

## 📌 Quick Reference
- **Provision → deploy (named) → call the deployment name.**
- Text/code → chat · image-out → **DALL-E** · image-in → **multimodal** · forms → Document Intelligence.
- Integrate via SDK + managed identity; wrap with content safety.

## 🎯 Exam-style practice
**Q1.** Your call returns **404 DeploymentNotFound** though the model is deployed. Most likely mistake?
<details><summary>Answer</summary>You passed the **base model name** to `model=`. Azure OpenAI requires the **deployment name** you created.</details>

**Q2.** Which client, and the three required constructor args for Azure?
<details><summary>Answer</summary>**`AzureOpenAI`** with **`azure_endpoint`**, an **auth** value (`api_key` or `azure_ad_token_provider`), and **`api_version`**.</details>

**Q3.** You need guaranteed **valid JSON** output for downstream parsing. Which parameter?
<details><summary>Answer</summary>`response_format={"type": "json_object"}` (JSON mode).</details>

## 🛑 STOP — Self-Check
A retailer wants to (a) auto-write product descriptions, (b) generate banner images, and (c) read a **photo of
a damaged return** and describe the damage. Which Azure OpenAI capability for each?

<details><summary>Answer</summary>

- **(a) Product descriptions → text generation** (chat/completions, e.g. GPT-4o).
- **(b) Banner images → DALL-E** (text-to-image).
- **(c) Describe a damage photo → a large multimodal model** (image-in + text).

All three run on **one provisioned Azure OpenAI resource** with the relevant model **deployments** — and your
code calls each by its **deployment name**.
</details>

⏭️ **Next:** 03 — Optimise & Operationalise (Branch 2.3).
