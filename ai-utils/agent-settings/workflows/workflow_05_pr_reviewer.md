---
trigger: manual
description: "Pipeline Stage 4.5 — Run when user says: Act as PR_REVIEWER"
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# PIPELINE STAGE 4.5: PR_REVIEWER

> **Rules in effect for this role -- read these uploaded files now:**
> - `0_analysis_rules.md` -- apply Exhaustive Analysis Protocol for every claim verification
> - `0_coding_rules.md` -- used when evaluating production quality of changed code
> - `0_context_rules.md` -- diff file is ground truth in browser mode; codebase in agent mode

**Activation:** User says `"Act as PR_REVIEWER"` or `"Act as PR_REVIEWER --feature [Feature]"`

**Position in pipeline:** Runs AFTER IMPLEMENTER produces `03_IMPLEMENTATION_LOG.md` and
BEFORE DELTA runs. PR_REVIEWER is the mandatory gate between them.

```
IMPLEMENTER -> 03_LOG -> [PR_REVIEWER] -> 05_REVIEW_REPORT.md -> DELTA -> 04_DELTA_PLAN.md
```

**Reads:**

*Agent mode:*
- Diff: runs `tools\make_pr_diff.bat -Feature [Feature]` automatically if diff files not present,
  then reads `browse-drop/[Feature]_06_PR_REVIEWER/[Feature]_pr_diff.txt`
- Log: `python pipeline.py find --feature [Feature] --type log`
- Plan: `python pipeline.py find --feature [Feature] --type plan`
- Spec: `Docs/[Project]/specs/[Feature]_spec.md`
- Arch docs: `Docs/[Project]/TECHNICAL_ARCHITECTURE.md` + `DEPLOYMENT.md`

*Browser mode:*
- Upload all files from `browse-drop/[Feature]_06_PR_REVIEWER/` folder
- The folder is assembled by `sync_and_drop.bat -Role PR_REVIEWER -Feature [Feature]`
- It contains: rules_pack.zip, diff files, log, plan, spec, arch docs

**Writes:**

*Agent mode:* `python pipeline.py save --feature [Feature] --type review --file [path]`
-> saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_05_REVIEW_REPORT.md`

*Browser mode:* Output complete review report in chat with pipeline header.
User saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_05_REVIEW_REPORT.md`.

---

## Core Mandate -- Non-Negotiable

PR_REVIEWER is a **forensic code reviewer**, not a log summariser.
Every COMPLETED claim in the log MUST be verified against the actual diff.
A claim not found in the diff is `FABRICATED` regardless of what the log says.

**The diff is ground truth. The log is a claim. Never reverse this.**

---

## Phase 1 -- Orientation (do this first, before any analysis)

1. **Split-Mode Check:** Read `Split Mode:` field in plan header. If `SPLIT` → output "SPLIT MODE DETECTED: Upload all IMPL_P0n.md phase files before I begin." Do NOT proceed until uploaded.
2. Read the diff stat file (`[Feature]_pr_diff_stat.txt`) to get a map of what files changed.
3. Read the implementation log header (Total/CF Status line).
4. Read the plan + phase files for CF Register and task list.
5. Build an internal index: `{ task_id → [files claimed changed] }` from the log.
6. Build a second index: `{ file → [hunks in diff] }` from the diff.

State: `"Orientation complete. [n] tasks claimed, [n] files in diff, [n] CFs to verify."`

---

## Phase 2 -- Claim vs Reality Cross-Check (apply Rule A + B from 0_analysis_rules.md)

> **Rule B applies here:** Max 8 tasks per batch. Use the standard `<<<BATCH [n] COMPLETE>>>` pause block format from `0_analysis_rules.md` §Rule B. Do NOT write a combined summary at the end — each task must be verdicted before moving to the next batch.

For EVERY task marked COMPLETED or PARTIAL in the log:

**Step 2a -- File presence check:**
Does the diff contain ANY hunk touching the files the task claims to have changed?
- YES -> proceed to Step 2b
- NO  -> mark task `FABRICATED`. Record it. Do not continue checking this task.

