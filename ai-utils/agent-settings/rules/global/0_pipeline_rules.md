---
trigger: always_on
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Shared/reusable content → extract to `modules/` (preferred). Role-specific overflow → split into a `_ref.md` companion. Never exceed this limit.

# PIPELINE — Multi-Agent Development Protocol
**Single file for agent mode (auto-loaded) and browser mode (upload manually).**

---

## ⚡ BROWSER MODE OVERRIDES (skip in agent mode)

No terminal. No `run_agent.bat`. Treat uploaded context file as Single Source of Truth.
State `"Using uploaded context from [filename]"` before any work.
Every code change must be output as a labelled block — the user applies it manually:
```
FILE: [exact/path/to/file.ext]
<<<SEARCH
[original code]
<<<END>>>
<<<REPLACE
[new code]
<<<END>>>
```

**Upload ALL of these files at session start:**
| Type | Files |
|------|-------|
| Always-on rules (read immediately) | `0_analysis_rules.md` ⚠️ read now · `0_coding_rules.md` ⚠️ read now · `0_context_rules.md` (Browser Override section only) |
| Pipeline ops reference | `0_pipeline_ops_ref.md` (§7A-§7B, always) · `0_pipeline_ops_ref_p2.md` (§7C-§7F, load when resolving artifacts or resuming dumps) |
| Browser role overrides | `0_pipeline_rules_browser_ref.md` — load when starting any browser session · `BROWSER_SESSION_CONTINUATION_RULE.md` — load when starting any browser session expected to last >10 turns |
| Project rules (always active) | `1_naming_conventions.md` · `2_webview2_standards.md` · `3_infrastructure_security.md` · `4_workflow_standards.md` |
| This file | `0_pipeline_rules.md` |
| Workflow files — discovery (load on demand) | `workflow_01_discovery.md` · `workflow_01_discovery_p4.md` · `workflow_01_discovery_cf_ref.md` · `workflow_01_discovery_ref.md` · `workflow_01_discovery_porting_ref.md` |
| Workflow files — pipeline roles (load on demand) | `workflow_02_validator.md`+`_ref.md` (VALIDATOR) · `workflow_02_planner.md`+`_ref.md`+`_phase2_ref.md` (PLANNER) · `workflow_03_implementer.md`+`_ref.md` (IMPLEMENTER) · `workflow_05_pr_reviewer.md`+`_ref.md` (PR_REVIEWER) · `workflow_04_delta.md`+`_ref.md` (DELTA) · `workflow_06_flow_auditor.md`+`_ref.md` (FLOW_AUDITOR) |

---

## Role Activation — Rule Active Confirmation Block (Mandatory Output)

> Full template: see `modules/output_blocks.md` §"Role Activation".
> Every role outputs this block on activation — compact rule summary + CF status.
> Do NOT skip even for short sessions.

---

## Pipeline Roles

| Trigger | Action |
|---------|--------|
| `"Act as DISCOVERY"` | Stage 1 — requirement gathering + architecture consensus |
| `"Act as VALIDATOR"` | Stage 1.5 — independent cross-check (run in separate session after DISCOVERY Phase 4C) |
| `"Act as FLOW_AUDITOR"` | Stage 1.8 — standalone flow discovery + line-by-line code audit. Invokable at any pipeline stage. |
| `"Act as PLANNER"` | Stage 2 — implementability dry-run + task generation |
| `"Act as IMPLEMENTER"` | Stage 3 — execute tasks + self-verify |
| `"Act as PR_REVIEWER"` | Stage 4.5 — forensic diff review + claim verification (mandatory before DELTA) |
| `"Act as DELTA"` | Stage 5 — triage failures + replan |

Flow: DISCOVERY → spec.md (gate=GO) → PLANNER → 02_IMPLEMENTATION_PLAN.md → IMPLEMENTER → 03_IMPLEMENTATION_LOG.md → PR_REVIEWER → 05_REVIEW_REPORT.md → DELTA → 04_DELTA_PLAN.md (max 3 loops, then human review).

**Standard paths:** `Docs/[Project]/specs/[Feature]_spec.md` · `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` · `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md` · `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_04_DELTA_PLAN.md`

> ⚠️ The pattern `.pipeline/` (dot-prefixed, project-root) is **not used** in this repo. All pipeline artifacts live under `Docs/[Project]/pipeline/[Feature]/`. Agent mode: `pipeline.py find --feature [F] --type plan` prints the exact path. Browser mode: navigate to that folder and pick the file with the highest timestamp prefix for the type you need — see `0_pipeline_ops_ref.md` §7C.

---

## Role → Workflow File Map

