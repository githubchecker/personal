# 04 — Responsible AI & Azure Content Safety

> Phase 5 · Module 5.1 · Lesson 4 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Plan & Manage (20–25%)**
> *"Implement AI responsibly" is its own exam objective, and content-safety/governance is a hard requirement
> in every regulated AI job. This is the Azure-native version of the guardrails from Phase 4.3.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** An AI app can produce harmful content (hate, violence, self-harm, sexual), leak
copyrighted text, hallucinate, or be **jailbroken** into ignoring its rules. Ship without controls and you
risk real harm, legal exposure, and brand damage. The exam tests Azure's safety stack: **content moderation,
content filters, blocklists, prompt shields, harm/groundedness detection, and a governance framework** — most
of it **configured, not coded**.

**Why care:** it's a named exam objective *and* a non-negotiable in finance, healthcare, and any EU-facing AI.

## 🔑 New Terms (plain English)
- **Azure AI Content Safety** — a service that scores text/images for harm (`analyze_text` / `analyze_image`),
  returning a **severity** level per category.
- **Content filter** — blocks hate / violence / sexual / self-harm above a chosen severity, on input *and* output.
- **Blocklist** — your own list of banned words/phrases.
- **Prompt shields** — detect and block **jailbreak** and **indirect prompt-injection** attempts.
- **Groundedness detection** — flags answers not supported by your source data (hallucination).
- **Protected-material detection** — flags copyrighted/known text in output.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a building's security desk)
Security checks people **on the way in** (prompt shields stop intruders trying to trick their way past the
rules) and checks parcels **on the way out** (content filters block anything harmful leaving the building),
keeps a **custom banned list** at the door (blocklist), verifies claims against the records (groundedness),
and logs every incident (governance). **Aha!:** safety is layered on **both input and output**, and you mostly
**turn knobs** rather than write code.

## ⚙️ Stage 2 — How It Works (each control as a mini-reference)

#### Content filters — block harm categories
- **What & why:** built into Azure OpenAI; scores hate/violence/sexual/self-harm and blocks above a severity
  you set, on prompt **and** completion. **✅ Use when:** any user-facing app. **🚫 Avoid → off:** never. **⚠️
  Gotcha:** default thresholds may be too loose or too strict — tune per category.

#### Blocklists — your own banned terms
- **What & why:** a custom list of words/phrases to always block (competitor names, slurs, internal codenames).
  **✅ Use when:** domain-specific bans the generic filter won't catch. **⚠️:** keep it maintained; it's exact-match-ish, not semantic.

#### Prompt shields — stop jailbreak & injection
- **What & why:** detect "ignore your instructions…" (direct jailbreak) and malicious instructions hidden in
  **retrieved documents** (indirect injection — the RAG risk). **✅ Use when:** any app taking user input or RAG
  content. **🚫 Avoid → relying on the system prompt alone:** models still get tricked. **⚠️:** pair with output filters.

#### Harm / groundedness / protected-material detection
- **Groundedness** flags answers unsupported by your context (hallucination). **Protected material** flags
  copyrighted output. **✅ Use when:** RAG/factual apps and content generation. **⚠️:** groundedness needs your source text to compare against.

#### Content moderation (text & images)
- **What & why:** the standalone **Content Safety** API moderates *any* text/image (not just OpenAI output),
  returning severities. **✅ Use when:** moderating user uploads or third-party content. **⚠️:** set per-category thresholds.

#### Responsible-AI governance framework
- **What & why:** the process wrapper — Microsoft's Responsible AI principles, the **Responsible AI dashboard**,
  **risk classification**, and **technical documentation** (EU AI Act). **✅ Use when:** regulated/enterprise. **⚠️:** governance is policy + docs, not just a toggle.

> 🔬 **Under the hood:** Content Safety is a **classifier API** that Azure OpenAI calls automatically around
> each request; you configure thresholds, blocklists, and shields in Foundry. It complements the
> framework-level guardrails from Phase 4.3 (NeMo Guardrails, Presidio) for **defence in depth** — Azure
> controls at the platform, your own rails in the app.

### 💻 The SDK in code
```python
# pip install azure-ai-contentsafety
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

client = ContentSafetyClient("https://<resource>.cognitiveservices.azure.com/",
                             AzureKeyCredential("<key>"))
resp = client.analyze_text(AnalyzeTextOptions(text="...user or model text..."))
for c in resp.categories_analysis:
    print(c.category, c.severity)   # Hate / SelfHarm / Sexual / Violence -> severity 0,2,4,6
# client.analyze_image(AnalyzeImageOptions(image=...)) for images
```
Inside **Azure OpenAI**, the same engine runs automatically as **content filters** (input + output); you also
configure **blocklists** and **prompt shields** in Foundry.

