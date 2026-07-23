# 02 — DeepEval: Pytest for LLMs

> Phase 4 · Module 4.1 · Lesson 2 · `[JD VERIFIED — unit-test your LLM app]`

> 🔬 DeepEval `4.x`. Pytest-style LLM eval; pairs with RAGAS.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** RAGAS gives you batch RAG scores. But you also want LLM quality wired into the same
**test suite** your code already uses — so a bad prompt change fails CI like a broken function. **DeepEval**
is "Pytest for LLMs": write `LLMTestCase`s, attach metrics, and `assert_test` thresholds — run with
`deepeval test run`. Its standout is **G-Eval**: describe *any* quality bar in plain English and an LLM grades
to it, so you're not limited to pre-built metrics. Where RAGAS is RAG-specific, DeepEval covers RAG, agents,
and chatbots.

**Why care:** ~the named eval framework alongside RAGAS; converts "vibe checks" into CI gates.

## 🔑 New Terms (plain English)
- **`LLMTestCase`** — one case: `input`, `actual_output`, optional `expected_output`, `retrieval_context`.
- **G-Eval** — a custom metric you define by writing **criteria in English**; an LLM scores 0–1 to it.
- **`AnswerRelevancyMetric` / `FaithfulnessMetric` / `HallucinationMetric` / `ContextualRecallMetric`** —
  ready-made metrics. **DAG** — a deterministic decision-tree metric (rule-based judging).
- **`assert_test`** — fail a pytest if metrics are below threshold. **RedTeamer** — auto adversarial probes.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Idea (analogy: pytest where assertions are graded by a judge)
Normal tests assert `==`. LLM output has no single right string — so the "assertion" is *"is this grounded /
correct / on-tone?"* graded by an LLM. **Aha!:** evals become ordinary CI tests; a quality regression turns
the build red.

## ⚙️ Stage 2 — How It Works

### 2.1 The shape: a test case + metrics, asserted like pytest

```python
# pip install deepeval ; export OPENAI_API_KEY=...
from deepeval import assert_test
from deepeval.metrics import GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

correctness = GEval(                                   # a custom metric defined in plain English
    name="Correctness",
    criteria="Is the 'actual output' factually correct compared to the 'expected output'?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.5)                                     # below 0.5 = fail

def test_refund():                                     # a normal pytest function
    tc = LLMTestCase(
        input="What's the refund window?",             # the question
        actual_output="You can refund within 30 days.",# what YOUR app produced
        expected_output="30-day full refund",          # the ideal answer
        retrieval_context=["30-day full refund"])      # chunks RAG retrieved (for RAG metrics)
    assert_test(tc, [correctness, AnswerRelevancyMetric(threshold=0.7)])   # fails build if below
# run:  deepeval test run test_file.py
```

A `LLMTestCase` is one row; you attach metrics; `assert_test` turns it into a pass/fail. Run with
`deepeval test run` and it behaves like pytest — green or red — so a prompt change that drops quality
**fails CI** just like a broken function.

### 2.2 The four kinds of metric (each a mini-reference)

#### G-Eval — your own rubric, in English
- **What & why:** you describe the bar ("is it polite and on-brand?"); an LLM scores 0–1 to it. Covers what
  no pre-built metric does. **Key features:** plain-English criteria; any params; explanations included.
- **✅ Use when:** bespoke quality (tone, format, correctness). **🚫 Avoid → ready metric:** standard RAG
  checks already exist. **⚠️ Gotcha:** vague criteria = noisy scores — be specific and set a threshold.

#### Ready-made metrics — the common bars off the shelf
- **What & why:** `AnswerRelevancyMetric`, `FaithfulnessMetric`, `HallucinationMetric`, `ContextualRecallMetric`.
- **✅ Use when:** standard RAG quality. **🚫 Avoid → G-Eval:** anything custom. **⚠️:** tune thresholds per app.

#### DAG — deterministic, rule-based judging
- **What & why:** a decision tree (e.g. "must contain a disclaimer → pass"). Predictable, no LLM wobble.
- **✅ Use when:** hard rules. **🚫 → G-Eval:** fuzzy quality. **⚠️:** you build the tree.

#### RedTeamer — adversarial probes
- **What & why:** auto-generates jailbreak/PII attacks to test safety (ties to Phase 4.3). **✅:** security
  testing. **🚫 → functional metrics:** correctness. **⚠️:** review flagged cases by hand.

Notebook style: `evaluate([tc], [metric])` (no pytest). Confident-AI platform shares datasets/reports.

> 🔬 **Under the hood:** every metric is either an LLM-as-judge (Lesson 03) or an NLP score; `deepeval test
> run` is a pytest plugin, so eval slots straight into existing CI with pass/fail + reports.

## 🚀 Stage 3 — In Practice
Teams keep RAGAS for batch RAG dashboards and DeepEval for **CI gates** — a G-Eval rubric per requirement,
asserted in pytest, blocking merges that regress quality.

## ⚖️ Variations & When to Use
| Need | Metric | Why |
|---|---|---|
| Custom bar (tone/format) | **G-Eval** | rubric in English |
| Standard RAG | ready metrics | off the shelf |
| Hard rule | DAG | deterministic |
| Safety | RedTeamer | adversarial |
| RAGAS vs DeepEval | both | RAGAS scores, DeepEval gates |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Noisy scores | vague G-Eval criteria | be specific; add steps |
| Nothing ever fails | no threshold | set `threshold=` |
| Costly | GPT-4o judge | gpt-4o-mini routine |

## 📌 Quick Reference
`LLMTestCase(input,actual_output,expected_output,retrieval_context)` + metric + `assert_test`; G-Eval for
custom; `deepeval test run`; DAG deterministic; RedTeamer security.

## 🛑 STOP — RAGAS vs DeepEval? <details><summary>A</summary>RAGAS = RAG-specific batch metrics + dashboards; DeepEval = pytest-style CI gates + custom G-Eval. Use both — RAGAS measures, DeepEval fails the build.</details>

⏭️ **Next:** 03 — LLM-as-a-Judge.
