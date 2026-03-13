---
description: "FLOW_AUDITOR Reference — output templates, check definitions, ledger format, resumption. Load at Phase 1 completion."
---
> ⚠️ **12 000 chars max.**

# FLOW_AUDITOR Reference

---

## § 1 — FLOW_REGISTRY.md Row Format

Row format:

```
| FLOW-[NNN] | [Flow Name] | [Entry Point] | [Layers Crossed] | [Source Files (A/B/A+B)] | [Priority] | [Audit Status] |
```

**Audit Status values:**
- `[NEW]` — discovered in current session, not yet audited
- `[AUDITED]` — Phase 2 audit completed with status PASS, GAP, or PARTIAL — source file was actually read
- `[UNAUDITED]` — existed in registry before audit tooling was set up; treat same as [NEW]
- `[CHANGED]` — source file was modified since last audit; treat same as [NEW] for re-audit
- `[NEEDS_HUMAN]` — Phase 2 attempted but source file was not in context; verdict is NEEDS_HUMAN; NOT equivalent to [AUDITED]; must be re-audited when source file is available
- `[EXCLUDED]` — explicitly excluded from auditing (e.g., FLOW-004 docs-only error); include reason

---

## § 2 — Full Audit Findings File Header

Every `YYYYMMDD_AUDIT_FINDINGS.md` file must begin with:

```markdown
# AUDIT FINDINGS — TradeInDepthPro
**Date:** YYYY-MM-DD
**Agent session:** [model name or session ID]
**Flows audited this session:** [n] (FLOW-[start] to FLOW-[end])
**Mode:** [Standard | Full Scan | Audit Only]
**Source registry:** FLOW_REGISTRY.md (as of YYYY-MM-DD)
**Checks applied:** INJ-01, PM-01, PM-02, AUTH-01, AUTH-02, ERR-01, RES-01, RACE-01, VALID-01, TIMEOUT-01

---
```

---

## § 3 — Cross-Reference Ledger (Rule D — Multi-Session or Multi-Model)

When two models audit the same set of flows (parallel mode), output this ledger BEFORE writing any findings:

```
CROSS-REFERENCE LEDGER
──────────────────────
| FLOW-ID   | Status (Model A) | Status (Model B) | Final Status | Note |
|-----------|-----------------|-----------------|--------------|------|
| FLOW-001  |      PASS       |      PASS       |     PASS     |      |
| FLOW-002  |      GAP        |      PARTIAL    |     GAP      | Model A found INJ-01 at L413; Model B saw PARTIAL — GAP wins |
| FLOW-003  |      PASS       |      GAP        |     GAP      | [Found by Model B only — verify] |
```

**Merge rule (always take the stricter verdict):**
`GAP > PARTIAL > NEEDS_HUMAN > PASS`

After ledger, process CONFLICT and ONLY-IN-A/B rows only. Agreements (both PASS) are confirmed by ledger — no further analysis needed.

---

## § 4 — Check Definitions

| Check ID | Name | Pass Condition | Fail Condition (→ GAP) |
|---|---|---|---|
| INJ-01 | Injection | All user-supplied values use `textContent`, `createTextNode`, or DOMPurify before innerHTML | Any `plan.field`, `user.input`, or external value interpolated directly into innerHTML or `Process.Start` |
| PM-01 | postMessage Origin (Receiver) | Every `window.addEventListener('message')` validates `event.origin` against an allowlist before reading `event.data` | Handler trusts `event.data` regardless of sender origin |
| PM-02 | postMessage Target (Sender) | Every `window.postMessage(msg, targetOrigin)` uses a specific origin string | Sender uses wildcard `'*'` as targetOrigin |
| AUTH-01 | Authentication Gate | Endpoint verifies session token before processing; JS bridge methods cannot be called without active session | Endpoint or bridge method callable without valid session |
| AUTH-02 | Timing-Safe Comparison | Secret/token comparison uses `CryptographicOperations.FixedTimeEquals` or equivalent | Comparison uses `==`, `string.Equals`, or direct byte equality without constant-time guarantee |
| ERR-01 | Error Leakage | `catch` blocks return a generic error response; `ex.Message` and stack trace never sent to client | Response body contains `ex.Message`, `ex.StackTrace`, or internal path |
| RES-01 | Resource Disposal | All `IDisposable` objects (ZMQ sockets, DB connections, streams) in `using` blocks or explicit `Dispose()` in `finally` | Resource allocated without `using` block, no `Dispose()` on error path |
| RACE-01 | Thread Safety | Shared mutable state accessed only under `lock`, `SemaphoreSlim`, or equivalent synchronization | Multiple `Thread.Start` / `Task.Run` write same field without lock |
| VALID-01 | Server-Side Validation | All format constraints (phone, GSTIN, email) validated server-side in addition to (not instead of) client-side | Server accepts any string that passes client-side validation without re-checking |
| TIMEOUT-01 | Operation Timeout | Long-running operations (`Process.WaitForExitAsync`, `HttpClient.SendAsync`, ZMQ receive) have a `CancellationToken` with timeout | Blocking wait with no timeout — process can hang indefinitely |
| ENCRYPT-01 | Asset Encryption Format | See `workflow_06_flow_auditor_ref_p2.md` for full definition | Change to `IsEncrypted()`, `DecryptAsset()`, or hardcoded `ASSET_ENCRYPTION_KEY` |

