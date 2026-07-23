# 04 — Fine-Tuning Overview

> Phase 4 · Module 4.4 · Lesson 4 · `[OPTIONAL — 🟢 conceptual awareness mandatory; hands-on optional]`

> ⚠️ Know when to fine-tune vs prompt/RAG, and SFT/DPO/LoRA. Fine-tuning before a working RAG = wrong order.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** When prompting + RAG aren't enough (consistent format/tone/domain skill), you
**fine-tune** — retrain on examples. But it's rarely the first answer: costly, freezes knowledge, needs
data. Architects must know *when* and the *methods*.

## 🔑 New Terms
**SFT** (prompt/completion pairs) · **DPO** (preference pairs, no reward model) · **LoRA/QLoRA** (train
tiny adapters, cheap) · when fine-tune vs prompt/RAG. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: prompt = instructions; RAG = give a textbook; fine-tune = send to school. School last, when behaviour must be innate. **Aha!:** RAG for knowledge, fine-tune for behaviour.

## ⚙️ Stage 2 — the methods (each a mini-reference)
- **SFT (Supervised Fine-Tuning)** — train on `{prompt, completion}` pairs (JSONL). **✅ Use when:** you want
  a consistent format/tone/skill baked in. **🚫 Avoid → RAG:** for facts/knowledge (use retrieval). **⚠️:** needs clean labelled pairs.
- **DPO (Direct Preference Optimisation)** — train on preference pairs (A better than B); no reward model.
  **✅:** aligning tone/quality from feedback. **🚫 → SFT:** when you have exact target outputs. **⚠️:** needs good pairs.
- **LoRA / QLoRA** — train tiny adapter weights instead of the whole model — cheap and fast. **✅:** most
  fine-tunes. **🚫 → full fine-tune:** rarely worth it. **⚠️:** adapters per task to manage.
Use OpenAI `fine_tuning.jobs.create()` or Azure ML; always re-evaluate base-capability regression afterwards.

> 🔬 Order: prompt → RAG → fine-tune (last). RAG adds *knowledge*; fine-tuning shapes *behaviour*. Fine-tuning before a working RAG is the wrong order.

## ⚖️ knowledge → RAG · format/skill → SFT · preference → DPO · cheap → LoRA. 🐛 FT for facts→use RAG; FT before RAG→wrong order. 📌 prompt→RAG→fine-tune; SFT/DPO/LoRA; re-eval regressions.
## 🛑 Want consistent JSON tone — fine-tune or RAG? <details><summary>A</summary>**SFT (LoRA)** — that's behaviour/format. RAG adds knowledge, not style. Get RAG right first.</details>

⏭️ **Next:** 05 — 🏁 Milestone.
