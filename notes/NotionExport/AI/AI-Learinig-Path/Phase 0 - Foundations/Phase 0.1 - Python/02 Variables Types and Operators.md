# 02 — Variables, Types & Operators

> Phase 0 · Module 0.1 · Lesson 2 of 16

## 🗺️ Stage 0 — Concept Map

Programs move **data** around: numbers, text, true/false flags. This lesson covers how Python
**stores** data (variables), the **kinds** of data (types), and how you **combine** data
(operators). You'll also see how Python tracks objects in computer memory with **`id()`**, and why
checking equality (**`==`**) is fundamentally different from checking identity (**`is`**). Every line
of code you ever write uses these. It comes right after setup because you can't do anything without it.

## 🔑 New Terms (plain English)

- **Variable** — a named label that points to a value.
- **Dynamic typing** — Python infers a value's type; you don't declare it.
- **Type** — the kind of value: `int`, `float`, `str`, `bool`, `None`.
- **Casting** — converting a value from one type to another (`int("5")`).
- **Memory address (`id()`)** — the unique number showing where an object lives in computer memory.
- **Identity (`is`) vs Equality (`==`)** — `==` asks "do they have the same value?"; `is` asks "are they the exact same object in memory?".
- **Truthiness** — whether a value counts as True or False in a condition.

## 🎈 Stage 1 — The Simple Idea (analogy: labelled boxes)

A **variable** is a labelled box you put a value in. You write the label, drop a value inside, and
later refer to the value by its label. In Python you don't declare the box's size or type up front
— you just assign, and Python figures out the type from the value.

```python
age = 36          # make a box labelled "age", put the number 36 in it
age = age + 1     # read the box (36), add 1, put 37 back in the same box
print(age)        # 37
```

**The "Aha!":** Python is **dynamically typed** — a variable has no fixed type; it takes on the
type of whatever you assign. The *value* has a type, the *label* doesn't. Even more: every value in
Python is an **object** living at a specific address in memory. Variables are just sticky name tags
pointing to those objects.

## ⚙️ Stage 2 — How It Actually Works

### 2.1 Assignment & naming

```python
first_name = "Ada"      # use lowercase_with_underscores (the Python convention, "snake_case")
total = 0
is_active = True
PI = 3.14159            # ALL_CAPS by convention means "constant — don't change me"
```

Rules: names start with a letter or `_`, contain letters/digits/`_`, are case-sensitive
(`age` ≠ `Age`), and can't be Python keywords (`for`, `if`, `class`, ...).

### 2.1.1 Shorthand assignments (Multiple, Swapping & Chained)

Python provides clean shorthands for assigning and updating variables without verbose boilerplate:

```python
# 1. Multiple assignment (tuple packing/unpacking shorthand):
a, b = 10, 20
print(a, b)                    # 10 20

# 2. Variable swapping in one line (no temporary variable needed!):
a, b = b, a
print(a, b)                    # 20 10

# 3. Chained assignment (assign the same value to multiple variables):
x = y = z = 0
print(x, y, z)                 # 0 0 0

# 4. Augmented assignment (operate and assign in place):
count = 5
count += 1                     # equivalent to: count = count + 1 (becomes 6)
count *= 2                     # equivalent to: count = count * 2 (becomes 12)
count -= 3                     # equivalent to: count = count - 3 (becomes 9)
```

> ⚠️ **Gotcha with chained assignment:** `a = b = []` points **both** variables to the **same** mutable list in memory! If you do `a.append(1)`, `b` will also become `[1]`! For independent mutable collections, always assign separately: `a = []; b = []`.

### 2.2 The core built-in types

```python
count = 42              # int    — whole numbers, unlimited size in Python
price = 19.99           # float  — numbers with a decimal point
name = "Ada"            # str    — text (string), in quotes
is_ready = True         # bool   — True or False (note the capitals)
nothing = None          # NoneType — a special "no value here" placeholder
```

Check a type with `type()`, and test a type with `isinstance()`:

```python
print(type(price))               # <class 'float'>
print(isinstance(count, int))    # True
```

`None` is worth a special note: it's Python's way of saying "empty / not set yet" — used for
optional values and missing results. It is **not** the same as `0`, `False`, or `""`.

### 2.3 Converting between types (casting)

User input and file data often arrive as strings; you convert explicitly:

