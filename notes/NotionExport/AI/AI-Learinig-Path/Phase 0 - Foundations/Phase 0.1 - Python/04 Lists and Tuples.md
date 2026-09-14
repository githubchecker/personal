# 04 — Lists & Tuples

> Phase 0 · Module 0.1 · Lesson 4 of 16

## 🗺️ Stage 0 — Concept Map

Real programs work with **collections** of values, not just single ones. **Lists** (changeable
sequences) and **tuples** (fixed sequences) are the two most fundamental. They build on the
indexing/slicing you learned for strings and set up dictionaries, comprehensions, and the data you
feed to AI models (batches of text are just lists). You will also see how Python lists compare to
true **arrays**.

## 🔑 New Terms (plain English)

- **Collection** — a single value that holds many items (here: lists and tuples).
- **Mutable** — changeable after you create it (a **list**).
- **Immutable** — fixed once created; can't be edited in place (a **tuple**, a string).
- **Index** — an item's position number, starting at `0`.
- **Aliasing** — two names pointing at the *same* object, so changing one appears to change "both".
- **Array** — a sequence storing raw, single-typed numbers (e.g. NumPy arrays or `array.array`), unlike Python lists which can store any mixed objects.
- **Unpacking** — extracting elements from a list or tuple directly into individual variables (`x, y = point`).
- **Rest operator (`*`)** — collecting all leftover elements during unpacking into a list (`first, *rest = items`).

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

---

### 4.1.1 Deep Dive: Sequence Slicing — Complete Syntax, Exclusions & In-Place Slice Assignments

Slicing extracts a contiguous or regularly spaced subsequence from a list (or string, or tuple). Slicing a list produces a **brand-new list** (a shallow copy of the selected elements).

#### 1. The Core Formula & Default Values

The general slice syntax is:
`list[start : stop : step]`

* **`start`**: Index where extraction begins (defaults to `0` if step is positive, `-1` if step is negative).
* **`stop`**: Index before which extraction ends (defaults to `len(list)` if step is positive, before the first item if step is negative).
* **`step`**: Stride size between items (defaults to `1` if omitted).

#### 2. The Fundamental "Exclusion Rule" (The Half-Open Interval `[start, stop)`)

In Python, slicing follows the **half-open interval** rule:
* `start` is **INCLUDED** (inclusive).
* `stop` is **EXCLUDED** (exclusive).

```python
# Indices:      0    1    2    3    4    5
tokens =     ["[B]", "AI", "is", "cool", "!", "[E]"]
# Neg idx:     -6   -5   -4   -3   -2   -1

# Slice tokens[1:4] extracts indices 1, 2, 3:
content = tokens[1:4]
print(content)       # ['AI', 'is', 'cool']  <-- Index 4 ('!') is strictly EXCLUDED!
```

##### Why Does Python Exclude `stop`? (The Architectural Rationale)
1. **Instant Length Calculation**: The length of the slice is always exactly `stop - start`.
   * For `tokens[1:4]`: $4 - 1 = 3$ elements. You never need to add or subtract 1.
2. **Seamless Consecutive Splitting**: You can cleanly split any sequence into two halves at index $k$ without overlapping or missing elements:
   ```python
   k = 3
   left = tokens[:k]   # elements before index k (indices 0, 1, 2)
   right = tokens[k:]  # elements starting at index k to the end (indices 3, 4, 5)
   assert left + right == tokens  # Perfectly reconstructs the original!
   ```
3. **Natural Symmetry with 0-Based Indexing**: `tokens[:N]` gives you the first $N$ items without guessing offsets.

#### 3. All Possible Syntax Variations (The Complete Matrix)

```python
data = ["A", "B", "C", "D", "E", "F"]
# Idx:   0    1    2    3    4    5

# (a) Full Shallow Copy (omitting start, stop, and step):
copy_all = data[:]              # ['A', 'B', 'C', 'D', 'E', 'F']
print(copy_all is data)         # False (different object in memory)

# (b) From start to the very end (omitting stop):
tail = data[2:]                 # ['C', 'D', 'E', 'F'] (from index 2 onwards)

# (c) From the beginning up to stop (omitting start):
head = data[:3]                 # ['A', 'B', 'C'] (indices 0, 1, 2)

# (d) Explicit start and stop (standard subsegment):
mid = data[1:5]                 # ['B', 'C', 'D', 'E'] (indices 1, 2, 3, 4)

# (e) Positive Step / Striding (every Nth element):
evens = data[::2]               # ['A', 'C', 'E'] (indices 0, 2, 4)
odds = data[1::2]               # ['B', 'D', 'F'] (indices 1, 3, 5)
step3 = data[::3]               # ['A', 'D'] (indices 0, 3)

# (f) Negative Indices (counting from the end):
last_three = data[-3:]          # ['D', 'E', 'F'] (indices -3, -2, -1)
all_but_last_two = data[:-2]    # ['A', 'B', 'C', 'D'] (omits last 2 items)
sub_neg = data[-5:-2]           # ['B', 'C', 'D'] (from idx -5 up to, excluding -2)

# (g) Negative Step / Reversal (stepping backwards):
reversed_data = data[::-1]      # ['F', 'E', 'D', 'C', 'B', 'A']

# (h) Stepping backwards between explicit bounds (start MUST be greater than stop!):
countdown = data[4:1:-1]        # ['E', 'D', 'C'] (starts at idx 4, steps down to idx 2; idx 1 excluded)
```

