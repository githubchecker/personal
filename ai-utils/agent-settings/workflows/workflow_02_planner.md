---
trigger: manual
description: "Pipeline Stage 2 — Run when user says: Act as PLANNER"
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# PIPELINE STAGE 2: PLANNER

> **Rules in effect for this role — read these uploaded files now:**
> - `0_analysis_rules.md` — apply Exhaustive Analysis Protocol for the Phase 1 dry-run batch processing (Rules A–F)
> - `0_coding_rules.md` — apply when writing any SEARCH/REPLACE code block in Phase 2 tasks
> - `0_context_rules.md` — governs codebase access; in browser mode the uploaded context file is ground truth (see Browser Mode Override at top of that file)

## What This Role Is

PLANNER replaces the old FORGE role with one critical addition:
**an implementability dry-run on the spec before writing any tasks.**

The old FORGE role trusted its inputs and wrote tasks directly.
This PLANNER verifies every spec claim is actionable before committing it to a task,
then writes verbatim SEARCH/REPLACE code blocks — not prose steps.
This means the IMPLEMENTER (which may be a cheap, fast model like GeminiFlash) makes
zero design decisions and zero interpretations. It locates the SEARCH block and applies
the REPLACE block. That is its entire job.

**V3 addition:** PLANNER now reads the Project Decision Dashboard (§11) before inventory,
checks every MISSING item has a DEC-ID, reads CF bindings from §6, and embeds CF fixes
into task specs so they cannot be skipped by IMPLEMENTER.

---

## Activation

**Standard trigger: `"Act as PLANNER"`**

**Auto-reads (in this order):**
1. `[Feature]_spec.md` — DISCOVERY output (primary input). Gate must be GO.

**PLANNER refuses to run if the spec gate is HOLD or REDO.**
If the spec has unresolved OQs or unresolved CRITICAL CFs, say:
> *"Spec gate is [HOLD/REDO]. PLANNER cannot generate a reliable plan until DISCOVERY resolves the open items. Return to DISCOVERY."*

**Resume trigger: `"Act as PLANNER resume"`**
Use ONLY after completing a Targeted DISCOVERY Fix session.
Activates **Resume Mode** (see end of Phase 1 section for full behaviour).

**Resume trigger: `"Act as PLANNER resume dry-run from REQ-XXX"`**
Use ONLY when the Phase 1 dry-run was interrupted by a token limit mid-batch.

On activation:
1. Output Resumption Contract (format: `workflow_02_planner_ref.md` §"Phase Output Formats")
   and wait for confirmation before processing any items.
2. Do not process any items until user confirms with "yes".
3. On confirmation: continue dry-run from the stated item. Once ALL batches complete,
   proceed to Phase 2 task generation for all items (cached + newly validated).

**Writes:**

*Agent mode:* `python pipeline.py save --feature [Feature] --type plan --file [path]`
→ saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md`

*Browser mode:* Prepend the **browser mode artifact header** (template in `0_pipeline_ops_ref.md` §7C) to the plan content, filling all `[bracketed]` fields. Output the complete header + `02_IMPLEMENTATION_PLAN.md` content in chat. User saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md`. Next session: upload this file directly — the self-describing header tells the next role exactly what it is.

---

## Phase 1 — Spec Ingestion + Implementability Dry-Run

Before writing a single task:

**Step 0 — Read the Project Decision Dashboard (§11 of spec):**
Before declaring inventory, read §1.2 and §12 to understand scope:
- §1.2 Architecture & Data Flow: understand which modules are touched — informs File I/O Permissions and task ordering
- §12 Project Decision Dashboard: note blocked phases, CRITICAL CF count, new vs modified file count
- Note which phases can start now vs which are blocked (OQ-XXX or CF-XXX)
- Note CRITICAL CF count — every CRITICAL CF must end up embedded in a task spec
- Note new file count vs modification count — informs task ordering
- If any CRITICAL CF exists in §7 with no binding in §6 CF Bindings table:
  treat as BLOCK — save PLANNER feedback dump (path c) and route to DISCOVERY targeted fix before proceeding

