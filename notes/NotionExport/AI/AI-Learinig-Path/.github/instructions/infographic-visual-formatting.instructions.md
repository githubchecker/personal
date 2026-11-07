---
description: 'Mandatory infographic visual formatting specification for all Markdown learning modules and notes. Standardizes GitHub-Flavored Markdown (GFM) rich presentation: colored KaTeX headings, Shields.io section banners, semantic colored bullets, colored bold keywords, 5-tier GFM alerts, styled Mermaid SVG diagrams, and diff block contrasts. Guarantees 100% content preservation while making content colorful for direct GitHub reading.'
applyTo: '**/*.md'
---

# Infographic Visual Formatting Guide — GitHub Markdown

> **Scope:** Mandatory presentation standard for all learning notes, road map modules, and lesson files in this workspace.  
> **Target Environment:** GitHub-Flavored Markdown (GFM) web preview and mobile app.  
> **Golden Invariant:** **NEVER drop, summarize, or alter existing educational text.** All visual engineering is strictly an additive styling layer over 100% of the content.

---

## 🎨 The Semantic Color Palette

Every color in this design system carries a consistent semantic meaning across all lessons:

| Tone | Hex Code | Visual Identity | Semantic Purpose & Usage |
| :--- | :---: | :---: | :--- |
| **Royal Navy** | `#0D47A1` / `#1565C0` | 🔵 | Master H1 Titles, Stage 0, Core Architecture, Python Engine, Interpreter. |
| **Cyan / Sky** | `#0288D1` / `#01579B` | 🔷 | "Builds on" anchors, client-side requests, introductory concepts. |
| **Teal / Emerald** | `#00695C` / `#00897B` | 🟢 | Stage 1 Simple Ideas, "Unlocks" anchors, safe/idiomatic paths, outputs. |
| **Forest Green** | `#1B5E20` / `#2E7D32` | 📗 | Quick Reference, package management (`pip`, `venv`), verified solutions, best practices. |
| **Amber / Rust** | `#BF360C` / `#D84315` | 🟠 | Stage 2 Mechanism, How It Works, step numbers, hardware/CPU execution. |
| **Deep Purple** | `#4A148C` / `#512DA8` | 🟣 | Key Terms / Vocabulary, "The Aha!" insight, AI Engineering connections. |
| **Crimson / Rose** | `#B71C1C` / `#D32F2F` | 🔴 | Traps, gotchas, STOP checkpoint questions, anti-patterns, error tables. |
| **Magenta / Plum**| `#880E4F` / `#AD1457` | 🛑 | Common Errors & Fixes, debugging headers, failure modes. |

---

## 🏷️ 1. Lesson Header & Navigation Standard

Every lesson must begin with a standardized 4-badge metadata row followed by the breadcrumb navigation bar:

```markdown
# $\Huge\color{#0D47A1}{\textsf{01 — How Python Runs and Setup}}$

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Curriculum](https://img.shields.io/badge/Roadmap-Phase%200.1-0288D1?style=for-the-badge&logo=compass&logoColor=white)](README.md)
[![Priority](https://img.shields.io/badge/Priority-MUST%20KNOW-D32F2F?style=for-the-badge&logo=target&logoColor=white)](../../AI%20Engineer%20Architect%20Road%20Map.md)
[![Status](https://img.shields.io/badge/Status-Foundational-2E7D32?style=for-the-badge&logo=checkmarx&logoColor=white)](#)

> $\color{#546E7A}\mathbf{Navigation:}$ **Phase 0** · **Module 0.1** · **Lesson 1 of 16** · [Phase 0.1 — Python Index](README.md) · [Next: 02 Variables, Types & Operators →](02%20Variables%20Types%20and%20Operators.md)

---
```

---

## 🏷️ 2. Section Banners (Shields.io `for-the-badge`)

Place high-contrast SVG banners before each major section to establish distinct visual chapters:

| Section | Badge Markdown |
| :--- | :--- |
| **Stage 0** | `![Stage 0](https://img.shields.io/badge/STAGE%200-CONCEPT%20MAP-0288D1?style=for-the-badge&logo=gitbook&logoColor=white)` |
| **Key Terms** | `![Key Terms](https://img.shields.io/badge/KEY%20TERMS-GLOSSARY-7B1FA2?style=for-the-badge&logo=book&logoColor=white)` |
| **Stage 1** | `![Stage 1](https://img.shields.io/badge/STAGE%201-THE%20SIMPLE%20IDEA-00897B?style=for-the-badge&logo=lightbulb&logoColor=white)` |
| **Stage 2** | `![Stage 2](https://img.shields.io/badge/STAGE%202-HOW%20IT%20ACTUALLY%20WORKS-E65100?style=for-the-badge&logo=gear&logoColor=white)` |
| **Stage 3** | `![Stage 3](https://img.shields.io/badge/STAGE%203-IN%20PRACTICE%20%2F%20WHY%20IT%20MATTERS-1565C0?style=for-the-badge&logo=rocket&logoColor=white)` |
| **Variations** | `![Variations](https://img.shields.io/badge/COMPARISON-VARIATIONS%20%26%20WHEN%20TO%20USE-00838F?style=for-the-badge&logo=scales&logoColor=white)` |
| **Errors** | `![Errors](https://img.shields.io/badge/DEBUGGING-COMMON%20ERRORS%20%26%20FIXES-C2185B?style=for-the-badge&logo=debug&logoColor=white)` |
| **Quick Ref** | `![Quick Reference](https://img.shields.io/badge/CHEAT%20SHEET-QUICK%20REFERENCE-2E7D32?style=for-the-badge&logo=codeigniter&logoColor=white)` |
| **STOP Check**| `![Stop Check](https://img.shields.io/badge/CHECKPOINT-STOP%20%26%20SELF%20CHECK-D32F2F?style=for-the-badge&logo=stop&logoColor=white)` |

