# 04 — Running the Eval

> Course 02 · Section 04 - Prompt evaluation · Lesson 4 of 6 · [← Prev: Generating Test Datasets](03%20Generating%20test%20datasets.md) · [Course Index](../README.md) · [Next: Model Based Grading →](05%20Model%20based%20grading.md)

---

## 🗺️ Stage 0 — Concept Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   3-TIER EVALUATION RUNNER PIPELINE                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  TIER 3: BATCH COORDINATOR                                     │   │
│   │  `run_eval(dataset)`                                           │   │
│   │  • Loads dataset.json                                          │   │
│   │  • Iterates over test cases                                    │   │
│   │  • Collects and aggregates results array                       │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │ for each test_case                 │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  TIER 2: SINGLE-CASE ORCHESTRATOR                              │   │
│   │  `run_test_case(test_case)`                                    │   │
│   │  • Calls run_prompt()                                          │   │
│   │  • Dispatches response to Grader (Score 1-10)                  │   │
│   │  • Packages structured result: {test_case, output, score}      │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │ calls                              │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  TIER 1: TEMPLATE & API EXECUTOR                               │   │
│   │  `run_prompt(test_case)`                                       │   │
│   │  • Interpolates task into prompt template                      │   │
│   │  • Invokes Claude API (messages.create)                        │   │
│   │  • Returns raw model generation string                         │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

With an evaluation dataset persisted to disk, the next engineering milestone is constructing the **Evaluation Pipeline Harness**. This harness coordinates taking each test input, injecting it into candidate prompt templates, executing the inference request through Claude, scoring the output, and persisting telemetry for analysis.

Designing this pipeline using a clean **three-tier modular architecture** ensures that prompt authoring, model inference, and grading logic remain strictly decoupled.

---

## 🔑 New Terms

| Term | One-Line Meaning |
| :--- | :--- |
| **Evaluation Harness (Runner)** | The software coordination pipeline that loads datasets, executes prompt variants, scores outputs, and logs metrics. |
| **Three-Tier Runner Architecture** | Decoupling the evaluation pipeline into prompt formatting (`run_prompt`), case scoring (`run_test_case`), and batch iteration (`run_eval`). |
| **Execution Record** | The standardized JSON telemetry object (`{"test_case": ..., "output": ..., "score": ...}`) logged for every evaluated sample. |
| **Scoring Stub (Placeholder)** | A temporary static value (e.g., `score = 10`) used to validate pipeline mechanics before plugging in active grading engines. |
| **Evaluation Latency** | The cumulative wall-clock time required to process an evaluation batch across API roundtrips. |

---

## 🎈 Stage 1 — The Simple Idea

### The Quality Control Assembly Line
Think of a high-tech manufacturing facility with three dedicated roles:
1. **The Machine Operator (`run_prompt`):** Takes a raw metal part from the cart, feeds it into the CNC lathe (Claude), and collects the machined part.
2. **The Quality Inspector (`run_test_case`):** Inspects the finished part against specifications, stamps a quality rating on an inspection card, and attaches it to the part.
3. **The Plant Floor Supervisor (`run_eval`):** Wheels the entire cart of raw parts to the line, tracks all parts through inspection, and tallies the final shipment report.

### The "Aha!" Unlock
> **Do not write monolithic evaluation scripts.**  
> If you combine file loading, template string interpolation, API calls, and grading assertions inside a single giant `for` loop, modifying a prompt template or testing an alternative grader requires rewriting your test harness. Separating these three concerns makes prompt experimentation completely modular.

---

## ⚙️ Stage 2 — How It Actually Works

![Running the Evaluation Overview](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623396%2F04_-_004_-_Running_the_Eval_00.1748623396420.png)

The evaluation runner is structured into three discrete functions:

---

### Tier 1: The `run_prompt` Function

The lowest-level function is solely responsible for merging the input task with the candidate prompt template and dispatching it to Claude:

```python
def run_prompt(test_case):
    """Merges the prompt and test case input, then returns the result"""
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""
    messages = []
    add_user_message(messages, prompt)
    output = chat(messages)
    return output
```

