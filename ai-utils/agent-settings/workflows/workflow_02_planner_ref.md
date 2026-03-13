---
trigger: manual
description: "PLANNER Reference — task format, complexity tags, phase output formats, feedback file format. Read before writing 02_IMPLEMENTATION_PLAN.md."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Split into companion if content must grow.

# PLANNER Reference — Output Format

> **When to read:** Phase 1 → Phase Output Formats; Phase 2 → before writing tasks. Do NOT load on activation.

---

## Complexity / Model Tags

| Tag | Lines Changed | Model |
|-----|---------------|-------|
| SMALL | <200 | ANY (Flash/Haiku fine) |
| MEDIUM | 200–500 | ANY |
| LARGE | >500 | PREFER_CAPABLE |
| PREFER_CAPABLE | any | Use Sonnet/Opus — security, arch changes, complex logic, any task with a CRITICAL CF |
| REF (optional) | any | Refactoring task — P3, user opt-in only. Never blocks delivery. |

> CRITICAL CF fix → automatically PREFER_CAPABLE regardless of line count.

---

## Phase Output Formats

### Resumption Contract — PLANNER DRY-RUN
```
RESUMPTION CONTRACT — PLANNER DRY-RUN
──────────────────────────────────────
Interrupted at: [REQ-XXX as stated in your message]
Items confirmed dry-run complete: REQ-001 through REQ-[previous]
Resuming dry-run from: REQ-XXX
Cached results will NOT be re-run.
──────────────────────────────────────
Does this match your records? (yes / no)
```

### Inventory Declaration
```
PLANNER INVENTORY DECLARATION
──────────────────────────────
Source: [Feature]_spec.md
Spec Gate: GO (confirmed — proceeding)
Total REQ-IDs: [n]
Total BUG-IDs: [n] (existing=[n] new-design=[n])
Total DEC-IDs: [n]
Total CF-IDs:  [n] (CRITICAL=[n] HIGH=[n] LOW=[n])
Batch size: 8 | Total batches: [ceil((REQ+BUG)/8)]
CF Bindings in §5: [n] — all CRITICAL CFs bound: YES / NO (if NO → BLOCK before proceeding)
Starting implementability dry-run: Batch 1 of [n]
```

### Per-Item Dry-Run Verdict
```
### REQ-XXX / BUG-XXX: [name]
Spec says: [one-line summary]
File/Function verified? YES ([file:fn]) / NO (new — DEC-ID confirms) / UNVERIFIED
Implementable without a design decision? YES / NO
  [Design decision = any WHAT or HOW not stated in spec. WHERE/WHEN/ORDER are not design decisions.]
DEC-ID present? (MISSING items only): YES — DEC-XXX / NO → BLOCK
CF bound to this item? [CF-IDs from §5, or NONE]
Callers impacted (rename/sig change): [n] — [list] / N/A
  [⚠️ If n > 5: LARGE-SCOPE — mandatory user gate. See `workflow_02_planner_phase2_ref.md` for gate protocol.]
Completeness: FULL / PARTIAL / UNDERSPECIFIED
Action: Proceed / Expand spec detail now / Ask user / BLOCK
--- Adversarial Gates (all three required) ---
Scope Creep: [≥1 thing implementer naturally touches outside File I/O. "CLEAN" = list what checked + confirmed absent → add to Watch Out For if non-empty]
SEARCH Unique: YES ([file:line], ≥3 context lines) / NO → fix
Dep Partial: YES (independent) / NO — [exact shared state/artifact → tighten dep]
```

### DRY-RUN COMPLETE
```
DRY-RUN COMPLETE
─────────────────
Total items: [n]
Proceed as-is: [n]
Expanded inline: [n]
Blocked — path (a) or (b): [n]  ← resolvable without DISCOVERY
Blocked — path (c) required: [n]  ← requires spec update
CRITICAL CFs with task binding confirmed: [n] / [n total]
CRITICAL CFs missing task binding: [n]  ← BLOCK if > 0
```

---

## Feedback File Format

When path (c) is triggered, PLANNER saves the feedback to `continuation\` with this content format:

*Agent mode:* Write this content to a temp file, then: `python pipeline.py dump --feature [Feature] --role PLANNER --file [temp_path]`
*Browser mode:* Output this content in chat, clearly labelled. User saves to `Docs/[Project]/continuation/`.

```markdown
# PLANNER Feedback — Targeted DISCOVERY Fix Required
Generated: [date] | Plan Version: [n] | Blocked items: [n]
Spec: [Feature]_spec.md

