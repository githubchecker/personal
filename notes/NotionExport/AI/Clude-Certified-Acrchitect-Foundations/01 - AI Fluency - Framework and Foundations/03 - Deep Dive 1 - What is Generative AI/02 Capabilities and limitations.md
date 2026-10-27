# 02 — Capabilities & Limitations

> Course 01 · Section 03 · Lesson 2 of 2 · [← Prev: Generative AI Fundamentals](01%20Generative%20AI%20fundamentals.md) · [Course Index](../README.md) · [Next: A Closer Look at Delegation →](../../04%20-%20Delegation/01%20A%20closer%20look%20at%20Delegation.md)

---

## 🗺️ Stage 0 — Concept Map

**The problem:** Treating an LLM as an omniscient, all-purpose computing engine leads to catastrophic production failures. Developers expect models to know yesterday's news from frozen weights, assume they can calculate complex multi-digit financial equations in their heads, or trust ungrounded answers without verifying factual citations.

**Where it fits:**
- **Builds on:** [01 Generative AI Fundamentals](01%20Generative%20AI%20fundamentals.md) (the statistical, probabilistic nature of transformers).
- **Unlocks:** [01 A Closer Look at Delegation](../../04%20-%20Delegation/01%20A%20closer%20look%20at%20Delegation.md) (you cannot strategically delegate tasks without knowing what models excel at vs. where they stumble).

**Why care as an Architect?** Resilient system design does not rely on wishful thinking about AI capabilities. An architect designs systems that maximize model superpowers (fluid translation, rapid synthesis, context continuity) while engineering explicit guardrails and external extensions (RAG, tools, MCP, temperature controls) around technical constraints.

---

## 🔑 New Terms (plain English)

| Term | One-line meaning |
| :--- | :--- |
| **Knowledge Cutoff** | The fixed date after which an LLM has no training data and no innate awareness of world events. |
| **Hallucination** | When a model generates plausible-sounding, grammatically confident, but factually false or fabricated statements. |
| **Context Window Capacity** | The maximum token limit a model can hold in working memory before earlier information is dropped (FIFO). |
| **Temperature** | A hyperparameter (typically 0.0 to 1.0) controlling the randomness and creativity of token selection during inference. |
| **Non-Deterministic Output** | The property where submitting the identical prompt twice can produce slightly different responses due to probability sampling. |
| **Extended Thinking / Reasoning** | Architectures where models generate hidden step-by-step reasoning tokens before producing a final answer, improving multi-step logic. |
| **Retrieval-Augmented Generation (RAG)** | Grounding an LLM by querying external databases and injecting relevant factual snippets directly into the prompt. |
| **Tool Use / Function Calling** | Extending an LLM with external APIs so it can query databases, run code, or browse the web instead of relying on memory. |

---

## 🎈 Stage 1 — The Simple Idea (Analogy: The Brilliant "New Colleague")

Working with a Large Language Model is like onboarding an exceptionally talented new work colleague who just arrived from an isolated, off-grid research institute.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      THE "NEW COLLEAGUE" PROFILE                       │
├────────────────────────────────┬───────────────────────────────────────┤
│ SUPERPOWERS (What They Excel At)│ VULNERABILITIES (Where They Struggle) │
├────────────────────────────────┼───────────────────────────────────────┤
│ • Speaks 30+ languages fluently│ • Hasn't seen today's news (cutoff)   │
│ • Reads 200 pages in 5 seconds │ • Cannot see internal company servers │
│ • Masters law, medicine & code │ • Confidently guesses when unsure     │
│ • Never tires of drafting text │ • Stumbles on complex mental math     │
└────────────────────────────────┴───────────────────────────────────────┘
```

You wouldn't ask this colleague to calculate a 10,000-row tax return in their head without a spreadsheet, nor would you blame them for not knowing an internal company memo they were never given. 

You succeed by **complementing strengths**: pairing your human judgment, ethical oversight, and domain context with their unmatched speed, scale, and language synthesis.

> **The "Aha!":** Do not expect an LLM to be an all-knowing oracle. Treat it as a capable cognitive partner whose limitations must be bridged with external tools, grounding data, and human discernment.

---

## ⚙️ Stage 2 — How It Actually Works

### 3.1 Complementary Strengths: The Human-AI Partnership

High-performance AI engineering is built on an intentional division of labor:

```text
       HUMAN CORE STRENGTHS                    AI SYSTEM STRENGTHS
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│ • Critical Thinking & Logic     │     │ • Massive Processing Speed      │
│ • Domain Judgment & Intuition   │  +  │ • Pattern Recognition at Scale  │
│ • Novel Creative Vision         │     │ • Polymath Domain Breadth       │
│ • Ethical & Legal Accountability│     │ • Multilingual Fluid Synthesis  │
└─────────────────────────────────┘     └─────────────────────────────────┘
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                       SYNERGISTIC ARCHITECTURE
                 (Superior outcomes than either alone)
