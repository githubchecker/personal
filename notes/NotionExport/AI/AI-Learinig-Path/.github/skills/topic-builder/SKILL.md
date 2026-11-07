---
name: topic-builder
description: 'Research-first, technology-agnostic workflow that runs AUTOMATICALLY whenever building or expanding any learning topic/subtopic (no manual invocation or multi-step approval). Works for ANY technology or subject. Runs a FRESH scan of current job postings (plus official docs and reputable interview prep) to find the VITAL-FEW subtopics that matter for real-life job applications — NOT exhaustive coverage and NOT random blogs. If a workspace curriculum/Road Map exists it is the base anchor; the skill validates it against live reality, ADDS missing subtopics, and shows the importance weightage of each subtopic (MUST/SHOULD/OPTIONAL + JD frequency). Then it authors non-shallow beginner-first lessons in the workspace lesson format, marking optional/awareness content clearly (never skipped). USE WHEN: adding a topic/phase, deepening shallow coverage, or matching a reference course/JD.'
argument-hint: 'topic to research and build (e.g. "Kubernetes networking", "Phase 1 FastAPI", "React hooks")'
---

# Topic Builder — Research-First Lesson Generation

Build any learning topic the right way: **explore reality first, then write.** A curriculum lists
*topics* but rarely every required *subtopic* — lessons go shallow until validated against real
jobs, docs, and interviews. This skill prevents that.

It is **technology- and subject-agnostic**: the identical process works for FastAPI, Kubernetes,
React, Rust, data engineering, security, or anything else. Nothing here is hardcoded to one stack.

> ⚙️ **Automatic by default.** Apply this whenever building or expanding **any** topic/subtopic —
> no manual invocation, no multi-step approval. Keep it lightweight and stay in flow.

## When to use
- Starting a new topic/module/phase, or expanding/deepening an existing one.
- Verifying a topic is not missing subtopics that real jobs/docs/interviews expect.
- Deciding teaching order and how important each subtopic is.
- A lesson feels shallow, or the user supplies a reference course/JD to match or exceed.

## When NOT to use
- Teaching a single, already-scoped concept (just follow the lesson format directly).
- Pure Q&A with no authoring.

## Inputs
- The topic (from the argument, or ask the user).
- Any reference URLs / courses / JDs the user provides (treat as primary sources).
- The workspace curriculum/Road Map **if one exists for this topic** (optional anchor — see Step 1).

---

## Phase 1 — EXPLORE (fresh + JD-verified — vital-few, NOT exhaustive)

Goal: the **vital few** subtopics that genuinely matter for **real job applications** — a *narrow,
important-first selection* (not an exhaustive list of every possible topic, and **never from random
blogs or content farms**). Depth is the opposite of narrow: each subtopic you *do* select is then
covered **exhaustively** in Phase 2 (every real variation). Stop once the picture is clear
(usually 4–7 focused lookups).

### Step 1 — Anchor (only if a curriculum exists)
If the workspace has a curriculum/Road Map covering this topic, use it as the **base** for scope and
placement. If there is none (any topic/technology), derive the structure from the research below.
Either way, **validate against live reality and augment** — add missing subtopics, drop legacy ones.

### Step 2 — Fresh JD scan (PRIMARY signal) — 🔴 always do this
Run a **live scan of current job postings** for the role/skill. Do **not** rely on stale curriculum
percentages — re-scan reality every time. Use `fetch_webpage` / web search:
- Queries like `"<topic> developer jobs <current-year>"`, `"<topic> required skills job description"`,
  `site:linkedin.com/jobs <topic>`, plus reputable "most in-demand `<topic>` skills `<year>`" analyses.
- Sample **~8–15 postings/sources**; **tally which subtopics recur and roughly how often**
  (e.g. "appears in ~80% of JDs"). These **fresh** frequencies are the primary importance signal.
- Cross-check any curriculum/Road Map JD figures; prefer the **fresher** signal and **note drift**
  (skills rising/falling, new tools, deprecations).

### Step 3 — Official documentation
The canonical source for **current, correct** usage and the natural subtopic breakdown (one stable
version). Catches currency gaps a curriculum predates.

### Step 4 — Reputable interview prep
Well-known interview-question sources → what is actually **tested** (often differs from day-job use).

### Step 5 — (only if ordering is unclear) one respected course syllabus
To sanity-check **sequence/prerequisites** — not for breadth, and never blogs.

### Record per subtopic
**Importance** (`MUST` / `SHOULD` / `OPTIONAL`) · **JD signal** (fresh frequency, e.g. "~82% of JDs",
or Core / Niche / Legacy) · **order/prereqs** · **variants** (competing approaches — for each: *when to
use it*, *when to AVOID it / which sibling instead*, and its *main gotcha*, if the subtopic involves a
real choice) · **source**.

For every **`MUST`/high-JD** subtopic also capture, from the official docs, the **full set of real
variations** (the complete list a practitioner meets, not only the JD-named ones), and **for each
variation** its **key features, ✅ use-when, 🚫 avoid-when (which sibling instead), and ⚠️ gotcha**, plus
the **old/painful way** it replaces and the **under-the-hood** mechanism — so the lesson reads like a
true standalone reference, not a summary.

**Filter hard:** keep only what carries a real **JD/interview** signal. Blog-hype, or legacy with no
JD presence, is **dropped or noted once as awareness** — never pad the curriculum.

> **Two axes — don't confuse them.** "Vital few" governs **which topics** you include (importance
> gating). It does **not** mean shallow: once a topic is selected as `MUST`/high-JD, cover it
> **exhaustively** — every real variation a practitioner meets, like a complete reference doc. So:
> **narrow on topic selection, deep and complete within each important topic.**

