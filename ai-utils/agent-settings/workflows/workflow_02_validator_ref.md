---
trigger: manual
description: "VALIDATOR Reference — Phases 1–3, check definitions, output sequence, anti-hallucination rules, resumption. Load alongside workflow_02_validator.md in every VALIDATOR session. Split from workflow_02_validator.md to stay under 12 000 chars."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# VALIDATOR — Analysis Phases & Output Reference

> **This file is Part B of VALIDATOR.** Load it alongside `workflow_02_validator.md` in every VALIDATOR session.
> It contains all analysis phases (1–3), check definitions, output sequence, anti-hallucination rules, and resumption protocol.

## Phase 1 — Load and Map

### MODE A and MODE B

State: `"Loading [source / v1] and [spec / v2]. Will not begin writing until both are fully mapped."`

Read both completely. Build Cross-Reference Ledger (Rule D2):
```
CROSS-REFERENCE LEDGER — [spec] vs [source]  [Rule D2]
| Item ID | Item | In Source | In Spec | Match | Conflict | Only-Source | Only-Spec |
|---------|------|:---------:|:-------:|:-----:|:--------:|:-----------:|:---------:|
| ITEM-001 | [section heading or REQ-ID] | ✓ | ✓ | ✓ | | | |
| ITEM-002 | [Journey A] | ✓ | | | | ✓ | |
```

Ledger covers: every named section heading in source · every Journey (A/B/C...) · every named gap (GAP-x.x) · every decision option table · every REQ-ID, BUG-ID, DEC-ID, CF-ID, §13 subsection in spec.

### MODE C and MODE D

State: `"Loading [spec filename]. Running internal consistency checks — no source document."`

Build spec item inventory (Rule D not applicable):
```
SPEC INVENTORY — [Feature]_spec.md
REQ-IDs      : [n]  (EXISTS=[n] MISSING=[n] PARTIAL=[n])
BUG-IDs      : [n]  (EXISTING=[n] NEW_FILE_DESIGN=[n])
DEC-IDs      : [n]
CF-IDs       : [n]  (CRITICAL=[n] HIGH=[n])
OQ-IDs       : [n]
§13 sections : [n]
Total items  : [n]
```

---

## Phase 2 — Inventory Declaration (Rule A)

### MODE A / B:
```
INVENTORY DECLARATION
---------------------
Source : [filename or "v[N] spec"]
Spec   : [filename or "v[N+1] spec"]
Source sections mapped : [n]
Spec entries mapped    : [n]
Agreements (Match)     : [n] — no further text needed
Gaps (in source, not in spec) : [n]
Conflicts (spec disagrees with source) : [n]
Total to process : [gaps + conflicts]
Batch size: 8 | Total batches: [ceil/8]
```

### MODE C / D:
```
INVENTORY DECLARATION — INTERNAL CHECKS ONLY
---------------------------------------------
Spec   : [filename]
Mode   : [Q&A+CODEBASE / SPEC-ONLY]
Items to check : [n]
Check 10 : SKIPPED — no source document
Batch size: 8 | Total batches: [ceil/8]
```

---

## Phase 3 — Findings (Rules B, C)

Per-item format (Rule C) — same for all modes:
```
### ITEM-[NNN]: [short description]
**Source section:** [exact heading / REQ-ID / Journey / gap — or "internal" for MODE C/D]
**Spec location:** [REQ-ID / DEC-ID / §13.N / "absent"]
**Status:** GAP | CONFLICT | PARTIAL | NEEDS_HUMAN
**Type:** BUG | CF | REQ | LOSSLESS | RISK | DEPENDENCY | CORRECTION
**Finding:** [1–3 sentences — what is wrong or missing]
**PLANNER impact:** [what PLANNER will get wrong or miss if unfixed]
**Action Required:** [specific fix — never blank for GAP or CONFLICT]
```

### Check applicability by mode:

