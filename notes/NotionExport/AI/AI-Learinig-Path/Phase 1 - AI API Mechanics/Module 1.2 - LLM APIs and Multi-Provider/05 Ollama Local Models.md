# 05 — Ollama: Local Models

> Phase 1 · Module 1.2 · Lesson 5 · `[SHOULD — 55%]`

## 🗺️ Stage 0 — Concept Map

Everything so far called a **cloud** model (your data leaves your machine, and you pay per token).
**Ollama** runs open models **locally** — private, offline, free-per-call, great for development and
sensitive data. It appears in ~55% of JDs (rising for privacy/cost reasons). Builds on lessons 01–04;
it even speaks the OpenAI format, so your existing code works.

> 🔑 Local model names like `gemma3` / `gpt-oss` are current examples — see ollama.com for the list.

## 🔑 New Terms (plain English)

- **Ollama** — an app that downloads and runs open LLMs on your own computer.
- **Local model** — a model whose weights live and run on *your* hardware (no network call out).
- **`ollama pull`** — download a model (like `docker pull` for models).
- **`localhost:11434`** — the local address Ollama serves on.
- **OpenAI-compatible endpoint** — Ollama also mimics the OpenAI API, so OpenAI-style code works against it.
- **Modelfile** — a recipe to create a customized model (base + system prompt + params).
- **Quantization** — shrinking a model's weights to fewer bits (e.g. 4-bit) so it fits less RAM/runs faster.
- **GGUF / `Q4_K_M`** — the local-model file format / a common 4-bit quantization level.
- **`keep_alive`** — how long Ollama keeps a model loaded in RAM between calls.

## 🎈 Stage 1 — The Simple Idea (analogy: cooking at home vs eating out)

Cloud models are **eating out**: great quality, someone else's kitchen, you pay per meal, and they see
your order. **Ollama is cooking at home**: **private**, **free per meal**, works with the **internet
off** — but you buy the equipment (RAM/GPU) and the dishes are simpler than a top restaurant's.

**The "Aha!":** for dev, testing, and sensitive/offline data, a *local* model is often the right call
— and you can keep the *same code* you wrote for the cloud.

**💢 The old/painful way** — renting a cloud GPU or paying per-token to a hosted API just to prototype,
and sending every prompt off your machine. Ollama runs capable open models **locally** — free,
private, and offline.

## ⚙️ Stage 2 — How It Actually Works

### 5.1 Set up

Install the Ollama app (it runs a background server), then pull a model and the Python library:

```powershell
ollama pull gemma3           # download a model once
pip install ollama
```

### 5.2 Call it with the native library

```python
from ollama import chat

response = chat(
    model="gemma3",
    messages=[{"role": "user", "content": "Why is the sky blue?"}],
)
print(response.message.content)        # or response['message']['content']
```

Streaming and async mirror the other SDKs:

```python
from ollama import chat
for chunk in chat(model="gemma3", messages=[{"role":"user","content":"Hi"}], stream=True):
    print(chunk.message.content, end="", flush=True)

# async:
from ollama import AsyncClient
await AsyncClient().chat(model="gemma3", messages=[{"role":"user","content":"Hi"}])
```

### 5.3 The trick: reuse your OpenAI code locally

