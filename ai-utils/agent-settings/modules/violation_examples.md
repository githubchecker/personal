---
trigger: on_demand
description: "Shared module — all violation-vs-compliant example pairs. Load when any workflow or rule file references this file."
---

# Violation Examples — Shared Module

> **Who uses this:** ALL roles — universal reference for what rule violations look like vs correct output.
> **When to load:** When a rule or workflow file says `> See modules/violation_examples.md`.

---

## Rule E — Silence as PASS (from `0_analysis_rules.md`)

❌ VIOLATION — silence as PASS:
```
### REQ-001: Session initialization
### REQ-002: Token refresh flow
**Status:** PASS
**Finding:** Looks correct.
```
*(REQ-001 has no verdict at all. REQ-002 has a verdict but no evidence sentence.
Both are protocol failures — indistinguishable from being skipped.)*

✅ COMPLIANT — explicit PASS with evidence:
```
### REQ-001: Session initialization
**Status:** PASS
**Finding:** Reviewed. `SessionManager.InitializeAsync()` exists at `SessionManager.cs:L47`.
Initialization sequence matches spec §2.1 exactly.
**Action Required:** NONE

### REQ-002: Token refresh flow
**Status:** PASS
**Finding:** Reviewed. `HybridBffService.RefreshTokenAsync()` at `HybridBffService.cs:L203`
handles 401 retry exactly as specified. No gaps found.
**Action Required:** NONE
```

---

## Rule 11 — Append vs Replace (from `0_coding_rules.md`)

❌ VIOLATION — directive appended, duplicate created:
```csharp
// Before
services.AddSingleton<IEncryptionService, AesEncryptionService>();

// After — WRONG: added a second registration instead of replacing
services.AddSingleton<IEncryptionService, AesEncryptionService>();
services.AddSingleton<IEncryptionService, NewEncryptionService>();  // ← duplicate key
```
*(The first registration is never removed. At runtime the container resolves the last
one registered — but both exist, the old one silently unused, creating ghost code.)*

✅ COMPLIANT — existing directive replaced:
```csharp
// Before
services.AddSingleton<IEncryptionService, AesEncryptionService>();

// After — CORRECT: old registration replaced
services.AddSingleton<IEncryptionService, NewEncryptionService>();
```
*(Negative verification performed: confirmed `AesEncryptionService` registration removed
before adding `NewEncryptionService`. No duplicate exists.)*

---

## Checklist Line-Citation (from IMPLEMENTER)

❌ VIOLATION — no evidence:
```
**Checklist Results:**
- [x] Session token is saved after refresh — Verified
- [x] ⚠️ CF-003 VERIFIED: encryption applied — Confirmed
```
*(Neither item has a file:line citation. "Verified" and "Confirmed" are protocol violations.
PR_REVIEWER will mark these as UNVERIFIABLE. DELTA cannot trust them.)*

✅ COMPLIANT — line citation on every item:
```
**Checklist Results:**
- [x] Session token is saved after refresh
      `SessionManager.cs:L203` — `_sessionToken = response.Token;` assigns the refreshed value
- [x] ⚠️ CF-003 VERIFIED: AES-GCM encryption applied before log write
      `DepthLogManager.cs:L89` — `var encrypted = _encryptionService.Encrypt(line);`
      satisfies CF-003 because encryption occurs before the StreamWriter.WriteLine call at L91
```

---

## FABRICATED Ground Truth Check (from PR_REVIEWER)

❌ VIOLATION — no ground truth check:
```
### FABRICATED: TASK-007 — Add encryption to depth log writer
**Log claimed:** COMPLETED
**Diff search:** No hunk found in DepthLogManager.cs in diff range stable-v1.0..HEAD
**DELTA action:** REPLAN as P0
```
*(No ground truth check performed. The change may exist in the working tree as an
unstaged file. This FABRICATED verdict is invalid without Step 2b.5 verification.)*

✅ COMPLIANT — ground truth check performed:
```
### FABRICATED: TASK-007 — Add encryption to depth log writer
**Log claimed:** COMPLETED
**Diff search:** No hunk found in DepthLogManager.cs in diff range stable-v1.0..HEAD
**Ground truth check (MANDATORY):** `view_file` performed on
  `TradeInDepthPro/Services/DepthLogManager.cs` lines 80–100 —
  `_encryptionService.Encrypt(line)` call is ABSENT from live codebase at 2026-03-06 14:32.
  Change confirmed not present in working tree or diff.
**CF Gates:** CF-003 CRITICAL — now unverified
**DELTA action:** REPLAN as P0. CF-003 carried forward as GATE item.
```
