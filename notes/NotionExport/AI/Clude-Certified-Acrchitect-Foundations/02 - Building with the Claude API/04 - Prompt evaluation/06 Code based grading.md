# 06 — Code Based Grading

> Course 02 · Section 04 - Prompt evaluation · Lesson 6 of 6 · [← Prev: Model Based Grading](05%20Model%20based%20grading.md) · [Course Index](../README.md) · [Next: Prompt Engineering →](../05%20-%20Prompt%20engineering%20techniques/01%20Prompt%20engineering.md)

---

## 🗺️ Stage 0 — Concept Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   HYBRID COMPOSITE EVALUATION PIPELINE                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                       Test Case & Model Output                         │
│                                   │                                    │
│                 ┌─────────────────┴─────────────────┐                  │
│                 ▼                                   ▼                  │
│   ┌───────────────────────────┐       ┌───────────────────────────┐    │
│   │    CODE-BASED GRADER      │       │     MODEL-BASED GRADER    │    │
│   │    (Technical Correctness)│       │    (Semantic Alignment)   │    │
│   ├───────────────────────────┤       ├───────────────────────────┤    │
│   │ Inspect `format` field:   │       │ Prompt Claude Judge:      │    │
│   │ • "json"   -> json.loads  │       │ • Strengths & Weaknesses  │    │
│   │ • "python" -> ast.parse   │       │ • Reasoning               │    │
│   │ • "regex"  -> re.compile  │       │ • Task compliance         │    │
│   │ Score: 0 or 10            │       │ Score: 1 to 10            │    │
│   └─────────────┬─────────────┘       └─────────────┬─────────────┘    │
│                 │                                   │                  │
│                 └─────────────────┬─────────────────┘                  │
│                                   ▼                                    │
│                   ┌───────────────────────────────┐                    │
│                   │   COMPOSITE SCORER (Weighted) │                    │
│                   │ Score = (Model + Syntax) / 2  │                    │
│                   └───────────────────────────────┘                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

When evaluating AI applications that generate structured artifacts—such as Python scripts, JSON configuration files, or regular expressions—subjective semantic grading is only half the battle. A response may sound fluent and relevant, but if it fails to compile or breaks downstream parsers, the application fails in production.

**Code-based grading** introduces fast, 100% deterministic, and zero-cost programmatic assertions to verify syntax validity and format compliance. Combining code-based graders with model-based graders creates a **Hybrid Evaluation Architecture** that measures both technical correctness and semantic task alignment.

---

## 🔑 New Terms

