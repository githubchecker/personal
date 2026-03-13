---
trigger: manual
description: "Pipeline Stage 1 (Part B) — Phases 4–6. Load at Phase 3 completion only — NOT on activation, NOT together with Part A."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# PIPELINE STAGE 1: DISCOVERY (Part B — Phases 4–6)

> **This file is Part B — load at Phase 3 completion, NOT on activation.**
> Part A (`workflow_01_discovery.md`) tells you when to load this file. Do not load it earlier.
> At Phase 4 also load `workflow_01_discovery_ref.md` (needed for format strings in Phase 4).
> At Phase 4B also load `workflow_01_discovery_cf_ref.md`.
> At Phase 6 re-read `workflow_01_discovery_ref.md` for spec template and anti-hallucination rules.

---

## Phase 4 — Self-Validation (Built-In, Mandatory)

Apply `0_analysis_rules.md` Rules A–F to your own draft spec. Each rule maps to a concrete output:

**Rule A (Inventory Declaration) — fires first, before any item is processed:**
Output the **Self-Validation Inventory** block (format: `workflow_01_discovery_ref.md` §"Self-Validation Inventory").
This declares the exact count of REQ, BUG, CF, DEC, OQ items. Without this count, silent skips are undetectable.

**Rule B (max 8 items/batch, hard PAUSE) — after every 8 items:**
Output the **Batch PAUSE** block (format: `workflow_01_discovery_ref.md` §"Batch PAUSE Block") and stop.
Do not continue until user replies "Continue" or "CONTINUE". The pause exists so findings are reviewed before being buried.

**Rule C (per-item verdict, no silent skips) — for every item:**
Output the **Per-Item Verdict** block (format: `workflow_01_discovery_ref.md` §"Per-Item Verdict").
PASS must be written explicitly — silence is not a verdict. Every REQ-ID, BUG-ID, and DEC-ID gets a verdict.

**Rule E (negative confirmation) — PASS is not silence:**
If an item has no issues, write `Status: PASS` with one sentence of evidence. Omitting a PASS verdict is a protocol failure equivalent to skipping the item.

**Rule F (Resumption Contract) — on token limit or session interrupt:**
Output the **Token Limit** block (format: `workflow_01_discovery_ref.md` §"Token Limit Block"). Do not rush remaining items — an incomplete rushed verdict is worse than a clean stop. The resume phrase is embedded in the Token Limit block.

**Rule D does not apply at Phase 4.** Rule D (Cross-Reference Ledger) fires only when two sources are compared. Phase 4 is single-source self-validation. Rule D fires at Phase 5.

**Critical self-check rules (all mandatory):**
- Every class/method/field reference: verified in codebase or flagged NEW+named
- Every constant: from codebase or user input — never invented
- Every "already handled" claim: cites specific file:function
- Every HIGH risk item: fixed before Phase 5 or escalated as OQ
- All MISSING items: confirm truly absent by searching class/method name
- Every MISSING item: confirm its DEC-ID exists in §3 with alternative rejected and Risk/Complexity tag
- §1.2 Architecture & Data Flow: confirm it is populated (not blank). If blank: write it now from Phase 1 mental model before proceeding.
- §5 QA & Verification Strategy: confirm it is populated or has [TBD] with an OQ flagged. A completely blank §5 is a spec defect.

After all batches complete, output the **Capability Summary** block then run the **PLANNER-Ready Gate**
(both formats: `workflow_01_discovery_ref.md` §"Phase Output Formats").

`NEEDS_EXPANSION` → fix spec NOW before Phase 4B. DISCOVERY is the last role with codebase access.
`PLANNER-READY` → proceed to Phase 4B.

---

## Phase 4B — Critical Findings (CF) Scan (Mandatory — runs after Phase 4)

**Read `workflow_01_discovery_cf_ref.md` now.** It contains the CF trap category checklist,
per-finding output format, and Dashboard format needed for Phase 4C.

**What this phase is:** Scan the entire spec for implementation traps — places where the *proposed
design* will fail at runtime in a non-obvious way. These are NOT bugs in existing code and NOT
feature gaps. They are design errors in proposed approaches that static analysis can catch now.
A clean CF Register is a positive result. Never skip this phase.

After scanning all categories (per `workflow_01_discovery_cf_ref.md`):
- If findings: output `CF REGISTER COMPLETE — [n] found: CRITICAL=[n] HIGH=[n] LOW=[n]`
- If none: output `CF REGISTER: CLEAR — no implementation traps found.`

**Gate:** Any CRITICAL CF must be fixed in the spec or escalated as OQ before proceeding to Phase 4C.
Do not proceed with an unresolved CRITICAL CF.

---

## Phase 4C — Project Decision Dashboard (Mandatory — runs after Phase 4B)

**Read `workflow_01_discovery_cf_ref.md`** for the Dashboard output format (already loaded from Phase 4B).

Output the full Dashboard block and copy it verbatim into §11 of the spec.
PLANNER reads §11 to set task order and identify blocked phases before it starts.

---

## Phase 5 — Multi-Model Cross-Check (User-Driven)

