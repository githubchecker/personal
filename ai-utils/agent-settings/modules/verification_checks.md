---
trigger: on_demand
description: "Shared module — per-task verification protocols used by IMPLEMENTER, referenced by PR_REVIEWER and DELTA. Load when any workflow references this file."
---

# Verification Checks — Shared Module

> **Who uses this:** IMPLEMENTER (defines and runs these checks), PR_REVIEWER (verifies they were run), DELTA (triages failures from them).
> **When to load:** When a workflow file says `> Load modules/verification_checks.md`.

---

## Step 6.5 — Self-Quality Gate (mandatory before logging COMPLETED)

Scan only YOUR introduced code. HIGH finding → task capped at `PARTIAL`. MEDIUM/LOW → `COMPLETED` but listed in `Side Effects Observed`.

| Issue | Sev | Check |
|-------|-----|-------|
| Unhandled exception (async/DB/HTTP) | HIGH | try/catch present? |
| Null dereference (`.Value`, `FirstOrDefault()`) | HIGH | null guard present? |
| Async misuse (`.Result`/`.Wait()`/`async void`) | HIGH | awaited correctly? |
| Contract violation (callers/implementors not updated) | HIGH | confirmed in Check A? |
| Hardcoded secret/env config | MED | use config/env instead |
| TODO/FIXME/HACK in new code | MED | remove before log |
| Missing audit trail (finance/payment) | MED | `_auditLog.Log(...)` present? |
| `DateTime.Now` (prohibited, use `UtcNow`) | LOW | replaced? |
| Debug output in production path | LOW | removed? |

---

## Step 6.6 — Agent Mode Per-Task Git Diff Verification

Skip entirely in browser mode — no terminal available.

Run for EVERY task before marking COMPLETED:
```
git diff HEAD -- [each file listed in this task's File I/O Permissions]
```

> ⚠️ Use `git diff HEAD` — NOT `git diff` alone.
> `git diff` only shows staged vs working tree. `git diff HEAD` shows working tree vs last commit,
> which covers unstaged changes, staged changes, and everything Gemini Flash applied
> regardless of whether you have run `git add` or committed.

Read the diff output and verify:
- The diff shows the exact transformation the SEARCH/REPLACE block described
- No extra lines were changed beyond what the task required
- The file listed in `File I/O Permissions` actually appears in the diff output

| Diff result | Action |
|-------------|--------|
| Diff shows correct transformation | Proceed to Check A |
| Diff shows nothing for a claimed file | Mark task `FAILED` — `"Step 6.6: git diff HEAD shows no change in [file]. Flash application did not succeed or targeted wrong file."` |
| Diff shows change but wrong location or content | Mark task `PARTIAL` — `"Step 6.6: change present in [file] but content differs from SEARCH/REPLACE spec. Actual: [quote diff]. Expected: [REPLACE block summary]."` |
| File is NEW (CREATE FILE task) | Run `git status -- [file]` instead. If file appears as untracked or new: PASS. If absent: FAILED. |
| File is DELETED (DELETE FILE task) | Run `git status -- [file]`. If absent or shows deleted: PASS. If still present: FAILED. |

Log format (mandatory — one line per file checked):
```
Step 6.6: git diff HEAD -- [file] → [change confirmed / NO CHANGE DETECTED / wrong content]
```
A COMPLETED task with no Step 6.6 log entry is a protocol violation in agent mode.

---

## Check A — Caller/Contract Integrity

`grep_search` full repo for the changed name. Report every file. Un-updated caller outside `File I/O Permissions` → downgrade task to `PARTIAL` + log `"Broken caller: [file:fn]"`. Interface changes → grep all implementors. Event changes → grep `+=`/`-=`. If 0 external callers → log `"Check A: 0 external callers confirmed."`

---

## Check B — Doc Impact

State explicitly whether each needs updating (update in same response if yes):
`DEPLOYMENT.md` · `TECHNICAL_ARCHITECTURE.md` · `[Feature]_spec.md` (flag only) · `PROJECT_SPECIFIC_RULES.md`
Use `📋 Post-Change Checks:` format from `4_workflow_standards.md`.

---

## Check C — Anti-Regression (Adversarial)

Before writing COMPLETED: name the single most likely thing accidentally broken that no Verification Checklist item tests. Cannot be N/A — must cite a specific behavior, class, or data flow. Verify intact (read code path). Log: `"Check C: verified [thing] unaffected — [evidence]."` If broken → FAILED.

### Check C — Evidence Standard

"Verified" or "looks correct" alone is a **protocol violation** — same line-citation rule as all other checklist items.

Required Check C log format:
```
Check C: verified [specific behavior/class/data flow] unaffected.
  Evidence: [file:line] — [exact code fragment or function call confirming the path is intact]
  Reasoning: [one sentence — why this code path is unaffected by the change made]
```

If the code path is broken → task status = FAILED, not COMPLETED. Check C cannot be marked passed with prose only.

---

## Check D — Callee Scope Check

For each function called BY the changed code: confirm valid inputs under new logic. Callees to focus on: those receiving params from changed variables, new control paths, previously unreachable callees. Log: `"Check D: callee inputs unchanged — [list]."` Invalid input → PARTIAL + `"Check D: [callee] receives [bad value]."`
