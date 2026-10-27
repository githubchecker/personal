# 02 — Project Planning & Delegation

> Course 01 · Section 04 · Lesson 2 of 2 · [← Prev: A Closer Look at Delegation](01%20A%20closer%20look%20at%20Delegation.md) · [Course Index](../README.md) · [Next: A Closer Look at Description →](../../05%20-%20Description/01%20A%20closer%20look%20at%20Description.md)

---

## 🗺️ Stage 0 — Concept Map

**The problem:** When developers and architects approach AI, they frequently fall into the "monolithic prompt" trap—submitting a massive, ambiguous goal in a single prompt (e.g., *"Design an enterprise microservices platform with security and monitoring"*). This produces superficial, generic outputs, blows through context with irrelevant tangents, and lacks measurable acceptance criteria.

**Where it fits:**
- **Builds on:** [01 A Closer Look at Delegation](01%20A%20closer%20look%20at%20Delegation.md) (Problem Awareness, Platform Awareness, and the 4 Work Allocation Tiers).
- **Unlocks:** All downstream course modules! The multi-step project plan created in this lesson serves as the **capstone thread** you will carry forward to practice [01 A Closer Look at Description](../../05%20-%20Description/01%20A%20closer%20look%20at%20Description.md), [01 A Closer Look at Discernment](../../07%20-%20Discernment/01%20A%20closer%20look%20at%20Discernment.md), and [01 A Closer Look at Diligence](../../09%20-%20Diligence/01%20A%20closer%20look%20at%20Diligence.md).

**Why care as an Architect?** Production AI systems do not run on single prompts; they run on **multi-step orchestration pipelines** (agent loops, chaining, RAG decomposition). Learning to deconstruct a high-level project into atomic tasks—and systematically assigning each task to human judgment, AI augmentation, automated scripting, or agentic execution—is the hallmark of a Senior Solutions Architect.

---

## 🔑 New Terms (plain English)

| Term | One-line meaning |
| :--- | :--- |
| **Task Decomposition** | Breaking a complex, ambiguous project into discrete, modular sub-tasks with explicit inputs, outputs, and dependencies. |
| **Capstone Project Thread** | An enduring, multi-step case study worked on across multiple lessons to ground theoretical concepts in practical execution. |
| **Socratic Scaffolding** | Inverting the interaction pattern by prompting the AI to interview *you* with clarifying questions to crystallize goals. |
| **Delegation Plan** | A structured document mapping each project milestone to its optimal execution mode (Automation, Augmentation, Agency, Human Reserved). |
| **Definition of Done (DoD)** | Explicit, verifiable success criteria that a deliverable must satisfy before moving to the next workflow stage. |
| **Cognitive Load Allocation** | Intentionally assigning mental tasks based on energy efficiency—offloading volume/pattern matching to AI and reserving critical judgment for humans. |

---

## 🎈 Stage 1 — The Simple Idea (Analogy: The General Contractor)

Imagine building a custom commercial facility. A novice might hire a backhoe operator and shout, *"Build me a modern tech office!"* The result would be disaster.

A seasoned **General Contractor** works in a deliberate three-step sequence:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     THE GENERAL CONTRACTOR'S FLOW                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SCOPE & VISION   │ Define square footage, budget, and purpose       │
│                     │ before purchasing any materials.                 │
├─────────────────────┼──────────────────────────────────────────────────┤
│ 2. BLUEPRINT &      │ Deconstruct into site grading, electrical,       │
│    DECOMPOSITION    │ plumbing, framing, and architectural finishes.   │
├─────────────────────┼──────────────────────────────────────────────────┤
│ 3. SPECIALIZED      │ Assign excavation to heavy machinery, wiring to │
│    DELEGATION       │ licensed electricians, and structural approvals   │
│                     │ exclusively to the certified structural engineer.│
└─────────────────────┴──────────────────────────────────────────────────┘
```

You do not ask the excavator to design the electrical schematic, and you do not ask the master architect to haul drywall. 

> **The "Aha!":** AI project planning is not about asking Claude to do the whole project for you. It is about **collaborating with Claude to architect the project plan first**, defining who does what, and creating a clear contract for human-machine execution.

---

## ⚙️ Stage 2 — How It Actually Works

### The 3-Step Project Planning Protocol

Anthropic defines a structured 20-minute protocol to transform an initial project concept into a production-ready Delegation Plan:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 3-STEP PROJECT PLANNING PROTOCOL                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐
│  STEP 1: CHOOSE PROJECT  │    │  STEP 2: VISION & GOALS  │    │   STEP 3: DELEGATION     │
│ • Select medium scope    │───>│ • Socratic interview     │───>│ • Atomic task breakdown  │
│ • Pick 1 of 4 archetypes │    │ • Define success criteria│    │ • 4-tier mode allocation │
│ • Sized for ~1 hour      │    │ • Clarify intrinsic value│    │ • Save project plan      │
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
```

