# $\Huge\color{#0D47A1}{\textsf{Phase 0.1 — Python All-In-One Revision Guide}}$

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Curriculum](https://img.shields.io/badge/Roadmap-Phase%200.1-0288D1?style=for-the-badge&logo=compass&logoColor=white)](README.md)
[![Priority](https://img.shields.io/badge/Priority-MUST%20KNOW-D32F2F?style=for-the-badge&logo=target&logoColor=white)](../../AI%20Engineer%20Architect%20Road%20Map.md)
[![Format](https://img.shields.io/badge/Format-Executive%20Cheat%20Sheet-2E7D32?style=for-the-badge&logo=quicklook&logoColor=white)](#)

> $\color{#546E7A}\mathbf{Navigation:}$ **Phase 0** · **Module 0.1** · **All-In-One Fast Revision Reference** · [Phase 0.1 — Python Index](README.md)

---

### 📑 Fast Revision Chapter Directory

| 🔹 Part 1: Core Fundamentals | 🔸 Part 2: Functions & Control | 🧱 Part 3: OOP Architecture | 🚀 Part 4: Advanced & AI Ops |
| :--- | :--- | :--- | :--- |
| • [01 — Setup & How Runs](#chapter-01)<br>• [02 — Variables & Types](#chapter-02)<br>• [03 — Strings In Depth](#chapter-03)<br>• [04 — Lists & Tuples](#chapter-04) | • [05 — Dictionaries & Sets](#chapter-05)<br>• [06 — Control Flow](#chapter-06)<br>• [07 — Functions](#chapter-07)<br>• [08 — Comprehensions](#chapter-08)<br>• [09 — Decorators](#chapter-09)<br>• [10 — Error Handling](#chapter-10)<br>• [11 — Modules & Files](#chapter-11) | • [12.1 — Object Lifecycle](#chapter-12-1)<br>• [12.2 — Inheritance](#chapter-12-2)<br>• [12.3 — Dunder Methods](#chapter-12-3)<br>• [12.4 — Properties](#chapter-12-4)<br>• [12.5 — Method Types](#chapter-12-5)<br>• [12.6 — Advanced Types](#chapter-12-6) | • [13 — Built-in Functions](#chapter-13)<br>• [14 — Advanced Python](#chapter-14)<br>• [22 — Type Hints & Pydantic](#chapter-22)<br>• [23 — Concurrency](#chapter-23)<br>• [24 — AI Essentials: NumPy](#chapter-24)<br>• [25 — Milestone CLI Tool](#chapter-25) |

---

<a id="chapter-01"></a>

## 📘 $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{01 — How Python Runs and Setup}}$

* $\color{#0288D1}\blacktriangleright$ **Execution Pipeline:** Python reads plain-text `.py` source code $\to$ compiles it internally to **bytecode** (cached as `.pyc` in `__pycache__`) $\to$ **PVM (Python Virtual Machine)** executes it on CPU/RAM.
* $\color{#00897B}\blacktriangleright$ **PATH & Verification:** The OS searches `PATH` directories to locate `python.exe` (always check `Add python.exe to PATH` on Windows).
  ```powershell
  python --version   # or 'py --version' on Windows
  ```
* $\color{#BF360C}\blacktriangleright$ **REPL vs. Scripts:** Run `python` alone for the interactive scratchpad (`>>>`, exit via `exit()` or `Ctrl+Z` + Enter); run `python main.py` to execute script files.
* $\color{#4A148C}\blacktriangleright$ **Virtual Environments (`venv`):** Isolates project dependencies into a local `site-packages` folder to prevent global version collisions. Under the hood, it creates lightweight stubs + `pyvenv.cfg` pointing to base Python, and activation temporarily prepends `.venv\Scripts` to `PATH`.
* $\color{#1B5E20}\blacktriangleright$ **Core `venv` Lifecycle:**
  ```powershell
  python -m venv .venv                 # Create (-m runs stdlib module as script)
  .\.venv\Scripts\Activate.ps1         # Activate (PowerShell) | CMD: activate.bat | Unix: source .venv/bin/activate
  python -c "import sys; print(sys.prefix)"  # Verify active venv path
  deactivate                           # Exit venv
  ```
* $\color{#D32F2F}\blacktriangleright$ **PowerShell Execution Policy Trap:** If `Activate.ps1` throws `PSSecurityException`, run once:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
* $\color{#00897B}\blacktriangleright$ **Package & Manifest Workflow (`pip`):** Install only while `(.venv)` is active and record dependencies in `requirements.txt`.
  ```powershell
  python -m pip install --upgrade pip
  pip install requests                 # Installs into .venv/Lib/site-packages (verify with: pip show requests)
  pip freeze > requirements.txt        # Export exact versions
  pip install -r requirements.txt      # Reinstall on another machine
  ```
* $\color{#BF360C}\blacktriangleright$ **Git Hygiene:** Never commit `.venv/` (machine-specific paths/binaries) or cache files; always commit `requirements.txt`.
  ```gitignore
  .venv/
  __pycache__/
  *.pyc
  ```
* $\color{#4A148C}\blacktriangleright$ **VS Code Setup:** `Ctrl+Shift+P` $\to$ `Python: Select Interpreter` $\to$ pick `.venv\Scripts\python.exe` (auto-activates integrated terminal).
* $\color{#1B5E20}\blacktriangleright$ **Syntax Rules:** Comments start with `#`. Code blocks are defined strictly by **4 spaces of indentation** (no `{}`).
* $\color{#0288D1}\blacktriangleright$ **Environment Tooling Alternatives:** `venv` (built-in default), `uv` (Rust-based, ultra-fast drop-in replacement), `conda` (heavy; only for complex non-Python C/Fortran/CUDA system dependencies).

---

<a id="chapter-02"></a>

## 📗 $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{02 — Variables, Types and Operators}}$

* $\color{#0288D1}\blacktriangleright$ **Dynamic Typing & Memory Model:** Variables are untyped labels pointing to typed objects in memory; reassignment moves the label to a new object address.
* $\color{#00897B}\blacktriangleright$ **Naming Conventions:** Use `snake_case` for variables and `ALL_CAPS` by convention for constants (Python has no `const` keyword). Case-sensitive; must start with letter or `_`; cannot use reserved keywords.
* $\color{#BF360C}\blacktriangleright$ **Shorthand Assignments:**
  ```python
  a, b = 10, 20     # Multiple assignment
  a, b = b, a       # Swap without temp variable
  x = y = z = 0     # Chained assignment (safe for immutables)
  x += 1; x *= 2    # Augmented assignment
  ```
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** `a = b = []` aliases both names to the *same* mutable list in memory. Always initialize mutables separately: `a, b = [], []`.
* $\color{#4A148C}\blacktriangleright$ **Core Built-in Types:**
  * $\color{#0288D1}\bullet$ `int` (arbitrary precision), `float` (64-bit IEEE 754), `str` (immutable Unicode), `bool` (subclass of `int`: `True == 1`, `False == 0`), `NoneType` (`None` singleton representing absence of value; distinct from `0`, `False`, `""`).
* $\color{#1B5E20}\blacktriangleright$ **Type Checking:** Prefer `isinstance(x, int)` over `type(x) == int` because `isinstance` respects inheritance (e.g., `isinstance(True, int)` is `True`).
* $\color{#0288D1}\blacktriangleright$ **Casting:** `int()`, `float()`, `str()`, `bool()`. Note `input()` always returns `str`, and `"3" + 5` raises `TypeError` (no implicit coercion).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** `int("42.8")` raises `ValueError`; cast decimal strings via `int(float("42.8"))`.
* $\color{#00897B}\blacktriangleright$ **Operators:**
  * $\color{#0288D1}\bullet$ **Arithmetic:** `+`, `-`, `*`, `/` (**always returns `float`**, e.g., `9 / 3 -> 3.0`), `//` (floor division, drops remainder: `9 // 3 -> 3`), `%` (modulo/remainder), `**` (exponentiation).
  * $\color{#0288D1}\bullet$ **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=` (`=` assigns, `==` compares).
  * $\color{#0288D1}\bullet$ **Logical (`and`, `or`, `not`):** Use **short-circuit evaluation** (`A and B` skips `B` if `A` is falsy; `A or B` skips `B` if `A` is truthy), enabling safe guards like `if client is not None and client.is_ready():`.
* $\color{#BF360C}\blacktriangleright$ **Float Comparison Trap:** Binary floats are approximate (`0.1 + 0.2` is `0.30000000000000004`, so `0.1 + 0.2 == 0.3` is `False`). Always compare within a tolerance:
  ```python
  import math
  abs(a - b) < 1e-9                               # abs() prevents negative-diff false positives
  math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12) # Preferred stdlib approach
  ```
* $\color{#4A148C}\blacktriangleright$ **Identity (`is`) vs. Equality (`==`) & `id()`:**
  * $\color{#0288D1}\bullet$ `id(x)` returns the object's unique memory address. `==` compares **values**; `is` / `is not` compares **memory identity** (`id(a) == id(b)`).
  ```python
  a, b = [1, 2], [1, 2]; c = a
  a == b  # True  (same content)
  a is b  # False (different objects)
  c is a  # True  (same object)
  ```
  * $\color{#2E7D32}\bullet$ **Golden Rule:** Always check `None` using `is None` / `is not None` (fast singleton check, PEP 8).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Python caches small ints (`-5` to `256`) and short strings, so `x is y` may accidentally return `True`. Never use `is` for value comparison.
* $\color{#1B5E20}\blacktriangleright$ **Truthiness:**
  * $\color{#0288D1}\bullet$ **All Falsy Values:** `None`, `False`, `0`, `0.0`, `0j`, `""`, `b""`, `[]`, `()`, `{}`, `set()`, `frozenset()`, `range(0)` (and custom objects with `__bool__ -> False` or `__len__ -> 0`).
  * $\color{#0288D1}\bullet$ **Truthy Traps:** Everything else is `True`, including `"0"`, `"False"`, `" "` (whitespace), `[0]`, `[None]`, and negative numbers (`-1`).
  * $\color{#2E7D32}\bullet$ **Idiomatic Check:** Write `if items:` / `if not text:` instead of `if len(items) > 0:`.

---

<a id="chapter-03"></a>

## 📙 $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{03 — Strings In Depth}}$

* $\color{#0288D1}\blacktriangleright$ **Immutability:** Strings cannot be modified in place (`s[0] = "J"` $\to$ `TypeError`). Every method returns a **new** string — if you don't reassign (`s = s.strip()`), the result is silently discarded. To "edit", slice and concatenate (`"J" + s[1:]`).
* $\color{#00897B}\blacktriangleright$ **Literals & Escaping:** `'...'` and `"..."` are identical. Use `\"`, `\n` (newline), `\t` (tab) for escapes; `"""..."""` for multi-line strings (preserves line breaks); and `r"..."` (**raw strings**) to treat backslashes literally (Windows paths, regex).
* $\color{#BF360C}\blacktriangleright$ **Indexing & Slicing (`s[start:stop:step]`):** 0-based forward (`0` = first), negative from right (`-1` = last). Slicing uses a **half-open interval `[start, stop)`** (`start` inclusive, `stop` **exclusive** — so `s[0:3]` yields 3 chars: indices `0, 1, 2`). `s[::-1]` creates a reversed copy.
* $\color{#4A148C}\blacktriangleright$ **Length & Membership:** `len(s)` returns character count. `sub in s` / `not in` performs fast substring search — **case-sensitive** (normalize first: `"error" in resp.lower()`).
* $\color{#1B5E20}\blacktriangleright$ **String Methods:**
  * $\color{#00C853}\bullet$ **Core:** `.strip()` (trim whitespace), `.split(sep)` (str $\to$ list), `sep.join(list)` (list $\to$ str), `.replace(old, new)`, `.lower()` / `.upper()`, `.startswith(pre)` / `.endswith(suf)`.
  * $\color{#FFB300}\bullet$ **Occasional:** `.find(sub)` (first match index or `-1`), `.index(sub)` (raises `ValueError` if missing), `.count(sub)`, `.encode("utf-8")` / `.decode("utf-8")` (str $\leftrightarrow$ bytes).
  * $\color{#757575}\bullet$ **Reference:** `.capitalize()`, `.title()`, `.isalnum()`, `.isalpha()`, `.center()`, `.zfill()`, `.partition()`.
* $\color{#0288D1}\blacktriangleright$ **Loop Performance (`+=` vs. `join`):** Never concatenate strings with `+=` inside a loop — **Why:** immutability forces a full memory copy every iteration ($O(N^2)$). Append to a list and call `"".join(parts)` once ($O(N)$, single allocation).
* $\color{#00897B}\blacktriangleright$ **f-strings (`f"..."`):** Evaluate expressions inline and format with `:specifier`: `:.2f` (decimals), `:.2%` (percent), `:,` (thousands), `:5d` / `:<5` / `:>10` (width & alignment), and `f"{var=}"` (Python 3.8+ debug shorthand printing name + value).

#### Consolidated Code Reference
```python
# 1. Literals & Immutability
path = r"C:\new\path"              # raw string: \n is NOT a newline
s = "PYTHON"
# s[0] = "J"                       # TypeError: 'str' object does not support item assignment
s = "J" + s[1:]                    # 'JYTHON' (must build new string)

# 2. Indexing, Slicing [start:stop:step] & Membership
s = "PYTHON"                       # 0:P, 1:Y, 2:T, 3:H, 4:O, 5:N | -1:N, -6:P
s[0:3], s[2:], s[:3]               # 'PYT', 'THON', 'PYT' (stop is excluded)
s[::2], s[::-1]                    # 'PTO', 'NOHTYP' (step 2, reversed copy)
len(s), "TH" in s, "th" in s       # 6, True, False (case-sensitive)

# 3. Essential Methods (all return NEW strings; originals untouched)
raw = "  Hello, World  "
raw.strip()                        # 'Hello, World' (must assign to keep: raw = raw.strip())
"a,b,c".split(",")                 # ['a', 'b', 'c']
"-".join(["a", "b", "c"])          # 'a-b-c' (O(N) — use this instead of += in loops)
"python".replace("p", "P")         # 'Python'
"data.csv".startswith("d"), "data.csv".endswith(".csv")  # True, True
"python".find("th"), "python".find("z"), "Hello".count("l")  # 2, -1, 2
b = "hi".encode("utf-8"); b.decode("utf-8")  # b'hi' -> 'hi'

# 4. f-strings & Format Specifiers
name, score, tokens = "Ada", 0.8736, 1500
f"{name.upper()} | {score:.2f} | {score:.1%} | {tokens:,}"  # 'ADA | 0.87 | 87.4% | 1,500'
f"{42:5d} | {42:<5}| | {tokens=}"                           # '   42 | 42   | | tokens=1500'
```

---

<a id="chapter-04"></a>

## 🗂️ $\Large\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{04 — Lists and Tuples}}$

* $\color{#0288D1}\blacktriangleright$ **Lists vs. Tuples (Core):** `list` (`[...]`) is a mutable dynamic sequence; `tuple` (`(...)`) is an immutable fixed sequence (~20% less memory, hashable for dict keys/caches). Both support 0-based/negative indexing, `len()`, `in`, mixed types, and nesting.
  ```python
  fruits = ["apple", "banana", "cherry"]
  nested = [[1, 2], [3, 4]]              # nested[1][0] -> 3
  point = (3, 4)                         # point[0] = 9 -> TypeError (immutable)
  single = (42,)                         # trailing comma mandatory; (42) is just int 42
  ```

* $\color{#00897B}\blacktriangleright$ **Slicing (`seq[start:stop:step]`):** Half-open interval `[start, stop)` (`start` inclusive, `stop` exclusive; length = `stop - start`; `seq[:k] + seq[k:] == seq`). Always returns a **new** shallow copy. Unlike direct indexing (`IndexError`), slicing **safely clips** out-of-bounds indices.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** With a negative `step`, `start` must be greater than `stop`, otherwise Python silently returns `[]`.
  ```python
  d = ["A", "B", "C", "D", "E", "F"]
  d[:3], d[2:], d[-2:], d[:-2]           # ['A','B','C'], ['C','D','E','F'], ['E','F'], ['A','B','C','D']
  d[::2], d[::-1], d[4:1:-1]             # ['A','C','E'], reversed copy, ['E','D','C']
  d[1:4:-1], d[50:100]                   # [], [] (directional mismatch / out-of-bounds clipped safely)
  HEAD = slice(0, 3); d[HEAD]            # reusable slice() object -> ['A', 'B', 'C']
  ```

* $\color{#BF360C}\blacktriangleright$ **Mutable Slice Assignment (Lists Only):** Modify, expand, shrink, insert, or clear segments in place (preserving object `id()`).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Extended slices (`step != 1`) require an **exact length match** on replacement (`ValueError` otherwise).
  ```python
  a = ["a", "b", "c", "d"]
  a[1:3] = ["X", "Y", "Z"]               # replace & expand -> ['a', 'X', 'Y', 'Z', 'd']
  a[1:1] = ["INS"]                       # zero-length slice inserts without deleting
  del a[1:3]                             # delete slice in place (or a[1:3] = [])
  a[:] = []                              # clears list in place, preserving all references
  g = [0, 1, 2, 3]; g[::2] = [10, 20]    # ok (2 == 2); g[::2] = [10] -> ValueError
  ```

* $\color{#4A148C}\blacktriangleright$ **List Mutation & Merging:**
  * $\color{#0288D1}\bullet$ `.append(x)` ($O(1)$) adds **one** item (nests if given a list); `.extend(it)` / `+=` ($O(k)$) flattens in place; `a + b` ($O(n+m)$) allocates a **new** list (originals untouched).
  * $\color{#0288D1}\bullet$ `.pop()` is $O(1)$ at end, $O(N)$ at index `pop(0)`; `.insert(0, x)` and `.remove(val)` are $O(N)$ (use `collections.deque` for frequent left-end ops).
  ```python
  a = [1, 2]; a.append([3, 4])           # [1, 2, [3, 4]] (nested)
  b = [1, 2]; b.extend([3, 4])           # [1, 2, 3, 4]   (flat, in-place)
  c = [1, 2] + [3, 4]                    # [1, 2, 3, 4]   (new list; originals unchanged)
  b.insert(0, 9); b.remove(9); last = b.pop(); del b[0]
  ```

* $\color{#1B5E20}\blacktriangleright$ **Sorting & Reversing:**
  * $\color{#0288D1}\bullet$ In-place (mutates, **returns `None`**): `.sort(key=..., reverse=...)`, `.reverse()`.
  * $\color{#0288D1}\bullet$ Non-mutating (returns **new list**): `sorted(seq, key=..., reverse=...)`, `seq[::-1]`.
  * $\color{#0288D1}\bullet$ Zero-copy backward iterator ($O(1)$ RAM): `reversed(seq)`.
  ```python
  nums = [3, 1, 2]
  ordered = sorted(nums, reverse=True)   # [3, 2, 1]; nums still [3, 1, 2]
  nums.sort(); nums.reverse()            # mutates in place; both return None
  words = sorted(["pear", "fig"], key=len)  # ['fig', 'pear']
  for x in reversed(nums): pass          # lazy reverse stream, zero copy
  ```

* $\color{#0288D1}\blacktriangleright$ **Aliasing vs. Copying (and Rebinding):** Variables hold references. `b = a` creates an alias (`b is a` is `True`).
  * $\color{#0288D1}\bullet$ **Why `b = b + [4]` differs from `b.append(4)`:** `+` creates a new list and *rebinds* `b` (leaving `a` intact); `.append()` *mutates* the shared object.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** `[[]] * 3` creates 3 references to the *same* inner list; use `[[] for _ in range(3)]`.
  ```python
  a = [1, 2]; b = a; b.append(3)         # a is now [1, 2, 3] (aliased)
  c = a.copy()                           # shallow copy (also a[:] or list(a)); c is a -> False
  b = b + [4]                            # rebinds b to new list; a stays [1, 2, 3]
  ```

* $\color{#00897B}\blacktriangleright$ **Iteration & The Mutating-While-Iterating Pitfall:** Use `enumerate(seq)` for `(idx, val)` and `zip(a, b)` for lockstep iteration.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Removing items from a list while iterating over it skips elements — **Why:** Python increments an internal index while the list shifts left.
  ```python
  tags = ["AI", "test", "test", "ML"]
  # ❌ for t in tags: if t == "test": tags.remove(t)  -> ['AI', 'test', 'ML'] (skipped 2nd!)
  clean = [t for t in tags if t != "test"]            # 1. Comprehension (idiomatic, O(N))
  tags[:] = [t for t in tags if t != "test"]          # 2. In-place slice (preserves id(tags))
  for t in tags[:]:                                   # 3. Iterate shallow copy (remove() is O(N^2))
      if t == "test": tags.remove(t)
  for i in range(len(tags) - 1, -1, -1):              # 4. Iterate backwards for index-based del
      if tags[i] == "test": del tags[i]
  ```

* $\color{#BF360C}\blacktriangleright$ **Tuple Conversions & Operations:** Convert via `list(t)` to edit and `tuple(l)` to freeze/hash. Concatenation (`+`), repetition (`*`), and slicing all return new tuples.
  ```python
  rec = ("Ada", 36); tmp = list(rec); tmp[1] = 37; rec = tuple(tmp)  # ('Ada', 37)
  t = (1, 2) + (3, 4); zeros = (0,) * 3                              # (1, 2, 3, 4), (0, 0, 0)
  ```

* $\color{#4A148C}\blacktriangleright$ **Sequence Unpacking & `*` (Rest) Operator:** Positional count must match exactly (`ValueError` otherwise). `*var` gathers remaining items — **always as a `list`**, even from a tuple. Use `*_` to discard.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Only **one** `*` expression is allowed per assignment (`SyntaxError` otherwise).
  ```python
  first, *mid, last = (98, 85, 76, 45)   # first=98, mid=[85, 76] (list!), last=45
  uid, *_, status = ["u1", "EU", "adm", "active"]  # uid='u1', status='active'
  ```

* $\color{#1B5E20}\blacktriangleright$ **List vs. `array.array` vs. NumPy `ndarray`:**
  * $\color{#0288D1}\bullet$ `list`: dynamic object pointers, mixed types, no vectorized math.
  * $\color{#0288D1}\bullet$ `array.array('i', [1, 2])`: stdlib, single C primitive type, memory-compact, no vectorized math.
  * $\color{#0288D1}\bullet$ `np.ndarray`: 3rd-party (`numpy`), contiguous homogeneous numeric grid, C/CUDA vectorized math (`arr * 2`).

* $\color{#0288D1}\blacktriangleright$ **Custom Objects & The "Tuple of Mutables" Trap:** Collections store references. A tuple prevents reassigning its slots, **not** mutating mutable objects inside those slots.
  ```python
  class Doc:
      def __init__(self, text): self.text = text
  t = (Doc("v1"),)
  # t[0] = Doc("v2")                     # TypeError (tuple slot is immutable)
  t[0].text = "v2"                       # Allowed! Inner object mutated in place
  ```

---

<a id="chapter-05"></a>

## 🗃️ $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{05 — Dictionaries and Sets}}$

* $\color{#0288D1}\blacktriangleright$ **Dictionaries (`dict`) & Key Hashability:** $O(1)$ hash map of `key -> value` pairs. Values can be anything; **keys must be immutable and hashable** (`str`, `int`, `tuple`, `frozenset` — never `list` or `set`, else `TypeError: unhashable type`).
  ```python
  d = {"name": "Ada", "age": 36}
  # d[[1, 2]] = "bad"                      # TypeError: unhashable type: 'list'
  ```

* $\color{#00897B}\blacktriangleright$ **Safe Lookups & Nested Traversal:** `d[k]` raises `KeyError` if missing; `d.get(k, default)` returns `None` or fallback without mutating `d`.
  * $\color{#0288D1}\bullet$ **Nested `None` Trap:** `d.get("profile", {}).get("font")` crashes with `AttributeError` if `"profile"` exists with value `None` (`.get()` only uses the default when the key is *absent*). Guard with `(d.get("profile") or {})`.
  ```python
  user = {"name": "Bo", "profile": None}
  user.get("email", "n/a")                 # 'n/a' (safe fallback; user unchanged)
  (user.get("profile") or {}).get("font", "Inter")  # 'Inter' (safe even when value is None)
  ```

* $\color{#BF360C}\blacktriangleright$ **Mutating, Merging & `setdefault()`:**
  * $\color{#0288D1}\bullet$ `d[k] = v` adds/overwrites; `del d[k]` deletes (`KeyError` if missing); `d.pop(k, default)` removes & returns safely; `d.popitem()` pops the last inserted pair.
  * $\color{#0288D1}\bullet$ Merging (Python 3.9+): `d1 | d2` creates a **new** dict (right side wins on conflict); `d1 |= d2` or `d1.update(d2)` mutates in place.
  * $\color{#0288D1}\bullet$ **`.get()` vs. `.setdefault()`:** `.get()` is read-only; `d.setdefault(k, default)` **inserts** `d[k] = default` in place if missing and returns it (idiomatic for grouping/nested init).
  ```python
  cfg = {"model": "gpt-4o", "temp": 0.7} | {"temp": 0.2}  # new dict: {'model': 'gpt-4o', 'temp': 0.2}
  temp = cfg.pop("temp", 0.5)              # 0.2 (removed from cfg); cfg.pop("x", 0) -> 0
  groups = {}
  groups.setdefault("user", []).append("Hi")  # inserts 'user': [] then appends -> {'user': ['Hi']}
  ```

* $\color{#4A148C}\blacktriangleright$ **Iteration & Membership:** `k in d` checks **keys** in $O(1)$. Iterating a dict directly (`for x in d:`) yields **keys**, not values — use `.items()` for pairs, `.values()` for values.
  ```python
  scores = {"math": 90, "art": 75}
  "math" in scores                         # True (O(1) key check)
  for k, v in scores.items(): pass         # ('math', 90), ('art', 75)
  ```

* $\color{#1B5E20}\blacktriangleright$ **Sets (`set`) — Uniqueness, $O(1)$ Membership & Traps:** Unordered bag of unique, hashable items; `x in s` is $O(1)$ (vs $O(N)$ for lists). Cannot index (`s[0]` $\to$ `TypeError`). Dynamic types can be constrained via type hints (`set[str]`), runtime `isinstance`, or Pydantic.
  * $\color{#0288D1}\bullet$ **Empty Set Trap:** `{}` creates an empty **`dict`**, not a set. Always use `set()`.
  * $\color{#0288D1}\bullet$ **Bool/Int Collision Trap:** Because `bool` subclasses `int` (`True == 1`, `False == 0`, same hash), booleans collapse into ints in sets.
  ```python
  empty_s, empty_d = set(), {}             # set vs dict
  set("banana"), set({"a": 1, "b": 2})     # {'b', 'a', 'n'} (chars), {'a', 'b'} (dict keys)
  list(set([1, 2, 2, 3]))                  # [1, 2, 3] (fast deduplication)
  {1, True, 0, False}                      # {0, 1} (True/False collapsed into 1/0!)
  ```

* $\color{#0288D1}\blacktriangleright$ **Set Mutation (`add`, `update`, `discard`, `remove`, `pop`, `clear`):**
  * $\color{#0288D1}\bullet$ `.add(x)` adds **one** hashable item (lists fail; tuples store as 1 item). `.update(*iters)` unpacks iterables in-place (strings $\to$ chars; dicts $\to$ keys).
  * $\color{#0288D1}\bullet$ `.discard(x)` silently ignores missing items; `.remove(x)` raises `KeyError`. `.pop()` removes & returns an **arbitrary** item (no index arg; `KeyError` if empty). `.clear()` empties in place.
  ```python
  s = {1, 2}; s.add((3, 4)); s.update([2, 5], "ab")  # {1, 2, (3, 4), 5, 'a', 'b'}
  s.discard(99)                            # safe no-op; s.remove(99) -> KeyError
  item = s.pop(); s.clear()                # pops arbitrary item; empties to set()
  ```

* $\color{#00897B}\blacktriangleright$ **Set Algebra (Operators vs. Methods):** Sets do **not** support `+` (`TypeError`).
  * $\color{#0288D1}\bullet$ Union `|` (all unique), Intersection `&` (overlap/common only), Difference `-` (in A, not B), Symmetric Difference `^` (in either, **not both**). In-place: `|=`, `&=`, `-=`, `^=`.
  * $\color{#0288D1}\bullet$ **Operator vs. Method Rule:** Operators require **both** sides to be sets; methods (`.union()`, `.intersection()`, `.difference()`, `.symmetric_difference()`) accept **any iterable** (e.g. a `list`).
  ```python
  a, b = {"search", "calc"}, {"calc", "repl"}
  a | b, a & b, a - b, a ^ b               # union, {'calc'}, {'search'}, {'search', 'repl'}
  # a & ["calc"]                           # TypeError (operator needs set on both sides)
  a.intersection(["calc", "other"])        # {'calc'} (method accepts any iterable)
  ```

* $\color{#BF360C}\blacktriangleright$ **`frozenset` (Immutable & Hashable Set):** Sealed counterpart to `set` (`list:tuple :: set:frozenset`). Supports membership and set algebra, blocks mutation (`AttributeError`), and is **hashable** — usable as a dict key or nested inside a `set`.
  ```python
  perms = {frozenset(["read", "write"]): "Editor"}
  perms[frozenset(["write", "read"])]      # 'Editor' (order-independent hashable key)
  groups = {frozenset([1, 2]), frozenset([3, 4])}  # set of sets
  ```

* $\color{#4A148C}\blacktriangleright$ **Custom Objects in Dicts & Sets (Identity vs. Value Hashing):** By default, custom class instances hash by memory `id()` — two distinct instances with identical fields will **not** deduplicate in a set. Use `@dataclass(frozen=True)` (or define `__hash__` + `__eq__`) for value-based deduplication.
  ```python
  from dataclasses import dataclass
  class Doc:
      def __init__(self, x): self.x = x
  len({Doc(1), Doc(1)})                    # 2 (distinct memory ids)

  @dataclass(frozen=True)
  class FrozenDoc: x: int
  len({FrozenDoc(1), FrozenDoc(1)})        # 1 (deduplicated by value)
  ```

---

<a id="chapter-06"></a>

## 🔀 $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{06 — Control Flow}}$

* $\color{#0288D1}\blacktriangleright$ **`if / elif / else` & Conditions:** Indentation (4 spaces) defines blocks. Supports **chained comparisons** (`18 <= age < 65`) and requires tolerance checks (`math.isclose()`) for floats instead of `==`.
  ```python
  import math
  age, val = 25, 0.1 + 0.2
  if 18 <= age < 65 and math.isclose(val, 0.3):
      grade = "Pass"                     # executes cleanly
  ```

* $\color{#00897B}\blacktriangleright$ **Truth Value Testing Protocol & The 5 Truthy Traps:** `if obj:` invokes `bool(obj)` in strict order: `obj.__bool__()` $\to$ `len(obj) != 0` (`__len__`) $\to$ defaults to `True`. Follow PEP 8: `if not items:` (not `len(items) == 0`), `if is_active:` (not `== True`).
  * $\color{#0288D1}\bullet$ **Falsy:** `False`, `None`, `0`, `0.0`, `-0.0`, `0j`, `""`, `b""`, `bytearray()`, `[]`, `()`, `{}`, `set()`, `frozenset()`, `range(0)`.
  * $\color{#0288D1}\bullet$ **5 Truthy Traps:** (1) `"0"` and `"False"` are `True`; (2) whitespace `"   "` is `True` (use `.strip()`); (3) non-empty containers of falsy items (`[None]`, `[0]`, `{"k": False}`) are `True`; (4) negative numbers (`-1`) are `True`; (5) **Optional Parameter Bug:** `temp = temperature or 0.7` silently overwrites valid `0.0` — always check `is not None`.
  ```python
  bool("0"), bool("   ".strip()), bool([None]), bool(-1)  # True, False, True, True
  def sample(temp: float | None = None):
      return temp if temp is not None else 0.7            # sample(0.0) -> 0.0 (safe!)
  ```

* $\color{#BF360C}\blacktriangleright$ **Conditional Expression (Ternary):** `val = x if cond else y` evaluates directly to a value (usable inline and in f-strings; avoid nesting).
  ```python
  model = "gpt-4o" if use_pro else "gpt-4o-mini"
  f"Mode: {'Creative' if temp > 0.5 else 'Deterministic'}"
  ```

* $\color{#4A148C}\blacktriangleright$ **`while` Loops:** Repeat while condition is `True`; ensure state progresses toward exit to avoid infinite loops. Use `while True:` with `break` for intentional event/polling loops.
  ```python
  n = 3
  while n > 0: n -= 1                    # exits when n == 0
  ```

* $\color{#1B5E20}\blacktriangleright$ **`for` Loops, `range()` & Iteration Helpers:** Python's `for` calls `iter(seq)` then `next()` until `StopIteration`.
  * $\color{#0288D1}\bullet$ `range(start, stop, step)` is an $O(1)$ lazy sequence (`stop` excluded; negative step for countdown). Use `_` as a throwaway variable for fixed repeats.
  * $\color{#0288D1}\bullet$ Prefer `enumerate(seq, start=1)` ($O(1)$ index+item), `zip(a, b)` ($O(1)$ lockstep), `reversed(seq)` ($O(1)$ zero-copy reverse), and `sorted(seq)` ($O(N)$ new list).
  * $\color{#0288D1}\bullet$ **Safe `None` Guard:** `for x in items or []:` prevents `TypeError: 'NoneType' object is not iterable` by running 0 times if `items` is `None`.
  ```python
  list(range(3, 0, -1))                  # [3, 2, 1] (0 excluded)
  for _ in range(3): pass                # repeat 3 times without index variable
  for i, t in enumerate(["a", "b"], 1): pass  # (1, 'a'), (2, 'b')
  for x in (None or []): pass            # safe 0-iteration guard (no TypeError)
  ```

* $\color{#0288D1}\blacktriangleright$ **Loop `else` (`for ... else` & `while ... else`):** The `else` block executes **only if the loop completes naturally without hitting `break`**. Skipped if `break` fires (useful for search/retry exhaustion; note: uncommon in production and meaningless without a `break`).
  ```python
  for doc in ["d1", "d2"]:
      if doc == "d9": break
  else:
      status = "Not found"               # runs because break was never hit
  ```

* $\color{#00897B}\blacktriangleright$ **Loop Control (`break` vs. `continue` vs. `pass`):**
  * $\color{#0288D1}\bullet$ `break`: terminates the entire loop immediately.
  * $\color{#0288D1}\bullet$ `continue`: skips the rest of the *current* iteration, jumps to the next.
  * $\color{#0288D1}\bullet$ `pass`: syntactic no-op placeholder (required because empty indented blocks raise `IndentationError`); execution falls through to the next line.
  ```python
  # On [1, 2, 3] with condition n == 2:
  # pass     -> prints 1 2 3 (does nothing, next line still runs)
  # continue -> prints 1 3   (skips rest of iteration 2)
  # break    -> prints 1     (exits loop immediately)
  def todo_stub(): pass                  # valid empty block
  ```

* $\color{#BF360C}\blacktriangleright$ **`match / case` (Python 3.10+) & `Enum` Pairing:** Clean multi-way branching replacing long `if/elif` chains; `case _:` is the wildcard catch-all. Commonly paired with `Enum` (in `if` checks, compare Enum members with `is` / `is not` since they are singletons).
  ```python
  from enum import Enum, auto
  class State(Enum): IDLE = auto(); RUN = auto()
  state = State.RUN
  match state:
      case State.IDLE: action = "wait"
      case State.RUN:  action = "exec"
      case _:          action = "unknown"
  if state is State.RUN: pass            # singleton identity check
  ```

---

<a id="chapter-07"></a>

## ⚙️ $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{07 — Functions}}$

* $\color{#0288D1}\blacktriangleright$ **Definition, Returns & Guard Clauses:** `def name(param):` defines input slots (**parameters**); calls pass values (**arguments**). Comma-separated returns (`return a, b`) auto-pack into an immutable `tuple`. Omitting `return` (or bare `return`) implicitly returns `None`. Use early `return` guard clauses at the top to avoid deep nesting.
  ```python
  def metrics(tok: int, sec: float) -> tuple[float, float]:
      if sec <= 0: return 0.0, 0.0         # early-return guard clause
      return tok / sec, tok * 0.00002      # packs into tuple
  speed, cost = metrics(500, 2.5)          # caller unpacking -> 200.0, 0.01
  ```

* $\color{#00897B}\blacktriangleright$ **Positional vs. Keyword Arguments:** Positional args match left-to-right; keyword args (`k=v`) match by name in any order. Mixed calls must place all positional args **before** keyword args.
  ```python
  def conn(host, port, db): return f"{host}:{port}/{db}"
  conn("loc", db="vec", port=5432)         # valid mixed call
  # conn(host="loc", 5432, "vec")          # SyntaxError: positional follows keyword
  # conn("loc", 5432, "vec", host="x")     # TypeError: multiple values for 'host'
  ```

* $\color{#BF360C}\blacktriangleright$ **Default Parameters & Skipping Defaults:** Parameters with defaults **must come after** required parameters — **Why:** left-to-right positional matching would otherwise be ambiguous (`SyntaxError`). Use keyword args to skip intermediate defaults.
  ```python
  def gen(prompt, model="gpt-4o", temp=0.7, stream=False): ...
  gen("Hi", stream=True)                   # skips model & temp, overrides only stream
  # def bad(model="gpt-4o", prompt): ...   # SyntaxError: non-default follows default
  ```

* $\color{#4A148C}\blacktriangleright$ **The Mutable Default Trap & Sentinel `None` Pattern:** Never use mutable objects (`[]`, `{}`) as default values — **Why:** `def` runs **once** at import/load time, binding that single object to `func.__defaults__`; every call omitting the arg mutates the *same* shared object.
  ```python
  # ❌ def add(x, store=[]): store.append(x); return store  # add(1)->[1], add(2)->[1, 2]!
  def add(x, store: list | None = None) -> list:
      if store is None: store = []         # fresh list created per call
      store.append(x); return store
  ```

* $\color{#1B5E20}\blacktriangleright$ **3-Zone Parameters (`/` Positional-Only & `*` Keyword-Only):** Params before `/` must be positional (lets library authors rename safely); between `/` and `*` are standard; after `*` must be passed by keyword (prevents flag/hyperparameter swaps).
  ```python
  def embed(text: str, /, model: str = "e3", *, norm: bool = True): ...
  embed("hello", "e3-lg", norm=False)      # valid
  # embed(text="hello")                    # TypeError (violates positional-only '/')
  # embed("hello", "e3", True)             # TypeError (violates keyword-only '*')
  ```

* $\color{#0288D1}\blacktriangleright$ **`*args`, `**kwargs` & Strict Parameter Order:** `*args` packs excess positional args into an immutable **`tuple`** (`()` if empty); `**kwargs` packs excess keyword args into a **`dict`** (`{}` if empty).
  * $\color{#0288D1}\bullet$ **Strict Definition Order:** `pos_req` $\to$ `pos_default` $\to$ `*args` $\to$ `kw_only` $\to$ `**kwargs`.
  * $\color{#0288D1}\bullet$ **Rules:** `**kwargs` must be **last**; any param after `*args` is automatically keyword-only; max one `*args` and one `**kwargs`.
  ```python
  def pipe(stage, timeout=60, *steps, verbose=False, **meta): ...
  pipe("Ingest", 120, "clean", "tok", verbose=True, env="prod")
  # Universal wrapper / forwarding pattern:
  def wrap(fn, *args, **kwargs): return fn(*args, **kwargs)
  ```

* $\color{#00897B}\blacktriangleright$ **Call-Site Argument Unpacking (`*` / `**`):** Explodes an iterable into positional args (`*list`) and a dict into keyword args (`**dict`). Positional `*` unpacking must precede keyword `**` unpacking (`SyntaxError` otherwise).
  ```python
  def api(prompt, model, temp): return f"{model}@{temp}:{prompt}"
  api(*["Hi"], **{"model": "gpt-4o", "temp": 0.2})  # 'gpt-4o@0.2:Hi'
  ```

* $\color{#BF360C}\blacktriangleright$ **Type Annotations & Docstrings:** Syntax is `param: Type = default` (annotation **before** `=`) and `-> ReturnType` (`None`, `list[str]`, `str | None`).
  * $\color{#0288D1}\bullet$ **Runtime Rule:** Python does **not** enforce type hints at runtime (`add("a", "b")` still runs). They power IDEs, `mypy`, Pydantic, and LLM tool-calling JSON schema generation via `__annotations__` + docstrings.
  ```python
  def find_tool(name: str, limit: int = 5) -> str | None:
      """Look up a registered tool by name."""
      return {"search": "WebSearch"}.get(name)
  ```

* $\color{#4A148C}\blacktriangleright$ **Scoping (LEGB), `global`, `nonlocal` & `UnboundLocalError`:** Lookup order is **L**ocal $\to$ **E**nclosing $\to$ **G**lobal $\to$ **B**uilt-in $\to$ `NameError`.
  * $\color{#0288D1}\bullet$ **Why `UnboundLocalError` happens:** Python compiles the entire function body first; any assignment (`x += 1`) marks `x` as **local** for the whole function, crashing when reading `x` before local assignment.
  * $\color{#0288D1}\bullet$ `global x` binds to module scope (can also create a new global — anti-pattern due to hidden side effects/order dependency). `nonlocal x` binds to the nearest enclosing non-global function scope (closures).
  ```python
  count = 0
  def inc_global():
      global count; count += 1             # without 'global', count += 1 -> UnboundLocalError

  def make_counter():
      n = 0
      def inc():
          nonlocal n; n += 1; return n     # mutates enclosing 'n'
      return inc
  ```

* $\color{#1B5E20}\blacktriangleright$ **`lambda` (Anonymous Functions):** Single-expression inline function (`lambda args: expr`, implicitly returned). Use for disposable callbacks (`sorted`, `filter`); never assign to a variable (PEP 8: use `def`).
  ```python
  docs = [{"id": "a", "s": 0.7}, {"id": "b", "s": 0.9}]
  sorted(docs, key=lambda d: d["s"], reverse=True)  # [{'id': 'b', 's': 0.9}, ...]
  ```

---

<a id="chapter-08"></a>

## ⚡ $\Large\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{08 — Comprehensions and Generators}}$

* $\color{#0288D1}\blacktriangleright$ **List Comprehensions — Anatomy, Speed & Execution Order:** `[expr for x in seq if cond]` runs faster than `for` + `.append()` because CPython uses optimized `LIST_APPEND` bytecode. `expr` can call any method, built-in, or function.
  * $\color{#0288D1}\bullet$ **Execution Order:** (1) `for` pulls item $\to$ (2) `if` filters (if `False`, `expr` never runs) $\to$ (3) `expr` evaluates and appends.
  ```python
  scores = [45, 82, 91]
  passing = [s + 5 for s in scores if s >= 60]             # [87, 96] (45 dropped before s+5)
  clean = [p.strip().upper() for p in ["  hi ", " "] if p.strip()]  # ['HI']
  ```

* $\color{#00897B}\blacktriangleright$ **The Two Faces of `if` (Filter vs. Ternary Transform):**
  * $\color{#0288D1}\bullet$ **Trailing `if` (Filter):** Drops items (changes length). Adding `else` here raises `SyntaxError`.
  * $\color{#0288D1}\bullet$ **Leading `x if c else y` (Transform):** Preserves length; **must** include `else`. Both can be combined.
  ```python
  nums = [-2, 5, 0]
  [n for n in nums if n > 0]                               # [5] (filtered; length changed)
  [n if n > 0 else 0 for n in nums]                        # [0, 5, 0] (ReLU transform; same length)
  # [n if n > 0 for n in nums]                             # SyntaxError: expected 'else'
  [r.upper() if r != "guest" else "ANON" for r in ["admin", "", "guest"] if r]  # ['ADMIN', 'ANON']
  ```

* $\color{#BF360C}\blacktriangleright$ **Nested Comprehensions (Flattening):** Multiple `for` clauses execute **left-to-right** (outer loop first, inner loop second). Avoid >2 nested loops or side effects — use a plain `for` loop for readability.
  ```python
  matrix = [["a", "b"], ["c"]]
  flat = [x for row in matrix for x in row]                # ['a', 'b', 'c']
  ```

* $\color{#4A148C}\blacktriangleright$ **Dict & Set Comprehensions:** Same syntax with `{}` — eager ($O(N)$ RAM). Dicts are ideal for $O(1)$ lookup indexes; sets auto-deduplicate.
  ```python
  prices = {"apple": 3, "pear": 5}
  doubled = {k: v * 2 for k, v in prices.items()}          # {'apple': 6, 'pear': 10}
  lengths = {len(w) for w in ["hi", "hey", "yo"]}          # {2, 3}
  ```

* $\color{#1B5E20}\blacktriangleright$ **Generator Expressions (`(...)`) — Lazy $O(1)$ Memory:** Parentheses create a lazy generator that computes **nothing upfront**, yielding one item at a time via `next()` or `for` ($O(1)$ RAM vs $O(N)$ for `[...]`).
  * $\color{#0288D1}\bullet$ **Exhaustion Trap:** Generators are **single-use** — they don't store past values. Iterating a second time yields `[]`. They also don't support indexing (`gen[0]`) or `len()`.
  ```python
  gen = (n * n for n in range(1, 5))                       # nothing computed yet
  next(gen), next(gen)                                     # 1, 4
  list(gen), list(gen)                                     # [9, 16], [] (exhausted on 2nd pass!)
  total = sum(n * n for n in range(1_000_000_000))         # constant O(1) memory; [...] would OOM
  ```

* $\color{#0288D1}\blacktriangleright$ **Generator Functions (`yield`) & Iterators:** Using `yield` instead of `return` turns a function into a generator — it hands out a value and **pauses** its local state until the next `next()` call (which `for` invokes automatically until `StopIteration`). *(Reference: generators also support coroutine methods `.send()`, `.throw()`, `.close()`.)*
  ```python
  def count_up(limit):
      n = 1
      while n <= limit:
          yield n                                          # pauses here, resumes next call
          n += 1
  list(count_up(3))                                        # [1, 2, 3]
  ```

---

<a id="chapter-09"></a>

## 🎨 $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{09 — Decorators and Closures}}$

* $\color{#0288D1}\blacktriangleright$ **First-Class Functions:** Functions are ordinary objects — store them in variables, pass them as arguments, or return them.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** `yell = shout` stores the function object; `yell = shout()` *calls* it immediately and stores its return value.
  ```python
  def shout(t): return t.upper()
  yell = shout                             # reference, no ()
  def apply(fn, val): return fn(val)
  apply(yell, "hi")                        # 'HI'
  ```

* $\color{#00897B}\blacktriangleright$ **Closures:** An inner function that remembers variables from its enclosing outer function even after the outer function's stack frame exits (retained in heap cells via `fn.__closure__`).
  ```python
  def make_mult(factor):
      def mult(x): return x * factor       # closes over 'factor'
      return mult
  double, triple = make_mult(2), make_mult(3)
  double(10), triple(10)                   # 20, 30
  ```

* $\color{#BF360C}\blacktriangleright$ **Mutating Enclosing State (`nonlocal`):** Reading enclosing variables is automatic; **rebinding/mutating** them (`+=`) requires `nonlocal` — **Why:** without it, Python treats the assignment as a new local variable and raises `UnboundLocalError`.
  ```python
  def make_counter():
      calls = 0
      def inc():
          nonlocal calls; calls += 1; return calls
      return inc
  c = make_counter(); c(), c()             # 1, 2
  ```

* $\color{#4A148C}\blacktriangleright$ **Decorators (`@name`) & Execution Timing:** A decorator takes a function and returns a new wrapped function. `@logged` above `def add(...)` is exact syntax sugar for `add = logged(add)`.
  * $\color{#0288D1}\bullet$ **Timing Rule:** The outer decorator runs **once** (at definition time); the inner `wrapper` runs on **every call**. Put per-call logic inside `wrapper`.
  * $\color{#0288D1}\bullet$ **Signature Forwarding:** Always accept `*args, **kwargs` in `wrapper` and forward to `func(*args, **kwargs)` so the decorator works on any function.
  * $\color{#0288D1}\bullet$ **Metadata Preservation (`@functools.wraps`):** Mandatory — without it, `add.__name__` becomes `'wrapper'` and `__doc__` is lost (breaks FastAPI routes, debuggers, and LLM `@tool` schema extraction).
  ```python
  import functools
  def logged(func):
      @functools.wraps(func)               # preserves func.__name__ & func.__doc__
      def wrapper(*args, **kwargs):
          res = func(*args, **kwargs)      # runs on EVERY call
          return res
      return wrapper                       # runs ONCE at definition time

  @logged
  def add(a, b): return a + b
  add(2, 3), add.__name__                  # 5, 'add' (would be 'wrapper' without @wraps)
  ```

* $\color{#1B5E20}\blacktriangleright$ **Parametrized Decorators & Caching:**
  * $\color{#0288D1}\bullet$ **Configurable Decorators (`@retry(max_retries=3)`):** 3-layer factory (outer takes config $\to$ returns decorator $\to$ returns wrapper).
  * $\color{#0288D1}\bullet$ **Memoization:** `@functools.lru_cache(maxsize=128)` caches deterministic function outputs in memory. *(Reference: class-based decorators implement `__call__`.)*
  ```python
  def repeat(n: int):                      # 1. Config factory
      def decorator(func):                 # 2. Decorator
          @functools.wraps(func)
          def wrapper(*args, **kwargs):    # 3. Per-call wrapper
              return [func(*args, **kwargs) for _ in range(n)]
          return wrapper
      return decorator

  @repeat(3)
  def ping(): return "ok"
  ping()                                   # ['ok', 'ok', 'ok']
  ```

---

<a id="chapter-10"></a>

## 🛡️ $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{10 — Error Handling}}$

* $\color{#0288D1}\blacktriangleright$ **Exception Hierarchy & Bare `except:` Trap:** All exceptions inherit from `BaseException`. `SystemExit` and `KeyboardInterrupt` (`Ctrl+C`) sit directly under `BaseException`; application errors sit under `Exception` (`ValueError`, `TypeError`, `LookupError` $\to$ `KeyError`/`IndexError`, `OSError` $\to$ `FileNotFoundError`/`TimeoutError`).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Never write bare `except:` (or catch `BaseException`) — **Why:** it intercepts `Ctrl+C` and `sys.exit()`, making runaway scripts unkillable. Never swallow errors silently (`except Exception: pass`). Keep `try` blocks narrow so you know which line failed.
  ```python
  try:
      val = int("abc")
  except (ValueError, TypeError) as err:     # catch specific error(s) in a tuple
      print(f"Bad input: {err}")
  ```

* $\color{#00897B}\blacktriangleright$ **Complete 4-Part Structure (`try / except / else / finally`):**
  * $\color{#0288D1}\bullet$ `else` runs **only if `try` raised zero exceptions** — **Why:** keeps follow-up logic out of `try` so its bugs aren't accidentally caught by `except`.
  * $\color{#0288D1}\bullet$ `finally` **always runs** (success, caught error, uncaught error, and **immediately before `return`**) — mandatory for guaranteed cleanup.
  ```python
  def parse(raw: str) -> dict:
      try:
          data = json.loads(raw)
      except json.JSONDecodeError:
          return {}
      else:
          return data                        # runs only on zero exceptions
      finally:
          print("Audit logged")              # ALWAYS runs BEFORE return hands control back
  ```

* $\color{#BF360C}\blacktriangleright$ **Raising & Re-raising (`raise`):** Raise built-ins deliberately to enforce invariants. A bare `raise` inside `except` re-raises the active exception upward after logging/auditing.
  ```python
  def set_temp(t: float) -> float:
      if not (0.0 <= t <= 2.0):
          raise ValueError(f"Temp must be 0..2, got {t}")
      return t

  try: set_temp(3.0)
  except ValueError as err:
      print(f"[AUDIT] {err}")
      raise                                  # propagates original ValueError + traceback
  ```

* $\color{#4A148C}\blacktriangleright$ **Exception Chaining (`raise ... from err`):** Wraps low-level library errors in a high-level domain exception while preserving the original root cause in the traceback.
  ```python
  class ConfigError(Exception): pass
  try:
      json.loads("{bad")
  except json.JSONDecodeError as err:
      raise ConfigError("Invalid agent config") from err  # chains original traceback
  ```

* $\color{#1B5E20}\blacktriangleright$ **Custom Exceptions & Domain Hierarchies:** Subclass `Exception` (never `BaseException`). Call `super().__init__(message)` when adding custom metadata attributes. Define a base domain exception so callers can catch broadly (`AgentError`) or narrowly (`RateLimitError`).
  ```python
  class AgentError(Exception): pass
  class RateLimitError(AgentError):
      def __init__(self, msg: str, retry_after: int):
          super().__init__(msg)
          self.retry_after = retry_after

  try: raise RateLimitError("Quota hit", retry_after=30)
  except RateLimitError as e: print(f"{e} — wait {e.retry_after}s")
  except AgentError as e:     print(f"Generic agent fallback: {e}")
  ```

* $\color{#0288D1}\blacktriangleright$ **EAFP vs. LBYL (and `assert`):**
  * $\color{#0288D1}\bullet$ **EAFP** (*Easier to Ask Forgiveness than Permission*): attempt the op and catch failure — idiomatic in Python, faster when failures are rare, avoids TOCTOU race conditions (e.g., checking file existence before `open()`).
  * $\color{#0288D1}\bullet$ **LBYL** (*Look Before You Leap*): check preconditions with `if` — prefer only when failure is common (50%+).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Never use `assert` for business/validation logic — Python `-O` mode strips all `assert` statements.
  ```python
  # EAFP (idiomatic):                       # LBYL:
  try: val = cache["key"]                   # val = cache["key"] if "key" in cache else None
  except KeyError: val = None
  ```

---

<a id="chapter-11"></a>

## 📦 $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{11 — Modules, Packages and Files}}$

* $\color{#0288D1}\blacktriangleright$ **Module vs. Package vs. Library:**
  * $\color{#0288D1}\bullet$ **Module:** Single `.py` file (name = filename without `.py`).
  * $\color{#0288D1}\bullet$ **Package:** Folder of modules + `__init__.py` under one namespace.
  * $\color{#0288D1}\bullet$ **Library:** Umbrella distribution of packages/modules installed via `pip` into `site-packages`.

* $\color{#00897B}\blacktriangleright$ **Import Variations, Collisions & Shadowing:**
  * $\color{#0288D1}\bullet$ `import mod` (safest; preserves namespace), `from mod import fn` (concise), `as` (community aliases like `np`, or disambiguating collisions).
  * $\color{#0288D1}\bullet$ **Avoid `from mod import *`:** Pollutes namespace, causes silent overwrites, breaks linters/IDE tracing (only acceptable in root `__init__.py` gated by `__all__`).
  * $\color{#0288D1}\bullet$ **Local Shadowing Trap:** Never name a local variable or function after an imported symbol (`date = "2026-09-14"` overwrites `from datetime import date`).
  ```python
  import json, yaml                                      # keeps prefixes -> zero collision
  from json import loads as json_loads                   # alias to disambiguate
  from PIL import Image as PILImage
  ```

* $\color{#BF360C}\blacktriangleright$ **Module Search Path (`sys.path`) & Self-Shadowing Bug:** On `import foo`, Python checks: `sys.modules` cache $\to$ (1) Current script directory $\to$ (2) Standard library $\to$ (3) `.venv/site-packages` $\to$ `ModuleNotFoundError`.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Because current directory is searched **first**, naming a local file `random.py`, `json.py`, or `openai.py` blocks the real library (`AttributeError: partially initialized module`).

* $\color{#4A148C}\blacktriangleright$ **Packages & `__init__.py` Lifecycle:**
  * $\color{#0288D1}\bullet$ **Submodule Trap:** `import pkg` executes `pkg/__init__.py` only — it does **not** auto-load submodules (`pkg.planner` raises `AttributeError` unless re-exported in `__init__.py` like `requests` does, or explicitly imported via `import pkg.planner` / `from pkg import planner, memory`).
  * $\color{#0288D1}\bullet$ **Lifecycle:** `__init__.py` runs **once per process** on the first import of *any* part of the package (cached in `sys.modules`). Use it for `__version__`, startup checks (`sys.version_info`), `logging.NullHandler()`, public API re-exports, and `__all__`. **Never** run heavy I/O, DB connects, or model downloads inside `__init__.py`.
  ```python
  # my_pkg/__init__.py
  __version__ = "1.2.0"
  from .planner import AgentPlanner          # façade re-export -> enables my_pkg.AgentPlanner
  __all__ = ["__version__", "AgentPlanner"]
  ```

* $\color{#1B5E20}\blacktriangleright$ **Absolute vs. Relative Imports:** Inside a package, prefer absolute (`from my_pkg.memory import VectorMemory`) or use relative dots (`.` = same folder, `..` = parent).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Running a file with relative imports via `python my_pkg/planner.py` raises `ImportError: attempted relative import with no known parent package`. Always run as a module from project root: `python -m my_pkg.planner`.

* $\color{#0288D1}\blacktriangleright$ **Standard Library Essentials:** Use `pathlib.Path` (replaces legacy `os.path`), `os.environ.get()` for secrets, and UTC `datetime`. *(Avoid `sys.path.append` hacks and insecure `pickle` on untrusted data.)*
  ```python
  import os
  from pathlib import Path
  from datetime import datetime, timezone

  api_key = os.environ.get("OPENAI_API_KEY", "")
  p = Path(__file__).parent / "data" / "chunks.txt"  # '/' works on Windows & Linux
  p.stem, p.suffix, p.exists()                       # 'chunks', '.txt', bool
  now = datetime.now(timezone.utc).isoformat()
  ```

* $\color{#00897B}\blacktriangleright$ **File I/O & The `with` Context Manager Protocol:**
  * $\color{#0288D1}\bullet$ Modes: `'w'` (overwrite/create), `'a'` (append), `'r'` (read). Stream large files line-by-line (`for line in f:`) for $O(1)$ RAM.
  * $\color{#0288D1}\bullet$ **Encoding Trap:** Always pass `encoding="utf-8"` — **Why:** Windows defaults to `cp1252`, crashing with `UnicodeDecodeError` or corrupting emojis/Unicode.
  * $\color{#0288D1}\bullet$ **Under the Hood:** `with` calls `__enter__()` (binds return value to `as` var) and deterministically calls `__exit__(exc_type, exc_val, exc_tb)` (closes file even on crash/return; returning `False` propagates exceptions).
  * $\color{#0288D1}\bullet$ **Why Not Rely on GC (`__del__`)?** (1) Non-deterministic timing (tracebacks/cycles keep handles open), (2) OS descriptor exhaustion (`OSError: Too many open files`), (3) Data loss from unflushed write buffers on crash/SIGTERM.
  ```python
  with open("log.txt", "w", encoding="utf-8") as f:
      f.write("Step 1\n")

  with open("log.txt", "r", encoding="utf-8") as f:
      for i, line in enumerate(f, 1): print(i, line.strip())  # O(1) streaming read

  # Custom Context Manager:
  import time
  class Timer:
      def __enter__(self): self.t0 = time.perf_counter(); return self
      def __exit__(self, exc_type, exc_val, exc_tb):
          print(f"{time.perf_counter() - self.t0:.4f}s")
          return False                                        # do not suppress exceptions
  ```

* $\color{#BF360C}\blacktriangleright$ **JSON Serialization (`json`):** Mnemonic: **`s`** = **S**tring (`dumps`/`loads`); no **`s`** = **File** (`dump`/`load`).
  ```python
  import json
  s = json.dumps({"model": "gpt-4o"}, indent=2)               # Python obj -> JSON str
  obj = json.loads(s)                                         # JSON str   -> Python obj
  with open("state.json", "w", encoding="utf-8") as f: json.dump(obj, f, indent=2)
  with open("state.json", "r", encoding="utf-8") as f: loaded = json.load(f)
  ```

* $\color{#4A148C}\blacktriangleright$ **The `if __name__ == "__main__":` Execution Guard:** When a file is run directly (`python app.py`), Python sets `__name__ = "__main__"`. When imported, `__name__` is the module's name (`"app"` or `"pkg.app"`).
  * $\color{#0288D1}\bullet$ **Why:** `import` executes top-level code top-to-bottom — without the guard, importing a helper runs scripts/DB calls immediately. Also mandatory for `multiprocessing` (`spawn` mode on Windows/macOS) to prevent infinite fork-bombs.
  ```python
  def main(): print("Running CLI...")
  if __name__ == "__main__":
      main()                                                  # skipped when imported
  ```

---

<a id="chapter-12-1"></a>

## 🧱 $\Large\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{12.1 — Classes and Object Lifecycle}}$

* $\color{#0288D1}\blacktriangleright$ **Classes, Instances & `self`:** A `class` bundles state (attributes) and behavior (methods). Python automatically passes the current instance as the first argument to instance methods — `self` is **not** a reserved keyword, just a mandatory PEP 8 convention.
  ```python
  class Dog:
      def __init__(self, name: str):
          self.name = name                   # instance attribute (unique per object)
      def bark(self) -> str:
          return f"{self.name} says woof!"

  rex, fido = Dog("Rex"), Dog("Fido")        # two independent instances
  rex.bark()                                 # 'Rex says woof!'
  ```

* $\color{#00897B}\blacktriangleright$ **Two-Phase Creation (`__new__` vs. `__init__`):** Instantiating `Cls(*args)` executes two methods in sequence:
  1. **`__new__(cls, ...)` (Allocator):** Runs **1st**, receives the class `cls`, allocates raw heap memory via `super().__new__(cls)`, and **must return an instance**.
  2. **`__init__(self, ...)` (Initializer):** Runs **2nd** automatically, receives the new instance `self`, attaches data, and **must return `None`** (returning `self` raises `TypeError`). Omitting `__init__` falls back to `object`'s parameterless default.
  ```python
  class Lifecycle:
      def __new__(cls, name):
          print(f"[__new__] allocating {cls.__name__}")
          return super().__new__(cls)        # MUST return instance
      def __init__(self, name):
          print(f"[__init__] setting name={name!r}")
          self.name = name                   # MUST return None

  obj = Lifecycle("Rex")                     # prints [__new__] then [__init__]
  ```

* $\color{#BF360C}\blacktriangleright$ **`super().__new__(cls)` & The Single-Argument Trap:** Every Python 3 class implicitly inherits from `object`, so `super().__new__(cls)` delegates to C-level `object.__new__(cls)`.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** If your class defines `__init__`, passing extra args to `super().__new__(cls, arg)` raises `TypeError: object.__new__() takes exactly one argument`. Always pass **only `cls`**.

* $\color{#4A148C}\blacktriangleright$ **Signature Matching Rule:** Python forwards the exact same arguments to both `__new__` and `__init__`. Mismatched signatures crash with `TypeError` — either mirror the exact parameter list or absorb everything in `__new__` with `*args, **kwargs`.
  ```python
  class Safe:
      def __new__(cls, *args, **kwargs):     # absorbs any signature safely
          return super().__new__(cls)        # passes ONLY cls to object.__new__
      def __init__(self, a, b):
          self.a, self.b = a, b
  ```

* $\color{#1B5E20}\blacktriangleright$ **Pattern A — Singleton via `__new__` (and the Re-Init Gotcha):** Store the single instance in a class attribute (`_instance = None`).
  * $\color{#D32F2F}\blacktriangleright$ **Gotcha:** Python **always** calls `__init__` after `__new__`, even when `__new__` returns the cached instance. Without an `_initialized` guard flag, subsequent calls silently overwrite the singleton's state.
  ```python
  class DatabaseConnection:
      _instance = None
      def __new__(cls, *args, **kwargs):
          if cls._instance is None:
              cls._instance = super().__new__(cls)
          return cls._instance
      def __init__(self, db_url: str):
          if not hasattr(self, "_initialized"):  # mandatory guard against overwrite!
              self.db_url = db_url
              self._initialized = True

  c1 = DatabaseConnection("postgres://prod")
  c2 = DatabaseConnection("postgres://other")
  c1 is c2, c2.db_url                        # True, 'postgres://prod' (protected)
  ```

* $\color{#0288D1}\blacktriangleright$ **Pattern B — Polymorphic Factory via `__new__` (Language Spec 3.3.1):** A base class `__new__` can inspect arguments and allocate a subclass transparently. Guard with `if cls is Base:` so direct subclass calls allocate normally.
  * $\color{#0288D1}\bullet$ **Why subclass `__init__` runs automatically:** After `__new__` returns, Python checks `isinstance(instance, Base)`. Because `Motorbike` inherits `Vehicle` (`True`), Python auto-calls `Motorbike.__init__`. If the returned object did *not* inherit from `Vehicle`, `__init__` would be skipped.
  ```python
  class Vehicle:
      def __new__(cls, wheels: int, brand: str):
          if cls is Vehicle:
              if wheels == 2: return super().__new__(Motorbike)
              if wheels == 4: return super().__new__(Car)
              raise ValueError(f"Unsupported wheels: {wheels}")
          return super().__new__(cls)

  class Motorbike(Vehicle):
      def __init__(self, wheels: int, brand: str): self.wheels, self.brand = wheels, brand
  class Car(Vehicle):
      def __init__(self, wheels: int, brand: str): self.wheels, self.brand = wheels, brand

  v = Vehicle(2, "Ducati")                   # type(v).__name__ -> 'Motorbike', v.brand -> 'Ducati'
  ```

* $\color{#00897B}\blacktriangleright$ **What Belongs in `__init__` (Architect's Rule):** Keep `__init__` lightweight and deterministic (validate args, store config, cheap derived fields). **Avoid** heavy I/O, network/DB sockets, or model downloads inside `__init__` — **Why:** breaks unit testing and fails construction on transient network errors. Decouple into explicit `.connect()` methods or `@classmethod` factories (`.from_pretrained()`).
  ```python
  class EmbeddingService:
      def __init__(self, model: str, api_key: str):
          if not api_key: raise ValueError("API key required")
          self.model, self.api_key, self._connected = model, api_key, False
      def connect(self): self._connected = True
      @classmethod
      def from_pretrained(cls, model: str, api_key: str):
          svc = cls(model, api_key); svc.connect(); return svc
  ```

---

<a id="chapter-12-2"></a>

## 🧬 $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{12.2 — Attributes and Inheritance}}$

* $\color{#0288D1}\blacktriangleright$ **Class vs. Instance Attributes:**
  * $\color{#0288D1}\bullet$ **Class attribute:** Defined on the class body outside `__init__`; shared by all instances (accessed via `Dog.species` or `rex.species`, which falls back to the class). Use only for immutable constants, config defaults, or intentional class counters.
  * $\color{#0288D1}\bullet$ **Instance attribute:** Defined on `self` inside `__init__`; unique to that object.
  ```python
  class Dog:
      species = "Canis familiaris"       # class attr (shared immutable constant)
      def __init__(self, name: str):
          self.name = name               # instance attr (unique per object)

  rex, fido = Dog("Rex"), Dog("Fido")
  Dog.species, rex.species, rex.name, fido.name  # 'Canis...', 'Canis...', 'Rex', 'Fido'
  ```

* $\color{#00897B}\blacktriangleright$ **The Mutable Class Attribute Trap:** Placing a mutable container (`[]`, `{}`) on the class body binds *all* instances to the **exact same object in memory** — mutating via one instance silently corrupts every other instance. Always initialize per-instance containers inside `__init__`.
  ```python
  class BadDog:
      tricks = []                        # ❌ ONE shared list in RAM for all instances!
  a, b = BadDog(), BadDog()
  a.tricks.append("sit")
  b.tricks, a.tricks is b.tricks         # ['sit'], True (polluted!)

  class GoodDog:
      def __init__(self): self.tricks = []  # fresh independent list per instance
  c, d = GoodDog(), GoodDog()
  c.tricks.append("sit")
  d.tricks, c.tricks is d.tricks         # [], False (isolated)
  ```

* $\color{#BF360C}\blacktriangleright$ **Inheritance & Polymorphism:** `class Child(Parent):` inherits all parent attributes and methods. **Polymorphism** means calling the same method across different subclasses triggers each type's own implementation without `if isinstance(...)` checks.
  ```python
  class Animal:
      def __init__(self, name): self.name = name
      def speak(self): return "..."

  class Cat(Animal):
      def speak(self): return f"{self.name} says meow"   # pure override (replaces parent)

  class Dog(Animal):
      def speak(self): return f"{self.name} says woof"

  [a.speak() for a in [Cat("Min"), Dog("Rex")]]          # ['Min says meow', 'Rex says woof']
  ```

* $\color{#4A148C}\blacktriangleright$ **Why `super().__init__()` is Mandatory in Subclasses:** Defining `__init__` in a subclass **completely replaces** the parent's `__init__` — it does *not* auto-run. Omitting `super().__init__(...)` leaves parent attributes uninitialized (`AttributeError`).
  ```python
  class Dog(Animal):
      def __init__(self, name, breed):
          super().__init__(name)         # runs Animal.__init__ to set self.name
          self.breed = breed             # without super(), self.name -> AttributeError

  d = Dog("Rex", "Lab")
  d.name, d.breed                        # 'Rex', 'Lab'
  ```

* $\color{#1B5E20}\blacktriangleright$ **Override Strategies — Pure (Replace) vs. Augmented (Extend):**
  * $\color{#0288D1}\bullet$ **Pure override:** Don't call `super()` — discards parent logic entirely (e.g., `Cat.speak()` above).
  * $\color{#0288D1}\bullet$ **Augmented override:** Call `super().method(...)` inside any overridden method to preserve parent behavior while wrapping it with pre-checks and post-enrichment.
  ```python
  class BaseAgent:
      def execute(self, task: str) -> dict:
          return {"status": "success", "task": task}

  class GuardrailedAgent(BaseAgent):
      def execute(self, task: str) -> dict:
          if "malicious" in task: raise ValueError("Blocked!")  # 1. pre-check
          result = super().execute(task)                        # 2. parent logic
          result["safety_checked"] = True                       # 3. post-enrichment
          return result

  GuardrailedAgent().execute("Analyze")  # {'status': 'success', 'task': 'Analyze', 'safety_checked': True}
  ```

* $\color{#0288D1}\blacktriangleright$ **`super()` Syntax, `@typing.override`, Mixins & MRO:**
  * $\color{#0288D1}\bullet$ Always use Python 3's zero-arg `super().method(...)` (auto-resolves class/instance; legacy Python 2 used `super(CurrentClass, self).method(...)`).
  * $\color{#0288D1}\bullet$ Python needs no runtime `override` keyword; Python 3.12+ adds `@typing.override` as a static type-checker hint to catch misspelled method names (e.g., `speek` vs `speak`).
  * $\color{#0288D1}\bullet$ Prefer single inheritance + small orthogonal mixins (`class LoggingMixin:`); inspect multiple-inheritance lookup order via `ClassName.__mro__` (C3 linearization) if needed.
  ```python
  from typing import override
  class SafeCat(Animal):
      @override                          # static checker flags if 'speak' doesn't exist on Animal
      def speak(self): return "meow"
  ```

---

<a id="chapter-12-3"></a>

## 🔮 $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{12.3 — Dunder Methods}}$

* $\color{#0288D1}\blacktriangleright$ **Dunder Hooks:** Special `__double_underscores__` methods that Python invokes automatically when you use built-in syntax (`print`, `==`, `+`, `len()`, `with`, `obj()`).

* $\color{#00897B}\blacktriangleright$ **`__str__` vs. `__repr__` & The Fallback Chain:**
  * $\color{#0288D1}\bullet$ **`__str__` (End-user):** Human-friendly output; triggered by `print(obj)`, `str(obj)`, `f"{obj}"`, `format(obj)`.
  * $\color{#0288D1}\bullet$ **`__repr__` (Developer):** Unambiguous, recreatable string (use `!r`); triggered by REPL/debugger, `repr(obj)`, `f"{obj!r}"`, and **always for items inside containers** (`print([obj])`).
  * $\color{#2E7D32}\bullet$ **Golden Rule:** Always implement `__repr__` first. **Why:** `print(obj)` falls back `__str__` $\to$ `__repr__` $\to$ `<Obj at 0x...>`, whereas containers (`print([obj])`) call `__repr__` directly and ignore `__str__`.
  ```python
  class ModelConfig:
      def __init__(self, name, temp): self.name, self.temp = name, temp
      def __repr__(self): return f"ModelConfig(name={self.name!r}, temp={self.temp})"
      def __str__(self):  return f"Model '{self.name}' (Temp: {self.temp})"

  cfg = ModelConfig("gpt-4o", 0.7)
  str(cfg)     # "Model 'gpt-4o' (Temp: 0.7)"                  (__str__)
  repr(cfg)    # "ModelConfig(name='gpt-4o', temp=0.7)"        (__repr__)
  print([cfg]) # [ModelConfig(name='gpt-4o', temp=0.7)]        (containers ALWAYS use __repr__!)
  ```

* $\color{#BF360C}\blacktriangleright$ **`self.__dict__` Under the Hood:** Standard Python instances store all their instance attributes in a hidden dictionary `self.__dict__` (`self.name = "Ada"` literally executes `self.__dict__["name"] = "Ada"`).
  ```python
  cfg.__dict__                           # {'name': 'gpt-4o', 'temp': 0.7}
  ```

* $\color{#4A148C}\blacktriangleright$ **Value Equality (`__eq__`) & `NotImplemented`:** Without `__eq__`, `==` defaults to memory identity (`is`), so two distinct objects with identical fields evaluate to `False`. Compare either selectively via tuple or globally via `self.__dict__ == other.__dict__`.
  * $\color{#0288D1}\bullet$ **Why return `NotImplemented` (not `False`) on type mismatch:** Tells Python *"ask the other operand's `__eq__`"* before defaulting to `False`, enabling symmetric comparisons (`1 == MyObj`).
  ```python
  class User:
      def __init__(self, name, role): self.name, self.role = name, role
      def __eq__(self, other):
          if not isinstance(other, User): return NotImplemented
          return (self.name, self.role) == (other.name, other.role)  # or self.__dict__ == other.__dict__

  User("Ada", "Admin") == User("Ada", "Admin")  # True
  User("Ada", "Admin") == "Ada"                 # False (NotImplemented -> fallback -> False)
  ```

* $\color{#1B5E20}\blacktriangleright$ **The Nested Equality Trap:** When an object holds nested custom objects (`Customer.address` $\to$ `Address`), `self.__dict__ == other.__dict__` delegates `==` recursively.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** If the inner class (`Address`) does **not** define `__eq__`, Python falls back to identity (`addr1 is addr2` $\to$ `False`) even when field values match! Every nested custom class must define `__eq__` (or use `@dataclass`).
  ```python
  class Address:
      def __init__(self, city): self.city = city
      def __eq__(self, other):
          return self.__dict__ == other.__dict__ if isinstance(other, Address) else NotImplemented

  class Customer:
      def __init__(self, name, addr): self.name, self.addr = name, addr
      def __eq__(self, other):
          return self.__dict__ == other.__dict__ if isinstance(other, Customer) else NotImplemented

  Customer("Ada", Address("NYC")) == Customer("Ada", Address("NYC"))  # True (recursive)
  ```

* $\color{#0288D1}\blacktriangleright$ **Operator & Protocol Dunders (`__add__`, `__call__`, `__len__`, etc.):**
  * $\color{#00C853}\bullet$ **Core AI Dunders:** `__call__(self, *args)` makes instances callable like functions (`model(x)` in PyTorch / LangChain `Runnable`); `__enter__`/`__exit__` power `with obj:`.
  * $\color{#0288D1}\bullet$ **Container & Arithmetic:** `__len__` (`len(a)`), `__getitem__`/`__iter__`, `__add__` (`a + b` — should return a **new** instance and raise `TypeError` on invalid types), `__sub__` (`a - b`). *(Reference-only: `__hash__`, `__lt__`, `__gt__`, `__mul__`, `__matmul__`, `__getattr__` vs `__getattribute__`.)*
  ```python
  class Money:
      def __init__(self, amt): self.amt = amt
      def __add__(self, other):
          if not isinstance(other, Money): raise TypeError("Need Money")
          return Money(self.amt + other.amt)        # returns a NEW instance
      def __call__(self, factor): return Money(self.amt * factor)

  (Money(10) + Money(25)).amt                       # 35 (__add__)
  Money(10)(3).amt                                  # 30 (__call__)
  ```

---

<a id="chapter-12-4"></a>

## 🔒 $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{12.4 — Access Control and Properties}}$

* $\color{#0288D1}\blacktriangleright$ **Access Control Levels (Attributes & Methods):** Python has no `public`/`protected`/`private` keywords — it relies on underscore conventions and name mangling:
  * $\color{#0288D1}\bullet$ **Public (`name`):** Open API; accessible everywhere.
  * $\color{#0288D1}\bullet$ **Protected (`_name`):** Single underscore — internal by convention ("consenting adults"; Python does *not* block access); intended for use/overriding by subclasses.
  * $\color{#0288D1}\bullet$ **Private (`__name`):** Double underscore — triggers **name mangling** to `_ClassName__name`, blocking direct access from outside and from subclasses (`AttributeError`).
  ```python
  class BankVault:
      def __init__(self, pin):
          self.location = "NY"               # public
          self._level = 3                    # protected (convention only)
          self.__pin = pin                   # private -> stored as '_BankVault__pin'
      def __verify(self, p): return p == self.__pin
      def unlock(self, p):   return self.__verify(p)

  v = BankVault("9876")
  v.location, v._level, v.unlock("9876")     # 'NY', 3, True
  # v.__pin / v.__verify("9876")             # AttributeError (name-mangled!)
  ```

* $\color{#00897B}\blacktriangleright$ **Name Mangling Internals, Subclass Visibility & Bypass:**
  * $\color{#0288D1}\bullet$ **Why it exists:** Prevents a subclass from accidentally overriding or colliding with a parent's internal attribute/method (e.g., parent's `unlock()` stays bound to `_BankVault__verify`).
  * $\color{#0288D1}\bullet$ **Subclass rule:** A child class inherits `_protected` directly, but accessing `self.__private` in `Child` looks up `_Child__private` (`AttributeError`). Explicit bypass syntax is `obj._ClassName__member` (or `self._Parent__member`).
  * $\color{#0288D1}\bullet$ **Architect's choice:** Subclass-extensible internal $\to$ `_member`; lock against subclass collision $\to$ `__member`.
  ```python
  class Parent:
      def __init__(self): self._prot = "ok"; self.__priv = "locked"

  class Child(Parent):
      def inspect(self):
          # self.__priv                      # AttributeError: '_Child__priv' not found
          return self._prot, self._Parent__priv  # explicit bypass

  Child().inspect()                          # ('ok', 'locked')
  ```

* $\color{#BF360C}\blacktriangleright$ **`@property` (Getter, Setter, Deleter):** Exposes methods as clean attribute syntax (`acc.balance`, `acc.balance = 250`, `del acc.balance`) instead of Java-style `get_balance()`/`set_balance()`, using a private backing variable (`self._balance`).
  * $\color{#0288D1}\bullet$ **Infinite Recursion Trap:** Inside `@balance.setter`, you **must** write `self._balance = val`. Writing `self.balance = val` recursively calls the setter itself $\to$ `RecursionError: maximum recursion depth exceeded`.
  ```python
  class BankAccount:
      def __init__(self, bal=0):
          self._balance = bal                # private backing variable

      @property
      def balance(self):                     # GETTER: acc.balance
          return self._balance

      @balance.setter
      def balance(self, val):                # SETTER: acc.balance = val
          if val < 0: raise ValueError("Negative balance!")
          self._balance = val                # MUST assign to _balance (not self.balance!)

      @balance.deleter
      def balance(self):                     # DELETER: del acc.balance
          del self._balance

  acc = BankAccount(100)
  acc.balance = 250; acc.balance             # 250 (acc.balance = -5 -> ValueError)
  del acc.balance                            # invokes deleter
  ```

* $\color{#4A148C}\blacktriangleright$ **Read-Only Computed Properties:** Define `@property` **without** a `.setter` to compute values on the fly and block assignment (`AttributeError`).
  ```python
  class Circle:
      def __init__(self, r): self.r = r
      @property
      def area(self): return 3.14159 * self.r ** 2

  c = Circle(2); c.area                      # 12.56636
  # c.area = 50                              # AttributeError: property 'area' has no setter
  ```

---

<a id="chapter-12-5"></a>

## 🏷️ $\Large\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{12.5 — Method Types: Instance, classmethod, staticmethod}}$

* $\color{#0288D1}\blacktriangleright$ **Constructor Overloading (The Python Way):** Python does **not** support multiple `__init__` definitions — the second silently overwrites the first.
  * $\color{#2E7D32}\bullet$ **Fix A (Optional params):** Use default arguments in a single `__init__` (with `None` sentinel for mutables).
  * $\color{#2E7D32}\bullet$ **Fix B (Different input formats):** Use `@classmethod` **alternative constructors** (`from_string`, `from_dict`, `from_env`, `from_pretrained`).
  * $\color{#0288D1}\bullet$ **Why `cls(...)` instead of `User(...)`:** If a subclass `AdminUser(User)` inherits `from_string`, `cls(...)` instantiates an `AdminUser`, not a base `User`.
  ```python
  class User:
      def __init__(self, name: str, age: int = 0):
          self.name, self.age = name, age

      @classmethod
      def from_string(cls, text: str):
          name, age = text.split(",")
          return cls(name.strip(), int(age.strip()))  # cls() preserves subclass type!

  class AdminUser(User): pass
  u = AdminUser.from_string("Ada, 36")
  type(u).__name__, u.name, u.age                     # 'AdminUser', 'Ada', 36
  ```

* $\color{#00897B}\blacktriangleright$ **The Three Method Types:**
  * $\color{#0288D1}\bullet$ **Instance Method (`def f(self, ...)`):** Receives `self`; reads/mutates instance state; must be called on an instance (`obj.f()`).
  * $\color{#0288D1}\bullet$ **`@classmethod` (`def f(cls, ...)`):** Receives `cls` (the class); callable without an instance (`Cls.f()`); used for alternative constructors and modifying class-level state.
  * $\color{#0288D1}\bullet$ **`@staticmethod` (`def f(...)`):** Receives **neither `self` nor `cls`**; pure utility function namespaced inside the class; callable on class or instance.
  ```python
  class TextProcessor:
      default_enc = "utf-8"                           # class attribute
      def __init__(self, enc=None): self.enc = enc or self.default_enc

      def process(self, text):                        # instance method (uses self)
          return self.clean(text).encode(self.enc)

      @classmethod
      def from_ascii(cls): return cls(enc="ascii")    # classmethod (uses cls)

      @classmethod
      def set_default(cls, enc): cls.default_enc = enc

      @staticmethod
      def clean(text): return " ".join(text.strip().split())  # staticmethod (pure helper)

  TextProcessor.clean("  hi   ai ")                   # 'hi ai' (no instance needed)
  TextProcessor.from_ascii().enc                      # 'ascii'
  TextProcessor().process(" AI ")                     # b'AI'
  ```

* $\color{#BF360C}\blacktriangleright$ **Subclass Polymorphism (`@classmethod` vs. `@staticmethod`):** `@classmethod` accesses class variables via `cls.var`, which dynamically resolves to the calling subclass. A `@staticmethod` must hardcode `Base.var`, breaking subclass overrides.
  ```python
  class Base:
      enc = "utf-8"
      @classmethod
      def get_cls(cls): return cls.enc                # resolves to calling subclass
      @staticmethod
      def get_static(): return Base.enc               # hardcoded -> ignores subclass!

  class Child(Base): enc = "utf-16"
  Child.get_cls(), Child.get_static()                 # 'utf-16', 'utf-8'
  ```

* $\color{#4A148C}\blacktriangleright$ **Memory, GC & Design Nuances:**
  * $\color{#0288D1}\bullet$ **Runtime internals:** Both are bound once at **module import time** (independent of instance count) and hold **no reference to `self`**, so they never prevent instance garbage collection or cause reference cycles. `@staticmethod` returns the raw function object (no bound-method wrapper); `@classmethod` returns a lightweight bound method tied to `cls`.
  * $\color{#0288D1}\bullet$ **`@staticmethod` vs. Module-Level Function:** Keep as `@staticmethod` when the helper is conceptually tied to the class domain (`TextProcessor.clean(...)`); move to a module-level `def` when it is generic and shared across unrelated classes.

---

<a id="chapter-12-6"></a>

## 💎 $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{12.6 — Advanced Types: Dataclasses, Enums, ABCs and Protocols}}$

* $\color{#0288D1}\blacktriangleright$ **`@dataclass`:** Auto-generates `__init__`, `__repr__`, and value-based `__eq__` from field annotations, removing boilerplate for data-carrier classes. Does **not** validate types at runtime (use Pydantic `BaseModel` for runtime validation; `NamedTuple` or `__slots__` for specialized lightweight containers).
  ```python
  from dataclasses import dataclass

  @dataclass
  class Point:
      x: int
      y: int

  p = Point(1, 2)
  repr(p), p == Point(1, 2)                # 'Point(x=1, y=2)', True
  ```

* $\color{#00897B}\blacktriangleright$ **Enumerations (`Enum`, `IntEnum`, `StrEnum`, `auto`):** Immutable, singleton named constants that eliminate typo-prone raw strings/ints.
  * $\color{#D32F2F}\blacktriangleright$ **Variants:** `Enum` (strict; **Trap:** `Status.READY == 1` is `False` — must compare `.value`), `IntEnum` (subclasses `int`; supports `== 3` and `<`/`>` ordering), `StrEnum` (Python 3.11+; subclasses `str`; supports `== "gpt-4o"`, ideal for JSON/APIs), `auto()` (assigns sequential ints `1, 2, ...`).
  * $\color{#0288D1}\bullet$ **Access, Lookup & Comparison:** Use `.name` / `.value`, `Role("admin")` (lookup by value; `ValueError` if invalid), `Role["ADMIN"]` (lookup by name), and `for m in Role:`. Prefer identity `is` / `is not` (fastest singleton check) or `match/case`.
  ```python
  from enum import Enum, IntEnum, StrEnum, auto

  class State(Enum):    IDLE = auto(); RUN = auto()       # 1, 2 (State.IDLE == 1 -> False!)
  class Priority(IntEnum): LOW = 1; HIGH = 3              # Priority.HIGH == 3 -> True; HIGH > LOW -> True
  class Tier(StrEnum):  PRO = "gpt-4o"; MINI = "gpt-4o-mini"

  t = Tier("gpt-4o")                                      # lookup by value (Tier["PRO"] by name)
  t is Tier.PRO, t == "gpt-4o", t.name, t.value           # True, True, 'PRO', 'gpt-4o'
  ```

* $\color{#BF360C}\blacktriangleright$ **Abstract Base Classes (`ABC` & `@abstractmethod`):** Nominal (inheritance-based) contract enforced at **runtime**. Instantiating the `ABC` directly or any subclass missing *any* `@abstractmethod` raises `TypeError`. Can include concrete helpers, `__init__`, and even baseline code inside an `@abstractmethod` (subclasses must still override, but can call `super().run()`). Use `...` (modern) or `pass` as empty body.
  * $\color{#0288D1}\bullet$ **Decorator Stacking Trap:** `@abstractmethod` **must** be the **innermost (bottom)** decorator under `@property` or `@classmethod` — **Why:** Python evaluates decorators bottom-to-top, so `@property`/`@classmethod` must wrap a callable already marked abstract.
  ```python
  from abc import ABC, abstractmethod

  class BaseLLM(ABC):
      @property
      @abstractmethod                      # MUST be innermost (bottom)!
      def dim(self) -> int: ...

      @abstractmethod
      def generate(self, prompt: str) -> str:
          print("[BASE LOG]")              # optional shared baseline via super()

  class OpenAI(BaseLLM):
      @property
      def dim(self) -> int: return 1536
      def generate(self, prompt: str) -> str:
          super().generate(prompt)
          return f"Response: {prompt}"

  # BaseLLM()                              # TypeError: Can't instantiate abstract class
  OpenAI().generate("Hi")                  # prints '[BASE LOG]', returns 'Response: Hi'
  ```

* $\color{#4A148C}\blacktriangleright$ **Protocols (`typing.Protocol` & `@runtime_checkable`):** Structural subtyping ("static duck typing") — any class exposing the required methods, typed attributes, or `@property` satisfies the contract with **zero inheritance / zero coupling** (works with third-party classes untouched). Checked statically by `mypy`/`pyright`/IDEs; uses `...` (Ellipsis) for method bodies.
  * $\color{#0288D1}\bullet$ **`@runtime_checkable` Gotcha:** Enables `isinstance(obj, Proto)` at runtime, **but only checks attribute name existence — not callability or parameter signatures** (`embed = "string"` still passes `isinstance`!).
  ```python
  from typing import Protocol, runtime_checkable

  @runtime_checkable
  class Embedder(Protocol):
      def embed(self, text: str) -> list[float]: ...

  class ThirdPartyModel:                   # NO inheritance from Embedder!
      def embed(self, text: str) -> list[float]: return [0.1, 0.9]

  class Broken: embed = "not a method"
  isinstance(ThirdPartyModel(), Embedder)  # True (structural match)
  isinstance(Broken(), Embedder)           # True! (Gotcha: only checks attribute name exists)
  ```

* $\color{#1B5E20}\blacktriangleright$ **`ABC` vs. `Protocol` Decision Rule:** Use **`ABC`** for *internal frameworks* you control that share base state/helpers (`__init__`, `super()`) or need immediate runtime instantiation checks. Use **`Protocol`** for *function parameters / public APIs* so any third-party or mock object with the right shape qualifies without inheritance or adapters.

---

<a id="chapter-13"></a>

## 🧰 $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{13 — Built-in Functions in Depth}}$

* $\color{#0288D1}\blacktriangleright$ **`isinstance(obj, classinfo)` vs. `type(obj) is Class`:** `isinstance` walks the entire inheritance tree (polymorphic) and accepts tuples `(int, float)`, unions `int | float` (3.10+), and `@runtime_checkable` Protocols. `type(obj) is ExactClass` ignores ancestors.
  * $\color{#0288D1}\bullet$ **`bool` is an `int` Trap:** Because `bool` subclasses `int`, `isinstance(True, int)` is `True`! For strict int validation (e.g., JSON retry counts), guard with `not isinstance(v, bool)`.
  ```python
  isinstance(True, int)                                    # True! (bool subclasses int)
  isinstance(True, int) and not isinstance(True, bool)     # False (safe strict int check)
  isinstance(3.14, int | float)                            # True (3.10+ union syntax)
  ```

* $\color{#00897B}\blacktriangleright$ **`callable(obj)`:** Returns `True` if `obj()` can be invoked — functions, built-ins, lambdas, **classes themselves** (calling invokes `__init__`), and instances defining `__call__`. Returns `False` for `str`, `int`, `dict`, `None`.
  * $\color{#0288D1}\bullet$ **Edge Case:** To verify an already-instantiated callable (not a class blueprint), check `callable(obj) and not isinstance(obj, type)`. Use `inspect.signature(obj)` to inspect parameter signatures.
  ```python
  class Tool:
      def __call__(self, q): return f"Search: {q}"
  callable(Tool), callable(Tool()), callable("v1.0")       # True, True, False
  ```

* $\color{#BF360C}\blacktriangleright$ **`globals()` and `locals()`:** Return dictionaries of the current module-level and function-level namespaces. At script root, `globals() is locals()` is `True`.
  * $\color{#0288D1}\bullet$ **Read-Only `locals()` Trap:** Mutating `globals()["x"] = 1` updates the live module variable (prod anti-pattern; use explicit config/classes). Inside a function, `locals()` is a **read-only snapshot** — **Why:** CPython compiles locals into fast C-array slots (`FAST_LOCALS`), so `locals()["x"] = 99` is silently discarded.
  ```python
  def demo():
      x = 10; locals()["x"] = 99
      return x                                             # 10 (locals() write ignored!)
  demo()
  ```

* $\color{#4A148C}\blacktriangleright$ **`range(start, stop, step)`:** Lazy, immutable, **reusable** sequence storing only `(start, stop, step)` in ~48 bytes ($O(1)$ RAM regardless of size); supports indexing, slicing, and $O(1)$ `x in r`. `stop` is excluded.
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** With a negative `step`, `start` must be `> stop`, else it yields empty `[]`. Wrapping in `list()` materializes all items into RAM. For reverse iteration over collections, prefer `reversed(seq)`.
  ```python
  list(range(5, 0, -2)), list(range(1, 5, -1))             # [5, 3, 1], [] (directional mismatch)
  # Batch striding: for i in range(0, len(tokens), 32): batch = tokens[i : i + 32]
  ```

* $\color{#1B5E20}\blacktriangleright$ **`enumerate(iterable, start=0)`:** Lazy, single-use iterator yielding `(index, item)` pairs — replaces manual counters and `range(len(seq))`. Use `start=1` for human rankings/RAG citations. Exhausts after one pass (wrap in `list()` to reuse).
  ```python
  list(enumerate(["DocA", "DocB"], start=1))               # [(1, 'DocA'), (2, 'DocB')]
  ```

* $\color{#0288D1}\blacktriangleright$ **`zip(*iterables, strict=False)`:** Lazy iterator pairing $N$ iterables into $N$-item tuples in lockstep. Unzip with `zip(*pairs)`.
  * $\color{#0288D1}\bullet$ **Silent Truncation Trap:** Default `zip()` silently drops trailing items when lengths differ! Always pass `strict=True` (3.10+) in data/eval pipelines to raise `ValueError` on mismatch. Use `itertools.zip_longest(..., fillvalue=...)` if you intentionally want padding.
  * $\color{#0288D1}\bullet$ **`dict(zip(...))` Trap:** Only works for **2** iterables; 3+ raises `ValueError`.
  ```python
  prompts, ans = ["Q1", "Q2", "Q3"], ["A1", "A2"]
  list(zip(prompts, ans))                                  # [('Q1','A1'), ('Q2','A2')] (Q3 lost!)
  # list(zip(prompts, ans, strict=True))                   # ValueError: argument 2 is shorter
  qs, as_ = zip(*[("q1", "a1"), ("q2", "a2")])             # unzip -> ('q1','q2'), ('a1','a2')
  ```

* $\color{#00897B}\blacktriangleright$ **`all(iterable)` and `any(iterable)`:** C-level **short-circuiting** predicates: `all()` stops on the first falsy item (`False`); `any()` stops on the first truthy item (`True`). Use `sum(1 for x in seq if cond)` to count matches.
  * $\color{#0288D1}\bullet$ **Generator Rule:** Pass a generator `all(check(x) for x in seq)`, **not** a list comprehension `all([check(x) for x in seq])` — **Why:** `[...]` eagerly evaluates every item first, defeating short-circuiting.
  * $\color{#0288D1}\bullet$ **Vacuous Truth Trap:** `all([])` is **`True`** (found no falsy item) and `any([])` is `False`. Guard empty batches: `if items and all(...):`.
  ```python
  all([]), any([])                                         # True (vacuous truth!), False
  items = [0.8, 0.9]
  bool(items and all(s > 0.7 for s in items))              # True (safe + short-circuits)
  ```

* $\color{#BF360C}\blacktriangleright$ **`map(func, *iterables)` and `filter(func, iterable)`:** C-level, **single-use lazy iterators** (exhaust after 1 pass).
  * $\color{#0288D1}\bullet$ **When to use vs. Comprehension:** Use `map(fn, seq)` for an *existing* named function (`map(float, strs)`); use comprehensions for inline math/expressions (avoid `map(lambda ...)`). Use **`filter(None, seq)`** as the fastest C-speed way to strip all falsy items (`""`, `None`, `0`, `False`).
  ```python
  list(map(float, ["1.5", "2.8"]))                         # [1.5, 2.8]
  list(filter(None, ["Doc1", "", None, "Doc2"]))           # ['Doc1', 'Doc2']
  ```

* $\color{#4A148C}\blacktriangleright$ **`sorted(iterable, key=None, reverse=False)`:** Returns a **new** list from *any* iterable using C-level stable $O(n \log n)$ Timsort/Powersort (preserves relative order on ties; leaves original untouched, unlike `list.sort()` which mutates in-place and returns `None`).
  * $\color{#D32F2F}\blacktriangleright$ **Multi-Criteria Tie-Breaking:** Return a tuple from `key=` and negate **numbers** to mix descending/ascending order. **Trap:** Unary `-` fails on strings (`TypeError`).
  ```python
  chunks = [{"s": 0.9, "tok": 500}, {"s": 0.9, "tok": 120}]
  sorted(chunks, key=lambda c: (-c["s"], c["tok"]))        # [{'s':0.9,'tok':120}, {'s':0.9,'tok':500}]
  ```

* $\color{#1B5E20}\blacktriangleright$ **`round(number, ndigits=None)`:** Returns `int` if `ndigits` omitted; negative `ndigits` rounds to tens/hundreds/thousands (`round(148620, -3) -> 149000`).
  * $\color{#0288D1}\bullet$ **Banker's Rounding (Half-to-Even):** Ties round to the nearest *even* digit to avoid upward statistical drift (`round(2.5) -> 2`, `round(3.5) -> 4`).
  * $\color{#0288D1}\bullet$ **Binary Float Trap:** `round(2.675, 2)` yields `2.67` (stored as `2.674999...`). For exact financial/billing math, use `decimal.Decimal` with `ROUND_HALF_UP`; for strict direction, use `math.floor`/`math.ceil`.
  ```python
  from decimal import Decimal, ROUND_HALF_UP
  round(2.5), round(3.5), round(2.675, 2)                  # 2, 4, 2.67
  Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Decimal('2.68')
  ```

* $\color{#0288D1}\blacktriangleright$ **`print(*objects, sep=' ', end='\n', file=None, flush=False)`:** Standard output is RAM-buffered until `\n`, buffer full, or exit.
  * $\color{#0288D1}\bullet$ **AI Streaming Trap:** When streaming LLM tokens with `end=""` (no newline), default `flush=False` freezes the terminal and dumps everything at the end. Always pass `flush=True`. *(In prod services, use `logging`/`structlog`, not `print`.)*
  ```python
  for tok in ["AI ", "streams ", "live."]:
      print(tok, end="", flush=True)                       # renders immediately token-by-token
  ```

* $\color{#00897B}\blacktriangleright$ **`eval()`, `exec()`, and `ast.literal_eval()`:**
  * $\color{#0288D1}\bullet$ `eval(expr, globals, locals)`: evaluates a **single expression** and returns its value (`SyntaxError` on statements like `x = 10`).
  * $\color{#0288D1}\bullet$ `exec(code, globals, locals)`: executes **multi-line statements/scripts** and returns `None`.
  * $\color{#0288D1}\bullet$ **RCE Security Danger & Safe Parsing:** Never pass untrusted/LLM strings to `eval()` or `exec()` (prompt injection $\to$ OS shell execution). Use **`ast.literal_eval()`** to safely parse stringified Python literals (`dict`, `list`, `tuple`, `str`, `int`, `bool`, `None`); it blocks all code execution with `ValueError`.
  * $\color{#0288D1}\bullet$ **Sandboxing Gotcha:** Passing `globals={}` is **unsafe** because Python auto-reinjects `__builtins__` (must pass `{"__builtins__": None}` or a strict whitelist). Even then, Python cannot be safely sandboxed at the language level — production code interpreters isolate in Docker / gVisor microVMs / WebAssembly (Pyodide).
  ```python
  import ast
  ast.literal_eval("{'model': 'gpt-4o', 'temp': 0.7}")     # {'model': 'gpt-4o', 'temp': 0.7} (safe)
  # ast.literal_eval("__import__('os').system('ls')")      # ValueError (blocked!)
  safe_g, safe_l = {"__builtins__": {"sum": sum}}, {}
  exec("total = sum([10, 20])", safe_g, safe_l)            # safe_l['total'] -> 30
  ```

---

<a id="chapter-14"></a>

## 🚀 $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{14 — Advanced Python}}$

* $\color{#0288D1}\blacktriangleright$ **Walrus Operator (`:=`, Python 3.8+):** Assigns a variable *inside* an expression and returns it simultaneously — eliminates `while True` + `break` stream boilerplate and avoids recomputing expensive calls in comprehensions.
  * $\color{#0288D1}\bullet$ **Precedence Trap:** `:=` has low precedence — always wrap in parentheses `(x := expr)`.
  ```python
  while (tok := stream.read_token()): process(tok)        # read, bind, and check in 1 line
  hits = [round(s, 2) for d in docs if (s := sim(d)) > 0.8]  # computes sim(d) ONCE, not twice
  ```

* $\color{#00897B}\blacktriangleright$ **Generator Delegation (`yield from`) & `itertools`:** `yield from sub_gen()` delegates directly to an inner generator at C-speed (no nested `for` loop). Combine with `itertools` for zero-copy streaming, plus `collections.defaultdict` / `Counter` for grouping and frequency counts.
  ```python
  from itertools import batched, chain, islice
  def corpus(): yield from pdf_stream(); yield from slack_stream()
  list(batched(range(1, 6), 2))                           # [(1, 2), (3, 4), (5,)] (3.12+)
  list(chain(["a"], ["b", "c"]))                          # ['a', 'b', 'c'] (zero-copy)
  list(islice(infinite_ids(), 3))                         # lazy pagination of infinite stream
  ```

* $\color{#BF360C}\blacktriangleright$ **Memory Optimization (`__slots__`, `del`, `weakref`):**
  * $\color{#0288D1}\bullet$ **`__slots__`:** Prevents per-instance dynamic `__dict__` allocation (~150B $\to$ ~48B fixed C-struct; cuts RAM by 60–70% for 10k+ objects), but blocks adding ad-hoc attributes (`AttributeError`).
  * $\color{#0288D1}\bullet$ **`del x`:** Does **not** immediately free memory — only removes the name binding and decrements refcount by 1 (memory frees only when refcount hits 0; also deletes dict keys/list items).
  * $\color{#0288D1}\bullet$ **`weakref.WeakValueDictionary()`:** Holds cache values weakly — automatically evicts entries when the app drops strong references (prevents OOM cache leaks).
  ```python
  import weakref
  class Chunk:
      __slots__ = ("id", "score")
      def __init__(self, cid, s): self.id, self.score = cid, s
  c = Chunk("d1", 0.9); hasattr(c, "__dict__")            # False (c.extra = 1 -> AttributeError)

  cache = weakref.WeakValueDictionary()
  class Heavy: pass
  doc = Heavy(); cache["k"] = doc
  del doc                                                 # refcount hits 0 -> auto-evicted
  "k" in cache                                            # False (zero memory leak)
  ```

* $\color{#4A148C}\blacktriangleright$ **Timing & Profiling (`perf_counter`, `timeit`, `cProfile`):**
  * $\color{#0288D1}\bullet$ Always benchmark with `time.perf_counter()` (monotonic nanosecond clock; never drifts backwards on NTP sync/DST like `time.time()`).
  * $\color{#0288D1}\bullet$ Use `timeit.timeit()` for micro-benchmarks (averages out OS noise) and `cProfile` + `pstats` for macro-profiling CPU bottlenecks.
  ```python
  import time, timeit, cProfile, pstats
  t0 = time.perf_counter(); work(); ms = (time.perf_counter() - t0) * 1000
  timeit.timeit("[x*2 for x in range(100)]", number=10_000)
  prof = cProfile.Profile(); prof.enable(); work(); prof.disable()
  pstats.Stats(prof).sort_stats("cumulative").print_stats(3)
  ```

* $\color{#1B5E20}\blacktriangleright$ **Memoization (`@lru_cache`) & Parametrized `@retry`:** `@functools.lru_cache(maxsize=N)` caches deterministic return values with LRU eviction (inspect via `.cache_info()`).
  * $\color{#0288D1}\bullet$ **Hashability Trap:** All arguments to an `@lru_cache` function must be hashable — passing a `list` or `dict` raises `TypeError: unhashable type` (pass `tuple` instead).
  ```python
  from functools import lru_cache, wraps
  @lru_cache(maxsize=512)
  def build_prompt(role: str, tags: tuple[str, ...]) -> str: return f"{role}:{tags}"
  build_prompt.cache_info()                               # CacheInfo(hits=..., misses=...)

  def retry(max_retries=3, delay=0.5):                    # 3-layer parametrized decorator
      def dec(fn):
          @wraps(fn)
          def wrap(*a, **kw):
              for i in range(max_retries):
                  try: return fn(*a, **kw)
                  except ConnectionError:
                      if i == max_retries - 1: raise
                      time.sleep(delay)
          return wrap
      return dec
  ```

* $\color{#0288D1}\blacktriangleright$ **Advanced Context Managers (`contextlib`):** `@contextmanager` turns a single-`yield` generator into a `with`-compatible manager (wrap `yield` in `try ... finally` for guaranteed teardown). `ExitStack` dynamically manages an arbitrary number of context managers.
  ```python
  from contextlib import contextmanager, ExitStack
  @contextmanager
  def gpu_guard(dev: int):
      print(f"alloc {dev}")
      try: yield f"cuda:{dev}"
      finally: print(f"flush {dev}")                      # guaranteed even on exception

  with ExitStack() as stack:
      files = [stack.enter_context(open(p)) for p in paths]  # all auto-closed on exit
  ```

* $\color{#00897B}\blacktriangleright$ **Structural Pattern Matching (`match / case`, Python 3.10+):** Destructures nested mappings, sequences, types, and conditional guards (`if`) in one step (`case _:` = wildcard).
  ```python
  match payload:
      case {"action": "search", "query": str(q)}:         run_search(q)
      case {"bbox": [int(x1), int(y1), int(x2), int(y2)]}: crop(x1, y1, x2, y2)
      case {"error": str(msg), "code": int(c)} if c >= 500: alert(c, msg)
      case _:                                             handle_unknown(payload)
  ```

* $\color{#BF360C}\blacktriangleright$ **Assertions (`assert`) & The `-O` Production Trap:** `assert cond, "msg"` verifies internal developer invariants (e.g., tensor shapes).
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Running `python -O script.py` **completely strips all `assert` statements** at compile time! Never use `assert` for auth, billing, or user/API input validation — always use explicit `if` + `raise`.
  ```python
  assert tensor.shape == (32, 768), "Shape mismatch"      # internal invariant only
  if not api_key: raise ValueError("Missing API key")     # safe even under python -O
  ```

* $\color{#4A148C}\blacktriangleright$ **Dynamic Metaprogramming & Monkey Patching:**
  * $\color{#0288D1}\bullet$ `__getattr__(self, name)`: fallback hook called **only** when an attribute does *not* exist (transparent proxies).
  * $\color{#0288D1}\bullet$ `__init_subclass__(cls, **kw)`: runs automatically when any subclass is defined (zero-boilerplate plugin/tool registries).
  * $\color{#0288D1}\bullet$ **Monkey Patching:** Hot-swapping methods at runtime (`Client.call = mock_call`) for offline unit testing; in formal test suites, always use `unittest.mock.patch` (auto-restores on exit).
  ```python
  REGISTRY = {}
  class BaseTool:
      def __init_subclass__(cls, name=None, **kw):
          super().__init_subclass__(**kw)
          REGISTRY[name or cls.__name__.lower()] = cls
  class SearchTool(BaseTool, name="web_search"): pass     # auto-registered in REGISTRY!
  ```

* $\color{#1B5E20}\blacktriangleright$ **Enterprise Domain Exception Hierarchies:** Group domain errors under one base class (`AIPlatformError`) with metadata-carrying subclasses (`RateLimitExceededError`, `ContextWindowOverflowError`) so callers can catch narrowly or fall back broadly.
  ```python
  class AIPlatformError(Exception): pass
  class ContextOverflowError(AIPlatformError):
      def __init__(self, cur: int, max_t: int):
          self.cur, self.max_t = cur, max_t
          super().__init__(f"{cur} > {max_t} tokens")
  ```

---

<a id="chapter-22"></a>

## 📐 $\Large\color{#4A148C}\blacksquare\space\color{#6A1B9A}{\textsf{22 — Type Hints and Pydantic}}$

* $\color{#0288D1}\blacktriangleright$ **Static Type Hints & Runtime Non-Enforcement:** Annotate variables (`x: int = 5`), parameters, and returns (`-> str`).
  * $\color{#0288D1}\bullet$ **Critical Rule:** Plain type hints are **not enforced at runtime** (`age: int = "oops"` still executes). They exist for IDEs, static checkers (`mypy`/`pyright`), and human clarity.
  ```python
  name: str = "Ada"
  def greet(person: str) -> str: return f"Hello, {person}"
  ```

* $\color{#00897B}\blacktriangleright$ **Collections, Optionals & Typing Utilities (Python 3.10+):** Use lowercase generics (`list[int]`, `dict[str, float]`, `tuple[int, int]`), union pipe `X | None = None` for nullable values, `Literal[...]` to restrict allowed constant values, `Callable[[In], Out]` for function signatures, and `Any` sparingly for unstructured JSON. *(Reference: `TypeVar`, `Generic[T]`, `Protocol`, `TypedDict`.)*
  ```python
  from typing import Any, Callable, Literal

  scores: list[int] = [90, 75]
  email: str | None = None                                 # optional / nullable
  def set_mode(mode: Literal["fast", "accurate"]) -> None: ...
  embed_fn: Callable[[str], list[float]]                   # function taking str -> list[float]
  ```

* $\color{#BF360C}\blacktriangleright$ **Pydantic `BaseModel` — Runtime Validation, Coercion & Constraints:** (`pip install pydantic`). Unlike `@dataclass` (no runtime checks), Pydantic actively **validates** external data at system boundaries (APIs, user input, LLM outputs) and **coerces** compatible types (`"36"` $\to$ `36`). Use `Field(...)` for bounds (`ge`, `le`, `min_length`) and `@field_validator` (paired with `@classmethod`) for custom rules; invalid data raises `ValidationError` pinpointing the exact field.
  ```python
  from pydantic import BaseModel, Field, field_validator

  class User(BaseModel):
      name: str = Field(min_length=1)
      age: int = Field(ge=0, le=150)                       # must be 0..150
      email: str | None = None
      roles: list[str] = []

      @field_validator("name")
      @classmethod
      def not_blank(cls, v: str) -> str:
          if not v.strip(): raise ValueError("name cannot be blank")
          return v

  u = User(name="Ada", age="36")                           # coerces "36" -> 36 (int)
  # User(name="  ", age=200)                               # raises ValidationError (both fields!)
  ```

* $\color{#4A148C}\blacktriangleright$ **Serialization & Deserialization:** Parse JSON directly at the boundary and dump cleanly back to dicts or JSON strings.
  ```python
  u2 = User.model_validate_json('{"name": "Bo", "age": 29}')  # JSON str -> validated User
  d = u2.model_dump()                                         # {'name': 'Bo', 'age': 29, ...}
  s = u2.model_dump_json()                                    # '{"name":"Bo","age":29,...}'
  restored = User(**d)                                        # dict -> validated User
  ```

* $\color{#1B5E20}\blacktriangleright$ **Environment Secrets & Config (`pydantic-settings`):** (`pip install pydantic-settings`). Subclass `BaseSettings` to automatically load and validate required environment variables (case-insensitive mapping: `openai_api_key` $\leftrightarrow$ `OPENAI_API_KEY`) — never hardcode secrets.
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      openai_api_key: str                                  # auto-read from OPENAI_API_KEY env var
      model: str = "gpt-4o-mini"                           # fallback default
  # settings = Settings()                                  # raises ValidationError if secret missing
  ```

---

<a id="chapter-23"></a>

## 🚦 $\Large\color{#0D47A1}\blacksquare\space\color{#1565C0}{\textsf{23 — Concurrency: Async, Threads and Processes}}$

* $\color{#0288D1}\blacktriangleright$ **The GIL (Global Interpreter Lock):** In standard CPython, only **one thread executes Python bytecode at a time**.
  * $\color{#0288D1}\bullet$ **Why it matters:** Threads do **not** speed up CPU-bound pure Python math. However, threads *release* the GIL while waiting on network/disk I/O, allowing I/O-bound tasks to overlap.

* $\color{#00897B}\blacktriangleright$ **Async (`asyncio`) — Default for I/O-Bound AI:** Single-threaded cooperative multitasking driven by an **event loop** (`asyncio.run()`). `async def` defines a **coroutine**; `await` suspends it on I/O so other tasks run. Use `asyncio.gather()` to fan out concurrently, `asyncio.create_task()` to schedule background work, `async with` / `async for` for async clients and LLM token streams, and `asyncio.Semaphore(N)` to cap concurrency (prevents HTTP 429 rate limits).
  * $\color{#0288D1}\bullet$ **3 Critical Traps:**
    1. Calling `await a(); await b()` runs **sequentially** — use `asyncio.gather(a(), b())` to overlap.
    2. Calling a blocking sync function (e.g., `time.sleep()`, `requests.get()`) inside `async def` **freezes the entire event loop** (all other coroutines stall).
    3. Calling `main()` without `asyncio.run(main())` returns an unexecuted coroutine object.
  ```python
  import asyncio

  sem = asyncio.Semaphore(5)                 # cap max 5 concurrent API calls
  async def fetch(name: str, sec: float) -> str:
      async with sem:
          await asyncio.sleep(sec)           # pauses cleanly; event loop runs others
          return name

  async def main():
      # Overlaps all 3 waits -> finishes in ~2s total (not 6s!)
      res = await asyncio.gather(fetch("A", 2), fetch("B", 2), fetch("C", 2))
      # async with client as c: ... | async for chunk in stream: ...
      return res

  asyncio.run(main())                        # ['A', 'B', 'C'] in ~2.0s
  ```

* $\color{#BF360C}\blacktriangleright$ **Threads (`ThreadPoolExecutor`) — For Blocking I/O:** Multiple OS threads sharing process memory (GIL-bound). Use for **I/O-bound** work when the library has **no `async` API** (e.g., `urllib`, legacy sync SQL drivers, blocking disk reads) or to offload blocking calls off the async event loop.
  ```python
  from concurrent.futures import ThreadPoolExecutor
  import urllib.request

  def download(url: str) -> bytes:
      return urllib.request.urlopen(url).read()[:50]

  with ThreadPoolExecutor(max_workers=3) as pool:
      results = list(pool.map(download, ["https://example.com"] * 3))
  ```

* $\color{#4A148C}\blacktriangleright$ **Processes (`ProcessPoolExecutor`) — For CPU-Bound Work:** Spawns independent OS processes, each with its **own** Python interpreter, memory space, and GIL — true multi-core CPU parallelism, at the cost of higher RAM/startup overhead. *(Remember `if __name__ == "__main__":` on Windows/macOS.)*
  ```python
  from concurrent.futures import ProcessPoolExecutor

  def heavy(n: int) -> int:
      return sum(i * i for i in range(n))

  if __name__ == "__main__":
      with ProcessPoolExecutor() as pool:
          results = list(pool.map(heavy, [1_000_000, 1_000_000]))
  ```

* $\color{#1B5E20}\blacktriangleright$ **Concurrency Decision Rule:**
  * $\color{#0288D1}\bullet$ **I/O-bound (LLM APIs, DBs, HTTP):** `asyncio` (lightest, AI default) — or `ThreadPoolExecutor` if the library is blocking.
  * $\color{#0288D1}\bullet$ **CPU-bound pure Python (parsing/tokenizing millions of rows):** `ProcessPoolExecutor`.
  * $\color{#0288D1}\bullet$ **Heavy array/matrix math (embeddings, tensors):** Delegate to C/CUDA libraries (**NumPy / PyTorch**), which bypass the GIL internally. *(Reference: `asyncio.Queue`, `asyncio.Lock`, raw `threading.Thread`, process IPC pipes.)*

---

<a id="chapter-24"></a>

## 🌐 $\Large\color{#00695C}\blacksquare\space\color{#00897B}{\textsf{24 — AI Essentials: NumPy and HTTP}}$

* $\color{#0288D1}\blacktriangleright$ **NumPy Basics & Vectorization:** (`pip install numpy`, alias `import numpy as np`). Stores homogeneous numbers in contiguous C memory (`np.ndarray`) and runs math across entire arrays in C/BLAS SIMD (**vectorization**) — 50–100x faster than Python loops. Inspect dimensions via `.shape` and type via `.dtype`. *(Occasional: broadcasting `matrix + bias` without copying, `.reshape(-1, dim)`, `np.zeros()`, `np.ones()`.)*
  * $\color{#D32F2F}\blacktriangleright$ **Trap:** Never iterate over large numeric arrays in pure Python loops — pointer chasing and dynamic boxing destroy performance.
  ```python
  import numpy as np
  a = np.array([1, 2, 3], dtype=np.float32)       # 1-D vector; a.shape -> (3,), a.dtype -> float32
  m = np.array([[1, 2], [3, 4]])                  # 2-D matrix; m.shape -> (2, 2)
  a * 10, a.mean(), a.sum(), a.max()              # array([10.,20.,30.]), 2.0, 6.0, 3.0
  float(np.dot(a, a)), float(a @ a)               # 14.0, 14.0 (vectorized dot product)
  ```

* $\color{#00897B}\blacktriangleright$ **Cosine Similarity, Embeddings & RAG Core:** An **embedding** is a vector capturing text meaning. **Cosine similarity** scores how aligned two vectors are by **direction** in `[-1, 1]` (`+1` = same meaning, `0` = unrelated/orthogonal, `-1` = opposite), ignoring length so short and long texts on the same topic still match. **Vector databases** (pgvector, Pinecone, Qdrant) scale this search to millions of embeddings; **RAG** retrieves top chunks and passes them to an LLM.
  ```python
  def cosine_sim(u: np.ndarray, v: np.ndarray) -> float:
      return float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

  dog, puppy, mkt = np.array([0.9, 0.1, 0.0]), np.array([0.8, 0.2, 0.0]), np.array([0.0, 0.1, 0.9])
  round(cosine_sim(dog, puppy), 3), round(cosine_sim(dog, mkt), 3)  # 0.985, 0.135
  ```

* $\color{#BF360C}\blacktriangleright$ **Synchronous HTTP (`requests`):** (`pip install requests`). Best for quick blocking scripts/tests. Passing `json={...}` auto-serializes the dict and sets JSON headers.
  * $\color{#0288D1}\bullet$ **2 Critical HTTP Traps:** (1) Always pass `timeout=...` — without it, a hung server freezes your process forever; (2) Always call `resp.raise_for_status()` before `resp.json()` — otherwise 4xx/5xx error HTML is passed to the JSON parser.
  ```python
  import requests
  r = requests.post(
      "https://httpbin.org/post",
      json={"name": "Ada"},
      headers={"Authorization": "Bearer SECRET"},
      timeout=10,
  )
  r.raise_for_status()                            # raises HTTPError on 4xx/5xx
  data = r.json()                                 # parses JSON body -> dict
  ```

* $\color{#4A148C}\blacktriangleright$ **Asynchronous HTTP (`httpx`) & Streaming:** (`pip install httpx`). Reuse a single `httpx.AsyncClient(timeout=10.0)` context manager for **connection pooling & TLS session reuse** across concurrent `asyncio.gather()` calls. Use `async with client.stream(...) as resp:` for Server-Sent Events (SSE) token streaming.
  ```python
  import asyncio, httpx

  async def get_todo(client: httpx.AsyncClient, n: int) -> str:
      r = await client.get(f"https://jsonplaceholder.typicode.com/todos/{n}")
      r.raise_for_status()
      return r.json()["title"]

  async def main():
      async with httpx.AsyncClient(timeout=10.0) as client:   # pooled async client
          return await asyncio.gather(*(get_todo(client, i) for i in range(1, 6)))
  # asyncio.run(main())                                       # 5 calls overlapped
  ```

* $\color{#1B5E20}\blacktriangleright$ **Secrets via Environment Variables:** Never hardcode API keys in source code (leak risk). Load from `os.environ` (or `.env`) and fail fast if absent.
  ```python
  import os
  api_key = os.environ.get("OPENAI_API_KEY")
  if not api_key: raise RuntimeError("Set OPENAI_API_KEY first")
  headers = {"Authorization": f"Bearer {api_key}"}
  ```

---

<a id="chapter-25"></a>

## 🏆 $\Large\color{#BF360C}\blacksquare\space\color{#D84315}{\textsf{25 — Milestone: Typed API CLI Tool}}$

* $\color{#0288D1}\blacktriangleright$ **Environment Setup:** Isolate with `venv` and install the 3 production libraries (`httpx` for async HTTP, `pydantic` for boundary validation, `tenacity` for decorator retries), then freeze to `requirements.txt`.
  ```powershell
  python -m venv .venv; .\.venv\Scripts\Activate.ps1
  pip install httpx pydantic tenacity && pip freeze > requirements.txt
  ```

* $\color{#00897B}\blacktriangleright$ **The 3 Guarded Production Boundaries:**
  1. **Network Boundary:** `async with httpx.AsyncClient(timeout=10)` prevents dangling sockets/infinite hangs; `resp.raise_for_status()` traps 4xx/5xx errors; `@retry` (`tenacity`) auto-retries transient failures (3 attempts, 1s fixed wait).
  2. **Data Shape Boundary:** `Todo(**resp.json())` validates JSON against a Pydantic `BaseModel` immediately, raising `ValidationError` on schema drift or bad types (e.g., changing `id: int` to `id: bool`).
  3. **Orchestration Boundary:** `asyncio.gather(...)` fans out requests concurrently; outer `try/except` chains any unhandled failure into a clean domain exception (`raise TodoError(...) from error`).

* $\color{#BF360C}\blacktriangleright$ **Complete Production CLI Reference (`main.py`):** Combines execution guard (`__name__ == "__main__"`), async fan-out, `@retry`, context managers, custom chained exceptions, Pydantic validation, ternary expressions, and aligned f-string slicing (`[:40]:<40`).
  ```python
  import asyncio, httpx
  from pydantic import BaseModel
  from tenacity import retry, stop_after_attempt, wait_fixed

  URL = "https://jsonplaceholder.typicode.com/todos/{id}"

  class Todo(BaseModel):
      userId: int; id: int; title: str; completed: bool

  class TodoError(Exception): pass

  @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
  async def fetch_todo(todo_id: int) -> Todo:
      async with httpx.AsyncClient(timeout=10) as client:
          resp = await client.get(URL.format(id=todo_id))
          resp.raise_for_status()                        # 4xx/5xx -> triggers @retry
          return Todo(**resp.json())                     # runtime schema boundary

  async def main() -> None:
      try:
          todos = await asyncio.gather(*(fetch_todo(i) for i in range(1, 4)))
      except Exception as err:
          raise TodoError(f"Failed to fetch todos: {err}") from err  # chained domain error

      for t in todos:
          status = "done" if t.completed else "pending"
          print(f"[{t.id}] {t.title[:40]:<40} — {status}")  # e.g. [1] delectus aut autem ... — pending

  if __name__ == "__main__":
      asyncio.run(main())                                # entry guard + event loop
  ```
