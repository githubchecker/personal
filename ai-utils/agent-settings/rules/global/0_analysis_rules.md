---
trigger: always_on
description: exhaustive_chunked_analysis_protocol
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Shared/reusable content → extract to `modules/` (preferred). Role-specific overflow → split into a `_ref.md` companion. Never exceed this limit.

# Global Exhaustive Analysis Protocol

**PROBLEM THIS SOLVES:** LLMs naturally compress and skip items when analyzing large inputs,
producing summaries instead of complete verdicts. Silent gaps require expensive manual
back-and-forth to discover. This protocol makes skipping structurally impossible and
gaps visually obvious — for any input type, in any context, pipeline or not.

**SCOPE:** Applies universally — to any role, any session, any input type — whenever:
- The input contains more than 5 discrete items to analyze, verify, or cross-check
- A user sends any document, file, or pasted list for review or audit
- Two sources are being compared (any cross-model, cross-document, or cross-version review)
- A batch run from a previous session is being resumed

This protocol is not limited to pipeline roles. It applies to any analysis task regardless
of context — pipeline, ad-hoc review, document audit, or code inspection.

---

## RULE A — Inventory Declaration (Before Any Analysis Begins)

Before processing any list, document, or set of outputs, you MUST declare:

```
INVENTORY DECLARATION
─────────────────────
Source: [filename, description, or "user input"]
Total items identified: [exact count]
Batch size: 8
Total batches: [ceil(count / 8)]
Starting: Batch 1 of [n]
```

If you cannot count the items (e.g., a free-form document), you MUST break it into
named logical blocks first and declare those blocks as your inventory.

**Why this matters:** Declaring the count upfront creates a commitment. If your analysis
ends before reaching that count, the gap is immediately visible to both you and the human.

---

## RULE B — Batch Processing with Hard Pause (Max 8 Items Per Batch)

Process a maximum of **8 items per response**. After completing item 8, you MUST stop
and output this exact block — no exceptions, even if you feel you could continue:

```
<<<BATCH [n] COMPLETE>>>
Items processed this batch: [x] through [y]
Items by ID this batch: ITEM-[n1], ITEM-[n2], … ITEM-[ny] ← missing IDs visible here
Items remaining: [z]
Running gap count: [number of items with issues found so far]
───────────────────────────────────────────────
Reply CONTINUE to process Batch [n+1]: items [y+1] through [y+8]
```

Do not process item 9 until the human replies "Continue" or "CONTINUE".

**Why 8, not 10:** 8 items leaves buffer in the output window for thorough per-item
analysis. At 10+, the model starts compressing the later items to reach the end.

---

## RULE C — Per-Item Mandatory Verdict Format

Every single item MUST receive an explicit written verdict using this format:

```
### ITEM-[NNN]: [Name or short description]
**Source line/section:** [where in the document]
**Status:** PASS | GAP | CONFLICT | PARTIAL | NEEDS_HUMAN
**Finding:** [1–3 sentences. What was found. Never omit this field.
  For GAP or CONFLICT: must include (a) exact source location (file:line or document section),
  (b) what specifically is wrong, (c) consequence if unresolved. A one-sentence Finding with
  no location for GAP/CONFLICT status is a protocol violation.]

**Action Required:** [specific next step, or NONE]
```

Rules:
- `PASS` is not silence. PASS must still be written explicitly.
- `NONE` is not acceptable for Action Required when Status is GAP or CONFLICT.
- If an item is ambiguous, Status = NEEDS_HUMAN with a specific question in Action Required.
- **Omission of any item is a protocol failure**, equivalent to a wrong answer.

---

## RULE D — Cross-Source Review Protocol

**Scope:** Rule D applies when two *complete documents* are compared holistically — e.g., a spec vs a source document, two spec versions, a plan vs a review report. Rule D does NOT apply to per-task SEARCH/REPLACE block matching (IMPLEMENTER) or per-task log-vs-diff checking (PR_REVIEWER). Those are governed by per-item verdict format (Rule C) applied at the task level, not the document level.