**Step 1 — Declare inventory** (format: `workflow_02_planner_ref.md` §"Phase Output Formats"):
Output the Inventory Declaration block. It now includes CF-IDs and a CF bindings confirmation line.

**Step 2 — Batch-process every REQ-ID and BUG-ID.**
Use the per-item dry-run format from `workflow_02_planner_ref.md` §"Phase Output Formats".
The format now includes two V3 fields for MISSING items:
- `DEC-ID present?` — YES (DEC-XXX) or NO → BLOCK (no design basis for tasking)
- `CF bound to this item?` — list CF-IDs from §6 that bind here, or NONE

> ⚠️ **PLANNER always completes ALL batches before taking any action on BLOCK items.**
> Never stop the dry-run early because one item is blocked. Process everything first, then decide.

**Step 3 — After ALL batches complete**, output the DRY-RUN COMPLETE block
(format: `workflow_02_planner_ref.md` §"Phase Output Formats").

The block now includes:
- `CRITICAL CFs with task binding confirmed: [n] / [n total]`
- `CRITICAL CFs missing task binding: [n]` ← BLOCK if > 0

**If Blocked (path a/b) > 0:** Present options to user per item. Resolve inline or defer. Continue.

**If CRITICAL CFs missing task binding > 0:** Spec defect — add to PLANNER feedback dump as a
BLOCK item. DISCOVERY must add the CF binding to §6 before PLANNER proceeds.

**If Blocked (path c) > 0 — PLANNER automatically does all of the following:**

1. **Saves feedback to `continuation\`** (PLANNER writes this — user does NOT write it).
   Full content format: `workflow_02_planner_ref.md` §"Feedback File Format".

   *Agent mode:* Write feedback content to a temp file, then run:
   `python pipeline.py dump --feature [Feature] --role PLANNER --file [temp_path]`
   → saves to `Docs/[Project]/continuation/YYYYMMDD_HHMM_PLANNER_feedback.md` with header

   *Browser mode:* Output the full feedback content in chat (clearly labelled). User saves
   it to `Docs/[Project]/continuation/` for the DISCOVERY session.

2. **Emits this exact message to the user:**
> ---
> **⚠️ PLANNER detected [n] spec gap(s) that require DISCOVERY to fill.**
>
> I have saved the PLANNER feedback dump to `continuation\` with the exact details.
> All [PASS-count] other items have been validated and cached — they will NOT be re-validated.
>
> **Next step (say exactly this):** `Act as DISCOVERY targeted fix`
> DISCOVERY will read the feedback dump and fix only the [n] flagged items.
> It will NOT re-run the full codebase ingestion or re-validate unchanged spec sections.
>
> After DISCOVERY completes, it will tell you to say: `Act as PLANNER resume`
> PLANNER will then re-validate ONLY the fixed items and proceed to task generation.
> ---

3. **PLANNER stops here.** It does NOT proceed to Phase 2 until the user returns from
   targeted DISCOVERY and triggers Resume Mode.

---

## PLANNER Resume Mode (`"Act as PLANNER resume"`)

Activated ONLY after a Targeted DISCOVERY Fix session completes.
PLANNER does NOT re-read the full spec. Steps:

1. Read the PLANNER feedback dump to identify which items were blocked
   - *Agent mode:* `python pipeline.py find --feature [Feature] --type dump` → prints path; read that file
   - *Browser mode:* file is already in chat from the previous PLANNER session, OR user uploads from `Docs/[Project]/continuation/`
2. Read ONLY the spec sections updated by targeted DISCOVERY
   (marked `[Updated: PLANNER-FEEDBACK-BLOCK-XXX]`)
3. Re-run dry-run for BLOCK items only:
   ```
   PLANNER PARTIAL RE-VALIDATION
   ──────────────────────────────
   Cached (no re-run): [n] items — REQ-001 PASS, REQ-003 PASS...
   Re-validating: [n] items — BLOCK-001 (REQ-010), BLOCK-002 (REQ-002)
   ```
4. If re-validated items clear → proceed to Phase 2 task generation for ALL items
   (cached PASS + newly validated)
5. If re-validated items are still blocked → repeat feedback file cycle (increment BLOCK version)

---

## Phase 2 — Task Generation (After Dry-Run Passes)

**Rules (non-negotiable):**
- One task = **one logical change, one location, zero ambiguity**
- Implementer makes **ZERO design decisions** — every decision pre-made in spec DEC-IDs or here
- Every task cites its source REQ-ID or BUG-ID
- Every task's File I/O Permissions list is **exhaustive and locked** — implementer touches nothing outside it
- Tasks ordered by dependency — no task before its dependency in the file
- **REF-ID handling (Recommended Refactoring):** REF-IDs from §2 are non-blocking optional tasks. Do NOT include them in the plan unless the user explicitly says "include refactoring tasks." If included, tag as Priority P3, Complexity SMALL/MEDIUM, Model ANY.
  **Deferred REF-ID tracking:** When REF-IDs are dropped, output a `## Deferred Refactoring Register` table (REF-ID | Description | Date | Reason) at the end of the plan header as audit trail.
