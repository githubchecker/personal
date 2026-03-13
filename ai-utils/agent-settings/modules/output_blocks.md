---
trigger: on_demand
description: "Shared module — structured output block templates for re-anchor, activation, and conflict surfacing. Load when any workflow references this file."
---

# Output Block Templates — Shared Module

> **Who uses this:** ALL roles use the activation and conflict blocks. IMPLEMENTER uses the re-anchor block.
> **When to load:** When a rule or workflow file says `> See modules/output_blocks.md`.

---

## Role Activation — Rule Active Confirmation Block

Every role MUST output this block immediately on activation, before any phase work begins.
It is a compact summary — not a substitute for reading the full rule files.
Its purpose: give the session a re-readable, near-the-top anchor that remains visible
throughout a long run without requiring a full re-read of all rule files.

```
RULES ACTIVE — [ROLE NAME] SESSION
─────────────────────────────────────────────────────────
Analysis protocol  : Rules A–F active
  A: Inventory declaration before any list processing
  B: Max 8 items per batch — hard pause after each
  C: Per-item explicit verdict — silence is a protocol violation
  D: Cross-reference ledger when comparing two documents
  E: PASS must be written explicitly — never omit
  F: Resumption contract before continuing interrupted work

Coding standards   : §6 Security (no hardcoded secrets) · §7 Error Handling (no silent catch)
                     §11 Anti-Duplication (replace, never append) · §12 Diff Check (git diff HEAD)

Context protocol   : [AGENT: run_agent.bat before any implementation / BROWSER: uploaded context = ground truth]

Project rules      :
  Naming           — JS csharp_ prefix · C# _camelCase private / PascalCase public · no DateTime.Now
  WebView2         — all settings in BaseWebView2Form · IPC via env vars only · HybridBffService only
  Security         — ENCRYPTED_V1:[nonce|tag|ct] locked · RSA-signed config · HMAC webhook verify
  Audit            — write AFTER profile update succeeds · append-only · never delete

CF status          : [n] CRITICAL in this session — [n] verified · [n] unverified
─────────────────────────────────────────────────────────
```

**Rules for filling the block:**
- CF status line: read from the plan or spec loaded for this session. If no plan yet: `CF status: pending spec/plan load`
- Context protocol line: detect mode from whether a terminal is available (agent) or a context file was uploaded (browser)
- Do NOT skip this block even for short sessions

---

## Rule Re-Anchor Block (Agent Mode — Every 10 Tasks)

After completing tasks 10, 20, 30, … (every multiple of 10), output this block verbatim
before reading the next task. Do not skip it — attention decay in long runs makes this
the single most important compliance guard.

```
RULE RE-ANCHOR — After Task [n]
─────────────────────────────────────────────────────────
Active rules re-confirmed (re-read relevant sections now):

0_coding_rules.md:
  §6  Security First     — no hardcoded secrets, always validate inputs
  §7  Error Handling     — no empty catch, no silent failures
  §11 Anti-Duplication   — check for existing directive before adding; replace, never append
  §12 Diff Check         — git diff HEAD -- [file] for every claimed change (agent mode)

Project rules:
  csharp_ prefix         — all JS functions called from C# via ExecuteScriptAsync
  No DateTime.Now        — use SessionManager.ServerAuthorizedTime for all time logic
  HybridBffService only  — no direct HttpClient calls to backend from any other service
  ENCRYPTED_V1 format    — [TIDE magic 4B][IV 16B][Ciphertext] — do not alter
  Audit log immutable    — write AFTER profile update succeeds; append-only; never delete

CF Status at this checkpoint:
  CRITICAL verified so far  : [n]
  CRITICAL unverified so far: [n]  ← if > 0, state which tasks and why unverified
─────────────────────────────────────────────────────────
```

**Gate:** If CF unverified count is > 0 at a re-anchor checkpoint — stop and surface to user
before continuing. Do not accumulate unverified CFs silently across 10-task blocks.

---

## Rule Conflict Surfacing Block

**Mandatory conflict surfacing (applies to ALL roles — no exceptions):**
Whenever a rule collision is detected during any task or analysis step, output this block
immediately before applying any resolution:

```
RULE CONFLICT DETECTED
──────────────────────────────────────────────────────
Rule A: [filename §section] — "[exact rule text or summary]"
Rule B: [filename §section] — "[exact rule text or summary]"
Conflict: [1 sentence — what specific decision they disagree on]
Resolution: Applying Rule [A/B] — reason: [more specific / more recent / project overrides global]
User review: [RECOMMENDED if touching security, payments, or CF-gated code / NOT REQUIRED otherwise]
──────────────────────────────────────────────────────
```

This block appears in the task log (IMPLEMENTER), the plan dry-run output (PLANNER),
or the findings (PR_REVIEWER / FLOW_AUDITOR) — wherever the conflict was encountered.
A conflict resolved without this block is a governance violation under R6.
