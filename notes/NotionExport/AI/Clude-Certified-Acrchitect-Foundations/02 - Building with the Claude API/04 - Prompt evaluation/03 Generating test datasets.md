# 03 — Generating Test Datasets

> Course 02 · Section 04 - Prompt evaluation · Lesson 3 of 6 · [← Prev: A Typical Eval Workflow](02%20A%20typical%20eval%20workflow.md) · [Course Index](../README.md) · [Next: Running the Eval →](04%20Running%20the%20eval.md)

---

## 🗺️ Stage 0 — Concept Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│               SYNTHETIC TEST DATASET GENERATION PIPELINE               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌───────────────────────────┐                                        │
│   │ Dataset Generator Prompt  │ ──► Specifies target domains:          │
│   │ (Constraints & Few-Shot)  │     AWS Python, JSON, & Regex tasks    │
│   └─────────────┬─────────────┘                                        │
│                 │                                                      │
│                 ▼                                                      │
│   ┌───────────────────────────┐                                        │
│   │ Claude 3.5 Haiku Engine   │ ──► High speed, ultra-low cost,        │
│   │ (Fast Generator Model)    │     optimal for creative data synth    │
│   └─────────────┬─────────────┘                                        │
│                 │                                                      │
│                 ▼                                                      │
│   ┌───────────────────────────┐                                        │
│   │ Assistant Prefilling &    │ ──► Prefills "```json",                │
│   │ Stop Sequences            │     stops on "```" for 100% clean JSON │
│   └─────────────┬─────────────┘                                        │
│                 │                                                      │
│                 ▼                                                      │
│   ┌───────────────────────────┐                                        │
│   │   Disk Persistence        │ ──► Saves to `dataset.json`            │
│   │   (Frozen Benchmark)      │     (Guarantees baseline consistency)  │
│   └───────────────────────────┘                                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

Building an automated evaluation suite requires test data. In many production engineering scenarios, you face a **cold-start problem**: you are building a new application and do not yet have historical user traffic or production query logs to test against.

Instead of handcrafting hundreds of test cases in spreadsheets, architects leverage **synthetic dataset generation**—using Claude to generate structured, realistic, and domain-specific test datasets that can be frozen to disk and reused as permanent regression benchmarks.

---

## 🔑 New Terms

| Term | One-Line Meaning |
| :--- | :--- |
| **Synthetic Dataset** | Artificially generated test records created by an LLM to simulate real-world query distributions. |
| **Cold-Start Evaluation** | Designing an evaluation benchmark before real-world user logs or historical traffic exist. |
| **Task Schema** | The structured JSON contract defining the fields in an evaluation record (e.g., `{"task": "..."}`). |
| **Model Sizing for Evals** | Architecturally selecting a smaller, faster model (e.g., Claude 3.5 Haiku) for high-volume data generation to reduce costs and latency. |
| **Dataset Persistence** | Serializing the generated test records to disk (e.g., `dataset.json`) to guarantee a static, repeatable benchmark across prompt versions. |

---

## 🎈 Stage 1 — The Simple Idea

### The Flight Simulator Scenario Generator
When aeronautical engineers train commercial pilots or test autopilot software, they don't wait for actual catastrophic thunderstorms or dual engine flameouts to occur during revenue flights. 

Instead, they use a **scenario generator** to programmatically inject hundreds of synthetic challenges: crosswinds at Denver, icing at Chicago, sensor failures over the Rockies. 

Synthetic test dataset generation does the exact same thing for LLMs:
- Rather than waiting for production users to expose prompt flaws with edge cases,
- You instruct a generator model to synthesize a battery of diverse, challenging, and realistic tasks.
- You freeze those tasks into a test suite and evaluate your system before a single user touches it.

### The "Aha!" Unlock
> **Generating evaluation datasets manually does not scale; generating them dynamically on every run invalidates your baseline.**  
> The architectural sweet spot is using Claude (specifically Haiku) to synthesize your dataset *once*, validating its quality, and persisting it to `dataset.json` as your frozen, immutable benchmark.

