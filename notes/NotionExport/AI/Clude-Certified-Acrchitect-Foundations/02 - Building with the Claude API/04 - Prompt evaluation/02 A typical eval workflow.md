# 02 — A Typical Eval Workflow

> Course 02 · Section 04 - Prompt evaluation · Lesson 2 of 6 · [← Prev: Prompt Evaluation](01%20Prompt%20evaluation.md) · [Course Index](../README.md) · [Next: Generating Test Datasets →](03%20Generating%20test%20datasets.md)

---

## 🗺️ Stage 0 — Concept Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 5-STEP PROMPT EVALUATION CYCLE                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌────────────────────┐          ┌───────────────────────┐            │
│   │ 1. Draft a Prompt  ├─────────►│ 2. Create Eval Dataset│            │
│   │    (Template)      │          │    (Input Questions)  │            │
│   └────────────────────┘          └───────────┬───────────┘            │
│             ▲                                 │                        │
│             │                                 ▼                        │
│   ┌─────────┴──────────┐          ┌───────────────────────┐            │
│   │ 5. Modify Prompt   │          │ 3. Feed Through Claude│            │
│   │    & Repeat Loop   │          │    (API Execution)    │            │
│   └─────────▲──────────┘          └───────────┬───────────┘            │
│             │                                 │                        │
│             │    ┌───────────────────────┐    │                        │
│             └────┤ 4. Feed Through Grader│◄───┘                        │
│                  │    (Scoring 1-10)     │                             │
│                  └───────────────────────┘                             │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

A robust prompt evaluation workflow follows a disciplined, **5-step empirical cycle**. Rather than relying on subjective intuition or ad-hoc tinkering, this structured pipeline establishes a baseline score, measures quantitative improvements, and guards against regression.

Whether using custom Python scripts or enterprise evaluation platforms, mastering this foundational 5-step architecture is essential for engineering reliable Claude-powered applications.

---

## 🔑 New Terms

| Term | One-Line Meaning |
| :--- | :--- |
| **Prompt Template** | A parameterized string with placeholders (e.g., `{question}`) that gets interpolated with test inputs dynamically. |
| **Eval Dataset** | A curated collection of representative input samples designed to test prompt performance across diverse real-world scenarios. |
| **Harness / Runner** | The automated execution script or pipeline that merges inputs into the template, invokes Claude, and passes outputs to the grader. |
| **Grader (Scorer)** | An automated evaluation component (code-based logic or an LLM judge) that inspects responses and scores them (e.g., 1–10). |
| **Baseline Score** | The benchmark average score of the initial, unoptimized prompt version across the entire evaluation dataset. |
| **Iteration Delta ($\Delta$)** | The quantitative difference in aggregate score between Prompt Version $N$ and Version $N+1$ ($\text{Score}_{v2} - \text{Score}_{v1}$). |

---

## 🎈 Stage 1 — The Simple Idea

### The Standardized Exam & Rubric Analogy
Imagine a student preparing for a standardized physics examination:
1. **The Baseline:** The student writes answers to practice questions using their raw knowledge.
2. **The Committee & Rubric:** A grading committee evaluates their answers using a strict 10-point rubric and issues a score report: Mechanics = 10/10, Thermodynamics = 4/10, Optics = 9/10 (Average = 7.66).
3. **Targeted Revision:** Rather than guessing what went wrong, the student reviews the specific rubric deductions in Thermodynamics, revises their study approach, and re-takes the practice exam.
4. **Verified Progress:** On the re-take, Thermodynamics climbs to 8/10, lifting their overall average to 8.7/10.

### The "Aha!" Unlock
> **Prompt development is an optimization loop.**  
> Without a frozen dataset and an objective grader, changing a prompt is like shooting at a moving target in the dark. With a 5-step evaluation loop, prompt modifications become measurable gradient steps that systematically drive performance higher.

---

## ⚙️ Stage 2 — How It Actually Works

![The 5-Step Eval Workflow](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623388%2F04_-_002_-_A_Typical_Eval_Workflow_00.1748623388621.png)

---

### Step 1: Draft a Prompt Template

Every evaluation begins with an initial prompt template containing interpolation variables:

```python
prompt = f"""
Please answer the user's question:

{question}
"""
```

![Step 1: Draft a Prompt](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623390%2F04_-_002_-_A_Typical_Eval_Workflow_04.1748623389909.png)

This baseline prompt defines the foundational instructions. It may be intentionally simple or an initial draft that needs hardening.

---

### Step 2: Create an Eval Dataset

The evaluation dataset contains representative input records that mirror the variety, complexity, and domain distribution of production queries.

![Step 2: Create an Eval Dataset](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623391%2F04_-_002_-_A_Typical_Eval_Workflow_06.1748623390933.png)