```python
quantity = int("5")        # str "5" -> int 5
total = float("19.99")     # str -> float
label = str(42)            # int 42 -> str "42"
flag = bool(0)             # 0 -> False ; any non-zero/with-content -> True

# This is why reading a number from input needs a cast:
# input() ALWAYS returns a string, even if the user types digits.
# age = int(input("Age? "))
```

### 2.4 Operators — combining values

**Arithmetic:**
```python
print(7 + 2)    # 9
print(7 - 2)    # 5
print(7 * 2)    # 14
print(7 / 2)    # 3.5   <- "/" ALWAYS gives a float (true division)
print(7 // 2)   # 3     <- "//" floor division: divide and drop the remainder
print(7 % 2)    # 1     <- "%" modulo: the remainder (great for "is it even?": n % 2 == 0)
print(7 ** 2)   # 49    <- "**" power (7 squared)
```

**Comparison** (always produce a `bool`):
```python
print(3 == 3)   # True   <- "==" means "equal?"  (TWO equals signs)
print(3 != 4)   # True   <- "!=" means "not equal?"
print(3 < 4, 4 >= 4)     # True True
```

### 2.4.1 Floating-Point Comparison & The Tolerance Pattern (`abs(a - b) < tolerance`)

One of the most surprising pitfalls for software engineers in any language is **floating-point inaccuracy**.

#### The Core Problem: Why `0.1 + 0.2 == 0.3` is `False`
Computers represent floating-point numbers using binary bits (powers of 2: $1/2, 1/4, 1/8, ...$). In base-10 mathematics, the fraction $1/3$ cannot be written as a finite decimal ($0.33333...$). Similarly, in binary hardware, numbers like $0.1$ ($1/10$) and $0.2$ ($1/5$) are repeating fractions that **cannot be stored with 100% exact precision**:

```python
a = 0.1 + 0.2
b = 0.3

print(a)                        # 0.30000000000000004
print(b)                        # 0.3

# ❌ THE FATAL EQUALITY BUG:
print(a == b)                   # False!
if a == b:
    print("Matches!")           # 💥 This NEVER executes!
```

---

#### The Solution: The Difference and Tolerance Pattern (`abs(a - b) < tolerance`)
Instead of testing whether two floating-point numbers are bit-for-bit identical, test whether **the absolute distance between them is smaller than an acceptable margin of error (called tolerance or epsilon $\epsilon$)**:

$$\text{difference} = |a - b| < \text{tolerance}$$

```python
a = 0.1 + 0.2
b = 0.3

# 1. Calculate the absolute difference:
difference = abs(a - b)         # abs() removes negative signs
print(f"Absolute difference: {difference}")
# Output: 5.551115123125783e-17 (approx 0.0000000000000000555)

# 2. Define an acceptable tolerance threshold (epsilon):
tolerance = 1e-9                # 0.000000001 (10^-9)

# 3. Check if difference is within tolerance:
if abs(a - b) < tolerance:
    print("Values are practically equal!")  # ✅ Runs successfully!
```

##### Why `abs()` is Crucial:
If $a = 0.29$ and $b = 0.30$, then $a - b = -0.01$. Without `abs()`, a negative number is always smaller than a positive tolerance (`-0.01 < 0.0001`), which would falsely report that any smaller number is "equal"! `abs()` guarantees you measure the **distance** between the numbers, regardless of which one is larger.

---

#### The Modern Pythonic Solution: `math.isclose()`
Python's standard library `math` module provides a dedicated, optimized function that handles both **relative tolerance** and **absolute tolerance**:

```python
import math

a = 0.1 + 0.2
b = 0.3

# Standard usage:
print(math.isclose(a, b))       # True! (default rel_tol=1e-09)

# Fine-tuning tolerances:
# - rel_tol: relative tolerance (scales with large numbers, e.g. 1,000,000.001)
# - abs_tol: absolute tolerance (essential when comparing numbers close to 0.0)
print(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12))  # True!
```

---

#### Why This Matters in AI Engineering:
* **Loss Functions & Convergence**: In machine learning training loops, you never check `if loss == 0.0:`. You check `if loss < 1e-5:` or `if abs(loss_prev - loss_curr) < 1e-6:`.
* **Cosine Similarity & Probabilities**: Model confidence scores and vector similarities are floats between `0.0` and `1.0`. Rounding errors can produce values like `0.9999999999999998` instead of `1.0`.
* **NumPy / PyTorch**: In vector/tensor operations, NumPy provides `np.isclose(vec_a, vec_b)` and `np.allclose(vec_a, vec_b)` which apply this exact tolerance formula across entire embedding arrays!

