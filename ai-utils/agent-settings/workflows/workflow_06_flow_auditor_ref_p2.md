---
trigger: manual
description: "FLOW_AUDITOR Reference Part 2 — FLOW_REGISTRY update protocol, [CHANGED] marking, and post-audit integration steps. Load after Phase 2 completion."
---
> ⚠️ FILE SIZE LIMIT: 12,000 characters.

# FLOW_AUDITOR Reference — Part 2

## § 6 — FLOW_REGISTRY.md Update Protocol

At end of Phase 2 (or after each batch if requested):

1. For every flow that received a verdict: change `[NEW]` → `[AUDITED]`.
2. For every `NEEDS_HUMAN` flow: change to `[NEEDS_HUMAN — [file missing]]`.
3. For every `CHANGED` flow: change to `[AUDITED — re-audited YYYY-MM-DD]`.
4. Do NOT remove any row — the registry is append-only.
5. Note at bottom of FLOW_REGISTRY.md:
   ```
   <!-- Last audit: YYYYMMDD_AUDIT_FINDINGS.md | Flows audited: FLOW-[start]–FLOW-[end] -->
   ```

---

## ENCRYPT-01 — Asset Encryption Format Integrity (Full Definition)

| Field | Value |
|-------|-------|
| **Check ID** | ENCRYPT-01 |
| **Name** | Asset Encryption Format Integrity |
| **PASS condition** | Any flow touching `OnWebResourceRequested`, `IsEncrypted()`, or `DecryptAsset()` in `BaseWebView2Form.cs` preserves the `[TIDE magic 4B][IV 16B][Ciphertext]` format exactly |
| **FAIL condition** | Any change to `IsEncrypted()` that reverts to the old `length > 16` heuristic, or any change to `DecryptAsset()` that alters the 4-byte magic header offset, or hardcoding of `ASSET_ENCRYPTION_KEY` instead of reading from `TIDP_ASSET_KEY` env var |

---

## Rule Re-Anchor (Every 10 Flows Audited)

> Full block: `modules/output_blocks.md` §"Rule Re-Anchor Block".
> **Trigger:** After auditing flows 10, 20, 30… output the RULE RE-ANCHOR block before continuing.
> **Gate:** CF unverified > 0 at checkpoint → stop. Surface before continuing to next batch.
> **Key FLOW_AUDITOR signal:** NEEDS_HUMAN accumulating (source files not in context) → surface at re-anchor, do not defer to Phase 3. Missing source = missing audit = registry cannot be updated.

