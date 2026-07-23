# 01 — How Python Runs & Setup

> Phase 0 · Module 0.1 · Lesson 1 of 16

## 🗺️ Stage 0 — Concept Map

Before writing real Python, you need a clear picture of **what Python actually is**, **how your
code runs**, and **how to set up a clean place to work**. Everything else in this module — and
every AI script later — sits on top of this. This lesson has no AI in it yet; it's the ground
floor.

By the end you'll be able to: install Python, open an interactive session, write and run a `.py`
file, and explain (simply) what happens when you press "run".

## 🔑 New Terms (plain English)

- **Interpreter** — the `python` program that reads and runs your code.
- **Source code** — the text you write in a `.py` file.
- **REPL** — an interactive prompt that runs one line at a time.
- **PATH** — the list of folders your terminal searches for programs.
- **Bytecode** — the compact internal form Python turns your code into before running.

## 🎈 Stage 1 — The Simple Idea (analogy: a live translator)

A computer's processor only understands raw machine instructions — not English, not Python.
**Python is a translator that stands between you and the machine.** You write readable Python; the
translator reads it line by line and tells the machine what to do, *as it goes*.

That "as it goes" part is what makes Python an **interpreted language**: there's no long "compile
the whole program first" step you have to run manually. You hand the translator a file and it
starts working through it immediately.

**The "Aha!":** "Python" means two things — **the language** (the rules you write in) and **the
interpreter** (the program named `python` that reads and runs your code). When people say "install
Python," they mean install the interpreter.

## ⚙️ Stage 2 — How It Actually Works

### 2.1 What happens when you run a program

```
your_file.py  ──►  Python interpreter  ──►  bytecode  ──►  runs on your machine
 (you write)        (reads & translates)    (internal)      (you see output)
```

- You write **source code** in a `.py` file (plain text).
- The **interpreter** reads it, quietly converts it to **bytecode** (a compact internal form —
  you never edit this), and executes it.
- You don't manage any of the middle steps; you just run the file.

### 2.2 Installing Python (Windows)

1. Get it from the official site **python.org/downloads** (or the Microsoft Store).
2. **Important:** on the installer's first screen, tick **"Add python.exe to PATH"**. This lets you
   type `python` in any terminal. (**PATH** — the list of folders your terminal searches for
   programs. If Python isn't on it, the terminal says "not recognized".)
3. Confirm it worked — open a terminal and check the version:

```powershell
python --version        # e.g. Python 3.13.1
# On Windows you may also have the launcher:
py --version            # the "py" launcher picks an installed Python for you
```

### 2.3 Two ways to run Python

**(a) The REPL — an interactive scratchpad.** **REPL** = Read-Eval-Print Loop: it reads one line,
evaluates it, prints the result, and loops. Great for quick experiments.

```powershell
python                  # start the REPL; you'll see the ">>>" prompt
>>> 2 + 2
4
>>> "hello".upper()
'HELLO'
>>> exit()              # leave the REPL (or press Ctrl+Z then Enter on Windows)
```

**(b) A script file — the real way to build things.** Put code in a file and run the file.

```python
# hello.py  —  your first program
# print(...) sends text to the screen (the "standard output").
print("Hello, Python!")

name = "Ada"                     # a variable (next lesson covers these)
print(f"Welcome, {name}!")       # an f-string drops the variable into the text
```

Run it:

```powershell
python hello.py
# Hello, Python!
# Welcome, Ada!
```

### 2.4 Your editor: VS Code

You're already in VS Code. Install the **Python extension** (Microsoft) for syntax highlighting,
the green "Run" arrow, and error squiggles. A `.py` file + the Run button runs exactly the command
above for you.

### 2.5 Comments and the golden rule of indentation

```python
# A line starting with # is a COMMENT — Python ignores it. Use comments to explain WHY.
print("step 1")     # a comment can also sit at the end of a line

# Python uses INDENTATION (leading spaces) to group code — 4 spaces is the standard.
# (We'll use this constantly from the Control Flow lesson onward.)
```

## 🚀 Stage 3 — In Practice / Why It Matters

Every later lesson is just "write code in a `.py` file, run it with `python file.py`, read the
output." The REPL is your friend for testing a single idea ("what does `"a,b".split(",")` do?")
without making a file.

**Common beginner mistakes (the reasoning):**
1. **`'python' is not recognized`** — Python isn't on PATH. Reinstall and tick "Add to PATH", or
   use `py` instead of `python` on Windows. *Reason:* the terminal can't find the interpreter.
2. **Editing the wrong file / not saving** — you run `hello.py` but see old output. Save the file
   (Ctrl+S) before running. *Reason:* Python runs what's on disk, not unsaved edits.
3. **Confusing the language with the interpreter** — "Python is slow/fast" usually refers to the
   interpreter's behaviour, not the syntax you write.

### Try it yourself
Create `me.py` that prints your name and what `7 // 2` evaluates to (guess first, then run it).

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `'python' is not recognized...` | Python isn't on PATH | Reinstall ticking "Add to PATH", or use `py` |
| `python: can't open file 'x.py'` | Wrong folder or filename typo | `cd` to the file's folder; check the name |
| `SyntaxError: ...` when you run | A typo in the code | Go to the line number, fix it, **save** |
| Old output after editing | File wasn't saved | Save (Ctrl+S) before running |

## 📌 Quick Reference

```powershell
python --version      # check it's installed
python file.py        # run a script
python                # start the REPL (type exit() to leave)
```
- `#` starts a comment · indent with **4 spaces** · **save** before you run.

## 🛑 STOP — Self-Check

Someone says: *"Python doesn't need compiling."* In one sentence, what's really happening when you
run `python hello.py`?

<details><summary>Answer</summary>

There *is* a translation step — the **interpreter** reads your source and compiles it to internal
**bytecode**, then runs it — but it happens **automatically, line by line, each time you run the
file**, so you never invoke a separate compile step yourself. "Interpreted" means *you* don't
manage compilation, not that none occurs.
</details>
