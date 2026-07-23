# ⚪ Phase 0.0 — Conceptual Foundations (before any code)

Reading-only background — the mental models that make Phases 0–5 make sense. **No Python here.**
Taught novice-first using the *conceptual* variant of the lesson template (Common Misconceptions
instead of code errors, small diagrams, and "explain-why" self-checks). Any new jargon links the
[AI Terms — Plain-English Glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).

> Why this matters: without these mental models, Phase 1 feels like a foreign language. This phase
> is vocabulary + history + how the pieces fit — the foundation everything else builds on.

## Modules (in order)

- [ ] [0.0.1 — What Is an AI Model? (Parameters & Weights)](0.0.1%20What%20Is%20an%20AI%20Model.md)
- [ ] [0.0.2 — How AI Got Here (Model Evolution Timeline)](0.0.2%20How%20AI%20Got%20Here.md)
- [ ] [0.0.3 — Encoder vs Decoder (the split that matters for RAG)](0.0.3%20Encoder%20vs%20Decoder.md)
- [ ] [0.0.4 — The Model Lifecycle (who does what — and what *your* job is)](0.0.4%20The%20Model%20Lifecycle.md)
- [ ] [0.0.5 — Core Vocabulary (tokens, context window, temperature, hallucination…)](0.0.5%20Core%20Vocabulary.md)
- [ ] [0.0.6 — The AI Landscape (types of models, when to use each)](0.0.6%20The%20AI%20Landscape.md)
- [ ] [0.0.7 — How a Transformer Works (conceptual deep-dive)](0.0.7%20How%20a%20Transformer%20Works.md) — *recommended; opens the "black box," best read after 0.0.3*

## Optional deep-dives (clearly optional — awareness, not required for your roles)

> Marked **optional** so you can choose — but the content is **here, not skipped**. These add depth
> that ML-engineer/researcher roles use; for AI engineer/architect they're awareness + interview bonus.

- [ ] [(Optional) 0.0.8 — How Models Learn: The Training Loop](0.0.8%20Optional%20-%20The%20Training%20Loop.md)
- [ ] [(Optional) 0.0.9 — Encoder-Decoder & Cross-Attention](0.0.9%20Optional%20-%20Encoder-Decoder%20and%20Cross-Attention.md)

**Your own gold-standard internals notes (now numbered here):**
- [ ] [(Optional) 0.0.10 — Transformers: Full Internals](0.0.10%20Optional%20-%20Transformers%20Full%20Internals.md) — Q/K/V attention, positional encoding, FFN, numerical traces.
- [ ] [(Optional) 0.0.11 — Model Creation: Full Internals](0.0.11%20Optional%20-%20Model%20Creation%20Full%20Internals.md) — BPE tokenizer, parameter matrices, the full training loop.
- [ ] [(Optional) 0.0.12 — Model Usage: Full Internals](0.0.12%20Optional%20-%20Model%20Usage%20Full%20Internals.md) — frozen weights, autoregressive loop, cross-attention.

## ✅ Completion check — answer all 8 without notes

1. What is a parameter, and why does a 70B model cost more than a 7B?
2. Why did the industry move from RNNs to transformers?
3. Which model family do you use for RAG embeddings, and why can't it generate text?
4. Fine-tuning vs RAG — what's the difference, and when do you choose each?
5. What does Temperature = 0 do, and when do you set it in an agent?
6. What is Top-P, and how does it differ from Temperature?
7. Why does hallucination happen, and how does RAG reduce it?
8. Closed vs open-weight model — the difference, and when an enterprise picks open-weight?

> Pass all 8 and Phase 0.0 is done — on to Phase 0 (Python), which you've already covered.