| Term | One-Line Meaning |
| :--- | :--- |
| **Code-Based Grader** | A deterministic programmatic function that tests outputs against formal grammars (e.g., AST parsers, JSON decoders, regex compilers). |
| **AST (Abstract Syntax Tree) Parsing** | Using Python's native `ast.parse()` to safely verify whether code is syntactically valid in memory without executing it. |
| **Dataset Schema Extension** | Enriching test records with target metadata (e.g., `"format": "python"`) to enable dynamic grader routing. |
| **Generic Code Prefill** | Using an assistant prefill like ```` ```code ```` to steer Claude into raw code emission when the specific language varies per request. |
| **Composite (Hybrid) Score** | A weighted mathematical combination of deterministic code scores and semantic LLM scores (e.g., $\frac{\text{Model} + \text{Syntax}}{2}$). |

---

## 🎈 Stage 1 — The Simple Idea

### The Hydraulic Pressure Sensor vs. The Flight Instructor
Imagine a commercial aviation flight simulator exam:
1. **The Automated Pressure Sensor (Code Grader):** When the pilot deploys the landing flaps, an electronic pressure sensor checks whether hydraulic pressure registers within exact PSI boundaries. It is instantaneous, binary, and unyielding: pass (10) or fail (0).
2. **The Chief Flight Instructor (Model Grader):** Observes the pilot's decision-making, situational awareness, and smoothness during turbulent approach, assigning a score on airmanship.

If the pilot demonstrates flawless airmanship but forgets to depressurize a line, the hydraulic line bursts and the plane crashes. In software engineering, both matter: code must compile (Code Grader), and it must solve the user's business problem (Model Grader).

### The "Aha!" Unlock
> **Never evaluate generated code using `exec()` or `eval()`!**  
> Running arbitrary LLM-generated code locally introduces severe remote code execution (RCE) security risks. Python's built-in `ast.parse()` validates syntactic correctness purely by constructing the Abstract Syntax Tree in memory—achieving 100% syntax verification with zero execution risk.

---

## ⚙️ Stage 2 — How It Actually Works

![Code-Based Grading Overview](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623444%2F04_-_006_-_Code_Based_Grading_00.1748623444116.png)

### 1. The Triad of Evaluation Criteria

| Criterion | Measured By | Pass Condition |
| :--- | :--- | :--- |
| **1. Format** | Code Grader | Raw payload only; zero conversational banter, preambles, or markdown wrappers. |
| **2. Valid Syntax** | Code Grader | Compiles cleanly via `json.loads()`, `ast.parse()`, or `re.compile()`. |
| **3. Task Following** | Model Grader | Accurately and securely satisfies the user's technical requirements. |

---

### 2. Syntax Validation Functions

To test syntax deterministically, we build three dedicated validator functions that return a binary score of **10** for valid syntax and **0** for syntax errors:

![Syntax Validation Functions](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623445%2F04_-_006_-_Code_Based_Grading_02.1748623445106.png)

```python
import ast
import json
import re

def validate_json(text: str) -> int:
    """Validates whether text parses as clean JSON."""
    try:
        json.loads(text.strip())
        return 10
    except (json.JSONDecodeError, TypeError):
        return 0

def validate_python(text: str) -> int:
    """Validates whether text parses into a valid Python Abstract Syntax Tree."""
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text: str) -> int:
    """Validates whether text compiles into a valid regular expression pattern."""
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0
```

> [!NOTE]
> **Why Format and Syntax are Intertwined:**  
> If Claude returns valid JSON wrapped in conversational text (e.g., *"Here is your JSON: { ... }"*), `json.loads()` will throw a `JSONDecodeError` and return **0**. Thus, syntax validators double as ruthless format checkers—enforcing zero-banter responses!

---

### 3. Extending the Dataset Schema

For the evaluation runner to route outputs to the appropriate validator, the test dataset schema must include a `"format"` attribute:

```json
[
  {
    "task": "Create a Python function to validate an AWS IAM username",
    "format": "python"
  },
  {
    "task": "Write an AWS EventBridge rule matching S3 object creation",
    "format": "json"
  },
  {
    "task": "Write a regex that matches valid AWS S3 bucket names",
    "format": "regex"
  }
]
```

We can create a dynamic dispatcher function that routes each test case to its respective validator:

```python
def grade_syntax(output: str, test_case: dict) -> int:
    """Dispatches the output to the appropriate syntax validator."""
    target_format = test_case.get("format", "").lower()
    
    if target_format == "json":
        return validate_json(output)
    elif target_format == "python":
        return validate_python(output)
    elif target_format == "regex":
        return validate_regex(output)
    else:
        raise ValueError(f"Unknown target format: {target_format}")