---

## 🔠 3. Colored Headings & Subheadings (KaTeX Typography)

Use KaTeX math formulas within Markdown headers. Always wrap title text in `\textsf{...}` to use a clean sans-serif font rather than italicized math variables:

```markdown
# $\Huge\color{#0D47A1}{\textsf{Master Title Here}}$

## 🗺️ $\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{Stage 0 — Concept Map}}$

### $\color{#D84315}\blacktriangleright\space\color{#BF360C}{\textsf{1.1 Subsection Title Here}}$

#### $\color{#4527A0}\blacklozenge\space\color{#283593}{\textsf{(a) Detailed Step / Variation Here}}$
```

> [!CAUTION]
> ### 🛑 GitHub KaTeX Sanitizer Rules (CRITICAL GOTCHA)
> 1. **NEVER use `&` or `\&` inside math blocks (`$...$` or `$$...$$`):**  
>    GitHub's markdown pre-processor converts `&` into `&amp;` *before* KaTeX runs. KaTeX chokes on the `&` in `&amp;` and displays a fatal red error box: `'&' can not be used here`. **Always use the plain English word `and` instead of `&` inside all KaTeX blocks.**
> 2. **Avoid `%` and `_` inside math text:**  
>    LaTeX treats `%` as comments and Markdown treats `_` as italics. Use plain words (e.g., `percent`) or keep them outside `$ ... $`.
> 3. **Always wrap words in `\textsf{...}`:**  
>    To prevent math mode from rendering text as italicized algebra variables, wrap readable labels in `\textsf{...}`.
> 4. **Use `\space` for spaces:**  
>    Math mode collapses whitespace by default; insert `\space` between words outside `\text{...}`.

---

## 🔹 4. Colored Bullets & List Accents

Replace plain gray Markdown list markers (`-` or `*`) with KaTeX colored geometric shapes:

```markdown
* $\color{#0288D1}\blacktriangleright$ **$\color{#01579B}{\textsf{Builds on:}}$** Prerequisite concept here.
* $\color{#00897B}\blacktriangleright$ **$\color{#004D40}{\textsf{Unlocks:}}$** Subsequent concept here.
* $\color{#2E7D32}\bullet$ **$\color{#1B5E20}{\textsf{Feature:}}$** Safe, recommended behavior here.
* $\color{#D32F2F}\blacktriangleright$ **$\color{#B71C1C}{\textsf{Pitfall:}}$** Bug or anti-pattern warning here.
```

---

## 🔤 5. Colored Bold Keywords & Table Cells

Apply consistent semantic inline coloring for vocabulary terms, table headers, and critical concept definitions:

### Inline Vocabulary Styling
- In definitions: `$\color{#0D47A1}\mathbf{Interpreter}$`
- In running text: `**$\color{#0D47A1}{\textsf{interpreted language}}$**`
- In critical traps: `**$\color{#D32F2F}{\textsf{Critical Step:}}$**`

### Colored Table Headers
Style markdown tables with colored KaTeX header cells:
```markdown
| $\color{#4A148C}\textsf{\textbf{Term}}$ | $\color{#00695C}\textsf{\textbf{One-Line Meaning}}$ |
| :--- | :--- |
| $\color{#0D47A1}\mathbf{Interpreter}$ | The program (`python.exe`) that translates code into actions. |
| $\color{#4A148C}\mathbf{Bytecode}$ | Compact machine-friendly instructions compiled before execution. |
```

---

## 📦 6. GitHub Flavored Markdown (GFM) 5-Color Alert Cards

Convert generic blockquotes and notes into official GitHub callout cards. GitHub automatically renders these with full-width tinted backgrounds, icons, and colored left borders:

### Blue Card — Context & Internal Mechanics
```markdown
> [!NOTE]
> ### $\color{#0D47A1}{\textsf{Under the Hood: Execution Mechanism}}$
> Explains internal runtime details, operating system behavior, or PATH mechanics.
```

