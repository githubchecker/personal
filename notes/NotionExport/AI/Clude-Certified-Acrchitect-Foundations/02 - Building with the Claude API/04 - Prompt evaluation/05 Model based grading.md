# 05 — Model Based Grading

> Course 02 · Section 04 - Prompt evaluation · Lesson 5 of 6 · [← Prev: Running the Eval](04%20Running%20the%20eval.md) · [Course Index](../README.md) · [Next: Code Based Grading →](06%20Code%20based%20grading.md)

---

## 🗺️ Stage 0 — Concept Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      GRADER TAXONOMY & ARCHITECTURE                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌────────────────────┐   ┌────────────────────┐   ┌──────────────┐   │
│   │    CODE GRADERS    │   │   MODEL GRADERS    │   │ HUMAN GRADERS│   │
│   │  (Deterministic)   │   │  (LLM-as-a-Judge)  │   │  (Reference) │   │
│   ├────────────────────┤   ├────────────────────┤   ├──────────────┤   │
│   │ • Syntax parsing   │   │ • Task alignment   │   │ • Highest    │   │
│   │ • Length / RegEx   │   │ • Completeness     │   │   nuance     │   │
│   │ • Pure code speed  │   │ • Safety & tone    │   │ • Expensive, │   │
│   │ • Zero token cost  │   │ • Semantic nuances │   │   slow       │   │
│   └─────────┬──────────┘   └─────────┬──────────┘   └──────────────┘   │
│             │                        │                                 │
│             └───────────┬────────────┘                                 │
│                         ▼                                              │
│         ┌───────────────────────────────┐                              │
│         │ HYBRID PRODUCTION EVALUATION  │                              │
│         │ Code: Format & Syntax Invariants│                             │
│         │ Model: Semantic Task Following │                             │
│         └───────────────────────────────┘                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

In automated evaluation pipelines, the **Grader** transforms raw model generation into quantifiable telemetry. A grader takes the candidate output (and optionally the input task and ground-truth reference) and returns an objective quality signal—typically a numerical score from **1 to 10**, where 10 represents a flawless response and 1 represents complete failure.

Understanding when to employ **Code Graders**, **Model Graders (LLM-as-a-Judge)**, or **Human Reviewers** is a foundational architectural skill for designing reliable AI systems.

---

## 🔑 New Terms

| Term | One-Line Meaning |
| :--- | :--- |
| **Model-as-a-Judge** | An architectural pattern where an LLM is prompted to evaluate, critique, and score another model's outputs against a rubric. |
| **Code Grader** | A deterministic programmatic function that inspects outputs using code rules (e.g., regex, string parsing, AST compilers). |
| **Central Tendency Bias** | The empirical tendency of LLMs to output safe, middling scores (e.g., 5–7/10) when asked for immediate scalar ratings without required reasoning. |
| **Reasoning-First Scoring** | Structuring the grader prompt to generate qualitative evidence (strengths, weaknesses, rationale) *before* emitting the final numerical score. |
| **Evaluation Criteria** | The explicit dimensions of quality being measured (e.g., formatting compliance, syntax validity, task adherence). |

---

## 🎈 Stage 1 — The Simple Idea

### The Code Linter vs. The Staff Engineer
Imagine submitting a pull request in an enterprise software team:
1. **The Code Linter (Code Grader):** The automated CI system instantly checks formatting, imports, and syntax. It is fast, deterministic, and costs zero dollars. If a semicolon is missing or code doesn't parse, it fails immediately.
2. **The Senior Staff Engineer (Model Grader):** The staff engineer reads the code to understand its architectural purpose. Does it solve the business ticket? Does it handle concurrency safely? Is it maintainable? They write qualitative feedback ("Strengths", "Weaknesses") and assign a review decision.
3. **The Product Director (Human Grader):** Manually spot-checks critical features when high-stakes user experience decisions are debated.