---

### Step 1: Choose Your Project Scope & Archetype

Your chosen project must satisfy three foundational scoping heuristics:
1. **Substantial:** Involves multiple distinct tasks (research, outlining, synthesis, formatting, review).
2. **Manageable:** Sized to take approximately **1 hour of total cumulative effort** across the course.
3. **Domain Familiarity:** Something you are genuinely interested in or have existing domain background in (remember: *Expertise First*).

Anthropic provides four core project archetypes:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       FOUR PROJECT ARCHETYPES                          │
├───────────────────┬────────────────────────────────────────────────────┤
│ Archetype         │ Candidate Project Concepts                         │
├───────────────────┼────────────────────────────────────────────────────┤
│ 1. Communication  │ • Executive presentation on a domain topic         │
│    Projects       │ • Explanatory technical blog series for beginners  │
│                   │ • System migration proposal or business pitch      │
│                   │ • Technical portfolio bio with supporting case docs│
├───────────────────┼────────────────────────────────────────────────────┤
│ 2. Research       │ • Emerging technology landscape (e.g., MCP vs RAG) │
│    Projects       │ • Architectural trade-off analysis of event buses  │
│                   │ • Dataset pattern discovery and recommendations   │
│                   │ • Comparative evaluation of cloud provider SLAs    │
├───────────────────┼────────────────────────────────────────────────────┤
│ 3. Creative       │ • System concept for a developer platform product │
│    Projects       │ • Information architecture and layout for a portal │
│                   │ • Short story / technical speculative fiction      │
│                   │ • Interactive tutorial scenario design             │
├───────────────────┼────────────────────────────────────────────────────┤
│ 4. Learning       │ • Structured study roadmap for Cloud Certification │
│    Projects       │ • Comprehensive curated resource hub on AI Agents  │
│                   │ • Interactive onboarding guide for junior engineers│
│                   │ • Flashcard and self-check exam preparation suite  │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

### Step 2: Crystallize Vision & Goals (The Socratic Interrogation)

Instead of dictating a rigid plan to Claude, invite Claude to act as an **architectural peer and interviewer**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    THE VISION DISCOVERY INTERACTION                    │
├────────────────────────────────────────────────────────────────────────┤
│ USER PROMPT:                                                           │
│ "Hi Claude, I want to develop [project concept]. Before we start       │
│ planning, please ask me 3-4 probing questions about my target audience,│
│ constraints, and ultimate vision until we have a crystal-clear picture │
│ of what success looks like."                                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ CLAUDE'S DIAGNOSTIC PROBES:                                            │
│ 1. "Who is the primary audience, and what is their technical level?"   │
│ 2. "What single decision or action should this deliverable enable?"    │
│ 3. "What constraints (length, tools, compliance) must be respected?"   │
│ 4. "What would make this project extraordinarily valuable to you?"     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ OUTCOME: A rock-solid Definition of Done (DoD) & Success Metric        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Step 3: Task Breakdown & Delegation Analysis

Once the vision is fixed, deconstruct the project into discrete milestones. For **each individual task**, conduct a deep-dive conversation with Claude across four diagnostic questions:

```text
                TASK DELEGATION DIAGNOSTIC CYCLE
                
                    ┌─────────────────────────┐
                    │ What specific skills or │
                    │ AI capabilities needed? │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Which parts demand     │
                    │ uniquely human judgment?│
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Which parts leverage   │
                    │  AI superpowers best?   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Where does human-AI    │
                    │ collaboration hit peak? │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ ASSIGN DELEGATION TIER: │
                    │ [Auto | Aug | Agency |  │
                    │  Human Reserved]        │
                    └─────────────────────────┘
```

---

## 🚀 Stage 3 — In Practice: Concrete Capstone Example

### Case Study: "Architectural Migration Guide — On-Prem Monolith to Cloud-Native Event Mesh"

Below is an authentic sample of the resulting **Project Delegation Plan** created using this exact 3-step workflow:

#### Project Overview
- **Archetype:** Communication / Technical Architecture Proposal
- **Timebox:** 1 Hour total across course modules
- **Success Criteria:** A 5-page RFC with clear risk matrices, sequence diagrams, and phased migration milestones ready for review by the CTO.

#### The Master Delegation Table