#### Architectural Note:
Notice how sparse this baseline prompt is. It contains zero output format specifications, zero instructions on XML tags, and no constraints on introductory fluff. As a result, Claude defaults to conversational helpfulness—which will provide the ideal baseline for our evaluation grader to critique.

---

### Tier 2: The `run_test_case` Function

The orchestrator function evaluates a single test case by invoking `run_prompt()`, passing the raw generation to the grader, and packaging the result into a standardized record:

```python
def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)
    
    # Placeholder: Will be replaced with automated grading logic
    score = 10
    
    return {
        "output": output,
        "test_case": test_case,
        "score": score
    }
```

By packaging both the input `test_case` and the model `output` alongside the `score`, developers have complete traceability to diagnose *why* a prompt failed without having to re-run the API request.

---

### Tier 3: The `run_eval` Function

The top-level batch coordinator iterates through every record in the dataset and aggregates results:

```python
def run_eval(dataset):
    """Loads the dataset and calls run_test_case with each case"""
    results = []
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)
    return results
```

---

### Executing the Evaluation

To execute the pipeline, we load the frozen `dataset.json` file and trigger the evaluation:

```python
with open("dataset.json", "r") as f:
    dataset = json.load(f)

results = run_eval(dataset)
```

> [!NOTE]
> **Sequential Runtime Expectations:**  
> When executing test cases sequentially over synchronous HTTP requests, each invocation takes 1–3 seconds. Evaluating even a modest dataset of 10–20 test cases will take 20–60 seconds. For enterprise suites with hundreds of cases, asynchronous concurrency or the Anthropic Message Batches API is recommended.

---

### Examining the Output Telemetry

Printing the structured results reveals exactly how Claude performed on each task:

```python
print(json.dumps(results, indent=2))
```

![Examining Evaluation Results](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623397%2F04_-_004_-_Running_the_Eval_18.1748623397308.png)

Each evaluation record contains:
1. **`test_case`**: The input task definition.
2. **`output`**: The complete, unedited text returned by Claude.
3. **`score`**: The numerical evaluation rating.

---

### Diagnosing the Baseline Flaw

Inspecting Claude's responses reveals the exact flaw in our baseline prompt:

![Verbose Claude Output Analysis](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623397%2F04_-_004_-_Running_the_Eval_01.1748623397839.png)

When asked to provide a Python function or EventBridge rule, Claude outputs:
```text
Here is the Python function using boto3 to upload a file to S3:

```python
import boto3

def upload_file_to_s3(file_name, bucket, object_name=None):
    ...
```

This function creates an S3 client and uploads the specified file...
```

**The Architectural Problem:** Claude wraps the code in conversational preambles (*"Here is the Python function..."*) and adds explanatory postscripts. In automated workflows or code generation tools, this conversational fluff breaks downstream compilers and parsers.

The hardcoded `score = 10` masks this flaw. In the upcoming lessons, we will replace this placeholder with **model-based and code-based graders** that automatically detect and penalize this verbosity.

---

## 🚀 Stage 3 — In Practice: Production-Grade Harness

Below is an enterprise-hardened implementation incorporating error handling, latency timing, and automated disk persistence:

