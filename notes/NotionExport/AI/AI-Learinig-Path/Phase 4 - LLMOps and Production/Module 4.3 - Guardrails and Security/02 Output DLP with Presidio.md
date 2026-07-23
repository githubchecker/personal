# 02 — Output DLP with Presidio

> Phase 4 · Module 4.3 · Lesson 2 · `[JD VERIFIED — stop the model leaking PII/PHI]`

> 🔬 Presidio `2.2.x` (AnalyzerEngine + AnonymizerEngine).

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** A model might emit a name, SSN, email, or card number — a compliance breach
(GDPR/HIPAA). **DLP (Data Loss Prevention)** scans outputs (and inputs) and **anonymises** detected PII/
PHI before they leave. Presidio is the open standard.

**Why care:** mandatory for regulated AI; named in JDs.

## 🔑 New Terms
**PII/PHI** · **Presidio Analyzer** (detect via NER+regex) · **Anonymizer** (replace with placeholders) ·
**custom NER** · **audit trail**. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a redaction clerk blacks out names/SSNs before a doc leaves the building. Presidio = the automatic clerk. **Aha!:** detect → anonymise → log, on the way out.

## ⚙️ Stage 2 — detect + anonymise (full)
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
analyzer = AnalyzerEngine()                                   # NER + regex + checksums
results = analyzer.analyze(text=out, language="en",          # find PERSON/EMAIL_ADDRESS/US_SSN/CREDIT_CARD
                           entities=["PERSON","US_SSN","CREDIT_CARD","EMAIL_ADDRESS"])
clean = AnonymizerEngine().anonymize(text=out, analyzer_results=results).text  # -> "<PERSON> ... <US_SSN>"
log_redactions(results)                                       # audit: type+offset (never the raw value)
```
#### Analyzer — detect PII/PHI
- **What & why:** the `AnalyzerEngine` finds entities via **NER + regex + checksums** (e.g. card-number Luhn
  check), returning typed spans with confidence. **✅ Use when:** scanning any text leaving (or entering) the
  system. **🚫 Avoid → regex-only:** it misses names/context. **⚠️ Gotcha:** recall isn't 100% — tune confidence and **layer** defences.

#### Anonymizer — replace what was found
- **What & why:** the `AnonymizerEngine` applies an operator per span — **replace** (`<PERSON>`), redact, **hash**,
  or encrypt. **✅ Use when:** sanitising before return/storage. **🚫 Avoid → keeping raw:** when compliance forbids
  it. **⚠️:** use **hash** (not plain redaction) if you later need to re-link records.

#### Custom recognizer — your own identifiers
- **What & why:** add patterns for proprietary IDs (employee#, policy#, medical-record#). **✅ Use when:** domain-
  specific data the built-ins don't know. **🚫 Avoid → custom:** for standard PII (built-ins already cover it). **⚠️:** you maintain the patterns.

**PHI for HIPAA:** add health recognizers; **audit** every detected entity by **type + span, never the raw value**;
scan **both input and output**.

> 🔬 **Under the hood:** Analyzer = recognizers → spans + score; Anonymizer = operators per span. It's
> **probabilistic** (NER), so treat it as one layer of defence, not the sole control.

## 🚀 Stage 3 — In Practice / Why It Matters
DLP is the difference between a chatbot and a *compliant* chatbot. A healthcare or finance assistant runs every
response through Presidio on the way out: detect PERSON/SSN/CARD/PHI, anonymise, and log the **type and offset**
(never the value) for the audit trail. It pairs with input guardrails (4.3.01) and content safety — DLP stops
the model **leaking** sensitive data; guardrails stop it being **manipulated**.

## ⚖️ Variations & When to Use
| The need is… | Use | Why |
|---|---|---|
| Find standard PII (name/SSN/card/email) | **built-in recognizers** | NER + regex + checksums out of the box |
| Find proprietary IDs | **custom recognizer** | your own patterns |
| Hide but keep re-linkable | **hash** operator | reversible mapping for joins |
| Hide irreversibly | **replace/redact** | placeholders, no recovery |
| Regulated (HIPAA/GDPR) | **+ PHI recognizers + audit** | compliance evidence |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| A name slips through | NER recall < 100% | add regex/custom recognizers; layer defence |
| Audit fails | nothing logged | log entity **type + span** (never the raw value) |
| Audit log itself leaks PII | logged raw values | store type/offset only |
| Can't reconcile records | values fully redacted | use the **hash** operator instead |

## 📌 Quick Reference
- **Flow:** `AnalyzerEngine.analyze()` → `AnonymizerEngine.anonymize()` → audit (type+span).
- **Scan input *and* output.** Built-ins for standard PII; **custom recognizers** for proprietary IDs; **PHI** for HIPAA.
- Hash if you must re-link; **never log raw PII**; it's probabilistic — layer it, don't rely on it alone.

## 🛑 STOP — Self-Check
A healthcare assistant might echo a patient's name or record number in its answer. What's the control, and what
must the audit log **not** contain?

<details><summary>Answer</summary>

**Presidio output DLP** — run each response through the **Analyzer** (detect PERSON + PHI, including a **custom
recognizer** for the medical record number), then the **Anonymizer** to replace/redact before returning. The
**audit log must not contain the raw PII values** — log only the entity **type and offset/span**, or the log
itself becomes a HIPAA breach. Layer it with input guardrails and prompt rules.
</details>

⏭️ **Next:** 03 — Jailbreak, adversarial & RAG security.
