# Browser Session Continuation Dump — Generic Rule
**Version:** 1.0
**Scope:** Any Claude browser session (claude.ai) doing extended work
**Purpose:** Ensure zero context loss when switching to a new session

---

## When to Generate a Continuation Dump

### Trigger A — User-initiated (explicit)
User says any of:
- "we're near the limit"
- "session is almost full"
- "generate a continuation dump"
- "we need to continue in a new session"
- "context is running out"

### Trigger B — Self-initiated (heuristic -- volunteer proactively)
Generate or OFFER to generate a dump when ALL of the following are true:
1. The conversation has 15+ visible back-and-forth turns
1.5. The conversation has 25+ turns AND the current task involves pipeline artifacts, implementation planning, or multi-file code changes (triggers proactive dump regardless of task completion status — the Turn 30 hard reset in `0_context_rules.md` Section 1 is approaching).
2. Multiple complex tasks have been completed (code written, files designed, decisions made)
3. The most recent user message contains new work OR a new question
4. You have not generated a dump in this session yet

When Trigger B fires, say at the END of your normal response:
> "[!] This session is getting long. I recommend generating a continuation dump
> before we go further so a new session can pick up without loss. Say
> 'generate continuation dump' when ready."

Do NOT interrupt the current response to generate a dump -- finish the task first.

### Trigger C — Forced (mandatory, no opt-out)
If you notice you are producing noticeably shorter responses than earlier in the
session, or you are omitting details you would normally include, generate the dump
immediately regardless of whether the user asked. Preface it with:
> "[!] I am compressing responses -- likely near context limit. Generating
> continuation dump now before quality degrades further."

---

## Continuation Dump Template

Use this exact structure. Fill every section. Do not skip sections even if they
seem short -- a missing section breaks the chain.

```markdown
<!-- ============================================================ -->
<!-- CONTINUATION DUMP                                            -->
<!-- Session: [one-line description of what this session was for] -->
<!-- Dumped:  [approximate date/time if known]                    -->
<!-- Resume:  [exact task or question to resume from]             -->
<!-- ============================================================ -->

# Continuation Dump: [Session Title]

---

## 1. SESSION PURPOSE
[1-3 sentences. What was this session trying to accomplish?
What is the end goal that may not be finished yet?]

---

## 2. CURRENT STATE (what is true RIGHT NOW)
[Describe the state of the work as of this dump.
Use bullet points. Be specific -- version numbers, file names, exact values.
This is what the new session reads first to get oriented.]

- [item: current value / status]
- [item: current value / status]

---

## 3. COMPLETED WORK (do not repeat in new session)
[List everything that is DONE and should NOT be re-done.
New session must treat these as closed.]

| # | What was done | Key detail / output |
|---|---------------|---------------------|
| 1 | [task] | [result / file / decision] |
| 2 | [task] | [result / file / decision] |

---

## 4. IN-PROGRESS WORK (resume here)
[The specific task or question that was interrupted.
Include enough detail that the new session can pick up mid-task
without starting over. If a code block was being written, include
the partial output and describe what is missing.]

**Task:** [exact task name or description]
**Progress:** [what has been done within this task]
**Next step:** [the exact next action required]
**Blockers:** [anything that needs resolving before next step, or NONE]

---

## 5. PENDING WORK (queue after resume)
[Everything that needs to happen AFTER the resumed task, in order.
Be specific enough that the new session doesn't need to re-derive the list.]

| Priority | Task | Why / depends on |
|----------|------|-----------------|
| P0 | [task] | [context] |
| P1 | [task] | [context] |

---

## 6. KEY DECISIONS MADE
[Decisions that were explicitly made in this session that the new session
must honour. Include the reasoning so the new session doesn't reverse them.]

| Decision | Rationale | Alternatives rejected |
|----------|-----------|-----------------------|
| [what was decided] | [why] | [what was considered and rejected] |

---

## 7. KNOWN ISSUES / WATCH-OUTS
[Anything the new session needs to be careful about.
Traps, gotchas, edge cases discovered during this session.
Non-obvious constraints that are easy to get wrong.]

- [issue]: [description and what to do / avoid]

---

## 8. OPEN QUESTIONS (not yet resolved)
[Questions that came up during the session that were NOT answered.
New session may need to answer these before proceeding.]

| # | Question | Why it matters | Best guess if forced |
|---|----------|---------------|---------------------|
| 1 | [question] | [impact] | [guess or UNKNOWN] |

---

## 9. FILES / ARTIFACTS PRODUCED THIS SESSION
[Every file created or modified. New session needs this to avoid re-creating
things that already exist, and to know which version is current.]

| File | Location | Status | Notes |
|------|----------|--------|-------|
| [filename] | [path] | NEW / MODIFIED / DELETED | [what changed] |

---

## 10. CONTEXT THE NEW SESSION NEEDS
[What to upload or provide at the start of the new session.
Be explicit -- "upload X" not "provide relevant files".]

Upload these:
- [ ] This dump file
- [ ] [specific file 1] -- needed for [reason]
- [ ] [specific file 2] -- needed for [reason]

Say this to start:
```
[exact trigger phrase or opening message for the new session]
```

---

## 11. CONVENTIONS / STYLE RULES ESTABLISHED THIS SESSION
[Any formatting, naming, or style decisions made during this session
that the new session must follow for consistency.
Only include things that are non-obvious or were explicitly decided here.]

- [convention]: [rule]

---

*End of Continuation Dump.*
*New session: read sections 1-2 for orientation, skip section 3,
resume from section 4, work through section 5 in order.*
```