---

**Logical** (combine booleans):
```python
print(True and False)   # False  — both must be True
print(True or False)    # True   — at least one True
print(not True)         # False  — flips it
```

**Shorthand assignment:**
```python
total = 10
total += 5      # same as total = total + 5  -> 15
total *= 2      # -> 30
```

### 2.5 Object identity: id(), memory addresses, and `is` vs `==`

Every object created in Python sits at a specific memory location. Python gives each object a unique
integer ID called its **memory address**. You can see this address using the built-in `id()` function:

```python
x = 42
print(id(x))    # e.g. 140718293028000 — the unique memory location of this object
```

This brings up one of the most important concepts in Python: **equality** vs **identity**.

- **`==` (Value Equality)**: checks whether two items hold the **same value** (*"Do they look identical?"*).
- **`is` (Identity)**: checks whether two variables point to the **exact same object in memory** (*"Are they the same physical object?"*).
- **`is not` (Non-identity)**: checks that two variables do *not* point to the exact same object in memory.

**Analogy (two identical notebooks):**
Imagine you and a classmate buy the exact same brand and model of notebook, and write the exact same
notes on page 1.
- With `==` (equality), they match: `notebook1 == notebook2` is `True` because the contents are identical.
- With `is` (identity), they do not: `notebook1 is notebook2` is `False` because they are two separate
  physical notebooks sitting on different desks (`id(notebook1) != id(notebook2)`).

```python
# Two separate lists with the exact same items:
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)         # True   <- values are identical
print(a is b)         # False  <- two different list objects in memory!
print(id(a) == id(b)) # False  <- different memory addresses

# Pointing a new variable name to an existing object:
c = a
print(c == a)         # True   <- same values
print(c is a)         # True   <- c and a point to the EXACT same object in memory
print(id(c) == id(a)) # True   <- identical memory addresses
```

**The golden rule for `None`:**
In Python, there is only one `None` object in the entire program. Therefore, checking for `None`
should **always** be done with `is` or `is not`, never with `==`:

```python
api_key = None

if api_key is None:        # ✅ The correct, idiomatic way (fast, checks memory identity)
    print("API key not provided")

if api_key is not None:    # ✅ The correct way to verify a value is present
    print("Ready to make calls")

# Avoid: if api_key == None  # ❌ Works, but unidiomatic and can be misled by custom classes
```

> ⚠️ **Gotcha (small integer caching):** For performance, Python pre-allocates and reuses the same
> memory addresses for small integers (`-5` to `256`) and short strings. That means `x = 10; y = 10; x is y`
> may evaluate to `True`. **Never rely on `is` to compare numbers or strings** — always use `==` to
> compare values, and reserve `is` for identity checks (especially `is None`).

### 2.6 Truthiness (Testing Values in Conditions)

In Python, every single value evaluates to either **`True`** (truthy) or **`False`** (falsy) when passed to `bool()` or used in an `if` condition.

#### The Complete List of Falsy Values in Python:
1. **Constants:** `None`, `False`
2. **Numeric Zero:** `0`, `0.0`, `0j`
3. **Empty Sequences:** `""` (str), `b""` (bytes), `[]` (list), `()` (tuple), `range(0)`
4. **Empty Mappings & Sets:** `{}` (dict), `set()`, `frozenset()`
5. **Custom Classes:** Instances defining `__bool__` returning `False` or `__len__` returning `0`.

**Literally everything else is TRUTHY.**

```python
# 1. Empty vs populated collections:
name = ""
print(bool(name))            # False — empty string is falsy

items = []
print(bool(items))           # False — empty list is falsy

# 2. ⚠️ Common Truthy Traps (Beginner Pitfalls):
print(bool("0"))             # True! (non-empty string of length 1)
print(bool("False"))         # True! (non-empty string)
print(bool(" "))             # True! (whitespace string has length 1)
print(bool([0]))             # True! (list contains 1 item)
print(bool([None]))          # True! (list contains 1 item)
print(bool(-1))              # True! (only 0 is falsy, negative numbers are truthy)
```