### Green Card — Pro-Tips & Idiomatic Best Practices
```markdown
> [!TIP]
> ### $\color{#1B5E20}{\textsf{Pythonic Pro-Tip}}$
> Explains best practices, shortcuts, and efficient architectural patterns.
```

### Purple Card — Foundational Insights & Core Problems
```markdown
> [!IMPORTANT]
> ### $\color{#512DA8}{\textsf{The Core Problem / The "Aha!" Insight}}$
> Explains the exact pain point being solved or the single mental model unlock.
```

### Yellow / Amber Card — Gotchas & Traps
```markdown
> [!WARNING]
> ### $\color{#D84315}{\textsf{⚠️ THE POWERSHELL EXECUTION POLICY TRAP}}$
> Explains common pitfalls, silent bugs, and operating system permission issues.
```

### Red Card — Critical Warnings & Destructive Anti-Patterns
```markdown
> [!CAUTION]
> ### $\color{#B71C1C}{\textsf{Never Commit .venv to Git}}$
> Highlights memory leaks, dependency collisions, and breaking production errors.
```

---

## 📊 7. Colored Mermaid SVG Diagrams

Never leave architectural flows, execution pipelines, or dispatch mechanics as flat gray monospace text. Convert them into colored Mermaid SVGs with custom `style` directives:

```mermaid
flowchart LR
    A["📄 <b>your_script.py</b><br/><code>Source Code (Plain Text)</code>"] --> B["⚙️ <b>Python Interpreter</b><br/><code>Checks Syntax & Parses Tokens</code>"]
    B --> C["📦 <b>Bytecode (.pyc)</b><br/><code>Internal Compact Instructions</code>"]
    C --> D["🚀 <b>PVM (Virtual Machine)</b><br/><code>Executes against CPU & RAM</code>"]
    D --> E["🖥️ <b>System Output</b><br/><code>Printed Results / Actions</code>"]

    style A fill:#E1F5FE,stroke:#0288D1,stroke-width:2px,color:#01579B
    style B fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#E65100
    style C fill:#EDE7F6,stroke:#512DA8,stroke-width:2px,color:#311B92
    style D fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#1B5E20
    style E fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,color:#880E4F
```

---

## 🚥 8. `diff` Code Blocks for Approach Contrasts

When demonstrating "The Fragile / Anti-Pattern Way" versus "The Robust / Pythonic Solution", use ````diff ```` code blocks. GitHub highlights `-` lines in **light red** and `+` lines in **light green**:

```diff
- ❌ FRAGILE: Global pip install overwrites versions across projects
- pip install pydantic==2.8.2  # Crashes Project Alpha which requires v1.10!

+ ✅ SAFE: Isolated virtual environment sandbox
+ python -m venv .venv && source .venv/bin/activate
+ pip install pydantic==2.8.2  # Isolated safely inside project folder
```

---

## ⌨️ 9. Interactive Elements & Keycaps

* **Keyboard Shortcuts:** Wrap hotkeys in `<kbd>` tags:
  `<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>`
* **Directory Trees:** Use emoji file indicators (`📁 .venv/`, `⚙️ python.exe`, `📜 Activate.ps1`, `📄 main.py`).
* **Collapsible Self-Check Cards:**
  ```markdown
  <details>
  <summary><b>🔍 $\color{#0D47A1}{\textsf{Click to Reveal the Answer and Architectural Fix}}$</b></summary>
  
  <br/>
  
  ### $\color{#D32F2F}\blacktriangleright\space\color{#B71C1C}{\textsf{The Mistakes:}}$
  ...
  
  ### $\color{#2E7D32}\blacktriangleright\space\color{#1B5E20}{\textsf{The Proper Sequence:}}$
  ...
  
  </details>
  ```

---

## 📋 10. AI Assistant Execution Checklist

When authoring or re-formatting any lesson in this repository:
1. [ ] **Verify zero text loss:** Do not delete, rephrase, or drop existing paragraphs, code comments, or explanations.
2. [ ] **Header badges placed:** 4-badge row (Python, Curriculum, Priority, Status) present at the top.
3. [ ] **Shields.io banners:** Every major section opens with its designated SVG banner.
4. [ ] **Headings colored:** H1, H2, H3, H4 use KaTeX `\color` with proper geometric anchors and `\&` escaping.
5. [ ] **Bullets enhanced:** List items use `$\color{#Hex}\blacktriangleright$` or `$\color{#Hex}\bullet$`.
6. [ ] **Alert cards converted:** Generic notes and gotchas converted to official GFM alerts (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`).
7. [ ] **ASCII converted to Mermaid:** Text diagrams upgraded to colored Mermaid flowcharts.
8. [ ] **Diff highlighting used:** Anti-pattern vs recommended contrasts formatted in ````diff ```` blocks.
9. [ ] **STOP dropdown formatted:** Socratic answers enclosed in interactive `<details>` with colored headings.