> ⚠️ **The Directional Contradiction Trap (Negative Step Gotcha):**
> When `step` is negative, Python steps backwards. Therefore, `start` MUST be to the right of `stop`!
> ```python
> broken = data[1:4:-1]   # Returns [] !
> ```
> *Why it returns `[]`:* You asked Python to start at index 1 and step backwards (`-1`), but index 4 is forward. Python cannot step backward to reach 4, so it safely returns an empty list without raising an error.

#### 4. Out-of-Bounds Behavior: Indexing vs. Slicing

This is one of the most critical behavioral differences in Python:

| Operation | Syntax | If Index is Out of Bounds ($\ge$ len) |
| :--- | :--- | :--- |
| **Direct Indexing** | `items[10]` | 💥 **Crashes:** `IndexError: list index out of range` |
| **Sequence Slicing** | `items[2:10]` | 🛡️ **Safe:** Python silently clips to actual boundaries; returns available items! |
| **Slice Fully Past End** | `items[50:100]` | 🛡️ **Safe:** Returns empty list `[]` without error |

```python
nums = [1, 2, 3]

# 1. Direct Indexing:
# print(nums[10])       # IndexError: list index out of range!

# 2. Slicing with oversized bounds (Safe Clipping):
print(nums[1:100])      # [2, 3] (takes everything available from index 1)
print(nums[10:20])      # [] (completely out of bounds -> empty list, no crash!)
print(nums[-100:2])     # [1, 2] (clipped to start index 0)
```

#### 5. Mutable Slice Assignment (Exclusive to Lists!)

Because lists are **mutable**, you can assign values to a slice. This allows modifying, expanding, shrinking, or deleting segments **in place** (strings and tuples cannot do this because they are immutable).

##### (a) Replacing a Slice (Can Expand or Shrink the List!)
The replacement does **not** need to match the length of the slice being replaced:
```python
letters = ["a", "b", "c", "d", "e"]

# Replace 2 items (indices 1, 2 -> "b", "c") with 3 new items:
letters[1:3] = ["X", "Y", "Z"]
print(letters)          # ['a', 'X', 'Y', 'Z', 'd', 'e'] (Length expanded from 5 to 6!)

# Replace 3 items (indices 1, 2, 3 -> "X", "Y", "Z") with 1 item:
letters[1:4] = ["B"]
print(letters)          # ['a', 'B', 'd', 'e'] (Length shrank!)
```

##### (b) Inserting Elements Without Deleting Anything (Zero-Length Slice)
Using matching `start` and `stop` creates a slice of length 0 at that position:
```python
nums = [10, 20, 30]
# Insert [99, 100] at index 1 without deleting anything:
nums[1:1] = [99, 100]
print(nums)             # [10, 99, 100, 20, 30]
```

##### (c) Deleting Slices
```python
data = [1, 2, 3, 4, 5]
# Method 1: del keyword
del data[1:3]           # deletes indices 1 and 2 in place
print(data)             # [1, 4, 5]

# Method 2: assign empty list
data[1:2] = []          # deletes index 1 in place
print(data)             # [1, 5]

# Method 3: Clear entire list in place (retains the same object reference):
data[:] = []
print(data)             # [] (all references to this list see the clearance!)
```

##### (d) Extended Slice Assignment Rule (Step $\ne 1$)
When assigning to a slice with a `step` other than 1, Python requires an **exact length match**:
```python
grid = [0, 1, 2, 3, 4, 5]

# Replace every 2nd item (indices 0, 2, 4 -> 3 items):
grid[::2] = [10, 20, 30]
print(grid)             # [10, 1, 20, 3, 30, 5]

# If the lengths do NOT match:
# grid[::2] = [10, 20]  # ValueError: attempt to assign sequence of size 2 to extended slice of size 3
```

#### 6. The `slice()` Built-in Object

Under the hood, `data[start:stop:step]` translates directly to calling `data[slice(start, stop, step)]`. You can create and pass named `slice` objects across your codebase for clarity and reusability:

