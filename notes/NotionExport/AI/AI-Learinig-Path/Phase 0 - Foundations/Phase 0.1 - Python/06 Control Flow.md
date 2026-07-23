# 06 — Control Flow

> Phase 0 · Module 0.1 · Lesson 6 of 16

## 🗺️ Stage 0 — Concept Map

So far code runs top to bottom, once. **Control flow** lets a program **make decisions** (`if`)
and **repeat work** (loops). This is where programs start to feel alive — and where indentation
(Lesson 01) becomes load-bearing. Every algorithm, every data pipeline, every agent loop is built
from these.

## 🔑 New Terms (plain English)

- **Condition** — an expression that evaluates to True or False.
- **Branch** — choosing which code runs (`if` / `elif` / `else`).
- **Loop** — repeating a block (`while`, `for`).
- **`break` / `continue`** — exit a loop early / skip to the next round.
- **`range`** — generates a sequence of numbers to loop over.

## 🎈 Stage 1 — The Simple Idea (analogy: a recipe with choices and repeats)

A recipe sometimes says *"if the dough is too dry, add water"* (a decision) and *"stir until
smooth"* (a repeat). Control flow gives your code those two powers:
- **Branching** — choose which steps to run based on a condition.
- **Looping** — run a block again and again until something changes.

**The "Aha!":** the **indented block** under an `if`/`for`/`while` is the body that those
statements control. Indentation *is* the grouping — there are no braces.

## ⚙️ Stage 2 — How It Actually Works

### 6.1 `if` / `elif` / `else`

```python
score = 72

if score >= 90:                 # condition: an expression that's True or False
    grade = "A"
elif score >= 75:               # checked only if the above was False
    grade = "B"
elif score >= 60:
    grade = "C"
else:                           # runs if none of the above matched
    grade = "F"

print(grade)                    # 'C'
```

Conditions use comparison (`==`, `<`, `>=`, ...) and logical (`and`, `or`, `not`) operators, and
they respect truthiness (Lesson 02):

```python
name = ""
if not name:                    # empty string is falsy
    print("name is missing")

age = 25
if 18 <= age < 65:              # Python allows chained comparisons
    print("working age")
```

### 6.2 `while` loops — repeat until a condition fails

```python
count = 3
while count > 0:                # keep looping while this stays True
    print(count)
    count -= 1                  # MUST move toward the exit, or you loop forever
print("liftoff")
```

`break` exits a loop early; `continue` skips to the next iteration:

```python
n = 0
while True:                     # an intentional "loop forever" — exit with break
    n += 1
    if n == 3:
        continue                # skip printing 3
    if n > 5:
        break                   # leave the loop
    print(n)                    # 1 2 4 5
```

### 6.3 `for` loops — walk through a collection

```python
for fruit in ["apple", "banana"]:   # the standard iteration
    print(fruit)

for i in range(5):              # range(5) -> 0,1,2,3,4 (stop is excluded)
    print(i)

for i in range(2, 10, 2):       # range(start, stop, step) -> 2,4,6,8
    print(i)

# Iterate a dict's pairs (from Lesson 05):
for key, value in {"a": 1, "b": 2}.items():
    print(key, value)
```

A loop can have an `else` that runs only if the loop finished **without** `break` (occasionally
handy for "searched everything, found nothing"):

```python
for x in [1, 2, 3]:
    if x == 9:
        print("found")
        break
else:
    print("not found")          # runs because we never broke
```

### 6.4 `match` — clean multi-way branching (modern Python)

```python
command = "start"

match command:                  # compares the value against each "case"
    case "start":
        print("starting...")
    case "stop":
        print("stopping...")
    case _:                     # "_" is the catch-all (like else)
        print("unknown command")
```

Use `match` when you'd otherwise write a long `if/elif` chain comparing one value to many options.

## 🚀 Stage 3 — In Practice / Why It Matters

Branching decides which model or tool to call; loops process every document chunk, retry failed
API calls, or drive an agent's "think → act → observe" cycle. Comfort with `for`, `range`,
`break`, and `continue` is non-negotiable for everything ahead.

**Common beginner mistakes (the reasoning):**
1. **Infinite `while`** — forgetting to change the condition variable. Always ensure progress
   toward the exit (`count -= 1`). *Reason:* the loop only stops when the condition becomes False.
2. **Indentation errors** — mixing tabs/spaces or uneven indents under `if`/`for`. Use 4 spaces
   consistently. *Reason:* indentation defines the block; unevenness changes meaning or errors.
3. **Modifying a list while looping over it** — deleting items mid-iteration skips elements. Loop
   over a copy (`for x in items[:]:`) or build a new list instead.
4. **Off-by-one with `range`** — `range(5)` is `0..4`, not `1..5`; the stop is excluded.

### Try it yourself
Use a `for` loop and `range` to print only the even numbers from 1 to 20, then rewrite it using
`continue` to skip odds.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `IndentationError: expected an indented block` | No indented body under `if`/`for`/`def` | Indent the body 4 spaces |
| `TabError: inconsistent use of tabs and spaces` | Mixed tabs and spaces | Use spaces only (VS Code does this for `.py`) |
| Program hangs forever | A `while` condition never becomes False | Make the loop variable move toward the exit |
| `range(5)` gives `0..4`, not `1..5` | The `stop` value is excluded | Use `range(1, 6)` for 1–5 |

## 📌 Quick Reference

```python
if c: ...        elif c2: ...        else: ...
while cond: ...                # break / continue inside
for x in items: ...
for i in range(2, 10, 2): ...  # 2, 4, 6, 8
match value:
    case "a": ...
    case _: ...                # catch-all (like else)
```

## 🛑 STOP — Self-Check

What does this print, and why does it stop where it does?

```python
total = 0
for n in range(1, 100):
    total += n
    if total > 10:
        break
print(n, total)
```

<details><summary>Answer</summary>

It prints **`5 15`**. The loop adds 1+2+3+4+5 = 15; after adding 5, `total` (15) exceeds 10, so
`break` fires immediately, leaving `n` at **5**. `range(1, 100)` starts at 1, and `break` stops the
loop the first time the condition is met — so it never reaches 6.
</details>
