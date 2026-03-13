---
trigger: manual
description: "Pipeline Stage 5 — Run when user says: Act as DELTA"
---

# PIPELINE STAGE 5: DELTA REASSESSMENT

> **Rules in effect for this role — read these uploaded files now:**
> - `0_analysis_rules.md` — apply Exhaustive Analysis Protocol when triaging non-COMPLETED tasks in batches (Rules A–F)
> - `0_coding_rules.md` — apply when writing any SEARCH/REPLACE code block in DELTA-TASKs
> - `0_context_rules.md` — governs codebase access; in browser mode the uploaded context file is ground truth (see Browser Mode Override at top of that file)

**Activation:** User says `"Act as DELTA"`

**Reads (resolve in this order):**

*Agent mode:*
- **Active Plan:** `python pipeline.py find --feature [Feature] --type delta` → if found, use it (Loop 2+). If not found (Loop 1): `python pipeline.py find --feature [Feature] --type plan`
- **Reference Plan (always):** `python pipeline.py find --feature [Feature] --type plan` → load for original REQ-IDs and intent even when using a delta plan
- **Latest Log:** `python pipeline.py find --feature [Feature] --type log` → highest-numbered run by timestamp — no manual `_R3/_R2` guessing
- **Review Report (load if present):** `python pipeline.py find --feature [Feature] --type review` → exit code 0 = load it, it is the primary triage input. Exit code 2 = not produced yet, skip. When present: FABRICATED verdicts override COMPLETED log status; MISSING verdicts add new DELTA-TASKs.

*Browser mode:*
- Navigate to `Docs/[Project]/pipeline/[Feature]/`
- **Active Plan:** most recent `YYYYMMDD_HHMM_04_DELTA_PLAN.md` (Loop 2+) or `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` (Loop 1)
- **Reference Plan:** most recent `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md`
- **Latest Log:** most recent `YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md`
- **Review Report (load if present):** most recent `YYYYMMDD_HHMM_05_REVIEW_REPORT.md` — if the file exists, it is the primary triage input; FABRICATED verdicts override COMPLETED log status; MISSING verdicts add new DELTA-TASKs. If absent, skip.
- Most recent = highest timestamp prefix. Upload files directly — their self-describing headers confirm what they are.

**Writes:**

