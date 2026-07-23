# 11 — Modules, Packages & Files

> Phase 0 · Module 0.1 · Lesson 11 of 16

## 🗺️ Stage 0 — Concept Map

Programs grow beyond one file, and they need to read/write data. This lesson covers **importing**
code (using Python's huge standard library and third-party packages), and **file I/O** (reading and
writing files, including JSON — the format AI APIs speak). It ties together venv/pip (Lesson 01)
and sets up real projects.

## 🔑 New Terms (plain English)

- **Module** — a `.py` file you can import.
- **Package** — a folder of related modules.
- **Standard library** — modules built into Python (no install needed).
- **Context manager (`with`)** — guarantees cleanup, e.g. closing a file.
- **JSON** — a text format for structured data, used by web APIs.

## 🎈 Stage 1 — The Simple Idea (analogy: a library of toolboxes)

You don't forge your own screwdriver — you grab one from a toolbox. A **module** is a toolbox (a
`.py` file full of ready-made functions); a **package** is a shelf of related toolboxes (a folder
of modules). `import` is you walking to the shelf and taking what you need. Python ships with a
vast built-in library, and `pip` installs more.

**The "Aha!":** most of what you need already exists. Your job is often to **import and combine**
existing tools, not write everything from scratch.

## ⚙️ Stage 2 — How It Actually Works

### 11.1 The import system

```python
import math                      # import the whole module; use with the prefix
print(math.sqrt(16))             # 4.0

from random import choice        # import ONE name directly (no prefix needed)
print(choice(["a", "b", "c"]))   # a random pick

import datetime as dt            # rename on import (a common shorthand)
print(dt.date.today())

# A module is just a .py file. If you have helpers.py with a function clean(),
# you import it the same way:  from helpers import clean
```

### 11.2 A quick tour of the standard library (built-in, no install)

```python
import os                 # operating system: environment variables, paths
import json               # read/write JSON (the language of web APIs)
from pathlib import Path  # modern, object-based file paths
from datetime import datetime
import random, math       # randomness and maths

print(os.environ.get("HOME"))         # read an environment variable safely
print(Path("data") / "file.txt")      # build a path with "/" — works on every OS
```

### 11.3 Third-party packages: pip + venv (recap, deeper)

```powershell
python -m venv .venv                 # create an isolated environment (Lesson 01)
.\.venv\Scripts\Activate.ps1         # activate it
pip install requests pydantic        # install packages INTO this venv
pip freeze > requirements.txt        # record exact versions so others can rebuild
pip install -r requirements.txt      # later: recreate the same environment
```

### 11.4 Reading and writing files with `with`

The `with` statement is a **context manager**: it guarantees the file is closed afterwards, even if
an error occurs.

```python
# WRITE: "w" mode creates/overwrites. The file auto-closes at the end of the "with" block.
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("line one\n")
    f.write("line two\n")

# READ: "r" mode (the default).
with open("notes.txt", "r", encoding="utf-8") as f:
    content = f.read()           # whole file as one string
print(content)

# Read line by line (memory-friendly for big files — note the generator idea from Lesson 08):
with open("notes.txt") as f:
    for line in f:
        print(line.strip())

# APPEND: "a" mode adds to the end without erasing.
with open("notes.txt", "a") as f:
    f.write("line three\n")
```

Always pass `encoding="utf-8"` for text so accented characters and emoji behave consistently.

### 11.5 JSON — the data format of APIs

```python
import json

data = {"name": "Ada", "scores": [90, 75], "active": True}

# Python object -> JSON text
text = json.dumps(data, indent=2)      # dumpS = "dump to String"
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)       # dump straight to a file

# JSON text -> Python object
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)              # load from a file -> dict
print(loaded["name"])                  # 'Ada'
```

### 11.6 The `__main__` guard

```python
def main():
    print("running as a script")

if __name__ == "__main__":   # True only when THIS file is run directly,
    main()                   # not when it's imported by another file
```

This lets a file work both as a runnable script and as an importable module of helpers.

## 🚀 Stage 3 — In Practice / Why It Matters

Loading documents (file I/O), parsing API responses (`json`), reading secrets from environment
variables (`os.environ`), and importing libraries (`openai`, `httpx`) are the daily mechanics of
AI engineering. The `with open(...)` pattern and `json.load/dump` show up in nearly every project.

**Common beginner mistakes (the reasoning):**
1. **Not using `with`** — manually `open()`-ing without closing leaks file handles. `with` closes
   automatically. *Reason:* the context manager handles cleanup even on errors.
2. **Wrong path assumptions** — relative paths are resolved from where you *run* Python, not where
   the file lives. Use `pathlib` and absolute paths when in doubt.
3. **Confusing `json.dumps` vs `json.dump`** — `dumps`/`loads` work with **strings**; `dump`/`load`
   work with **files**. The `s` means "string."
4. **Forgetting `encoding="utf-8"`** — causes garbled text or errors on non-ASCII content.

### Try it yourself
Write a dict to `profile.json`, then read it back and print one field. Confirm the file appears in
your folder and is human-readable.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'x'` | Not installed, or wrong venv active | `pip install x` in the **active** venv |
| `FileNotFoundError` | Wrong relative path | Use full/`pathlib` paths; check your cwd |
| Garbled / mojibake characters | Missing text encoding | `open(..., encoding="utf-8")` |
| `dumps` vs `dump` confusion | `s` = string, no `s` = file | `dumps`/`loads` = strings; `dump`/`load` = files |

## 📌 Quick Reference

```python
import math; from random import choice; import datetime as dt
with open("f.txt", "r", encoding="utf-8") as f:
    text = f.read()
import json
json.dump(obj, file); obj = json.load(file)      # files
if __name__ == "__main__":   # runs only when executed directly
    main()
```

## 🛑 STOP — Self-Check

Why is `with open("f.txt") as f:` preferred over plain `f = open("f.txt")`, and what's the
difference between `json.dump` and `json.dumps`?

<details><summary>Answer</summary>

`with open(...)` is a **context manager** that **automatically closes** the file when the block
ends — even if an error is raised inside — preventing leaked file handles. `json.dump` writes JSON
directly to a **file** object, while `json.dumps` (with an `s` for "string") returns JSON as a
**string** you can store or send. The same `s` distinction applies to `json.load` (file) vs
`json.loads` (string).
</details>