```

---

### 3.2 Key Capabilities (What LLMs Do Exceptionally Well)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     FOUR PILLARS OF LLM CAPABILITY                     │
├───────────────────┬────────────────────────────────────────────────────┤
│ Capability        │ Architectural Manifestation                        │
├───────────────────┼────────────────────────────────────────────────────┤
│ 1. Fluid Language │ Adapts instantly to tone, audience, and complex    │
│    Mastery        │ technical jargon across diverse domains.           │
├───────────────────┼────────────────────────────────────────────────────┤
│ 2. Dynamic Task   │ Switches from writing SQL to summarizing papers    │
│    Switching      │ or explaining microbiology without retraining.     │
├───────────────────┼────────────────────────────────────────────────────┤
│ 3. Context &      │ Maintains coherent conversational threads, tracking│
│    Continuity     │ subtle constraints across long conversations.      │
├───────────────────┼────────────────────────────────────────────────────┤
│ 4. Tool & System  │ Extends beyond static memory to call APIs, search  │
│    Integration    │ the web, execute code, and query databases.        │
└───────────────────┴────────────────────────────────────────────────────┘
```

#### 1. Fluid Language Mastery
- LLMs excel at manipulating and synthesizing natural language. They can translate complex microbiology papers into plain English for executives, adopt specific brand voices, or refactor verbose code into clean, idiomatic patterns.

#### 2. Dynamic Task-Switching (Zero-Shot Agility)
- Traditional software is single-purpose (a spellchecker only checks spelling; a SQL parser only parses SQL). A single foundation model can draft an executive memo, write unit tests, brainstorm system topologies, and analyze sentiment without requiring architectural modification.

#### 3. Conversational Context & Multi-Turn Continuity
- Modern models maintain continuity across dozens of interaction turns. They retain conversational history, recall subtle project constraints mentioned turns earlier, and incrementally refine solutions based on user critique.

#### 4. Tool & System Integration
- Models are no longer confined to static text completion. Through structured tool calling (JSON schemas), models can emit function calls to execute shell scripts, run Python calculations, and query external REST endpoints.

---

### 3.3 Primary Limitations & Technical Constraints

Every software architect must design defensively around these **six fundamental constraints**:

```text
                   ┌──────────────────────────────────────────────┐
                   │    SIX TECHNICAL CONSTRAINTS OF LLMs         │
                   └──────────────────────┬───────────────────────┘
                                          │
    ┌──────────────┬──────────────┬───────┴──────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼              ▼              ▼
┌────────┐    ┌────────┐    ┌──────────┐    ┌──────────┐   ┌─────────┐   ┌────────────┐
│Knowledge    │ Hallu- │    │ Context  │    │   Non-   │   │ Complex │   │  Private   │
│Cutoffs │    │cinations│   │ Window   │    │Determinis│   │Reasoning│   │    Data    │
│(Static)│    │(Plaus.)│    │ (FIFO)   │    │  (Temp)  │   │ (Logic) │   │ Boundaries │
└────────┘    └────────┘    └──────────┘    └──────────┘   └─────────┘   └────────────┘
```

