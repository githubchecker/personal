# 03 — Optimise & Operationalise a GenAI Solution

> Phase 5 · Module 5.2 · Lesson 3 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Generative AI (15–20%)**
> *"Optimise and operationalise" is its own exam objective — and the difference between a demo and a product
> in any Azure genAI job.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** A working model still needs to be **controlled** (right output style), **watched**
(monitoring/tracing), **scaled** (capacity, model updates), **improved** (feedback, reflection, prompt
engineering), and sometimes **specialised** (fine-tuning) or pushed to the **edge** (containers). The exam tests
each of these day-2 levers. Skip them and you get runaway cost, silent quality drift, or an app that can't scale.

**Why care:** it's an explicit exam objective and the operational half of the AI engineer role.

## 🔑 New Terms (plain English)
- **Generation parameters** — dials that shape output: **temperature**/**top-p** (creativity), **max-tokens**
  (length), **stop** sequences, frequency/presence penalties.
- **Tracing** — recording each request/response (inputs, tokens, latency) to debug and monitor.
- **Orchestration** — routing a request to the right model (cheap vs frontier) by task complexity.
- **Reflection** — having the model critique and revise its own output (Phase 3.1.02).
- **Fine-tuning** — retraining a model on your examples to bake in tone/format (Phase 4.4).
- **Edge container** — running a model/service on-prem or on a device, not the cloud.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: tuning and running a car fleet)
Building the car was Lesson 02. Now you **tune the engine** (parameters), put it on a **dashboard with sensors**
(monitoring/tracing), **add vehicles for rush hour** (scale), **route easy trips to the small car** (model
orchestration), **send drivers to advanced training** only if needed (fine-tuning), and run a **local depot**
for off-grid routes (edge containers). **Aha!:** the model is fixed talent; operationalising is everything
around it that keeps it cheap, reliable, and good.

## ⚙️ Stage 2 — How It Works (each lever a mini-reference)

#### Configure generation parameters
- **What & why:** **temperature/top-p** control creativity (low = factual/deterministic, high = creative);
  **max-tokens** caps length; **stop** ends output cleanly. **✅ Factual bot → low temp; brainstorming → higher.**
  **⚠️ Gotcha:** high temperature on a factual task invites hallucination.

#### Monitoring & diagnostics
- **What & why:** track performance, token usage, errors, and latency via Azure Monitor. **✅ Always in prod.**
  **⚠️:** turn on diagnostic logging to a workspace, or you can't see history or cost drivers.

#### Scale & manage resources (capacity + model updates)
- **What & why:** choose PAYG vs **PTU** (reserved throughput) and plan **base-model version updates**. **✅ Use
  PTU when:** steady high volume needs predictable latency/cost. **⚠️:** model versions get retired — test before upgrading.

#### Tracing & feedback collection
- **What & why:** capture full traces and user thumbs-up/down to build eval datasets and find failures. **✅ Use
  when:** improving quality over time. **⚠️:** mask PII in traces (Phase 4.3).

#### Model reflection
- **What & why:** the model critiques and revises its own answer for higher quality. **✅ Use when:** quality >
  latency/cost (writing, reasoning). **🚫 Avoid → plain single-shot:** simple lookups. **⚠️:** needs a stop rule or it loops.

#### Orchestrate multiple models
- **What & why:** route simple tasks to a cheap/small model and hard ones to a frontier model. **✅ Use when:**
  cutting cost at scale (Phase 4.4 / LiteLLM router pattern). **⚠️:** a mis-route hurts quality — test the router.

#### Prompt engineering & prompt-flow tuning
- **What & why:** few-shot examples, clear instructions, and grounding lift quality cheaply *before* you fine-
  tune. **✅ Always try first.** **⚠️:** keep prompts as versioned templates.

#### Fine-tune a model
- **What & why:** retrain on `{prompt, completion}` examples to bake in consistent tone/format. **✅ Use when:**
  prompting + RAG still can't get the behaviour. **🚫 Avoid → for facts:** use RAG/grounding instead. **⚠️:** fine-tuning before a working RAG is the wrong order; re-evaluate for regressions after.

#### Deploy to edge/local containers
- **What & why:** run a service in a container on-prem/edge for compliance or low latency. **✅ Use when:** data
  can't leave the network or you need offline. **⚠️:** still needs a billing link to Azure.

> 🔬 **Under the hood:** parameters reshape the model's sampling; monitoring/tracing tap Azure's telemetry;
> orchestration is a router in front of several deployments; fine-tuning trains adapter/model weights on your
> data. None change the *base* model's knowledge — for that you ground (Lesson 01) or fine-tune behaviour.

### 💻 The SDK in code
Most "optimise" levers are **parameters on the call** plus **config**, not new clients:
```python
resp = client.chat.completions.create(
    model="gpt-4o",                 # deployment name
    messages=[...],
    temperature=0.0,                # 0 = deterministic/factual; higher = creative
    top_p=1.0,                      # nucleus sampling (tune temperature OR top_p, not both)
    max_tokens=400,                 # cap output length (cost control)
    stop=["\n\n"],                   # stop sequence(s)
    frequency_penalty=0.0,          # discourage repetition
    presence_penalty=0.0,           # encourage new topics
    seed=42,                        # reproducibility (best-effort)
)
```
- **Monitoring/tracing:** Azure Monitor + diagnostic settings; emit **OpenTelemetry** traces
  (`azure-ai-projects` tracing + `azure-monitor-opentelemetry`) to capture inputs, tokens, latency.
- **Scale:** choose **PTU** (provisioned) vs PAYG; plan base-model version upgrades.
- **Fine-tuning:** run a fine-tune **job** on `{prompt, completion}` data — only after prompting + RAG fall short.
> 🔎 Note: monitoring/fine-tuning SDK surfaces evolve — memorise the **levers** over exact method names.

### 📦 Levers & parameters quick reference
| Goal | Lever |
|---|---|
| Factual/deterministic | `temperature=0` (low `top_p`) |
| Creative | higher `temperature`/`top_p` |
| Cap cost/length | `max_tokens`, `stop` |
| Reduce repetition | `frequency_penalty` / `presence_penalty` |
| Reproducibility | `seed` |
| Predictable latency at volume | **PTU** capacity |
| Observability | Azure Monitor + **OpenTelemetry** tracing + feedback |
| Cut cost at scale | **model orchestration** (route cheap↔frontier) |
| Consistent tone/format | **fine-tuning** (last resort) |

### 🎯 Exam facts to memorise
- **temperature vs top_p:** tune **one**, not both; `temperature=0` for factual/deterministic output.
- **max_tokens** caps output (cost); **stop** sequences end generation cleanly; **seed** aids reproducibility.
- **PTU** (provisioned throughput) = predictable latency/cost for steady high volume; **PAYG** for spiky/low.
- **Order for behaviour:** prompt-engineer → RAG (facts) → **fine-tune last** (tone/format, not knowledge).
- **Tracing + feedback** build your eval datasets; **mask PII** in traces.
- **Model orchestration** routes simple calls to a cheap model, hard ones to a frontier model (cost control).
- **Edge/local containers** for compliance/offline (still need a billing link to Azure).

## 🚀 Stage 3 — In Practice / Why It Matters
A mature Azure genAI app: low temperature + grounding for accuracy → Azure Monitor + tracing → PTU capacity →
a cheap/frontier model router for cost → prompt-template iteration → fine-tune only the one stubborn behaviour
→ an edge container for the regulated tenant. That operational discipline is what the exam's "optimise and
operationalise" objective is really checking, and it reuses Phase 4 wholesale.

## ⚖️ Variations & When to Use
| Goal | Lever |
|---|---|
| Factual, deterministic output | low **temperature** |
| Creative output | higher temperature/top-p |
| Cut cost at scale | **model orchestration** (cheap vs frontier) |
| Higher answer quality | **reflection** / prompt engineering |
| Consistent tone/format | **fine-tuning** (after RAG) |
| Compliance / offline | **edge container** |
| Predictable latency at volume | **PTU** capacity |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Factual bot hallucinates | temperature too high | drop to ~0 + ground it |
| Surprise cost | no monitoring / wrong tier | Azure Monitor + budgets; consider PTU; orchestrate |
| Fine-tune didn't add facts | wrong tool | use **RAG/grounding** for knowledge |
| Reflection loops forever | no stop rule | cap iterations |
| Upgrade broke output | base-model version change | test new version before switching |

## 📌 Quick Reference
- **Tune:** temperature/top-p/max-tokens. **Watch:** Monitor + tracing + feedback. **Scale:** PTU + plan model
  updates. **Save cost:** orchestrate cheap↔frontier. **Improve:** prompt-engineer → reflect → fine-tune (last).
  **Edge:** container for compliance/offline.
- Order for behaviour: **prompt → RAG → fine-tune.** RAG for facts, fine-tune for style.

## 🎯 Exam-style practice
**Q1.** A factual bot occasionally hallucinates and answers vary run-to-run. Two parameter changes?
<details><summary>Answer</summary>Set **`temperature=0`** (deterministic) and ground it (RAG); optionally set a **`seed`** for reproducibility.</details>

**Q2.** Steady, high-volume traffic needs predictable latency and cost. Which capacity option?
<details><summary>Answer</summary>**PTU** (provisioned throughput units), not PAYG.</details>

**Q3.** Prompting + RAG still can't enforce a strict house style. Last resort — and what it does NOT fix?
<details><summary>Answer</summary>**Fine-tuning** (bakes in tone/format). It does **not** add facts/knowledge — that's RAG's job.</details>

## 🛑 STOP — Self-Check
Your genAI app is (a) too expensive at scale, and (b) occasionally invents facts in its support answers. Name
the operational lever for each — and the one trap to avoid.

<details><summary>Answer</summary>

- **(a) Cost at scale → model orchestration:** route simple/classification calls to a cheap small model and
  only hard reasoning to a frontier model (plus PTU if volume is steady, and caching from Phase 4.4).
- **(b) Inventing facts → low temperature + grounding (RAG):** make it deterministic and answer from your data.
- **Trap to avoid:** **don't fine-tune to fix the hallucinations** — fine-tuning bakes in *behaviour/format*,
  not *facts*; grounding is the right tool, and fine-tuning before a working RAG is the wrong order.
</details>

⏭️ **Next:** Module 5.3 — Agents on Foundry (Branch 3.1).
