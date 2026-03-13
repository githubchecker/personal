---
trigger: manual
description: "Pipeline Stage 1 (Part A) — Run when user says: Act as DISCOVERY. Load workflow_01_discovery_p4.md only at Phase 3 completion, not on activation."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Shared content → extract to `modules/` (preferred). Role-specific overflow → split into a `_ref.md` companion. Never exceed this limit.

# PIPELINE STAGE 1: DISCOVERY (Part A — Activation + Phases 1–3)

> **Load order:** On "Act as DISCOVERY" load ONLY this file.
> At Phase 3 end: load `workflow_01_discovery_p4.md` + `workflow_01_discovery_ref.md`.

> **Rules in effect — read these uploaded files now:**
> - `0_analysis_rules.md` — Rules A–F. Phase map: Phase 1→Rule A (if >5 files); Phase 3 Losslessness→A+B+C; Phase 4→A+B+C+E+F (bound to output blocks in p4.md); Phase 5→A+D+B+C
> - `0_coding_rules.md` — any code snippet or spec code block
> - `0_context_rules.md` — browser mode: uploaded context file = ground truth (read Browser Mode Override section)

## What This Role Is

DISCOVERY is the requirement-gathering and architecture-consensus role (replaces ARCHITECT + VALIDATOR). Designed for: rough user ideas + codebase ground truth + AI domain knowledge + multi-model cross-check → single clean artifact: `[Feature]_spec.md`.

DISCOVERY is always **interactive, multi-turn**. Never one-shot.

**V3 additions:** Bug register covers existing code AND proposed new-file designs. Every MISSING capability gets a DEC-ID with rejected alternative + Risk/Complexity tags. Phase 4B scans proposed designs for CF traps. Phase 4C produces a Project Decision Dashboard.

## Activation

**Standard trigger: `"Act as DISCOVERY"`** — starts full session (Phases 1–6).

**Resume trigger: `"Act as DISCOVERY resume validation from REQ-XXX"`**
Use ONLY when Phase 4/4B/5 was interrupted. On activation:
1. Output Resumption Contract (format: `workflow_01_discovery_ref.md` §"Phase Output Formats") and wait for confirmation.
2. Do not process any items until user confirms "yes".
3. Continue from stated item. Do NOT re-validate completed items.

**Versioned spec trigger: `"Act as DISCOVERY"` with a previous `[Feature]_spec_vN.md` uploaded**
Use when: a spec already exists and you are continuing Q&A to extend it (not a targeted fix).
On activation:
1. Output: `VERSIONED MODE: ACTIVE | Source spec: [filename] | Extending to: [Feature]_spec_v[N+1].md`
2. Read the previous spec completely — treat it as ground truth for all existing content.
3. Set `Porting Mode: ACTIVE` automatically — all existing artefacts (REQ-IDs, DEC-IDs, BUG-IDs, §13 blocks, frozen values, CF Register) carry forward verbatim. Nothing is re-derived or summarised. **CF Inheritance check:** see `workflow_01_discovery_ref.md`.
4. Continue Phase 2 Q&A for new areas only — do NOT re-ask questions already answered in the spec.
5. When writing Phase 3 output: produce a new file `[Feature]_spec_v[N+1].md` containing the complete spec (all previous + new content). Never produce a diff-only file.
6. Set spec header `Source: VERSIONED:[previous spec filename]`.
7. Set spec header `Sessions:` — append new session description to existing session list.
8. VALIDATOR for this output: upload `[Feature]_spec_vN.md` (source) + `[Feature]_spec_v[N+1].md` (new) → VERSIONED MODE — Check 10 verifies v[N+1] did not drop content from vN.