```python
import json
import time
from typing import List, Dict, Any
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-3-5-haiku-20241022"

def add_user_message(messages: list, text: str):
    messages.append({"role": "user", "content": text})

def chat(messages: list, temperature: float = 0.0) -> str:
    """Executes Claude API with temperature=0.0 for deterministic evaluation."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=temperature,
        messages=messages
    )
    return response.content[0].text

def run_prompt(test_case: Dict[str, Any]) -> str:
    """Tier 1: Formats the candidate prompt and executes model inference."""
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

def run_test_case(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Tier 2: Orchestrates single case execution, timing, and score packaging."""
    start_time = time.perf_counter()
    
    try:
        output = run_prompt(test_case)
        status = "SUCCESS"
    except Exception as e:
        output = f"ERROR: {str(e)}"
        status = "FAILED"
        
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    # Temporary placeholder score (to be replaced by active grader)
    score = 10 if status == "SUCCESS" else 0
    
    return {
        "test_case": test_case,
        "output": output,
        "score": score,
        "latency_ms": duration_ms,
        "status": status
    }

def run_eval(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Tier 3: Coordinates dataset batch execution and telemetry collection."""
    print(f"🚀 Starting evaluation run across {len(dataset)} test cases...")
    results = []
    
    for idx, test_case in enumerate(dataset, start=1):
        print(f"  [{idx}/{len(dataset)}] Evaluating: {test_case.get('task', '')[:45]}...")
        result = run_test_case(test_case)
        results.append(result)
        
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)
    print(f"\n✅ Evaluation complete! Avg Score: {avg_score:.1f}/10 | Avg Latency: {avg_latency:.1f}ms")
    return results

if __name__ == "__main__":
    with open("dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    eval_results = run_eval(dataset)
    
    # Save full telemetry to disk for downstream grader development
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
```

---

## ⚖️ Variations & When to Use

| Execution Strategy | Architecture | Latency / Throughput | Best Suited For |
| :--- | :--- | :--- | :--- |
| **Sequential Execution** (`for` loop) | Synchronous HTTP calls per test case | Slow ($O(N \times \text{RTT})$); ~30s for 10 items | Local development, debugging, initial scaffold testing |
| **Asynchronous Concurrency** (`asyncio`) | Concurrent coroutines with semaphore rate-limiting | High speed; 10 items in ~3–5s | CI/CD pipelines, interactive test suites |
| **Anthropic Message Batches API** | Async cloud batch processing | Detached; 50% discount on API costs | Massive regression suites (1,000+ items), overnight benchmarks |

---

## 🐛 Common Errors & Anti-Patterns

| Anti-Pattern | Root Cause | Architectural Remediation |
| :--- | :--- | :--- |
| **Discarding the Raw Output** | Storing only the numeric score in results to save memory. | **Always preserve the raw `output` string.** Without the output, you cannot inspect why a prompt received a low grade or calibrate your grader. |
| **Monolithic Function Design** | Merging prompt templating, API calls, and grading into one giant block. | Maintain clean separation across `run_prompt()`, `run_test_case()`, and `run_eval()`. |
| **Crashing on Single API Failures** | Lacking `try/except` around the API call in `run_test_case`. | Wrap inference calls so transient network glitches log an error status without aborting the rest of the batch. |
| **Premature Score Optimization** | Trying to tweak prompts before replacing the `score = 10` stub with real grading logic. | Build the grader first; you cannot optimize prompt performance against a hardcoded placeholder. |

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     EVALUATION HARNESS RESPONSIBILITIES                │
├─────────────────────┬──────────────────────────────────────────────────┤
│ `run_prompt`        │ Injects task into template -> invokes Claude API │
│ `run_test_case`     │ Calls `run_prompt` -> calls Grader -> logs record│
│ `run_eval`          │ Loads dataset -> iterates cases -> aggregates    │
│ Result Schema       │ `{"test_case": ..., "output": ..., "score": ...}`│
└─────────────────────┴──────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check

### Question 1
Why is it essential that `run_test_case()` returns an object containing the full raw `output` text from Claude, rather than just returning the numerical `score`?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because the raw output provides the **diagnostic evidence** needed to improve the prompt and calibrate the grader.  
If an eval yields a score of 4/10, an engineer cannot diagnose whether the deduction was caused by incorrect code logic, excessive conversational fluff, or a grader hallucination without inspecting the exact generated text.
</details>

---

### Question 2
In the initial baseline run, why did Claude generate verbose explanations and markdown code blocks even though our desired architectural outcome is raw, clean code/JSON?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because the baseline prompt template (`Please solve the following task:\n{task}`) contained **zero formatting constraints or negative constraints**. Claude's default conversational pre-training encourages polite greetings, markdown framing, and explanatory postscripts unless explicitly instructed otherwise or steered via prefilling.
</details>