---

## Rules for Filling the Template

**Section 2 (Current State):**
Write it as if explaining to someone who has never seen this session.
Do not assume they remember anything. Every fact must be self-contained.

**Section 3 (Completed Work):**
When in doubt, include it. A false positive (listing something that could
be re-done) is better than a false negative (losing completed work).

**Section 4 (In-Progress):**
This is the most important section. If the session was interrupted
mid-task, reproduce the partial output in full so the new session
continues from where it left off, not from scratch.

**Section 5 (Pending Work):**
Prioritise ruthlessly. P0 = blocks everything. P1 = important but
not blocking. P2 = nice to have. P3 = can drop if needed.

**Section 7 (Watch-outs):**
Include anything you wish you had known at the start of this session.
This is institutional memory.

**Section 10 (Context Needed):**
The opening message for the new session should be copy-pasteable verbatim.
Don't make the user figure out what to say.

---

## Anti-Patterns (what makes a bad dump)

| Bad | Good |
|-----|------|
| "We were working on the pipeline" | "We were adding PR_REVIEWER as Stage 4.5 between IMPLEMENTER and DELTA in the TradeInDepthPro pipeline at D:\Code\repo\Utils\agent-settings\" |
| "Continue from where we left off" | "Resume from TASK-C2: add 06_PR_REVIEWER pack to sync_and_drop.bat" |
| "Various files were modified" | Table of every file with status NEW/MODIFIED and what changed |
| "The user knows the context" | Write as if the new session has zero memory of this conversation |
| Skipping Section 7 because "nothing went wrong" | Always fill it -- include what almost went wrong, what to watch for |
| "Upload the relevant files" | "Upload: rules_pack.zip, SESSION_CONTINUATION_DUMP.md, 20260226_1646_02_IMPLEMENTATION_PLAN.md" |

---

## Compact Variant (for simpler sessions)

For sessions with fewer than 5 completed tasks and a single clear resume point,
use this shorter form instead of the full template:

```markdown
# Quick Continuation Dump: [Title]
Dumped: [date]

## What this was
[2 sentences]

## Done (don't repeat)
- [item]
- [item]

## Resume here
[Exact task. Exact next step. Any partial output to continue from.]

## Then do
1. [next task]
2. [next task]

## Upload to new session
- This file
- [specific file]

## Say to start
"[trigger phrase]"
```

Use the full template for: any session with code/file production, multi-hour
sessions, pipeline/architecture work, anything with decisions that have
long-term impact.

Use the compact variant for: single-topic Q&A sessions, short writing tasks,
debugging sessions with a single clear resolution path.