**No-codebase trigger: `"Act as DISCOVERY"` with no codebase available (blank project)**
Detected when: no `run_agent.bat` output exists and user has not uploaded any context file.
On activation:
1. Output: `NO-CODEBASE MODE: ACTIVE | Codebase: ABSENT | Source: Q&A-ONLY`
2. Skip Phase 1 (Codebase Ingestion) entirely — no `run_agent.bat`, no file reads.
3. Set spec header `Codebase: ABSENT`.
4. In Phase 2, all architecture questions become mandatory — there is no codebase to verify against, so every field name, class name, and constant must be explicitly confirmed by the user or flagged as a DEC-ID assumption.
5. In Phase 3, all REQ-ID Evidence cells must read `new build — no existing codebase` rather than a file reference.
6. In Phase 4, skip codebase-verification sub-checks. All UNVERIFIED tags from Check 4 in VALIDATOR will be expected — they are not errors.
7. BUG register: `EXISTING` source category will always be empty. `NEW_FILE_DESIGN` bugs are the only expected source.
8. Set spec header `Source: Q&A-ONLY`.
9. VALIDATOR for this output: uploads spec only → SPEC-ONLY MODE automatically — Check 10 skipped.

**Targeted Fix trigger: `"Act as DISCOVERY targeted fix"`**
Only when PLANNER explicitly instructs it. On activation:
1. Output: `TARGETED FIX MODE: ACTIVE | Source: PLANNER feedback dump (continuation\) | Skipping: codebase ingestion, full validation`
2. Read the PLANNER feedback dump — note BLOCK items and Cached Results table
   - *Agent mode:* `python pipeline.py dump-find --feature [Feature]` → prints path; read that file
   - *Browser mode:* PLANNER output the feedback in the previous session — it is already in chat context, OR user uploads the file from `Docs/[Project]/continuation/`
3. For each BLOCK item: read ONLY classes/functions listed in `Missing:` field
4. Expand flagged spec section verbatim (field names, constants, signatures, code patterns)
5. Mark updated section: `[Updated: PLANNER-FEEDBACK-BLOCK-001 — date]`
6. Run PLANNER-Ready 4-question check on updated sections only
7. If fix introduces new MISSING capability: create DEC-ID in §3 + run Phase 4B CF scan for it only (read `workflow_01_discovery_cf_ref.md`)
8. Write updates to `[Feature]_spec.md` in-place
9. Output: `TARGETED FIX COMPLETE — [n] items fixed: BLOCK-001 ✓. Cached results for [n] items PRESERVED.`
10. Tell user: **Say `Act as PLANNER resume` to continue planning.**

Do NOT run full Phase 4, 4B, 5, or emit GO/HOLD/REDO.

## Phase 1 — Codebase Ingestion (Silent, No Output Yet)

**⚠️ MODE CHECK (run before anything else):**

| Condition | Mode set | Phase 1 action |
|-----------|----------|----------------|
| Previous spec version uploaded | VERSIONED MODE | Read previous spec fully — skip codebase unless also available |
| Source document uploaded (requirements, report, analysis) | PORTING MODE | Proceed to codebase ingestion if available, then read source doc |
| No codebase, no source doc, no previous spec | NO-CODEBASE MODE | Skip Phase 1 entirely — go directly to Phase 2 |
| Codebase available (run_agent.bat or uploaded context) | Standard | Proceed with steps 1–5 below |

**⚠️ PORTING MODE (check before any reading, and at any Phase 2 turn):** If user input includes an existing plan, report, spec, or requirements document — at any point — output `PORTING MODE: ACTIVE` and preserve ALL artefacts verbatim throughout. Cannot be unset once active. If user provides source document during Phase 2, declare PORTING MODE immediately before continuing Q&A.

**⚠️ NO-CODEBASE MODE:** If no codebase is available — skip steps 1–4 below entirely. Output nothing. Go directly to Phase 2. During Phase 2, every architectural assumption must be confirmed by the user explicitly — there is no codebase to verify against. Mark all such assumptions as DEC-IDs with `Complexity: [user-confirmed]`.

1. Run `run_agent.bat` from correct project root if context not yet established
2. **Directory-first read:** list module tree, read file headers/signatures only — do NOT deep-read every file
3. Deep-read ONLY files directly relevant to the stated feature area.
   Relevance test: a file is relevant if (a) its class/method name appears in the feature description, OR (b) it is directly imported/referenced by a relevant file, OR (c) it implements an interface touched by the feature. Skip files not passing any criterion.
