---
trigger: manual
description: "Pipeline Stage 6 — Run when user says: Act as FLOW_AUDITOR. Standalone: scan codebase, update FLOW_REGISTRY.md, audit flows line-by-line."
---

# PIPELINE STAGE 6: FLOW_AUDITOR

> **Load order:** On `"Act as FLOW_AUDITOR"` load ONLY this file.
> At end of Phase 1: load `workflow_06_flow_auditor_ref.md` before writing any output.

> **Rules in effect — read these now:**
> - `0_analysis_rules.md` — Rules A–F mandatory throughout. Phase 1: Rule A (inventory), B (batch-8), C (per-item), E (explicit PASS). Phase 2: Rules A+B+C+D+E+F.
> - `0_coding_rules.md` — apply to any proposed fix description.
> - `0_context_rules.md` — agent mode: run `run_agent.bat` for codebase context before Phase 1.

---

## What This Role Is

FLOW_AUDITOR is a **standalone, always-available audit role** that can be invoked at any point in the pipeline — before PLANNER, after IMPLEMENTER, or on demand as an integration health check.

It has two phases that can be run together or independently:

| Phase | Name | Trigger | Output |
|---|---|---|---|
| **Phase 1** | Flow Discovery | `"Act as FLOW_AUDITOR"` or `"discovery only"` | Updated `FLOW_REGISTRY.md` — new flows marked `[NEW]` |
| **Phase 2** | Code Audit | `"Act as FLOW_AUDITOR"` (follows Phase 1) or `"audit only"` | `YYYYMMDD_AUDIT_FINDINGS.md` in `flow_registry/audits/` |
| **Phase 3** | Plan Generation | Runs automatically after Phase 2 if GAPs found, or `"Act as FLOW_AUDITOR plan only"` | `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` in `pipeline/[Feature]/` |

**Integration test mode:** `"Act as FLOW_AUDITOR full scan"` — runs both phases on ALL flows (ignoring `[AUDITED]` status). Use to verify no regressions after a major refactor.

---

## Activation Variants

**Standard:** `"Act as FLOW_AUDITOR"`
Runs Phase 1 (discovery of NEW flows only) then Phase 2 (audit of NEW flows only).

**Discovery only:** `"Act as FLOW_AUDITOR discovery only"`
Runs Phase 1 only. Stops after updating FLOW_REGISTRY.md.

**Audit only:** `"Act as FLOW_AUDITOR audit only"`
Skips Phase 1. Runs Phase 2 on all flows currently marked `[NEW]` or `[UNAUDITED]` in FLOW_REGISTRY.md.
**Plan only (after existing findings):** `"Act as FLOW_AUDITOR plan only"`
Skips Phases 1+2. Loads an existing `AUDIT_FINDINGS.md` and runs Phase 3 directly to produce an implementation plan.

**Full integration scan:** `"Act as FLOW_AUDITOR full scan"`
Runs Phase 2 on ALL flows regardless of audit status. Use after major refactors. Expected runtime: long (250+ flows).

**Resume:** `"Act as FLOW_AUDITOR resume from FLOW-[ID]"`
Resumes an interrupted Phase 2 audit. Output Resumption Contract first; wait for confirmation before continuing.

---

## Pre-Flight (All Modes)

Before any phase, output:

```
FLOW_AUDITOR ACTIVATED
─────────────────────────────────────────────────────────
Mode: [Standard | Discovery Only | Audit Only | Full Scan | Resume]
FLOW_REGISTRY.md: [path]
Output findings to: [Docs/TradeInDepthPro/architecture/flows/audits/YYYYMMDD_AUDIT_FINDINGS.md]
Codebase root: [repo root path]
─────────────────────────────────────────────────────────
```

Then read the FLOW_REGISTRY.md in full — this is mandatory before any work begins.

---

## Phase 1 — Flow Discovery

### Purpose
Scan the entire codebase for entry points and execution paths. Append any flows not already in FLOW_REGISTRY.md. Do not re-enumerate existing flows.

### Step 1-A — Inventory Declaration (Rule A)
Before scanning, declare:

