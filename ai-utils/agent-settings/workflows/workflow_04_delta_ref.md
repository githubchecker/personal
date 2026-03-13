---
trigger: manual
description: "DELTA Output Reference — 04_DELTA_PLAN.md template, DELTA-TASK format, escalation format, go/no-go format, stage failure handling. Load before writing DELTA output. Split from workflow_04_delta.md to stay under 12 000 chars."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# DELTA — Output Format Reference

> **This file is Part B of DELTA.** Load it before writing any `04_DELTA_PLAN.md` output.
> Contains: the full `04_DELTA_PLAN.md` template, DELTA-TASK format, escalation output, Go/No-Go format, and stage failure table.

## Output Format: `04_DELTA_PLAN.md`

```markdown
# Delta Reassessment Plan
Generated: [date] | Loop: [n of 3 max]
Based on: 03_IMPLEMENTATION_LOG_R[n].md
Active plan used: [02_IMPLEMENTATION_PLAN or 04_DELTA_PLAN — which one]
CF Status: CRITICAL=[n] verified | CRITICAL=[n] unverified | UNBOUND_CF absorbed=[n]

## Delta Summary
[3–5 sentences: what completed, what remains, root causes of failures, CF status, confidence level]

## Triage Table
| Task | Decision | CF Gate? | Root Cause |
|------|----------|----------|------------|
| TASK-002 | REPLAN | YES — CF-001 unverified | Wrong function + CF fix steps incomplete |
| TASK-005 | RESCHEDULE | NO | Env var was missing, now confirmed present |
| TASK-007 | ESCALATE | NO | Requires human: approach A vs B |
| TASK-009 | DROP | NO | Covered by TASK-003 completion |

## Spot-Check (Completed Tasks)
| Task | Result | Issue |
|------|--------|-------|
| TASK-001 | PASS | — |
| TASK-003 | FLAG | Condition inverted at line 45 → becomes DELTA-TASK-001 |

## Revised Tasks for Next Run

---
### DELTA-TASK-001
**Origin:** TASK-XXX (REPLAN) / DISCOVERY-XXX (UNBOUND_CF absorbed)
**What Changed From Original:** [exact correction — why original was wrong, what's now correct]

**Title:** [name]
**Type:** BUG_FIX / FEATURE / REFACTOR / CF_REGRESSION
**Priority:** P0/P1/P2/P3  |  **Complexity:** SMALL/MEDIUM/LARGE  |  **Model:** ANY/PREFER_CAPABLE
**Depends On:** None / DELTA-TASK-XXX
**CF Embedded:** CF-XXX (CRITICAL — GATE) / NONE  [carry forward from original task — never drop]

**Why:** [updated context — what the failure revealed]
**Location:** [corrected file / function / line]

**⚠️ Codebase Verification (mandatory before writing Exact Change):**
Confirm: *"`[ClassName.MethodName]` exists in `[file path]` at approximately line [n]."*
If cannot confirm from codebase context: mark as ESCALATE — do not write Exact Change.

**File I/O Permissions:**
- Files to modify: [exhaustive, locked list]
- Files to create: [or NONE]
- Files to delete: [or NONE]

**Exact Change (MANDATORY: SEARCH/REPLACE blocks — same format as PLANNER tasks):**
Same verbatim `<<<SEARCH` / `<<<REPLACE` / `<<<END>>>` blocks as PLANNER. No prose steps.
If target function not confirmed in codebase: mark as ESCALATE — do not write Exact Change.

[If task has CF GATE — include explicitly labelled CF fix block:]
⚠️ CF-XXX FIX (CRITICAL — GATE): [CF short name]
FILE: [path]
<<<SEARCH
[exact context]
<<<END>>>
<<<REPLACE
[code with CF fix applied — unambiguous]
<<<END>>>

**Verification Checklist:**
- [ ] [specific criterion]
- [ ] [edge case]
- [ ] ⚠️ CF-XXX VERIFIED: [concrete, testable criterion — specific line of code that must exist]

**Post-Change Documentation Check (mandatory — apply `4_workflow_standards.md` Check A + Check B):**
IMPLEMENTER must run Check A (caller detection) and Check B (doc impact) after executing this DELTA-TASK.

**Watch Out For:** [what the previous attempt got wrong]

---
## Escalations (Human Input Required)
### ESCALATION-001
**Question:** [specific decision needed — not vague]
**Option A:** [description + tradeoff]
**Option B:** [description + tradeoff]
**Recommended:** A / B / None (with one-sentence reasoning)
**Unblocks:** TASK-XXX, TASK-XXX

---
## Go / No-Go
**Verdict:** GO / HOLD
**Reason (if HOLD):** [what must be resolved — unverified CRITICAL CFs always force HOLD]
**Tasks Remaining:** [n]  |  **Loop:** [n] of 3
**Unverified CRITICAL CFs:** [n]  ← must be 0 for GO
```

