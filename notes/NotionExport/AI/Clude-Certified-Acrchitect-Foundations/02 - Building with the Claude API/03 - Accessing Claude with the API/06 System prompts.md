# 06 — System Prompts

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 6 of 10 · [← Prev: Chat Exercise](05%20Chat%20exercise.md) · [Course Index](../README.md) · [Next: System Prompts Exercise →](07%20System%20prompts%20exercise.md)

---

## 🗺️ Concept Overview

System prompts are a powerful way to customize how Claude responds to user input. Instead of receiving generic answers, you can shape Claude's tone, style, and approach to match your specific application requirements.

![System Prompts Overview](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623273%2F03_-_006_-_System_Prompts_00.1748623272065.png)

---

## 🎯 Why System Prompts Matter

Consider building a math tutor chatbot. When a student asks: *"How do I solve $5x + 2 = 3$ for $x$?"*, you want Claude to act like an authentic, pedagogical tutor rather than just spitting out the solution.

### A Good Math Tutor Should:
- Initially provide hints rather than complete solutions.
- Patiently walk students through problems step by step.
- Demonstrate solutions for similar problems as illustrative examples.

### A Good Math Tutor Should NOT:
- Immediately hand over direct answers.
- Tell students to just use a calculator.

A system prompt enforces these behavioral boundaries and sets the operational persona before the user even enters their prompt.

---

## ⚙️ How System Prompts Work

System prompts provide Claude with top-level operational guidance on **how** to respond:

![How System Prompts Work](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623273%2F03_-_006_-_System_Prompts_05.1748623273817.png)

- **Role Guidance:** Claude attempts to respond in the exact manner of someone operating in the specified role.
- **Focus:** Helps keep Claude strictly on-task across multi-turn interactions.
- **API Implementation:** You define the system prompt as a plain string and pass it directly into the `client.messages.create()` function using the dedicated `system` parameter:

```python
system_prompt = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""

response = client.messages.create(
    model=model,
    messages=messages,
    max_tokens=1000,
    system=system_prompt
)
```

---

## 🔍 Seeing the Difference in Practice

### Without a System Prompt (Default Behavior)
If you send *"How do I solve 5x + 2 = 3 for x?"* without a system prompt:
> **Claude:** *"To solve $5x + 2 = 3$ for $x$:\n1. Subtract 2 from both sides: $5x = 1$\n2. Divide by 5: $x = 1/5$ or $0.2$."*

*Outcome:* The full answer is given immediately, eliminating the student's opportunity to reason through the problem.

### With the Math Tutor System Prompt
With the system prompt applied:
> **Claude:** *"Let's work through this together! Our goal is to isolate the $x$ term. What do you think would be a good first step to start moving terms away from $5x$ on the left side of the equation?"*

*Outcome:* Claude guides the student constructively using Socratic scaffolding.

---

## 🛠️ Building a Flexible Chat Function

Rather than hard-coding system prompts or creating separate functions for every persona, you can build a reusable `chat` helper that accepts an optional `system` parameter:

```python
def chat(messages: list, system: str | None = None) -> str:
    # 1. Base parameters dictionary
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }
    
    # 2. Conditionally inject system prompt only when provided
    if system:
        params["system"] = system
    
    # 3. Unpack parameters cleanly into client.messages.create
    message = client.messages.create(**params)
    return message.content[0].text
```

> [!NOTE]
> **API Parameter Handling:** The Anthropic API does not accept `system=None`. Passing `system=None` directly can trigger validation errors. Conditionally injecting the key into a dictionary and using `**params` unpacking cleanly handles this edge case.

### Using the Flexible Chat Function:

```python
# 1. Without system prompt (default assistant behavior)
answer_default = chat(messages)

# 2. With customized persona system prompt
tutor_system = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""
answer_tutored = chat(messages, system=tutor_system)
```

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM PROMPTS CHEATSHEET                       │
├───────────────────────┬────────────────────────────────────────────────┤
│ Primary Role          │ Sets persona, tone, style, and constraints     │
│ API Parameter         │ Top-level `system="..."` in create function    │
│ Data Type             │ Plain string (`str`)                           │
│ Handling None         │ Exclude the parameter entirely via `**params`  │
│ Position in Memory    │ Stays active across all message turns          │
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
What happens if you pass `system=None` directly as an explicit keyword argument into `client.messages.create(system=None)`?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** It triggers an API validation error. The Anthropic API expects either a valid string for the `system` parameter or for the parameter to be omitted entirely. Using dictionary unpacking (`**params`) or `anthropic.NOT_GIVEN` ensures `None` values are never sent over the wire.
</details>

---

### Question 2
What is the core distinction between the purpose of the `system` prompt and the user messages list in a Claude application?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** The `system` prompt defines **how** Claude should behave, think, and format its answers (role, persona, constraints), whereas user messages provide **what** specific problem, text, or task Claude is being asked to address in that exchange.
</details>