#### 1. Knowledge Cutoffs (Frozen Memory)
- **Constraint:** A model's internal weights reflect only the data it was trained on up to its cutoff date. It has zero awareness of real-world events, new library releases, or CVE security advisories published post-cutoff.
- **Architectural Impact:** Never rely on model weights for dynamic, time-sensitive facts.

#### 2. Hallucinations & Factual Inaccuracies
- **Constraint:** Models are probabilistic sentence completers, not truth-verifiers. When asked about obscure topics or nonexistent APIs, they prioritize statistical plausibility over factual reality, inventing convincing citations or arguments.
- **Architectural Impact:** Critical business assertions must be grounded in verified documents (RAG) or validated by deterministic code.

#### 3. Context Window Boundaries
- **Constraint:** An LLM's active working memory is finite (e.g., 200k tokens in Claude). While massive, if a conversation or document exceeds this threshold, earlier tokens are dropped—typically on a First-In, First-Out (FIFO) basis.
- **Architectural Impact:** Exceeding context capacity causes silent amnesia, where the model forgets earlier system instructions or constraints.

#### 4. Non-Deterministic Outputs & Temperature
- **Constraint:** Unlike traditional code where `f(x)` always returns `y`, LLMs sample from probability distributions. The same prompt submitted twice can return varying sentence structures or reasoning steps.
- **Role of Temperature:** A setting near `0.0` makes token selection greedy and near-deterministic (ideal for code and extraction), while higher values (`0.7`–`1.0`) introduce diversity and creativity.

#### 5. Complex Multi-Step Reasoning & Mental Math
- **Constraint:** Transformers predict token-by-token without an innate scratchpad. Forcing a model to calculate multi-digit multiplication or navigate deep combinatorial logic in a single pass often leads to errors.
- **Evolution:** Newer "extended thinking" models allocate hidden thinking tokens before responding, dramatically improving mathematical and logical deduction.

#### 6. Private Data & Corporate Boundaries
- **Constraint:** Foundation models have zero inherent access to proprietary internal company files, private Git repos, or intranet databases unless specifically connected via secure interfaces.
- **Architectural Impact:** Models must be integrated into enterprise environments using secure protocols (like Model Context Protocol) and identity-aware proxies.

---

### 3.4 Under the Hood: Architectural Mitigations

How enterprise architects systematically eliminate these constraints:

```text
┌─────────────────────────────────┬──────────────────────────────────────┐
│ Technical Constraint            │ Architectural Mitigation             │
├─────────────────────────────────┼──────────────────────────────────────┤
│ Knowledge Cutoffs               │ Grounding via Web Search Tools / APIs│
│ Hallucinations & Inaccuracies   │ Retrieval-Augmented Generation (RAG) │
│ Context Window Eviction         │ Context Pruning, Summarization & Caching
│ Multi-Step Logic & Math Errors  │ Extended Thinking & Code Interpreter │
│ Private Data Access Limits      │ Model Context Protocol (MCP) Servers │
│ Non-Deterministic Variance      │ Low Temperature (0.0) + Schema Parsing│
└─────────────────────────────────┴──────────────────────────────────────┘
```

> [!TIP]
> **Cultivating Architectural Intuition**  
> Because model capabilities and tool ecosystems evolve constantly, reading documentation is not enough. Architects must engage in **continuous direct experimentation**—testing model edge cases, observing failure modes, and calibrating when to trust an LLM vs. when to enforce deterministic verification.

---

## 🚀 Stage 3 — In Practice / Architecture Case Study

### Case Study: Financial Compliance Assistant

An architect is designing an automated assistant to review corporate quarterly earnings:

1. **Leveraging Capabilities:**
   - Uses **Fluid Language Mastery** to translate complex balance sheets into executive summaries.
   - Uses **Conversational Context** to allow analysts to ask multi-turn clarifying questions.
2. **Defending Against Limitations:**
   - **Mitigating Cutoffs & Private Data:** Connects the model via **MCP** to the company's internal ERP database.
   - **Mitigating Math Hallucinations:** When calculations are required, the model emits an API tool call to a deterministic financial calculator rather than computing revenue margins in its head.
   - **Enforcing Determinism:** Sets `temperature = 0.0` and validates all output structures using strict Pydantic JSON schemas.

