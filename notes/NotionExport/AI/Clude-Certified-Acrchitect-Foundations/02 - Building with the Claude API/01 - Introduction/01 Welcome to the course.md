# 01 — Welcome to the Course

> Course 02 · Section 01 · Lesson 1 of 1 · [← Back to Course Index](../README.md) · [Next: Overview of Claude Models →](../02%20-%20Anthropic%20overview/01%20Overview%20of%20Claude%20models.md)

---

## 🗺️ Stage 0 — Concept Map

**The problem:** Transitioning from conversational web playgrounds to building scalable production software requires a paradigm shift. Production applications cannot rely on ad-hoc prompts, unversioned inputs, manual copy-pasting, or unconstrained token usage. Developers need programmatic control over system prompts, message state, streaming buffers, structured schemas, tool execution loops, and cost optimization.

**Where it fits:**
- **Builds on:** [Course 01 — AI Fluency: Framework and Foundations](../../01%20-%20AI%20Fluency%20-%20Framework%20and%20Foundations/README.md) (translating the theoretical 4D framework—Delegation, Description, Discernment, Diligence—into software architecture).
- **Unlocks:** The entire developer curriculum of [Course 02 — Building with the Claude API](../README.md), spanning SDK integrations, evaluation pipelines, tool calling, RAG, prompt caching, MCP, and autonomous agent loops.

**Why care as an Architect?** The Claude API is the foundational runtime engine for enterprise AI systems. As an architect, you are responsible for designing resilient, low-latency, and cost-effective pipelines. This course equips you to make principled engineering trade-offs across model families, state management, schema enforcement, and agentic autonomy.

---

## 🔑 New Terms (plain English)

| Term | One-line meaning |
| :--- | :--- |
| **Messages API** | Anthropic's primary REST/SDK endpoint (`/v1/messages`) for creating structured, multi-turn conversational completions. |
| **Stateless API** | An architectural property where the Anthropic API retains zero memory between calls; the client must resend conversation history on every request. |
| **Model Spectrum** | Anthropic's tiered model portfolio (Haiku, Sonnet, Opus) optimized along the Pareto frontier of intelligence, speed, and cost. |
| **Tool Calling / Tool Use** | Enabling Claude to interface with external APIs, databases, and code runners by outputting structured JSON execution blocks. |
| **Model Context Protocol (MCP)** | An open standard protocol created by Anthropic that standardizes how AI applications connect to external tools, resources, and prompts. |
| **Prompt Caching** | An API capability that stores processed token prefixes in cache for up to 5 minutes (ephemeral), cutting costs by up to 90% and slashing latency. |

---

## 🎈 Stage 1 — The Simple Idea (Analogy: The Cognitive Engine in the Factory)

Using Claude through a web chat interface is like riding in a luxury passenger car: someone else configured the engine, set the dashboard, and handles the maintenance.

