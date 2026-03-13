---
trigger: manual
description: "PLANNER Phase 2 Reference — Stage Failure Handling table and Path (c) Re-Entry map. Split from workflow_02_planner.md to stay under 12 000 chars. Load before writing Phase 2 output or handling blocked items."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# PLANNER — Phase 2 Reference

> **This file is Part B of PLANNER.** Load when handling failures, blocked items, or re-entry from DISCOVERY.
> Contains: Stage Failure Handling table · Path (c) Re-Entry map.

---

## Scope Creep Check — Required Output Format

The dry-run per-item `Scope Creep:` field MUST use this format — prose or "CLEAN" alone is a protocol violation:

```
Scope Creep:
  Checked: [list every adjacent concern examined — e.g., "caller list of renamed method", "shared config file", "migration script"]
  Status: CLEAN (none of the above fall outside declared File I/O Permissions)
  OR
  FLAGGED: [item] — [why it is outside scope] → [Add to File I/O Permissions / Split task / Escalate]
```

An agent writing `Scope Creep: CLEAN` with no list has not performed the check.

---

## External API Deps Field — Mandatory for Tasks Touching External Services

For any task that requires reading from or writing to an external API (Fyers, Razorpay, MongoDB Atlas, any third-party HTTP endpoint), PLANNER MUST add this field to the task spec:

```
External API Deps: [service name] — [doc URL or "NOT_PROVIDED"]
```

- If `NOT_PROVIDED`: IMPLEMENTER will SKIP the task with reason `"BLOCKED: External API docs required."`
- If doc URL is provided: IMPLEMENTER reads the URL content before implementing.
- If no external API is involved: `External API Deps: NONE`

This field must appear in the PLANNER task template between `CF Embedded:` and `Why:` fields.
Add it to the `02_IMPLEMENTATION_PLAN.md` task block format.

---

## Stage Failure Handling

| Situation | Action |
|-----------|--------|
| Spec gate is HOLD | Refuse to generate plan. Tell user to return to DISCOVERY. |
| Spec gate is REDO | Refuse to generate plan. Tell user spec needs to be rebuilt. |
| Unresolved CRITICAL CF with no §6 binding | Save PLANNER feedback dump (path c). Route to DISCOVERY targeted fix. |
| MISSING REQ-ID has no DEC-ID | Mark as BLOCK path (c). DISCOVERY must add DEC-ID. |
| CF bound to task but fix not in Exact Change | Add CF fix to Exact Change + ⚠️ CF-XXX VERIFIED item to checklist. |
| Dry-run finds Blocked items | Present 3 resolution options (a/b/c). Wait. Never decide unilaterally. |
| Dry-run finds UNVERIFIED file references | Do not create task. Mark as BLOCK. Ask user to verify file exists. |
| All items blocked | Say: "Spec cannot be tasked as written. Recommend full DISCOVERY re-run." |
| Plan written but spec changes later | Invalidate plan. Re-run PLANNER with updated spec. Do NOT patch tasks manually. |
| Code-level pre-read finds SEARCH won't match | Mark task as BLOCK. State exact mismatch. User must update spec or confirm correct location. |
| Caller impact check finds callers outside scope | Expand File I/O Permissions and add a new task, OR escalate to user to decide scope. |

---

## Path (c) Re-Entry: Returning to DISCOVERY

When PLANNER uses resolution path (c) — *"Return to discovery: spec section [X] needs updating"* —
DISCOVERY resumes as follows:

| What PLANNER says | DISCOVERY re-entry point | What is preserved |
|-------------------|--------------------------|-------------------|
| "Section §3 DEC-XXX is underspecified" | Phase 3 — expand that DEC-ID in-place | All other DEC-IDs, REQ-IDs, OQ answers |
| "Section §4 missing constant value for X" | Phase 4 — add constant to §4, re-run PLANNER-Ready for that item | All other items stay GO |
| "REQ-XXX has wrong capability status" | Phase 4 — re-run self-validation for that REQ-ID only | All other verdicts preserved |
| "MISSING REQ-XXX has no DEC-ID" | Phase 3 — create DEC-ID, then Phase 4B CF scan for it | All existing DEC-IDs preserved |
| "CF-XXX has no task binding in §6" | Phase 4B — add CF binding to §6 Phase Plan table | All other CFs and tasks preserved |
| "Feature scope conflict — A and B contradict" | Phase 2 — targeted Q&A on the contradiction only | All non-conflicting answers preserved |

After DISCOVERY resolves the flagged section:
1. Emit updated spec with `Plan Version: 1.0 → [incremented]` note
2. Emit `PLAN INVALIDATED — spec updated at [section]` per Phase 6 invalidation rule
3. PLANNER re-runs Phase 1 dry-run only for the changed items — unchanged items retain their verdicts

---

## Split-Mode Chunk Dependency Header (mandatory — add to every IMPL_P0n.md file)

Every phase chunk file MUST begin with this header block:
```
<!-- IMPL CHUNK HEADER -->
<!-- Phase      : P[n] of [total] -->
<!-- Phase Gate : All tasks in IMPL_P0[n-1].md must be COMPLETED before reading this file. -->
<!--              Exception: user may override by uploading this file with note "override gate". -->
<!-- Depends on : [IMPL_P0(n-1).md / NONE for P01] -->
<!-- Tasks      : [count] ([first task ID] through [last task ID]) -->
```
IMPLEMENTER must read the Phase Gate line and check the previous log before proceeding.

---

## LARGE-SCOPE Gate Protocol (triggered when callers impacted > 5)

When a dry-run item has > 5 callers impacted, PLANNER MUST output this block and halt:

```
LARGE-SCOPE GATE: [REQ-XXX] — [n] callers affected: [list]
Reply with one of:
  (a) Proceed — expand File I/O Permissions to include all listed callers
  (b) Split — create separate caller-update tasks
  (c) Reduce — limit rename scope to [subset]
```
PLANNER halts task writing for this item until user responds. Do not guess the user's preference.

---