```

---

### 4. Improving Prompt Clarity (Prompt Engineering Iteration)

When our baseline prompt returned conversational explanations, `grade_syntax()` awarded scores of **0/10**. We can dramatically improve syntax scores by hardening our prompt template:

#### Strategy A: Explicit Negative Constraints
```python
prompt = f"""
Please solve the following task:

{task}

Requirements:
* Respond ONLY with valid {format} code.
* Do NOT include any introductory comments, markdown blocks, commentary, or explanations.
"""
```

#### Strategy B: Generic Code Prefilling
When an application handles multiple target formats (Python, JSON, Regex) dynamically, you cannot always hardcode `add_assistant_message(messages, "```json")`. 

Instead, architects use **Generic Code Prefilling**:
```python
# Steers Claude into immediate code generation mode
add_assistant_message(messages, "```code")
```
Claude immediately begins emitting raw code without spending tokens on introductory greetings.

---

### 5. Combining Scores (Composite Scoring)

The final evaluation metric merges the qualitative Model Grader score with the deterministic Code Grader score:

```python
def run_test_case(test_case):
    output = run_prompt(test_case)
    
    # 1. Semantic evaluation via Claude
    model_grade = grade_by_model(test_case, output)
    model_score = model_grade["score"]
    
    # 2. Deterministic syntax validation via Code Grader
    syntax_score = grade_syntax(output, test_case)
    
    # 3. Composite score (Equal 50/50 weighting)
    composite_score = (model_score + syntax_score) / 2
    
    return {
        "test_case": test_case,
        "output": output,
        "model_score": model_score,
        "syntax_score": syntax_score,
        "score": composite_score,
        "reasoning": model_grade["reasoning"]
    }
```

---

## 🚀 Stage 3 — In Practice: Full Hybrid Evaluation Pipeline

```python
import ast
import json
import re
from statistics import mean
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-3-5-haiku-20241022"

# ----------------- SYNTAX VALIDATORS -----------------
def validate_json(text: str) -> int:
    try:
        json.loads(text.strip())
        return 10
    except Exception:
        return 0

def validate_python(text: str) -> int:
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text: str) -> int:
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0

def grade_syntax(output: str, test_case: dict) -> int:
    fmt = test_case.get("format", "").lower()
    if fmt == "json":
        return validate_json(output)
    if fmt == "python":
        return validate_python(output)
    if fmt == "regex":
        return validate_regex(output)
    return 0

# ----------------- PROMPT & MODEL RUNNERS -----------------
def run_prompt(test_case: dict) -> str:
    """V2 Prompt: Enforces strict format and negative constraints."""
    prompt = f"""Please provide a solution to the following task:
{test_case['task']}

* Respond only with {test_case['format'].upper()}
* Do not add any comments or commentary or explanation
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def grade_by_model(test_case: dict, output: str) -> dict:
    """Evaluates task alignment and domain correctness."""
    eval_prompt = f"""
You are an expert technical evaluator. Evaluate this solution.
Task: {test_case['task']}
Target Format: {test_case['format']}
Solution: {output}

Return JSON with:
- "reasoning": Concise explanation of task compliance
- "score": Integer between 1 and 10
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        temperature=0.0,
        messages=[
            {"role": "user", "content": eval_prompt},
            {"role": "assistant", "content": "```json"}
        ],
        stop_sequences=["```"]
    )
    return json.loads(response.content[0].text.strip())

# ----------------- HARNESS ORCHESTRATION -----------------
def run_test_case(test_case: dict) -> dict:
    output = run_prompt(test_case)
    syntax_score = grade_syntax(output, test_case)
    model_eval = grade_by_model(test_case, output)
    model_score = model_eval["score"]
    
    composite_score = (model_score + syntax_score) / 2
    
    return {
        "test_case": test_case,
        "output": output,
        "syntax_score": syntax_score,
        "model_score": model_score,
        "composite_score": composite_score,
        "reasoning": model_eval["reasoning"]
    }

def run_eval(dataset: list) -> list:
    print(f"🚀 Running Hybrid Evaluation on {len(dataset)} items...")
    results = [run_test_case(tc) for tc in dataset]
    
    avg_syntax = mean([r["syntax_score"] for r in results])
    avg_model = mean([r["model_score"] for r in results])
    avg_composite = mean([r["composite_score"] for r in results])
    
    print("\n" + "="*45)
    print(f"HYBRID BENCHMARK SUMMARY")
    print(f"  • Avg Syntax Validity: {avg_syntax:.2f} / 10.0")
    print(f"  • Avg Task Alignment:  {avg_model:.2f} / 10.0")
    print(f"  • Final Composite:     {avg_composite:.2f} / 10.0")
    print("="*45 + "\n")
    return results

