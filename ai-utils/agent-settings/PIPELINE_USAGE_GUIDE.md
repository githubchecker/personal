# Pipeline Usage Guide
**Who this is for:** You (the developer) + any AI agent that needs to understand the system.

---

## Part 0 — Daily Operations Reference
> **Read this first every day.** Everything else in this guide is reference detail.
> This section answers the questions that come up on every single feature run.

---

### 0A. How the Whole Pipeline Flows — The Master Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE — FULL FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

  YOU                  AI ROLE              OUTPUT FILE             FOLDER
  ───                  ───────              ───────────             ──────

  "Act as DISCOVERY"
  ──────────────────►  DISCOVERY      →    [Feature]_spec.md    →  specs\
                       (Claude/Gemini)      Gate must = GO
                            │
                            ▼  (optional but recommended)
  "Act as VALIDATOR"
  ──────────────────►  VALIDATOR      →    corrections in chat      (no file)
                       (different model)    paste back to DISCOVERY
                            │
                            ▼
  "Act as PLANNER"
  ──────────────────►  PLANNER        →    02_IMPLEMENTATION_PLAN.md  pipeline\[F]\
                       (Claude/Gemini)      + IMPL_P01.md …           (if split)
                            │
                            ▼
  "Act as IMPLEMENTER"
  ──────────────────►  IMPLEMENTER    →    03_IMPLEMENTATION_LOG.md   pipeline\[F]\
                       (Gemini Flash        ONE file, always
                        or any model)       covers ALL tasks
                            │
                  ┌─────────┴──────────┐
                  │                    │
              All COMPLETED?      Any FAILED /
                  │               SKIPPED?
                  ▼                    │
              DONE ✓                   ▼
                  ┌─────────┴──────────┐
                  │                    │
              All COMPLETED?      Any FAILED /
                  │               SKIPPED?
                  ▼                    │
              DONE ✓                   ▼
                            "tools\make_pr_diff.bat -Feature [F]"
                            "sync_and_drop.bat -Role PR_REVIEWER -Feature [F]"
                            "Act as PR_REVIEWER"
                            ──────────────────────►  PR_REVIEWER  →  05_REVIEW_REPORT.md pipeline\[F]\
                                                     reviews git diff   FABRICATED / MISSING /
                                                     vs log claims      VERIFIED verdicts
                                                          │
                                                          ▼
                            "Act as DELTA"
                            ──────────────►  DELTA         →    04_DELTA_PLAN.md   pipeline\[F]\
                                             (reasoning          only failed tasks
                                              model)             COMPLETED dropped
                                                  │
                                                  ▼
                                          "Act as IMPLEMENTER"
                                          (reads delta plan,
                                           NOT original)
                                                  │
                                    ┌─────────────┴──────────────┐
                                    │                             │
                                All COMPLETED?          Still failures?
                                    │                             │
                                    ▼                    Loop max 3×
                                DONE ✓                   then human decision
                                                         (REDUCE SCOPE requires
                                                         DEFERRED_CF for CRITICAL CFs)

  ──────────────────────────────── OPTIONAL ─────────────────────────────────

   "Act as FLOW_AUDITOR"           (run on any existing codebase / flow list, e.g., ENCRYPT-01)
   ──────────────────►  FLOW_AUDITOR  →  AUDIT_FINDINGS.md   flow_registry\audits\
                        (reasoning           one file per audit
                         model)              source-first batch analysis
                             │
                             ▼
                         Gaps → feeds DISCOVERY / PLANNER as new feature
                         or standalone AuditFix pipeline run
```

---

### 0B. The 3 Folders — Where Everything Lives

```
Docs\TradeInDepthPro\
│
├── specs\                        ← GIT COMMITTED
│   └── MVP1_spec.md                Written by DISCOVERY only.
│                                   Never overwrite — version it (spec_v2.md).
│
├── pipeline\                     ← GIT COMMITTED
│   └── MVP1\                       One subfolder per feature, flat inside.
│       ├── 20260226_1340_02_IMPLEMENTATION_PLAN.md   ← PLANNER final output
│       ├── IMPL_P01.md                               ← chunk 1 (fixed name, no timestamp — only if split)
│       ├── IMPL_P02.md                               ← chunk 2 (fixed name, no timestamp — only if split)
│       ├── 20260226_1520_03_IMPLEMENTATION_LOG.md    ← IMPLEMENTER output (run 1)
│       ├── 20260226_1700_05_REVIEW_REPORT.md         ← PR_REVIEWER output (review of run 1)
│       ├── 20260226_1720_04_DELTA_PLAN.md            ← DELTA output (loop 1)
│       └── 20260226_1800_03_IMPLEMENTATION_LOG.md    ← IMPLEMENTER output (run 2)
│           ↑
│           Newest YYYYMMDD_HHMM_ prefix per type = "latest"
│           Alphabetical = chronological. No pointer file needed.
│
└── continuation\                 ← GIT IGNORED — scratch space, flat
    └── anything not yet final:
        mid-run dumps, partial outputs, command output, notes
        Named however — pipeline.py adds the header automatically.