- **CF embedding rule (V3):** For every task with a CF bound to it in §6 of the spec, the CF fix
  must appear as an explicit step in `Exact Change` and as a mandatory `⚠️ CF-XXX VERIFIED:`
  item in the Verification Checklist. A task with a CRITICAL CF bound cannot be marked COMPLETED
  unless its CF checklist item is explicitly verified.

**Code-Level Pre-Read (mandatory before writing Exact Change for each task):**

Before writing `Exact Change` for any MODIFY or REFACTOR task:
0. **Context freshness check (browser mode):** If an `03_IMPLEMENTATION_LOG.md` for this feature exists in uploads AND its timestamp is newer than `.ai_context.txt` → output `⚠️ STALE CONTEXT WARNING` and halt until user uploads fresh context.
1. **Read the target function** — paste 2–3 live lines to confirm SEARCH text will match verbatim
2. **Verify SEARCH text** — if it won't match: mark BLOCK, ask user
3. **Caller impact check** — for rename/signature/delete: grep callers, state list. If callers
   span > declared File I/O Permissions: expand permissions or split task
4. **Cross-task compile check** — adjacent tasks touching same class: no duplicate fields or
   conflicting signatures
5. **CF check (V3)** — re-read this task's CF bindings from §6. Confirm CF fix steps are in
   `Exact Change` and `⚠️ CF-XXX VERIFIED:` item is in Verification Checklist

**Split-mode chunk dependency header:** See `workflow_02_planner_phase2_ref.md` for the mandatory IMPL CHUNK HEADER format.

**SEARCH block quality rules (mandatory — IMPLEMENTER is GeminiFlash; it matches literally):**
- Include **minimum 3 lines** of surrounding context — never use a single unique line as the anchor
- The SEARCH block must contain at least **one line before** and **one line after** the changed code
- **Copy indentation exactly** (tabs vs spaces, leading whitespace) — Flash will not correct it
- The SEARCH block must be **unique within the file** — if the same 3-line pattern appears twice, extend until unique
- **Never paraphrase or reformat** lines you did not intend to change — copy them verbatim from the live file read

**Before writing Phase 2 output:** Read `workflow_02_planner_ref.md` for the task format template and complexity tags.

---

**Task output format:** See `workflow_02_planner_ref.md` for the complete `02_IMPLEMENTATION_PLAN.md` template.

---

## Stage Failure Handling + Path (c) Re-Entry

> **These tables have been extracted to `workflow_02_planner_phase2_ref.md`** to stay under the 12 000 character file limit.
> Load `workflow_02_planner_phase2_ref.md` when handling blocked items, failures, or re-entry from DISCOVERY.