---

## ⚙️ Stage 2 — How It Actually Works

### 1. Setting Up the Goal: The AWS Code Assistant

We are building and evaluating a prompt that assists cloud engineers in generating AWS-specific technical solutions across three specific output formats:

1. **Python code** (e.g., Boto3 automation scripts, Lambda functions)
2. **JSON configuration files** (e.g., IAM policies, EventBridge rules, CloudFormation snippets)
3. **Regular expressions** (e.g., S3 bucket name validation, ARN pattern matching)

![Setting Up the Goal](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623393%2F04_-_003_-_Generating_Test_Datasets_01.1748623392676.png)

#### Architectural Requirement
When a user submits a task, the system must return **pure, clean output** matching one of these formats—without introductory banter, explanatory paragraphs, or conversational footers.

#### Baseline Prompt (Version 1)
Our starting template is intentionally basic:

```python
prompt = f"""
Please provide a solution to the following task:
{task}
"""
```

---

### 2. Structuring the Evaluation Dataset Schema

The evaluation dataset consists of an array of JSON objects, where each object contains a `"task"` property describing the problem to be solved:

```json
[
  {
    "task": "Write an AWS EventBridge rule as JSON that matches EC2 instance stop events."
  },
  {
    "task": "Write a Python function using boto3 that uploads a local file to an S3 bucket."
  },
  {
    "task": "Write a regular expression that validates whether an AWS S3 bucket name complies with naming rules."
  }
]
```

![Creating an Evaluation Dataset](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623393%2F04_-_003_-_Generating_Test_Datasets_05.1748623393811.png)

---

### 3. Model Sizing: Why Use Haiku for Dataset Generation?

When generating synthetic evaluation datasets, architects prioritize **throughput, creativity, and cost**:
- **Sonnet / Opus:** Excellent for complex reasoning and final application execution, but more expensive for bulk generation of simple task prompts.
- **Claude 3.5 Haiku:** Near-instantaneous response times, negligible token cost, and outstanding creative diversity. It is the optimal choice for synthesizing dozens or hundreds of evaluation test cases.

---

### 4. Clean Extraction via Assistant Prefilling & Stop Sequences

To ensure the generated dataset can be ingested cleanly via `json.loads()` without brittle markdown regex stripping, we apply the pattern mastered in Section 03:
1. **User Prompt:** Defines the schema and domain constraints.
2. **Assistant Prefill:** Injects ```` ```json ```` into the assistant turn.
3. **Stop Sequence:** Configures `stop_sequences=["```"]` to immediately halt generation when the JSON array closes.

```python
messages = []
add_user_message(messages, prompt)
add_assistant_message(messages, "```json")

# Generation stops at closing fence; returned text is 100% valid JSON
raw_json = chat(messages, stop_sequences=["```"])
dataset = json.loads(raw_json)
```

---

## 🚀 Stage 3 — In Practice: Complete Implementation

Here is the complete, runnable Python script for synthesizing and persisting an AWS evaluation dataset:

```python
import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Configure Haiku for fast, low-cost dataset synthesis
MODEL = "claude-3-5-haiku-20241022"

def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages, system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": MODEL,
        "max_tokens": 1500,
        "messages": messages,
        "temperature": temperature
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    
    response = client.messages.create(**params)
    return response.content[0].text