---

## ⚖️ Variations: When to Use Which Mitigation

| Architectural Challenge | Option A (Prompt Only) | Option B (Tool Calling / API) | Option C (RAG / Vector DB) | Recommended Decision Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Outdated Facts** | ❌ Fails (Cutoff) | ✅ Web Search Tool | ✅ Fresh Document Retrieval | Use Option B/C when facts change daily |
| **Exact Mathematical Calculation** | ❌ Prone to math drift | ✅ Python Code Interpreter | ❌ Irrelevant | Delegate all pure math to Option B |
| **Large Private Repositories** | ❌ Exceeds context | ⚠️ Limited context | ✅ Hybrid RAG Search | Use Option C for corpus > 200k tokens |
| **Strict JSON Formatting** | ⚠️ Can drift | ✅ Schema Enforcement | ❌ Irrelevant | Enforce JSON schemas with Option B |

---

## 🐛 Common Anti-Patterns

| Anti-Pattern | What Goes Wrong | The Architectural Remedy |
| :--- | :--- | :--- |
| **The "Calculator" Trap** | Asking an LLM to calculate multi-digit interest rates or currency conversions directly. | Give the model access to an external Python calculator tool. |
| **The "Closed-Book" Trap** | Prompting an LLM about internal company policies without providing the policy text. | Use RAG to fetch and inject the exact policy into the prompt context. |
| **The "Infinite Chat" Trap** | Letting a support conversation run for 50 turns without summarizing or clearing history. | Implement context window management: summarize past turns to prevent FIFO truncation. |

---

## 📌 Quick Reference (Exam Revision Card)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CAPABILITIES & LIMITATIONS SUMMARY                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Core Capabilities (What LLMs Do Well):                              │
│    • Fluid Language Synthesis · Dynamic Task-Switching (Polymath)      │
│    • Multi-Turn Context Continuity · Tool & API Integration            │
│                                                                        │
│ 2. Technical Constraints (What LLMs Struggle With):                    │
│    • Knowledge Cutoffs ──────────► Fix with Search / Real-Time Tools    │
│    • Hallucinations ─────────────► Fix with Grounded RAG & Testing     │
│    • Context Boundaries (FIFO) ──► Fix with Caching & Pruning          │
│    • Non-Determinism ────────────► Control with Temperature (0.0)      │
│    • Mental Math & Logic ────────► Fix with Extended Thinking & Code   │
│    • Private Data Boundaries ────► Fix with MCP & Enterprise Connectors│
│                                                                        │
│ Core Formula:                                                          │
│ Human Critical Judgment + Deterministic Tools + LLM Synthesis = Success│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check (Exam Practice)

**Exam-Style Scenario:**  
A team deploys an internal customer service agent powered by Claude. During testing, an employee asks:  
*"What is our company's refund policy for Enterprise Tier 3 customers, and how much did customer ACME Corp pay last month?"*

The model replies with a confident, beautifully formatted, but completely fabricated refund timeline, and states an imaginary dollar figure for ACME Corp.

**Identify the two technical limitations causing this failure, and state the exact architectural remedy for each.**

<details><summary>Answer</summary>

**The Two Limitations:**
1. **Private Data Boundary:** The foundation model has no internal access to the company's private policy repository or customer billing databases.
2. **Hallucination / Confabulation:** Because the model was asked about specific facts it did not have access to, its statistical next-token generation produced a plausible-sounding but fictitious policy and revenue figure.

**The Architectural Remedies:**
1. **For the Refund Policy:** Implement **RAG (Retrieval-Augmented Generation)** to query the internal policy database and inject the verified refund documentation directly into Claude's context window.
2. **For the Billing Figure:** Provide an external **API Tool (MCP connector)** that queries the billing system deterministically, allowing Claude to inspect real database records rather than fabricating numbers.

---

Ready for the next lesson? Continue to [A Closer Look at Delegation →](../../04%20-%20Delegation/01%20A%20closer%20look%20at%20Delegation.md)
</details>
