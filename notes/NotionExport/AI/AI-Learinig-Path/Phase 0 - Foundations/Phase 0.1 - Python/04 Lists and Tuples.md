# 04 — Lists & Tuples

> Phase 0 · Module 0.1 · Lesson 4 of 16

## 🗺️ Stage 0 — Concept Map

Real programs work with **collections** of values, not just single ones. **Lists** (changeable
sequences) and **tuples** (fixed sequences) are the two most fundamental. They build on the
indexing/slicing you learned for strings and set up dictionaries, comprehensions, and the data you
feed to AI models (batches of text are just lists).

## 🔑 New Terms (plain English)

- **Collection** — a single value that holds many items (here: lists and tuples).
- **Mutable** — changeable after you create it (a **list**).
- **Immutable** — fixed once created; can't be edited in place (a **tuple**, a string).
- **Index** — an item's position number, starting at `0`.
- **Aliasing** — two names pointing at the *same* object, so changing one appears to change "both".

## 🎈 Stage 1 — The Simple Idea (analogy: an egg carton vs. a sealed gift box)

A **list** is like an egg carton: an ordered row of slots you can refill — take an egg out, put a
new one in, add more slots. A **tuple** is like a sealed gift box: an ordered set of items fixed at
packing time; you can look inside but not change the contents.

**The "Aha!":** lists are **mutable** (changeable), tuples are **immutable** (fixed). You pick
based on whether the data should be allowed to change.

## ⚙️ Stage 2 — How It Actually Works

### 4.1 Lists: create, read, slice

```python
fruits = ["apple", "banana", "cherry"]   # a list literal: square brackets, comma-separated
print(fruits[0])      # 'apple'   — same 0-based indexing as strings
print(fruits[-1])     # 'cherry'  — negative indexes from the end
print(fruits[0:2])    # ['apple', 'banana']  — slicing returns a NEW list
print(len(fruits))    # 3
print("banana" in fruits)   # True — membership test

numbers = [3, 1, 2]
mixed = [1, "two", 3.0, True]   # a list can hold mixed types (though usually you keep them uniform)
nested = [[1, 2], [3, 4]]       # lists can contain lists
print(nested[1][0])   # 3
```

### 4.2 Lists: changing them (mutation)

```python
fruits = ["apple", "banana"]
fruits[0] = "avocado"          # replace an item in place
fruits.append("cherry")        # add ONE item to the end -> ['avocado','banana','cherry']
fruits.insert(1, "blueberry")  # insert at index 1
fruits.extend(["date", "fig"]) # add MANY items (note: append([...]) would nest a list!)
fruits.remove("banana")        # remove by VALUE (first match)
last = fruits.pop()            # remove & RETURN the last item
del fruits[0]                  # remove by index
print(fruits)
```

### 4.3 Sorting

```python
nums = [3, 1, 2]
nums.sort()                 # sorts IN PLACE (changes nums), returns None
print(nums)                 # [1, 2, 3]

original = [3, 1, 2]
ordered = sorted(original)  # returns a NEW sorted list, leaves original alone
print(original, ordered)    # [3, 1, 2] [1, 2, 3]

words = ["pear", "fig", "banana"]
print(sorted(words, key=len))         # ['fig', 'pear', 'banana'] — sort by a rule
print(sorted(nums, reverse=True))     # descending
```

`sort()` (in place, returns `None`) vs `sorted()` (new list) is a classic point of confusion —
note which one you need.

### 4.4 The aliasing pitfall (very important)

A list variable holds a **reference** to the list, not a private copy. Assigning it to another
name makes a second label for the **same** list:

```python
a = [1, 2, 3]
b = a            # b is NOT a copy — it's another name for the SAME list
b.append(4)
print(a)         # [1, 2, 3, 4]  <- changing b changed a!

# To get an independent COPY:
c = a.copy()     # or  c = a[:]  or  c = list(a)
c.append(99)
print(a)         # unchanged by c
```

### 4.5 Iterating

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:                 # the normal way: item by item
    print(fruit)

