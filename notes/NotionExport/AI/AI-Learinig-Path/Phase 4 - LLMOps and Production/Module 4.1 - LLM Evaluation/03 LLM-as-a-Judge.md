# 03 — LLM-as-a-Judge Patterns

> Phase 4 · Module 4.1 · Lesson 3 · `[JD VERIFIED — the engine behind RAGAS/DeepEval]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Both RAGAS and DeepEval are *built on* one idea: when there's no exact-match key, you
**ask another LLM to grade**. It scales infinitely and reads nuance — but it has biases (favours longer or
first answers, even its own outputs). Knowing the modes (pointwise/pairwise), how to write a rubric, and how
to neutralise bias is what makes the score *trustworthy* — and is itself a JD topic.

**Why care:** every eval tool is a judge under the hood; judging well is the architect-level eval skill.

## 🔑 New Terms (plain English)
- **Pointwise** — judge scores one answer absolutely (0–10). **Pairwise** — judge picks A vs B (preference).
- **Reference-based** — judge compares answer to a gold answer. **Rubric** — the written grading criteria.
- **Position bias** (favours first), **verbosity bias** (favours longer), **self-preference** (favours own
  family). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Idea (analogy: a cooking-contest judge)
Score each dish 1–10 (pointwise), or taste two and pick the better (pairwise). A clear scorecard (rubric)
and fair tasting order keep it honest. **Aha!:** an LLM scales human judging to thousands of cases — *if* you
control its biases.

## ⚙️ Stage 2 — How It Works

### 2.1 The three judging modes (each a mini-reference)

#### Pointwise — score one answer absolutely
- **What & why:** the judge reads one answer and a rubric and gives a number (e.g. 0–10). Simplest; the basis
  of metric dashboards. **Syntax (sketch):** prompt = rubric + answer → "score 1–10 + reason".
- **✅ Use when:** tracking an absolute quality number over time, or threshold gates in CI.
- **🚫 Avoid → pairwise:** comparing two prompts/models (absolute scores wobble between versions).
- **⚠️ Gotcha:** scores drift when you change the judge model — pin the judge model + version.

#### Pairwise — pick A vs B
- **What & why:** show the judge both answers, ask which is better. The most reliable signal for choices.
- **✅ Use when:** A/B-testing a prompt or model. **🚫 Avoid → pointwise:** when you need a standalone number.
- **⚠️ Gotcha:** position bias (favours the first) — run both orders and average.

#### Reference-based — compare to a gold answer
- **What & why:** judge scores the answer against a known-correct reference. **✅:** correctness with labels.
  **🚫 → open-ended:** no gold answer exists. **⚠️:** needs a labelled set.

### 2.2 Writing a rubric + killing bias
A good rubric is **specific and scaled**: "5 = every claim grounded; 3 = minor gap; 1 = fabricated," one
criterion at a time. Three biases to neutralise: **position** (randomise/average A-B order), **verbosity**
(cap or normalise length so longer ≠ better), **self-preference** (don't grade GPT with GPT). Right-size the
judge: GPT-4o for hard calls, gpt-4o-mini for routine. Always **validate the judge against ~50 human labels**.

> 🔬 A judge = LLM + rubric prompt → score or choice. Quality depends entirely on rubric clarity + bias control.

## 🚀 Stage 3 — In Practice / Why It Matters
Every eval tool you use is a judge underneath: **RAGAS** faithfulness is a pointwise judge over claims;
**DeepEval**'s G-Eval is a pointwise rubric judge; model leaderboards are **pairwise** judges. In production
you'll pointwise-score quality nightly for the dashboard, and pairwise whenever you choose between two prompts
or models (the most trustworthy signal). The architect move is to **validate the judge itself**: sample ~50
cases, have a human grade them, and check the judge agrees — an unvalidated judge is just a confident guess.

## ⚖️ Variations & When to Use
| The decision is… | Mode | Why / trade-off |
|---|---|---|
| Track one quality number over time | **Pointwise** | absolute score for dashboards + CI gates |
| Choose between prompt A and prompt B | **Pairwise** | direct comparison — strongest, most stable signal |
| Grade against a known-correct answer | **Reference-based** | objective when you have labels |
| Hard / high-stakes call | frontier judge (GPT-4o) | accuracy over cost |
| Routine, high-volume scoring | mini judge (gpt-4o-mini) | cost over nuance |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| First answer keeps "winning" | position bias | run **both orders**, average |
| Longer answers always score higher | verbosity bias | cap/normalise length in the rubric |
| Scores drift between runs | judge model changed | **pin** judge model + version |
| Judge favours its own family | self-preference | don't grade GPT with GPT; cross-judge |
| Scores don't match reality | unvalidated judge | correlate against ~50 human labels |

## 📌 Quick Reference
- **Modes:** pointwise (absolute number) · pairwise (A vs B, strongest) · reference-based (vs gold).
- **Rubric:** specific + scaled, one criterion at a time ("5 = every claim grounded; 1 = fabricated").
- **Kill 3 biases:** position (swap+average) · verbosity (normalise length) · self-preference (cross-judge).
- **Right-size:** frontier for hard calls, mini for routine. **Always validate vs ~50 human labels.**

## 🛑 STOP — Self-Check
You're A/B-testing two system prompts. Which judging mode, and what's the one bias you must guard against first?

<details><summary>Answer</summary>

**Pairwise** — show the judge both answers and ask which is better; it's the most stable signal for a choice
(absolute pointwise scores wobble between versions). The first bias to neutralise is **position bias** (the
judge tends to favour whichever answer it sees first) — run **both orderings and average**, so the winner
isn't just "the one we listed first."
</details>

⏭️ **Next:** 04 — Eval pipeline architecture.
