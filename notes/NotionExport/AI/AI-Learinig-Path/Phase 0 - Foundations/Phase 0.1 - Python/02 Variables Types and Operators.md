# 02 — Variables, Types & Operators

> Phase 0 · Module 0.1 · Lesson 2 of 16

## 🗺️ Stage 0 — Concept Map

Programs move **data** around: numbers, text, true/false flags. This lesson covers how Python
**stores** data (variables), the **kinds** of data (types), and how you **combine** data
(operators). Every line of code you ever write uses these. It comes right after setup because you
can't do anything without it.

## 🔑 New Terms (plain English)

- **Variable** — a named label that holds a value.
- **Dynamic typing** — Python infers a value's type; you don't declare it.
- **Type** — the kind of value: `int`, `float`, `str`, `bool`, `None`.
- **Casting** — converting a value from one type to another (`int("5")`).
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
type of whatever you assign. The *value* has a type, the *label* doesn't.

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

### 2.5 Truthiness

Every value is either "truthy" or "falsy" when used as a condition. **Falsy** values: `0`, `0.0`,
`""` (empty string), `[]` (empty list), `{}` (empty dict), and `None`. Everything else is truthy.

```python
name = ""
if name:                 # empty string is falsy -> this block is skipped
    print("has a name")
else:
    print("no name")     # this runs
```

## 🚀 Stage 3 — In Practice / Why It Matters

In AI code you'll constantly convert API responses (strings/JSON) into numbers, build conditions
on truthiness ("did we get any results?"), and use `%`/`//` for batching and token math. Knowing
that `/` returns a float and `==` compares values prevents a surprising number of bugs.

**Common beginner mistakes (the reasoning):**
1. **`=` vs `==`** — `=` *assigns*, `==` *compares*. `if x = 5:` is an error; you want `if x == 5:`.
2. **Adding a string and a number** — `"3" + 5` raises `TypeError`. Convert first: `int("3") + 5`.
   *Reason:* `+` means "concatenate" for strings and "add" for numbers; Python won't guess.
3. **Float surprises** — `0.1 + 0.2` prints `0.30000000000000004`. Floats are approximate; never
   compare them with `==` for equality — compare with a small tolerance instead.
4. **Forgetting `input()` returns a string** — `input()` then doing math without `int(...)` fails.

### Try it yourself
Predict, then run: `print(10 / 3)`, `print(10 // 3)`, `print(10 % 3)`, `print(2 ** 10)`.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `SyntaxError` on `if x = 5:` | Used `=` (assign) instead of `==` (compare) | Use `==` in conditions |
| `TypeError: can only concatenate str (not "int") to str` | Added a string and a number | Convert first: `int("3") + 5` or `str(5)` |
| `ValueError: invalid literal for int()` | `int("forty")` — not a numeric string | Only cast numeric strings; validate input |
| `0.1 + 0.2` → `0.30000000000000004` | Floats are approximate | Don't `==` floats; compare with a tolerance |

## 📌 Quick Reference

```python
x = 5            # int   |  5.0 float  |  "5" str  |  True bool  |  None
int("5"); float("5"); str(5); bool(0)        # casting
7 / 2  # 3.5   7 // 2  # 3   7 % 2  # 1   2 ** 3  # 8
==  !=  <  >  <=  >=        and  or  not     # compare / logic
```
- Falsy values: `0`, `0.0`, `""`, `[]`, `{}`, `None`. Everything else is truthy.

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