### 📦 Responsible-AI controls quick reference
| Risk | Control |
|---|---|
| Harmful generated text/images | **Content filters** (severity per category, input+output) |
| Specific banned terms | **Blocklists** |
| Jailbreak / injected instructions | **Prompt shields** (direct + indirect) |
| Hallucination on RAG | **Groundedness detection** |
| Copyrighted output | **Protected material detection** |
| Moderate any text/image | **Content Safety** `analyze_text` / `analyze_image` |
| Compliance/audit | **Responsible AI** governance (RAI Standard, transparency notes) |

### 🎯 Exam facts to memorise
- **Four harm categories:** **Hate · Sexual · Violence · Self-Harm**.
- **Severity levels: 0, 2, 4, 6** (the trimmed scale; the full text scale is 0–7) — you set the block threshold per category.
- `ContentSafetyClient` → **`analyze_text`** / **`analyze_image`**; package `azure-ai-contentsafety`.
- **Prompt shields** detect **direct jailbreak** *and* **indirect (document) injection** — the RAG risk.
- **Groundedness detection** flags unsupported answers; **protected material detection** flags copyrighted output.
- Azure OpenAI **content filters** apply to **prompt and completion** (and DALL-E prompts); mostly **configured in Foundry**, not coded.

## 🚀 Stage 3 — In Practice / Why It Matters
A production Azure AI app layers them: **prompt shields** on input → **content filters** + **blocklist** on
output → **groundedness** on RAG answers → **Content Safety** on user uploads → all logged under a
**governance framework** with risk classification and documentation. This "responsible by design" stack is
both an exam objective and the thing that lets an enterprise actually deploy AI.

## ⚖️ Variations & When to Use
| The risk is… | Control |
|---|---|
| Harmful generated content | **Content filters** (severity per category) |
| Specific banned terms | **Blocklist** |
| Jailbreak / injected instructions | **Prompt shields** |
| Hallucination on RAG | **Groundedness detection** |
| Copyrighted output | **Protected-material detection** |
| Moderating user uploads | **Content Safety** `analyze_text`/`analyze_image` |
| Compliance / audit | **Responsible-AI governance** (dashboard, risk class, docs) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Harmful output slips through | filters off or too loose | enable + tighten severity per category |
| Jailbreak via a pasted doc | no input shielding | enable **prompt shields** (covers indirect injection) |
| Bot states made-up "facts" | no grounding check | enable **groundedness detection**; cite sources |
| Audit fails | no governance docs | adopt the Responsible-AI framework: risk class + documentation |

## 📌 Quick Reference
- **Input:** prompt shields. **Output:** content filters + blocklist + groundedness + protected-material.
- **Any media:** Content Safety `analyze_text` / `analyze_image` (severity levels).
- **Wrap it all:** Responsible-AI governance (dashboard, risk classification, EU-AI-Act docs).
- Mostly **configured in Foundry**, not coded; pairs with Phase 4.3 for defence in depth.

## 🎯 Exam-style practice
**Q1.** Name the four Content Safety harm categories and the severity levels returned.
<details><summary>Answer</summary>**Hate, Sexual, Violence, Self-Harm**; severities **0, 2, 4, 6** (trimmed scale; full 0–7).</details>

**Q2.** A user uploads a document containing hidden "ignore your instructions" text. Which control, and which threat type?
<details><summary>Answer</summary>**Prompt shields** — they detect **indirect prompt injection** (hidden instructions in retrieved/uploaded content), as well as direct jailbreak.</details>

**Q3.** Your RAG bot states facts not in its sources. Which Azure safety feature catches this?
<details><summary>Answer</summary>**Groundedness detection** (flags answers unsupported by the provided context).</details>

## 🛑 STOP — Self-Check
Users are jailbreaking your RAG bot two ways: typing "ignore your rules…", and **uploading documents that
contain hidden instructions**. Plus, leadership wants proof you're compliant. Name the Azure controls.

<details><summary>Answer</summary>

- **Both jailbreak routes → Prompt shields** — they detect *direct* jailbreak ("ignore your rules") **and**
  *indirect* prompt-injection hidden in **retrieved/uploaded documents**.
- Add **output content filters** (+ a **blocklist**) so anything harmful that slips through is caught on the
  way out, and **groundedness detection** so it can't state unsupported "facts".
- **Compliance proof → the Responsible-AI governance framework**: risk classification, the Responsible AI
  dashboard, and technical documentation (EU AI Act).

Layered input+output safety, plus governance for the audit.
</details>

⏭️ **Next:** Module 5.2 — Generative AI on Foundry (Branch 2.1).