*Agent mode:* `python pipeline.py save --feature [Feature] --type delta --file [path]`
→ saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_04_DELTA_PLAN.md`

*Browser mode:* Prepend the **browser mode artifact header** (template in `0_pipeline_ops_ref.md` §7C) to the delta plan content, filling all `[bracketed]` fields. Output the complete header + `04_DELTA_PLAN.md` content in chat. User saves to `Docs/[Project]/pipeline/[Feature]/YYYYMMDD_HHMM_04_DELTA_PLAN.md`. Next session: upload this file directly — the self-describing header confirms what it is.

**Loop Number Verification (mandatory — do this before CF Status check):**
1. In agent mode: `python pipeline.py find --feature [Feature] --type delta` — if a previous delta plan exists, read its `Loop:` header field. Current loop = that number + 1. If no delta plan exists: Loop 1.
2. In browser mode: read the `Loop:` field from the most recently uploaded `04_DELTA_PLAN.md`. If no delta plan was uploaded: Loop 1. If delta plan was uploaded but `Loop:` field is absent or illegible: output `LOOP AMBIGUITY — I read Loop [n] from [filename]. Confirm? (yes / state correct number)` and wait.
3. Never infer loop number from user instruction alone. User may miscount. Artifact is authoritative.

**On activation — check CF Status first:**
Read the `CF Status` line at the top of the implementation log. Output:
```
CF STATUS READ
── CRITICAL unverified: [n] → all = P0  |  HIGH CF GATE unverified: [n] → all = P0  |  LOW CF GATE unverified: [n] → P1
Total auto-promoted to P0: [n]
```
Any `CF GATE unverified` task is automatically P0 priority. Any `UNBOUND_CF` discovery must be absorbed before writing DELTA-TASKs.

---

## Process

Triage every non-COMPLETED task. Spot-check COMPLETED tasks for correctness.
Fix broken task specs. Produce an updated plan targeting only what remains.

**Do NOT re-analyze the full codebase** unless a DISCOVERY explicitly requires it.

**MANDATORY RULE APPLICATION (when writing DELTA-TASK Exact Change blocks):**
Before writing any code in a DELTA-TASK, you MUST apply:
1. `0_coding_rules.md` — SOLID, Security First, No Silent Failures, Anti-Duplication
2. `1_naming_conventions.md` — JS `csharp_` prefix, C# `_camelCase`/`PascalCase`, Python `snake_case`, `DateTime.Now` prohibition, audit log immutability
3. `2_webview2_standards.md` — WebView2 settings centralized in `BaseWebView2Form`, no `Task.WaitAll()`, asset encryption format locked, `HybridBffService` as single API gateway
4. `3_infrastructure_security.md` — Encrypted log format locked (`ENCRYPTED_V1:`), RSA-signed config, MongoDB indexes via `MongoDbIndexManager.cs`, Razorpay HMAC verification, Nginx `X-Custom-Client` enforcement
5. `4_workflow_standards.md` — Release build order, post-change Check A (caller integrity) + Check B (doc impact)

**Token Bloat Prevention (Mandatory):** When generating the revised `04_DELTA_PLAN.md`,
completely DROP and omit tasks marked COMPLETED from the new document unless explicitly
referenced by a failed task. Never carry completed tasks forward — it wastes tokens.

**Spot-Check Scope (Mandatory — not optional):**
Spot-checking is NOT random. Apply these rules to determine which COMPLETED tasks must be checked:
1. Any COMPLETED task (from CURRENT run or ANY PRIOR loop) that shares a file with a FAILED, PARTIAL, or FABRICATED task in the current run → mandatory spot-check. Read Reference Plan to find prior tasks mapped to this file.
2. Any COMPLETED task whose Verification Checklist included a CRITICAL CF GATE item → mandatory spot-check.
3. Tasks not meeting criteria 1 or 2 → spot-check is optional (check at least 1 per 10 COMPLETED).

Spot-check output per task:
```
Spot-Check: TASK-XXX → PASS (evidence: [file:line] — [key criterion confirmed intact])
Spot-Check: TASK-XXX → FLAG — [what is broken] → becomes DELTA-TASK-[n] type CF_REGRESSION / FLAG
```
"Spot-check: all PASS" with no per-task evidence is a protocol violation.

**Completed Task Permanence (Mandatory):**
Tasks marked `COMPLETED` in any prior IMPLEMENTER or DELTA run are **permanently closed**.
DELTA never re-opens, re-runs, or re-audits a COMPLETED task unless a Spot-Check reveals
it is actively broken (regression). In that case it becomes a new `DELTA-TASK` with type `FLAG`,
not a re-opened old task. This rule prevents completed work from regressing silently across loops.

**FABRICATED Verdict Override (Mandatory — applies when review report is present):**
If the `05_REVIEW_REPORT.md` records a `FABRICATED` verdict for a task, that task is treated as
**NOT COMPLETED** regardless of what the implementation log says. Create a `DELTA-TASK` with
type `REPLAN`, priority `P0`, and note: `"FABRICATED: PR_REVIEWER found no corresponding change
in git diff. Log claim is unverified. Treat as unimplemented."` The `Completed Task Permanence`
rule does NOT protect FABRICATED tasks — their log status is suspect.

**CF GATE regression exception:** If a COMPLETED task's CF GATE item was logged as verified
but Spot-Check reveals the fix is absent or wrong, create a `DELTA-TASK` with type `CF_REGRESSION`,
priority P0. Do not re-open the original task.

---

## CF-Specific Triage Rules (apply before general triage)

