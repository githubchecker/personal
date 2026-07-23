# Phase 4 — LLMOps, Security & Production Engineering

> **Where AI systems become trustworthy.** Eval design is the "hardest skill to fake" and the top
> portfolio differentiator at Lead/Architect level. This phase hardens, evaluates, monitors, secures,
> and cost-optimises everything built in Phases 1–3 — to the same reference-grade bar.

---

## 🔭 Topic & subtopic explorer (JD-verified + standard-course cross-checked)

**Research-first:** Road Map anchored, then validated against the live tools (mid-2026): **RAGAS 0.4.x**,
**DeepEval 4.x**, **LangSmith**, **NeMo Guardrails 0.22**, **Presidio 2.2.363**, **LiteLLM 1.90**.

| # | Lesson | Importance | JD signal |
|---|--------|-----------|-----------|
| **4.1** | **LLM Evaluation & Continuous Testing** | | *"hardest to fake" — top differentiator* |
| 4.1.01 | RAGAS — RAG metrics + synthetic data + CI | 🔴 MUST | high |
| 4.1.02 | DeepEval — pytest for LLMs, G-Eval | 🔴 MUST | high |
| 4.1.03 | LLM-as-a-Judge patterns | 🔴 MUST | high |
| 4.1.04 | Evaluation Pipeline Architecture | 🟡 SHOULD | bonus |
| **4.2** | **Observability & Trace Analytics** | | |
| 4.2.01 | LangSmith | 🔴 MUST | ~90% obs |
| 4.2.02 | Phoenix & OpenTelemetry | 🟢 OPTIONAL | awareness |
| **4.3** | **Guardrails & Security Hardening** | | |
| 4.3.01 | Prompt Injection Defence | 🔴 MUST | high |
| 4.3.02 | Output DLP (Presidio) | 🔴 MUST | high |
| 4.3.03 | Jailbreak, Adversarial & RAG Security | 🟡 SHOULD | bonus |
| **4.4** | **Infrastructure Economics & Resiliency** | | |
| 4.4.01 | Semantic Caching | 🔴 MUST | high |
| 4.4.02 | Circuit Breakers & Model Fallbacks | 🔴 MUST | high |
| 4.4.03 | Prompt & Token Optimisation | 🟢 OPTIONAL | awareness |
| 4.4.04 | Fine-Tuning Overview | 🟢 OPTIONAL | awareness |
| 4.4.05 | 🏁 Milestone — Full Production AI System | 🔴 MUST | — |

**Legend:** 🔴 MUST · 🟡 SHOULD · 🟢 OPTIONAL (read, labelled — never skipped).

---

## 📦 Modules
- **4.1 Evaluation** ✅ — [RAGAS](Module%204.1%20-%20LLM%20Evaluation/01%20RAGAS.md) · [DeepEval](Module%204.1%20-%20LLM%20Evaluation/02%20DeepEval.md) · [LLM-as-a-Judge](Module%204.1%20-%20LLM%20Evaluation/03%20LLM-as-a-Judge.md) · [Eval Pipeline](Module%204.1%20-%20LLM%20Evaluation/04%20Evaluation%20Pipeline%20Architecture.md)
- **4.2 Observability** ✅ — [LangSmith](Module%204.2%20-%20Observability/01%20LangSmith.md) · [Phoenix & OTel](Module%204.2%20-%20Observability/02%20Phoenix%20and%20OpenTelemetry.md)
- **4.3 Guardrails & Security** ✅ — [Prompt Injection](Module%204.3%20-%20Guardrails%20and%20Security/01%20Prompt%20Injection%20Defence.md) · [DLP/Presidio](Module%204.3%20-%20Guardrails%20and%20Security/02%20Output%20DLP%20with%20Presidio.md) · [Jailbreak & RAG Sec](Module%204.3%20-%20Guardrails%20and%20Security/03%20Jailbreak%20Adversarial%20and%20RAG%20Security.md)
- **4.4 Economics & Resiliency** ✅ — [Semantic Caching](Module%204.4%20-%20Economics%20and%20Resiliency/01%20Semantic%20Caching.md) · [Circuit Breakers & Fallbacks](Module%204.4%20-%20Economics%20and%20Resiliency/02%20Circuit%20Breakers%20and%20Fallbacks.md) · [Token Opt](Module%204.4%20-%20Economics%20and%20Resiliency/03%20Prompt%20and%20Token%20Optimisation.md) · [Fine-Tuning](Module%204.4%20-%20Economics%20and%20Resiliency/04%20Fine-Tuning%20Overview.md) · [Milestone](Module%204.4%20-%20Economics%20and%20Resiliency/05%20Milestone%20-%20Full%20Production%20System.md)
> Terms → [AI Terms glossary](../AI%20Terms%20-%20Plain%20English%20Glossary.md).

## ✅ Status
**Complete** — 4 modules (15 lessons) built research-first to the reference bar; all 0 corrupted characters. Next: Phase 5 (Azure AI-102).