for i, fruit in enumerate(fruits):   # when you ALSO need the index
    print(i, fruit)                  # 0 apple / 1 banana / 2 cherry

names = ["Ada", "Bo"]
ages = [36, 29]
for name, age in zip(names, ages):   # walk two lists in lockstep
    print(f"{name} is {age}")
```

### 4.6 Tuples: fixed sequences

```python
point = (3, 4)            # parentheses (or just: point = 3, 4)
print(point[0])          # 3 — index like a list
# point[0] = 9           # TypeError! tuples are immutable

x, y = point             # "unpacking": x=3, y=4 in one line
single = (42,)           # a ONE-item tuple needs the trailing comma; (42) is just the number 42

# Tuples are great for fixed groupings and for returning multiple values:
def min_max(items):
    return min(items), max(items)   # returns a tuple
lo, hi = min_max([5, 2, 9])         # unpack the result
```

**When to use which:** list = a changing collection of similar things (rows, chunks, results).
Tuple = a fixed record whose shape won't change (a coordinate, an RGB colour, a returned pair),
or when you need an unchangeable value.

## 🚀 Stage 3 — In Practice / Why It Matters

AI code is full of lists: a batch of sentences to embed, the `messages` you send to an LLM, search
results to rank. `enumerate` and `zip` show up constantly when pairing data. Tuples often carry
fixed pairs like `(score, document)`.

### Try it yourself
Start with `scores = [70, 95, 60, 88]`. Print them sorted descending, and print the highest and
lowest using one function that returns a tuple.

## 🐛 Common Errors & Fixes

Real messages you'll actually see, plus the silent gotchas:

| What you see | Cause | Fix |
| --- | --- | --- |
| `IndexError: list index out of range` | A position that doesn't exist (`x[5]` on 3 items) | Check `len(x)`; the last index is `len(x) - 1` |
| `TypeError: 'tuple' object does not support item assignment` | Editing a tuple (`t[0] = 9`) | Tuples are immutable — use a list, or build a new tuple |
| `AttributeError: 'tuple' object has no attribute 'append'` | A list method called on a tuple | Use a list when you need to add items |
| *(no error)* `x = nums.sort()` makes `x` `None` | `sort()` sorts in place and returns `None` | Use `sorted(nums)` when you want a new list back |
| *(no error)* editing `b` also changes `a` | `b = a` aliases the **same** list | Copy: `b = a.copy()` (or `a[:]`, `list(a)`) |
| *(no error)* `append([1, 2])` nests a list | `append` adds **one** item; you wanted the items | Use `extend([1, 2])` to add the items |

## 📌 Quick Reference

```python
nums = [1, 2, 3]
nums.append(4)          # add one item to the end
nums.extend([5, 6])     # add many items
nums.insert(0, 9)       # insert at an index
nums.pop()              # remove & return the last item
nums.remove(9)          # remove the first matching VALUE
nums[0:2]               # slice -> a NEW list
ordered = sorted(nums)  # NEW sorted list (original untouched)
nums.sort()             # sorts in place, returns None
for i, v in enumerate(nums): ...   # index + value together
for a, b in zip(xs, ys): ...       # walk two lists in lockstep
point = (3, 4); x, y = point       # tuple + unpacking; (42,) is a 1-tuple
```

- **Pick:** list = it will change · tuple = fixed record (or must stay unchangeable).
- **Copy, don't alias:** `b = a.copy()` when you need an independent list.
- **`sort()` vs `sorted()`:** in place + returns `None` · vs · returns a new list.

## 🛑 STOP — Self-Check

What does `a` end up as, and why?

```python
a = [1, 2, 3]
b = a
b = b + [4]      # note: b + [4], not b.append(4)
print(a)
```

<details><summary>Answer</summary>

`a` is **`[1, 2, 3]`** — unchanged. `b + [4]` builds a **brand-new** list and rebinds `b` to it,
leaving the original list (still labelled `a`) untouched. Contrast with `b.append(4)`, which
mutates the shared list in place and *would* change `a`. The difference between rebinding a name
and mutating an object is one of Python's most important subtleties.
</details>
