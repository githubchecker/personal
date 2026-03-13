# `run_agent.bat` — Reference Guide

**Location:** Place `run_agent.bat` in the **root of each project** (e.g., `TradeInDepthPro\`).  
**Script it calls:** `Utils\AI_Code\agent.py` — never run `agent.py` directly.  
**Output file:** `[ProjectName].ai_context.txt` (created in the project root).

> This guide covers the three commands the script exposes.  
> For how agents *use* the output, see `agent-settings\rules\global\0_context_rules.md` Sections 1–3.  
> For pipeline artifact management (save/find/dump/log-cmd), see `Utils\AI_Code\ai-utils\pipeline.py help`.

---

## Commands at a Glance

| Command | When to use | Output |
|---------|------------|--------|
| `run_agent.bat` | Cold Start / full refresh | `[Project].ai_context.txt` (full codebase snapshot) |
| `run_agent.bat --changes` | After any code edits (Delta Protocol) | `[Project].ai_context.txt` (changed files only, git diff) |
| `run_agent.bat --generate-list` | First-time setup or after adding new libraries | `new_files_to_consider.txt` (candidate ignore list) |

---

## 1. Default — Full Project Snapshot (Cold Start)

```bat
run_agent.bat
```

Scans every file in the project root (respecting `.aicontextignore.txt`) and writes a single
context file. Use this at the start of any new session or when the AI seems confused about
the overall project structure.

**When to use:**
- First session on a project (mandatory Cold Start)
- AI has lost context of the overall architecture
- Many files changed and `--changes` output would be confusing

**What happens:**
1. `agent.py` validates you are in a valid project root (looks for a sentinel file:
   `*.sln`, `package.json`, `run_agent.bat`, etc.)
2. Reads `.aicontextignore.txt` and filters out ignored paths
3. Prioritises files by type (interfaces → models → config → business logic → docs)
4. Warns if output exceeds 200K tokens; hard warning at 500K tokens
5. Writes `[ProjectName].ai_context.txt` to the project root
6. Copies to clipboard if small enough (< 500K chars); otherwise prints "use the file"

**Agent mode workflow:**
1. Run `run_agent.bat` from the project root
2. Agent reads the generated `.ai_context.txt`
3. Agent states "Cold Start complete — context loaded from [filename]" before any work

**Browser mode workflow:**
1. Run `run_agent.bat` from the project root
2. Upload the generated `.ai_context.txt` to the browser AI session (Claude, Gemini, etc.)
3. AI treats the uploaded file as Single Source of Truth for the session

---

## 2. `--changes` — Delta Update (After Code Edits)

```bat
run_agent.bat --changes
```

Uses `git diff` to find files modified or added since the last commit. Writes only those
files into `[ProjectName].ai_context.txt`. Much smaller and faster than a full scan.

**When to use:**
- After any batch of code edits in Agent mode, to update the AI's mental model
- Follow-up prompts in the same session after applying changes
- Quick bug fix iterations

**What happens:**
1. Runs `git diff --name-only HEAD` to find changed files
2. Reads and bundles only those files into the context file
3. Almost always small enough to be copied to clipboard automatically

**Agent mode workflow:**
1. Make code edits
2. Run `run_agent.bat --changes`
3. Agent reads the delta file and states "Delta verified from Turn X"

> ⚠️ **Critical disambiguation — `--changes` vs `pipeline.py diff`**
>
> These look similar but do completely different things:
>
> | | `run_agent.bat --changes` | `pipeline.py diff` |
> |--|--------------------------|-------------------|
> | **Purpose** | Update AI mental model of the repo | Verify file wasn't corrupted during a move |
> | **Scope** | Whole repo — all git-changed files | Single file only |
> | **Trigger** | After editing code (Delta Protocol) | After moving or renaming a file (Rule 12 audit) |
>
> Never use `--changes` to verify a file move — it's too broad.  
> Never use `pipeline.py diff` after code edits — it only checks one file.

---

## 3. `--generate-list` — Ignore List Setup

```bat
run_agent.bat --generate-list
```

Scans the whole project and writes a list of every file and folder **not already covered**
by `.aicontextignore.txt`. Use this once on a new project to quickly build your ignore list,
and again after adding new libraries or build tools.

**Output:** `new_files_to_consider.txt` in the project root. Nothing is copied to clipboard.

**Workflow:**
1. Run `run_agent.bat --generate-list`
2. Open `new_files_to_consider.txt` side-by-side with `.aicontextignore.txt`
3. For every entry you want excluded from context (e.g., `bin/`, `obj/`, `node_modules/`),
   copy that line into `.aicontextignore.txt`
4. Save `.aicontextignore.txt` and delete `new_files_to_consider.txt`
5. Run `run_agent.bat` (full scan) to confirm the output is now the right size

---

## Project Root Requirements

Each project needs two files in its root:

| File | Purpose |
|------|---------|
| `run_agent.bat` | Launcher — calls `Utils\AI_Code\agent.py` with correct relative path |
| `.aicontextignore.txt` | Gitignore-style exclusion list for the context scan |

The generated files below are already covered by the repo `.gitignore` — never commit them:

| Generated File | Covered by |
|---------------|-----------|
| `[ProjectName].ai_context.txt` | `*.ai_context.txt` in `.gitignore` |
| `new_files_to_consider.txt` | Add manually if not already in `.gitignore` |

---

## Directory Layout (Reference)

```
D:\Code\repo\
├── TradeInDepthPro\               ← project root (always run bat from here)
│   ├── run_agent.bat
│   ├── .aicontextignore.txt
│   └── TradeInDepthPro.ai_context.txt   ← generated, git-ignored
│
└── Utils\
    └── AI_Code\
        ├── agent.py               ← the engine (never run directly)
        ├── guide.md               ← this file
        └── ai-utils\
            └── pipeline.py        ← artifact manager (separate tool, see: pipeline.py help)
```
