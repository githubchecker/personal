# 09 — Decorators & Closures

> Phase 0 · Module 0.1 · Lesson 9 of 16

## 🗺️ Stage 0 — Concept Map

This lesson explains the mysterious `@something` lines you'll see above functions in every AI
framework (FastAPI routes, `@tool`, `tenacity` retries). To understand decorators you first need
two ideas: functions are **values** you can pass around, and a function can **remember** variables
from where it was created (a **closure**). This is the most "advanced" core-Python topic — take it
slowly.

## 🔑 New Terms (plain English)

- **First-class function** — a function you can store, pass, or return like any value.
- **Closure** — an inner function that remembers variables from its outer function.
- **Decorator** — a function that wraps another to add behaviour, applied with `@name`.
- **Wrapper** — the inner function a decorator returns.
- **`functools.wraps`** — keeps the original function's name and docstring on the wrapper.

## 🎈 Stage 1 — The Simple Idea (analogy: gift-wrapping)

A **decorator** wraps a function in extra behaviour without changing the function's own code — like
gift-wrapping a box. The present inside is unchanged; the wrapping adds something around it
(logging, timing, retrying, access checks). You apply the wrap with one line: `@decorator`.

**The "Aha!":** in Python, functions are ordinary objects — you can store them in variables, pass
them as arguments, and return them from other functions. A decorator is just *a function that takes
a function and returns a new, wrapped function.*

## ⚙️ Stage 2 — How It Actually Works

### 9.1 Functions are first-class values

```python
def shout(text):
    return text.upper()

yell = shout              # store the function itself (no parentheses!) in another name
print(yell("hi"))         # 'HI'

def apply(func, value):   # a function can take ANOTHER function as an argument
    return func(value)
print(apply(shout, "hello"))   # 'HELLO'
```

### 9.2 Closures — a function that remembers

A function defined **inside** another can capture the outer function's variables, and keeps them
even after the outer function has returned. That captured bundle is a **closure**.

```python
def make_multiplier(factor):       # outer function
    def multiply(number):          # inner function...
        return number * factor     # ...remembers "factor"
    return multiply                # hand back the inner function

double = make_multiplier(2)        # factor=2 is "baked in"
triple = make_multiplier(3)        # factor=3 is "baked in"
print(double(10))                  # 20
print(triple(10))                  # 30
```

`double` "remembers" `factor=2` even though `make_multiplier` has already finished. That memory is
the closure — and it's the machinery decorators are built on.

### 9.3 A decorator, built up

```python
import functools

def logged(func):                          # takes the function to wrap
    @functools.wraps(func)                 # keeps the original name/docstring on the wrapper
    def wrapper(*args, **kwargs):          # accepts ANY arguments (Lesson 07)
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)     # call the real function
        print(f"{func.__name__} returned {result}")
        return result                      # pass its result back out
    return wrapper                         # return the wrapped version

@logged                                    # <-- apply the decorator
def add(a, b):
    return a + b

add(2, 3)
# calling add
# add returned 5
```

The `@logged` line is exactly equivalent to writing `add = logged(add)`. The decorator runs once,
replacing `add` with `wrapper`. Now every call to `add` is logged — without touching `add`'s body.

`*args, **kwargs` in the wrapper let the decorator work on *any* function regardless of its
parameters, and `@functools.wraps(func)` preserves the original's identity (without it, `add.__name__`
would wrongly say `"wrapper"`).

## 🚀 Stage 3 — In Practice / Why It Matters

You won't write many decorators, but you'll **use** them constantly:
- `@app.get("/items")` (FastAPI) registers a function as a web endpoint — Phase 1.
- `@retry(...)` (tenacity) auto-retries a flaky API call — Phase 1/4.
- `@tool` marks a function as something an agent can call — Phase 3.
- `@property`, `@staticmethod` shape classes — Lesson 12.

Recognising "a decorator wraps my function with extra behaviour" demystifies a huge amount of
real-world code.

**Common beginner mistakes (the reasoning):**
1. **Adding `()` when storing a function** — `yell = shout()` *calls* it; `yell = shout` stores it.
   *Reason:* parentheses mean "invoke now."
2. **Omitting `*args, **kwargs`** in the wrapper, so the decorator only works on functions with a
   specific signature. Accept anything.
3. **Forgetting `@functools.wraps`** — debugging gets confusing because every wrapped function
   reports the name `wrapper`.
4. **Expecting the decorator to run on every call** — the *decorator* runs once (at definition);
   the *wrapper* runs on every call. Put per-call logic inside `wrapper`.

### Try it yourself
Write a `timed` decorator that prints how long the wrapped function took (use
`import time; start = time.perf_counter()` before the call and the difference after).

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| The function runs when you meant to store it | Added `()` — `x = func()` calls it | Store without parentheses: `x = func` |
| Decorated function breaks on some arguments | Wrapper didn't accept `*args, **kwargs` | Define `def wrapper(*args, **kwargs)` |
| `func.__name__` shows `'wrapper'` | Missing `@functools.wraps` | Add `@functools.wraps(func)` to the wrapper |
| Your logic runs once, not per call | Code placed outside `wrapper` | Put per-call logic **inside** `wrapper` |

## 📌 Quick Reference

```python
import functools
def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

@logged                       # same as: add = logged(add)
def add(a, b): return a + b
```

## 🛑 STOP — Self-Check

What is a **closure**, and how does it make the `@logged` decorator above possible?

<details><summary>Answer</summary>

A **closure** is an inner function that **remembers variables from the enclosing function** even
after that outer function has returned. In `@logged`, the inner `wrapper` closes over `func` (the
original function it was given), so each time `wrapper` runs it still has access to the specific
function it's meant to wrap. Without closures, `wrapper` would have no way to "remember" which
function to call.
</details>