if __name__ == "__main__":
    sample_dataset = [
        {"task": "Write an EventBridge rule for EC2 termination", "format": "json"},
        {"task": "Write a boto3 function to list S3 buckets", "format": "python"},
        {"task": "Write a regex validating an S3 bucket name", "format": "regex"}
    ]
    results = run_eval(sample_dataset)
```

---

## ⚖️ Variations & When to Use

| Grading Technique | Strengths | Weaknesses | Production Applicability |
| :--- | :--- | :--- | :--- |
| **AST / Syntax Parsers** | Microsecond execution, 100% deterministic, zero cost, secure. | Validates syntax only; cannot verify runtime logic or edge cases. | **Mandatory** for any code/JSON generation task. |
| **Sandboxed Unit Execution** (Docker/Pytest) | Tests actual functional execution and runtime correctness. | Higher latency, infrastructure complexity, container isolation required. | Recommended for mission-critical software generation pipelines. |
| **Model Grader (LLM Judge)** | Evaluates readability, architectural best practices, and requirements. | Minor stochastic drift, API token cost. | Essential for assessing human intent and requirements coverage. |

---

## 🐛 Common Errors & Anti-Patterns

| Anti-Pattern | Root Cause | Architectural Remediation |
| :--- | :--- | :--- |
| **Using `exec()` / `eval()` for Validation** | Testing code validity by executing it directly in the evaluator process. | **CRITICAL SECURITY RISK.** Always use `ast.parse()` to check syntax safely without code execution. |
| **Markdown Code Block Trapping** | Claude returning ```` ```python def foo(): ... ``` ````, causing `ast.parse()` to fail on backticks. | Use assistant prefilling or strip markdown fences programmatically before feeding to the compiler. |
| **Ignoring Whitespace Traps** | Forgetting to call `.strip()` on model output before invoking parsers. | Always sanitize leading/trailing newlines (`text.strip()`) before syntax validation. |
| **Unbalanced Weighting** | Giving 90% weight to model score, allowing broken code (syntax=0) to receive an overall passing grade. | Consider a **Gating (Veto) Architecture**: if `syntax_score == 0`, final score drops immediately to 0 regardless of model score. |

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      CODE GRADER SYNTAX TOOLKIT                        │
├──────────────┬───────────────────┬─────────────────────────────────────┤
│ Format       │ Python Library    │ Validation Expression               │
├──────────────┼───────────────────┼─────────────────────────────────────┤
│ JSON         │ `import json`     │ `json.loads(text.strip())`          │
│ Python       │ `import ast`      │ `ast.parse(text.strip())`           │
│ Regex        │ `import re`       │ `re.compile(text.strip())`          │
├──────────────┴───────────────────┴─────────────────────────────────────┤
│ Golden Rule: Never execute generated code with `eval()`; use AST parsers│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check

### Question 1
Why is `ast.parse(code_string)` strictly preferred over `exec(code_string)` when validating Python syntax inside an automated evaluation runner?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** **Security and Isolation.**  
`exec()` executes the arbitrary Python code inside the host runtime. If the generated code contains malicious instructions (e.g., `os.system("rm -rf /")`), infinite loops, or network calls, it will compromise or hang the evaluation runner. In contrast, `ast.parse()` builds the Abstract Syntax Tree in memory to verify grammar and syntax without executing a single instruction.
</details>

---

### Question 2
If Claude generates syntactically valid JSON but surrounds it with ```` ```json\n{ ... }\n``` ````, why does `validate_json(text)` return `0`, and why is this desirable?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because `json.loads()` cannot parse markdown backticks, throwing a `JSONDecodeError`.  
This behavior is desirable because our architectural goal specifies **pure, raw data with zero conversational or markdown framing**. The code grader acts as an uncompromising filter: if the prompt fails to suppress markdown fences, the code grader penalizes it with a 0, forcing engineers to improve the prompt or use assistant prefilling.
</details>