In our introductory walkthrough, the dataset contains three distinct test queries:
1. `"What's 2+2?"` *(Arithmetic / exact factual recall)*
2. `"How do I make oatmeal?"` *(Procedural / multi-step instructional)*
3. `"How far away is the Moon?"` *(Scientific / quantitative knowledge)*

> [!NOTE]
> In real-world enterprise architectures, eval datasets typically range from **tens to hundreds or thousands of records**. These can be curated from production logs, authored by subject-matter experts, or generated synthetically by Claude.

---

### Step 3: Feed Through Claude

The automated evaluation runner iterates through each record in the dataset, interpolates the test question into the prompt template, and sends the request to Claude via the API:

![Step 3: Feed Through Claude](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623391%2F04_-_002_-_A_Typical_Eval_Workflow_08.1748623391715.png)

#### Example Request Execution:
```text
[Input Question 1]: "What's 2+2?"
   │
   ▼
[Interpolated Prompt]:
Please answer the user's question:
What's 2+2?
   │
   ▼
[Claude Output]: "2 + 2 = 4"
```

Claude produces independent responses for every input question in the dataset:
- **Math response:** `"2 + 2 = 4"`
- **Oatmeal response:** Step-by-step cooking instructions
- **Moon response:** Average lunar distance (~384,400 km)

---

### Step 4: Feed Through a Grader

The outputs from Claude—along with the original test questions and any evaluation criteria—are passed to an automated **Grader**:

![Step 4: Feed Through a Grader](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623392%2F04_-_002_-_A_Typical_Eval_Workflow_11.1748623392294.png)

The grader evaluates each response on an objective scale (typically **1 to 10**, where 10 represents a perfect response conforming to all quality criteria):

| Test Question | Claude Output Summary | Grader Score (1–10) | Grader Diagnostic Feedback |
| :--- | :--- | :---: | :--- |
| **"What's 2+2?"** | `"2 + 2 = 4"` | **10** | Precise, accurate, zero extraneous commentary. |
| **"How do I make oatmeal?"** | Basic 2-line microwave instruction | **4** | Lacks ingredient ratios, cooking times, and stovetop instructions. |
| **"How far away is the Moon?"** | Detailed explanation with miles and kilometers | **9** | Highly accurate; minor points for formatting. |

#### Calculating the Baseline Metric:
$$\text{Average Score} = \frac{10 + 4 + 9}{3} = \mathbf{7.66}$$

This numerical value establishes the **empirical baseline** for Prompt Version 1.

---

### Step 5: Change Prompt and Repeat

With a concrete baseline score and diagnostic feedback highlighting weaknesses (such as the oatmeal recipe lacking sufficient depth), we modify the prompt template to steer Claude toward more detailed answers:

```python
prompt = f"""
Please answer the user's question:

{question}

Answer the question with ample detail
"""
```

![Step 5: Change Prompt and Repeat](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623393%2F04_-_002_-_A_Typical_Eval_Workflow_15.1748623393094.png)

The entire evaluation pipeline is executed again against the **exact same evaluation dataset**:

| Test Question | Prompt V1 Score | Prompt V2 Score | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **"What's 2+2?"** | 10 | 9 | -1 *(Added slight verbosity to simple math)* |
| **"How do I make oatmeal?"** | 4 | 9 | +5 *(Rich recipe with ratios and variations)* |
| **"How far away is the Moon?"** | 9 | 10 | +1 *(In-depth astronomical context)* |
| **Aggregate Score** | **7.66** | **9.33** *(or 8.7 in slide)* | **+1.04 to +1.67** |

---

### Prompt Scoring & Continuous Benchmarking

By comparing numeric performance across versions, teams can make data-driven architectural decisions:

![Prompt Scoring Comparison](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623393%2F04_-_002_-_A_Typical_Eval_Workflow_17.1748623393804.png)

- **Objective Selection:** Always deploy the prompt version demonstrating the superior aggregate score across the golden dataset.
- **Regression Detection:** Instantly spot if an improvement in one domain (e.g., recipe instructions) causes a penalty in another (e.g., concise math calculations).
- **Stopping Criteria:** Know when a prompt has reached diminishing returns (e.g., 9.4 $\to$ 9.45) and further engineering is unnecessary.

---

## 🚀 Stage 3 — In Practice: A Minimal Python Evaluation Harness

The following architecture demonstrates how a 5-step evaluation loop is constructed in pure Python using the Anthropic API:

```python
import anthropic

client = anthropic.Anthropic()

# Step 2: Define the frozen evaluation dataset
eval_dataset = [
    {"question": "What's 2+2?", "domain": "math"},
    {"question": "How do I make oatmeal?", "domain": "recipe"},
    {"question": "How far away is the Moon?", "domain": "science"}
]

# Step 1: Candidate prompt templates
prompts = {
    "v1_baseline": "Please answer the user's question:\n\n{question}",
    "v2_detailed": "Please answer the user's question:\n\n{question}\n\nAnswer the question with ample detail."
}

def mock_or_llm_grader(question: str, response: str) -> float:
    """
    Step 4: Automated grader logic (Can be rule-based code or LLM-as-a-judge).
    Returns an objective score between 1.0 and 10.0.
    """
    # In production, this can invoke Claude with an evaluation rubric
    # or assert deterministic regex/structural invariants.
    if "2+2" in question and "4" in response:
        return 10.0 if len(response) < 50 else 8.0
    if "oatmeal" in question:
        return 9.0 if len(response.split()) > 40 else 4.0
    if "Moon" in question and ("384,400" in response or "238,855" in response):
        return 9.5
    return 6.0

def run_eval(prompt_template: str) -> float:
    """Step 3 & 4: Execute dataset through Claude and compute aggregate score."""
    total_score = 0.0
    
    for item in eval_dataset:
        formatted_prompt = prompt_template.format(question=item["question"])
        
        # Step 3: API Execution (use temperature=0.0 for deterministic benchmarking)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.0,
            messages=[{"role": "user", "content": formatted_prompt}]
        )
        response_text = message.content[0].text
        
        # Step 4: Grader scoring
        score = mock_or_llm_grader(item["question"], response_text)
        total_score += score
        
    return total_score / len(eval_dataset)

# Step 5: Compare versions
score_v1 = run_eval(prompts["v1_baseline"])
score_v2 = run_eval(prompts["v2_detailed"])

print(f"Prompt V1 Baseline Score: {score_v1:.2f} / 10.0")
print(f"Prompt V2 Detailed Score: {score_v2:.2f} / 10.0")
print(f"Improvement Delta (Δ):   {score_v2 - score_v1:+.2f}")
```

---

## ⚖️ Variations & When to Use

| Evaluation Scale | Dataset Size | Grader Implementation | Execution Frequency | Recommended Environment |
| :--- | :---: | :--- | :--- | :--- |
| **Micro-Eval** | 5 – 20 items | Fast rule-based assertions / regex | Interactive development, pre-commit | Local CLI or notebook |
| **Standard Regression Eval** | 50 – 200 items | Hybrid: deterministic code + LLM judge | Pull request CI/CD pipeline | Automated build runners |
| **Enterprise Comprehensive Eval** | 500 – 5,000+ items | Multi-criteria LLM judges + human sampling | Nightly builds or pre-release release gates | Distributed cloud batch pipeline |

---

## 🐛 Common Errors & Anti-Patterns

| Anti-Pattern | Root Cause | Architectural Remediation |
| :--- | :--- | :--- |
| **Changing the Dataset Mid-Cycle** | Adding or removing questions between V1 and V2 runs. | **Keep the dataset frozen.** Changing the test set invalidates the baseline score; comparisons must be strictly like-for-like. |
| **Evaluating with High Temperature** | Running evals with `temperature=1.0`. | Set `temperature=0.0` during evaluation runs to ensure reproducible, deterministic benchmarking. |
| **Masking Outlier Regressions** | Looking only at the aggregate average score. | Always inspect the distribution and minimum score. A prompt that improves average score from 7.6 to 8.5 but drops a safety/security query to 0 is unusable. |
| **Uncalibrated Graders** | Using an LLM grader whose scoring criteria drift or hallucinate. | Test and evaluate your *grader* before trusting its scores. Graders need clear rubrics and few-shot calibration. |

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      5-STEP EVAL WORKFLOW SUMMARY                      │
├───────┬────────────────────────┬───────────────────────────────────────┤
│Step 1 │ Draft Prompt Template  │ Define instructions with placeholders │
│Step 2 │ Create Eval Dataset    │ Representative inputs (kept frozen)   │
│Step 3 │ Feed Through Claude    │ API invocation (temperature=0.0)      │
│Step 4 │ Feed Through Grader    │ Score responses (1–10) & compute mean │
│Step 5 │ Change Prompt & Repeat │ Re-run, compute Delta (Δ), iterate    │
└───────┴────────────────────────┴───────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check

### Question 1
Why is it strictly forbidden in production engineering to add new questions to the evaluation dataset during the middle of an evaluation cycle comparing Prompt V1 and Prompt V2?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because it **invalidates the baseline score**.  
Evaluation scores are only statistically comparable if both prompt candidates are subjected to the exact same distribution of test inputs. If new questions are added during V2, a change in average score could be caused by the new questions being easier or harder, rather than the prompt modification itself.
</details>

---

### Question 2
What parameter in the Anthropic API call should typically be set to `0.0` when executing an automated evaluation runner, and why?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** **`temperature=0.0`**.  
Setting temperature to 0 eliminates random sampling variability, making Claude's outputs as deterministic and reproducible as possible. This ensures that measured score deltas reflect actual differences in prompt design rather than stochastic sampling noise.
</details>