```

Decision rule:
```
Role finished completely → pipeline\[Feature]\   (via pipeline.py save)
Anything else           → continuation\          (via pipeline.py dump, or just drop it there)
```

---

### 0C. PLANNER — Split Mode vs Token Limit (Two Different Things)

These look similar but are completely different situations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SPLIT MODE — a deliberate design decision, not a crash                     │
└─────────────────────────────────────────────────────────────────────────────┘

PLANNER evaluates BEFORE writing anything:
  ≤30 tasks AND ≤8 LARGE tasks  →  SINGLE FILE (everything in 02_IMPLEMENTATION_PLAN.md)
  >30 tasks OR  >8 LARGE tasks  →  SPLIT MODE  (index + phase files)

PLANNER announces upfront:
  "SPLIT MODE: 45 tasks — writing index + IMPL_P01.md … IMPL_P04.md"

Files produced (all saved to pipeline\MVP1\):
  02_IMPLEMENTATION_PLAN.md    ← master index — ALWAYS exists, always the anchor
  IMPL_P01.md                  ← phase 1 full tasks
  IMPL_P02.md                  ← phase 2 full tasks
  IMPL_P03.md                  ← phase 3 full tasks

  pipeline.py save  →  master plan only
  manual copy       →  chunk files (IMPL_P0n.md are fixed-name, not timestamped)


┌─────────────────────────────────────────────────────────────────────────────┐
│  TOKEN LIMIT MID-RUN — an accident, handled by dump + resume               │
└─────────────────────────────────────────────────────────────────────────────┘

PLANNER wrote 3 of 5 chunks then hit token limit:
  → Dump whatever is in chat to continuation\ (paste or pipeline.py dump)
  → New session: upload dump + say "Act as PLANNER resume"
  → PLANNER reads Resumption Contract, skips completed chunks, continues
  → Master index 02_IMPLEMENTATION_PLAN.md is ONLY finalized when ALL
    phase files are complete — it is ALWAYS generated before you save anything

RULE: 02_IMPLEMENTATION_PLAN.md is ALWAYS generated. It is the anchor. Nothing works without it.
```

---

### 0D. Moving PLANNER Output to pipeline\ — Exact Steps

After PLANNER finishes (whether single file or split):

```
Step 1 — Put all files in continuation\ (named however you like)
          continuation\
          ├── my_plan.md          ← the master plan
          ├── phase1.md           ← chunk 1
          └── phase2.md           ← chunk 2

Step 2 — Tell local agent (Gemini):
          "Move my PLANNER output to pipeline\.
           Run:
             python pipeline.py save --feature MVP1 --type plan --file continuation\my_plan.md
           Then copy directly (NOT through pipeline.py save):
             pipeline\MVP1\IMPL_P01.md  ← from phase1.md
             pipeline\MVP1\IMPL_P02.md  ← from phase2.md

           Chunk files use fixed names (IMPL_P0n.md) and are never timestamped.
           Only the master plan goes through pipeline.py save."

Step 3 — Verify:
          python pipeline.py status --feature MVP1
```

---

### 0E. IMPLEMENTER — How It Handles Split Plans

IMPLEMENTER never produces chunks. It always writes ONE log file covering everything.

```
Plan is SINGLE FILE:
  IMPLEMENTER reads 02_IMPLEMENTATION_PLAN.md
  Executes all tasks inline
  Writes ONE 03_IMPLEMENTATION_LOG.md

Plan is SPLIT:
  IMPLEMENTER reads 02_IMPLEMENTATION_PLAN.md (index)
      sees TASK-P01 stub → you upload IMPL_P01.md → completes all tasks in it
      sees TASK-P02 stub → you upload IMPL_P02.md → completes all tasks in it
      sees TASK-P03 stub → you upload IMPL_P03.md → completes all tasks in it
  Writes ONE 03_IMPLEMENTATION_LOG.md covering every task across all phases

Output is always a single file. Never chunked.
```

---

### 0F. PR_REVIEWER — When, Who, What

```
+-----------------------------------------------------------------------------+
|  PR_REVIEWER runs ONCE after IMPLEMENTER, BEFORE DELTA                     |
+-----------------------------------------------------------------------------+

IMPLEMENTER finishes → writes 03_IMPLEMENTATION_LOG.md
        |
        +-- Any FAILED / SKIPPED / PARTIAL? → you MUST run PR_REVIEWER
        |
        v
YOU run locally:
  tools\make_pr_diff.bat -Feature [Feature]          <- generates git diff vs stable baseline
  sync_and_drop.bat -Role PR_REVIEWER -Feature [Feature]  <- assembles drop folder
        |
        v
YOU upload browse-drop\[Feature]_06_PR_REVIEWER\ to new Claude session
Say: "Act as PR_REVIEWER"
        |
        v
PR_REVIEWER (reasoning model) reads:
  +-- [Feature]_spec.md           always -- original requirements + CF constraints
  +-- 02_IMPLEMENTATION_PLAN.md   always -- what PLANNER said to do
  +-- 03_IMPLEMENTATION_LOG.md    always -- what IMPLEMENTER claims it did
  +-- [Feature]_pr_diff.txt       always -- GROUND TRUTH: what actually changed in git
  +-- [Feature]_pr_diff_stat.txt  always -- summary of changed files
        |
        v
PR_REVIEWER writes: 05_REVIEW_REPORT.md
  For every task in the log: VERIFIED / FABRICATED / PARTIAL_VERIFIED / MISSING /
  CF_VIOLATED / WRONG_IMPL / BROKEN_CALLER / CALLER_RISK / VERIFIED_WITH_WARNINGS
  Go/No-Go gate block for DELTA
        |
        v
YOU say: "Act as DELTA"
  DELTA reads review report + log + plan
  FABRICATED verdict overrides COMPLETED log status (P0 priority)
  MISSING tasks are added as new DELTA-TASKs
```

**Why PR_REVIEWER exists:** IMPLEMENTER runs in browser mode without codebase access. It cannot
verify its own SEARCH/REPLACE blocks were applied correctly. It trusts Gemini Flash applied them
and logs COMPLETED. PR_REVIEWER reads the actual git diff to verify these claims forensically.
A FABRICATED verdict = IMPLEMENTER logged COMPLETED but the code change is absent from git.

---