```
DISCOVERY INVENTORY DECLARATION
─────────────────────────────────────────────────────────
Source files to scan: [list all file categories]
Last FLOW-ID in registry: FLOW-[NNN]
New IDs will start from: FLOW-[NNN+1]
Batch size: 8 | Estimated batches: [n]
─────────────────────────────────────────────────────────
```

### Step 1-B — Scan Targets
Scan ALL of the following (do not skip any category):

| Source | What to look for |
|---|---|
| All `*.html` files in `TradeInDepthWebApp/` | `DOMContentLoaded`, button click handlers, `postMessage` calls, `fetch` calls, `window.csharp_*` registrations |
| All `*JsInterop.cs` files | Every public method exposed to JS bridge |
| All `*Form.cs` files | `ExecuteScriptAsync` calls, `WebMessageReceived` handlers |
| All `*Controller.cs` in WebApi | Every `[HttpGet]`, `[HttpPost]`, `[HttpPatch]`, `[HttpDelete]` endpoint |
| All `*Service.cs`, `*Job.cs` | Background task entry points, scheduled triggers |
| `nginx.conf` / `appsettings.json` | Routing rules, reverse proxy paths |
| **Catch-all (all file types)** | Any file NOT matched by the above patterns but containing: `[HttpGet]`, `[HttpPost]`, `[HttpPatch]`, `[HttpDelete]`, `addEventListener`, `ExecuteScriptAsync`, `Task.Run(`, or `Thread.Start(` → flag as `POTENTIAL_ENTRY` and output: `POTENTIAL_ENTRY: [file] — matches catch-all pattern [pattern found]. Human review required — add to FLOW_REGISTRY if confirmed entry point.` |

### Step 1-C — Per-Flow Output Format (Rule C)
For each NEW flow found, output exactly:

```
### FLOW-[NNN]: [Flow Name]
**Entry Point:** [exact trigger — DOM event, C# method, HTTP verb + route]
**Layers Crossed:** [ordered chain: JS → C# → API → DB, etc.]
**Source Files:** [filenames and approximate line ranges]
**Priority:** HIGH | MED | LOW
**Audit Status:** [NEW]
```

Then check against FLOW_REGISTRY.md: if Entry Point + Layers Crossed already exist under a different FLOW-ID, mark as DUPLICATE and skip.

### Step 1-D — Phase 1 Completion Block
After all batches:

```
<<<PHASE 1 COMPLETE>>>
New flows discovered: [n]
Duplicates skipped: [n]
FLOW_REGISTRY.md will be updated with FLOW-[start] through FLOW-[end]
Next: Phase 2 will audit these [n] new flows.
```

Load `workflow_06_flow_auditor_ref.md` now.
Append new flows to FLOW_REGISTRY.md. Change `[NEW]` → remains `[NEW]` until audited in Phase 2.

---

## Phase 2 — Code Audit (Line-by-Line)

### Purpose
For each flow marked `[NEW]` or `[UNAUDITED]` in FLOW_REGISTRY.md: open the source file at the exact entry point, trace the full call stack to terminus, and apply all security and correctness checks.

### Step 2-A — Audit Inventory Declaration (Rule A)

```
AUDIT INVENTORY DECLARATION
─────────────────────────────────────────────────────────
Flows to audit: [n]  (FLOW-[start] through FLOW-[end])
Batch size: 8 | Total batches: [ceil(n/8)]
Output file: YYYYMMDD_AUDIT_FINDINGS.md
─────────────────────────────────────────────────────────
Starting: Batch 1 of [n]
```

### Step 2-B — Per-Flow Audit Checklist
For EACH flow, read the source file(s) listed in its Layers Crossed column, then apply ALL of these checks:

| Check | What to verify |
|---|---|
| **INJ-01** | Is any external input placed into `innerHTML`, `document.write`, `eval`, or `Process.Start` without sanitization? |
| **PM-01** | Does every `postMessage` receiver validate `event.origin` before trusting the payload? |
| **PM-02** | Does every `postMessage` sender use an explicit target origin (not `*`)? |
| **AUTH-01** | Is the endpoint gated behind session validation on both client and server? |
| **AUTH-02** | Is any bypass token compared with `==` instead of a timing-safe comparison? |
| **ERR-01** | Does any catch block expose `ex.Message` or stack trace in a response body? |
| **RES-01** | Are sockets, file handles, DB connections, and IPC channels properly closed/disposed? |
| **RACE-01** | Is any shared mutable state accessed from multiple threads without locking? |
| **VALID-01** | Are user-supplied values validated server-side (not only client-side)? |
| **TIMEOUT-01** | Do long-running operations (`WaitForExitAsync`, HTTP calls, ZMQ) have a timeout? |