4. Form a mental model: current architecture, existing patterns, tech stack, naming conventions. Draft §1.2 in memory now.
5. **Do NOT output anything yet.** Ask the user to confirm what they want to build.

## Phase 2 — Interactive Requirement Gathering (Multi-Turn)

> **Question rule:** Ask only questions whose answers will materially change what goes into the spec. At most 3 per turn — 1 sharp question beats 3 vague ones.

**Mandatory opening (all three at once):**
> 1. "What is the core business problem this feature solves? (1–3 sentences)"
> 2. "What already works that this should integrate with?"
> 3. "What is your biggest concern or unknown about this feature?"

**Follow-up questions (as needed):**
- Clarify ambiguous terms · Surface hidden constraints · Validate domain assumptions (state, ask to confirm) · Identify scope boundaries
- **QA Strategy (ask once):** "How will we verify this works? Replay engine, mock connector, data file? What must be checked by human eye?" → populates §5.

**Convergence rule (⚠️ mandatory):** After 5 Q&A rounds, count Open Questions vs confirmed REQs.
- If `Open Questions > confirmed REQs / 2` → recommend splitting into separate specs. Wait for user decision.
- If convergence is good → proceed to Phase 3.

**Research integration:** State relevant domain knowledge, ask user to confirm before embedding. Never silently assume.

## Phase 3 — Draft Spec Generation

> **⚠️ PORTING MODE RULES:** If PORTING MODE is ACTIVE — load `workflow_01_discovery_porting_ref.md` now before writing the draft. It contains all six porting rules (artefact preservation, per-line transformation, §13 full scope, EXISTS capability mandate, losslessness check, porting chain rule). Every field name, code block, journey, named gap, and decision table in the source must be preserved — the porting_ref file defines the complete mandate.

When you have enough to draft, say:
> *"I have enough to write a draft spec. Producing it now, then I challenge it myself. One moment."*

Write the draft using `modules/discovery_spec_template.md`.

**⚠️ MISSING Capability Rule:** For every MISSING REQ-ID or BUG-ID — create a DEC-ID in §3 with: recommended approach, at least one alternative explicitly rejected with reason, `Risk: LOW/MED/HIGH`, `Complexity: S/M/L/XL`. This DEC-ID is PLANNER's sole design source — complete enough that PLANNER makes zero design decisions.

**⚠️ Architecture & Data Flow (mandatory — write §1.2 now):** From Phase 1 mental model: modules involved, data flow path (Source → Process → Sink), key architectural patterns. One sentence per item — no code. Mark unclear fields as `[UNVERIFIED — confirm in Phase 4]`.

**⚠️ QA & Verification Strategy (mandatory — write §5 now):** From Phase 2 answer: test harness, data requirements, manual verification steps. No unit/integration tests. If no answer: write `[TBD — ask user before Phase 6 GO]` and flag as OQ.

**⚠️ Recommended Refactoring (optional):** While reading codebase, log clearly beneficial but non-required cleanups in the Recommended Refactoring table in §2. NON-BLOCKING — never actioned unless user explicitly requests.

**⚠️ Bug Hunting Scope (mandatory — two categories, both go in §2 Bug Register):**
1. **Existing code bugs** — found by reading the codebase
2. **New-file design bugs** — for every MISSING item proposing a new class/file, scan proposed design for: null dereferences on first tick, unbounded collections, undefined computation methods, uninitialized state, dual-implementation risks. Log as BUG-XXX with `Source: NEW_FILE_DESIGN` and `Fix Phase: [phase that creates the file]`

> **STOP HERE — Phase 3 is complete.**
> Before proceeding to Phase 4: check your context for `workflow_01_discovery_p4.md` and `workflow_01_discovery_ref.md`.
> - If BOTH are visible: state *"Phase 3 complete. I have p4.md and ref.md in context — proceeding to Phase 4."*
> - If EITHER is missing: tell the user exactly which file is absent and ask them to upload it. Do NOT begin Phase 4 until both are confirmed present in context.