### 0H. DELTA — When, Who, What

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DELTA runs ONCE per IMPLEMENTER run, AFTER it finishes, ONLY IF needed    │
└─────────────────────────────────────────────────────────────────────────────┘

IMPLEMENTER finishes → writes 03_IMPLEMENTATION_LOG.md
        │
        ├── All COMPLETED? ──────────────────────────► DONE. Delta never runs.
        │
        └── Any FAILED / SKIPPED / PARTIAL?
                │
                ▼
        YOU say: "Act as DELTA"
                │
                ▼
        DELTA (reasoning model — NOT Flash) reads:
          ├── 02_IMPLEMENTATION_PLAN.md   always — original intent + REQ-IDs
          ├── 04_DELTA_PLAN.md            only on Loop 2+ — previous delta
          └── 03_IMPLEMENTATION_LOG.md   newest timestamp — what just happened
                │
                ▼
        DELTA writes: 04_DELTA_PLAN.md
          Only the failed/skipped tasks (with fixed SEARCH blocks)
          COMPLETED tasks permanently dropped — never appear again
                │
                ▼
        YOU say: "Act as IMPLEMENTER"
          reads 04_DELTA_PLAN.md (not the original)
          writes a NEW 03_IMPLEMENTATION_LOG.md
                │
                ├── All done? ─────────────────────── DONE ✓
                └── Still failures? → loop (max 3 total)
                                       after loop 3 → human decision menu


Concrete loop sequence example:
─────────────────────────────────
Loop 1:
  IMPLEMENTER reads  02_IMPLEMENTATION_PLAN.md
  Writes  20260226_1520_03_IMPLEMENTATION_LOG.md  (15 done, 3 failed, 2 skipped)
  YOU: "Act as DELTA"
  DELTA reads plan + log
  Writes  20260226_1600_04_DELTA_PLAN.md          (5 tasks only)

Loop 2:
  IMPLEMENTER reads  04_DELTA_PLAN.md
  Writes  20260226_1700_03_IMPLEMENTATION_LOG.md  (4 done, 1 still failed)
  YOU: "Act as DELTA"
  DELTA reads original plan + newest delta + newest log
  Writes  20260226_1730_04_DELTA_PLAN.md          (1 task)

Loop 3:
  IMPLEMENTER reads newest 04_DELTA_PLAN.md → still fails
  DELTA outputs Post-Loop-3 Human Review Block
  Options: (A) Resume  (B) Reduce scope  (C) Replan  (D) Abandon  (E) Env fix
```

---

### 0I. Browser Claude + Local Gemini Flash — Full Handoff

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Claude (browser) = IMPLEMENTER brain  |  Gemini Flash (local) = hands     │
└─────────────────────────────────────────────────────────────────────────────┘

YOU upload to Claude (browser):
  browser_packs\04_IMPLEMENTER\ + context snapshot + plan file(s)
  Say: "Act as IMPLEMENTER"

Claude outputs one task at a time:
  FILE: src/module/Service.cs
  <<<SEARCH
  [verbatim existing code — 3+ lines context]
  <<<END>>>
  <<<REPLACE
  [new code]
  <<<END>>>

YOU paste to Gemini Flash:
  "Apply this SEARCH/REPLACE to the file exactly as written."
  Flash applies — no design decisions, pure mechanical application

YOU run locally:  git diff  or  run_agent.bat --changes
  Paste relevant diff back to Claude

Claude reads diff → marks task COMPLETED / PARTIAL / FAILED → next task

If Claude hits token limit mid-run:
  Claude logs remaining tasks SKIPPED ("Token limit at TASK-XXX")
  Claude outputs log so far with pipeline header pre-filled
  YOU save → pipeline.py dump → new Claude session → resume
  New Claude reads dump header → resumes from exact task

When all tasks done:
  Claude outputs complete 03_IMPLEMENTATION_LOG.md with header
  YOU save to pipeline\MVP1\YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md
  Tell local Gemini: "pipeline.py save --feature MVP1 --type log --file [path]"
```

---

### 0J. 6 Commands You Use Every Day

```
# Role just finished — archive the output:
python pipeline.py save --feature MVP1 --type plan|log|delta --file path	o\output.md

# Starting a new role — find which file to load:
python pipeline.py find --feature MVP1 --type plan|log|delta

# Token limit hit or partial output — save mid-run to continuation\:
python pipeline.py dump --feature MVP1 --role IMPLEMENTER --file path\dump.md ^
                        --contains "Tasks 1-15 done" --resume-from TASK-016

# Find the latest dump to resume from:
python pipeline.py dump-find --feature MVP1

# After moving or renaming a file — prove content unchanged:
python pipeline.py diff --old old/path/file.md --new D:/repo/new/path/file.md

# See everything at a glance:
python pipeline.py status --feature MVP1
```

---

## Part 1 — The Big Picture

```
DISCOVERY → VALIDATOR → PLANNER → IMPLEMENTER → PR_REVIEWER → DELTA (if needed)
"What to build"  "Is it right?"  "How to build it"  "Build it"  "Verify it"  "Fix what broke"
```

**Roles** = what job the AI is doing.
**Rules** = how it behaves during any job. Always active.
**Workflow files** = the detailed instructions for each role. Load only when that role is active.

The pipeline is designed so each stage gates the next. You cannot skip DISCOVERY and go straight to PLANNER — PLANNER needs a spec to read. You cannot skip PLANNER and go straight to IMPLEMENTER — IMPLEMENTER needs a task plan. The gates exist to prevent expensive mistakes.

---

## Part 2 — Agent Mode vs Browser Mode

### Agent Mode (Gemini in Cursor / Windsurf / IDE)
Rules with `trigger: always_on` load automatically. You do nothing — just activate a role and work.