*(See [06 — Control Flow](06%20Control%20Flow.md#611-truth-value-testing-falsy-vs-truthy-across-all-python-types) for the complete type-by-type matrix, under-the-hood rules, and best practices in `if` statements).*

## 🚀 Stage 3 — In Practice / Why It Matters

In AI code you'll constantly convert API responses (strings/JSON) into numbers, build conditions
on truthiness ("did we get any results?"), and use `%`/`//` for batching and token math.

You will also use `is None` and `is not None` on almost every script you write — LLM function parameters
often default to `None` (e.g. `temperature=None`, `max_tokens=None`), and you check whether the user
provided one before applying defaults.

**Common beginner mistakes (the reasoning):**
1. **`=` vs `==`** — `=` *assigns*, `==` *compares*. `if x = 5:` is an error; you want `if x == 5:`.
2. **Adding a string and a number** — `"3" + 5` raises `TypeError`. Convert first: `int("3") + 5`.
   *Reason:* `+` means "concatenate" for strings and "add" for numbers; Python won't guess.
3. **Float surprises** — `0.1 + 0.2` prints `0.30000000000000004`. Floats are approximate; never
   compare them with `==` for equality — compare with a small tolerance instead.
4. **Forgetting `input()` returns a string** — `input()` then doing math without `int(...)` fails.
5. **Using `== None` instead of `is None`** — `if result == None:` works in simple cases, but PEP 8
   requires `if result is None:`. *Reason:* `is` checks the memory address directly; `==` runs
   the object's equality comparison method, which can be slow or overridden.
6. **Using `is` to compare values** — writing `if score is 100:` or `if name is "Ada":`. *Reason:*
   `is` checks memory address (`id()`), not value content. Python can assign separate addresses to
   identical numbers or strings. Always use `==` for values.

### Try it yourself
Predict, then run: `print(10 / 3)`, `print(10 // 3)`, `print(10 % 3)`, `print(2 ** 10)`.
Then test:
```python
x = [10, 20]
y = [10, 20]
print(x == y, x is y, id(x) == id(y))
```

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `SyntaxError` on `if x = 5:` | Used `=` (assign) instead of `==` (compare) | Use `==` in conditions |
| `SyntaxWarning: "is" with 'int' literal` | Used `is` with a number (`x is 5`) | Use `==` for values (`x == 5`); use `is` only for identity (`is None`) |
| `TypeError: can only concatenate str (not "int") to str` | Added a string and a number | Convert first: `int("3") + 5` or `str(5)` |
| `ValueError: invalid literal for int()` | `int("forty")` — not a numeric string | Only cast numeric strings; validate input |
| `0.1 + 0.2 == 0.3` returns False | Binary floating-point representation has rounding inaccuracies | Never use `==` on floats; use `abs(a - b) < 1e-9` or `math.isclose(a, b)` |

## 📌 Quick Reference

```python
x = 5            # int   |  5.0 float  |  "5" str  |  True bool  |  None
int("5"); float("5"); str(5); bool(0)        # casting
a, b = 10, 20; a, b = b, a; x = y = 0        # multiple, swap & chained assignment
x += 1; x -= 2; x *= 3                       # augmented assignment
7 / 2  # 3.5   7 // 2  # 3   7 % 2  # 1   2 ** 3  # 8
==  !=  <  >  <=  >=        and  or  not     # compare / logic
id(x)            # unique memory address number of an object
a == b           # True if VALUES match (content equality)
a is b           # True if EXACT SAME object in memory (id(a) == id(b))
x is None        # standard check for None (also: x is not None)
math.isclose(a, b) # safe float equality check: abs(a - b) < 1e-9
```
- Falsy values: `False`, `None`, `0`, `0.0`, `0j`, `""`, `b""`, `[]`, `()`, `{}`, `set()`, `range(0)`. Everything else is truthy (including `"0"`, `[0]`, `[None]`, and `-1`).
- Use `==` for values; use `is` for object identity and checking `None`.
- For float equality: use `math.isclose(a, b)` or `abs(a - b) < tolerance`.

## 🛑 STOP — Self-Check

What are the **values and types** of `a` and `b` here, and why are they different?

```python
a = 9 / 3
b = 9 // 3
```

<details><summary>Answer</summary>

`a` is **`3.0`**, a **`float`** — the `/` operator always performs true division and returns a
float. `b` is **`3`**, an **`int`** — `//` is floor division on two ints and stays an int. Same
mathematical answer, different *type*, which matters when later code expects one or the other.
</details>