### The "Aha!" Unlock
> **Why LLM judges fail without Chain of Thought:**  
> If you ask Claude: *"Rate this code from 1 to 10"*, it almost always gives a non-committal 6 or 7. Autoregressive models generate token-by-token; without writing out an explanation first, the model has not "thought" through the flaws before emitting the number. Forcing the grader to articulate **"strengths"**, **"weaknesses"**, and **"reasoning"** first unlocks accurate, calibrated scoring.

---

## ⚙️ Stage 2 — How It Actually Works

![Types of Graders](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623451%2F04_-_005_-_Model_Based_Grading_03.1748623451557.png)

### 1. The Three Approaches to Grading

| Dimension | Code Graders | Model Graders | Human Graders |
| :--- | :--- | :--- | :--- |
| **Mechanism** | Programmatic scripts (Python/regex) | Secondary Claude API invocation | Manual human review |
| **Speed** | Sub-millisecond | 1–3 seconds per call | Hours to days |
| **Cost** | $0.00 (Local compute) | API token costs | High engineering labor cost |
| **Determinism** | 100% reproducible | Slight variance (controlled via temp=0) | High subjective variance |
| **Best Used For** | Syntax, format, length, regex | Reasoning, helpfulness, instruction following | Gold-standard benchmark validation |

---

### 2. Defining Evaluation Criteria for Code Generation

Before writing grader code, architects must define the exact dimensions of quality. For our AWS technical assistant prompt, we isolate three criteria:

![Defining Evaluation Criteria](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623452%2F04_-_005_-_Model_Based_Grading_06.1748623452682.png)

1. **Format:** Output must strictly contain only Python, JSON, or Regex—with **zero introductory conversational banter, markdown fencing, or postscripts**.
2. **Valid Syntax:** The generated artifact must be syntactically valid (parses via `ast.parse()`, `json.loads()`, or `re.compile()`).
3. **Task Following:** The solution must accurately and comprehensively address the specific technical requirements of the user's task.

![Assigning Graders to Criteria](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623453%2F04_-_005_-_Model_Based_Grading_07.1748623453532.png)

#### The Division of Labor:
- **Criteria 1 & 2 (Format & Syntax):** Best suited for **Code Graders**. Using an LLM to check if brackets match is wasteful and non-deterministic; code compilers check syntax definitively in microseconds.
- **Criteria 3 (Task Following):** Best suited for **Model Graders**. Evaluating whether Boto3 correctly handles S3 pagination or whether an IAM policy grants minimal privilege requires deep semantic comprehension.

---

### 3. Implementing the Model Grader

The `grade_by_model()` function constructs a structured evaluation prompt, requests structured JSON critique, and leverages assistant prefilling for 100% reliable parsing:

```python
def grade_by_model(test_case: dict, output: str) -> dict:
    """
    Evaluates model output using Claude as an expert code reviewer.
    Enforces reasoning-first scoring via structured JSON schema.
    """
    eval_prompt = f"""
You are an expert code reviewer. Evaluate this AI-generated solution.

Task: {test_case["task"]}
Solution: {output}

Provide your evaluation as a structured JSON object with:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement  
- "reasoning": A concise explanation of your assessment
- "score": A number between 1-10
"""
    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    
    # Halt on closing fence for clean JSON extraction
    eval_text = chat(messages, stop_sequences=["```"])
    return json.loads(eval_text.strip())
