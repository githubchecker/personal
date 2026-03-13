---
trigger: manual
description: "IMPLEMENTER Reference — Code Change Output Format, 03_IMPLEMENTATION_LOG.md template, Stage Failure Handling. Split from workflow_03_implementer.md to stay under 12 000 chars. Load before writing any output."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# IMPLEMENTER — Output Format Reference

> **This file is Part B of IMPLEMENTER.** Load it before writing any output.
> Contains: Code Change Output Format · `03_IMPLEMENTATION_LOG.md` template · Stage Failure Handling.

---

## Code Change Output Format

> **Note:** When PLANNER has provided verbatim SEARCH/REPLACE blocks in the task, IMPLEMENTER applies them directly.
> IMPLEMENTER does NOT rewrite or reinterpret PLANNER's blocks.
> IMPLEMENTER constructs its OWN blocks ONLY for:
> - Corrections discovered during step 3.5 (file state different from PLANNER's block)
> - DELTA-TASKs (which DELTA writes — see `workflow_04_delta.md`)
> - Tasks where PLANNER was unable to write a block (marked `PLANNER-BLOCK: provide-block` in the task)

All code changes MUST be expressed as explicit tagged blocks.
Every block opens with a tag and closes with `<<<END>>>`. No exceptions.

```
FILE: src/module/file.ext
<<<SEARCH
[exact existing code, line-for-line match — no paraphrasing, no summarising]
<<<END>>>
<<<REPLACE
[new code replacing it exactly]
<<<END>>>
```

```
FILE: src/module/file.ext
<<<INSERT AFTER: [exact anchor line from file]
[new code to insert]
<<<END>>>
```

```
<<<DELETE FILE: src/module/file.ext>>>
```

```
<<<CREATE FILE: src/module/newfile.ext>>>
[complete file content here]
<<<END>>>
```

**Block rules:**
- SEARCH block must match the file exactly
- **Whitespace Exception (strictly scoped):** Applies ONLY to: (a) trailing whitespace on a line, (b) Windows `\r\n` vs Unix `\n` line endings, (c) a single blank line added or removed. Tab-vs-space indentation changes, brace position changes, or any character difference beyond the above three cases are NOT whitespace — log PARTIAL with `"SEARCH mismatch: [describe exact character difference]"` and flag for DELTA REPLAN. Do NOT attempt a "close enough" replacement for non-whitespace differences.
- Every open block tag must have a corresponding `<<<END>>>` — never leave a block open
- DELETE FILE has no body and no `<<<END>>>` — the tag is self-closing
- Multiple blocks in one task must each be complete and closed before starting the next

---

## Output Format: `03_IMPLEMENTATION_LOG.md`

> **Enforcement:** The checklist section for each task MUST be written before moving to the next task.
> Every checklist item MUST include `[file:line]` evidence. "Verified" alone is a protocol violation.

> Violation examples: see `modules/violation_examples.md` §"Checklist Line-Citation"

```markdown
# Implementation Log
Generated: [date] | Model: [self-identify] | Run: [n]
Plan: [YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md or YYYYMMDD_HHMM_04_DELTA_PLAN.md — which was used]
Total: [n] | Completed: [n] | Partial: [n] | Skipped: [n] | Failed: [n]
CF Status: CRITICAL=[n] in plan | Verified=[n] | Unverified=[n] (DELTA P0)

---
### TASK-001 — [Title]
**Status:** COMPLETED / PARTIAL / SKIPPED / FAILED
**CF Embedded:** CF-XXX (CRITICAL — GATE) / NONE

**Changes Made:** *(omit blocks if SKIPPED — go straight to Skip/Fail Reason)*
FILE: src/module/file.ext
<<<SEARCH
[exact original code]
<<<END>>>
<<<REPLACE
[new code]
<<<END>>>

**Checklist Results:** *(every item must include [file:line] evidence — omitting is a protocol violation)*
- [x] Criterion 1 — `[file.ext:line]` — [exact line or quote that proves compliance]
- [ ] Criterion 2 — FAILED: [exact reason — what is wrong or missing]
- [x] ⚠️ CF-XXX VERIFIED: `[file.ext:line]` — "[exact code fragment]" satisfies constraint because [reason]
  OR
- [ ] ⚠️ CF-XXX GATE UNVERIFIED: [exact reason — forces task status to PARTIAL]

**Quality Gate Results (Step 6.5):** *(scan changed code only — pre-existing code is out of scope)*
- HIGH: [issue found, or NONE]
- MEDIUM: [issue found, or NONE]
- LOW: [issue found, or NONE]
*(Any HIGH finding caps task status at PARTIAL. MEDIUM/LOW: COMPLETED allowed, must list here.)*

**Skip/Fail Reason:** [required if SKIPPED or FAILED]
  Common skip reasons:
  - `"Cascade: TASK-XXX [FAILED/SKIPPED]"`
  - `"BLOCKED: External API docs required — Fyers OptionChain v3. User must paste doc content or URL before this task can run."`
  - `"SEARCH mismatch at [file:fn] — [description]"`
**Side Effects Observed:** [anything introduced but not in checklist, or NONE]

📋 Post-Change Checks:
- Check A (Caller/Contract Integrity): grep `'[changed name]'` across full repo → [list all references found with file:line, or "0 external callers confirmed"]
  - Interface implementors checked: [YES — [list] / N/A]
  - Event subscription sites checked: [YES — [+=/-= list] / N/A]
- Check B (Doc Impact): DEPLOYMENT.md=[yes — [reason] / no]. TECHNICAL_ARCHITECTURE.md=[yes — [reason] / no]. [Feature]_spec.md=[gap flagged: [desc] / no]. PROJECT_SPECIFIC_RULES.md=[yes — [reason] / no].
- Check D (Callee Scope): For each function called by changed code — confirm inputs are valid under new logic.
  Required format: `Check D: [callee name] at [file:line] — receives [param] from [changed variable] — value range [valid/invalid under new logic].`
  If invalid input detected: task status = PARTIAL + `"Check D: [callee] receives [bad value] from [source] — caller must guard."`
  "Check D: callee inputs unchanged" is only acceptable when the changed code introduces NO new call sites and NO new parameter values to existing callees.

---
## Discoveries (Found During Implementation)
### DISCOVERY-001
- **Found during:** TASK-XXX
- **Type:** BUG / MISSING_DEPENDENCY / AMBIGUITY / ARCH_CONFLICT / UNBOUND_CF
  [Use UNBOUND_CF when you find an implementation trap during implementation that was not
   in the spec's CF Register — flag it so DELTA can add the fix to affected future tasks.]
- **Description:** [exactly what was found]
- **Impact:** [what it affects — be specific]
- **Recommendation:** Fix in DELTA / Escalate to user / Ignore (with reasoning)

---
## Summary Table
| Task | Title | Status | Notes |
|------|-------|--------|-------|

## Delta Needed For
[Plain list — one line per item]
1. TASK-XXX skipped because...
2. TASK-XXX — CF GATE unverified: CF-XXX — [reason] — DELTA must treat as P0
3. DISCOVERY-001 needs architectural decision from user...

## FLOW_REGISTRY Update Required
After writing this log, check `FLOW_REGISTRY.md` for any flow whose `Source Files` column overlaps with files modified in this run.

Output:
```
FLOW_REGISTRY UPDATE:
  FLOW-[NNN] ([Flow Name]) — source file [filename] was modified in TASK-[XXX] → mark [CHANGED]
  FLOW-[NNN] ([Flow Name]) — source file [filename] was modified in TASK-[XXX] → mark [CHANGED]
  [or] FLOW_REGISTRY: no flows affected — no source files overlap with this run's changes.
```

This output is the trigger for FLOW_AUDITOR to re-audit those flows on its next run.
The user must manually update FLOW_REGISTRY.md based on this output (or local agent applies it directly).
```

---

## Check C — Anti-Regression Evidence Standard

> Full protocol + evidence format: see `modules/verification_checks.md` §"Check C".
> Summary: name the most likely breakage, cite `[file:line]` evidence it's intact. Prose-only = protocol violation.

---

## Rule Re-Anchor Block (Agent Mode — Every 10 Tasks)

> Full template: see `modules/output_blocks.md` §"Rule Re-Anchor Block".
> Summary: after tasks 10, 20, 30… output the re-anchor block. CF unverified >0 = stop and surface.

---

## Stage Failure Handling

| Situation | Action |
|-----------|--------|
| Cannot find file listed in task | Log SKIPPED: "File not found: [path]". Note in Discoveries as MISSING_DEPENDENCY. |
| Codebase state doesn't match SEARCH block | Log PARTIAL: "SEARCH mismatch at [file:fn]". Describe diff. Do NOT guess a replacement. |
| Token limit mid-task | Complete current task if within ~200 tokens. Log rest as SKIPPED "Token limit at TASK-XXX". |
| Task spec is ambiguous | Log SKIPPED: "Ambiguous: [specific question]". Note in Discoveries as AMBIGUITY. |
| Cascade dependency failed | Log SKIPPED immediately: "Cascade: TASK-XXX [FAILED/SKIPPED]". Do not attempt. |
| CF GATE item cannot be verified | Log PARTIAL: "CF GATE unverified: CF-XXX — [reason]". DELTA treats as P0. |
| Implementation trap found not in CF Register | Log as DISCOVERY type UNBOUND_CF. DELTA adds fix to affected future tasks. |
| All tasks SKIPPED or FAILED | Write log with all statuses. Activate DELTA. Do not retry independently. |

---

## Step 6.6 — Agent Mode Per-Task Git Diff Verification

> Full protocol: see `modules/verification_checks.md` §"Step 6.6".
> Summary: run `git diff HEAD -- [file]` for every File I/O Permission entry.
> No change detected = FAILED. Skip in browser mode.

---