```python
# Define reusable, descriptive slice objects:
HEAD_WINDOW = slice(0, 3)
TAIL_WINDOW = slice(-2, None)       # None means 'to the end'
EVEN_STRIDE = slice(None, None, 2)  # None means 'default boundary'

batch = ["prompt1", "prompt2", "prompt3", "prompt4", "prompt5"]
print(batch[HEAD_WINDOW])           # ['prompt1', 'prompt2', 'prompt3']
print(batch[TAIL_WINDOW])           # ['prompt4', 'prompt5']
print(batch[EVEN_STRIDE])           # ['prompt1', 'prompt3', 'prompt5']
```

---

### 4.2 Lists: changing them (mutation)

```python
fruits = ["apple", "banana", "date"]
fruits[0] = "avocado"          # replace an item in place -> ['avocado', 'banana', 'date']
fruits.append("cherry")        # add ONE item to the end -> ['avocado', 'banana', 'date', 'cherry']
fruits.insert(1, "blueberry")  # insert at index 1 -> ['avocado', 'blueberry', 'banana', 'date', 'cherry']
fruits.remove("banana")        # remove by VALUE (first match) -> ['avocado', 'blueberry', 'date', 'cherry']

last = fruits.pop()            # pop() defaults to -1: removes & RETURNS last item ('cherry')
first_item = fruits.pop(0)     # pop(index): removes & RETURNS item at that index ('avocado')
del fruits[0]                  # del: removes by index ('blueberry') without returning
print(fruits)                  # ['date']

# append() vs extend() with multiple items:
a = [1, 2]
a.append([3, 4])               # append treats [3, 4] as ONE single item
print(a)                       # [1, 2, [3, 4]]   <- NESTED list (len is 3)

b = [1, 2]
b.extend([3, 4])               # extend unpacks and appends EACH element
print(b)                       # [1, 2, 3, 4]     <- FLAT list (len is 4)

# Merging with '+' vs in-place extend():
first = [1, 2]
second = [3, 4]
merged = first + second        # '+' creates a BRAND-NEW list (originals are untouched)
print(merged)                  # [1, 2, 3, 4]
print(first)                   # [1, 2]           <- unchanged!
# Use 'first.extend(second)' (or 'first += second') when you want to modify 'first' in place.
```

### 4.3 Sorting and reversing

**Sorting:**
```python
nums = [3, 1, 2]
nums.sort()                 # sorts IN PLACE (changes nums), returns None
print(nums)                 # [1, 2, 3]

original = [3, 1, 2]
ordered = sorted(original)  # returns a NEW sorted list, leaves original alone
print(original, ordered)    # [3, 1, 2] [1, 2, 3]

words = ["pear", "fig", "banana"]
print(sorted(words, key=len))         # ['fig', 'pear', 'banana'] — sort by a rule
print(sorted(nums, reverse=True))     # [3, 2, 1] — sort descending
```

**Reversing (flipping order without sorting by value):**
```python
# 1. In place with .reverse() (changes the list, returns None):
messages = ["msg1", "msg2", "msg3"]
messages.reverse()          # flips IN PLACE
print(messages)             # ['msg3', 'msg2', 'msg1']

# 2. Slicing with [::-1] (creates a brand-new reversed list):
messages = ["msg1", "msg2", "msg3"]
reversed_copy = messages[::-1]  # 'messages' stays unchanged
print(reversed_copy)        # ['msg3', 'msg2', 'msg1']

# 3. reversed() built-in (memory-friendly iterator, ideal for loops):
for msg in reversed(messages):
    print(msg)              # prints msg3, then msg2, then msg1
```

Notice the exact same rule applies:
- `.sort()` and `.reverse()` modify the list **in place** and return `None`.
- `sorted(items)` and `items[::-1]` leave the original alone and return a **new list**.
- `reversed(items)` yields an **iterator** without allocating a whole new list copy.

### 4.4 The aliasing pitfall (very important)

A list variable holds a **reference** to the list, not a private copy. Assigning it to another
name makes a second label for the **same** list in memory:

```python
a = [1, 2, 3]
b = a            # b is NOT a copy — it's another name for the SAME list
b.append(4)
print(a)         # [1, 2, 3, 4]  <- changing b changed a!

# You can prove they are the exact same object using "is" and id():
print(b is a)    # True  <- id(b) == id(a); they point to the same memory address

# To get an independent COPY:
c = a.copy()     # or  c = a[:]  or  c = list(a)
c.append(99)
print(a)         # unchanged by c

# Verification with "==" vs "is":
print(c == a)    # False (now has 99)
d = a.copy()
print(d == a)    # True  <- same items inside
print(d is a)    # False <- different lists at different memory addresses! id(d) != id(a)
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

---

### 4.5.1 The "Mutating While Iterating" Pitfall (Skipped Elements Gotcha & Solutions)

One of the most notorious traps in Python occurs when you **remove or add elements to a list while looping over it with `for`**.

#### 1. The Gotcha: Why Elements Get Skipped

When you write `for item in my_list:`, Python does not freeze a snapshot of the list. Instead, it internally tracks a simple integer index counter (`0, 1, 2, ...`) and retrieves `my_list[index]` on each step:

```
Initial List: ["Alice", "Bob", "Charlie", "David"]
                Idx 0    Idx 1    Idx 2     Idx 3