---

## § 5 — Resumption Contract (Rule F)

Output this block at the start of any resumed session before processing any flows:

```
RESUMPTION CONTRACT
───────────────────
Previous session completed: Batch [n], FLOW-[x] through FLOW-[y]
Resuming: Batch [n+1], FLOW-[y+1] through FLOW-[y+8]
Output file: YYYYMMDD_AUDIT_FINDINGS.md (appending)
Human confirmation required: Does this resumption point match your records? (yes/no)
```

Do not process flows until user confirms.

---

## § 6 — FLOW_REGISTRY.md Update Protocol → See `workflow_06_flow_auditor_ref_p2.md`
> Load `workflow_06_flow_auditor_ref_p2.md` after Phase 2 completion for the full registry update protocol.

---

## § 7 — Pipeline Integration Points

| When to invoke FLOW_AUDITOR | Mode | Why |
|---|---|---|
| After any new feature ships | Standard | Catch new flows from feature PRs — append `[NEW]` rows, then audit them |
| After IMPLEMENTER completes | Audit Only | Verify no security gap was accidentally introduced by the code changes |
| Before starting PLANNER on a new audit cycle | Standard | Ensure FLOW_REGISTRY.md is current so PLANNER works from accurate data |
| After a major refactor touching many files | Full Scan | Reset all flow statuses and re-audit everything |
| When PLANNER or IMPLEMENTER references a flow not in registry | Discovery Only | Add the missing flow, assign FLOW-ID, then continue pipeline |

---

## § 8 — File Outputs at Each Stage

| Phase | Output File | Location | Updated Files |
|---|---|---|---|
| Phase 1 | — (rows appended inline) | — | `FLOW_REGISTRY.md` |
| Phase 2 | `YYYYMMDD_AUDIT_FINDINGS.md` | `flow_registry/audits/` | `FLOW_REGISTRY.md` (status updated) |
| Phase 3 | `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` | `pipeline/[Feature]/` | — |
| Verify | Script output to console | — | — |

---

## § 9 — verify_plan_coverage.ps1 Invocation

Script location: `Utils\agent-settings\tools\verify_plan_coverage.ps1`

Default params auto-resolve from `$PSScriptRoot` — no arguments needed for standard usage:

```powershell
.\verify_plan_coverage.ps1 `
  -MasterFlowListPath "..\..\..\flow_registry\FLOW_REGISTRY.md" `
  -FindingsPath       "..\..\..\flow_registry\audits\[YYYYMMDD]_AUDIT_FINDINGS.md" `
  -PlanPath           "..\[Feature]\[YYYYMMDD_HHMM]_02_IMPLEMENTATION_PLAN.md"