```

#### Why the JSON Schema Order Matters:
Notice the ordering of keys in the prompt:
1. `"strengths"` $\to$ 2. `"weaknesses"` $\to$ 3. `"reasoning"` $\to$ 4. `"score"`

Because Claude generates JSON top-to-bottom, forcing the model to articulate the specific technical deficiencies *before* outputting the integer `"score"` eliminates the **Central Tendency Bias** and produces highly differentiated scores (e.g., giving 3s to hallucinated answers and 10s to clean code).

---

### 4. Integrating the Grader into the Evaluation Harness

We update `run_test_case()` to invoke `grade_by_model()`, unpacking the score and diagnostic reasoning:

```python
def run_test_case(test_case):
    """Calls run_prompt, then grades the result using the Model Grader"""
    output = run_prompt(test_case)
    
    # Grade the output using Claude
    model_grade = grade_by_model(test_case, output)
    score = model_grade["score"]
    reasoning = model_grade["reasoning"]
    
    return {
        "test_case": test_case,
        "output": output, 
        "score": score,
        "reasoning": reasoning,
        "strengths": model_grade.get("strengths", []),
        "weaknesses": model_grade.get("weaknesses", [])
    }
```

---

### 5. Computing the Benchmark Mean

In `run_eval()`, we calculate the arithmetic mean across all test cases using Python's `statistics.mean`:

```python
from statistics import mean

def run_eval(dataset):
    results = []
    
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)
    
    # Calculate objective baseline metric
    average_score = mean([result["score"] for result in results])
    print(f"\n==========================================")
    print(f"EVALUATION COMPLETE | Average Score: {average_score:.2f} / 10.0")
    print(f"==========================================\n")
    
    return results
```

---

## 🚀 Stage 3 — In Practice: Full Production Pipeline

Here is the complete, runnable Python evaluation harness incorporating dataset loading, model inference, model grading, and structured telemetry logging:

```python
import json
from statistics import mean
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

MODEL_APP = "claude-3-5-haiku-20241022"    # Candidate model being evaluated
MODEL_JUDGE = "claude-3-5-haiku-20241022"  # Evaluator model

def add_user_message(messages: list, text: str):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages: list, text: str):
    messages.append({"role": "assistant", "content": text})

def chat(messages: list, model: str = MODEL_APP, temperature: float = 0.0, stop_sequences: list = None) -> str:
    params = {
        "model": model,
        "max_tokens": 1000,
        "temperature": temperature,
        "messages": messages
    }
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
        
    response = client.messages.create(**params)
    return response.content[0].text

def run_prompt(test_case: dict) -> str:
    """Tier 1: Executes the candidate prompt template."""
    prompt = f"Please solve the following task:\n\n{test_case['task']}"
    messages = []
    add_user_message(messages, prompt)
    return chat(messages, model=MODEL_APP, temperature=0.0)

def grade_by_model(test_case: dict, output: str) -> dict:
    """Tier 2 Grader: Evaluates solution using model-as-a-judge."""
    eval_prompt = f"""
You are an expert cloud architect and code reviewer. Evaluate this AI-generated AWS solution.

Task: {test_case['task']}
Solution: {output}

Evaluation Rubric:
- Accuracy: Does the code correctly solve the AWS requirement?
- Format: Did it provide clean code without unnecessary conversational filler?
- Quality: Is it secure, production-ready, and idiomatic?

Provide your evaluation as a structured JSON object with:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your assessment
- "score": An integer number between 1 and 10
"""
    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    
    raw_eval = chat(messages, model=MODEL_JUDGE, temperature=0.0, stop_sequences=["```"])
    return json.loads(raw_eval.strip())

def run_test_case(test_case: dict) -> dict:
    """Tier 2 Orchestrator: Runs prompt and grades output."""
    output = run_prompt(test_case)
    grade = grade_by_model(test_case, output)
    
    return {
        "test_case": test_case,
        "output": output,
        "score": grade["score"],
        "reasoning": grade["reasoning"],
        "strengths": grade.get("strengths", []),
        "weaknesses": grade.get("weaknesses", [])
    }

