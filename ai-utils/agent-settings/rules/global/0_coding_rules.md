---
trigger: always_on
---
> ⚠️ **FILE SIZE LIMIT: 12 000 characters.** Keep this file under 12 000 chars. Split into a `_ref.md` companion if content must grow — never exceed this limit.

# Global Coding Rules (AntiGravity)

These rules define the standards and behaviors for code generation and modification.

## 1. Focused and Minimal Changes
- **Strict Scope**: Do not touch code that is not directly related to the user's request.
- **Minimalism**: Implement only the requested suggestion or fix. Avoid unnecessary refactoring or formatting changes in unrelated sections.

## 2. Preservation of Context
- **Comments**: Do NOT remove existing comments unless they are directly invalidated by the code change.
- **Documentation**: Preserve existing docstrings and inline documentation.

## 3. Reference Integrity and Contract Safety
- **Reference Checks**: When removing or updating code, run `grep_search` across the **full repository including all subfolders and all file extensions** (`.cs`, `.js`, `.html`, `.py`, `.ts`, `.md`, `.json`). Cross-language call sites (e.g., JS calling a C# COM object method, Python calling a C# API) must be explicitly checked. If any reference is found: update it immediately or list it as `⚠️ BROKEN REFERENCE: [file:line] — [old name]` in the task log. Do NOT mark a task complete with known broken references.
- **Contract Maintenance**: If only the internal logic of a function or method needs to change, strictly maintain the existing API contract (Input Parameters and Return Type) to prevent breaking changes.

## 4. Production-Grade Quality (SOLID)
- **SOLID Principles**: Adhere to SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) whenever applicable.
- **Maintainability**: Write clean, readable, and modular code suitable for a production environment.

## 5. Proactive Analysis and Advisory
- **Solution Analysis**: Critically analyze suggestions provided by the user.
- **Loophole Detection**: Identify potential security vulnerabilities, edge cases, or logic gaps in the proposed solution.
- **Better Alternatives**: If a more robust, efficient, or standard "production-grade" solution exists, explicitly alert the user and present the alternative for consideration.

## 6. Security First
- **Input Validation**: Always validate and sanitize external inputs to prevent injection attacks and unexpected behavior.
- **Secret Management**: NEVER hardcode secrets, API keys, or passwords. Suggest using environment variables or secure vaults.

## 7. Robust Error Handling
- **No Silent Failures**: Avoid empty `except` blocks. Log errors or re-raise them with context.
- **Specific Exceptions**: Catch specific exceptions rather than generic `Exception` whenever possible.

## 8. Code Style and Naming
- **Consistency**: Follow the existing coding style and naming conventions of the project (e.g., PEP8 for Python, CamelCase for C#).
- **Readability**: Use descriptive variable and function names that convey intent.

## 9. Performance Awareness
- **Efficiency**: Avoid obvious performance bottlenecks (e.g., nested loops on large datasets) unless necessary.
- **Resource Management**: Ensure resources (files, sockets, connections) are properly closed or disposed of (use `with` statements or `try/finally`).

## 10. Comprehensive Documentation
- **Self-Documenting Code:** Every non-trivial function must have a name or comment that states its purpose without requiring the reader to trace its implementation. A function named `DoIt()` or `Process()` with no comment fails this rule.


## 11. Code Modification Integrity (Anti-Duplication)
- **Negative Verification**: Before adding a line of code or configuration, explicitly verify if a conflicting or duplicate directive already exists. Replace the existing line instead of appending a new one.
- **Ghost Code Cleanup**: When updating logic, immediately remove the deprecated or commented-out version of the code to keep files clean.
- **Syntax Validity**: Ensure edits to structured files (YAML, JSON, XML) do not result in duplicate keys, empty lists, or invalid hierarchy.

> Violation examples: see `modules/violation_examples.md` §"Rule 11 — Append vs Replace"

## 12. Pre-Confirmation Diff Check (pipeline.py diff)
**Trigger:** Any time you claim "only location references changed" or "content is identical" after moving, renaming, or editing files.

**Rule: NEVER confirm content integrity based on memory or assumptions. ALWAYS verify and explicitly report the actual differences.**

### Agent Mode (terminal available)
You MUST run the diff tool and output the EXACT result to the user.

```bash
# Single file verification
python Utils\AI_Code\ai-utils\pipeline.py diff `
  --repo "[RepoRoot]\[ProjectFolder]" `
  --old  "relative/path/in/git/to/old/file.md" `
  --new  "[RepoRoot]\path\to\new\file.md"
```

**Output contract (token-efficient — only changed lines, never full file):**
- `STATUS: IDENTICAL` — content matches after encoding normalisation → safe to confirm
- `STATUS: MODIFIED (+N added, -M removed)` — lists exact added/removed lines → you MUST report these exact lines to the user
- Exit 0 = all identical · Exit 1 = differences found · Exit 2 = error

### Browser Mode (no terminal — script not available)
`pipeline.py` requires a local terminal and cannot run in browser sessions. You must rely on your analytical capabilities.

**Rule:**
1. You MUST read both the original file (from context/history) and the new file.
2. You MUST explicitly list the EXACT lines that differ. Do NOT make vague assumptions like "looks the same" or "only location changed".
3. You MUST state to the user exactly: `"Browser mode: manual review only. Run pipeline.py diff in agent mode for byte-exact verification."`

**When to use:**
- After moving files between directories or repos
- After any "location-only" rule/doc edit
- When user explicitly asks to verify that content was not altered
- During any DELTA or post-implementation verification phase