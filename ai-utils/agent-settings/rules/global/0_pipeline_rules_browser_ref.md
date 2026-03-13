---
trigger: manual
description: "Pipeline Browser Overrides — per-role upload checklists and browser-mode operating instructions. Load when setting up any browser session for DISCOVERY, VALIDATOR, FLOW_AUDITOR, PLANNER, IMPLEMENTER, DELTA, or PR_REVIEWER."
---

# Pipeline — Role Browser Overrides (Section 3)

> Companion to `0_pipeline_rules.md`. Load when starting a browser session for any pipeline role.

**Shared modules (always upload with any role):**
`violation_examples.md` · `output_blocks.md`
— These are referenced by `>` pointers in rule files. Without them, the agent cannot follow those pointers.

**IMPLEMENTER / DELTA / PR_REVIEWER also need:** `verification_checks.md`
— Contains Check A–D, Step 6.5, Step 6.6 definitions.

---

### VALIDATOR — load `workflow_02_validator.md` + `workflow_02_validator_ref.md`
Minimal required uploads: `0_analysis_rules.md` · `0_pipeline_rules.md` · `workflow_02_validator.md` · `workflow_02_validator_ref.md` · `[Feature]_spec.md` · `violation_examples.md` · `output_blocks.md`
> `workflow_02_validator_ref.md` contains Phases 1–3, check definitions, output sequence, and resumption — it is required for any analysis work.
Optional (only when it exists): previous spec version OR the document DISCOVERY ported from — if neither exists, upload spec alone.
Do NOT load: any other workflow files, codebase context, or project rules (unless findings touch those areas).
VALIDATOR auto-detects mode from the spec header `Source:` field. No source document is always valid — see workflow_02_validator.md.
VALIDATOR has no codebase access. Run in a completely separate session from DISCOVERY.

### FLOW_AUDITOR — load `workflow_06_flow_auditor.md` + `workflow_06_flow_auditor_ref.md`
Required uploads: `0_analysis_rules.md` · `0_pipeline_rules.md` · both workflow files · `FLOW_REGISTRY.md` · codebase `.ai_context.txt` · `violation_examples.md` · `output_blocks.md`.
> `workflow_06_flow_auditor_ref.md` contains all 10 check definitions, output templates, cross-reference ledger, and resumption contract — required for any audit work.
Variants: standard / `discovery only` / `audit only` / `full scan` / `resume from FLOW-[ID]`. Output: `flow_registry/audits/YYYYMMDD_AUDIT_FINDINGS.md`.
⚡ Browser: upload full source codebase context file — agent needs to trace call chains in actual source files.

### DISCOVERY — load `workflow_01_discovery.md`
Deferred loads (as instructed inside that file):
`workflow_01_discovery_p4.md` at Phase 3 end · `workflow_01_discovery_cf_ref.md` at Phase 4B · `workflow_01_discovery_ref.md` at Phase 6
Also upload: `violation_examples.md` · `output_blocks.md` · `discovery_spec_template.md`

⚡ Browser: no terminal commands · if context missing output `"Please upload .ai_context.txt"` · cross-model prompts in a markdown block for copy-paste.
⚡ Browser REDO: if re-running DISCOVERY on an existing feature, also upload the current `[Feature]_spec.md` — DISCOVERY uses it as the baseline to correct.

### PLANNER — load `workflow_02_planner.md`
Deferred: `workflow_02_planner_ref.md` before Phase 2 tasks · `workflow_02_planner_phase2_ref.md` when handling failures or re-entry.
Also upload: `violation_examples.md` · `output_blocks.md`

⚡ Browser: dry-run batch output as numbered list in response · code-level pre-read from uploaded context only.

### IMPLEMENTER — load `workflow_03_implementer.md` + `workflow_03_implementer_ref.md`
Also upload: `verification_checks.md` · `violation_examples.md` · `output_blocks.md`
⚡ Browser: upload most recent `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` (and companion `IMPL_P01.md`…`IMPL_P0n.md` if Split Mode: SPLIT) · output SEARCH/REPLACE blocks with `FILE:` header for manual apply · verification by re-reading uploaded context sections.
> Chunk files (`IMPL_P01.md`, `IMPL_P02.md`, …) are **fixed-name, not timestamped** — live in the same `pipeline\[Feature]\` folder as the plan.
> Large plan upload rule: for SPLIT mode, upload ONLY the current phase chunk file — not the full plan. For SINGLE FILE plans with >50 tasks, paste only the tasks for this session. A full plan exceeding token budget silently suppresses rules.

### DELTA — load `workflow_04_delta.md` + `workflow_04_delta_ref.md`
Also upload: `verification_checks.md` · `violation_examples.md` · `output_blocks.md`
⚡ Browser: upload most recent `YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md`, `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md`, and (if PR_REVIEWER has run) `YYYYMMDD_HHMM_05_REVIEW_REPORT.md` from `pipeline\[Feature]\` · output DELTA_PLAN.md content directly in chat.
> `workflow_04_delta_ref.md` contains the `04_DELTA_PLAN.md` template, DELTA-TASK format, and stage failure handling — load before writing output.

### PR_REVIEWER — load `workflow_05_pr_reviewer.md` + `workflow_05_pr_reviewer_ref.md`
Also upload: `verification_checks.md` · `violation_examples.md` · `output_blocks.md`
⚡ Browser: upload `[Feature]_spec.md` + most recent `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` + most recent `YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md` + `[Feature]_pr_diff.txt` + all project `.ai_context.txt` files. Generate the diff first: `tools\make_pr_diff.bat -Feature [Feature]`, then assemble the drop: `sync_and_drop.bat -Role PR_REVIEWER -Feature [Feature]`.
> `workflow_05_pr_reviewer_ref.md` contains the `05_REVIEW_REPORT.md` template and per-task format — load before writing any output.

