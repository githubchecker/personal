---
trigger: manual
description: "DISCOVERY Reference — spec.md output template, anti-hallucination rules, phase output formats, and cross-model prompt. Read before writing Phase 6 output."
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# DISCOVERY Reference — Output Format & Rules

> **When to read:** Phase 4 → §Phase Output Formats (all block formats); Phase 5 → §Ledger Completeness Check; Phase 6 → §Output Format + §Anti-Hallucination Rules. Do NOT load on activation — load at Phase 3 completion (with p4.md).

## Output Format: `[Feature]_spec.md`

> **Full template:** Load `modules/discovery_spec_template.md` before writing Phase 6 output.
> Follow its structure exactly. Fill every bracketed field — VALIDATOR auto-detects mode from the `Source:` field.



## Anti-Hallucination Rules (Always Active)

1. **Never invent a class, method, or field name.** If you reference one, cite the file.
2. **Never assume a feature "already exists"** without reading the file and finding it.
3. **Never use a magic number** unless it came from the codebase or the user stated it explicitly.
4. **If unsure — say so.** Write `[UNVERIFIED]` and ask. Never silently assume.
5. **All code snippets** must be verified-correct syntax — not pseudocode unless labelled as such.
6. **PORTING MODE — lossless preservation:** Apply all rules from `workflow_01_discovery_porting_ref.md` (artefact verbatim preservation, §13 full scope, EXISTS context annotation, losslessness check with LOSSLESSNESS CHECK: output). Verify all three sub-rules before emitting Phase 6 GO.
7. **Every MISSING REQ-ID must have a DEC-ID.** A MISSING item with no DEC-ID is a spec failure.
8. **Every CF must be bound to a phase** in §6 Critical Findings Bound to Phases. An unbound CF will be ignored by PLANNER.

## Phase Output Formats

### Resumption Contract
```
RESUMPTION CONTRACT — DISCOVERY
--------------------------------
Interrupted at: [REQ-XXX / Phase 4B / Phase 5 — as stated in your message]
Items confirmed complete: REQ-001 through REQ-[previous]
Resuming from: [REQ-XXX or Phase 4B CF scan or Phase 5 Cross-Check]
--------------------------------
Does this match your records? (yes / no — if no, state the correct resume point)
```

### Self-Validation Inventory
```
SELF-VALIDATION INVENTORY: [Feature]_spec.md
Items: REQ=[n] BUG=[n](existing=[n] new-design=[n]) CF=[n](Phase 4B only) DEC=[n] OQ=[n]
Total to validate in Phase 4 batches (REQ+BUG+DEC): [n] | Batch size: 8 | Batches: [ceil(n/8)]
CF items: listed for reference only — processed in Phase 4B batches, not Phase 4.
```

### Per-Item Verdict
```
### REQ-XXX: [name]
Source: [source document section / codebase file:fn — where this item was found]
Status: PASS / GAP / CONFLICT / PARTIAL / NEEDS_HUMAN
Capability: EXISTS ([file:fn]) / PARTIAL ([what exists, what's missing]) / MISSING
Implementable as written? YES / NO / NEEDS_CLARIFICATION
Hallucination risk: LOW (cosmetic if wrong) / MEDIUM (wasted effort) / HIGH (breaks at runtime)
Finding: [spec claim vs codebase reality — 1–3 sentences, never omit]
Action: Proceed as-is / Fix spec now / Ask user / Mark as OQ-XXX
```
> Rule E: Status: PASS must be written explicitly — silence is a protocol failure. If no issues: write Status: PASS with one sentence of evidence.

### Batch PAUSE Block
```
<<<SELF-VALIDATION BATCH [n] COMPLETE>>>
Items processed this batch: REQ-[x] through REQ-[y]
Items remaining: [z]
High-risk items found this batch: [n]
----------------------------------------
Reply CONTINUE to process next batch
```

### Token Limit Block
```
SELF-VALIDATION INTERRUPTED — TOKEN LIMIT
Last item completed: REQ-XXX
Next item to process: REQ-XXX
Items remaining: [n]
Resume instruction: Say "Act as DISCOVERY resume validation from REQ-XXX"
```

### Capability Summary
```
CAPABILITY SUMMARY
Total: EXISTS=[n] PARTIAL=[n] MISSING=[n]
HIGH risk resolved: [n] | Remaining as OQ: [n]
| REQ-ID | Requirement | Status | Evidence |
|--------|-------------|--------|----------|
| REQ-001 | [name] | EXISTS/PARTIAL/MISSING | [file:fn] |
```

### PLANNER-Ready Gate
For each MISSING DEC-ID, answer all four. Any NO → NEEDS_EXPANSION (fix before Phase 4B).
```
PLANNER-READY GATE: [Feature]_spec.md
DEC-001: names=YES constants=YES algorithm=YES signature=YES → PLANNER-READY
DEC-002: names=YES constants=NO  algorithm=YES signature=YES → NEEDS_EXPANSION
Overall: PLANNER-READY / NEEDS_EXPANSION
```

### Ledger Completeness Check
```
LEDGER COMPLETENESS CHECK
-------------------------
Items in this model's spec:        [n]
Items in second model's findings:  [n]
Total unique items in ledger:      [n]  ← must equal union of both
Agreements (Match ✓):              [n]
Conflicts:                         [n]
Only in this spec:                 [n]
Only in second model:              [n]
Sum check: [agreements + conflicts + only-A + only-B] = [n]  ← must equal total unique
```

### Discovery Gate
```
DISCOVERY GATE
HIGH risk unresolved: [n] | Blocked OQs: [n] | Unresolved CRITICAL CFs: [n]
Cross-model corrections absorbed: [n] | Cross-check: DONE / SKIPPED (risk acknowledged)
Verdict: GO / HOLD / REDO
```

## Cross-Model Absorption (Phase 5)
When user pastes VALIDATOR output: apply Rule A, build Rule D ledger, absorb per p4.md §Phase 5. If VALIDATOR not configured: load `workflow_01_discovery_crosscheck.md`.