**Step 2b -- Change content check:**
Does the diff hunk match the SEARCH/REPLACE block from the plan (or a reasonable equivalent)?
- FULL MATCH -> mark `VERIFIED`
- PARTIAL MATCH (some changes present, some absent) -> mark `PARTIAL_VERIFIED`. List what's missing.
- WRONG CHANGE (file changed but not what the task required) -> mark `WRONG_IMPL`. Describe what's there vs what was needed.

**Step 2b.5 — ⚠️ MANDATORY Ground Truth Reconciliation (agent mode only — before issuing FABRICATED):**

The diff window may not capture all changes (e.g., a Delta Loop applied after the diff baseline, or files outside tracked paths). Before issuing ANY `FABRICATED` verdict:

1. **Targeted codebase read:** Use `view_file` or `grep_search` on the actual target file to check whether the claimed change is present in the LIVE codebase.
2. **If found in codebase but NOT in diff:** Verdict = `VERIFIED_OUT_OF_BAND`. Note: *"Change confirmed in live codebase at [file:line] but absent from diff window. Diff window is incomplete — likely applied in a prior loop or session outside this diff range."* Do NOT mark FABRICATED.
3. **If NOT found in either diff OR codebase:** Verdict = `FABRICATED`. Only now is the FABRICATED verdict valid.
4. **Log the reconciliation:** Every FABRICATED verdict MUST include: `"Ground truth check performed: grep_search/view_file confirmed absent at [file path]."` A FABRICATED verdict without this statement is a protocol violation.

> **Why this step exists:** Diff-based review has a fundamental blind spot when the diff window is bounded to a specific commit range and the IMPLEMENTER applied changes in a separate loop/session. Without a live codebase check, the reviewer silently conflates "not in diff" with "not in codebase" — producing false FABRICATED verdicts on real implementations.

> Violation examples: see `modules/violation_examples.md` §"FABRICATED Ground Truth Check"


**Step 2c -- CF Gate verification (CRITICAL tasks only):**
For every CF GATE item in a task:
- Find the exact code in the diff OR live codebase (agent mode: always grep if not visible in diff) that satisfies the CF constraint.
- Quote the specific lines that prove compliance, with `[file:line]` citation.
- If the lines are absent from BOTH diff AND codebase -> mark `CF_VIOLATED`. This is P0 regardless of task status.

---

## Phase 3 -- Call Chain Integrity (apply Rule C from 0_analysis_rules.md)

For every task that changed a method signature, interface, class name, constructor, or public API:

1. Search the diff for ALL files that reference the old name/signature.
2. **Agent mode additionally:** `grep_search` the FULL codebase for the old name — diff only shows changed files; unchanged callers are invisible to diff.
3. Check whether each reference site was also updated in the same diff or live codebase.
4. If a reference site exists in the diff and was NOT updated -> flag as `BROKEN_CALLER`.
5. If a reference site is outside the diff (unchanged files) -> flag as `CALLER_RISK` in agent mode only after confirming via grep.
   Note: browser mode can only see what's in the diff — flag as `CALLER_RISK (unverifiable in browser mode)`.

---

## Phase 4 -- Production Quality Audit

For each VERIFIED or PARTIAL_VERIFIED task, scan the changed code in the diff for:

| Issue | Severity | What to look for |
|-------|----------|-----------------|
| Unhandled exception paths | HIGH | async calls without try/catch, MongoDB ops without error handling |
| Null dereference risk | HIGH | `.Value` without null check, first-or-default without null guard |
| Async misuse | HIGH | `.Result` or `.Wait()` on Task, missing `await`, `async void` non-event |
| Hardcoded values | MEDIUM | connection strings, keys, environment names in code |
| TODO/FIXME left in | MEDIUM | any `// TODO`, `// FIXME`, `// HACK` in new code |
| Missing audit trail | MEDIUM | financial/payment changes without audit log write |
| DateTime.Now usage | LOW | project rule: prohibited -- must use UTC |
| Debug logging left in | LOW | `Console.WriteLine`, excessive `Debug.Log` in production paths |
| Missing function documentation | LOW | Any new `public` or `protected` method added in diff with no XML doc comment (`/// <summary>`) and a non-descriptive name (e.g., `DoWork`, `Process`, `Execute`, `Handle` with no qualifier) — Rule 10 of `0_coding_rules.md` |

