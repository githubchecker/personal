# 02 — The 4D Framework

> Course 01 · Section 02 · Lesson 2 of 2 · [← Prev: Why do we need AI Fluency?](01%20Why%20do%20we%20need%20AI%20Fluency.md) · [Course Index](../README.md) · [Next: Generative AI Fundamentals →](../03%20-%20Deep%20Dive%201%20-%20What%20is%20Generative%20AI/01%20Generative%20AI%20fundamentals.md)

---

## 🗺️ Stage 0 — Concept Map

- **The Problem:** Engaging with AI across any mode without a structured framework results in misallocated effort, vague prompts, undetected errors, and regulatory or ethical exposure.
- **Where It Fits:** The central competency model of the Anthropic AI Fluency curriculum. It governs all three engagement modes (**Automation**, **Augmentation**, **Agency**) and sets up the deep dives in Sections 04–09.
- **Exam Relevance:** The exam tests your ability to identify which "D" resolves a specific real-world failure mode (e.g., catching bias, setting task boundaries, avoiding vague prompts).

---

## 🔑 Key Terms & Definitions

| Term | Exam Definition |
| :--- | :--- |
| **AI Fluency** | A dynamic synthesis of practical skills, knowledge, insights, and values to interact with AI **effectively, efficiently, ethically, and safely**. |
| **Delegation** | **Strategic Planning:** Deciding what work to handle yourself vs. what to assign to AI based on capabilities and goals. |
| **Description** | **Clear Communication:** Articulating vision, background context, operational steps, constraints, and format expectations. |
| **Discernment** | **Critical Evaluation:** Assessing AI outputs using domain expertise, logic, factual verification, and value alignment. |
| **Diligence** | **Responsibility & Accountability:** Ensuring interactions are safe, unbiased, data-protected, transparent, and owned by humans. |

---

## 🎈 Stage 1 — The Core Concept