| Rule | Trigger | Required Action |
|------|---------|----------------|
| CF GATE unverified | Task PARTIAL: "CF GATE unverified: CF-XXX" | Always REPLAN P0. Rewrite CF fix steps in Exact Change. Add `⚠️ CF-XXX VERIFIED:` item with concrete criterion. Never RESCHEDULE. |
| UNBOUND_CF discovery | DISCOVERY type UNBOUND_CF in log | Find affected future tasks. Add CF fix as mandatory step in their DELTA-TASKs. Note in Delta Summary. |
| CF GATE on SKIPPED task | Task SKIPPED with CF Embedded | Carry forward: `CF Embedded: CF-XXX (CRITICAL — GATE) [carried from TASK-XXX]`. Never drop it. |
| FABRICATED verdict (review report) | PR_REVIEWER marked task FABRICATED | REPLAN P0. Task is unimplemented. Do not trust COMPLETED log status. |
| MISSING verdict (review report) | PR_REVIEWER found tasks absent from log | Add as new DELTA-TASK with type REPLAN. Priority: P0 if task has a CF GATE embedded, P1 otherwise. |
| CALLER_RISK verdict (review report) | PR_REVIEWER flagged unverifiable callers in browser mode | Add as DELTA-TASK type GREP_VERIFY. Agent mode: grep full repo for old signature. Browser mode: task MUST instruct "Run global search for [Signature] in your IDE and paste the results" — wait for paste before generating plan. |

---

## Triage Decisions

- **RESCHEDULE** — retry as-is (transient failure, env issue, dependency now resolved)
- **REPLAN** — fix the task spec (wrong location, underspecified, missing context, hallucinated reference)
- **ESCALATE** — needs human decision before proceeding
- **DROP** — no longer needed (covered by another task, requirement changed)

> A task with an unverified CF GATE is always REPLAN — never RESCHEDULE.

---

## Loop Termination Rules

- After loop 3: output the **Post-Loop-3 Human Review Block** (see below) — do not loop further
- If all remaining tasks are ESCALATED: surface escalations immediately, do not loop further
- If <3 LOW-complexity tasks remain with no CRITICAL CFs: note "this should be the final run"
- If any CRITICAL CF remains unverified after loop 3: include it as a blocking item in Post-Loop-3

## Post-Loop-3 Human Review Block (mandatory format after Loop 3 exhausted)

Output this block verbatim and wait for user response:

```
POST-LOOP-3 REVIEW
──────────────────
Completed: [n] tasks (permanently closed — not retried)
Unresolved: [n] tasks (listed below)
Unverified CRITICAL CFs: [n] (listed below — block shipping regardless of task status)
Root cause of remaining failures: [2–3 sentences]

Unresolved task summary:
| Task | Type | CF Gate? | Root Cause | Estimated Fix Complexity |
|------|------|----------|------------|--------------------------|
| TASK-XXX | [type] | YES — CF-XXX | [cause] | SMALL/MEDIUM/LARGE |

Escalations requiring human decision:
[List any ESCALATE items with their questions]

Choose one of the following options:

  (A) RESUME — Fix the root cause externally, then say "resume IMPLEMENTER"
      → IMPLEMENTER re-runs from the first unresolved task
      → No new planning needed. Use current 04_DELTA_PLAN.md.

  (B) REDUCE SCOPE — Remove specific failing tasks and continue
      → Say: "drop TASK-XXX, TASK-XXX — continue with remaining"
      → DELTA writes a final plan excluding dropped tasks. IMPLEMENTER runs.
      → If a dropped task has a CRITICAL CF GATE, state the CF is being deferred.

  (C) REPLAN — The approach is wrong; PLANNER must re-design these tasks
      → Say: "replan failing tasks" + describe what is wrong
      → PLANNER re-runs Phase 2 for the named tasks only (not full plan)
      → DISCOVERY not required unless the spec itself is wrong

  (D) ABANDON FEATURE — Archive the pipeline and stop
      → Say: "abandon"
      → Final state written to 04_DELTA_PLAN.md with status ABANDONED
      → COMPLETED tasks remain in codebase. No rollback.

  (E) ENVIRONMENT FIX — Failure is not a code issue (missing SDK, wrong config, etc.)
      → Say: "env fixed: [what you changed]"
      → DELTA re-triages all RESCHEDULE/FAILED tasks. May reduce to 0 unresolved.
      → No new planning. Same 04_DELTA_PLAN.md.

Waiting for your response.
```

---


---

## Output Format → Load `workflow_04_delta_ref.md`

> **The output format template for `04_DELTA_PLAN.md`** has been extracted to `workflow_04_delta_ref.md`
> to stay under the 12 000 character file limit.
> Load `workflow_04_delta_ref.md` before writing any DELTA output.