Step 1 (index = 0): inspects "Alice" (keep)
Step 2 (index = 1): inspects "Bob"   ──> you call names.remove("Bob")
                     "Bob" is deleted!
                     
The list immediately shifts left in memory:
              ["Alice", "Charlie", "David"]
                Idx 0    Idx 1      Idx 2

Step 3 (index = 2): Python advances counter to 2!
                     Inspects names[2], which is now "David"!
                     💥 "Charlie" (now at index 1) was completely SKIPPED!
```

#### 2. The Code Demonstrating the Silent Bug

##### Case A: The Skipped Element
```python
names = ["Alice", "Bob", "Charlie", "David"]

for name in names:
    if name == "Bob":
        names.remove(name)          # delete "Bob" mid-loop
    print(f"Processed: {name}")

# Output:
# Processed: Alice
# Processed: Bob
# Processed: David    <-- "Charlie" was NEVER processed at all!
print(names)          # ['Alice', 'Charlie', 'David']
```

##### Case B: Consecutive Matching Items Fail to Remove
```python
tags = ["AI", "test", "test", "ML"]

# Attempt to remove all "test" tags:
for tag in tags:
    if tag == "test":
        tags.remove(tag)

print(tags)           # ['AI', 'test', 'ML']  <-- The second "test" was skipped and NOT removed!
```

---

#### 3. How to Cope with It: 4 Proven Solutions

##### Solution 1: List Comprehension (Recommended / Idiomatic Python)
Instead of modifying the existing list, produce a new filtered list in a single clean line:
```python
names = ["Alice", "Bob", "Charlie", "David"]

# Keep all names that are NOT "Bob":
clean_names = [name for name in names if name != "Bob"]
print(clean_names)    # ['Alice', 'Charlie', 'David']
```
* **Why it's best:** Cleanest syntax, fastest ($O(N)$ single pass in C-bytecode), and completely avoids mutable state bugs.

##### Solution 2: In-Place Slice Assignment (`names[:] = ...`)
If other parts of your application hold references to `names` and you **must modify the list in place** (preserving its memory ID `id(names)`), assign a comprehension back to a full slice:
```python
names = ["Alice", "Bob", "Charlie", "David"]
alias = names         # alias references the exact same list

# Mutate the original list in place without iterator corruption:
names[:] = [name for name in names if name != "Bob"]

print(names)          # ['Alice', 'Charlie', 'David']
print(alias)          # ['Alice', 'Charlie', 'David']  <-- alias sees the update!
print(alias is names) # True (still the exact same object in memory)
```

##### Solution 3: Iterate Over a Snapshot Copy (`names[:]`)
If you have multi-step logic and truly need to call `.remove()` inside a loop, iterate over a **shallow copy** (`names[:]` or `list(names)`) while mutating the original:
```python
names = ["Alice", "Bob", "Charlie", "David"]

# Loop over the COPY, but delete from the ORIGINAL:
for name in names[:]:
    if name == "Bob":
        names.remove(name)

print(names)          # ['Alice', 'Charlie', 'David']  <-- Works correctly!
```
> ⚠️ **Performance Warning:** Calling `names.remove(x)` inside a loop has **$O(N^2)$ quadratic complexity** because `.remove()` scans the list from index 0 on every deletion. For large lists (>1,000 items), prefer Solution 1 or Solution 2 ($O(N)$ linear time).

##### Solution 4: Iterate Backwards by Index (For Index-Based `del`)
When deleting by index, loop backwards from the end using `range(len(names) - 1, -1, -1)`. Deleting a high index shifts elements that have *already* been visited, leaving all lower unprocessed indices in their exact positions:
```python
names = ["Alice", "Bob", "Bob", "Charlie"]

# Step backwards: len-1 down to 0:
for i in range(len(names) - 1, -1, -1):
    if names[i] == "Bob":
        del names[i]   # deletes without shifting upcoming indices

