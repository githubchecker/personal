# 07 — Functions

> Phase 0 · Module 0.1 · Lesson 7 of 16

## 🗺️ Stage 0 — Concept Map

A **function** is a named, reusable block of code. Functions are how you stop repeating yourself,
give names to ideas, and build programs out of small testable parts. Everything from here on —
decorators, methods, async functions, API handlers — is a variation on the plain function. This is
one of the most important lessons in the module.

## 🔑 New Terms (plain English)

- **Function** — a named, reusable block of code.
- **Parameter** — the input name in the definition.
- **Argument** — the actual value you pass in.
- **Return value** — what the function hands back (`None` if no `return`).
- **Scope** — where a variable is visible (local inside vs global outside).

## 🎈 Stage 1 — The Simple Idea (analogy: a kitchen appliance)

A function is like a blender: you put **ingredients in** (arguments), it does a defined **job**
(the body), and it hands you a **result out** (the return value). Once built, you reuse it
endlessly without caring about the internal wiring — you just feed it inputs and take the output.

**The "Aha!":** define the recipe **once** with `def`, then **call** it as many times as you like
with different inputs. A function packages behaviour behind a name.

## ⚙️ Stage 2 — How It Actually Works

### 7.1 Defining and calling

```python
def greet(name):            # "def" names the function; "name" is a PARAMETER (input slot)
    return f"Hello, {name}!"  # "return" hands a value back to the caller

message = greet("Ada")      # CALL it with an ARGUMENT; message = "Hello, Ada!"
print(greet("Bo"))          # reuse with a different input
```

- **parameter** = the variable in the definition (`name`).
- **argument** = the actual value you pass in (`"Ada"`).
- A function with no `return` gives back `None` automatically.

### 7.2 Multiple parameters, defaults, keyword arguments

```python
def power(base, exponent=2):     # exponent has a DEFAULT -> optional to pass
    return base ** exponent

print(power(5))            # 25  — uses default exponent=2
print(power(5, 3))         # 125 — positional arguments, matched by order
print(power(exponent=3, base=2))  # 8 — KEYWORD arguments, matched by name (order-free)
```

Keyword arguments make calls self-documenting: `create_user(name="Ada", admin=True)` reads clearly.

### 7.3 Flexible arguments: `*args` and `**kwargs`

```python
def total(*numbers):        # *args collects EXTRA positional args into a tuple
    return sum(numbers)
print(total(1, 2, 3, 4))    # 10

def describe(**info):       # **kwargs collects EXTRA keyword args into a dict
    for key, value in info.items():
        print(f"{key}={value}")
describe(name="Ada", role="engineer")   # name=Ada / role=engineer
```

You'll see `*args, **kwargs` everywhere in libraries — it means "accept any extra arguments."

### 7.4 Docstrings and type hints

```python
def average(numbers: list[float]) -> float:   # type hints: inputs are floats, returns a float
    """Return the arithmetic mean of a list of numbers."""  # docstring: what it does
    return sum(numbers) / len(numbers)
```

Type hints don't change behaviour (Python doesn't enforce them at runtime — Lesson 13), but they
document intent and power editor autocomplete and error-checking.

### 7.5 Scope — where variables live

```python
total = 0                    # GLOBAL (module-level)

def add(x):
    result = total + x       # can READ the global "total"
    return result            # "result" is LOCAL — it vanishes when the function ends

add(5)
# print(result)              # NameError! "result" doesn't exist out here
```

Variables created inside a function are **local** to that call. This isolation is a feature: a
function's internals can't accidentally clobber the rest of your program.

### 7.6 `lambda` — tiny inline functions

```python
square = lambda x: x * x     # a one-expression anonymous function
print(square(4))             # 16

# Most common use: a quick "key" for sorting (Lesson 04).
people = [("Ada", 36), ("Bo", 29)]
print(sorted(people, key=lambda person: person[1]))   # sort by age -> Bo, Ada
```

## 🚀 Stage 3 — In Practice / Why It Matters

You'll wrap every LLM call, every retrieval step, every tool in a function — small, named, testable
units you compose into pipelines and agents. `*args/**kwargs` and keyword arguments are how AI
libraries expose dozens of options without chaos.

**Common beginner mistakes (the reasoning):**
1. **The mutable default argument trap** — `def f(items=[]):` reuses the *same* list across calls,
   accumulating data unexpectedly. Use `def f(items=None):` then `if items is None: items = []`.
   *Reason:* default values are created once, at definition time.
2. **Forgetting `return`** — a function that only `print`s gives back `None`; `x = f()` then makes
   `x` `None`. Return the value you need.
3. **Confusing print and return** — `print` shows text to a human; `return` hands a value to code.
   In real programs you almost always want `return`.
4. **Expecting to read a local outside** — locals don't exist after the function ends.

### Try it yourself
Write `def greet(name, greeting="Hello"): ...` that returns `"Hello, Ada!"` by default but lets the
caller override the greeting (e.g. `greet("Ada", "Hi")`).

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `TypeError: f() missing 1 required positional argument` | Called without a needed argument | Pass it, or give the parameter a default |
| `NameError: name 'result' is not defined` | Used a local variable outside its function | Return it; locals vanish when the function ends |
| Function "returns nothing" (`None`) | Forgot `return` | Add `return value` |
| Default list grows across calls | Mutable default `def f(x=[])` | Use `def f(x=None): x = x or []` |

## 📌 Quick Reference

```python
def greet(name, greeting="Hello") -> str:
    return f"{greeting}, {name}!"
greet("Ada"); greet("Bo", greeting="Hi")   # positional / keyword
def total(*args): ...       # extra positionals -> tuple
def opts(**kwargs): ...      # extra keywords -> dict
square = lambda x: x * x     # tiny inline function
```

## 🛑 STOP — Self-Check

Why is this function buggy across repeated calls, and what's the fix?

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket
```

<details><summary>Answer</summary>

The default `basket=[]` is created **once** when the function is defined, and every call that
omits `basket` reuses that **same** list — so items pile up across calls
(`add_item("a")` → `['a']`, then `add_item("b")` → `['a', 'b']`). Fix it with a `None` sentinel:
`def add_item(item, basket=None): if basket is None: basket = []`. This makes a fresh list per call.
</details>
