# 04 — Fine-Tuning & Model Adaptation (SFT, LoRA & QLoRA)

> Phase 4 · Module 4.4 · Lesson 4 of 5 · [← Prev: 03 Prompt and Token Optimisation](03%20Prompt%20and%20Token%20Optimisation.md) · [Module 4.4 Index](README.md) · [Next: 05 Milestone — Full Production System →](05%20Milestone%20-%20Full%20Production%20System.md)

---

## 🗺️ Stage 0 — Concept Map

**The problem:** Prompt engineering fails when an LLM refuses to adhere strictly to complex, domain-specific syntax or output schemas across millions of calls. Meanwhile, RAG fails when the task requires learning a new *behavior* (such as diagnosing medical codes, generating proprietary SQL dialects, or adopting an exact corporate voice) rather than merely looking up *facts*. Trying to force base models to do this solely via massive system prompts blows up token latency and cost.

**Where it fits:**
- **Builds on:** Phase 0.0 (Parameters & Weights), Phase 1 (Prompt Engineering & Structured Outputs), and Phase 2 (RAG).
- **Unlocks:** Model right-sizing (distilling reasoning from a costly 70B model into a private, blazing-fast 8B model), enterprise domain adaptation, and complete autonomy over model weights.

**Why care as an AI Engineer / Architect?**
Enterprise leadership frequently asks: *"Should we fine-tune a model or build a RAG system?"* Recommending fine-tuning for dynamic enterprise data is a career-limiting mistake (fine-tuned models cannot stay up-to-date with daily documents). Conversely, failing to fine-tune when an 8B model needs to output strict, deterministic DSL code costs millions in wasted API fees on frontier models. Knowing the **exact decision boundaries**, how to format datasets, and how to execute **QLoRA / LoRA parameter-efficient adaptation** is a mandatory Lead/Architect capability.

---

## 🔑 New Terms (plain English)

| Term | One-line meaning |
| :--- | :--- |
| **Full Fine-Tuning** | Updating all billions of original model weights during training (rarely used; prohibitive GPU cost and high risk of catastrophic forgetting). |
| **SFT (Supervised Fine-Tuning)** | Training a base model on curated `(instruction, response)` example pairs to teach it a specific task or behavior. |
| **PEFT** | Parameter-Efficient Fine-Tuning — techniques that freeze original weights and train only a tiny fraction (<1%) of additional parameters. |
| **LoRA (Low-Rank Adaptation)** | Decomposing weight updates into two tiny low-rank matrices ($A \times B$), cutting memory usage by 70–80% without losing quality. |
| **QLoRA** | Quantized LoRA — quantizing base model weights to 4-bit (`NF4`) precision while training LoRA adapters in 16-bit, enabling fine-tuning on consumer GPUs. |
| **Rank ($r$) & Alpha ($\alpha$)** | LoRA hyperparameters: $r$ controls adapter matrix dimension (capacity); $\alpha$ scales the adapter's influence over the base model. |
| **ChatML / Messages Format** | The standard JSONL multi-turn dialogue schema (`system`, `user`, `assistant`) used to feed training data to instruction-tuned models. |
| **Token Masking** | Calculating training loss strictly on the model's generated tokens, ignoring user/prompt tokens so the model learns to answer, not repeat questions. |
| **Catastrophic Forgetting** | The risk where a model becomes great at the newly trained task but forgets how to do basic general reasoning. |
| **Adapter Merging** | Fusing the trained LoRA adapter weights directly into the base model weights (`merge_and_unload`) for zero-latency standalone serving. |

---

## 🎈 Stage 1 — The Simple Idea

