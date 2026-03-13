---
trigger: always_on
description: strict_context_workflow
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# Global Browser-Level Accuracy Protocol (Context Rules)

## BROWSER MODE OVERRIDE (Read This First)

**If the user has manually uploaded an `ai_context.txt` or a full codebase file into this conversation:**
- Treat the uploaded file as the **Single Source of Truth** — equivalent to a completed Cold Start.
- ❌ Do NOT run or request `run_agent.bat` — there is no terminal in browser mode.
- ❌ Do NOT run `run_agent.bat --changes` after edits — output code blocks labeled with their target file path instead.
- ✅ State: `"Using uploaded context as ground truth."` at the start of the session.
- ✅ After any code change, output a clearly labelled `FILE: [path]` diff block so the user can apply it manually.
- All Sections 1–5 below apply to **agent mode only**. Browser mode is governed by this override.
- ✅ **Continuation dump resume:** If the user says `"resume from dump"` or pastes raw text in chat, see `0_pipeline_ops_ref.md` §7D — Dump Loading Rules.

---

**MANDATE (Agent Mode):** You are PROHIBITED from writing code based on partial information. You MUST strictly follow this Context-First Workflow.

## 1. The "Cold Start" Protocol (Mandatory)
**Trigger:** Start of session, or any of: receiving an architectural question; encountering a file reference not in current context; preparing for a change that requires reading or modifying more than 2 distinct source files, OR a single-file change where understanding callers or dependencies requires reading 2+ other files.
**Action:**
1.  **EXECUTE:** `run_agent.bat` from the **project root** (e.g. `[ProjectName]\`).
    - Do NOT run `python agent.py` directly — `agent.py` lives in `Utils/AI_Code/` and is not in the project root. Always use `run_agent.bat`.
    - Each project has its own `run_agent.bat` and `.aicontextignore.txt`. Always run from the correct project root.
    - *Creates:* `[ProjectName].ai_context.txt` (Full Context + Priority TOC).
2.  **READ & VERIFY:** The generated `.ai_context.txt`.
3.  **INGEST (ONE-SHOT):**
    - **Memory-First Check**: Before requesting a "Cold Start", check if a prioritized TOC already exists in this conversation history. If Turn > 1 and context exists, do NOT re-ingest.
    - **Context ID**: Note the `GENERATION ID` from the header.
    - **Trust & Reliance**: Trust this file as the **Single Source of Truth**. Do NOT re-read it in subsequent turns of this session unless Turn Count > 30.
    - **Turn Limit Rule**: If Turn Count > 30, **START A NEW CONVERSATION** and re-ingest. This is the only way to "skip" old tokens and prevent history bloat.
    - **Turn Counter (mandatory output):** At session start output `Session Turn: 1`. Every 5 turns output `Session Turn: [N]`. At turn 28+ output `⚠️ APPROACHING TURN LIMIT — complete this task then start a new session`.
    - **Context Statement**: State "Establishing context [Project] from Turn X" to confirm ingest.

## 2. The "Delta" Protocol (Maintenance)
**Trigger:** You have already loaded the full context and just applied a fix.
**Action:**
1.  **EXECUTE:** `run_agent.bat --changes` from the same project root.
2.  **READ:** The output.
    - **Verify:** Did your changes apply correctly?
    - **Diff:** Does the delta match your mental model?
    - **Note:** If `--changes` finds no git changes, the agent automatically falls back to a full scan. This is expected on a clean working tree.
    - *If Delta is massive/confusing:* Revert to "Cold Start" to refresh.
3.  **After every batch of edits**, state "Delta verified from Turn X" to confirm you checked the output.

> 🛑 **Disambiguation: `run_agent.bat --changes` vs `pipeline.py diff`**
>
> | Command | Purpose | Scope | Trigger |
> |---------|---------|-------|---------|
> | `run_agent.bat --changes` | Update your **mental model** of the repo | Whole repo — global git diff | After ANY batch of code edits |
> | `pipeline.py diff` | Verify a **single file was not corrupted** during a move or rename | Single file or folder only | After moving/renaming a file |
>
> **Quick rule:** "I just edited code" → `run_agent.bat --changes`. "I just moved a file" → `pipeline.py diff`. Never interchangeable.

## 3. The "Missing File" Exception
**Trigger:** A file is referenced (e.g., in imports) but missing from `ai_context.txt` (likely ignored).
**Action:** Use standard `read_file` for that specific path only. This is a "Surgical Strike."

## 4. Documentation & Big Change Strategy (Smart Delta)
**Task:** Updating `DEPLOYMENT.md`, `ARCHITECTURE.md`, or a `[Feature]_spec.md`.
**Default Action:** Use the **Delta Protocol** (`run_agent.bat --changes`) first.
**Escalation Rule**: Only run "Cold Start" IF: Delta shows > 15 files changed · `GENERATION ID` is over 4 hours old · mental model is broken. "Cold Start" should be the **last resort** to save user tokens.

## 5. Implementation & Hygiene Rules
- **Root Awareness:** Always run `run_agent.bat` from the active project root. The agent validates this automatically.
- **Hallucination Check:** If you cannot find a file, run the agent again. Do not invent paths.
- **Token Hygiene:** Do not dump full file contents into the chat. Output only the necessary code blocks or diffs.
- **Continuity Check:** Always state "Using context from Turn X" to confirm you are using session memory.
- **Post-Edit Compliance:** After every set of edits, run `run_agent.bat --changes` and state "Delta verified from Turn X".

## 6. Token Budget Awareness
- ✅ **< 200K tokens** — Safe to paste into AI context.
- 🟡 **200K–500K tokens** — Consider using `--changes` for targeted updates.
- 🔴 **> 500K tokens** — Context will be truncated by most models. Tighten `.aicontextignore.txt`.

If you start a complex task WITHOUT running `run_agent.bat`, or request a full context upload when Turn Count < 30 and context already exists in history, you are in violation of core protocols (agent mode).

If you begin writing code without confirming the uploaded context file is present, you are in violation of the Browser Mode Override. State `"Using uploaded context from [filename]"` before any implementation (browser mode).

---

## 7. Pipeline Operations Reference

> **§7 has been extracted to `0_pipeline_ops_ref.md`** to stay under the 12 000 character file limit.
> Load `0_pipeline_ops_ref.md` at the start of any session involving pipeline artifacts or dumps.
> Contains: §7A Folder Map · §7B All Commands · §7C Artifact Resolution (naming-convention-based — no pointer files) · §7D Dump Flow · §7E Headers · §7F Git-Ignore.

**Quick reference (full syntax in `0_pipeline_ops_ref.md`):**
```
pipeline.py save      --feature X --type plan|log|delta --file path   ← finished artifact
pipeline.py find      --feature X --type plan|log|delta               ← get path to load
pipeline.py dump      --feature X --role R --file path                ← partial/mid-run save
pipeline.py dump-find --feature X                                      ← find latest dump to resume
pipeline.py diff      --old path --new path                           ← integrity check after move
pipeline.py status    [--feature X]                                    ← see what is saved
```