**Gap-check:** flag subtopics the curriculum **omits but JDs require**, and curriculum items that are
now **legacy** (mark optional/awareness).

---

## Proceed (lightweight — no mandatory approval)

State the plan as a short ordered table, then **proceed to author** — stay in flow; do **not** block
for approval unless the scope is large/ambiguous, the research seriously contradicts the curriculum,
or the user asked to review first.

```
| # | Subtopic | Importance | JD signal (fresh) | Order/Prereq | Source |
|---|----------|-----------|-------------------|--------------|--------|
```

---

## Phase 2 — GENERATE (author the lessons)

Author the notes in the workspace lesson format
(`.github/instructions/lesson-format.instructions.md`), applying the mandatory visual styling in
(`.github/instructions/infographic-visual-formatting.instructions.md`), and any always-on guide (e.g. `AGENTS.md`):

- **Beginner-first, non-shallow.** Every `MUST`/`SHOULD` subtopic gets a real lesson: Concept Map
  (name **the problem** first) → 🔑 New Terms → analogy → How it works (fully-commented examples) →
  In practice → **⚖️ Variations & When to Use** (when a real choice exists) → 🐛 Common Errors
  (or 🧠 Common Misconceptions for concept topics) → 📌 Quick Reference → 🛑 STOP self-check.
- **Cover variations at every level.** Wherever a *subtopic within the lesson* has its own real
  alternatives, add an inline **"use X when…"** decision note right there — not only as the
  topic-level section. Only where the choice is genuine and important (never invent options).
- **Depth scales with importance (reference-grade for important topics).** For `MUST`/high-JD topics,
  make the lesson a **complete standalone reference**: a problem-first *old-way → new-way* contrast,
  **every real variation as its own named mini-reference** (Key Features + Syntax + **✅ use-when** +
  **🚫 avoid-when → which sibling instead** + **⚠️ gotcha**), a brief **under-the-hood** note, and a
  **comparison table** that digests those use/avoid lines. `OPTIONAL`/awareness gets a concise overview.
  (Importance picks the topics; *within* an important topic, be exhaustive — each variation must carry
  its own use / avoid / gotcha, not a single shared 'when to use'.)
- **Optional ≠ omitted.** Write `OPTIONAL`/awareness subtopics too, clearly headed `(Optional)` /
  `[OPTIONAL — awareness]`, concise but real. Never silently skip them.
- **Order matters.** Teach in dependency order; number files so the order is obvious.
- **Define every term** before use; link the workspace glossary and add new terms to it (create one
  if none exists).
- **Save** under the appropriate topic/phase folder, with an index/README that links lessons in order
  and marks the optional ones.

## Quality gates (check before finishing)
- [ ] **Fresh JD scan done** — importance comes from *current* postings, not just stale curriculum data.
- [ ] **Infographic visual formatting applied** — 4-badge header, Shields.io banners, KaTeX colored headings, geometric bullets, 5-tier GFM alerts, styled Mermaid flowcharts, diff comparisons, and zero text dropped (per `infographic-visual-formatting.instructions.md`).
- [ ] **Depth gate (MUST topics) — NON-NEGOTIABLE.** Each `MUST`/high-JD lesson reads like a standalone
  reference, *not* a summary: problem-first old→new contrast, **every variation a mini-reference** (Key
  Features + real Syntax + ✅ use / 🚫 avoid→sibling / ⚠️ gotcha), a runnable commented example, under-the-
  hood, errors table, cheat-sheet. **Reject any MUST lesson that is mostly one-line bullets** — terse
  speed-writing is a failure even if coverage is right. Compare against a top course; if it's thinner, deepen.
- [ ] Every `MUST` subtopic maps to a real JD/interview signal (recurring in postings), not blog-hype.
- [ ] Every `MUST`/`SHOULD` subtopic has a lesson; none silently dropped; optionals labelled.
- [ ] Lessons in dependency order and not shallow (examples + errors + cheat-sheet + STOP).
- [ ] New jargon defined and added to the glossary.
- [ ] **Beginner-language pass done** — re-read as a beginner: no unexplained jargon; plain everyday
  words preferred over academic ones; every hard term glossed in the same sentence.
- [ ] **Links resolve** — index and cross-links point to files that exist (no broken paths).
- [ ] **Emoji integrity** — after bulk emoji edits, verify no corrupted characters:
  ```powershell
  Get-ChildItem "<dir>\*.md" | ForEach-Object { $t=[IO.File]::ReadAllText($_.FullName); "{0}: {1}" -f $_.Name, ([regex]::Matches($t,[char]0xFFFD)).Count }
  ```
  If any `U+FFFD` appear, repair and rewrite as UTF-8 (no BOM) before finishing.

## Notes
- **Adapts to the workspace:** if there is no curriculum/Road Map or glossary, the skill still works —
  it derives structure from the research and creates the index/glossary as needed.
- For a brand-new *broad* subject from scratch, a heavyweight curriculum generator (if the workspace
  has one) is an alternative; this skill (research → author in the lesson format) is the default.
- Prefer the `Explore` subagent or parallel `fetch_webpage` calls to gather sources efficiently.

## Anti-patterns
- Authoring before the fresh JD scan + subtopic list.
- Relying only on stale curriculum percentages (always re-scan live JDs).
- Copying a curriculum's topic list without reality-checking subtopics.
- Dropping optional topics instead of labelling them.
- Shallow lessons with no runnable examples, errors, or self-check.
- Leaving broken links or corrupted emoji after a build.
