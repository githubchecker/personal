---
trigger: conditional
description: "Meta-governance rule for AI editing rules and workflows. Apply whenever modifying, creating, or reviewing any file in rules/ or workflows/ directories."
---

# Rule & Workflow Governance (AI Meta-Rule)

**SCOPE:** Apply whenever modifying, creating, reviewing, or deleting any file in `rules/` or `workflows/` directories. This file is the authoritative source for how the pipeline evolves.

---

## R1 — Hard File Size Limit (Canonical — No Redundant Headers Required)

**12 000 bytes maximum per file. No exceptions.**

This file is the single authoritative source for the 12k limit. Individual file banners are **optional** safety reminders — not the authoritative source. Do not add banners to files if not already present; do not require them as a compliance gate.

If a file must grow — two options (pick first applicable):
1. **Shared/reusable content** → extract to `modules/` with `trigger: on_demand`. Update all references per R4.
2. **Role-specific overflow** → create a `_ref.md` companion. Update all load instructions per R4.

After any size-critical edit: confirm with `(Get-Item "[file]").Length`.

Companion split decision:
- Primary file: role activation, core behavior, per-step protocol, status codes — everything always needed
- `modules/`: shared content used by 2+ roles (templates, checks, examples, output blocks)
- `_ref.md`: role-specific output formats, stage failure tables — load on demand by that role only

---

## R2 — Compact but Never Vague

Rules must be **both concise and unambiguous**. Two gates must both pass before a compaction is accepted:

**Gate 1 — Alternative Interpretation Test (specificity/vagueness):**
> Could an LLM with no prior context interpret the compacted statement differently and still claim it followed the rule? If YES — add back the disambiguating clause.

**Gate 2 — Compaction Losslessness Check (meaning/correctness):**
> List every distinct behavioral requirement in the original text. Confirm each one is still present — explicitly or implicitly — in the compacted version. If ANY requirement is absent: the compaction silently dropped behavior. Restore it.

Gate 2 catches what Gate 1 misses: text that is clear and unambiguous but simply no longer says everything the original said.

**Gate 3 — Minimal Compliance / Adversarial Test (hallucination prevention):**
> Play adversary: what is the laziest, most literal interpretation that still technically complies with this rule? If that minimum behavior produces acceptable output — the rule is correct. If minimum compliance produces wrong or incomplete output — the rule is under-specified. Tighten it.

Gate 3 catches what Gates 1 and 2 both miss: a rule can be unambiguous (Gate 1), complete (Gate 2), and still allow a technically-compliant minimal execution that produces wrong output.

Examples:
- Rule: `"grep for callers"` → Lazy: grep only the current file → **Gate 3 fail.** Fix: `"grep_search the FULL repo (all solution folders)"`
- Rule: `"log the result"` → Lazy: log `"done"` → **Gate 3 fail.** Fix: `"log with [file:line] citation for every checklist item"`
- Rule: `"verify the change"` → Lazy: glance at the diff → **Gate 3 fail.** Fix: `"read changed code and explicitly confirm every Verification Checklist criterion is met"`

Examples:
- ✅ Valid: `"grep full repo — undeclared callers → PARTIAL"` (unambiguous, nothing dropped)
- ❌ Invalid: `"check callers where needed"` (Gate 1 fail — ambiguous)
- ❌ Invalid: `"grep full repo — update callers"` when original also said *"log the grep result even when 0 callers found"* (Gate 1 passes, Gate 2 fails — requirement silently dropped)

**No paraphrasing of exact-match blocks (SEARCH/REPLACE, output templates, format strings):** Reproduce verbatim — never compact.

---

## R3 — Generic vs Project-Specific

Global rules (`rules/global/`) must apply to any repository, any tech stack.

- Project-specific patterns belong in `rules/project/[ProjectName]/`.
- Global rules may reference project rule filenames but must not embed project-specific logic as the authoritative source.
- When writing an example in a global rule: use a generic placeholder (e.g. `MyService.DoWork()`) rather than a real project class.

---

## R4 — Cross-Reference Integrity

When any stage/role/file is added, removed, or renamed, update ALL references:

| What changed | Must update |
|---|---|
| New stage (e.g. `07_ANALYST`) | `0_pipeline_rules.md` — Flow, Role->Workflow map, Quick Reference, Browser Overrides; `0_pipeline_ops_ref.md` — §7A, §7B; `sync_and_drop.ps1` Phases config (Files + needs_* flags); `PIPELINE_USAGE_GUIDE.md`; `BROWSER_SESSION_CONTINUATION_RULE.md` — update "Upload these:" section in §10 template if new role needs specific files |
| Stage removed | Same — remove all references. Dead references are hallucination bait. |
| Stage renamed | Same — rename atomically everywhere. |
| New artifact type | `sync_and_drop.ps1` ArtifactRegex + `needs_*` in Phases config for affected roles; `0_pipeline_ops_ref.md` §7A, §7B, §7C |
| New `_ref.md` companion | Primary file load instruction; `sync_and_drop.ps1` Phases.Files for affected roles; `0_pipeline_rules.md` upload table; `PIPELINE_USAGE_GUIDE.md` |
| New global rule file | `sync_and_drop.ps1` Phases.Files for all roles that need it; `0_pipeline_rules.md` upload table |
| Content extracted to `modules/` | (1) Source file: replace inline content with `> Load modules/[name].md` pointer; (2) grep for **every workflow/rule file that references the moved section by name** (e.g., `§"Output Format"`) — update each to point to the module; (3) `sync_and_drop.ps1` Phases.Files for all roles that use this content; (4) `0_pipeline_rules_browser_ref.md` per-role upload list; (5) Dead reference grep: zero remaining references to old inline location |