### Browser Mode (Google AI Studio / Claude.ai / any web chat)
No automatic loading. **Upload every file manually before typing anything.**
The AI cannot see any file you have not explicitly uploaded in this session.

**Fastest upload method — pre-built phase packs (see Part 10 for full details):**
Run `sync_and_drop.bat (internally)` once (or after any rule change) to produce `browser_packs\` folders:
```
agent-settings\
  browser_packs\
    01_DISCOVERY\     ← select-all + upload, then say "Act as DISCOVERY"
    02_VALIDATOR\     ← select-all + upload (separate session), then "Act as VALIDATOR"
    03_PLANNER\       ← select-all + upload, then "Act as PLANNER"
    04_IMPLEMENTER\   ← select-all + upload, then "Act as IMPLEMENTER"
    05_DELTA\         ← select-all + upload, then "Act as DELTA"
    06_PR_REVIEWER\   ← select-all + upload + diff files, then "Act as PR_REVIEWER"
    07_FLOW_AUDITOR\  ← select-all + upload + FLOW_REGISTRY.md, then "Act as FLOW_AUDITOR"
    00_FULL_SESSION\ ← all roles in one session (200K+ context only)
```
Each folder contains a `README.md` telling you exactly what additional files to upload (spec, context snapshot, etc.) and the exact trigger phrase to use.

---

## Part 3 — Minimal File Sets Per Role

> **Why minimal?** Every uploaded file consumes token budget. Loading workflow files for roles you are not using wastes context and can cause the AI to confuse instructions from different stages.

### Full session (DISCOVERY → PLANNER → IMPLEMENTER → DELTA in one session)
```
0_pipeline_rules.md          ← always
0_analysis_rules.md          ← always
0_coding_rules.md            ← always
0_context_rules.md           ← always
1_naming_conventions.md      ← always (project rules)
2_webview2_standards.md      ← always (project rules)
3_infrastructure_security.md ← always (project rules)
4_workflow_standards.md      ← always (project rules)
workflow_01_discovery.md     ← DISCOVERY
workflow_01_discovery_p4.md  ← DISCOVERY
workflow_01_discovery_cf_ref.md ← DISCOVERY
workflow_01_discovery_ref.md ← DISCOVERY
workflow_02_planner.md       ← PLANNER
workflow_02_planner_ref.md   ← PLANNER
workflow_02_planner_phase2_ref.md ← PLANNER (failure handling)
workflow_03_implementer.md   ← IMPLEMENTER
workflow_03_implementer_ref.md ← IMPLEMENTER (output templates)
workflow_04_delta.md         ← DELTA
workflow_04_delta_ref.md     ← DELTA (required — output templates)
[your .ai_context.txt]       ← your codebase snapshot
```

### DISCOVERY only (requirement gathering + spec writing)
```
0_pipeline_rules.md
0_analysis_rules.md
0_coding_rules.md
0_context_rules.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_01_discovery.md          ← Phase 1–3 (load on activation)
workflow_01_discovery_p4.md       ← Phase 4–6 (AI loads at Phase 3 end — upload upfront)
workflow_01_discovery_ref.md      ← Format strings (AI loads at Phase 3 end — upload upfront)
workflow_01_discovery_cf_ref.md   ← CF scan (AI loads at Phase 4B — upload upfront)
workflow_01_discovery_crosscheck.md ← Fallback manual prompt if VALIDATOR not configured
[your .ai_context.txt]
```
> **Browser mode shortcut:** Use `browser_packs\01_DISCOVERY\` — select-all and upload.

### VALIDATOR only (second model cross-check — SEPARATE session)
```
0_pipeline_rules.md          ← mandatory (role context, routing)
0_analysis_rules.md          ← mandatory (Rules A–F — full analysis protocol)
0_coding_rules.md            ← for code correctness checks in DEC-IDs and §13 blocks
1_naming_conventions.md      ← for identifier naming correctness
3_infrastructure_security.md ← for security architecture decisions
workflow_02_validator.md     ← the VALIDATOR role file
workflow_02_validator_ref.md ← the VALIDATOR reference (check definitions, output format)
[Feature]_spec.md            ← the spec DISCOVERY just produced
[source document]            ← e.g. requirements.md, architect report
```
Do NOT upload: `0_context_rules.md`, `2_webview2_standards.md`, `4_workflow_standards.md`,
discovery workflow files, planner, implementer, delta, or your codebase context.
VALIDATOR has no codebase access by design — extra files only waste token budget.
> **Browser mode shortcut:** Use `browser_packs\02_VALIDATOR\` — select-all and upload, then additionally upload the spec and source document.

### PLANNER only (task plan generation — after spec is ready)
```
0_pipeline_rules.md  0_analysis_rules.md  0_coding_rules.md  0_context_rules.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_02_planner.md
workflow_02_planner_ref.md
[Feature]_spec.md            ← the spec from DISCOVERY
[your .ai_context.txt]
```

### IMPLEMENTER only (execution — after plan is ready)
```
0_pipeline_rules.md  0_analysis_rules.md  0_coding_rules.md  0_context_rules.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_03_implementer.md  workflow_03_implementer_ref.md
[Feature]_spec.md
YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md  (most recent — highest timestamp)
IMPL_P01.md … IMPL_P0n.md               (only if plan header shows Split Mode: SPLIT)
[your .ai_context.txt]
```

### DELTA only (failure triage — after implementer run)
```
0_pipeline_rules.md  0_analysis_rules.md  0_coding_rules.md  0_context_rules.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_04_delta.md  workflow_04_delta_ref.md
[Feature]_spec.md
YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md  (most recent — highest timestamp)
YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md   (most recent — highest timestamp)
YYYYMMDD_HHMM_05_REVIEW_REPORT.md        (most recent -- if PR_REVIEWER has run, optional but recommended)
[your .ai_context.txt]
```

### PR_REVIEWER only (forensic review — after implementer run, before DELTA)
```
0_pipeline_rules.md  0_analysis_rules.md  0_coding_rules.md  0_context_rules.md
0_pipeline_ops_ref.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_05_pr_reviewer.md  workflow_05_pr_reviewer_ref.md
[Feature]_spec.md
YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md  (most recent -- highest timestamp)
YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md   (most recent -- highest timestamp)
[Feature]_pr_diff.txt        ← generated by: tools\make_pr_diff.bat -Feature [Feature]
[Feature]_pr_diff_stat.txt   ← generated by: tools\make_pr_diff.bat -Feature [Feature]
```
> **Browser mode shortcut:** Run `sync_and_drop.bat -Role PR_REVIEWER -Feature [Feature]`
> to auto-assemble the drop folder including the git diff files.
> Then select-all the folder contents and upload.

### FLOW_AUDITOR only (codebase flow audit — standalone, any time)
```
0_pipeline_rules.md  0_analysis_rules.md  0_coding_rules.md  0_context_rules.md
1_naming_conventions.md  2_webview2_standards.md  3_infrastructure_security.md  4_workflow_standards.md
workflow_06_flow_auditor.md  workflow_06_flow_auditor_ref.md  workflow_06_flow_auditor_ref_p2.md
FLOW_REGISTRY.md             ← the master flow list to audit
[ProjectName].ai_context.txt  ← codebase snapshot for source-first verification
```
> **Browser mode shortcut:** Use `browser_packs\07_FLOW_AUDITOR\` — select-all and upload,
> then additionally upload `FLOW_REGISTRY.md` and your `.ai_context.txt`.

After uploading, say:
> `"All files uploaded. Ready to begin."`

---

## Part 4 — Exact Role Trigger Phrases

Use these word for word. Do not paraphrase.

| Intent | Exact phrase |
|--------|-------------|
| Start new feature | `"Act as DISCOVERY"` |
| Resume interrupted validation | `"Act as DISCOVERY resume validation from REQ-XXX"` |
| Fix only what PLANNER flagged | `"Act as DISCOVERY targeted fix"` |
| Cross-check spec (2nd model) | `"Act as VALIDATOR"` |
| Generate implementation plan | `"Act as PLANNER"` |
| Resume after DISCOVERY fix | `"Act as PLANNER resume"` |
| Resume interrupted dry-run | `"Act as PLANNER resume dry-run from REQ-XXX"` |
| Execute the plan | `"Act as IMPLEMENTER"` |
| Review implementation against git diff | `"Act as PR_REVIEWER"` |
| Triage failures | `"Act as DELTA"` |
| Audit codebase flows against source | `"Act as FLOW_AUDITOR"` |

---

## Part 5 — Essential Prompts (Non-Obvious Only)

> Obvious prompts like "CONTINUE", "Yes — write the plan", "Act as [ROLE]" are in Part 4.
> This section is for prompts you won't guess.

### PLANNER — Resolve a BLOCK
```
"For BLOCK on REQ-XXX: the answer is [value]. Proceed."
"For BLOCK on REQ-XXX: assume [answer]. Proceed with that assumption."
"For BLOCK on REQ-XXX: send back to DISCOVERY targeted fix. Write the feedback file."
```

### PLANNER — Resume after token limit mid dry-run
```
"Act as PLANNER resume dry-run from REQ-XXX"
```

### PLANNER — Resume after DISCOVERY targeted fix
```
"Act as PLANNER resume"
```

### IMPLEMENTER — Fix a SEARCH mismatch
```
"I have manually updated [file] to match the SEARCH block. Retry TASK-XXX."
"Change applied. Verify TASK-XXX checklist now."
"Skip TASK-XXX this run — I will handle it manually."
```

### DELTA — After Loop 3 exhausted
```
"(A) RESUME"                              ← env/blocker fixed, retry same plan
"(B) drop TASK-XXX — continue with remaining"
"(C) replan failing tasks — [what is wrong]"
"(D) abandon"
"(E) env fixed: [what you changed]"
```

### DELTA — Override a triage decision
```
"Change TASK-005 from RESCHEDULE to ESCALATE — the environment issue is not fixed."
"TASK-XXX was COMPLETED in the previous run. It is permanently closed. Remove it."
```

### Any phase — Recovery
```
"Stop. Protocol failure. Re-declare inventory and batch-process from ITEM-001."
"What phase are you in right now? State it before continuing."
"List every uploaded file you have read this session before we proceed."
"The spec has changed at [section]. Invalidate the current plan. Re-run PLANNER from scratch."
```

---

## Part 6 — What You Type vs What AI Does

| Step | You type | AI does |
|------|----------|---------|
| Activate role | Role trigger phrase | Loads workflow, confirms rules active |
| Phase 1 | Nothing | Reads codebase silently |
| Phase 2 Q&A | Answer questions | Builds requirement list |
| Spec draft | `"Proceed to Phase 3"` or wait | Writes draft spec |
| Batch validation | `"CONTINUE"` after each batch | Processes 8 items, pauses |
| Phase 4B/4C | Wait | CF scan + decision dashboard |
| VALIDATOR | Open new session, upload, say `"Act as VALIDATOR"` | Reads both docs, outputs findings |
| Cross-check absorb | Paste VALIDATOR output + `"Absorb them"` | Builds ledger, processes corrections |
| Spec gate | `"Yes — write spec"` | Writes final spec.md |
| Dry-run | `"CONTINUE"` after each batch | Validates every REQ/BUG |
| BLOCK items | Path a/b/c answer | Resolves or saves feedback dump to `continuation\` |
| Task write | `"Yes — write plan"` | Writes plan + runs `pipeline.py save --type plan` |
| Implementation | `"Act as IMPLEMENTER"` | Executes tasks, logs results |
| PR review | Run `tools\make_pr_diff.bat -Feature [F]` then `sync_and_drop.bat -Role PR_REVIEWER -Feature [F]`, upload drop, `"Act as PR_REVIEWER"` | Reviews git diff vs log claims, outputs 05_REVIEW_REPORT.md |
| Failure triage | `"Act as DELTA"` | Triages, replans, writes DELTA plan |
| Loop 3 exhausted | Choose A/B/C/D/E | Executes your choice |

---

## Part 7 — Gotchas, Common Mistakes & Troubleshooting

### ── SETUP GOTCHAS ──

**❌ Browser session — AI ignores rules or behaves generically**
Cause: Started typing before uploading all files, or forgot an always-on rule file.
Fix: Fresh session. Upload the correct minimal file set for your role first. Say nothing until all files are uploaded.

**❌ AI does not recognise the role trigger**
Cause: Trigger phrase was paraphrased. `"Be the planner"` does not reliably load the workflow file.
Fix: Use the exact phrases from Part 4 word for word. If still failing: `"Read workflow_02_planner.md and activate PLANNER role."`

**❌ Agent mode — rules seem not to be applying**
Cause: Past Turn 30 in a long conversation. Old history polluting context window.
Fix: Start a fresh chat. Rules reload automatically. Never continue past Turn 30 for complex work.

**❌ VALIDATOR findings not matching what DISCOVERY absorbs**
Cause: VALIDATOR output was incomplete (session interrupted) or pasted partially.
Fix: Always paste the entire VALIDATOR output including the VALIDATOR COMPLETE block. If interrupted, use the Resumption Contract to complete VALIDATOR first, then paste the full output.

---

### ── DISCOVERY GOTCHAS ──

**❌ AI asks too many questions and never drafts**
Cause: Convergence rule hasn't triggered, or AI is being overly cautious.
Fix: `"You have enough information. Stop gathering and proceed to Phase 3 now."`

**❌ Spec scope is too large**
Cause: Feature is genuinely too big for one session.
Fix: `"Split this. Do [Feature A] only. [Feature B] is a separate spec."`

**❌ AI marks something MISSING that already exists**
Cause: Shallow Phase 1 read missed the implementation.
Fix: `"REQ-XXX is wrong — [ClassName.MethodName] EXISTS in [file]. Correct the verdict, do not create a DEC-ID, and continue."`

**❌ AI marks something EXISTS that is actually broken**
Cause: Found the method name but didn't read the implementation deeply.
Fix: `"REQ-XXX is PARTIAL, not EXISTS. [What is missing]. Update the verdict and add a BUG-ID."`

**❌ Phase 4 batch stops and never resumes**
Cause: Didn't type CONTINUE, or typed something that broke batch state.
Fix: `"CONTINUE"` — exactly that word. If AI seems lost: `"Resume self-validation from REQ-XXX. Declare inventory and continue batch."`

**❌ Spec gate stuck at HOLD**
Cause: A blocking open question requires information you don't have.
Fix: Either find the answer or: `"Change OQ-XXX to non-blocking — resolve in implementation. Note the risk in spec."` Only do this if the OQ genuinely won't break the design.

**❌ AI produces a vague DEC-ID**
Cause: MISSING capability was not fully designed in Phase 3.
Fix: `"DEC-XXX is underspecified. Expand with exact field names, method signatures, and algorithm steps now."`

**❌ Porting mode — content was lost**
Cause: AI summarised or dropped sections instead of transforming them.
Fix: `"You are in PORTING MODE. Apply the per-line transformation question to [section]: classify it, map it to the correct spec section, and add it. Do not discard any content from the source."`

---

### ── VALIDATOR GOTCHAS ──

**❌ VALIDATOR only read the spec and ignored the source document**
Cause: Source document was not uploaded, or AI confused the two files.
Fix: Start fresh. Upload both files explicitly. Say `"Act as VALIDATOR"` only after both are confirmed uploaded.

**❌ VALIDATOR produced a summary instead of per-item verdicts**
Cause: Analysis protocol not applied — Rule A inventory not declared.
Fix: `"Protocol failure. Apply 0_analysis_rules.md — declare inventory of source sections vs spec sections, build the Cross-Reference Ledger, then batch-process findings with per-item verdict format."`

**❌ VALIDATOR skipped a batch without waiting for CONTINUE**
Cause: AI ignored the hard PAUSE rule.
Fix: `"Stop. Batch limit is 8 items. Output the BATCH COMPLETE block now and wait for CONTINUE."`

**❌ DISCOVERY cannot absorb VALIDATOR output — format mismatch**
Cause: VALIDATOR was run without `workflow_02_validator.md`, so it used a different output format.
Fix: Ensure `workflow_02_validator.md` is uploaded in the VALIDATOR session. The CORRECTION-XXX / MISSED-XXX / AGREE format is mandatory for DISCOVERY absorption.

---

### ── PLANNER GOTCHAS ──

**❌ PLANNER refuses to run**
Cause: Spec gate is HOLD or REDO — unresolved blocking OQs or CRITICAL CFs.
Fix: Return to DISCOVERY. Resolve the blocking items. PLANNER should not and will not proceed on a broken spec.

**❌ PLANNER flags a BLOCK on something you thought was clear**
Cause: A DEC-ID is missing exact field names, constants, or signatures.
Fix: `"(c) — send to DISCOVERY targeted fix."` PLANNER saves the feedback dump to `continuation\`. Then: `"Act as DISCOVERY targeted fix."`

**❌ SEARCH blocks in the plan don't match actual code**
Cause: Code changed between DISCOVERY read and PLANNER write, or PLANNER hallucinated a line.
Fix: IMPLEMENTER catches this and logs PARTIAL. Then `"Act as DELTA"` to rewrite the SEARCH block. Do not manually fix SEARCH blocks.

**❌ Plan has tasks in wrong dependency order**
Cause: PLANNER miscalculated dependency chain.
Fix: `"TASK-005 depends on TASK-002, not TASK-001. Reorder before writing the plan."`

**❌ Plan was written but spec changed afterwards**
Cause: New requirement added, OQ answered differently, or cross-check changed an architecture decision.
Fix: `"The spec has changed at [section]. Invalidate the current plan. Re-run PLANNER from scratch."` Never patch the plan manually.

---

### ── IMPLEMENTER GOTCHAS ──

**❌ IMPLEMENTER improvises — writes code not in the SEARCH/REPLACE blocks**
Cause: Task spec was underspecified. PLANNER left a design decision for IMPLEMENTER.
Fix: Log as PARTIAL. `"Act as DELTA"` — DELTA will replan that task with correct specificity.

**❌ SEARCH block fails to match**
Cause 1: An earlier task already modified that file.
Cause 2: PLANNER's read was from stale context.
Fix: IMPLEMENTER logs PARTIAL. `"Act as DELTA"` — DELTA rewrites the SEARCH block from current file state.

**❌ Task marked COMPLETED but CF GATE not verified**
Cause: Protocol violation.
Fix: `"TASK-XXX cannot be COMPLETED — CF-XXX was not verified. Revert to PARTIAL and state why."` DELTA handles as P0.

**❌ Token limit mid-implementation**
Cause: Large plan.
Fix: IMPLEMENTER logs remaining tasks as SKIPPED. New session: `"Act as IMPLEMENTER"` — reads log, resumes. If it doesn't: `"Read 03_IMPLEMENTATION_LOG.md. Resume from TASK-XXX."`

---

### ── DELTA GOTCHAS ──

**❌ DELTA keeps replanning the same task across loops with no progress**
Cause: Root cause is environmental (missing SDK, wrong config, env var) — not a code problem.
Fix: Investigate the environment. Once fixed: `"env fixed: [what you changed]"` — DELTA re-triages without counting as a new loop.

**❌ DELTA loop 3 exhausted**
Cause: Systemic issue AI cannot self-resolve.
Fix: Read the Post-Loop-3 Human Review Block. Choose one of the five options (A–E). Do not ask DELTA to loop again.

**❌ DELTA drops a CF GATE from a replanned task**
Cause: DELTA incorrectly omitted the CF from DELTA-TASK.
Fix: `"DELTA-TASK-XXX is missing CF-XXX GATE. Add the CF fix block and the verification checklist item before I run IMPLEMENTER."`

**❌ DELTA rewrites code for a task already COMPLETED**
Cause: DELTA mistakenly reopened a closed task.
Fix: `"TASK-XXX was COMPLETED in the previous run. It is permanently closed. Remove it from the DELTA plan."`

---

### ── PR_REVIEWER GOTCHAS ──

**❌ PR_REVIEWER has no git diff to read**
Cause: tools\make_pr_diff.bat was not run before the session, or diff file not included in upload.
Fix: Close session. Run `tools\make_pr_diff.bat -Feature [Feature]` locally. Re-run
`sync_and_drop.bat -Role PR_REVIEWER -Feature [Feature]`. Upload the full drop folder including
the diff files. Without the diff, PR_REVIEWER cannot do forensic review and will fall back to
trusting the log (which defeats the purpose).

**❌ PR_REVIEWER marks a task FABRICATED but the code IS in the codebase**
Cause: The change was committed under a different feature branch or the baseline tag is wrong.
Fix: Verify with `git log --oneline -- [file]`. If the commit exists: `"The change for TASK-XXX
IS in git. Commit [hash]. Re-evaluate that task as VERIFIED."` If the commit is missing:
PR_REVIEWER is correct -- IMPLEMENTER logged a fabrication.

