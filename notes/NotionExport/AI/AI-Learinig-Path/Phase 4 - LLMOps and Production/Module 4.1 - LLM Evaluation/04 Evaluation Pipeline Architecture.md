# 04 — Evaluation Pipeline Architecture

> Phase 4 · Module 4.1 · Lesson 4 · `[ARCHITECT BONUS — 🟡 SHOULD; eval-driven development]`

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** One-off evals don't keep quality. Architects build an **eval pipeline**: a
versioned golden dataset, evals before prompts (eval-driven dev), shadow runs on prod traffic, and AI
SLOs that gate releases. This is the differentiator interviewers probe.

## 🔑 New Terms
**Golden dataset** (versioned test cases in git) · **Shadow eval** (new version on live traffic in
parallel) · **online vs offline** eval · **eval-driven dev** (evals first) · **AI SLO** (hallucination/
grounding/latency targets). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: QA for AI — a fixed test suite (golden set), shadow-test new builds beside prod, ship only if SLOs hold. **Aha!:** write evals *before* prompts.

## ⚙️ Stage 2 — How It Works (the four pieces, each a mini-reference)

#### Golden dataset — a versioned regression suite in git
- **What & why:** a curated set of test cases (question + ideal answer/context) committed to git, so quality
  has a fixed yardstick that grows over time. **✅ Use when:** any system you'll change more than once.
  **🚫 Avoid → ad-hoc spot checks:** they don't catch regressions. **⚠️ Gotcha:** it goes stale — review
  quarterly and **add every production bug as a new case** so the same failure can't return.

#### Eval-driven development — write the evals first
- **What & why:** define the metrics and golden cases **before** writing prompts, then iterate the prompt
  until it passes (TDD for LLMs). **✅ Use when:** building a new feature/flow. **🚫 Avoid → prompt-then-pray:**
  tweaking blindly with no target. **⚠️:** resist editing the test to match the model — that hides regressions.

#### Shadow evaluation — test on real traffic without serving it
- **What & why:** run a new model/prompt **in parallel** on live production traffic, compare its metrics to
  the current version, but **don't return** its output to users. **✅ Use when:** validating a change at real-
  world scale. **🚫 Avoid → offline-only:** when you have no representative traffic. **⚠️:** doubles calls — **sample**.

#### AI SLOs — the release gate
- **What & why:** explicit targets (e.g. faithfulness > 0.85, P99 latency < 2 s, hallucination < 2%) that a
  release must meet to ship. **✅ Use when:** gating deploys in CI. **🚫 Avoid → shipping on vibes:** no bar = silent
  drift. **⚠️:** set thresholds from a measured **baseline**, not wishes.

**Online vs offline:** *offline* = batch the golden set in CI; *online* = monitor prod live (+ shadow). You want both.

> 🔬 **Under the hood:** the pipeline is git golden set → CI runs RAGAS/DeepEval → shadow on live traffic →
> SLO gate → promote. Scores are tracked **per release like latency** — quality becomes a first-class metric.

## 🚀 Stage 3 — In Practice / Why It Matters
This is the difference interviewers probe between "I built a RAG demo" and "I run RAG in production." A Lead
keeps a versioned golden set, writes evals before prompts, shadow-tests every candidate against live traffic,
and blocks releases that miss the SLOs — so quality can't silently regress between sprints. It's the same
discipline as SRE error-budgets, applied to AI quality.

## ⚖️ Variations & When to Use
| Stage | Use | Why |
|---|---|---|
| In CI, before merge | **offline** eval on golden set | fast, deterministic regression gate |
| Validating at scale | **shadow** eval on prod traffic | real distribution, zero user risk |
| Deciding to ship | **AI SLO** gate | one objective pass/fail bar |
| Catching live drift | **online** monitoring | quality changes after deploy too |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Old bugs keep returning | golden set never grows | add every prod failure as a case; review quarterly |
| Ship-then-discover-broken | no eval-first discipline | write evals + golden cases before prompts |
| A bad version reached users | no shadow/SLO gate | shadow-test, gate on SLOs before promote |
| "Tests pass" but users unhappy | test tuned to the model | freeze the test; fix the system |

## 📌 Quick Reference
- **Four pieces:** golden dataset (git) · eval-driven dev (evals first) · shadow eval (live traffic, not served)
  · AI SLOs (release gate).
- **Offline** = CI on golden set; **online** = live monitoring + shadow. Track scores **per release**.
- Add every production bug to the golden set; set SLOs from a baseline.

## 🛑 STOP — Self-Check
You want to test a new model on **real production patterns** without risking a single user. Which technique?

<details><summary>Answer</summary>

**Shadow evaluation** — run the new model **in parallel** on live production traffic, compare its metrics
(faithfulness, latency, etc.) against the current version, but **don't serve** its output to users. You get a
real-world quality read with zero user exposure, and promote it only if it clears your **AI SLOs**.
</details>

⏭️ **Next:** Module 4.2 — LangSmith observability.
