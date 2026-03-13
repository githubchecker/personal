---
trigger: manual
description: "DISCOVERY CF Reference — CF trap categories, per-finding format, Dashboard format. Load at Phase 4B only."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# DISCOVERY CF Reference — Critical Findings & Dashboard

> **When to read this file:** Load at Phase 4B only. Do NOT load on activation.
> Also used at Phase 4C for the Dashboard format.

---

## Phase 4B — CF Trap Category Checklist

**Before scanning — apply Rule A (Inventory Declaration):**
```
CF SCAN INVENTORY
─────────────────
Categories to check: 10 (all mandatory — Rule E: every category needs explicit verdict even if CLEAR)
MISSING and PARTIAL items in spec to scan: [n]
```

**Per-category verdict — Rule C (no silent skips):**
After checking each category, output either the CF-XXX block below (if finding found) or:
`Category [n] — [name]: CLEAR — no instances found in proposed designs.`
Silence is not a verdict. A category with no findings must still be explicitly marked CLEAR.

Scan the entire spec for each category below. Check every MISSING item's proposed design.

| # | Trap Category | What to look for |
|---|---------------|-----------------|
| 1 | **Unbounded collections** | Any proposed Queue, List, Dictionary that enqueues every tick — does it have explicit dequeue-on-overflow? |
| 2 | **Undefined computation method** | Any computation named but not specified — "compute Q90 EWM": which algorithm exactly? |
| 3 | **Dual-implementation risk** | Two places in the spec claiming to compute the same value — which is authoritative? |
| 4 | **Underspecified dependent service** | A downstream service that cannot be coded without info the spec doesn't provide (tensor names, output shapes, enum ordering) |
| 5 | **Uninitialized state on first tick** | Proposed state fields with no stated initial value — what does the class return on tick 0? |
| 6 | **Large-scope rename** | A rename or signature change where callers across the codebase are not explicitly counted |
| 7 | **Sign / direction ambiguity** | A formula or comparison where + vs − direction is not explicitly stated and wrong sign corrupts output |
| 8 | **Thread-safety assumption** | Proposed shared state accessed from multiple threads without stated synchronisation |
| 9 | **Integer overflow in financials** | Any integer accumulation of ticks, prices, or quantities without overflow bounds check — financial values can exceed int32 range |
| 10 | **Non-atomic operations assumed atomic** | Any read-modify-write on shared state (e.g., `counter++`, dictionary add-or-update) performed without a lock or atomic primitive |

---

## Per-Finding Output Format

For each trap found, output:

```
### CF-XXX: [short name]
Severity: 🔴 CRITICAL (breaks at runtime, silent data corruption, data loss) /
          🟡 HIGH (wasted implementation effort, wrong output) /
          🟢 LOW (cosmetic, easily caught in testing)
Phase: P[n] — [which task creates the affected code]
Finding: [what will fail and exactly why — be specific]
Fix: [exact fix — pseudocode acceptable, must be unambiguous]
Binds to §6 Phase Plan: YES — add to CF Bindings table in §6 "Critical Findings Bound to Phases"
```

---

## After Scanning All Categories

```
CF REGISTER COMPLETE
Total CF found: [n] (CRITICAL=[n] HIGH=[n] LOW=[n])
```
Or if none found:
```
CF REGISTER: CLEAR — no implementation traps found.
```

**Gate:** Any CRITICAL CF must be fixed in the spec or escalated as OQ before Phase 4C.

---

## Phase 4C — Project Decision Dashboard Format

Output this block in full, then copy it verbatim into §11 of the spec:

```
PROJECT DECISION DASHBOARD
───────────────────────────────────────────────────────
Total REQ-IDs analysed:          [n]
  EXISTS (no work needed):       [n]
  PARTIAL (modification needed): [n]
  MISSING (new build):           [n]
Total BUG-IDs:                   [n]
  Existing code bugs:            [n]
  Proposed new-file design bugs: [n]
Critical Findings (CF):          [n]  (CRITICAL=[n]  HIGH=[n]  LOW=[n])
Open Questions (OQ):             [n]  (blocking=[n]  non-blocking=[n])
Architecture Decisions (DEC):    [n]
New files to create:             [n]  — [list file names]
Existing files to modify:        [n]  — [list file names]
Phases that can start NOW:       [list — no blocking OQs or unresolved CFs]
Phases currently BLOCKED:        [list — with blocker ID: OQ-XXX or CF-XXX]
Estimated overall complexity:    XL / L / M / S
───────────────────────────────────────────────────────
```

---

## Supplementary DISCOVERY Rules (overflow from `workflow_01_discovery.md` and `_ref.md`)

### Convergence Rule — Qualified REQ Count Definition (W-D2)

The Phase 2 convergence rule tests `Open Questions > confirmed REQs / 2`.
**"Confirmed REQ"** counts ONLY REQ-IDs that pass the PLANNER-Ready 4-question check:
`names=YES AND constants=YES AND algorithm=YES AND signature=YES`.
Vague or partially-specified REQs do NOT count toward the confirmed total.
This prevents inflated counts from suppressing the convergence trigger prematurely.

### Phase 3 New-File Bug Hunt — Completeness Gate (W-D3)

For every MISSING REQ-ID proposing a new class or file, apply this per-category scan before Phase 4:

| Category | What to check |
|----------|---------------|
| NF-1 Null on first tick | Any field used on tick 0 with no stated initial value? |
| NF-2 Unbounded collection | Any Queue/List/Dict that grows on every tick with no eviction? |
| NF-3 Undefined computation | Any named calculation whose algorithm is not fully specified? |
| NF-4 Uninitialized state | Any state field with no constructor default or init assignment? |
| NF-5 Dual implementation | Two places in the design claiming to produce the same value? |

Per-category output (Rule E — silence is a protocol failure):
- Finding: `NF-[n]: [class] — [description]` → add to BUG register as `Source: NEW_FILE_DESIGN`
- Clear: `NF-[n]: CLEAR — no instance found in proposed design for [class].`

This scan supplements (does not replace) Phase 4B CF scanning.

### CF Inheritance Check — VERSIONED MODE (W-D4)

Every CRITICAL CF from vN must appear in vN+1 with the same severity, OR with a note: `[Resolved in vN+1: reason]`. A CRITICAL CF silently absent from vN+1 is a spec failure — add it back before Phase 4B.

### Adjacency Impact Check — Targeted Fix Only (W-D5)

If the targeted fix changes a field name, class name, or method signature — read one level of callers in the codebase. If any caller is outside the targeted spec section, note it as a PLANNER_WATCH item in the feedback, do not expand the fix scope. Do not read beyond direct callers.