| Check | A: Porting | B: Versioned | C: Q&A+Codebase | D: Spec-Only |
|-------|:---:|:---:|:---:|:---:|
| 1 — Wrong capability status | ✓ | ✓ | ✓ | ✓ |
| 2 — Flawed architecture decisions | ✓ | ✓ | ✓ | ✓ |
| 3 — Missed requirements | ✓ source→spec | ✓ vN→vN+1 | ✓ internal | ✓ internal |
| 4 — Incorrect references | ✓ flag UNVERIFIED | ✓ flag UNVERIFIED | ✓ internal only | ✓ internal only |
| 5 — Underspecified items | ✓ | ✓ | ✓ | ✓ |
| 6 — Contradictions | ✓ | ✓ | ✓ | ✓ |
| 7 — Missing Critical Findings | ✓ | ✓ | ✓ | ✓ |
| 8 — Bug Register gaps | ✓ source bugs | ✓ source bugs | ✓ NEW_FILE_DESIGN | NEW_FILE_DESIGN only |
| 9 — Architecture gaps | ✓ | ✓ | ✓ internal | ✓ internal |
| 10 — Losslessness | ✓ | ✓ | **SKIPPED** | **SKIPPED** |

---

**Check 1 — Wrong capability status**
EXISTS items source says do not exist. MISSING items source says already exist. PARTIAL descriptions that mischaracterise what is partial.
*MODE C/D:* capability matrix status must be consistent with the BUG register for the same item.

**Check 2 — Flawed architecture decisions**
DEC-IDs with a clearly better untested alternative. Risk/Complexity tags wrong for the described change. "Alternative rejected" reasoning that is incomplete, circular, or missing.

**Check 3 — Missed requirements**
*MODE A/B:* capabilities in source with no REQ-ID, BUG-ID, DEC-ID, or §13 block in spec.
*MODE C/D:* every MISSING REQ-ID must have a DEC-ID. Every BUG-ID must have a Fix Phase. Every OQ must have a resolution path or be marked blocking.

**Check 4 — Incorrect references**
*MODE A/B:* file paths, class names, method names in spec not found in source → flag UNVERIFIED.
*MODE C/D:* Flag two types: (1) same identifier spelled differently across spec sections (e.g., `ValidateToken` vs `ValidateTokenAsync`); (2) any `file:method` evidence cell where the same method name appears under different class names in different REQ-IDs. Do NOT flag codebase references as unverified — they were verified during DISCOVERY. Do flag internal naming inconsistency as CORRECTION type with note: "DISCOVERY should confirm canonical name."

**Check 5 — Underspecified items**
MISSING REQ-IDs or DEC-IDs where an implementer would make an unguided design decision. Look for: missing field names, missing constant values, missing algorithm steps, missing interface signatures, missing error handling.

**Check 6 — Contradictions**
Requirements conflicting with each other or with DEC-IDs. Capability matrix status contradicting the BUG register for the same item. Phase dependencies in §6 contradicting each other.

**Check 7 — Missing Critical Findings**
CF Register omissions: unbounded collections · undefined computation · dual-implementation risk · uninitialized state on first tick · large-scope renames with callers uncounted · sign/direction ambiguity · thread-safety assumptions · integer overflow in financials · non-atomic operations assumed atomic.

**Check 8 — Bug Register gaps**
*MODE A/B:* bugs in source ("What Is Broken", GAP notes) absent from BUG register.
*All modes:* every MISSING REQ-ID proposing a new file must have at least one `NEW_FILE_DESIGN` BUG-ID or CF-ID covering its design risks.

**Check 9 — Architecture gaps**
*MODE A/B:* modules or data flows in source absent from §1.2. Missing phase dependencies in §6.
*MODE C/D:* every module named in REQ-IDs/DEC-IDs must appear in §1.2. Every CF-ID must be bound to a phase in §6. §1.2 data flow must be internally self-consistent.

**Check 10 — Losslessness (MODE A and MODE B only — SKIP for MODE C and D)**
For every named section heading in source, at least ONE must be true in spec:
maps to REQ-IDs · OR BUG-IDs · OR DEC-IDs · OR reproduced as §13 subsection.
Every source section with NONE → Status: GAP · Type: LOSSLESS.

Sub-checks:
- Every named Journey (A/B/C...) has its own §13 subsection — DEC-ID reference alone insufficient
- Every decision option table: full options AND WHY rationale for each rejected alternative
- Every named gap (GAP-x.x) in source appears in BUG register
- Every EXISTS REQ-ID has a `Context:` annotation naming key class/method
- Every EXISTS REQ-ID with a journey in source has a `DEC-ID: CONTEXT-ONLY` entry in §3
- *MODE B only:* Every §13 subsection in vN must exist in vN+1 or be marked `[Superseded by: reason]`

---

## Output Sequence

Output in this exact order. DISCOVERY Phase 5 absorption reads this format directly.