**❌ PR_REVIEWER verdicts conflict with DELTA's existing plan**
Cause: DELTA was run before PR_REVIEWER (wrong order) or a stale delta plan is in context.
Fix: Discard the stale delta plan. PR_REVIEWER runs FIRST, then DELTA. DELTA reads the review
report and treats FABRICATED verdicts as P0 regardless of what the old delta plan said.

**❌ PR_REVIEWER marks tasks MISSING that are in a different repo**
Cause: tools\make_pr_diff.bat only diffed one repo; multi-repo changes were missed.
Fix: Re-run `tools\make_pr_diff.bat -Feature [Feature]` -- it diffs all repos automatically
(TradeInDepthPro, WebApi, WebApp). If a repo was not detected, check that the -Project param
points to the correct project root.

---

### ── ANALYSIS PROTOCOL GOTCHAS ──

**❌ AI produces a summary instead of per-item verdicts**
Symptom: `"Overall the requirements look good..."` or `"Most items match..."`
Cause: Analysis protocol not applied — inventory never declared.
Fix: `"Stop. Protocol failure. Re-declare inventory, count all items, and batch-process from ITEM-001 with a full verdict for every item."`

**❌ Batch contains more than 8 items**
Cause: AI ignored the hard batch limit.
Fix: `"Batch limit is 8 items maximum. Stop this batch at ITEM-8. Output the BATCH COMPLETE block and wait for CONTINUE."`

