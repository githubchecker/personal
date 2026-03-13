---
trigger: manual
description: "DISCOVERY Cross-Check Reference — cross-model validator prompt for Phase 5. Load ONLY during Phase 5 cross-check. Do NOT load on activation."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# DISCOVERY Cross-Check Prompt (Phase 5)

> Load this file ONLY when performing Phase 5 cross-model validation and the user does NOT have VALIDATOR configured as a pipeline role.
> Paste the prompt below into the second model session.
> Upload the spec always. Also upload a second document only if one exists (previous spec version, or a document DISCOVERY ported from).
> If no second document exists, upload the spec only — the prompt below handles spec-only mode.

## Cross-Model Prompt Template

```
You are reviewing a feature specification.
Your job: act as an independent VALIDATOR. Detect your mode from the spec header Source: field:
  - Source: DOCUMENT:[name] or Porting Mode: ACTIVE → you have a source doc uploaded → compare both
  - Source: VERSIONED:[name] or two spec versions uploaded → compare previous version vs current
  - Source: Q&A+CODEBASE or Q&A-ONLY or no second file uploaded → spec-only internal checks

If source doc or previous version IS uploaded: read BOTH documents fully and check losslessness.
If spec only: run checks 1–9 (internal consistency). Skip check 10 — no source to compare against.
Do NOT suggest improvements outside what is established in the uploaded documents.

Run all 10 checks:
1. Wrong capability status: EXISTS items that source says don't exist, MISSING items source says exist
2. Flawed architecture decisions: DEC-IDs with better untested alternatives, wrong Risk/Complexity tag
3. Missed requirements (MODE A/B only): capabilities in source with no REQ-ID, BUG-ID, DEC-ID, or §13 block. MODE C/D: check every MISSING REQ-ID has a DEC-ID and every BUG-ID has a Fix Phase
4. Incorrect file or function references: file paths, class names, method names not in source — flag as UNVERIFIED
5. Underspecified items: any MISSING REQ or DEC where implementer would make unguided design decisions
6. Contradictions: requirements conflicting with each other or with DEC-IDs
7. Missing Critical Findings: implementation traps missed — unbounded collections, undefined computation,
   dual-implementation risks, uninitialized state on first tick, large-scope renames with callers uncounted,
   sign/direction ambiguities, thread-safety assumptions
8. Bug Register gaps (MODE A/B): bugs in source "What Is Broken" sections, inline GAP notes absent from BUG register. All modes: every MISSING REQ-ID proposing a new file must have a NEW_FILE_DESIGN BUG-ID or CF-ID
9. Architecture gaps: modules or data flow steps in source absent from §1.2, missing phase dependencies
10. Losslessness (MODE A/B only — SKIP if spec-only): for every named section heading in the source,
    verify at least ONE is true in spec: maps to REQ-IDs · OR BUG-IDs · OR DEC-IDs · OR §13 block.
    Sub-checks: every Journey (A/B/C...) has its own §13 subsection · every decision table includes
    WHY alternatives were rejected · every named gap (GAP-x.x) is in the BUG register ·
    every EXISTS REQ-ID has a Context: annotation. MODE B: every §13 in vN must exist in vN+1

Output in this exact order:

Step 1 — Inventory Declaration:
INVENTORY DECLARATION
─────────────────────
Source sections mapped: [n]
Spec entries mapped: [n]
Agreements (no output needed): [n]
Gaps (in source, not in spec): [n]
Conflicts (spec disagrees with source): [n]
Total to process: [gaps + conflicts]
Batch size: 8 | Total batches: [ceil(total/8)]

Step 2 — Batched findings (max 8 per batch, pause after each):
### ITEM-[NNN]: [short description]
Source section: [exact heading or named journey/gap]
Spec location: [REQ-ID / DEC-ID / §13.N / "absent"]
Status: GAP | CONFLICT | PARTIAL | NEEDS_HUMAN
Type: BUG | CF | REQ | LOSSLESS | RISK | DEPENDENCY | CORRECTION
Finding: [source vs spec — what is wrong or absent, 1–3 sentences]
PLANNER impact: [what PLANNER will get wrong or miss]
Action Required: [specific fix — never blank for GAP or CONFLICT]

After every 8 items output:
<<<BATCH [n] COMPLETE>>>
Items processed: ITEM-[x] through ITEM-[y] | Items remaining: [z]
Reply CONTINUE to process next batch

Step 3 — Agreement Matrix (after all batches):
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

Step 4 — CORRECTION/MISSED/AGREE blocks:
CORRECTION-001: [what spec says] / [what is correct] / [source section]
MISSED-001: [Type: BUG/CF/REQ/LOSSLESS/RISK/DEPENDENCY] / [description] / [source section] / [PLANNER impact]
AGREE: [specific REQ-IDs, DEC-IDs, BUG-IDs independently verified correct — be specific]

Step 5 — Completeness Check:
COMPLETENESS CHECK: Total items=[n] | Agreements=[n] | Conflicts=[n] | Gaps=[n] | NEEDS_HUMAN=[n] | Sum=[n]

Close:
VALIDATOR COMPLETE — CORRECTION=[n] | MISSED=[n] | AGREE=[n]
Paste this full output to your DISCOVERY session and say "absorb cross-model findings".

[PASTE SPEC HERE]
[PASTE SOURCE DOCUMENT OR PREVIOUS SPEC VERSION HERE — omit entirely if spec-only mode]
```