**1.** Cross-Reference Ledger (MODE A and MODE B only — omit for MODE C/D)
**2.** Inventory Declaration
**3.** Batched findings — max 8 per batch, hard PAUSE after each (Rule B):
```
<<<VALIDATOR BATCH [n] COMPLETE>>>
Items processed : ITEM-[x] through ITEM-[y]
Items remaining : [z]
Reply CONTINUE to process Batch [n+1]
```
**4.** Agreement Matrix (after all batches):

> **Linkage rule:** For any section marked PARTIAL or DISAGREE, list the specific ITEM-NNN identifiers from the batch findings that caused that verdict — e.g., `PARTIAL (ITEM-003, ITEM-007)`. A section-level verdict without ITEM-NNN references is not verifiable by DISCOVERY during absorption.
```
VALIDATOR AGREEMENT MATRIX
| Section | Verdict | Notes |
|---------|---------|-------|
| §1 Architecture & Context | AGREE/PARTIAL/DISAGREE | |
| §2 Capability Matrix | AGREE/PARTIAL/DISAGREE | |
| §2 Bug Register | AGREE/PARTIAL/DISAGREE | |
| §3 Architecture Decisions | AGREE/PARTIAL/DISAGREE | |
| §4 Frozen Values | AGREE/PARTIAL/DISAGREE | |
| §5 QA Strategy | AGREE/PARTIAL/DISAGREE | |
| §6 Phase Plan & CF Bindings | AGREE/PARTIAL/DISAGREE | |
| §7 Critical Findings Register | AGREE/PARTIAL/DISAGREE | |
| §10 Risk Register | AGREE/PARTIAL/DISAGREE | |
| §13 Implementation Reference | AGREE/PARTIAL/DISAGREE | |
| Check 10 Losslessness | AGREE/PARTIAL/DISAGREE / N/A (MODE C/D) | |
```
**5.** DISCOVERY absorption format:
```
CORRECTION-001: [what spec says] / [what is correct] / [source section or "internal"]
MISSED-001: [Type] / [description] / [source section or "internal"] / [PLANNER impact]
AGREE: [specific REQ-IDs, DEC-IDs, BUG-IDs verified correct — be specific]
```
**6.** Completeness Check (Rule D4):
```
COMPLETENESS CHECK
------------------
Mode       : [PORTING / VERSIONED / Q&A+CODEBASE / SPEC-ONLY]
Total items: [n]
Agreements : [n]
Conflicts  : [n]
Gaps       : [n]
NEEDS_HUMAN: [n]
Check 10   : [n items checked / SKIPPED]
Sum        : [must equal total]
```
**7.** Close:
```
VALIDATOR COMPLETE — CORRECTION=[n] | MISSED=[n] | AGREE=[n]
Mode: [PORTING / VERSIONED / Q&A+CODEBASE / SPEC-ONLY]
[If MODE C or D]: Check 10 was skipped — no source document available.
  To enable next time: save Q&A transcript as .md + upload alongside spec (→ MODE A)
  OR continue Q&A from this spec, produce v2, upload v1+v2 (→ MODE B)
Paste this full output to your DISCOVERY session.
Say "absorb cross-model findings" to trigger DISCOVERY Phase 5 absorption.
```

---

## Anti-Hallucination Rules (Always Active)

1. **Never assert a file, class, or method does not exist.** No codebase access in VALIDATOR. Flag as UNVERIFIED if not verifiable from uploaded documents.
2. **Never flag a finding from domain knowledge not in the uploaded documents.** External best-practice disagreements are not VALIDATOR findings.
3. **Never mark something absent without checking all uploaded documents.** State exactly where you looked before flagging as missing.
4. **If uncertain — surface it, never suppress it.** Add: "DISCOVERY should independently verify." Suppression is a protocol failure.
5. **In MODE C or D — never invent a source document to compare against.** Training knowledge is not a source. Internal checks only.

---

## Resumption (Rule F)

If interrupted mid-batch:
```
RESUMPTION CONTRACT — VALIDATOR
--------------------------------
Mode: [PORTING / VERSIONED / Q&A+CODEBASE / SPEC-ONLY]
Previous session: Batch [n], ITEM-[x] through ITEM-[y] complete
Resuming: Batch [n+1] from ITEM-[y+1]
Does this match your records? (yes / no)
```
Do not process any items until confirmed.