## Cached Dry-Run Results (do NOT re-validate these)
| Item | Verdict | Notes |
|------|---------|-------|
| REQ-001 | PASS | [file:fn confirmed] |
| BUG-003 | PASS | [confirmed] |
... [all PASS items listed here]

## Items Requiring DISCOVERY Fix
### BLOCK-001: [REQ-XXX / BUG-XXX]
Spec section to fix: §[n] [DEC-XX / §4 / §5 / §6]
Missing: [exact list — field names? constants? signature? algorithm? DEC-ID absent? CF not bound?]
Why PLANNER cannot resolve with path (a) or (b): [reason]
Minimum DISCOVERY must provide: [specific, concrete list of what is needed]

### BLOCK-002: [REQ-XXX]
...
```

---

## Output Format: `02_IMPLEMENTATION_PLAN.md`

```markdown
# Implementation Plan
Generated: [date] | Model: [self-identify]
Spec: [Feature]_spec.md | Spec Gate: GO | Plan Version: 1.0 | Total Tasks: [n]
CF Coverage: [n] CFs embedded across [n] tasks (CRITICAL=[n] HIGH=[n] LOW=[n])
Split Mode: SINGLE FILE / SPLIT — [n] phase files (IMPL_P01.md … IMPL_P0[n].md)

## Pre-Implementation Checklist
- [ ] [Environment/dependency/config that must be true before first task]
- [ ] [Open Questions resolved: OQ-001 answered as: ...]
- [ ] All CRITICAL CF fixes confirmed embedded in their bound tasks (see CF Coverage above)

## Global Constraints
[Rules that apply to ALL tasks:
- Naming conventions to follow
- Patterns to preserve
- Files/classes that must NEVER be touched regardless of task scope
- Cross-cutting concerns: logging pattern, error handling style, null handling convention]

---
### TASK-001
**Title:** [Short descriptive name]
**Type:** BUG_FIX / FEATURE / REFACTOR / CONFIG / TEST / REF
  [REF = optional refactoring from §2 Recommended Refactoring table. Always P3. Only present if user opted in.]
**Priority:** P0 (blocker) / P1 / P2 / P3
**Complexity:** SMALL / MEDIUM / LARGE
**Model:** ANY / PREFER_CAPABLE
**Refs:** REQ-001, BUG-003
**Depends On:** None / TASK-XXX
**CF Embedded:** CF-XXX (CRITICAL — GATE) / NONE
  [GATE = task cannot be COMPLETED without CF checklist item explicitly verified.
   ACCOMPANIES = CF fix must be in the initial implementation, not retrofitted.]

**External API Deps:** NONE / [Service: DocName — PROVIDED / NOT_PROVIDED]
  [List every 3rd-party API this task writes against. IMPLEMENTER skips the task if any dep is NOT_PROVIDED.
   e.g. "Fyers: OptionChain v3 API — NOT_PROVIDED (user must paste doc/URL before IMPLEMENTER runs)"
        "Razorpay: Webhook v1 — PROVIDED (spec §6.2 has full payload schema)"]

**Why:** [1–2 sentences: what problem this solves]

**Location:**
- File: `src/module/file.ext`
- Function: `methodName()` ~line 45
- Also touches: `src/other/file.ext` → `otherMethod()`

**File I/O Permissions:**
- Files to modify: [exhaustive — Implementer may ONLY touch these]
- Files to create: [path + purpose, or NONE]
- Files to delete: [or NONE]
- ⚠️ If a file not listed here must be changed, Implementer logs PARTIAL and notes it in Discoveries.

**Exact Change — MANDATORY: SEARCH/REPLACE blocks (not prose):**

Change [N] of [total] | File: `[path]` | Function: `[ClassName.MethodName]()`
Context (1 line): [why this block changes]

FILE: [path]
<<<SEARCH
[verbatim existing code — copied from live file read in code-level pre-read.
 Minimum 3 lines for context. Must be unique within the file.]
<<<END>>>
<<<REPLACE
[verbatim new code with all changes applied]
<<<END>>>

[If this task has a CF GATE binding — add clearly labelled block:]
⚠️ CF-XXX FIX (CRITICAL — GATE): [CF short name]
FILE: [path]
<<<SEARCH
[exact context]
<<<END>>>
<<<REPLACE
[code with CF fix applied — unambiguous]
<<<END>>>

For new files:
FILE: [path]
<<<CREATE FILE: [path]>>>
[complete file content — with CF fix embedded if CF is bound to this task]
<<<END>>>

For deletions:
<<<DELETE FILE: [path]>>>