```text
       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
       │1. DELEGATION │      │2. DESCRIPTION│      │3.DISCERNMENT │      │ 4. DILIGENCE │
       │  Strategic   │ ───► │    Clear     │ ───► │   Critical   │ ───► │Responsibility│
       │   Planning   │      │Communication │      │  Evaluation  │      │& Accountability
       └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

> **The "Aha!":** Prompting is only **one part** (Description). True fluency requires knowing what to assign (**Delegation**), critically validating the output (**Discernment**), and standing behind the final product with full accountability (**Diligence**).

---

## ⚙️ Stage 2 — The Four Competencies (Exam-Focused Deep Dive)

### 1. Delegation (Strategic Planning)
- **Core Focus:** Taking a big-picture view to decide what work you should handle yourself and where AI can be genuinely helpful.
- **Key Questions:**
  - What are you trying to accomplish overall?
  - What specific sub-tasks are involved?
  - How can the workload be divided strategically?
- **Requirements:** 
  - Understanding your ultimate goal.
  - Recognizing what AI can and cannot do well.
  - Thoughtfully integrating AI into the process rather than blindly offloading work.
- **Practical Example:** In a research project, delegating lengthy document review and initial findings extraction to Claude, while reserving critical analysis and final conclusions for yourself.

---

### 2. Description (Clear Communication)
- **Core Focus:** Articulating vision, context, and expectations clearly to set up both yourself and the AI for collaborative success.
- **Beyond Basic Prompts:** Moving past one-line commands into context-rich conversations specifying:
  - **Desired Output Format:** (e.g., JSON schema, markdown table, executive summary).
  - **Approach/Methodology:** How the AI should step through the task.
  - **Background Information:** Context, audience, and constraints.
  - **Tone & Style:** Professional, concise, pedagogical, etc.
- **Practical Examples:**
  - *Vague:* "Make me a logo."  
    *Fluent Description:* Detailing company values, target audience demographics, color palettes, and style references.
  - *AI Tutor Prompt:* *"Don't tell me the answer, just help me work through this problem step by step so I can better understand the concept."*

---

### 3. Discernment (Critical Evaluation)
- **Core Focus:** Thoughtfully evaluating and assessing AI outputs using your own domain expertise, judgment, and critical insight.
- **Core Evaluation Criteria:**
  1. **Factual Accuracy:** Are the facts, references, and data correct?
  2. **Logic & Reasoning:** Does the argument or technical approach make sense?
  3. **Value Alignment:** Does the output align with project values and ethical standards?
  4. **Utility:** Does the deliverable actually move your work forward?
- **The Iterative Loop:** Most workflows are not one-shot; they operate as a continuous small loop:
  $$\text{Describe} \longrightarrow \text{Discern / Evaluate} \longrightarrow \text{Refine Request} \longrightarrow \text{Repeat}$$

---

### 4. Diligence (Responsibility & Accountability)
- **Core Focus:** Ensuring all interactions with AI are safe, ethical, transparent, and responsible.
- **Key Considerations:**
  - **Controlling Biases:** Checking for unintended bias (e.g., in job descriptions, candidate screening, or policy drafting).
  - **Verifying Facts:** Proactively corroborating claims against ground-truth sources.
  - **Protecting Sensitive Data:** Enforcing privacy, redacting PII, and safeguarding proprietary IP.
  - **Transparency:** Being open about where and how AI was involved in producing work.
- **Ownership (Non-Negotiable):** Taking ultimate responsibility for AI-assisted work and being willing to stand fully behind the final product.

---

## ⚖️ The 4Ds Across the Three Interaction Modes

| Mode | What It Is | How the 4Ds Apply |
| :--- | :--- | :--- |
| **Automation** | AI completes specific tasks based on direct instructions. | • **Delegation:** Choose bounded, low-ambiguity tasks.<br>• **Description:** Specify exact schemas & rules.<br>• **Discernment:** Validate automated outputs via assertions.<br>• **Diligence:** Check data privacy before batch processing. |
| **Augmentation** | Human and AI collaborate as creative thinking & execution partners. | • **Delegation:** Split exploration vs. decision-making.<br>• **Description:** Provide background context & goals.<br>• **Discernment:** Challenge AI reasoning & trade-offs.<br>• **Diligence:** Ensure recommendations align with values. |
| **Agency** | AI configured to work independently within defined boundaries. | • **Delegation:** Define mission scope & permission gates.<br>• **Description:** Set rules, docs, and `CLAUDE.md` files.<br>• **Discernment:** Inspect diffs, test logs, and summaries.<br>• **Diligence:** Sandbox tool access and audit telemetry. |

---

## 🎯 Exam Scenarios: Identifying the Correct "D"

| Exam Question Scenario | Primary "D" Tested | Why |
| :--- | :--- | :--- |
| An engineer gives Claude access to an internal code repo without setting test commands or coding standards. | **Description** | Failed to articulate context, expectations, and operational guidelines. |
| An HR team uses AI to rank resumes, but the model systematically filters out non-traditional degrees. | **Diligence** | Failed to control for bias, ethical fairness, and responsible oversight. |
| A developer copies an AI-generated SQL query into production without testing for SQL injection or indexing. | **Discernment** | Failed to critically evaluate and test accuracy, logic, and safety. |
| A company assigns financial forecasting to an LLM rather than deterministic modeling tools. | **Delegation** | Misallocated work: misunderstood what AI can and cannot do well. |

---

## 📌 Quick Reference (Exam Revision Card)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 4D COMPETENCY CARD                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. DELEGATION  ──► STRATEGIC PLANNING                                  │
│    "What to do yourself vs. what AI should help with."                 │
│                                                                        │
│ 2. DESCRIPTION ──► CLEAR COMMUNICATION                                 │
│    "Context + Desired Format + Approach + Tone (Beyond basic prompts)" │
│                                                                        │
│ 3. DISCERNMENT ──► CRITICAL EVALUATION                                 │
│    "Check Accuracy + Logic + Value Alignment + Utility"                │
│    (Operates via the Description-Discernment Iterative Loop)           │
│                                                                        │
│ 4. DILIGENCE   ──► RESPONSIBILITY & ACCOUNTABILITY                     │
│    "Control Bias + Protect Data + Transparency + Human Ownership"      │
│                                                                        │
│ Core Goal: Effective, Efficient, Ethical, and Safe AI Interaction.     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check (Exam Practice)

**Exam-Style Question:**  
A project manager uses an AI assistant to summarize customer interviews. Before presenting the slide deck to executive stakeholders, the manager cross-checks three surprising statistics against the original interview transcripts and replaces one metric that was misattributed.

**Which specific 4D competency did the manager exercise during this verification step?**

<details><summary>Answer</summary>

**Discernment (Critical Evaluation).**  
The manager thoughtfully evaluated the output using domain judgment, verified factual accuracy against ground truth sources, and refined the deliverable before using it. (Standing behind the final deck also demonstrates **Diligence / Ownership**, but the specific act of cross-checking accuracy is **Discernment**).

---

Ready for the next lesson? Continue to [Generative AI Fundamentals →](../03%20-%20Deep%20Dive%201%20-%20What%20is%20Generative%20AI/01%20Generative%20AI%20fundamentals.md)
</details>
