---
trigger: manual
description: "Pipeline Operations Reference — §7A Folder Map, §7B Commands, §7C Artifact Resolution, §7D Dump Flow, §7E Headers, §7F Git-Ignore. Load when working with pipeline artifacts or dumps."
---

# Pipeline Operations — Complete Agent Reference

> **Single source of truth for all pipeline file operations.** Load at the start of any session involving pipeline artifacts or dumps. Full guide: `python pipeline.py help`.

---

## §7A. Folder Map — Where Everything Lives

```
Docs\[Project]\
│
├── specs\                      GIT-COMMITTED
│   └── [Feature]_spec.md         Written by DISCOVERY Phase 6 only.
│                                  Never overwritten — only versioned.
│
├── flow_registry\              GIT-COMMITTED
│   ├── FLOW_REGISTRY.md          Living flow map. Updated by FLOW_AUDITOR. [NEW]/[AUDITED] status. Append-only.
│   └── audits\
│       └── YYYYMMDD_AUDIT_FINDINGS.md   Point-in-time audit output per run.
│
├── pipeline\                   GIT-COMMITTED
│   └── [Feature]\
│       ├── YYYYMMDD_HHMM_02_IMPLEMENTATION_PLAN.md
│       ├── IMPL_P01.md                           ← chunk 1 (if split — fixed name, no timestamp)
│       ├── IMPL_P02.md                           ← chunk 2 (if split — fixed name, no timestamp)
│       ├── YYYYMMDD_HHMM_03_IMPLEMENTATION_LOG.md
│       ├── YYYYMMDD_HHMM_05_REVIEW_REPORT.md     ← written by PR_REVIEWER (Stage 4.5)
│       └── YYYYMMDD_HHMM_04_DELTA_PLAN.md
│           Newest YYYYMMDD_HHMM_ prefix per type = "latest" — auto-discovered.
│           All files flat inside [Feature]\. No sub-folders.
│           Chunk files (IMPL_P0n.md) use fixed names — never timestamped.
│
└── continuation\               GIT-IGNORED  ← everything in-progress, flat
    ├── YYYYMMDD_HHMM_[Feature]_[Role]_dump.md
    │   Any role, any content: mid-run save, token-limit output, partial chunks,
    │   command output, notes, any file not yet final.
    └── (all files flat — no sub-folders)
```

**What goes where — decision:**
```
Role finished completely (plan / log / delta)?
  → pipeline\[Feature]\  via: python pipeline.py save --feature X --type Y --file path

Anything NOT final (partial output, mid-run save, command output, notes)?
  → continuation\         via: python pipeline.py dump --feature X --role R --file path
  OR paste directly in next chat (Path A — fastest, no file needed)
```

**Moving from continuation\ to pipeline\ (agent-assisted):**
Drop any file into continuation\ (named however). When you say "this is final, move it":
1. Agent reads the file header (Feature, Type fields)
2. Agent runs: `python pipeline.py save --feature [F] --type [T] --file [path]`
3. File lands in `pipeline\[Feature]\` with correct timestamp name
Files with no header also work — `pipeline.py save` prepends one automatically.

---

## §7B. All Pipeline Commands — When to Use Each

**Script location:** `Utils\AI_Code\ai-utils\pipeline.py`
**Full guide:** `python pipeline.py help`  |  **Interactive menu:** `python pipeline.py`

#### SAVE — archive a finished artifact
```
python pipeline.py save --feature MVP1 --type plan   --file C:/Temp/plan.md
python pipeline.py save --feature MVP1 --type log    --file C:/Temp/log.md
python pipeline.py save --feature MVP1 --type delta  --file C:/Temp/delta.md
python pipeline.py save --feature MVP1 --type review --file C:/Temp/review.md
```
Use immediately after PLANNER / IMPLEMENTER / PR_REVIEWER / DELTA finishes.
Timestamps the file and copies to `pipeline\[Feature]\`. Alphabetical = chronological for timestamped files.
Type keys: `plan` = 02_IMPLEMENTATION_PLAN · `log` = 03_IMPLEMENTATION_LOG · `delta` = 04_DELTA_PLAN · `review` = 05_REVIEW_REPORT

#### FIND — load the right file for the next role
```
python pipeline.py find --feature MVP1 --type plan
python pipeline.py find --feature MVP1 --type log
python pipeline.py find --feature MVP1 --type delta
python pipeline.py find --feature MVP1 --type review
```
Prints the absolute path on stdout. Load that file — never guess or list directories.
Exit code `2` = artifact not saved yet. Browser mode: navigate to `pipeline\[Feature]\` and pick the highest `YYYYMMDD_HHMM_` prefix for the type needed.

#### DUMP — save a partial/mid-run file to continuation\
```
python pipeline.py dump --feature MVP1 --role IMPLEMENTER --file C:/Temp/dump.md
python pipeline.py dump --feature MVP1 --role IMPLEMENTER --file C:/Temp/dump.md \
                        --contains "TASK-001 to TASK-015 done. Stopped mid-TASK-016." \
                        --resume-from TASK-016
```
Adds the mandatory header, saves to `continuation\` with a timestamp.
Use when: browser hit token limit, role paused mid-run, any partial save.

#### DUMP-FIND — find the latest dump to resume from
```
python pipeline.py dump-find --feature MVP1
```
Returns path to the newest dump for that feature.

#### PR_REVIEWER -- generate git diff and assemble browser drop
**Script location:** `Utils\agent-settings\tools\make_pr_diff.bat`  (developer tool -- run locally, not by AI agent directly)
```
tools\make_pr_diff.bat -Feature MVP1
tools\make_pr_diff.bat -Feature MVP1 -Since stable-v1.0
```
Generates `[Feature]_pr_diff.txt` + `[Feature]_pr_diff_stat.txt` in `browse-drop\[Feature]_06_PR_REVIEWER\`.
Auto-detects stable baseline: stable-* tag -> merge-base with main -> HEAD~20.
Diffs all repos (TradeInDepthPro, WebApi, WebApp).

```
sync_and_drop.bat -Role PR_REVIEWER -Feature MVP1
```
Assembles the complete PR_REVIEWER browser upload drop including rule files, workflow files,
pipeline artifacts, and the git diff. Upload the drop folder to start a PR_REVIEWER session.

#### DIFF — verify file integrity after a move or rename
```
python pipeline.py diff --old old/path/to/rule.md --new D:/repo/new/path/rule.md
python pipeline.py diff --repo D:/repo --old old/folder/ --new D:/repo/new/folder/
```
Use ONLY after moving or renaming a file — not after code edits.
For code edits: use `run_agent.bat --changes` instead.
Exit 0 = identical · Exit 1 = differences found (MUST report diff lines to user).

#### STATUS — see what has been saved
```
python pipeline.py status
python pipeline.py status --feature MVP1
```
Shows plan/log/delta status, chunk files, and dump count per feature.

---

## §7C–§7F → See `0_pipeline_ops_ref_p2.md`

Load `0_pipeline_ops_ref_p2.md` when you need:
- **§7C** — Artifact resolution (agent mode `pipeline.py find`, browser mode file selection, browser header template)
- **§7D** — Dump flow (resume after token limit, PATH A paste, PATH B save)
- **§7E** — Mandatory file header rule + pre-save checklist
- **§7F** — Git-ignore entries required

> Load trigger: any session involving browser-mode artifact output, dump/resume, or file integrity checks.