print(names)          # ['Alice', 'Charlie']  <-- Both 'Bob' instances removed cleanly!
```

---

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

# Converting between Lists and Tuples:
# 1. Tuple -> List: when you need to edit an immutable tuple
point_tuple = (3, 4)
editable = list(point_tuple)        # creates a NEW mutable list: [3, 4]
editable.append(5)                  # now you can modify it!
print(editable)                     # [3, 4, 5]

# 2. List -> Tuple: "freeze" a list so it cannot be changed (and becomes hashable)
raw_items = ["chunk1", "chunk2"]
frozen = tuple(raw_items)           # creates a NEW immutable tuple: ('chunk1', 'chunk2')
# frozen.append("chunk3")           # AttributeError! Cannot be modified
print(frozen)                       # ('chunk1', 'chunk2')

# 3. Tuple to Tuple (building new tuples from existing ones):
# Because tuples cannot be mutated, any operation produces a BRAND-NEW tuple:
t1 = (1, 2)
t2 = (3, 4)
combined = t1 + t2                  # '+' concatenation -> (1, 2, 3, 4)
repeated = (0,) * 3                 # '*' repetition -> (0, 0, 0)
sub_tuple = combined[1:3]           # slicing -> (2, 3)

# 4. How to "update" a tuple in practice:
# Standard Python idiom: tuple -> list -> modify -> tuple
record = ("Ada", 36)
temp = list(record)
temp[1] = 37                        # update the age
record = tuple(temp)                # rebind to updated tuple: ('Ada', 37)
```

**When to use which:** list = a changing collection of similar things (rows, chunks, results).
Tuple = a fixed record whose shape won't change (a coordinate, an RGB colour, a returned pair),
or when you need an unchangeable, hashable value.

### 4.7 Sequence Unpacking & the '*' (Rest) Operator

**Unpacking** lets you pull elements directly out of a tuple or list into separate variables in a single line.

#### 1. Basic Unpacking (Lists & Tuples)

Python matches variables to items by position:

```python
# Unpacking a tuple:
coords = (10, 20)
x, y = coords                  # x = 10, y = 20
print(f"x={x}, y={y}")

# Unpacking a list:
rgb = [255, 128, 0]
r, g, b = rgb                  # r = 255, g = 128, b = 0

# Python's famous variable swap (uses tuple unpacking under the hood!):
a, b = "apple", "banana"
a, b = b, a                    # a is now 'banana', b is now 'apple' (no temp variable needed!)
```

> ⚠️ **The exact-match rule:** The number of variables on the left MUST match the number of items
> on the right. If they don't match, Python crashes:
> - Too many items: `x, y = [1, 2, 3]` $\longrightarrow$ `ValueError: too many values to unpack (expected 2)`
> - Not enough items: `x, y, z = (1, 2)` $\longrightarrow$ `ValueError: not enough values to unpack (expected 3, got 2)`

#### 2. The `*` (Rest) Operator: Extended Unpacking

When you don't know the exact length of a list, or only care about certain elements, prefix a variable
with `*` (the **rest** or **starred** operator) to collect all remaining items.

**Key Rule:** The starred variable **always collects items into a `list`**, even if unpacking a tuple!

```python
# (a) Grab the first item, collect the rest:
numbers = [1, 2, 3, 4, 5]
first, *rest = numbers
print(first)                   # 1
print(rest)                    # [2, 3, 4, 5]  <- always a list!

# (b) Grab the first and last, collect everything in between:
scores = (98, 85, 76, 92, 45)  # unpacking a tuple
best, *middle, worst = scores
print(best)                    # 98
print(middle)                  # [85, 76, 92]  <- list!
print(worst)                   # 45

# (c) Grab everything up to the last element:
*head, tail = [10, 20, 30, 40]
print(head)                    # [10, 20, 30]
print(tail)                    # 40

# (d) Ignore unwanted items using *_ (the throwaway convention):
record = ["user_123", "2026-09-11", "Europe", "admin", "active"]
user_id, *_, status = record   # ignores all the middle items
print(user_id, status)         # 'user_123' 'active'
```

> ⚠️ **Gotcha:** You can only use **one** `*` expression in an unpacking assignment. Writing `*a, *b = [1, 2, 3]`
> raises `SyntaxError: two starred expressions in assignment` because Python wouldn't know where `a` ends and `b` begins.

#### 3. Real-World AI & LangGraph Application

In AI pipelines, messages arrive as sequences. You frequently use unpacking to isolate the system prompt
and the most recent user turn from the middle conversation history:

```python
# A conversation list: [SystemMessage, Msg1, Msg2, Msg3, LatestUserMsg]
system_msg, *chat_history, current_query = messages

# Send current_query to retrieval, format chat_history as memory, apply system_msg!
```

### 4.8 Is a list an array? (List vs array.array vs NumPy)

Beginners often ask: *"Does Python have arrays?"*

In casual conversation, Python programmers often say "array" when they simply mean a Python `list`.
However, Python actually has **three distinct options**, each with a different purpose:

1. **Python `list` (`[1, "two", 3.0]`) — Built-in dynamic sequence (your daily default).**
   - Holds references to *any* Python objects (mixed types allowed).
   - Highly flexible, but has slight memory overhead because each item is a full Python object.

2. **Standard Library `array` (`import array`) — Built-in typed C-style array.**
   - Included with Python without installing anything (`from array import array`).
   - Stores a flat sequence of *strictly one C-primitive type* (e.g. `'i'` for signed 32-bit integers, `'d'` for double-precision floats).
   - Memory-compact, but does **not** support vector math or multi-dimensional matrices. Rarely used in modern AI engineering.