def generate_dataset(num_records: int = 3) -> list:
    """
    Synthesizes a structured evaluation dataset for AWS tasks.
    Uses assistant prefilling and stop sequences for guaranteed clean JSON.
    """
    prompt = f"""
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects, each representing a task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {{
    "task": "Description of task"
  }}
]
```

Guidelines:
* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex.
* Focus on tasks that do not require writing excessive code.
* Ensure a balanced mix of Python (Boto3), JSON (IAM/CloudFormation/EventBridge), and Regex (ARNs/S3 names).

Please generate exactly {num_records} objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    
    raw_text = chat(messages, stop_sequences=["```"], temperature=0.8)
    return json.loads(raw_text.strip())

# 1. Generate the dataset
dataset = generate_dataset(num_records=3)
print("Generated Dataset Successfully:")
print(json.dumps(dataset, indent=2))

# 2. Persist the frozen dataset to disk
dataset_filepath = "dataset.json"
with open(dataset_filepath, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print(f"\nPersisted {len(dataset)} records to {dataset_filepath} as frozen benchmark.")
```

---

## ⚖️ Variations & When to Use

| Dataset Source | Speed / Cost | Realism & Diversity | Best Suited For |
| :--- | :---: | :---: | :--- |
| **Synthetic Generation (Haiku)** | Instant / Pennies | High variety, but may reflect LLM distribution biases. | **Cold-start applications**, initial benchmark bootstrapping, edge-case expansion. |
| **Anonymized Production Logs** | Slow / Engineering pipeline required | 100% authentic real-world customer usage patterns. | **Mature production systems**, regression detection against actual customer bugs. |
| **Subject-Matter Expert (SME) Handcrafted** | Slow / High human labor cost | Deep domain edge cases and nuanced business logic. | **High-stakes compliance, legal, medical, and security systems**. |
| **Hybrid (Recommended)** | Balanced | Comprehensive coverage. | Bootstrap synthetically with Haiku, then continuously enrich with failing production logs. |

---

## 🐛 Common Errors & Anti-Patterns

| Anti-Pattern | Root Cause | Architectural Remediation |
| :--- | :--- | :--- |
| **Re-generating Datasets on Every Run** | Calling `generate_dataset()` inside the test runner before each eval. | **Persist once to `dataset.json`.** Re-generating inputs introduces random variance, making it impossible to distinguish between prompt improvements and dataset shifts. |
| **Parse Failures on Markdown Bloat** | Forgetting assistant prefill, causing Claude to output ```` ```json ```` with introductory commentary. | Always use `add_assistant_message(messages, "```json")` and `stop_sequences=["```"]` for zero-regex parsing. |
| **Over-Clustered Synthetic Data** | Prompts asking for test data without formatting guidelines, leading to repetitive questions. | Provide clear categorization guidelines (e.g., *"mix of Python, JSON, and Regex"* or specific AWS services). |
| **Using Opus/Sonnet for Bulk Synth** | Using premium tier models for basic synthetic prompt generation. | Route synthetic dataset generation to **Claude 3.5 Haiku** to save 80%+ on token costs with faster execution. |

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   SYNTHETIC DATASET GOLDEN RULES                       │
├───────────────────────┬────────────────────────────────────────────────┤
│ 1. Model Selection    │ Use Claude 3.5 Haiku (Speed + Cost efficiency) │
│ 2. Clean JSON Format  │ Assistant prefill "```json" + stop seq ["```"] │
│ 3. Domain Framing     │ Explicitly constrain scope (e.g. AWS, length)  │
│ 4. Golden Rule        │ Save to `dataset.json` — NEVER re-synth per run│
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check

### Question 1
Why is it considered a major architectural defect to call `dataset = generate_dataset()` dynamically inside your prompt evaluation test runner instead of reading from a persisted `dataset.json` file?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Calling `generate_dataset()` dynamically creates a brand new set of test questions on every single test execution. If you evaluate Prompt V1 on Dataset A and Prompt V2 on Dataset B, you cannot determine whether a score difference was caused by your prompt improvements or because Dataset B happened to contain easier or harder questions. A benchmark dataset must be **frozen and deterministic**.
</details>

---

### Question 2
In the dataset generation pipeline, what is the architectural benefit of using Claude 3.5 Haiku rather than Claude 3.5 Sonnet?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** **Latency and Cost Efficiency.**  
Generating synthetic datasets often requires producing hundreds of candidate records. Claude 3.5 Haiku provides near-instantaneous inference speeds at a fraction of the token cost of Sonnet, while possessing more than sufficient linguistic creativity and instruction adherence to generate realistic evaluation prompts.
</details>
