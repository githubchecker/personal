# 08 — Comprehensions & Generators

> Phase 0 · Module 0.1 · Lesson 8 of 16

## 🗺️ Stage 0 — Concept Map

You constantly need to **transform** one collection into another ("uppercase every word", "keep
only the long sentences"). **Comprehensions** are Python's concise, idiomatic way to do this in one
line. **Generators** do the same lazily — one item at a time — which is how you handle huge or
streaming data (like tokens arriving from an LLM) without running out of memory.

## 🔑 New Terms (plain English)

- **Comprehension** — a one-line way to build a list/dict/set from an iterable.
- **Generator** — produces items lazily, one at a time (saves memory).
- **`yield`** — hands out one value and pauses the function until the next request.
- **Iterator** — anything you can step through with a `for` loop / `next()`.
- **Lazy** — computed only when needed, not all upfront.

## 🎈 Stage 1 — The Simple Idea (analogy: an assembly line)

Imagine an assembly line: raw parts go in one end, each gets the same operation, finished parts
come out the other. A **comprehension** is that line written compactly: *"give me `f(x)` for every
`x` in this collection (optionally only if some condition holds)."*

A **generator** is the same line, but it makes each finished part **only when you ask for the next
one** — nothing is built ahead of time, so it uses almost no memory.

**The "Aha!":** comprehension = build the whole new list now; generator = produce items
on-demand, one at a time.

## ⚙️ Stage 2 — How It Actually Works

### 8.1 List comprehensions

The shape is: `[ expression for item in iterable ]`

```python
numbers = [1, 2, 3, 4]

squares = [n * n for n in numbers]          # [1, 4, 9, 16]

# The long-hand equivalent (same result, more lines):
squares_long = []
for n in numbers:
    squares_long.append(n * n)
```

Add a condition with `if` to **filter**:

```python
evens = [n for n in numbers if n % 2 == 0]   # [2, 4] — keep only where condition is True

words = ["hi", "hello", "hey", "greetings"]
long_words = [w.upper() for w in words if len(w) > 3]   # ['HELLO', 'GREETINGS']
```

### 8.2 Dict and set comprehensions

```python
# Dict comprehension: { key_expr: value_expr for ... }
prices = {"apple": 3, "pear": 5}
doubled = {name: price * 2 for name, price in prices.items()}   # {'apple': 6, 'pear': 10}

# Set comprehension: { expr for ... } -> unique results
lengths = {len(w) for w in ["hi", "hey", "yo"]}   # {2, 3}
```

### 8.3 Generators — lazy sequences

A **generator expression** looks like a list comprehension but with **parentheses**, and it
produces values one at a time instead of building a list:

```python
numbers = [1, 2, 3, 4]

gen = (n * n for n in numbers)   # NOTHING is computed yet — this is lazy
print(next(gen))                 # 1   — compute the first value on demand
print(next(gen))                 # 4   — then the next
for value in gen:                # continue consuming the rest
    print(value)                 # 9, 16
```

Write your own generator with a function that uses **`yield`** instead of `return`. `yield` hands
out a value and *pauses*, resuming where it left off on the next request:

```python
def count_up_to(limit):
    n = 1
    while n <= limit:
        yield n          # pause here, give out n, resume next time
        n += 1

for x in count_up_to(3):
    print(x)             # 1, 2, 3
```

### 8.4 Why lazy matters: memory

```python
# A list of a billion squares would try to build ALL of them in memory (gigabytes) -> crash risk.
# squares = [n * n for n in range(1_000_000_000)]   # don't!

# A generator holds only ONE value at a time, so this is fine:
squares = (n * n for n in range(1_000_000_000))
total = sum(squares)     # streams through them; constant memory
```

**iterator** — anything you can step through with `next()` / a `for` loop. Generators are
iterators you create easily; `for` loops quietly call `next()` until the items run out.

## 🚀 Stage 3 — In Practice / Why It Matters

Comprehensions are the everyday way to clean and reshape data: `[chunk.strip() for chunk in chunks
if chunk]`. Generators are how you process a 10 GB file line by line, or stream an LLM's response
**token by token** without waiting for (or storing) the whole thing — exactly the streaming you'll
build in Phase 1.

**Common beginner mistakes (the reasoning):**
1. **Cramming too much logic into a comprehension** — if it needs nested conditions or several
   steps, a plain `for` loop is clearer. Readability beats cleverness.
2. **Consuming a generator twice** — once exhausted, it's empty. `list(gen)` a second time yields
   `[]`. Rebuild it or convert to a list if you need to reuse the data. *Reason:* generators don't
   store past values.
3. **Using `[]` when you meant `()`** for huge data — the list version builds everything in memory.
4. **Forgetting the `if` goes at the end** — `[x for x in items if cond]`, not before the `for`
   (that's the different "conditional expression" form).

### Try it yourself
From `words = ["  Ada ", "", "Bo  ", "   "]`, use one comprehension to produce a clean list of
non-empty, stripped names: `["Ada", "Bo"]`.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Generator is empty the 2nd time | Generators exhaust after one pass | Rebuild it, or use a list if you'll reuse it |
| `MemoryError` on a huge `[...]` | Built a giant list in memory | Use a generator `(...)` instead |
| `SyntaxError` in a comprehension | `if` placed in the wrong spot | Filter goes at the end: `[x for x in xs if c]` |
| Comprehension is unreadable | Too much logic in one line | Use a normal `for` loop instead |

## 📌 Quick Reference

```python
[x * x for x in nums]                 # list comprehension
[x for x in nums if x % 2 == 0]       # with a filter
{k: v for k, v in pairs}              # dict comprehension
(x * x for x in nums)                 # generator (lazy, parentheses)
def gen():
    yield 1
    yield 2                           # generator function
```

## 🛑 STOP — Self-Check

What's the key difference between `squares = [n*n for n in range(5)]` and
`squares = (n*n for n in range(5))`, and when would you prefer the second?

<details><summary>Answer</summary>

`[ ... ]` builds a **list** — all 5 values computed and stored immediately. `( ... )` builds a
**generator** — values are produced **lazily**, one at a time, only as you consume them. Prefer the
generator when the sequence is **large or streaming** (to save memory) or when you'll consume items
one-by-one and don't need them all stored at once — e.g. streaming tokens or reading a huge file.
</details>
