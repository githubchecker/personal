# 01 — RAGAS: RAG Evaluation Metrics

> Phase 4 · Module 4.1 · Lesson 1 · `[JD VERIFIED — eval is the "hardest skill to fake"]`

> 🔬 **Currency:** RAGAS `0.4.x`. Builds on Phase 2 §5.7 (the four metrics) — here we go deep + CI.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** You built RAG (Phase 2) and agents (Phase 3). Are they *good*? "Looks fine" isn't
shippable. You need **numbers** — and unlike unit tests, answers are fuzzy. **RAGAS** scores a RAG system
on four metrics (using an LLM-as-judge), and generates a synthetic test set so you don't hand-label. Wire
it into CI and a quality drop **fails the build** — eval becomes a regression test.

**Why care:** eval is the top Lead/Architect differentiator; RAGAS is the named RAG-eval tool.

## 🔑 New Terms
**Faithfulness** (answer grounded in context? = hallucination check) · **Answer relevancy** (addresses
the question?) · **Context precision** (retrieved chunks relevant/ranked?) · **Context recall** (got all
needed context?) · **TestsetGenerator** (auto synthetic Q/A from your docs). ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea (analogy: grading a student two ways)
Grade the **answer** (relevant? truthful?) and grade their **research** (right pages, all of them). RAGAS:
generation metrics (faithfulness/answer-relevancy) + retrieval metrics (context-precision/recall). **Aha!:**
low faithfulness + high recall = good docs, model ignored them → fix the prompt, not retrieval.

## ⚙️ Stage 2 — How It Actually Works

### 2.1 One sample, scored four ways (fully commented)

```python
# pip install ragas langchain-openai
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithReference, LLMContextRecall
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

judge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))   # the grader model

dataset = EvaluationDataset.from_list([{                        # one row per test question
    "user_input":        "What's the refund window?",          # the question
    "retrieved_contexts":["Refunds within 30 days of delivery."], # what your retriever returned
    "response":          "You can refund within 30 days.",     # what your RAG answered
    "reference":         "30 days from delivery.",             # the ideal answer (for recall)
}])

result = evaluate(dataset, metrics=[Faithfulness(), ResponseRelevancy(),
                                    LLMContextPrecisionWithReference(), LLMContextRecall()], llm=judge)
print(result)   # -> {'faithfulness':1.0,'answer_relevancy':0.96,'context_precision':1.0,'context_recall':1.0}
```

Each metric returns 0–1. You don't assert exact text — you assert a **threshold** (e.g. faithfulness ≥ 0.85).

### 2.2 The four metrics (each a mini-reference)

#### Faithfulness — generation
- **What & why:** fraction of answer claims supported by the context. Your hallucination alarm.
- **✅ Use when:** always — the single most important production metric. **🚫 Low → fix:** prompt the model
  to "answer only from context," or improve grounding; *not* a retrieval problem. **⚠️ Gotcha:** very short
  answers can score deceptively high (few claims to check).

#### Response relevancy — generation
- **What & why:** does the answer address the asked question (penalises waffle/partial answers).
- **✅ Use when:** answers drift off-topic. **🚫 Low → fix:** tighten the prompt. **⚠️:** a correct-but-terse
  answer may dip; read alongside faithfulness.

#### Context precision — retrieval
- **What & why:** are relevant chunks ranked **high** (low noise at top). **✅:** judging your reranker
  (Phase 2.3). **🚫 Low → fix:** add/upgrade reranking. **⚠️:** precision can be high while recall is low.

#### Context recall — retrieval
- **What & why:** did you retrieve **all** needed context (needs a `reference`). **✅:** judging chunking +
  top-k. **🚫 Low → fix:** chunking/k/embeddings. **⚠️:** requires reference answers.

### 2.3 Generate a test set instead of hand-writing one

```python
from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
gen = TestsetGenerator.from_langchain(ChatOpenAI(model="gpt-4o-mini"), OpenAIEmbeddings())
testset = gen.generate_with_langchain_docs(docs, testset_size=50)   # 50 synthetic Q/A from YOUR docs
```

This builds varied questions (simple, multi-hop, reasoning) so you measure real coverage, not 5 hand cases.

### 2.4 The CI gate (eval as a unit test)

```python
def test_rag_quality():
    res = evaluate(dataset, metrics=[Faithfulness(), LLMContextRecall()], llm=judge)
    assert res["faithfulness"] >= 0.85       # build FAILS if grounding regresses
    assert res["context_recall"] >= 0.80
```

> 🔬 **Under the hood.** Each metric is an LLM-as-judge prompt over (question, contexts, answer): faithfulness
> extracts claims and checks each against context; recall checks reference sentences against retrieved chunks.
> So scores cost model calls and wobble ±a few % — fix a judge model+version, average over a real set (50+),
> and treat thresholds as ranges, not absolutes.

## 🚀 Stage 3 — In Practice / Why It Matters

Production teams generate a 50–200 Q/A set, score it nightly + in CI, and gate deploys on faithfulness and
context-recall. Track scores per release like latency. The decoupling is the architect payoff: **context
precision/recall grade retrieval; faithfulness/relevancy grade generation** — so the dashboard says *where*
to invest. RAGAS is "done" when a regression fails a build automatically.

## ⚖️ Variations & When to Use

| Score pattern | Diagnosis | Fix |
|---|---|---|
| Low faithfulness, high recall | model ignores good context | prompt/model (generation) |
| Low recall | needed chunks not retrieved | chunking, k, embeddings |
| Low precision, ok recall | right chunks buried in noise | reranking (Phase 2.3) |
| Low relevancy, ok faithfulness | on-source but off-question | prompt focus |
| RAGAS vs DeepEval | batch RAG metrics vs pytest gates | both — RAGAS scores, DeepEval gates |

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Scores swing run-to-run | judge non-determinism | pin judge model+version; average over 50+ |
| `context_recall` errors | no `reference` | add reference answers (or TestsetGenerator) |
| All ~1.0 | trivial cases | generate harder multi-hop set |
| Slow/costly | big set + GPT-4o judge | sample; gpt-4o-mini judge for routine |

## 📌 Quick Reference

```python
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithReference, LLMContextRecall
evaluate(EvaluationDataset.from_list(rows), [Faithfulness(), ResponseRelevancy(),
         LLMContextPrecisionWithReference(), LLMContextRecall()], llm=judge)
# TestsetGenerator.from_langchain(...).generate_with_langchain_docs(docs, 50); assert score>=0.85 in CI
```
Generation = faithfulness/relevancy · retrieval = precision/recall · gate CI on thresholds · pin the judge.

## 🛑 STOP — Self-Check

Faithfulness 0.6, context-recall 0.95. Where's the bug, and which lever do you pull?

<details><summary>Answer</summary>

**Generation.** Recall 0.95 = retrieval fetched the right context; faithfulness 0.6 = the model isn't
grounding its answer in it (hallucinating). Fix the **prompt/model** (force "answer only from context",
maybe a stronger model) — *not* the retriever. That decoupling is exactly why you keep both metric families.
</details>

⏭️ **Next:** 02 — **DeepEval** (pytest-style LLM testing + custom G-Eval rubrics).