3. **NumPy Array (`numpy.ndarray`) — The AI & Data Science standard.**
   - Installed via `pip install numpy` (`import numpy as np`).
   - Fast, contiguous, homogeneous numeric grid designed for vectorized math, linear algebra, embeddings, and tensors.
   - We explore this in depth in **Lesson 15 (AI Essentials — NumPy & HTTP)** and **Phase 0.2 (PyTorch)**.

```python
# 1. Plain list (flexible, any type, standard):
my_list = [1, 2, 3]

# 2. Standard library array (fixed C type; 'i' = signed 32-bit int):
import array
my_arr = array.array('i', [1, 2, 3])
# my_arr.append("text")   # TypeError! Elements must match the type code 'i'

# 3. NumPy array (vectorized math across the entire array — Lesson 15):
# import numpy as np
# my_np = np.array([1, 2, 3])
# print(my_np * 2)        # [2, 4, 6] — operates on all elements at once without a loop
```

| Structure | Module | Contents | Vectorized Math? | Primary Use Case |
| --- | --- | --- | --- | --- |
| **`list`** | Built-in | Any mixed Python objects | ❌ (requires loops) | General programming, text chunks, API messages |
| **`array.array`** | `import array` | Single C primitive type (`'i'`, `'d'`) | ❌ (requires loops) | Low-level C interop or tight memory without 3rd-party dependencies |
| **NumPy `ndarray`** | `import numpy as np` | Homogeneous numeric grid | ✅ Fast C/CUDA vectorization | Embeddings, tensors, model weights (Lesson 15) |

### 4.9 Storing Custom Objects in Lists & Tuples

Python collections do not store data inline; they store **references (pointers) to objects in memory**. Because everything in Python is an object, lists and tuples can hold instances of custom classes, dataclasses, or library objects (like LLM messages or PyTorch tensors).

```python
class Document:
    def __init__(self, doc_id: int, text: str):
        self.doc_id = doc_id
        self.text = text

    def __repr__(self):
        return f"Doc({self.doc_id})"

doc1 = Document(1, "Attention is all you need")
doc2 = Document(2, "RAG pipeline architecture")

# 1. List of objects:
docs = [doc1, doc2]
print(docs)                            # [Doc(1), Doc(2)]
print(docs[0].text)                    # 'Attention is all you need'

# Extracting an attribute across all objects:
all_texts = [d.text for d in docs]
print(all_texts)                       # ['Attention is all you need', 'RAG pipeline architecture']

# 2. Tuple of objects:
doc_tuple = (doc1, doc2)
print(doc_tuple[1].doc_id)             # 2

# ⚠️ GOTCHA: The "Tuple of Mutable Objects" trap:
# A tuple is immutable: you CANNOT swap or reassign its slots:
# doc_tuple[0] = Document(3, "New")    # TypeError: 'tuple' object does not support item assignment

# BUT the objects inside the tuple CAN still be mutated:
doc_tuple[0].text = "Updated Title"
print(doc_tuple[0].text)               # 'Updated Title' — the inner object mutated!
```

## 🚀 Stage 3 — In Practice / Why It Matters

AI code is full of lists and tuples:
- **Batches of text:** Sending 64 document chunks to an embedding model is just a list of strings: `["chunk 1", "chunk 2", ...]`.
- **LLM conversation history:** The prompt sent to an API is an ordered list of message objects: `[SystemMessage(...), HumanMessage(...), AIMessage(...)]`.
- **Ranked search results:** Vector search returns ranked lists; pairing similarity scores with documents uses tuples: `[(0.92, doc_a), (0.81, doc_b)]`.

### 🤖 Sneak Peek: How Lists & Tuples Power LangGraph & AI Agents (Phase 3)

Even if you haven't studied AI architectures yet, here is how these exact list and tuple operations
power production frameworks like **LangGraph**:

1. **State Reducers (`messages + [new_message]`):**
   In LangGraph, agents are state machines where graph nodes receive the current state and return an update.
   Using `state["messages"] + [new_message]` produces a **brand-new list**, which allows LangGraph
   to checkpoint history, time-travel, and undo agent steps without corrupting earlier checkpoints.
2. **Context Window Pruning (`reversed(messages)`):**
   LLMs have fixed token limits. To keep conversation within bounds without allocating extra memory,
   agent buffers use `for msg in reversed(messages):` to walk backwards from the newest message,
   tallying tokens until the threshold is hit — zero extra RAM used because `reversed()` is an iterator.
3. **Tensor Shapes & Tool Returns (`tuple`):**
   In PyTorch (Phase 0.2), array shapes are always tuples like `(batch_size, sequence_length, embedding_dim)`.
   Because tuples are immutable and hashable, they also serve as cache keys (e.g. caching embeddings so you
   never pay for the same API call twice).