Building with the **Claude API** is like taking that high-performance engine out of the car and **mounting it into your own custom automated factory**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   THE FACTORY FLOOR (Claude API Pipeline)              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INGRESS & VALIDATION │ Secure API keys, enforce DLP, format JSON.   │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 2. MODEL ROUTING        │ Route lightweight tasks to Haiku; route      │
│                         │ complex architectural logic to Sonnet/Opus.  │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 3. TOOL EXECUTION LOOP  │ Let Claude invoke database queries, execute  │
│                         │ code in sandbox containers, and parse docs.  │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 4. EGRESS & VERIFICATION│ Stream tokens chunk-by-chunk to frontends,   │
│                         │ validate schemas, and log audit metrics.     │
└─────────────────────────┴───────────────────────────────────────────────┘
```

> **The "Aha!":** The API gives you programmatic leverage. You are no longer chatting with an assistant; **you are orchestrating an intelligent reasoning component inside distributed software**.

---

## ⚙️ Stage 2 — How the Curriculum Is Structured

This course covers the end-to-end engineering lifecycle across **13 comprehensive sections**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     COURSE 02 ARCHITECTURE ROADMAP                     │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 01–03: API FOUNDATIONS                                         │
│ • Model families (Haiku, Sonnet, Opus)                                 │
│ • Client setup, authentication, Messages API schema                    │
│ • Multi-turn state, system prompts, temperature, streaming, JSON        │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 04–05: EVALUATION & PROMPT TECHNIQUES                          │
│ • Building automated eval pipelines (code-based & model-based grading) │
│ • Precision prompting, XML tags, few-shot conditioning                 │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 06–07: TOOL USE & RAG                                          │
│ • Tool schemas, message blocks, tool results, multi-turn tool loops   │
│ • Text chunking, Voyage embeddings, vector search, BM25 hybrid RAG     │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 08: FRONTIER FEATURES                                          │
│ • Extended Thinking, Prompt Caching, Citations, Vision, Files API      │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 09–11: PROTOCOLS & AGENTS                                      │
│ • Model Context Protocol (MCP) clients, servers, resources, prompts    │
│ • Claude Code CLI, parallel git worktrees, computer use                │
│ • Workflow patterns (Chaining, Routing, Parallelization) vs. Agents    │
├────────────────────────────────────────────────────────────────────────┤
│ SECTION 12–13: CERTIFICATION & ASSESSMENT                              │
│ • Comprehensive final API assessment & course wrap-up                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Stage 3 — In Practice: Architectural Prerequisites

Before issuing your first API call, establish your engineering environment:

1. **SDK Availability:** Official SDKs are maintained for **Python** (`anthropic`), **TypeScript / JavaScript** (`@anthropic-ai/sdk`), **Go**, and **Ruby**.
2. **Security Baseline:** Never embed API keys in client-side code (browsers, mobile apps). All API calls must originate from your secure backend server.
3. **Stateless State Handling:** Understand that you must maintain the array of conversation messages in your own application database (Redis, Postgres) and provide it on each turn.

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     API ARCHITECTURE CHEAT SHEET                       │
├───────────────────────┬────────────────────────────────────────────────┤
│ Resource              │ Detail                                         │
├───────────────────────┼────────────────────────────────────────────────┤
│ Base Endpoint         │ `https://api.anthropic.com/v1/messages`        │
│ Authentication Header │ `x-api-key: $ANTHROPIC_API_KEY`                │
│ Version Header        │ `anthropic-version: 2023-06-01`                │
│ Core SDKs             │ Python (`pip install anthropic`), TypeScript   │
├───────────────────────┴────────────────────────────────────────────────┤
│ GOLDEN RULE: "Keep keys on the server; manage state in the database."  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 STOP — Self-Check: Exam-Style Question

An engineering team wants to add Claude to a React single-page application (SPA). A developer proposes installing the Anthropic TypeScript SDK directly in the React frontend and storing `ANTHROPIC_API_KEY` in client-side local storage to eliminate backend server costs.

Why must an architect reject this proposal?

- **A)** The Claude API does not support JSON payloads generated by React.
- **B)** Storing the API key in client-side code exposes the key to end users, allowing unauthorized API access, billing theft, and security compromise; all API requests must route through a secure backend proxy.
- **C)** React applications cannot handle streaming HTTP responses.
- **D)** Anthropic requires all API requests to originate from AWS IP addresses.

<details><summary>Click to view Answer & Detailed Explanation</summary>

### Correct Answer: **B**

### Architectural Breakdown:
- **Security Vulnerability:** Client-side bundles and local storage are readable by any end user using browser developer tools. Placing an Anthropic API key in client code compromises account security, leading to credential harvesting, quota exhaustion, and financial liability.
- **Production Architecture:** The client application must send user messages to a developer-controlled backend server. The backend validates user authentication, applies rate limits, and uses the secret API key to communicate with Anthropic.
- **Why A, C, and D are wrong:**
  - Option A is false; Claude accepts standard JSON payloads regardless of framework.
  - Option C is false; modern browsers handle Server-Sent Events (SSE) natively via `fetch()` and `ReadableStream`.
  - Option D is false; Anthropic accepts requests from any authenticated IP over HTTPS.

Ready for model selection? Continue to [Overview of Claude Models →](../02%20-%20Anthropic%20overview/01%20Overview%20of%20Claude%20models.md)
</details>
