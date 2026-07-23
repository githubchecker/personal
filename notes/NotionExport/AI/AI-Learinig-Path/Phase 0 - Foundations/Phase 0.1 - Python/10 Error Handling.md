# 10 — Error Handling

> Phase 0 · Module 0.1 · Lesson 10 of 16

## 🗺️ Stage 0 — Concept Map

Real programs hit problems: a file is missing, a network call fails, an LLM returns malformed JSON.
**Error handling** is how you anticipate failures and respond gracefully instead of crashing. AI
systems lean on networks and external services constantly, so this skill is essential — and it
pairs directly with the retry/fallback patterns you'll build in later phases.

## 🔑 New Terms (plain English)

- **Exception** — Python's signal that it can't continue normally.
- **Traceback** — the error report showing what failed and where.
- **`try` / `except`** — run risky code, and handle a failure if it happens.
- **`raise`** — deliberately signal an error.
- **Custom exception** — your own error type (a subclass of `Exception`).

## 🎈 Stage 1 — The Simple Idea (analogy: a safety net)

When a trapeze artist might fall, you string a **safety net** under the risky part of the act —
not under the whole circus. In Python you wrap the risky lines in a `try` block; if something goes
wrong, the `except` block catches it and you decide what to do, instead of the whole program
ending.

**The "Aha!":** an **exception** is Python's way of saying "I can't continue normally here." You
either let it stop the program (the default), or **catch** it and handle it.

## ⚙️ Stage 2 — How It Actually Works

### 10.1 What an unhandled error looks like

```python
print(10 / 0)
# ZeroDivisionError: division by zero   <- the program stops with a "traceback"
```

The error's **type** (`ZeroDivisionError`) tells you what went wrong. Common built-in types:
`ValueError` (right type, bad value), `TypeError` (wrong type), `KeyError` (missing dict key),
`IndexError` (list index out of range), `FileNotFoundError`.

### 10.2 try / except

```python
try:
    age = int(input("Age? "))       # might fail if the user types "abc"
    print(f"Next year you'll be {age + 1}")
except ValueError:                  # catch ONLY this kind of error
    print("Please enter a whole number.")
```

Catch different errors differently, and access the error object with `as`:

```python
try:
    result = risky_operation()
except FileNotFoundError:
    print("File missing — using defaults.")
except (ValueError, TypeError) as error:   # catch several types together
    print(f"Bad data: {error}")            # the error object holds the message
```

### 10.3 else and finally

```python
try:
    data = load_file("config.json")
except FileNotFoundError:
    print("not found")
else:
    print("loaded!")        # runs ONLY if no exception happened
finally:
    print("done")           # ALWAYS runs — success or failure (great for cleanup)
```

`finally` is for cleanup that must happen no matter what (closing a connection, releasing a lock).

### 10.4 Raising your own errors

```python
def set_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")   # signal a problem deliberately
    return age

# Define a custom exception type for your domain by subclassing Exception:
class RetrievalError(Exception):
    """Raised when document retrieval fails."""

def fetch_docs(query):
    if not query:
        raise RetrievalError("query was empty")
```

Custom exceptions let callers catch *your* specific failure (`except RetrievalError:`) without
accidentally swallowing unrelated errors.

### 10.5 The Pythonic mindset: EAFP

Python favours **EAFP** — "Easier to Ask Forgiveness than Permission": *try* the operation and
handle failure, rather than checking every precondition first (LBYL, "Look Before You Leap").

```python
# EAFP (idiomatic): just try it
try:
    value = data["key"]
except KeyError:
    value = "default"

# (LBYL alternative: if "key" in data: ... — fine too, but EAFP is common in Python)
```

## 🚀 Stage 3 — In Practice / Why It Matters

Every external call in an AI system can fail: rate limits (`429`), timeouts, malformed responses.
You'll wrap these in `try/except`, raise domain errors like `RetrievalError`, and combine this with
retries (`tenacity`) and fallbacks (try model A, on failure try model B). Good error handling is
the difference between a demo and a production system.

**Common beginner mistakes (the reasoning):**
1. **Bare `except:`** (catching *everything*) — hides real bugs and even catches Ctrl+C. Catch the
   **specific** exception you expect. *Reason:* you should only handle errors you understand.
2. **Swallowing errors silently** — `except Exception: pass` makes failures invisible. At minimum,
   log it. *Reason:* silent failure is the hardest kind to debug.
3. **Putting too much in one `try`** — wrap only the risky line(s) so you know exactly what failed.
4. **Using exceptions for normal control flow** that an `if` handles better — reserve them for
   genuine "can't proceed" situations.

### Try it yourself
Write a `safe_divide(a, b)` that returns the quotient, but returns the string `"undefined"` instead
of crashing when `b` is `0`.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Real bugs stay hidden | Bare `except:` catches everything | Catch the specific type (`except ValueError`) |
| Failures vanish with no message | `except Exception: pass` swallows them | At least log; handle only what you expect |
| Cleanup didn't run | Cleanup placed in `try`/`except` only | Put guaranteed cleanup in `finally` |
| Your `except` never triggers | Catching the wrong exception type | Match the exception actually raised |

## 📌 Quick Reference

```python
try:
    risky()
except (ValueError, KeyError) as e:
    handle(e)
else:
    ...          # ran only if no exception
finally:
    ...          # always runs (cleanup)

raise ValueError("message")
class MyError(Exception): ...   # custom error type
```

## 🛑 STOP — Self-Check

In a `try/except/else/finally` block, which part runs when **no** exception occurs, and which part
runs **regardless** of whether one occurred?

<details><summary>Answer</summary>

The **`else`** block runs only when the `try` completes with **no exception**. The **`finally`**
block runs **always** — whether the code succeeded, raised and was caught, or even raised something
uncaught — which is why `finally` is the right place for cleanup that must happen no matter what.
</details>
