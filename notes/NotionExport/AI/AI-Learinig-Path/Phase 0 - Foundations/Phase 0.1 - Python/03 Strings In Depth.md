# 03 — Strings In Depth

> Phase 0 · Module 0.1 · Lesson 3 of 16

## 🗺️ Stage 0 — Concept Map

Text is everywhere in AI: prompts, model replies, document chunks, JSON. **Strings** are Python's
text type, and you'll manipulate them constantly — slicing, cleaning, searching, and building them
from pieces. This lesson goes deep on strings because comfort here pays off in every later phase.

## 🔑 New Terms (plain English)

- **String** — text, written in quotes.
- **Index** — a character's position, starting at `0`; `-1` is the last.
- **Slice** — a sub-range `s[start:stop]` (the `stop` is excluded).
- **Immutable** — can't be changed in place; string methods return a *new* string.
- **f-string** — `f"...{value}..."`, drops values into text.

## 🎈 Stage 1 — The Simple Idea (analogy: a bead necklace)

A **string** is an ordered sequence of characters — like beads on a string, each bead a letter,
digit, space, or symbol, in a fixed order. Because the order is fixed, every bead has a **position
(index)**, and you can grab one bead or a run of beads.

**The "Aha!":** strings are **immutable** — once made, you can't change a bead in place. Every
"edit" actually builds a **new** string. (This sounds limiting but prevents whole classes of bugs.)

## ⚙️ Stage 2 — How It Actually Works

### 3.1 Making strings

```python
a = "double quotes"
b = 'single quotes'          # identical; pick one and be consistent
c = "She said \"hi\""        # \" is an escaped quote; \n = newline, \t = tab
d = """A multi-line
string spanning
several lines."""            # triple quotes keep the line breaks
e = r"C:\new\path"           # r"" = raw string: backslashes are literal (great for Windows paths)
```

### 3.2 Indexing & slicing (the most important skill)

Positions start at **0**. Negative positions count from the end (`-1` is the last character).

```python
s = "PYTHON"
#    012345          (and from the right: -6 -5 -4 -3 -2 -1)
print(s[0])     # 'P'   first character
print(s[-1])    # 'N'   last character

# SLICING: s[start:stop]  -> from start UP TO (but NOT including) stop
print(s[0:3])   # 'PYT'  positions 0,1,2
print(s[2:])    # 'THON' from 2 to the end
print(s[:3])    # 'PYT'  from start to 3
print(s[::2])   # 'PTO'  every 2nd char (s[start:stop:step])
print(s[::-1])  # 'NOHTYP' a reversed copy (handy trick)
```

The "up to but not including stop" rule is consistent across all Python sequences — learn it once.

### 3.3 Length and membership

```python
print(len("hello"))        # 5
print("th" in "python")    # True   — substring check
print("z" not in "python") # True
```

### 3.4 Essential string methods

Methods return a **new** string (remember: immutable). A tour of the ones you'll actually use:

```python
text = "  Hello, World  "

print(text.strip())            # 'Hello, World'  — remove leading/trailing whitespace
print(text.lower())            # '  hello, world  '
print(text.upper())            # '  HELLO, WORLD  '
print("hello".capitalize())    # 'Hello'
print("a,b,c".split(","))      # ['a', 'b', 'c']  — string -> list
print("-".join(["a", "b"]))    # 'a-b'            — list -> string
print("python".replace("p", "P"))   # 'Python'
print("python".startswith("py"))    # True
print("data.csv".endswith(".csv"))  # True
print("python".find("th"))     # 2   — index of first match, or -1 if not found
print("a1b2".isalnum())        # True — only letters/digits?
print("Hello".count("l"))      # 2
```

`split()` and `join()` are a pair you'll use a lot: `split` breaks text apart, `join` glues a list
back into text.

### 3.5 f-strings (the modern way to build text)

Prefix a string with `f` and put expressions inside `{ }`:

```python
name = "Ada"
score = 0.8736

print(f"{name} scored {score}")          # Ada scored 0.8736
print(f"{name.upper()} scored {score:.2%}")  # ADA scored 87.36%  — expressions + formatting

# Format specifiers after a colon control the look:
pi = 3.14159
print(f"{pi:.2f}")     # '3.14'   — 2 decimal places
print(f"{42:5d}")      # '   42'  — width 5, right-aligned
print(f"{42:<5}|")     # '42   |' — left-aligned in width 5
print(f"{1000000:,}")  # '1,000,000' — thousands separator
```

## 🚀 Stage 3 — In Practice / Why It Matters

You'll build prompts with f-strings (`f"Answer using: {context}"`), clean model output with
`.strip()`, split documents on delimiters, and check `"error" in response.lower()`. The token
splitter you'll write later leans entirely on `split()` and `join()`.

**Common beginner mistakes (the reasoning):**
1. **Trying to mutate a string** — `s[0] = "x"` raises `TypeError`. Build a new one instead:
   `"x" + s[1:]`. *Reason:* strings are immutable.
2. **Forgetting methods return a new value** — `text.strip()` alone does nothing lasting; you must
   capture it: `text = text.strip()`.
3. **Off-by-one in slices** — `s[0:3]` gives 3 chars (0,1,2), not 4. The stop index is excluded.
4. **`+` to build big strings in a loop** is slow and clumsy — collect parts in a list and
   `"".join(parts)` at the end.

### Try it yourself
Given `path = "report_2026.pdf"`, use slicing and/or methods to print the extension (`pdf`) and
the name without extension (`report_2026`).

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `TypeError: 'str' object does not support item assignment` | `s[0] = "x"` — strings are immutable | Build a new string: `"x" + s[1:]` |
| `IndexError: string index out of range` | Asked for a position past the end | Check `len(s)`; last index is `len(s) - 1` |
| `text.strip()` "did nothing" | Didn't capture the result | `text = text.strip()` |
| `.find(...)` returns `-1` | Substring not present | `-1` means "not found" — check before using it |

## 📌 Quick Reference

```python
s[0]; s[-1]; s[0:3]; s[::-1]          # index, slice, reverse
s.strip(); s.lower(); s.upper()
"a,b".split(","); "-".join(["a", "b"])  # split / join
s.replace("a", "b"); s.startswith("x"); "x" in s
f"{name} scored {score:.2%}"          # formatting
```

## 🛑 STOP — Self-Check

What does this print, and why doesn't `greeting` change?

```python
greeting = "hello"
greeting.upper()
print(greeting)
```

<details><summary>Answer</summary>

It prints **`hello`** (lowercase). `greeting.upper()` *returns* a new string `"HELLO"`, but the
result is thrown away because it isn't assigned anywhere — and strings are **immutable**, so the
original `greeting` is untouched. To keep it you'd write `greeting = greeting.upper()`.
</details>