**Dead reference check (mandatory):** Before marking DONE, `grep_search` for the old name across all `rules/` and `workflows/` files. Zero remaining references required.

**Conflict resolution:** When two rules conflict, the more specific rule wins.
Specificity order: project rule > global rule; workflow file > rule file.
Same specificity: the rule in the more recently modified file wins.
Ambiguous specificity: surface the conflict — never resolve silently.

> Mandatory conflict surfacing block: see `modules/output_blocks.md` §"Rule Conflict Surfacing Block".
> Output the RULE CONFLICT DETECTED block immediately before applying any resolution.
> A conflict resolved without this block is a governance violation under R6.

---

## R5 — Context Window Management (Critical for AI)

The context window is finite and precious. Violating this rule causes silent context loss — the most dangerous failure mode.

**Trigger discipline — three tiers:**

| Trigger | Meaning | Examples |
|---|---|---|
| `always_on` | Loaded in every session, every role, automatically | `0_analysis_rules.md`, `0_coding_rules.md` |
| `conditional` | Loaded only when a specific condition is met | `0_rule_governance.md` (only when editing rules/workflows) |
| `manual` | Loaded on explicit user or role instruction only | All workflow files |

Adding a file to `always_on` costs context tokens in every session. Only add to `always_on` if the rule is genuinely needed in ALL roles ALL the time.

**On-demand loading discipline for workflow files:**

Workflow files must never all be loaded simultaneously. Each role loads only:
1. Its own primary workflow file (e.g. `workflow_03_implementer.md`)
2. Its companion `_ref.md` immediately before writing output (not on activation)
3. Deferred files only at the exact step that requires them (e.g. `workflow_01_discovery_p4.md` loaded at Phase 3 end, not on activation)

**Context re-read rule (turn 21+):** At turn 21 or later, re-read the relevant section before applying any of the following:
- Any Rule A–F from `0_analysis_rules.md`
- Any CF GATE criterion from a spec or plan
- Security rules (0_coding_rules.md Rule 6) or Reference Integrity (Rule 3)
Output: `"Turn [N] — re-read [rule/section] confirmed."` Omitting this output at turn 21+ is a protocol violation.

**Context budget for browser sessions (guideline):**

| Content type | Max tokens | Rule |
|---|---|---|
| Rule/workflow files | ~30k | Only role-specific files |
| AI context (.ai_context.txt) | ~100k | One per project needed |
| Pipeline artifacts (plan/log/delta) | ~30k | Latest only |
| Total target | ~160k | Leave 40k for response |

If uploads would exceed this budget: tell the user which file to drop and why.

---

## R6 — Anti-Hallucination for Rule Authoring

- Never reference a file path, role trigger, or artifact filename without first confirming it exists in the repo.
- Never claim a rule is satisfied without citing `[file:line]` evidence.
- Never add a rule that contradicts an existing rule without explicitly marking the old rule as superseded with the reason.
- Never write a rule that requires knowing facts only available in session (e.g. "check the last task you ran") — rules must be stateless.
- Never use open-ended qualifiers: "as needed", "where appropriate", "if relevant" — always replace with a testable condition.

---

## R7 — Character and Formatting Economy

Every byte counts. Rules:

- No decorative emoji, Unicode box-drawing, or section dividers beyond `---`. Use only `>`, `-`, `|` for structure.
- No filler phrases: "This is important", "Note that", "Please ensure", "As mentioned above".
- No restating what the next line already says (redundant headers).
- No commented-out code blocks kept as examples unless they are the only way to document format.
- Code blocks in rule files: use only for exact-match templates, CLI commands, or format strings. Never for prose examples.
- Tables: prefer over bullet lists when there are 3+ parallel items with 2+ attributes each.

---

## R8 — Browser Pack Integrity

Any change to which files an AI role needs: edit the `Phases` config dict at the top of `sync_and_drop.ps1`:
- `Files` array — which rule/workflow files go in the browser pack
- `needs_*` flags — which pipeline artifacts go in the drop folder

Single source of truth. No second file to keep in sync. Check after every R4 update.

---

## R9 — Self-Application Audit

After editing any rule or workflow file, run before marking DONE:

```
GOVERNANCE AUDIT
[ ] File size ≤ 12 000 bytes: (Get-Item "[file]").Length = [n]
[ ] R2 Gate 1 — Alternative Interpretation Test: no valid alternative reading exists
[ ] R2 Gate 2 — Losslessness Check: every behavioral requirement in original is present in result
[ ] R2 Gate 3 — Minimal Compliance Test: laziest literal interpretation produces acceptable output
[ ] R6: no open-ended qualifiers ("as needed", "if relevant", "where appropriate")
[ ] R7: no filler phrases, decorative emoji, or redundant prose
[ ] R3: project-specific content in rules/project/, not rules/global/
[ ] R4: dead reference grep returned 0 hits for any removed/renamed/extracted content
[ ] R4: all back-references updated (pipeline_rules, pipeline_ops_ref, sync_and_drop.ps1 Phases config, PIPELINE_USAGE_GUIDE)
[ ] R4: browser_ref.md per-role upload lists include any new module files
[ ] R4: workflow files that reference moved content by §section name updated to point to new location
[ ] R5: trigger tier correct (always_on / conditional / manual)
[ ] R5: deferred loads kept deferred — not promoted to always-load
[ ] R8: sync_and_drop.ps1 Phases config is the single source (Files + needs_* flags in one entry per role)
```