def run_eval(dataset: list) -> list:
    """Tier 3 Batch Coordinator: Iterates through dataset and computes benchmark mean."""
    print(f"🔬 Running evaluation across {len(dataset)} test cases...")
    results = []
    
    for idx, test_case in enumerate(dataset, start=1):
        print(f"  [{idx}/{len(dataset)}] Evaluating: {test_case.get('task', '')[:40]}...")
        result = run_test_case(test_case)
        print(f"       -> Score: {result['score']}/10 | Reason: {result['reasoning'][:60]}...")
        results.append(result)
        
    avg_score = mean([r["score"] for r in results])
    print(f"\n📈 Final Benchmark Baseline: {avg_score:.2f} / 10.0")
    return results

if __name__ == "__main__":
    with open("dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    results = run_eval(dataset)
    
    with open("eval_results_model_graded.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
```

---

## ⚖️ Variations & When to Use

| Grading Pattern | Architecture | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| **Direct Scoring Rubric** (Used here) | Single prompt returning 1–10 score with reasoning. | Fast, flexible, provides explanatory feedback. | Susceptible to judge model calibration drift. |
| **Reference-Guided Grading** | Prompt includes input + output + *human golden answer*. | Highly accurate ground-truth comparison. | Requires expensive pre-authored reference answers for every test case. |
| **Pairwise Comparison (Elo)** | Judge compares `Output A` vs. `Output B` head-to-head. | Eliminates numerical score anchoring; high human agreement. | Requires $O(N^2)$ comparisons; computationally expensive. |

---

## 🐛 Common Errors & Anti-Patterns

| Anti-Pattern | Root Cause | Architectural Remediation |
| :--- | :--- | :--- |
| **Immediate Score Prompting** | Asking for `"score": 10` before asking for `"reasoning"`. | **Always require reasoning first.** Autoregressive tokens generate sequentially; reasoning forces the model to deliberate before scoring. |
| **Using LLMs for Deterministic Checks** | Prompting an LLM to check if JSON syntax parses correctly. | Use a **Code Grader** (`json.loads()`). Never pay LLM tokens or accept non-deterministic risk for checks a compiler executes in 5 microseconds. |
| **Unanchored Rubrics** | Asking *"Is this good?"* without explicit evaluation guidelines. | Provide explicit criteria (e.g., accuracy, formatting, completeness) in the judge prompt. |
| **Judge Position Bias** | In pairwise comparisons, models preferring the first option. | Randomize output ordering when comparing two candidate prompts head-to-head. |

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   MODEL-AS-A-JUDGE BEST PRACTICES                      │
├───────────────────────┬────────────────────────────────────────────────┤
│ 1. Schema Ordering    │ strengths -> weaknesses -> reasoning -> score  │
│ 2. Prefill Extraction │ Assistant prefill "```json" + stop seq ["```"] │
│ 3. Temperature        │ Always set `temperature=0.0` for evaluation    │
│ 4. Separation of Labor│ Code graders for syntax; LLMs for semantics    │
│ 5. Aggregation        │ Compute `statistics.mean([r["score"] ...])`    │
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check

### Question 1
Why does requesting `"strengths"`, `"weaknesses"`, and `"reasoning"` prior to the `"score"` integer in the model grader JSON schema significantly improve scoring reliability?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because it enforces **Chain-of-Thought (CoT) reasoning** within autoregressive generation.  
Claude produces tokens sequentially from left to right. If forced to emit the numerical score first, the model has zero deliberation context and defaults to safe, middling numbers (e.g., 6 or 7). Requiring it to articulate specific technical strengths and flaws first grounds the final score token in its own recorded critique.
</details>

---

### Question 2
An engineer wants to evaluate whether an AI-generated SQL query has valid syntax. They propose writing a model grader with Claude 3.5 Sonnet to check the syntax. Is this an optimal architectural design?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** **No, this is an architectural anti-pattern.**  
Validating syntax is a deterministic problem that should be delegated to a **Code Grader** (e.g., using a SQL parser library like `sqlglot` or executing `EXPLAIN` against a test database). Code graders run in microseconds, cost $0.00 in API tokens, and provide 100% deterministic true/false answers without hallucination risk.
</details>