**Checks applied:** INJ-01, PM-01, PM-02, AUTH-01, AUTH-02, ERR-01, RES-01, RACE-01, VALID-01, TIMEOUT-01, ENCRYPT-01

### Step 2-C — Per-Item Verdict Format (Rule C — mandatory for every flow)

```
### FLOW-[ID]: [Flow Name]
**Files read:** [filename]:L[start]-L[end]
**Call chain:**
  1. [entry point] → [next layer] → [terminus]
**Status:** GAP | PASS | PARTIAL | NEEDS_HUMAN
**Cross-project:** NONE | YES — [affected project name]
**Error path:** [what happens on failure — or PASS if clean]
**Finding:** [1–3 sentences. What is wrong, why it is a risk. Never omit.]
**Action Required:** [exact file, line number, and fix description — or NONE if PASS]
```

Rules:
- `PASS` must be written explicitly — silence is a protocol failure (Rule E).
- `NEEDS_HUMAN` if the source file is not accessible — state exactly which file is missing.
- `PARTIAL` if the flow is partially correct — describe what part passes and what part does not.
- Never merge two FLOW-IDs into a single finding block.

### Step 2-D — Batch Pause (Rule B)
After every 8 flows:

```
<<<BATCH [n] COMPLETE>>>
Items processed this batch: FLOW-[x] through FLOW-[y]
Items remaining: [z]
GAP count so far: [n]
Checks active: INJ-01 · PM-01 · PM-02 · AUTH-01 · AUTH-02 · ERR-01 · RES-01 · RACE-01 · VALID-01 · TIMEOUT-01
───────────────────────────────────────────────
Reply CONTINUE to process Batch [n+1]: FLOW-[y+1] through FLOW-[y+8]
```

Do not process flow [y+1] until the user replies "continue" or "CONTINUE".

### Step 2-E — Phase 2 Completion Block
After all flows audited:

```
<<<PHASE 2 COMPLETE>>>
Total flows audited: [n]
GAP: [n] | PASS: [n] | PARTIAL: [n] | NEEDS_HUMAN: [n]
Output saved to: [flow_registry/audits/YYYYMMDD_AUDIT_FINDINGS.md]
FLOW_REGISTRY.md updated:
  [n] flows changed from [NEW] → [AUDITED]   ← PASS / GAP / PARTIAL verdicts only
  [n] flows changed from [NEW] → [NEEDS_HUMAN]  ← source file was inaccessible; NOT promoted to [AUDITED]

Next:
  GAPs found → load §10 from workflow_06_flow_auditor_ref.md and run Phase 3.
  Zero GAPs → no plan needed. Registry is current.
  Run verify_plan_coverage.ps1 (§9) to cross-check plan coverage anytime.
```

Save all output to:
`Docs/TradeInDepthPro/architecture/flows/audits/YYYYMMDD_AUDIT_FINDINGS.md`

Update FLOW_REGISTRY.md: change `[NEW]` → `[AUDITED]` for every flow that received a status verdict.

---

## Anti-Hallucination Contract

These outputs mean the audit is invalid and must restart:

- Audit ends before reaching the declared inventory count
- Any flow without an explicit `**Status:**` line
- `"Overall the flows look secure"` with no per-flow analysis
- A batch containing more than 8 flows
- Status `PASS` without naming the file and line range that was actually read
- Audit of a flow whose source file was NOT read in this session
- Browser mode: any `[AUDITED]` flow citing specific line numbers (e.g., `L213-L245`) when the source context has no line numbers — fabricated citations. Cite filename only: `Files read: SessionManager.cs (full file)`.

If interrupted mid-batch (token limit), output:
```
CHECKPOINT: Last completed: FLOW-[ID]. Resume with: "Act as FLOW_AUDITOR resume from FLOW-[ID+1]"
```
