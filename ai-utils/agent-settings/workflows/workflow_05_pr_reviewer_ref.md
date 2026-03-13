---
trigger: manual
description: "PR_REVIEWER Output Reference -- 05_REVIEW_REPORT.md template and per-task format. Load before writing any PR_REVIEWER output. Split from workflow_05_pr_reviewer.md to stay under 12 000 chars."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Shared/reusable content → extract to `modules/` (preferred). Role-specific overflow → split into a `_ref.md` companion. Never exceed this limit.

# PR_REVIEWER -- Output Format Reference

> **This file is Part B of PR_REVIEWER.** Load it before writing any output.
> Contains: the full `05_REVIEW_REPORT.md` template, per-task review block format,
> CF violation format, doc debt table, and go/no-go block.

---

## Output Format: `05_REVIEW_REPORT.md`

```markdown
# 05_REVIEW_REPORT.md -- PR Code Review
Generated : [date] | Model: [self-identify]
Feature   : [Feature]
Diff range: [baseline]..[HEAD]  ([n] commits across [n] repos)
Plan      : [YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md]
Log       : [YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md]

## Review Summary
Tasks in plan    : [n]
Tasks in log     : [n]  ([n] COMPLETED, [n] PARTIAL, [n] SKIPPED, [n] FAILED)
Tasks missing    : [n]  (in plan, absent from log)
VERIFIED         : [n]
VERIFIED_OUT_OF_BAND: [n]  <- confirmed in live codebase, not in diff (diff window incomplete)
VERIFIED_WITH_WARNINGS: [n]
PARTIAL_VERIFIED : [n]
FABRICATED       : [n]  <- P0 (ground truth check performed on each one)
CF_VIOLATED      : [n]  <- P0 (blocks shipping)
WRONG_IMPL       : [n]
BROKEN_CALLER    : [n]  <- P0 (compile/runtime break)
MISSING          : [n]

CF Gate Summary  : [n] CRITICAL in plan | [n] confirmed in diff | [n] violated | [n] unverifiable
Overall Verdict  : CLEAN GO / GO with P0 tasks / HOLD

---

## Per-Task Review

---
### [TASK-ID] -- [Title]
**Log claimed  :** COMPLETED / PARTIAL / SKIPPED
**Review verdict:** VERIFIED / FABRICATED / CF_VIOLATED / PARTIAL_VERIFIED / etc.

**Diff evidence:**
- File `[path]` -- hunk at line ~[n]: [brief description of what the diff shows]
- [or] No hunk found for claimed files -- FABRICATED
- [or] Change found in LIVE CODEBASE but not in diff — VERIFIED_OUT_OF_BAND
  Applied session: [Loop N / commit hash if known / "prior session — untrackable"]
  Note: diff window was bounded to [baseline]..[HEAD] — change was applied outside this range.

**CF Gate check:** [if task has CF]
- CF-XXX ([CRITICAL/HIGH]): [quote the exact diff lines that satisfy or violate the constraint]
  -> SATISFIED / VIOLATED

**Quality issues found:** [or NONE]
- [HIGH] [file:fn] -- [issue description]

**Broken callers:** [or NONE]
- `[OldName]` referenced in `[file]` -- not updated in diff

**Caller risk (browser mode — unverifiable):** [or NONE]
- `[OldName]` may have callers in files outside the diff — unverifiable in browser mode. DELTA must grep full repo for `[OldName]` before closing.

**Verdict notes:** [1-2 sentences explaining the verdict]

---
```

---

## CF Violation Block Format

Use this format whenever `CF_VIOLATED` is found. Place it in the per-task block AND
in the consolidated CF Violations section at the end of the report.

```markdown
### CF-VIOLATION: CF-XXX ([CRITICAL/HIGH]) -- [CF short name]
**Task          :** [TASK-ID]
**Constraint    :** [exact constraint from plan CF Register -- quote verbatim]
**What diff shows:** [quote the actual lines from the diff]
**Why violated  :** [1 sentence -- what specifically is wrong]
**Fix required  :** [1 sentence -- what DELTA must do]
**DELTA priority:** P0 -- HOLD (CRITICAL) / P0 -- GO (HIGH)
```

---

## FABRICATED Task Block Format

```markdown
### FABRICATED: [TASK-ID] -- [Title]
**Log claimed  :** COMPLETED
**Files claimed:** [list from log]
**Diff search  :** No hunk touching any claimed file in range [baseline]..[HEAD]
**Ground truth check (MANDATORY):** `grep_search`/`view_file` performed on `[file path]` — change confirmed ABSENT from live codebase at [timestamp].
**CF Gates     :** [list any CF gates this task carried -- these are now unverified]
**DELTA action :** REPLAN as P0 DELTA-TASK. CF gates carried forward as GATE items.
```

---

## Missing Tasks Section

```markdown
## Missing Tasks (In Plan, Not In Log)

| Task | Title | CF Gate? | Complexity | DELTA Priority |
|------|-------|----------|------------|----------------|
| P6-T4 | Desktop TOS version field | NO | SMALL | P1 |
| P-OC-1-T2 | fyers_connector.py index quote | CF-009 CRITICAL, CF-013 CRITICAL | LARGE | P0 -- HOLD |
```