### Try it yourself
Start with `scores = [70, 95, 60, 88]`. Print them sorted descending, and print the highest and
lowest using one function that returns a tuple.

## ⚖️ Variations & When to Use (Efficiency & Decision Guide)

A developer constantly chooses between these operations. Here is the exact performance and decision rule:

| Operation | Syntax | Time / Memory Cost | Mutates Original? | ✅ When to Use | AI / LangGraph Application |
| --- | --- | --- | --- | --- | --- |
| **Append single** | `a.append(x)` | $O(1)$ time · zero extra memory | ✅ In-place | Adding one item to an existing sequence | Adding a new user/assistant message to chat history |
| **Extend in-place** | `a.extend(b)` or `a += b` | $O(k)$ time · zero extra memory | ✅ In-place | Merging many items when you don't need the old list | Ingesting a batch of scraped web documents into a queue |
| **Merge new list** | `a + b` | $O(n+m)$ time · copies all items | ❌ Brand-new list | You must keep the original list untouched | **LangGraph State Updates:** clean, immutable state checkpoints |
| **Prepend item** | `a.insert(0, x)` | $O(n)$ time (shifts all elements) | ✅ In-place | Only on tiny lists (<100 items); avoid on big lists | Prepending a system prompt to a small message list |
| **Pop last** | `a.pop()` | $O(1)$ time · zero extra memory | ✅ In-place | LIFO stack / undoing the most recent step | Removing the last failed tool call in an agent retry loop |
| **Pop by index** | `a.pop(i)` | $O(n)$ time (shifts items) | ✅ In-place | Removing and retrieving an item from a specific position | Taking the highest-priority task from a task queue |
| **Reverse in-place** | `a.reverse()` | $O(n)$ time · zero extra memory | ✅ In-place | Flipping order permanently without allocating memory | Reversing chronological database logs to newest-first |
| **Reverse stream** | `reversed(a)` | $O(1)$ time · zero extra memory | ❌ Iterator (no copy) | Looping backwards through a list without memory overhead | **Token Window Truncation:** scanning chat history backwards |
| **Reverse copy** | `a[::-1]` | $O(n)$ time · copies all items | ❌ Brand-new list | You need a reversed copy to pass to another function | Sending a reversed view while keeping original list order |
| **Convert to list** | `list(tuple)` | $O(n)$ time · $O(n)$ memory | ❌ Brand-new list | Unlocking an immutable tuple so you can edit, append, or sort it | Converting a fixed config tuple into an editable list |
| **Convert to tuple** | `tuple(list)` | $O(n)$ time · $O(n)$ memory | ❌ Brand-new tuple | Freezing a list to prevent accidental edits; making it hashable | Creating immutable cache keys or fixed coordinate pairs |
| **Tuple concat** | `t1 + t2` | $O(n+m)$ time · $O(n+m)$ memory | ❌ Brand-new tuple | Combining fixed records or shape dimensions | Combining PyTorch tensor shapes, e.g. `(batch,) + shape` |
| **Unpack with `*`** | `first, *rest = items` | $O(n)$ time · copies rest | ❌ New list for `rest` | Grabbing head/tail or separating known endpoints | Extracting system prompt, history, and latest query from `messages` |
| **List vs Tuple** | `[...]` vs `(...)` | Tuples use ~20% less memory | Tuples are immutable | **List:** data will grow/change · **Tuple:** fixed records or cache keys | Model shapes `(batch, seq, dim)` and tool pairs `(result, status)` |

**Decision Rule of Thumb:**
- **In-place speed:** `.append()`, `.extend()`, and `.reverse()` modify in place with minimal memory.
- **Immutable safety (LangGraph/Agents):** `a + b` and `.copy()` ensure prior history is never accidentally altered.
- **Memory-efficient reverse:** Use `reversed(a)` when iterating backwards; use `a[::-1]` only when you need an actual list object.
- **Fixed records & cache keys:** Use `tuple`. Use `list` when items will be added, removed, or reordered.
- **Convert when needed:** Use `list(t)` to edit a tuple, and `tuple(l)` to freeze and hash a list.
- **Unpack with `*`:** Use `first, *rest = items` to cleanly split sequences without fragile index math.

## 🐛 Common Errors & Fixes

Real messages you'll actually see, plus the silent gotchas:

| What you see | Cause | Fix |
| --- | --- | --- |
| `IndexError: list index out of range` | A position that doesn't exist (`x[5]` on 3 items) | Check `len(x)`; the last index is `len(x) - 1` (note: slicing `x[2:10]` never raises IndexError!) |
| *(no error)* `items[1:4:-1]` returns `[]` | Direction contradiction: negative step steps backwards, but start < stop | When `step < 0`, start must be greater than stop (e.g. `items[4:1:-1]`) |
| `ValueError: attempt to assign sequence of size X to extended slice of size Y` | Assigned wrong number of elements to a strided slice (`nums[::2] = [...]`) | Right-hand side sequence length must exactly equal the number of items in the extended slice |
| `TypeError: slice indices must be integers or None` | Used a float or string in a slice index (`items[1.5:4]`) | Cast slice boundaries to `int` |
| `ValueError: too many values to unpack (expected 2)` | Sequence has more items than variables (`x, y = [1, 2, 3]`) | Match variable count, or collect extra items with `*rest` (`x, *rest = ...`) |
| `ValueError: not enough values to unpack (expected 3, got 2)` | Sequence has fewer items than variables (`x, y, z = (1, 2)`) | Check sequence length, or use default parameters |
| `SyntaxError: two starred expressions in assignment` | Used `*` twice in one unpacking line (`*a, *b = items`) | Only one `*` variable is allowed per unpacking line |
| `TypeError: 'tuple' object does not support item assignment` | Editing a tuple (`t[0] = 9`) | Convert to a list first (`temp = list(t)`), edit, then `tuple(temp)` |
| `AttributeError: 'tuple' object has no attribute 'append'` | A list method called on a tuple | Convert to list (`list(t)`) or use tuple concatenation (`t + (new_item,)`) |
| *(no error)* `x = nums.sort()` or `nums.reverse()` makes `x` `None` | `.sort()` and `.reverse()` mutate in place and return `None` | Use `sorted(nums)` or `nums[::-1]` when you want a new list back |
| *(no error)* items skipped when calling `.remove()` or `del` in `for` loop | Mutating a list while iterating shifts indices left under the advancing loop counter | Use a list comprehension `[x for x in items if ...]`, slice assignment `items[:] = ...`, or loop over a copy `items[:]` |
| *(no error)* `editing b` also changes `a` | `b = a` aliases the **same** list | Copy: `b = a.copy()` (or `a[:]`, `list(a)`) |
| *(no error)* `append([1, 2])` nests a list | `append` adds **one** item; you wanted the items | Use `extend([1, 2])` to add the items |

## 📌 Quick Reference

```python
nums = [1, 2, 3, 4, 5]
nums.append(6)                      # add one item to the end
nums.extend([7, 8])                 # add many items
nums.insert(0, 9)                   # insert at an index
nums.pop()                          # remove & return last item (or nums.pop(0) by index)
nums.remove(9)                      # remove the first matching VALUE
# Slicing: [start:stop:step] (start inclusive, stop exclusive)
nums[1:4]                           # indices 1, 2, 3 -> NEW list (stop 4 is excluded!)
nums[:3]                            # first 3 items (indices 0, 1, 2)
nums[-2:]                           # last 2 items
nums[::2]                           # every 2nd item (striding)
nums[::-1]                          # brand-new reversed list
nums[1:3] = [88, 99]                # mutable slice assignment: replaces in place
nums[1:1] = [50]                    # insert 50 at index 1 without deleting
ordered = sorted(nums)              # NEW sorted list (original untouched)
nums.sort()                         # sorts in place, returns None
nums.reverse()                      # reverses in place, returns None
rev = nums[::-1]                    # brand-new reversed list (or list(reversed(nums)))
for i, v in enumerate(nums): ...    # index + value together
for a, b in zip(xs, ys): ...        # walk two lists in lockstep
point = (3, 4); x, y = point        # tuple + unpacking; (42,) is a 1-tuple
a, b = b, a                         # swap two variables in one line (no temp variable)
first, *rest = [1, 2, 3, 4]         # first=1, rest=[2, 3, 4] (*rest is always a list)
first, *_, last = (10, 20, 30, 40)  # first=10, last=40 (ignore middle with *_)
merged = a + b                      # '+' concatenation -> BRAND-NEW list (a, b untouched)
t_to_l = list(point)                # tuple -> list (now mutable: [3, 4])
l_to_t = tuple(nums)                # list -> tuple (now frozen: (1, 2, 3))
t_merged = (1, 2) + (3, 4)          # tuple concat -> (1, 2, 3, 4)
```

- **Pick:** list = it will change · tuple = fixed record (or must stay unchangeable).
- **Copy, don't alias:** `b = a.copy()` when you need an independent list (`b is a` is `False`).
- **Convert:** `list(t)` to make a tuple editable · `tuple(l)` to freeze a list.
- **Unpack:** Match variable count exactly, or use `*rest` to gather remaining elements into a list.
- **In place vs New list:** `.sort()` / `.reverse()` mutate in place · `sorted(nums)` / `nums[::-1]` return a new list.
- **`+` vs `.extend()`:** `a + b` builds a new list (originals unchanged) · `a.extend(b)` (or `a += b`) mutates `a` in place.
- **List vs Array:** list = general mixed collection · `array.array` = standard library typed C-array · NumPy `ndarray` = fast AI vector/matrix math (Lesson 15).

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
