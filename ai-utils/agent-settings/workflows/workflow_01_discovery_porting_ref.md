---
trigger: manual
description: "DISCOVERY Porting Rules — load when PORTING MODE is ACTIVE (triggered from workflow_01_discovery.md Phase 3). Contains all six porting rules for transforming an existing document into a spec without data loss."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# DISCOVERY — Porting Rules Reference

> **When to load:** Load only when PORTING MODE: ACTIVE is set in Phase 3. Not loaded on activation. Not needed for Q&A-only or versioned-spec flows.

> **⚠️ PORTING RULE — ARTEFACT PRESERVATION:**
> When input is an existing plan, report, analysis, or spec — you are PORTING. **PRESERVE all concrete implementation artefacts verbatim:** field names, class names, method signatures, constant values, code patterns, algorithm steps, config schemas, interface definitions. Do NOT summarise into a DEC-ID alone — DEC-IDs capture WHY; the artefact is the HOW. If source includes a code block, field list, or constant — reproduce it in §3 DEC-ID body, §4 Frozen Values, or §13. Never discard it.
>
> **⚠️ PORTING RULE — PER-LINE TRANSFORMATION QUESTION (apply to every paragraph/block of source):**
> Do NOT read the source in bulk then decide what to preserve. Process each paragraph/block by asking two questions in sequence:
> 1. **"What does this content say?"** — Classify it: requirement · design decision · code artefact · user journey · inventory list · named gap · decision option table · config/env table · broken-state description.
> 2. **"What must it become in the spec format?"** — Map it:
>    - Requirement → REQ-ID row; if MISSING also a DEC-ID
>    - Design decision → DEC-ID with WHY + alternative rejected
>    - Code artefact (field list, constant, pattern) → §3 DEC-ID body or §4 verbatim
>    - User journey (any named Journey A/B/C) → §13 subsection verbatim
>    - Inventory prose ("What Currently Exists") → §13 subsection verbatim
>    - Named gap (GAP-x.x) → BUG register entry + §13 verbatim
>    - Decision option table → §13 verbatim — options table AND the rationale sentences for each rejected alternative
>    - Config/env variable table → §13 verbatim
>    - Broken-state table ("What Is Broken or Missing") → §13 verbatim
> **If a block does not map cleanly to any category above → §13 verbatim. Never discard.**
> The ONLY content that may be omitted is explicitly superseded legacy content where the source itself states the old behaviour is replaced.
>
> **⚠️ PORTING RULE — §13 FULL SCOPE (additive, applies alongside artefact rule):**
> §13 is NOT limited to code artefacts. It must reproduce ALL of the following from the source:
> 1. **All user journeys** — step-by-step sequences for EVERY named feature (EXISTS and MISSING alike).
> 2. **All "What Currently Exists" inventory sections** — method names, class names, data structures. Preserve as §13 subsection, not just a REQ-ID row.
> 3. **All environment variable tables and config tables** — reproduce verbatim.
> 4. **All decision option tables with full rationale** — options table AND rationale sentences explaining why each alternative was rejected (even when already captured in a DEC-ID).
> 5. **All explicitly named gaps** — e.g. "GAP-1.1", "GAP-9.2" — even if they do not map to a MISSING REQ-ID. Add to the BUG register as LOW severity if not already captured. Never silently discard a named gap.
> 6. **All "What Is Broken or Missing" tables** — reproduce in §13, even if already covered by BUG-IDs.
>
> **⚠️ PORTING RULE — EXISTS CAPABILITY PRESERVATION MANDATE:**
> A capability matrix row with status EXISTS is NOT sufficient preservation on its own. You MUST also:
> - Append a `Context:` annotation to the matrix row: one-line description of the key class/method/flow (e.g. `Context: RedisService.RegisterDeviceLoginAsync`).
> - If the EXISTS capability has a step-by-step journey or decision table in the source: add a `DEC-ID: CONTEXT-ONLY` entry in §3 to preserve it. Mark it `[CONTEXT-ONLY — no implementation work implied]` so PLANNER does not generate tasks from it.
> - If the EXISTS capability has a named gap in the source — that gap MUST appear in the BUG register even if no REQ-ID is MISSING.
>
> **⚠️ PORTING RULE — LOSSLESSNESS CHECK (mandatory — run BEFORE Phase 4):**
> Enumerate every named section heading in the source document. For each, verify at least ONE is true:
>   a. Maps to one or more REQ-IDs, OR  b. Maps to one or more BUG-IDs, OR  c. Maps to one or more DEC-IDs, OR  d. Reproduced as a §13 subsection.
> If any heading has NONE of a–d → add a §13 block for it before proceeding.
> Output: `LOSSLESSNESS CHECK: [n] source sections — [n] fully covered, [n] added to §13 during check.`
> **This check is MANDATORY even when context is tight. Silent omissions are a spec failure.**
>
> **⚠️ PORTING CHAIN RULE (runs immediately after LOSSLESSNESS CHECK, mandatory):**
> From all filenames and timestamps visible in this session, determine if multiple versions of the same document exist. If so and the source ported from is not the oldest, also run the LOSSLESSNESS CHECK against the oldest version — intermediate versions may have already dropped content. If the oldest is not in context, ask for it before Phase 4. If user declines: output `PORTING CHAIN WARNING: oldest version not checked — risk acknowledged.`