| Trigger | Workflow File | Writes | On Failure |
|---------|--------------|--------|-----------|
| `"Act as DISCOVERY"` | `workflow_01_discovery.md` | `[Feature]_spec.md` | HOLD (OQs open) / REDO (>20% corrections) |
| `"Act as VALIDATOR"` | `workflow_02_validator.md` | CORRECTION/MISSED/AGREE output (no file written) | Paste output to DISCOVERY session |
| `"Act as FLOW_AUDITOR"` | `workflow_06_flow_auditor.md` | `FLOW_REGISTRY.md` (updated) + `YYYYMMDD_AUDIT_FINDINGS.md` | NEEDS_HUMAN → add to HOLD in plan |
| `"Act as PLANNER"` | `workflow_02_planner.md` | `02_IMPLEMENTATION_PLAN.md` | BLOCK → 3 resolution paths |
| `"Act as IMPLEMENTER"` | `workflow_03_implementer.md` | `03_IMPLEMENTATION_LOG.md` (timestamped — pipeline.py save auto-prefixes) | SKIPPED/FAILED → PR_REVIEWER |
| `"Act as PR_REVIEWER"` | `workflow_05_pr_reviewer.md` | `05_REVIEW_REPORT.md` | HOLD → resolve before DELTA / GO → activate DELTA |
| `"Act as DELTA"` | `workflow_04_delta.md` | `04_DELTA_PLAN.md` | Loop 3 → human review |

**Legacy names:** ARCHITECT → DISCOVERY · FORGE → PLANNER
**Note:** VALIDATOR is now a distinct pipeline role (Stage 1.5), not a legacy name.

---

## Section 1 — Exhaustive Analysis Protocol

> ⚠️ **READ `0_analysis_rules.md` NOW** — it is authoritative for Rules A–F.
> This section defines when each rule fires. No role is exempt.

| Situation | Rules |
|-----------|-------|
| Any list >5 REQ-IDs, BUG-IDs, or tasks | A, B, C, E |
| DISCOVERY Phase 4 self-validation | A, B, C, E |
| DISCOVERY Phase 5 cross-model absorption | A, B, C, D, E — full ledger mandatory |
| VALIDATOR (entire session) | A, B, C, E mandatory · D (Cross-Reference Ledger) only when a second source document or previous spec version is uploaded — see workflow_02_validator.md Source Mode Detection |
| PLANNER Phase 1 dry-run | A, B, C, E |
| DELTA triaging non-COMPLETED tasks | A, B, C, E |
| Any pasted `.md` list of requirements | A, B, C, E |
| Session interrupted mid-batch | F first — Resumption Contract before anything |

Rules: **A** Inventory Declaration · **B** Max 8 items/batch, hard PAUSE · **C** Per-item verdict (Status + Finding + Action, no silent skips) · **D** Cross-Reference Ledger before any cross-model writing · **E** PASS must be written explicitly — silence is a protocol failure · **F** Resumption Contract on resume — confirm point before continuing.

---

## Section 2 — Global Coding Rules

> ⚠️ **READ `0_coding_rules.md` NOW** — it is authoritative for Rules 1–12.
> Do not write or modify any code until read.

| Situation | Rules |
|-----------|-------|
| Any SEARCH/REPLACE block (PLANNER, IMPLEMENTER, DELTA) | All 12 |
| Code snippet in a spec (DISCOVERY) | 1, 2, 4, 6, 7, 10, 11 |
| Rename or refactor (any role) | 1, 3, 11 |
| Config / YAML / JSON change | 11 |

---

## Section 3 — Role Browser Overrides → See `0_pipeline_rules_browser_ref.md`

Load `0_pipeline_rules_browser_ref.md` when starting any browser session.
Contains per-role upload checklists and browser-mode operating instructions for: VALIDATOR, FLOW_AUDITOR, DISCOVERY, PLANNER, IMPLEMENTER, DELTA, PR_REVIEWER.

---

## Quick Reference

| Role | Trigger | Output | On Failure |
|------|---------|--------|------------|
| DISCOVERY | `"Act as DISCOVERY"` | `[Feature]_spec.md` | HOLD / REDO |
| FLOW_AUDITOR | `"Act as FLOW_AUDITOR"` | `FLOW_REGISTRY.md` + `YYYYMMDD_AUDIT_FINDINGS.md` | NEEDS_HUMAN → HOLD |
| PLANNER | `"Act as PLANNER"` | `02_IMPLEMENTATION_PLAN.md` | BLOCK → 3 paths |
| IMPLEMENTER | `"Act as IMPLEMENTER"` | `03_IMPLEMENTATION_LOG.md` | SKIPPED/FAILED → PR_REVIEWER |
| PR_REVIEWER | `"Act as PR_REVIEWER"` | `05_REVIEW_REPORT.md` | HOLD / GO → DELTA |
| DELTA | `"Act as DELTA"` | `04_DELTA_PLAN.md` | Loop 3 → human review |

**Status:** `COMPLETED` · `PARTIAL` · `SKIPPED` · `FAILED`
**Triage (DELTA):** `RESCHEDULE` · `REPLAN` · `ESCALATE` · `DROP`

| Complexity | Lines | Model |
|------------|-------|-------|
| SMALL | <200 | ANY |
| MEDIUM | 200–500 | ANY |
| LARGE | >500 | PREFER_CAPABLE |
| PREFER_CAPABLE | any | Sonnet/Opus — required for CRITICAL CF tasks |
| REF | any | P3 optional refactoring — only if user opts in |

| Symptom | Fix |
|---------|-----|
| SEARCH mismatch in browser | Output corrected block with `FILE:` label |
| Implementer improvises design | PLANNER spec too vague → DELTA REPLAN |
| Hallucinated file reference | PLANNER dry-run missed it → DELTA AMBIGUITY |
| Same task fails 3 loops | Escalate — missing context or env issue |
| Token limit mid-task | Log remaining SKIPPED, note "Resume from TASK-XXX" |