**❌ AI processes batch 2 without waiting for CONTINUE**
Cause: AI ignored the hard pause rule.
Fix: `"Do not proceed to the next batch without my CONTINUE. Output the BATCH COMPLETE block now and stop."`

**❌ Resuming after token limit — AI re-processes completed items**
Cause: Resumption Contract was not output or not confirmed.
Fix: `"Output the Resumption Contract first. State which items are confirmed complete and which item we resume from. Do not process anything until I confirm."`

---

## Part 8 -- Browser Pack Generator & Agent Sync

### What it is

`sync_and_drop.bat` is the **single entry point** for all session-prep work. It runs 4 steps in the correct order:

```
Step 0  Sync rules\ + workflows\ -> .agent\    (IDE/Cursor reads from .agent\)
Step 1  Refresh .ai_context.txt files          (run_agent.bat per project)
Step 2  Rebuild browser_packs\                 (sync_and_drop.bat (internally) -- once)
Step 3  Build browse-drop\ folders             (one per Feature+Role, ready to upload)
```

`sync_and_drop.bat (internally)` is called by `sync_and_drop.bat` internally -- you do not run it directly.

### When to run it

| Situation | Command |
|-----------|---------|
| Edited a rule or workflow file | `sync_and_drop.bat` (full run) |
| Rule changed, code unchanged | `sync_and_drop.bat -SkipContext` |
| Code changed, rules unchanged | `sync_and_drop.bat -SkipSync` |
| Neither changed -- just rebuild drops | `sync_and_drop.bat -SkipSync -SkipContext` |
| Only one feature or role | `sync_and_drop.bat -Feature MVP1 -Role 04_IMPLEMENTER -SkipContext` |