### The Analogy: Prompt vs. RAG vs. Fine-Tuning
Imagine you hire a brilliant new employee at your software company:
1. **Prompt Engineering = Giving Verbal Instructions:** You tell them, *"Format your daily email with these 4 bullet points."* Fast and immediate, but if the instructions get too long, they get confused or forget.
2. **RAG = Giving an Open-Book Reference Manual:** You hand them your company's 500-page policy handbook and an internal search engine. When a customer asks a question, they look up the exact paragraph. Perfect for facts and live information.
3. **Fine-Tuning = Sending Them to Intense Trade School:** You send them to a 3-week bootcamp to speak fluent, idiomatic corporate legalese or Japanese. Their core behavior, syntax, and reflex reactions change permanently.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        The Architect Rule of Thumb                     │
├────────────────────────────────────────────────────────────────────────┤
│ • Need to teach FACTS / LIVE KNOWLEDGE? ──► Use RAG                    │
│ • Need to teach STYLE / FORMAT / TASK?  ──► Use FINE-TUNING (LoRA)     │
│ • Need both?                            ──► FINE-TUNE for style + RAG  │
└────────────────────────────────────────────────────────────────────────┘
```

> **The "Aha!":** Fine-tuning changes **how the model talks and behaves** (its reflexes). RAG changes **what the model knows** (its library of facts). You almost never fine-tune to teach facts!

---

## ⚙️ Stage 2 — How It Actually Works

### 1. The Architect Decision Matrix: Prompting vs. RAG vs. Fine-Tuning

```text
                               Do you need the model to know
                               private or rapidly changing facts?
                                        │
                         ├── YES ───────┴─────── NO ──┐
                         ▼                            ▼
                 Implement RAG                Does an off-the-shelf LLM
           (Vector DB + Embeddings)           follow your required syntax/tone
                         │                    with basic few-shot prompts?
                         │                            │
                         │              ├── YES ──────┴────── NO ──┐
                         │              ▼                          ▼
                         │      Use Prompt Engineering       Do you want to run a
                         │      (Cheapest & Fastest)         cheap 8B local model
                         │                                   with 70B formatting accuracy?
                         │                                         │
                         │                           ├── YES ──────┴────── NO ──┐
                         │                           ▼                          ▼
                         └──────────────► Use Fine-Tuning (LoRA)       Stick with Frontier
                                          (Style / Format / Task)      APIs (GPT-4o, Claude)
```

---

### 2. Dataset Engineering & Formatting (The ChatML Standard)

The modern standard for fine-tuning instruction models is the multi-turn `messages` JSONL format.

#### Problem-First Contrast:
```json
// ❌ NAIVE FORMAT (Brittle, ignores conversational roles and system guardrails):
{"prompt": "Convert to SQL: Show active users", "completion": "SELECT * FROM users WHERE active = 1;"}

// ✅ PRODUCTION CHATML FORMAT (Preserves system prompt, multi-turn context, and guardrails):
{"messages": [
  {"role": "system", "content": "You are a deterministic SQL compiler for PostgreSQL 16. Output valid SQL only."},
  {"role": "user", "content": "Fetch active users created in the last 30 days."},
  {"role": "assistant", "content": "SELECT id, email, created_at FROM users WHERE is_active = TRUE AND created_at >= NOW() - INTERVAL '30 days';"}
]}
```

#### Dataset Preparation Script (Python):
```python
import json

training_samples = [
    {
        "messages": [
            {"role": "system", "content": "You are a triage bot for Jira tickets. Output valid JSON only."},
            {"role": "user", "content": "Database pool exhausted under heavy API traffic."},
            {"role": "assistant", "content": json.dumps({"severity": "CRITICAL", "component": "Infrastructure", "routing": "DevOps"})}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a triage bot for Jira tickets. Output valid JSON only."},
            {"role": "user", "content": "Button color looks slightly off on iPad screens."},
            {"role": "assistant", "content": json.dumps({"severity": "LOW", "component": "Frontend", "routing": "UI/UX"})}
        ]
    }
]

# Write to jsonl format
with open("train_dataset.jsonl", "w", encoding="utf-8") as f:
    for entry in training_samples:
        f.write(json.dumps(entry) + "\n")

print(f"Generated {len(training_samples)} training samples.")
```

> [!IMPORTANT]
> **Data Quality Rule:** For task-specific adaptation, **500 to 1,000 meticulously verified, high-quality examples** produce far superior results compared to 50,000 noisy, web-scraped examples. Quality of target completions is everything.

---

### 3. Under the Hood: PEFT, LoRA & QLoRA Mechanics

In full fine-tuning, an 8-billion parameter model requires updating 8,000,000,000 weights. At 16-bit precision, the optimizer states (Adam), gradients, and weights consume over **80 GB to 120 GB of VRAM** — requiring massive enterprise GPU clusters ($A100 / H100$).

#### How LoRA Solves This:
Instead of updating the original weight matrix $W_0 \in \mathbb{R}^{d \times k}$, LoRA **freezes $W_0$ entirely** and injects two tiny trainable matrices, $A$ and $B$, of rank $r$:

$$\Delta W = \frac{\alpha}{r} (B \times A)$$

```text
                       Input x (Dimension: d)
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
       Original Weights W_0                Adapter Matrix A
       (FROZEN - No Gradients)            (Trainable, rank r)
        Shape: [d × k]                     Shape: [d × r]
               │                                 │
               │                                 ▼
               │                           Adapter Matrix B
               │                          (Trainable, rank r)
               │                           Shape: [r × k]
               │                                 │
               │                                 ▼
               │                           Scaled by (α / r)
               └────────────────┬────────────────┘
                                ▼
                       Output y = W_0(x) + ΔW(x)