---

## Doc Debt Table

Always include this section even when all items are clean.

**Evidence rule:** For every row, write one sentence showing the evaluation was performed — not just a verdict. Acceptable: `"DEPLOYMENT.md — no update: reviewed diff for new env vars, ports, startup scripts — none present."` Not acceptable: `"DEPLOYMENT.md — NO UPDATE NEEDED"` with no evidence sentence. A table with verdicts but no evidence is not verifiable.

```markdown
## Documentation Debt

| Document | Status | Reason |
|----------|--------|--------|
| DEPLOYMENT.md | NEEDS UPDATE | [task X added env var Y -- document it] |
| TECHNICAL_ARCHITECTURE.md | NEEDS UPDATE | [new PointsService component -- add to arch diagram] |
| TECHNICAL_ARCHITECTURE.md | NO UPDATE NEEDED | -- |
| [Feature]_spec.md | SPEC GAP FLAGGED | [implementation revealed X was unspecified -- DELTA should escalate] |
| Project rule files | NO UPDATE NEEDED | -- |
```

---

## Phase 3 — Call Chain Integrity (mandatory — always present)

Every task that changed a method signature, renamed a method, or changed a parameter must appear here. N/A is a valid entry when no signature changed, but the table must still be output.

```markdown
## Phase 3 — Call Chain Integrity

| Task | Changed Signature | Callers found (grep) | All Updated? |
|------|-------------------|---------------------|--------------|
| TASK-XXX | OldMethod() → NewMethod(param) | File.cs:L89 | YES / NO |
| TASK-XXX | No signature change | N/A | N/A |
```
*If all tasks had no signature changes: table still required — use N/A rows.*

---

## Phase 6 — Missing Task Cross-Check (mandatory — always present)

```markdown
## Phase 6 — Missing Task Cross-Check

Plan task count  : [n]
Log task count   : [n]
Tasks in plan but absent from log: [list task IDs, or NONE]
```
*NONE is a valid and required entry. Omitting this section is a protocol violation.*

---

## Production Quality Issues Section

Group all quality findings here (also referenced per-task above).

```markdown
## Production Quality Issues

| Severity | File | Function | Issue | Task |
|----------|------|----------|-------|------|
| HIGH | PaymentController.cs | ProcessWebhook | Missing null check on order before .Status access | P7-T2 |
| MEDIUM | PointsService.cs | FreezeForOrderAsync | TODO comment left in: "// TODO: confirm units" | P5-T1 |
| LOW | DbInitializer.cs | StartAsync | DateTime.Now used -- must be DateTime.UtcNow (project rule) | P0-T1 |
```

---

## Go / No-Go Block (mandatory -- end of every report)

```markdown
## Go / No-Go for DELTA

**Verdict: [CLEAN GO / GO with P0 tasks / HOLD]**

### HOLD items (must resolve before DELTA runs):
| Item | Type | Task | Why blocking |
|------|------|------|-------------|
| CF-013 violated in fyers_connector.py | CF_VIOLATED | P-OC-1-T2 | NameError at runtime if unresolved |
| P-OC-1-T2 fabricated | FABRICATED + CF GATE | P-OC-1-T2 | CRITICAL CFs CF-009 + CF-013 unverified |

### P0 DELTA tasks (GO but these are mandatory first):
| Item | Type | Task | DELTA action |
|------|------|------|-------------|
| P6-T4 missing | MISSING | P6-T4 | Add as DELTA-TASK, SMALL, no CF |
| P12-T1 partial | PARTIAL_VERIFIED | P12-T1 | DELTA-TASK for binary TIDV frame format |

### Recommended DELTA prompt additions:
[Any corrections DELTA should be told explicitly, based on this review]
```

---

## Stage Failure Handling

| Situation | Action |
|-----------|--------|
| Diff file missing in agent mode | Run `tools\make_pr_diff.bat -Feature [Feature]` first. Do NOT proceed without it. |
| Diff file missing in browser mode | Tell user to run `tools\make_pr_diff.bat -Feature [Feature]` and re-upload. |
| Diff too large for context window | Process stat file first. Ask user which repos/phases to prioritise. |
| Log references files not in diff | **First:** run ground truth check — `view_file`/`grep_search` on the live codebase for the claimed change. If found: verdict = `VERIFIED_OUT_OF_BAND`, note diff range was incomplete. If NOT found: verdict = `FABRICATED`. Never issue FABRICATED without ground truth check in agent mode. |
| CF constraint ambiguous from diff alone | Mark as `UNVERIFIABLE` in browser mode. In agent mode: grep codebase for the constraint. |
| All tasks VERIFIED | Still run Phase 5 (doc debt) and Phase 6 (missing tasks). Output CLEAN GO. |

---

## Rule Re-Anchor (Every 10 Tasks Reviewed)

> Full block: `modules/output_blocks.md` §"Rule Re-Anchor Block".
> **Trigger:** After reviewing tasks 10, 20, 30… output the RULE RE-ANCHOR block before continuing.
> **Gate:** CF unverified > 0 at checkpoint → stop. Do not continue until surfaced.
> **Key PR signal:** FABRICATED verdicts accumulating or ground truth checks being skipped → surface at re-anchor, do not defer to report summary.