---

## Stage Failure Handling

| Situation | Action |
|-----------|--------|
| Loop 3 exhausted, tasks remain | Output Post-Loop-3 Human Review Block. Wait. Do NOT loop further. |
| All tasks ESCALATED | Surface all escalations immediately. Do NOT output GO. |
| DELTA-TASK references unverified file | Mark as ESCALATE — do not generate Exact Change steps |
| Spot-check reveals COMPLETED task is broken | Add as DELTA-TASK with type FLAG, priority P0. Do NOT re-open original task. |
| CF GATE verified but Spot-Check shows fix absent | Add as DELTA-TASK with type CF_REGRESSION, priority P0. |
| Task has unverified CF GATE | Always REPLAN (never RESCHEDULE). CF fix steps must be corrected. |
| UNBOUND_CF found in Discoveries | Absorb into affected future DELTA-TASKs. Note in Delta Summary. |
| User cannot resolve escalation | Defer to next sprint. Document in Deferred Items. Output GO for remaining non-blocked tasks only. |
| User responds (A) RESUME | IMPLEMENTER re-runs with current 04_DELTA_PLAN.md. No replanning. |
| User responds (B) REDUCE SCOPE | DELTA writes final plan excluding named tasks. For each dropped task carrying a CRITICAL CF GATE: DELTA MUST output a DEFERRED_CF block (format below) before writing the plan. User must acknowledge. |
| User responds (C) REPLAN | PLANNER re-runs Phase 2 for named tasks only. DISCOVERY not re-run unless spec is wrong. |
| User responds (D) ABANDON | Write final 04_DELTA_PLAN.md with ABANDONED status. Stop pipeline. |
| User responds (E) ENV FIX | DELTA re-triages all RESCHEDULE/FAILED tasks against fixed environment. Re-enter triage loop (counts as same loop). |

---

## DEFERRED_CF Block Format (mandatory when REDUCE SCOPE drops a CRITICAL CF task)

```markdown
### DEFERRED_CF: CF-[XXX] — [CF short name]
**Dropped task:** [TASK-ID / DELTA-TASK-ID]
**CF severity:** CRITICAL
**Runtime risk left open:** [1 sentence — what can break in production if this CF is never fixed]
**Recommended next action:** Add as P0 task in next feature spec for this module
**User acknowledgment required:** Reply "acknowledged CF-[XXX] deferred" to proceed.
```
DELTA does NOT proceed to write the reduced plan until user acknowledges every DEFERRED_CF block.

**After writing:**
*Agent mode:* Run `python pipeline.py save --feature [Feature] --type delta --file [path]` to archive the delta plan, then say: *"Delta plan saved. Loop [n] of 3. CF: [n] CRITICAL verified, [n] unverified. GO → Activate IMPLEMENTER for next run? (yes/no) HOLD → Resolve unverified CRITICAL CFs / escalations listed above first."*
*Browser mode:* Say: *"Delta plan written. Loop [n] of 3. CF: [n] CRITICAL verified, [n] unverified. File above includes the pipeline header — save it to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_04_DELTA_PLAN.md` and upload it to start next IMPLEMENTER run. GO/HOLD as indicated above."*

---

## Rule Re-Anchor (Every 10 Tasks Triaged)

> Full block: `modules/output_blocks.md` §"Rule Re-Anchor Block".
> **Trigger:** After triaging tasks 10, 20, 30… output the RULE RE-ANCHOR block before continuing.
> **Gate:** CF unverified > 0 at checkpoint → stop. Do not write the delta plan until resolved.
> **Key DELTA signal:** If CF_VIOLATED tasks are accumulating — surface at re-anchor, not at report end.