### How to run
```
Double-click sync_and_drop.bat
```
Or from a terminal:
```powershell
cd "D:\Code\repo\Utils\agent-settings"
.\sync_and_drop.bat -SkipContext
```


### Output folders

| Folder | Use when | Say after uploading |
|--------|----------|---------------------|
| `01_DISCOVERY\` | Starting a new feature spec | `"Act as DISCOVERY"` |
| `02_VALIDATOR\` | Cross-checking (separate session) | `"Act as VALIDATOR"` |
| `03_PLANNER\` | Generating the implementation plan | `"Act as PLANNER"` |
| `04_IMPLEMENTER\` | Executing the plan | `"Act as IMPLEMENTER"` |
| `05_DELTA\` | Triaging failures | `"Act as DELTA"` |
| `06_PR_REVIEWER\` | Forensic review of IMPLEMENTER output | `"Act as PR_REVIEWER"` |
| `07_FLOW_AUDITOR\` | Source-first flow audit of existing codebase | `"Act as FLOW_AUDITOR"` |
| `00_FULL_SESSION\` | All roles, 200K+ context only | `"Act as DISCOVERY"` |

Each folder also contains a `README.md` listing the additional session-specific files you must
upload yourself (spec file, source document, codebase snapshot) and the exact trigger phrase.

### How the script finds files

The script searches **recursively under `agent-settings\`** for each filename in `$PhaseMap`.
It excludes `browser_packs\` itself (to avoid stale copies matching instead of the real file).

This means:
- You can freely reorganise files into new subfolders under `agent-settings\` — the script still finds them
- File**names** must remain unique across the entire `agent-settings\` tree
- If two files with the same name ever exist, the script warns you and uses the first match

### Phase-to-File mapping (where to edit)

The mapping that controls which files go into which pack lives in **one place only**:
the `$Config.Phases` ordered hashtable in `sync_and_drop.ps1` (lines ~94–256).

```
MAINTENANCE RULE: never manually edit files inside browser_packs\.
                  browser_packs\ is always wiped and regenerated on each run.