```

* If $d = 4096$ and $k = 4096$, $W_0$ has **16,777,216 parameters**.
* If we choose rank $r = 8$, Matrix $A$ has $4096 \times 8 = 32,768$ and Matrix $B$ has $8 \times 4096 = 32,768$.
* **Total trainable parameters = 65,536 (a 99.6% parameter reduction!).**

#### What QLoRA Adds:
QLoRA quantizes the frozen base model weights $W_0$ down to **4-bit NormalFloat (`NF4`)**. The base model now occupies just ~4 GB–5 GB of VRAM. The LoRA adapter matrices $A$ and $B$ are kept in 16-bit bfloat16. This allows you to fine-tune an 8B model on a **single consumer GPU with 16 GB to 24 GB VRAM**.

---

### 4. Hands-on Fine-Tuning with Hugging Face `TRL` & `PEFT`

Here is the exact production script using Hugging Face's `SFTTrainer`, `peft`, and `bitsandbytes`:

```python
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 1. Base model identifier
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# 2. QLoRA 4-bit Quantization Configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",               # NormalFloat4 (optimized for weights)
    bnb_4bit_compute_dtype=torch.bfloat16,   # Fast 16-bit computation
    bnb_4bit_use_double_quant=True           # Quantize quantization constants for extra VRAM savings
)

# 3. Load Tokenizer & Quantized Model
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"                        # Automatically allocate across available GPU memory
)

# Prepare model for 4-bit gradient computation
model = prepare_model_for_kbit_training(model)

# 4. LoRA Adapter Configuration
peft_config = LoraConfig(
    r=16,                                    # Rank dimension (typical range: 8 to 64)
    lora_alpha=32,                           # Scaling parameter (typically 2x rank)
    lora_dropout=0.05,                       # Regularization to prevent overfitting
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]  # Target attention layers
)

# 5. Training Arguments
training_args = TrainingArguments(
    output_dir="./lora_checkpoints",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,          # Effective batch size = 4 * 2 = 8
    learning_rate=2e-4,
    logging_steps=10,
    fp16=False,
    bf16=True,                               # Use bfloat16 on Ampere/Ada GPUs
    optim="paged_adamw_8bit",                # Paged optimizer prevents OOM spikes
    report_to="none"
)

# 6. Load training dataset
dataset = load_dataset("json", data_files="train_dataset.jsonl", split="train")

# 7. Initialize SFTTrainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=2048
)

# 8. Run Training
# trainer.train()
# trainer.model.save_pretrained("./my_custom_adapter")
```

---

### 5. Cloud-Managed Alternative: OpenAI Fine-Tuning API

When you do not want to manage GPU infrastructure, cloud APIs provide one-click fine-tuning:

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Upload the training file to OpenAI
file_response = client.files.create(
    file=open("train_dataset.jsonl", "rb"),
    purpose="fine-tune"
)
training_file_id = file_response.id
print(f"Uploaded training file: {training_file_id}")

# 2. Launch the fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=training_file_id,
    model="gpt-4o-mini-2024-07-18",          # Cost-effective base model
    hyperparameters={"n_epochs": 3}
)
print(f"Fine-tuning job initiated: {job.id}")
```

---

### 6. Adapter Merging & Standalone Deployment

After training, you have two choices for serving:
1. **Dynamic Adapters:** Keep the base model in memory and dynamically swap small 50MB LoRA adapter weights depending on the tenant or task.
2. **Merged Standalone Model:** Permanently blend the adapter weights into the base weights for zero inference overhead.

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

base_model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
adapter_dir = "./my_custom_adapter"

# 1. Load base model in full 16-bit precision (NOT 4-bit during merging)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch.bfloat16,
    device_map="cpu"                         # Merging is typically done on CPU/RAM
)

# 2. Attach the trained LoRA adapter
model_with_adapter = PeftModel.from_pretrained(base_model, adapter_dir)

# 3. Fuse weights permanently
merged_model = model_with_adapter.merge_and_unload()

# 4. Save the merged model to disk
merged_model.save_pretrained("./final_custom_model")
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
tokenizer.save_pretrained("./final_custom_model")