After Phase 4C, say:
> *"Spec is self-validated and CF-scanned. For independent cross-check, open a new AI model session
> and activate the VALIDATOR role:*
> *1. Upload `[Feature]_spec.md` (the spec just produced) — always required*
> *2. If this spec was ported from an existing document: also upload that document*
>    *If this spec extends a previous version: also upload the previous spec version*
>    *If this spec was built purely from Q&A: no second file needed — upload spec only*
> *3. Say: `Act as VALIDATOR`*
>    *VALIDATOR reads the spec header `Source:` field and detects the correct mode automatically.*
>
> *VALIDATOR outputs: (1) Inventory Declaration, (2) batched ITEM-NNN findings, (3) Agreement Matrix, (4) CORRECTION/MISSED/AGREE blocks, (5) Completeness Check. Paste its complete output back here and I will absorb it.*
>
> *To skip: say `skip cross-check — acknowledged risk.` Skipping will be recorded in the spec header.*"

**Do NOT provide a manual prompt.** VALIDATOR is a pipeline role — it knows its own job.
If the user does not have VALIDATOR configured: fall back to `workflow_01_discovery_crosscheck.md`.

**When second model findings arrive:**
1. State: *"Loading spec and cross-model findings. Building Cross-Reference Ledger before writing anything."*
2. **Rule A — Inventory Declaration first:** Count every item in VALIDATOR's output (CORRECTION-NNN, MISSED-NNN, AGREE items). Output: `CROSS-CHECK INVENTORY: CORRECTION=[n] MISSED=[n] AGREE=[n] | Total to process: [n] | Batches: [ceil(n/8)]`
3. Build Rule D Cross-Reference Ledger (`0_analysis_rules.md`) covering every item in both outputs — a ledger that does not cover all items from both models is a protocol failure.
4. Output the **Ledger Completeness Check** (format: `workflow_01_discovery_ref.md` §"Ledger Completeness Check"). If sum check fails: find missing items before proceeding. Do not continue with an incomplete ledger.
5. Process only CONFLICTS and GAPS — batch-process (max 8 per response, hard PAUSE after each batch per Rule B)
6. Absorb corrections into spec
7. Run PLANNER-Ready check on every new MISSING item added by cross-model findings. NEEDS_EXPANSION → expand before Phase 6 GO. Cross-model additions are not exempt.
8. For any new MISSING item added: create its DEC-ID (Phase 3 MISSING Capability Rule) and run CF scan for it

**Cross-Check Gate (mandatory before Phase 6):**
Output the **Discovery Gate** block (format: `workflow_01_discovery_ref.md` §"Phase Output Formats").
```
GO   = zero unresolved HIGH-risk items (resolved = fixed in spec OR converted to non-blocking OQ), zero blocked OQs, zero unresolved CRITICAL CFs
HOLD = blocked OQs or unresolved CRITICAL CFs — list them, wait for answers, re-run gate
REDO = >20% REQ-IDs had major corrections — restart Phase 2, do NOT pass to PLANNER
```
**If HOLD:** List OQs and unresolved CFs. Wait. Re-run gate. No spec write until GO.
**If REDO:** Summarise what changed, ask user to confirm restart.

---

## Phase 6 — Final Spec Output

After gate = GO, confirm path, then write:
> *"Ready to write `Docs/[Project]/[Feature]_spec.md` — confirm? (yes/no)"*

**⚠️ Before writing:** Load `modules/discovery_spec_template.md` for the spec structure. Re-read `workflow_01_discovery_ref.md` §"Anti-Hallucination Rules". Both govern spec writing.

After writing:
> *"Spec written. Gate: GO. REQ=[n] BUG=[n] CF=[n] (CRITICAL=[n]) OQ=[n]. Ready to activate PLANNER? (yes/no)"*

**⚠️ PLAN INVALIDATION RULE:**
If the spec is revised after Phase 6 (user adds a requirement, cross-model check yields corrections,
or an OQ answer changes an architecture decision):
1. Emit: `PLAN INVALIDATED — spec changed after PLANNER ran`
2. State exactly which REQ-IDs / DEC-IDs / CF-IDs changed
3. PLANNER must re-run from scratch — partial patching of `02_IMPLEMENTATION_PLAN.md` is forbidden
4. Completed tasks from a previous IMPLEMENTER run on the old plan are **permanently marked COMPLETED**
   — they do not re-run unless explicitly listed in the new plan

---

## Anti-Hallucination Rules (Always Active)

See `workflow_01_discovery_ref.md` for the full rules. Summary:
- Never invent names — cite the file. Never assume EXISTS without reading. No magic numbers.
- PORTING MODE: every artefact from source reproduced verbatim in spec body.
- Every MISSING item must have a DEC-ID. A MISSING item with no DEC-ID is a spec failure.

---

## Stage Failure Handling

| Situation | Action |
|-----------|--------|
| Q&A stalls | Mark as OQ, note "needs domain research", continue |
| Spec self-contradicts | Fix in Phase 4 self-validation — never pass to Phase 4B |
| MISSING item has no DEC-ID | Create DEC-ID before Phase 4B — never leave a MISSING item without a design decision |
| CRITICAL CF found in Phase 4B | Fix spec now OR escalate as OQ — do not proceed to Phase 4C with unresolved CRITICAL CF |
| Cross-model > 20% wrong | Gate = REDO → restart Phase 2 with revised scope |
| User can't answer HOLD OQs | Spec gate stays HOLD. Do not activate PLANNER. |
| Scope too large | After 5 Q&A rounds with OQs > REQs/2: recommend split |
| PLANNER-Ready fails post-Phase 5 | Expand spec in-place before Phase 6 GO |
| REDO after PLANNER already ran | Emit PLAN INVALIDATED. PLANNER must full re-run. |
| Porting — detail lost | Restore all field names, constants, code patterns from source verbatim |
| New-file design bug found | Add to BUG register with Source: NEW_FILE_DESIGN. CF scan catches design traps. |