Only flag issues introduced or exposed by the diff -- do not flag pre-existing code.

---

## Phase 5 -- Documentation Debt Check (apply 4_workflow_standards.md Check B)

For every file changed in the diff, evaluate:

| Doc | Must update if... |
|-----|------------------|
| `DEPLOYMENT.md` | New env vars, config keys, startup sequence, scripts, ports, build steps |
| `TECHNICAL_ARCHITECTURE.md` | New architectural component, changed data format, new security boundary, new service |
| `[Feature]_spec.md` | Implementation revealed a spec gap or correction (flag only -- do not edit spec here) |
| Project rule files | New "must not do" pattern found during review |

Output a doc debt table even if all items are "no update needed" -- this confirms the check ran.

---

## Phase 6 -- Missing Task Detection

Cross-check: tasks in the plan that are NOT in the log at all (not COMPLETED, not SKIPPED -- simply absent).
These are silently dropped tasks. List each one with its CF status and complexity.

---

## Review Verdicts (per task)

| Verdict | Meaning |
|---------|---------|
| `VERIFIED` | Claim confirmed in diff. CF gates satisfied. No quality issues. |
| `VERIFIED_WITH_WARNINGS` | Claim confirmed but quality issues found. List warnings. |
| `PARTIAL_VERIFIED` | Some changes present, some absent. Describe gap. |
| `FABRICATED` | Claimed COMPLETED but no matching diff hunk found. P0 for DELTA. |
| `CF_VIOLATED` | CF GATE constraint breached in actual code. P0 regardless of other status. |
| `WRONG_IMPL` | Change present but implements something different from the plan requirement. |
| `BROKEN_CALLER` | Signature changed, callers in diff not updated. Will break at compile/runtime. |
| `MISSING` | Task in plan, not mentioned in log at all. |

---

## Go / No-Go Gate

PR_REVIEWER issues a GO or HOLD verdict for DELTA:

**HOLD (DELTA must not run until resolved):**
- Any `FABRICATED` task with CF GATE
- Any `CF_VIOLATED` finding
- Any `BROKEN_CALLER` finding

**GO with mandatory DELTA grep task:**
- Any `CALLER_RISK` finding: DELTA must create a `DELTA-TASK` of type `GREP_VERIFY` — grep the full repo for the old signature before the feature ships. If undeclared callers found, treat as BROKEN_CALLER.

**GO with P0 DELTA tasks (DELTA runs but these are mandatory P0):**
- Any `FABRICATED` task without CF GATE
- Any `PARTIAL_VERIFIED` task
- Any `MISSING` task
- Any `VERIFIED_WITH_WARNINGS` with HIGH severity issues that are NOT in the blocking list below

**HOLD additions (HIGH severity issues that block shipping):**
- Async misuse: `.Result` / `.Wait()` on Task, `async void` non-event handler → deadlock risk
- Null dereference: `.Value` without null check, `.First()` without null guard → crash on production data
- Hardcoded secret or connection string in new code → security breach risk
These three HIGH patterns are always HOLD regardless of task verdict.

**CLEAN GO (DELTA runs normally):**
- All tasks `VERIFIED` or `VERIFIED_WITH_WARNINGS` with LOW/MEDIUM only
- All CFs confirmed in code
- No missing tasks

---

## Output Format -> Load `workflow_05_pr_reviewer_ref.md`

> Load `workflow_05_pr_reviewer_ref.md` before writing any output.
> It contains the full `05_REVIEW_REPORT.md` template.

---

**After writing:**
*Agent mode:* Run `python pipeline.py save --feature [Feature] --type review --file [path]`
then say: *"Review report saved. Verdict: [GO/HOLD]. [n] FABRICATED, [n] CF_VIOLATED,
[n] VERIFIED. [If GO:] Activate DELTA? (yes/no)"*

*Browser mode:* Say: *"Review report written. Verdict: [GO/HOLD]. Save the file above to
`Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_05_REVIEW_REPORT.md` then upload it
when starting DELTA."*
