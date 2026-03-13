---
trigger: manual
description: "Pipeline Operations Reference Part 2 — §7C Artifact Resolution, §7D Dump Flow, §7E File Headers, §7F Git-Ignore. Load alongside 0_pipeline_ops_ref.md when working with artifact files, browser mode output, or dump/resume flows."
---

# Pipeline Operations — Part 2 (§7C–§7F)

> Companion to `0_pipeline_ops_ref.md`. Load this file when: resolving artifact filenames, writing browser-mode output, resuming from a dump, or checking git-ignore.

---

## §7C. Pipeline Artifact Resolution Protocol

**Rule: NEVER guess filenames. NEVER list directory contents to discover the right file.**

#### Agent Mode
1. Run `python pipeline.py find --feature [Feature] --type [plan|log|delta]`
2. Load the path printed on stdout — nothing else.
3. Exit code `2` = artifact not saved yet. Tell the user. Do not proceed.

#### Browser Mode (no terminal)
Navigate to `Docs\[Project]\pipeline\[Feature]\` and locate the most recent file by timestamp prefix:
- **Active Plan:** most recent `YYYYMMDD_HHMM_04_DELTA_PLAN.md` (Loop 2+) or `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md` (Loop 1)
- **Reference Plan:** most recent `YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md`
- **Latest Log:** most recent `YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md`
- **Review Report:** most recent `YYYYMMDD_HHMM_05_REVIEW_REPORT.md`

Sort ascending — alphabetical = chronological. Take the last match per type.
If no matching file: tell the user the artifact has not been produced yet — do not proceed.

**Split plans:** If plan header says `Split Mode: SPLIT`, chunk files (`IMPL_P01.md`, `IMPL_P02.md`, …) exist in same folder with fixed names (no timestamp). Load in order as IMPLEMENTER reaches each phase stub.

**After writing any pipeline artifact (browser mode):**
Prepend the header block below to the artifact content before outputting it. The user saves the file with the correct `YYYYMMDD_HHMM_` prefixed name.

**Browser mode artifact header template** (prepend to every artifact output in browser mode):
```
<!-- ══════════════════════════════════════════════════════════════ -->
<!-- PIPELINE ARTIFACT HEADER  —  DO NOT EDIT THIS BLOCK          -->
<!-- ══════════════════════════════════════════════════════════════ -->
<!-- Project      : [CONFIG project name]                          -->
<!-- Feature      : [Feature]                                      -->
<!-- Type         : [02_IMPLEMENTATION_PLAN / 03_IMPLEMENTATION_LOG / 04_DELTA_PLAN / 05_REVIEW_REPORT] -->
<!-- Role         : [PLANNER / IMPLEMENTER / DELTA / PR_REVIEWER]                -->
<!-- Mode         : Browser (Claude.ai)                            -->
<!-- Timestamp    : [current date-time YYYY-MM-DD HH:MM]           -->
<!-- Session Turn : [turn number in this session]                  -->
<!-- Split Mode   : [SINGLE FILE / SPLIT — n phase files: IMPL_P01.md…IMPL_P0n.md] -->
<!-- Contains     : [1-2 sentence plain-English summary]           -->
<!-- Resume From  : N/A — complete artifact                        -->
<!-- ══════════════════════════════════════════════════════════════ -->
<!-- HOW TO USE IN A NEW SESSION: upload file, then say:          -->
<!--   Plan  → "Act as IMPLEMENTER"   (also upload chunk files if Split Mode: SPLIT) -->
<!--   Log   → "Act as DELTA"                                      -->
<!--   Delta → "Act as IMPLEMENTER" (re-run failed tasks)         -->
<!-- ══════════════════════════════════════════════════════════════ -->
```

---

## §7D. Dump Flow — Resuming After Token Limit

**Any role can dump.** DISCOVERY, PLANNER, IMPLEMENTER, DELTA, VALIDATOR, FLOW_AUDITOR — all go to `continuation\`.

#### PATH A — Paste directly in new session (FASTEST)
1. Copy agent output from browser → open new session → upload rule/browser pack → paste raw text
2. Say: `"This is a continuation dump. Read it and resume."`
✓ Best for: same-day resumption

#### PATH B — Save to continuation\ (reusable)
1. Save agent output to any file (e.g. dump.md)
2. Run: `python pipeline.py dump --feature X --role R --file dump.md --contains "..." --resume-from TASK-016`
3. Upload the saved file to next session, say: `"Resume from continuation dump."`
✓ Best for: multi-day work, record-keeping

**When user says "resume from dump":**
1. File uploaded → read the header block first, extract `Resume From` field, resume there.
2. Raw text pasted → read it directly, extract any header if present.
3. Just "resume" with no file → run `python pipeline.py dump-find --feature [F]` and load the result.
4. State: `"Resuming [Role] for [Feature] from [Resume From field]."`

---

## §7E. Mandatory File Header Rule

**Every file written to `pipeline\` or `continuation\` MUST begin with the appropriate header block.**
`pipeline.py` adds the header automatically when you use `save` or `dump` commands.

The header encodes: what it contains · where to resume · who wrote it · when · how it was created.

**Agent pre-save checklist (fill before calling `pipeline.py save`):**
- role, mode (Agent/Browser), turn number, contains (1–2 sentence summary), resume-from (task/phase or N/A), split-mode (SINGLE FILE or SPLIT with chunk list)

---

## §7F. Git-Ignore Entries Required

Add to repo root `.gitignore` if not already present:
```
Docs/*/continuation/
*.ai_context.txt
browse-drop/
```
`pipeline\`, `specs\`, and `flow_registry\` stay committed. `continuation\` is scratch space — never committed.
`browse-drop\` is generated output — never committed.