print("Model successfully merged and saved for vLLM or Ollama deployment!")
```

---

## 🚀 Stage 3 — In Practice / Why It Matters

### The Three Legitimate Enterprise Use Cases for Fine-Tuning:
1. **Deterministic Syntax & Structured Extraction:**
   * An off-the-shelf 8B model will intermittently emit invalid Markdown, commentary, or unparsable JSON.
   * Fine-tuning on 1,000 clean samples achieves **99.9% syntax determinism**, matching GPT-4o reliability at 5% of the cost.
2. **Model Distillation (Cost Optimization):**
   * Use GPT-4o or Claude 3.7 to generate high-quality chain-of-thought solutions for 5,000 domain queries.
   * Fine-tune Llama 3.1 8B on these solutions. You get 90% of frontier model reasoning at **sub-cent local serving costs**.
3. **Domain Language & Proprietary Tool Calling:**
   * Teaching a model an internal enterprise query language or proprietary API parameters that were never present in open internet training data.

---

## ⚖️ Variations & Decision Table

| Method | VRAM Required (8B Model) | Training Speed | Trainable Params | Best For | Avoid When |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Prompt Engineering** | Zero (API) | Instant | 0% | General queries, prototyping, early MVPs. | Complex syntax errors persist; context length too high. |
| **RAG** | Vector DB only | Fast | 0% | Live company documents, dynamic policies, source citations. | Model needs to change its fundamental tone or syntax. |
| **QLoRA (4-bit)** | **~10–14 GB VRAM** | Moderate | ~0.1%–1% | **Enterprise standard.** Fine-tuning 8B models on a single GPU. | Ultra-low latency training required (4-bit dequantization adds ~15% overhead). |
| **LoRA (16-bit)** | **~24–32 GB VRAM** | Fast | ~0.1%–1% | Cloud GPUs (A10G, A100), fastest convergence with zero dequant overhead. | Limited GPU VRAM (< 20GB). |
| **Full Fine-Tuning** | **80–120+ GB VRAM** | Slow | 100% | Foundation model pre-training from scratch; massive multi-task alignment. | Almost all enterprise engineering tasks (waste of money and high forgetting risk). |

---

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| :--- | :--- | :--- |
| `torch.cuda.OutOfMemoryError` during training | Batch size too large or sequence length exceeding VRAM | Reduce `per_device_train_batch_size` to 1 or 2, increase `gradient_accumulation_steps`, and enable `optim="paged_adamw_8bit"`. |
| Model repeats prompt verbatim in output | Training loss computed over prompt tokens instead of only completions | Ensure `SFTTrainer` or data collator is using token masking (`DataCollatorForCompletionOnlyLM`). |
| Catastrophic forgetting (model forgets basic reasoning) | Learning rate too high, too many epochs, or training on a narrow dataset | Lower learning rate (`2e-4` $\rightarrow$ `5e-5`), stop at 2–3 epochs, and mix in 10% general instruction data. |
| Merging fails with `AttributeError` | Tried to call `merge_and_unload()` on a 4-bit quantized model | Load base model in `torch.float16` or `bfloat16` without `load_in_4bit=True` before merging. |
| Training loss goes to `NaN` | Exploding gradients due to high learning rate with 16-bit precision | Set `max_grad_norm=0.3`, verify no `NaN` values in dataset, and use `bf16=True` instead of `fp16`. |

---

## 📌 Quick Reference

```python
# 1. Essential QLoRA Imports
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 2. 4-bit Quantization Config (Runs 8B models on <=16GB VRAM)
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# 3. LoRA Configuration (Freeze base, train 0.5% weights)
lora = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM"
)

# 4. Standard ChatML Message Format (JSONL)
# {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

# 5. Merge Adapter into Base Model for Serving
# merged = peft_model.merge_and_unload()
```

---

## 🛑 STOP — Self-Check

A financial firm wants an AI system to query their quarterly earnings PDFs and generate answers matching their strict internal compliance disclosure format. 

The junior engineer says: *"We should fine-tune Llama 3 on our quarterly reports so it memorizes our earnings numbers."*

**As the AI Solutions Architect, what is wrong with this suggestion, and what architecture would you propose instead?**

<details><summary>Answer</summary>

### Why the Junior Engineer is Wrong:
1. **Fine-Tuning Does Not Reliably Store Factual Numbers:** Fine-tuning adjusts probability distributions over tokens; it frequently hallucinates specific numbers and cannot provide clickable citations back to the source document.
2. **Quarterly Reports Change Constantly:** Every time new earnings reports are released, the firm would have to re-train and re-deploy the model.
3. **Catastrophic Forgetting & Risk:** The model risks forgetting general financial reasoning.

### The Correct Architect Proposal:
A **Hybrid RAG + Fine-Tuning (or Prompt Engineering) Architecture**:
1. **RAG for the Facts:** Ingest the quarterly earnings PDFs into a Vector Store (e.g. pgvector with HNSW) and use hybrid search (BM25 + Cosine) to retrieve the exact, verifiable revenue figures.
2. **Fine-Tuning (LoRA) for the Compliance Style:** If standard few-shot prompting fails, fine-tune a small model (e.g., Llama 3.1 8B) on 500 examples of the **strict compliance disclosure format and syntax** only.
3. Feed the retrieved earnings numbers into the fine-tuned formatting model. Facts stay accurate and verifiable; formatting is 100% compliant.

🎉 **Lesson Complete!** Continue to the final module milestone: [05 Milestone — Full Production System →](05%20Milestone%20-%20Full%20Production%20System.md)

</details>