When comparing two sources — two model outputs, two document versions, two reports,
a spec vs. codebase, or any other pair — apply this sub-protocol:

### Step D1 — Load Both Sources Completely Before Writing Anything
State: `"Loading [Source A] and [Source B]. Will not begin writing until both are fully mapped."`

### Step D2 — Build a Cross-Reference Ledger First
Before writing any verdicts, output this table covering EVERY item from both sources:

**Ledger granularity rules:**
- Structured docs (spec with IDs): items = all named IDs (REQ-NNN, BUG-NNN, DEC-NNN, CF-NNN, OQ-NNN) — one row per ID, prefixed with type
- Unstructured docs: items = H2-level section headings — one row per heading
- Use ONE ledger per document pair — do not split by ID type

```
CROSS-REFERENCE LEDGER
──────────────────────
| Item ID | Present in A | Present in B | Match | Conflict | Only in A | Only in B |
|---------|-------------|-------------|-------|----------|-----------|-----------|
| ITEM-001|      ✓      |      ✓      |   ✓   |          |           |           |
| ITEM-002|      ✓      |      ✓      |       |    ✓     |           |           |
| ITEM-003|      ✓      |             |       |          |     ✓     |           |
| ITEM-004|             |      ✓      |       |          |           |     ✓     |
```

This ledger must be complete before any detailed analysis begins.

### Step D3 — Analyze Conflicts and Gaps Only (Not Agreements)
After the ledger, process only rows marked CONFLICT, Only in A, or Only in B.
Agreements (both ✓, Match ✓) are confirmed by the ledger itself — no further text needed.

### Step D4 — Final Completeness Check
After all batches complete, output:

```
COMPLETENESS CHECK
──────────────────
Total items in ledger: [n]
Agreements confirmed: [n]
Conflicts analyzed: [n]
Gaps (Only in A): [n]
Gaps (Only in B): [n]
Items with NEEDS_HUMAN: [n]
Total accounted for: [sum — must equal ledger total]
```

If Total accounted for ≠ ledger total, identify missing items before proceeding.

---

## RULE E — Negative Confirmation is Mandatory

Silence is never acceptable as a verdict. If an item requires no action, you must write:

```
### ITEM-[NNN]: [Name]
**Status:** PASS
**Finding:** Reviewed. No issues found. [One sentence of evidence.]
**Action Required:** NONE
```

"I didn't mention it" is indistinguishable from "I skipped it." Only explicit PASS verdicts
are verifiable.

> Violation examples: see `modules/violation_examples.md` §"Rule E — Silence as PASS"

---

## RULE F — Resumption Contract (For Interrupted Analysis)

When a batch run is interrupted (token limit, session end, user pause), the next session
MUST begin with:

```
RESUMPTION CONTRACT
───────────────────
Previous session completed: Batch [n], Items [x] through [y]
Verified complete: [list item IDs or range]
Resuming: Batch [n+1], Items [y+1] through [y+8]
Human confirmation required: Does this resumption point match your records? (yes/no)
```

Do not proceed until the human confirms. This prevents silent re-analysis or skipping.

---

## WHEN THIS PROTOCOL APPLIES

| Trigger | Rules |
|---------|-------|
| Any input with >5 discrete items to analyze | A, B, C, E |
| User sends any document or file for review or audit | A, B, C, E |
| User pastes any list (requirements, tasks, bugs, rules, code items) | A, B, C, E |
| Comparing any two sources (models, documents, versions, spec vs code) | A, B, C, D, E |
| Resuming any interrupted analysis | F first, then A–E |
| Single-item questions or quick lookups | None — normal response |

---

## ANTI-PATTERNS THAT INVALIDATE THIS PROTOCOL

These outputs mean the protocol was violated and analysis must restart:

- `"Overall, the document looks good with a few gaps..."` → No inventory declared
- `"Most items match between the two sources..."` → No cross-reference ledger built
- `"See above for details"` → Items not individually verdicted
- Analysis that ends before reaching the declared inventory count
- A batch that contains more than 8 items
- Any item without an explicit Status field