```

Exit 0 = all GAPs have a TASK or HOLD → safe to send to IMPLEMENTER.
Exit 1 = FAIL rows remain → do not proceed until gaps are addressed.

---

## § 10 — Phase 3: Audit-to-Plan Conversion Protocol

> Load this section immediately after Phase 2 completes and GAPs are found.
> Phase 3 IS the PLANNER stage specialized for audit input.
> Also loads: `workflow_02_planner_ref.md` (task format template).

### Step 3-A — GAP Inventory Declaration

Before writing any tasks, output:

```
GAP INVENTORY
─────────────────────────────────────────────────────────────
Total GAPs identified from AUDIT_FINDINGS.md: [n]
CRITICAL: [n]  HIGH: [n]  MEDIUM: [n]  LOW: [n]
NEEDS_HUMAN (no task written — becomes HOLD): [n]
Tasks after dedup/merge: [n]
Batch size: 8 | Total batches: [n]
─────────────────────────────────────────────────────────────
```

Extraction rules (apply to ALL findings files, no exceptions):
- Include only entries where `**Status:** GAP`.
- Collect `NEEDS_HUMAN` entries separately — write them as HOLD items, never as executable tasks.
- Ignore `PASS` and `PARTIAL` entries (PARTIAL may become HOLD if `Action Required` is ambiguous).
- Merge two GAP entries that cite the **exact same file + line** into one task. List both FLOW-IDs in `**Refs:**`.
- Derive severity from the Finding text: injection/auth/race = CRITICAL; unauthenticated bypass = HIGH; missing validation = MEDIUM; logging/timeout = LOW.

### Step 3-B — Code-Level Dry-Run (Per gap, before writing any task)

For **each** GAP entry:
1. Open the file cited in `**Action Required:**` at the stated line.
2. Read and paste the 3–5 lines you will use as the SEARCH block.
3. Confirm those lines are unique within that file.
4. Confirm the fix stated in `Action Required` is implementable as described.
5. If the SEARCH text does not match the live file: note the discrepancy and derive the correct anchor from what you actually read. Do NOT guess or paraphrase.

Dry-run output per gap:

```
### DRY-[NNN]: [FLOW-ID(s)] — [short gap name]
File read: [filename]:L[start]–L[end]
SEARCH unique? YES ([anchor line excerpt]) | NO → [corrected anchor]
Fix implementable as stated? YES | PARTIAL → [describe what changes]
Severity: CRITICAL | HIGH | MEDIUM | LOW
Action: Proceed | Merge with DRY-[NNN] | HOLD
```

Process exactly 8 gaps per batch. After each batch:
```
<<<DRY-RUN BATCH [n] COMPLETE>>>
Items: DRY-[x] through DRY-[y] | Continuing automatically.
```
(Do not wait for user input between dry-run batches.)

### Step 3-C — Write Implementation Plan

After ALL dry-run batches complete, write the plan using the
`02_IMPLEMENTATION_PLAN.md` format from `workflow_02_planner_ref.md`.

**File header (fill all fields):**
```
# AUDIT-SOURCED IMPLEMENTATION PLAN
Generated : [YYYY-MM-DD] | Model: [self-identify]
Source    : [YYYYMMDD_AUDIT_FINDINGS.md] (FLOW_AUDITOR Phase 2)
Feature   : [feature or audit batch name, e.g. AuditFix]
Total Tasks: [n] | HOLD items: [n]
CF Coverage: [n] CRITICAL gaps embedded as GATE tasks
Split Mode : SINGLE FILE
```

**Task ordering (non-negotiable):**
1. P0 — CRITICAL (most-shared or most-dangerous callee first)
2. P1 — HIGH
3. P2 — MEDIUM
4. P3 — LOW
5. Within same tier: tasks that unblock other tasks come first

**Task format:** use `workflow_02_planner_ref.md` exactly. Each task must include:
`Title`, `Type`, `Priority`, `Complexity`, `Model`, `Refs` (FLOW-IDs), `Depends On`, `CF Embedded`,
`Why`, `File I/O Permissions`, `SEARCH` block (verbatim from dry-run), `REPLACE` block, `Verification`.

**HOLD format (for every NEEDS_HUMAN finding):**
```
### HOLD-[NNN]: [FLOW-ID] — [topic]
**Reason:** [why human review is required — missing file, ambiguous fix, security policy decision]
**Resume When:** [condition that makes this unblockable]
```

### Step 3-D — Phase 3 Completion

```
<<<PHASE 3 COMPLETE>>>
Plan written: [YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md]
Save with: python pipeline.py save --feature [Feature] --type plan --file [path]
Tasks: [n] executable | HOLD: [n] deferred
Next: Run verify_plan_coverage.ps1 (§9). Then: "Act as IMPLEMENTER".
```