| Phase / Task | Nature of Work | Human Role | AI Role | Assigned Tier | Downstream Module Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. RFC Scope & Target Audience** | Strategic intent & business alignment | Formulates constraints, budget caps, and regulatory rules | Probes for missing non-functional requirements | **Augmentation** | Section 05: *Description* |
| **2. Pattern Extraction & Literature Review** | Synthesizing 10+ Kafka & EventBridge case studies | Skims final citations; provides vetted seed URLs | Ingests documentation and generates comparative feature matrix | **Automation / Augmentation** | Section 06: *Prompting Techniques* |
| **3. Architecture Topology & Trade-Offs** | Deciding Saga pattern vs. Outbox pattern | Evaluates transaction volume; picks architectural pattern | Acts as devils advocate; red-teams edge cases & failure states | **Augmentation** | Section 07: *Discernment* |
| **4. Sequence Diagram & Spec Generation** | Mechanical formatting & PlantUML / Mermaid code | Validates logic flow against enterprise security specs | Generates valid Mermaid code and OpenAPI JSON schemas | **Automation** | Section 08: *Description-Discernment Loop* |
| **5. Continuous Compatibility Linting** | Running schema validation against internal CI tools | Sets permission bounds and review checkpoints | Runs CLI tool tests autonomously via Agent loop | **Agency** | Section 09: *Diligence* |
| **6. Legal, Security & Final Sign-Off** | Compliance attestation & executive accountability | Exclusive sign-off and final governance approval | None (strictly isolated from model influence) | **Reserved for Humans** | Section 09: *Diligence* |

---

## ⚖️ Variations & Decision Matrix: Choosing Your Project

Not all project types exercise the same fluency muscles. Use this matrix to select your topic based on your learning goals:

| Project Archetype | Domain Knowledge Need | AI Acceleration Factor | Primary Risk to Discern | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| **Communication** (e.g., Exec Pitch / RFC) | **High** (Need to know internal company context) | **Very High** (Tone adaptation, slide structuring, executive summaries) | Generic jargon, lack of punchy specifics | Aspiring Solutions Architects & Tech Leads |
| **Research** (e.g., Tech Comparison) | **Medium to High** (Need ability to spot hallucinated benchmarks) | **Extremely High** (Massive data digestion, matrix tables) | Stale data, plausible-sounding hallucinated features | Research Engineers & Platform Architects |
| **Creative** (e.g., Product Concept) | **Moderate** (User persona intuition) | **High** (Divergent brainstorming, storyboarding) | Derivative or cliché concept tropes | Product Managers & Innovation Leads |
| **Learning** (e.g., Study Curriculum) | **Low to Medium** (Learning the topic as you go) | **High** (Flashcard generation, question banks, study guides) | Inaccurate technical explanations | Certification Candidates & Students |

---

## 🐛 Common Misconceptions & Anti-Patterns

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   PROJECT PLANNING ANTI-PATTERNS                       │
├──────────────────────────────────┬─────────────────────────────────────┤
│ Anti-Pattern                     │ Why It Fails & How to Correct It   │
├──────────────────────────────────┼─────────────────────────────────────┤
│ ❌ "The Monolithic Prompt"       │ Asking Claude to execute all tasks  │
│    (One-Shot Project Execution)  │ in one prompt yields generic,       │
│                                  │ shallow output. Decompose first!    │
├──────────────────────────────────┼─────────────────────────────────────┤
│ ❌ "Order-Taker Syndrome"        │ Only giving instructions without    │
│    (Passive Monologue)           │ inviting Claude to critique, probe, │
│                                  │ or interview your vision.           │
├──────────────────────────────────┼─────────────────────────────────────┤
│ ❌ "The Ephemeral Scratchpad"    │ Devising a plan but discarding it;  │
│    (Throwaway Conversation)      │ this plan MUST be saved as your     │
│                                  │ persistent artifact for future labs!│
├──────────────────────────────────┼─────────────────────────────────────┤
│ ❌ "The Zero-Knowledge Topic"    │ Choosing a topic you know nothing   │
│    (Violating Expertise-First)   │ about makes it impossible to discern│
│                                  │ subtle hallucinations or low quality│
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

## 🛠️ Hands-on Exercise: Execute Your 20-Minute Planning Lab

Set a timer for 20 minutes and complete this foundational exercise:

### Phase 1: Topic Selection (3 mins)
Select one topic from the [Four Project Archetypes](#step-1-choose-your-project-scope--archetype) that you have strong personal interest or domain background in.

### Phase 2: Claude Socratic Dialogue (10 mins)
Open Claude and submit this exact initial message:

```text
"Hi Claude, I am working on a multi-step project for my AI Fluency curriculum. 
I have chosen to work on: [Insert your project, e.g., 'An architectural evaluation of vector databases vs graph databases for enterprise knowledge management'].

Before we jump into execution, I want to establish a comprehensive Delegation Plan.
Please ask me 3 or 4 clarifying questions about my goals, audience, and constraints so we can solidify what success looks like."
```

Engage in a genuine, multi-turn chat:
- Clarify who will consume the output.
- Discuss which parts require your domain expertise vs Claude's analytical speed.
- Challenge Claude if it suggests automating something that carries security, compliance, or brand risk.

### Phase 3: Generate & Save the Delegation Plan (7 mins)
Ask Claude to compile the discussion into a structured table:
```text
"Please synthesize our discussion into a Markdown table with columns:
| Milestone / Task | Required Capabilities | Human Role | AI Role | Delegation Tier (Automation / Augmentation / Agency / Human Reserved) |"
```

> [!IMPORTANT]
> **Save this Markdown artifact!** Keep this project plan in an easily accessible note. You will explicitly use this exact project in Section 05 (*Description*), Section 07 (*Discernment*), and Section 09 (*Diligence*).

---

### Reflection Questions

Before moving to Section 05, take a moment to answer these three core Anthropic prompts:

1. **Unexpected Discoveries:** *What unexpected insights or blindspots emerged during your planning conversation when Claude questioned your assumptions?*
2. **Anticipated Friction:** *What do you anticipate will be the most challenging aspect of your delegation plan (e.g., verifying AI factual claims, maintaining voice, or constraining scope)?*
3. **Skill Gaps:** *What additional information or prompting capabilities (e.g., structured outputs, few-shot examples) might help you delegate more seamlessly to Claude?*

---

## 🎯 Official Anthropic Key Takeaways

- **The Power of Scaffolding:** Effective AI project execution is an iterative, multi-stage discipline—never a one-shot command.
- **Socratic Goal Clarification:** Using Claude to interview you sharpens fuzzy requirements into concrete, measurable success metrics.
- **Granular Task Decomposition:** Breaking complex deliverables into modular, atomic tasks enables targeted application of the 4 Work Allocation Tiers.
- **The Enduring Spine:** Saving a structured Delegation Plan provides the essential foundation needed to practice *Description*, *Discernment*, and *Diligence* throughout the rest of your AI engineering journey.

---

## 📌 Quick Reference & Schema

### The 3-Step Planning Summary Card

```text
┌────────────────────────────────────────────────────────────────────────┐
│                 PROJECT PLANNING & DELEGATION SUMMARY                  │
├───────────────────────┬────────────────────────────────────────────────┤
│ Step                  │ Core Action Required                           │
├───────────────────────┼────────────────────────────────────────────────┤
│ 1. Choose Project     │ Sized for ~1 hour; 1 of 4 archetypes; high     │
│                       │ domain familiarity (Expertise First).          │
├───────────────────────┼────────────────────────────────────────────────┤
│ 2. Vision & Goals     │ Socratic interview with Claude to define       │
│                       │ measurable Definition of Done (DoD).           │
├───────────────────────┼────────────────────────────────────────────────┤
│ 3. Task Breakdown     │ Decompose into atomic sub-tasks; assign to     │
│                       │ Automation, Augmentation, Agency, or Human.    │
├───────────────────────┴────────────────────────────────────────────────┤
│ GOLDEN RULE: "Do not automate the plan; collaborate to architect it." │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check: Exam-Style Question

A Solutions Architect is planning a 3-week initiative to modernize an internal customer support platform using Claude. During the initial project kickoff, which of the following approaches demonstrates proper adherence to Anthropic's Project Planning and Delegation framework?

- **A)** Prompt Claude with the complete legacy source code in one prompt and instruct it to autonomously rewrite and deploy the entire serverless backend to AWS.
- **B)** Break the initiative into distinct tasks (intent classification, draft reply generation, PII masking, and human agent sign-off), collaborating with Claude to define acceptance criteria for each and assigning PII masking to deterministic automation and final customer dispatch to Human-in-the-Loop.
- **C)** Manually write all classification code and draft generation logic by hand to avoid model unpredictability, reserving Claude solely for generating congratulatory team emails upon project completion.
- **D)** Instruct an autonomous agent loop to scrape competitor support platforms and dynamically deploy matching features to production without staging review.

<details><summary>Click to view Answer & Detailed Explanation</summary>

### Correct Answer: **B**

### Architectural Breakdown:
- **Option B is optimal:** It exemplifies **Task Decomposition** and strategic **Work Allocation**. It breaks a complex system into atomic components, pairs deterministic logic where safety is paramount (PII masking), leverages AI for high-velocity text generation (draft replies), and maintains rigorous **Human-in-the-Loop (HITL)** governance for final outbound communication.
- **Why A is incorrect:** Submitting the entire system in a single monolithic prompt commits the "Handing over the wheel" anti-pattern and invites unvetted regressions and architectural drift.
- **Why C is incorrect:** It ignores AI's massive efficiency superpowers, resulting in wasted engineering hours on tasks that an LLM can accelerate safely under proper prompt constraints.
- **Why D is incorrect:** It completely bypasses human governance, validation, and security review, violating all core principles of ethical and safe agency.

Ready for the next core competency? Continue to [A Closer Look at Description →](../../05%20-%20Description/01%20A%20closer%20look%20at%20Description.md)
</details>
