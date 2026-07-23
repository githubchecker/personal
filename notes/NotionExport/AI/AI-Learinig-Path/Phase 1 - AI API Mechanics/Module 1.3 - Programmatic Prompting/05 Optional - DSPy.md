# 05 — (Optional) DSPy: Programming, Not Prompting

> Phase 1 · Module 1.3 · Lesson 5 · `[OPTIONAL — awareness]`

> 🟡 **Optional / awareness.** Appears in ~15–25% of (research-leaning) JDs and is an emerging
> approach. Know **what it is and the problem it solves** — that's enough here. Reach for it once you
> have evaluation data (Phase 4) and are tired of hand-tuning prompts.

## 🗺️ Stage 0 — Concept Map

Everything in this module so far has you **writing prompts by hand**. **DSPy** (from Stanford) flips
that: you **declare what you want** and let DSPy **generate and optimize the prompts for you** from
examples and a metric. It builds on structured outputs (lesson 01) and the reasoning patterns (lesson
03), and connects to evaluation (Phase 4).

## 🔑 New Terms (plain English)

- **DSPy** — a framework for "**programming, not prompting**" language models.
- **Signature** — a declarative spec of a step's **inputs → outputs** (e.g. `question -> answer`).
- **Module** — a building block that runs a signature (e.g. `dspy.Predict`, `dspy.ChainOfThought`).
- **Optimizer (compile)** — an algorithm that **auto-tunes** the prompts (and few-shot examples) using
  your training examples + a **metric**.

## 🎈 Stage 1 — The Simple Idea (analogy: a compiler for prompts)

Hand-tuning prompts is like writing **assembly** — fiddly and brittle. DSPy is a **compiler**: you
write **what** you want in high-level terms (a signature), and DSPy **compiles** it into an optimized
prompt, automatically trying variations and picking what scores best on your examples.

**The "Aha!":** instead of *you* guessing prompt wording, DSPy **optimizes the prompt with data** —
the same way you'd tune model hyperparameters rather than hand-pick them.

## ⚙️ Stage 2 — How It Actually Works (awareness)

```python
# pip install dspy
import dspy

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))     # pick a model

# 1) Declare the task as a SIGNATURE (inputs -> outputs), not a prompt:
class Answer(dspy.Signature):
    """Answer a question concisely."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

# 2) Pick a MODULE that runs it (ChainOfThought adds reasoning automatically):
qa = dspy.ChainOfThought(Answer)
print(qa(question="What's the capital of France?").answer)   # DSPy builds the actual prompt for you

# 3) (Optional) OPTIMIZE: give examples + a metric, and DSPy tunes the prompt automatically.
#    (Optimizers are also called "teleprompters".)
#    optimizer = dspy.MIPROv2(metric=my_metric)   # or dspy.BootstrapFewShot(metric=my_metric)
#    compiled_qa = optimizer.compile(qa, trainset=examples)
```

You never wrote the prompt text — DSPy generated it from the **signature**, and an **optimizer** can
improve it using **data**.

### When to use it
- You have **evaluation examples + a metric** (Phase 4) and want to stop hand-tuning prompts, or you're
  building a **multi-step pipeline** (RAG/agent) where prompts interact.
- **Overkill** for a simple single prompt — hand-written prompts (lessons 01–04) are simpler there.

## 🧠 Common Misconceptions

- **"DSPy replaces prompting entirely."** → You still design signatures and pipelines; DSPy automates
  the *wording/optimization*, not the *thinking*.
- **"It works without data."** → Its superpower (optimization) needs **examples + a metric**. Without
  them you just get sensible default prompts.

## 📌 Quick Reference

- **DSPy = programming, not prompting:** declare **signatures** (in→out), run via **modules**
  (`Predict`, `ChainOfThought`), **optimize** with **teleprompters** (`BootstrapFewShot`, `MIPROv2`)
  from examples + a metric.
- Use when you have **eval data** / multi-step pipelines; skip for simple single prompts.

## 🛑 STOP — Self-Check

What does DSPy automate that you'd otherwise do by hand in lessons 01–04 — and what do you still have
to provide for that automation to work well?

<details><summary>Answer</summary>

DSPy automates **writing and optimizing the prompt text** (including choosing few-shot examples): you
declare a **signature** (inputs → outputs) and a **module**, and an **optimizer** tunes the actual
prompt for you. For that optimization to work, **you must still provide training examples and a
metric** (a way to score outputs — Phase 4); without data it can only give sensible default prompts,
not optimized ones.
</details>

---
🎉 **Module 1.3 (Programmatic Prompting) complete** — and with it the **learning** of Phase 1. You can
force structured outputs, manage prompts as versioned code, apply few-shot/CoT/ReAct, engineer the
context window, and know where DSPy fits. Next: the **Phase 1 Milestone — a FastAPI AI Gateway** that
ties Modules 1.1–1.3 together (streaming, multi-provider, validation, tools).