**Verification Checklist:**
- [ ] [Specific, testable criterion — not "it works"]
- [ ] [Edge case that must be handled]
- [ ] [Integration point that must still function — what to check]
- [ ] [Anti-regression: confirm nothing outside scope changed]
- [ ] ⚠️ CF-XXX VERIFIED: [exact testable criterion for the CF fix]
  [Only present when CF Embedded is not NONE. This item blocks COMPLETED status.]

**Watch Out For:**
[Side effects, gotchas, things that look related but must NOT be changed]

---
### TASK-002
[repeat structure]

---
## Deferred Items
| Item | Reason | REQ-ID | Suggested Future Action |
|------|--------|--------|------------------------|

## Task Dependency Order
TASK-001 → TASK-002 → TASK-004
                    ↘ TASK-003 (parallel with TASK-002, after TASK-001)
[Annotate tasks with CRITICAL CF GATEs:]
TASK-003 ⚠️CF-001  ← cannot be COMPLETED without CF-001 verified
```

---

## Output Splitting — Large Spec Escape Hatch

> **Default:** Single `02_IMPLEMENTATION_PLAN.md`. Always exists — IMPLEMENTER and DELTA depend on it by name.
> Split is decided **once, upfront, before writing any task**. Never mid-output.

### Upfront decision — evaluate immediately after dry-run, before writing Phase 2

Count: **T** = total tasks from dry-run. **L** = tasks tagged LARGE or PREFER_CAPABLE.

| Condition | Decision |
|-----------|----------|
| T ≤ 30 AND L ≤ 8 | Single file — write all tasks inline as normal |
| T > 30 OR L > 8 | Split — write primary file as index + one phase file per phase |

Announce the decision in chat before writing anything:
`"SPLIT MODE: [n] tasks, [n] LARGE/PREFER_CAPABLE — writing 02_IMPLEMENTATION_PLAN.md as index + IMPL_P01.md…IMPL_P0[n].md phase files."`
or
`"SINGLE FILE: [n] tasks, [n] LARGE/PREFER_CAPABLE — writing 02_IMPLEMENTATION_PLAN.md inline."`

### Phase file canonical naming

Phase files: `IMPL_P01.md`, `IMPL_P02.md`, … `IMPL_P0[n].md` — 1-indexed, zero-padded to 2 digits, no variants.

### Split format

`02_IMPLEMENTATION_PLAN.md` retains its full header, Pre-Implementation Checklist, Global Constraints, and Task Dependency Order. Each phase's tasks are replaced with a **phase stub** in standard `### TASK-XXX` format — the Implementer reads it identically to a normal task:

```
---
### TASK-P01 — [Phase Name]
**Priority:** P0 | **Gate:** [condition] | **Depends On:** [or None]
**CF Embedded:** [CF-IDs or NONE]
**Why:** [one-line summary]

**Exact Change:**
⚠️ SPLIT PLAN — full tasks for this phase are in a separate file.
Upload `IMPL_P01.md` (same folder as this plan) and complete all tasks
in it before proceeding to TASK-P02.

**Verification Checklist:**
- [ ] All tasks in `IMPL_P01.md` marked COMPLETED
- [ ] Gate condition met before proceeding to TASK-P02
---
### TASK-P02 — [Phase Name]
...
⚠️ SPLIT PLAN — Upload `IMPL_P02.md` and complete all tasks before proceeding to TASK-P03.
...
```

Phase files contain full tasks only, with a 4-line back-reference header:
```
# IMPL_P01 — [Phase Name]
Primary plan: 02_IMPLEMENTATION_PLAN.md | Spec: [Feature]_spec.md
Gate: [condition] | Depends on: [phase IDs or None]
Active CFs: [CF-IDs and one-line summaries for this phase only]
---
[full tasks in standard TASK-XXX format]
```

### Pre-Implementation Checklist — split mode additions

When in SPLIT MODE, add these items to the Pre-Implementation Checklist in `02_IMPLEMENTATION_PLAN.md`:

```
## Pre-Implementation Checklist
...
[SPLIT MODE — add one line per phase file:]
- [ ] IMPL_P01.md — all tasks COMPLETED
- [ ] IMPL_P02.md — all tasks COMPLETED
...
```

A phase is **complete** when every task in its phase file carries status `COMPLETED` in the implementation log. PARTIAL, SKIPPED, or FAILED tasks in a phase file mean the phase is not complete — do not proceed to the next phase stub.

### Resumption when split

Completed phase files are intact — do NOT regenerate. State which phases are complete and resume from the first incomplete task in the current phase file.

---