```

#### When you add a new rule file
1. Drop the file anywhere under `agent-settings\` (e.g. `rules\global\`, `rules\project\`, or a new subfolder)
2. In `sync_and_drop.ps1`, add its **filename only** (not path) to the `Files` array of every phase in `$Config.Phases` that needs it
3. Re-run the script — the recursive search finds it automatically regardless of which subfolder it is in

#### When you rename a rule file
1. Rename the actual file on disk
2. Find the old filename in `$PhaseMap` (Ctrl+F in the script)
3. Replace it with the new filename
4. Re-run the script

#### When you add a new workflow phase
1. Create the new `workflow_xx_name.md` in `workflows\`
2. Add a new key+hashtable entry to `$Config.Phases` in `sync_and_drop.ps1` following the existing pattern
3. Re-run the script

#### When a workflow file changes (content update, no rename)
Just re-run the script — it copies the latest version of every file automatically.

### Current phase-to-file mapping reference

| Phase folder | Global rules | Project rules | Workflow files |
|---|---|---|---|
| `01_DISCOVERY` | all 4 (0_pipeline, 0_analysis, 0_coding, 0_context) | all 4 (1–4) | discovery, p4, ref, cf_ref, crosscheck |
| `02_VALIDATOR` | pipeline, analysis, coding | naming, security | validator |
| `03_PLANNER` | all 4 | all 4 | planner, planner_ref |
| `04_IMPLEMENTER` | all 4 | all 4 | implementer + implementer_ref |
| `05_DELTA` | all 4 | all 4 | delta + delta_ref |
| `06_PR_REVIEWER` | all 4 + 0_pipeline_ops_ref | all 4 | pr_reviewer + pr_reviewer_ref |
| `07_FLOW_AUDITOR` | all 4 | all 4 | flow_auditor + flow_auditor_ref + flow_auditor_ref_p2 |
| `00_FULL_SESSION` | all 4 | all 4 | all discovery + planner + planner_ref + implementer + delta |

All phases also include `BROWSER_SESSION_CONTINUATION_RULE.md` for session continuation support.

> VALIDATOR intentionally omits `0_context_rules.md`, `2_webview2_standards.md`, and
> `4_workflow_standards.md` — VALIDATOR has no codebase access and those files add token weight
> with no benefit in a cross-check-only session.

---