Ollama exposes an **OpenAI-compatible** endpoint, so you can point the **OpenAI client** (lesson 01)
straight at it — no rewrite:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # key is ignored locally
client.chat.completions.create(model="gemma3", messages=[{"role":"user","content":"Hi"}])
```

Or via LiteLLM (lesson 04): `completion(model="ollama/gemma3", messages=[...])`. So you can **develop
against a free local model and switch to the cloud in production by changing one string**.

### 5.4 Modelfile — bake in a custom model

A **Modelfile** creates a reusable, named model from a base + your defaults (system prompt, params):

```dockerfile
# Modelfile
FROM gemma3
SYSTEM "You are a terse code reviewer. Reply in bullet points."
PARAMETER temperature 0.2
```
```powershell
ollama create my-reviewer -f Modelfile     # now: ollama run my-reviewer  (or model="my-reviewer")
```

### 5.5 Quantization — pick the right size for your RAM

Local models ship in **quantized** forms (weights squeezed to fewer bits) so they fit your hardware.
The format is **GGUF**; the level looks like **`Q4_K_M`** (4-bit) up to `Q8` (8-bit) or `fp16` (full):

| Level | Size / RAM | Quality | Use when |
| --- | --- | --- | --- |
| `Q4_K_M` | smallest | good | **the default** — best size/quality trade-off |
| `Q5` / `Q6` | medium | better | you have RAM to spare |
| `Q8` / `fp16` | largest | best | quality-critical + a big GPU |

```powershell
ollama pull llama3.1:8b-instruct-q4_K_M    # the tag picks the quantization
```

A 7–8B model at `Q4_K_M` needs roughly **5–6 GB RAM**; the same model at `fp16` needs ~16 GB. Pick the
biggest level that fits comfortably. (Open models you'll see: **Llama 3.x, Mistral, Phi-4, Qwen2.5**.)

### 5.6 Keep it warm + force JSON

```python
from ollama import chat
chat(model="gemma3", messages=[...], keep_alive="10m")   # keep the model in RAM 10 min (avoid reload lag)
chat(model="gemma3", messages=[...], format="json")      # force valid JSON (or pass a Pydantic JSON schema)
```

### 5.7 When to use local vs cloud

- **Use local:** sensitive/PII data, offline, cheap iteration during dev, full control.
- **Use cloud:** you need top-tier quality/large models, or you lack the GPU/RAM to run them well.

> 🔬 **Under the hood:** `ollama serve` runs a local HTTP server on **:11434**; `ollama pull` downloads
> a **quantized GGUF** model (e.g. `Q4_K_M`) that it loads into RAM/VRAM on first use. It exposes an
> **OpenAI-compatible** `/v1` endpoint, so the same SDK code just points at localhost. `keep_alive`
> controls how long the model stays resident in memory between calls.

## 🚀 Stage 3 — In Practice / Why It Matters

A common workflow: **prototype against Ollama** (fast, free, private), then flip to a cloud model for
production via LiteLLM — same code. For regulated data that can't leave the building, local models may
be the *only* option. That privacy/cost angle is why JDs increasingly list Ollama.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Local vs cloud** | Ollama vs a cloud API | **local** for privacy/PII, offline, cheap dev iteration, cost · **cloud** for top quality/big models or no GPU |
| **How to call** | native `ollama` lib vs OpenAI-compatible endpoint vs LiteLLM | **OpenAI-compat / LiteLLM** to reuse code & swap to cloud · **native lib** for Ollama-only features (`pull`/`create`/`ps`) |
| **Quantization** | `Q4_K_M` vs `Q5/Q6` vs `Q8/fp16` | **`Q4_K_M`** default (best size/quality) · higher bits if RAM allows · `fp16` for max quality + big GPU |
| **Customize** | base model vs **Modelfile** | **Modelfile** to bake a system prompt/params into a reusable named model |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `ConnectionError` to `:11434` | Ollama app not running | Start Ollama (it runs the local server) |
| `model 'x' not found` | Didn't pull it | `ollama pull x` first |
| Answers weaker than ChatGPT | Smaller local model | Expected — use a bigger model or the cloud for hard tasks |
| Very slow / runs on CPU | No GPU / too-big model | Pick a smaller model, or one that fits your hardware |
| OpenAI-compat call 404s | Wrong base URL | `base_url="http://localhost:11434/v1"` |

## 📌 Quick Reference

```python
# native:
from ollama import chat
chat(model="gemma3", messages=[{"role":"user","content":"..."}]).message.content   # stream=True to stream

# reuse OpenAI code locally:
OpenAI(base_url="http://localhost:11434/v1", api_key="ollama").chat.completions.create(model="gemma3", ...)
# or LiteLLM:  completion(model="ollama/gemma3", messages=[...])
```
- `ollama pull <model>` then `chat(...)` · serves on **`localhost:11434`** · **OpenAI-compatible** so existing code works.
- Local = **private/offline/free-per-call**, trade-off = smaller models + your hardware.
- **Quantization** `Q4_K_M` = default size/quality · **Modelfile** = custom named model · `keep_alive` = stay in RAM · `format="json"` = force JSON.

> 🎯 **Interview angle:** "When would you use a local model like Ollama?" → sensitive/offline data,
> cheap dev iteration, and cost control; it's OpenAI-API-compatible, so you can prototype locally and
> switch to a cloud provider in production by changing the model string.

## 🛑 STOP — Self-Check

You want to develop and test your AI feature **for free and offline**, then deploy it to a powerful
cloud model later **without rewriting your call code**. How does Ollama make that possible?

<details><summary>Answer</summary>

Ollama runs an open model locally and exposes an **OpenAI-compatible endpoint** (and works through
LiteLLM). So you write your code once in OpenAI format, point it at
`http://localhost:11434/v1` (or `ollama/<model>` via LiteLLM) during development — **free, offline,
private** — and to go to production you just **change the base URL / model string** to a cloud
provider. Same code, no rewrite.
</details>
