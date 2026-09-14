# 05 — Dictionaries & Sets

> Phase 0 · Module 0.1 · Lesson 5 of 16

## 🗺️ Stage 0 — Concept Map

Lists store items by **position**. But often you want to look something up by **name** — a price
by product, a score by user. That's a **dictionary**, the most-used data structure in real Python.
A **set** is its cousin: an unordered bag of **unique** items. And just as lists have immutable
tuples, sets have an immutable counterpart: **`frozenset`**. Both build on what you know and
power configuration, JSON data, and the `messages`/metadata you'll send to AI models.

## 🔑 New Terms (plain English)

- **Dictionary (dict)** — stores **key → value** pairs; you look things up by key.
- **Key** — the unique label you look up (must be immutable: str/int/tuple/frozenset).
- **Value** — the data stored under a key (can be anything).
- **Set** — an unordered collection of **unique** items.
- **`frozenset`** — an immutable (unchangeable), hashable version of a set.
- **Hashable** — an object whose value never changes, producing a fixed hash code (required for dict keys and set elements).
- **Membership** — testing whether something is present: `x in collection`.

## 🎈 Stage 1 — The Simple Idea (analogy: a real dictionary, and a bag of unique marbles)

A **dictionary (dict)** is like a word dictionary: you look up a **key** (the word) to get its
**value** (the definition). Lookups are by key, not position, and they're instant.

A **set** is a bag of marbles where duplicates are impossible — toss in two identical marbles and
only one remains. Order isn't tracked; membership is.

A **`frozenset`** is that same bag of marbles sealed tight in clear epoxy resin — you can inspect the
contents and check if a marble is inside, but you can never add or remove anything. Because it is
fixed and immutable, it can safely serve as a dictionary key or sit inside another set.

**The "Aha!":** dict = "look up a value by its key"; set = "a collection that automatically removes
duplicates and answers 'is this in here?' very fast." Notice the symmetry:
`list` (mutable) ──► `tuple` (immutable)
`set`  (mutable) ──► `frozenset` (immutable)

## ⚙️ Stage 2 — How It Actually Works

### 5.1 Creating and reading dicts

```python
# keys -> values, in curly braces. Keys are usually strings; values can be anything.
person = {"name": "Ada", "age": 36, "is_engineer": True}

print(person["name"])      # 'Ada'  — look up by key with square brackets
# print(person["email"])   # KeyError! the key doesn't exist

# .get() is the SAFE lookup: returns None (or a default) instead of crashing.
print(person.get("email"))            # None
print(person.get("email", "n/a"))     # 'n/a'  — supply a fallback
```

### 5.2 Adding, updating, deleting

```python
person["email"] = "ada@example.com"   # add a new key (or overwrite if it exists)
person["age"] = 37                     # update
person.update({"city": "London", "age": 38})  # add/overwrite several at once

del person["is_engineer"]              # remove a key
removed = person.pop("city")           # remove AND return the value
print("name" in person)                # True — membership tests the KEYS
```

### 5.3 Looping over a dict

```python
scores = {"math": 90, "art": 75}

for key in scores:                 # iterating a dict yields its KEYS
    print(key, scores[key])

for key, value in scores.items():  # .items() gives key+value pairs — the usual way
    print(f"{key} -> {value}")

print(list(scores.keys()))         # ['math', 'art']
print(list(scores.values()))       # [90, 75]
```

### 5.4 Nested Dictionaries & Real-Life Patterns (JSON, APIs, and setdefault)

Real-world Python and AI code rarely deals with flat dictionaries. API responses, database records, and LLM payloads are **nested dictionaries** containing lists and other dicts.

#### 1. Accessing nested data: direct indexing vs safe chained lookups

Direct square brackets `d["a"]["b"]` work when keys are guaranteed to exist, but crash with `KeyError` if any intermediate key is missing. Use chained `.get()` with an empty dictionary `{}` fallback for safe traversal.

```python
user = {
    "name": "Ada",
    "roles": ["admin", "editor"],                  # list inside a dict
    "address": {"city": "London", "zip": "EC1"},  # dict inside a dict
}

# Direct access (crashes with KeyError if any key is missing):
print(user["roles"][0])                    # 'admin'
print(user["address"]["city"])             # 'London'

# Safe navigation using chained .get():
# If "profile" is absent, returns {} so the second .get() doesn't crash:
theme = user.get("profile", {}).get("theme", "light")
print(theme)                               # 'light' (default used safely)

# ⚠️ Real-world API gotcha: What if a key exists, but its value is None?
# {"profile": None}.get("profile", {}) returns None, not {}!
# Pattern: use '(d.get("key") or {})' to guarantee a dict:
api_user = {"name": "Bo", "profile": None}
font = (api_user.get("profile") or {}).get("font", "Inter")
print(font)                                # 'Inter'
```

#### 2. Real-life AI application: Parsing an LLM API response

When you call modern LLM APIs (OpenAI, Anthropic, Gemini), the response arrives as a nested dictionary structure. Here is how you extract output and metrics:

```python
# Realistic OpenAI chat completion dictionary:
response = {
    "id": "chatcmpl-876",
    "model": "gpt-4o",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "A dictionary is a hash map in Python.",
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 14, "completion_tokens": 9, "total_tokens": 23},
}

# 1. Extract the generated assistant message:
assistant_reply = response["choices"][0]["message"]["content"]
print(assistant_reply)                     # 'A dictionary is a hash map in Python.'

# 2. Safely read token metrics without crashing if usage is omitted:
total_tokens = response.get("usage", {}).get("total_tokens", 0)
print("Tokens used:", total_tokens)        # 23
```

#### 3. `setdefault()`: Grouping & safe nested initialization

- **`d.get(key, default)`**: reads the value or returns default, but **never modifies** the dictionary.
- **`d.setdefault(key, default)`**: if `key` exists, returns its value. If `key` is missing, it **inserts** `d[key] = default` and returns it.

This is the standard pattern for grouping items into lists or initializing nested dictionaries dynamically.

```python
# (a) Difference between .get() and .setdefault():
d1 = {}
res1 = d1.get("tags", [])
print("d1 after .get():", d1)              # {} (d1 is still completely empty!)

d2 = {}
res2 = d2.setdefault("tags", [])
print("d2 after setdefault:", d2)          # {'tags': []} (inserted in-place!)
res2.append("python")
print("d2 after append:", d2)              # {'tags': ['python']}

# (b) Real-world AI pattern: Grouping conversation messages by role:
chat_log = [
    {"role": "user", "content": "What is RAG?"},
    {"role": "assistant", "content": "Retrieval-Augmented Generation."},
    {"role": "user", "content": "Can you give an example?"},
]

messages_by_role = {}
for msg in chat_log:
    # If role doesn't exist, creates an empty list; then appends content:
    messages_by_role.setdefault(msg["role"], []).append(msg["content"])

print(messages_by_role)
# Output:
# {
#   'user': ['What is RAG?', 'Can you give an example?'],
#   'assistant': ['Retrieval-Augmented Generation.']
# }

# (c) Initializing nested configuration dynamically:
agent_config = {}
agent_config.setdefault("llm_params", {})["temperature"] = 0.2
agent_config.setdefault("llm_params", {})["max_tokens"] = 500
print(agent_config)                        # {'llm_params': {'temperature': 0.2, 'max_tokens': 500}}
```

#### 4. Merging dictionaries: `|` vs `|=` vs `.update()`

In Python 3.9+, you can merge dictionaries cleanly using the pipe operator `|`.

```python
default_settings = {"model": "gpt-4o", "temperature": 0.7, "stream": False}
user_overrides = {"temperature": 0.2, "stream": True}

# 1. New dictionary using '|' (overrides overwrite defaults):
active_config = default_settings | user_overrides
print(active_config)
# {'model': 'gpt-4o', 'temperature': 0.2, 'stream': True}

# 2. In-place merge using '|=' or .update():
default_settings |= user_overrides         # or default_settings.update(user_overrides)
print(default_settings["temperature"])     # 0.2
```

#### 5. Safe popping with defaults (`pop(key, default)`)

Unlike `del d[key]` which crashes with `KeyError` if the key is absent, `d.pop(key, default)` returns a fallback:

```python
params = {"model": "gpt-4o", "temperature": 0.5}

# Extract and remove a parameter, with a safe fallback if missing:
temp = params.pop("temperature", 0.7)      # returns 0.5 and deletes it from params
timeout = params.pop("timeout", 30)        # missing key -> returns 30 without error
print("Extracted temp:", temp)             # 0.5
print("Remaining params:", params)         # {'model': 'gpt-4o'}
```

#### 6. Storing Custom Objects in Dictionaries

Dictionary **values** can be any Python object without restriction (models, class instances, agent tools). Dictionary **keys** can also be objects, provided they are **hashable** (custom class instances are hashable by default based on memory `id()`):

```python
class AgentTool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, query: str) -> str:
        return f"Executing {self.name} for query: '{query}'"

# 1. Custom objects as dictionary values (the standard AI agent registry pattern):
tool_registry = {
    "search": AgentTool("WebSearch", "Searches the web for recent info"),
    "calculator": AgentTool("Calculator", "Solves math expressions"),
}

print(tool_registry["search"].description)
# Output: 'Searches the web for recent info'

result = tool_registry["calculator"].execute("25 * 4")
print(result)
# Output: "Executing Calculator for query: '25 * 4'"

# 2. Custom objects as dictionary keys (allowed because instances have unique id()):
tool_obj = AgentTool("Translator", "Translates text")
call_counts = {tool_obj: 0}
call_counts[tool_obj] += 1
print(call_counts[tool_obj])               # 1
```

### 5.5 Sets — unique, fast membership

A set is an unordered collection of unique, hashable items. Duplicates collapse automatically, and membership checks (`in`) run in $O(1)$ constant time.

```python
tags = {"python", "ai", "python"}   # duplicates collapse
print(tags)                          # {'python', 'ai'} (order not guaranteed)
print("ai" in tags)                  # True — very fast membership check
```

#### 1. Adding elements: `add()` vs `update()`

- **`add(item)`**: adds a **single** hashable element (like `list.append()`). Cannot take a list.
- **`update(*iterables)`**: unpacks collections and adds items **in-place** (like `list.extend()`), collapsing duplicates.

```python
s = {1, 2}

# add(item) — adds a single element; duplicates are silently ignored:
s.add(3)
s.add(2)                             # 2 already exists, nothing changes
print(s)                             # {1, 2, 3}

# ⚠️ GOTCHA: add() CANNOT take a list (lists are unhashable):
# s.add([4, 5])                      # TypeError: unhashable type: 'list'

# Adding a tuple with add() stores the tuple as ONE compound item:
s.add((4, 5))
print(s)                             # {1, 2, 3, (4, 5)}

# update(*iterables) — unpacks collections and collapses duplicates in-place:
numbers = {1, 2}

# Literal list with internal duplicates:
numbers.update([2, 3, 3, 4])         # 2 already in set; duplicate 3 collapsed
print(numbers)                       # {1, 2, 3, 4}

# List variable with duplicates:
more_nums = [4, 5, 5, 6]
numbers.update(more_nums)            # 4 already in set; duplicate 5 collapsed
print(numbers)                       # {1, 2, 3, 4, 5, 6}

# Other data types with update():
numbers.update((6, 7, 7))            # tuple (duplicate 7 collapsed)
print(numbers)                       # {1, 2, 3, 4, 5, 6, 7}

word_set = {"start"}
word_set.update("cat")               # string (unpacks individual characters!)
print(word_set)                      # {'start', 'c', 'a', 't'}

word_set.update({"model": "gpt-4", "temp": 0.7}) # dict (unpacks only the KEYS)
print(word_set)                      # {'start', 'c', 'a', 't', 'model', 'temp'}

numbers.update([8, 9], (9, 10))      # multiple iterables in one call
print(numbers)                       # {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

#### 2. Removing elements: `discard()`, `remove()`, `pop()`, `clear()`

- **`discard(x)`**: removes `x` if present; silent no-op if absent (safe).
- **`remove(x)`**: removes `x` if present; crashes with `KeyError` if absent.
- **`pop()`**: removes and returns an **arbitrary** item (sets are unordered, so you cannot predict or choose which item is popped, and cannot pass an index).
- **`clear()`**: removes all items in-place, leaving `set()`.

```python
items = {"chunk_1", "chunk_2", "chunk_3"}

# (a) discard(x) — safe removal (no error if missing):
items.discard("chunk_99")            # does nothing, NO error raised
print(items)                         # {'chunk_1', 'chunk_2', 'chunk_3'}

# (b) remove(x) — strict removal (crashes if missing):
items.remove("chunk_1")              # successfully removed
print(items)                         # {'chunk_2', 'chunk_3'}
# items.remove("chunk_99")           # 💥 KeyError: 'chunk_99'

# (c) pop() — removes and returns an arbitrary item:
# ⚠️ Cannot pass an index like items.pop(0) — raises TypeError: set.pop() takes no arguments
popped_item = items.pop()            # removes an arbitrary item
print("Popped:", popped_item)        # e.g. 'chunk_2'
print("Remaining:", items)           # e.g. {'chunk_3'}
# empty_s = set(); empty_s.pop()     # 💥 KeyError: 'pop from an empty set'

# (d) clear() — removes all elements in-place:
items.clear()
print(items)                         # set() (empty set)
```

#### 3. Mixed data types & the Boolean gotcha

A set can hold multiple different data types at once as long as each element is hashable. However, because Python treats `True == 1` and `False == 0`, boolean values will collapse into their integer counterparts.

```python
# Mixed types in one set:
mixed_set = {"user_101", 42, (1, 2), 3.14}
print(mixed_set)                     # {'user_101', 42, (1, 2), 3.14}

# ⚠️ GOTCHA: bool is a subclass of int (True == 1, False == 0, hash matches):
bool_gotcha = {1, True, 0, False}
print(bool_gotcha)                   # {0, 1} (True collapsed into 1, False into 0!)
```

#### 4. How to restrict data types in sets

Python sets are dynamic and do not enforce types at runtime by default. Modern Python and AI code use three common approaches:

```python
# (a) Static type hints (Python 3.9+ standard — checked with Mypy / IDE):
doc_ids: set[str] = {"doc_a", "doc_b"}

# (b) Runtime validation function / assertion:
def add_doc_id(id_set: set[str], new_id: str) -> None:
    if not isinstance(new_id, str):
        raise TypeError(f"Expected str, got {type(new_id).__name__}")
    id_set.add(new_id)

# (c) Pydantic model validation (modern standard in AI / FastAPI schemas):
# from pydantic import BaseModel
# class AgentState(BaseModel):
#     visited_tools: set[str]        # validates and guarantees only strings at runtime
```

#### 5. Combining sets (Concatenation): `|` vs `.union()` vs `|=`

Sets do not support the `+` operator. Use the union operator `|` or the `.union()` method to create a new combined set, or `|=` / `.update()` to combine in-place.

```python
set_a = {"retrieve", "rerank"}
set_b = {"rerank", "generate"}

# ⚠️ GOTCHA: '+' does NOT work on sets!
# combined = set_a + set_b           # TypeError: unsupported operand type(s) for +: 'set' and 'set'

# Use union operator '|' (requires both sides to be sets):
print(set_a | set_b)                 # {'retrieve', 'rerank', 'generate'} (new set)

# Use .union() method (accepts ANY iterable, like a list):
print(set_a.union(["evaluate"]))     # {'retrieve', 'rerank', 'generate', 'evaluate'} (new set)

# In-place union / update (mutates set_a in-place):
set_a |= set_b                       # or set_a.update(set_b)
print(set_a)                         # {'retrieve', 'rerank', 'generate'}
```

#### 6. Overlaps vs differences: `intersection`, `symmetric_difference`, `difference`

- **Intersection (`&`)**: keeps **only duplicates / common elements** present in both sets.
- **Symmetric Difference (`^`)**: keeps elements present in either set, but **not in both** (excludes common duplicates).
- **Difference (`-`)**: keeps elements present in the first set that are **not** in the second set.

```python
agent_a_tools = {"search", "calculator", "summarize"}
agent_b_tools = {"calculator", "python_repl", "summarize"}

# (a) INTERSECTION ('&' or .intersection()) — KEEP ONLY DUPLICATES (items in BOTH sets):
common_tools = agent_a_tools & agent_b_tools
print(common_tools)                  # {'calculator', 'summarize'}
# In-place: agent_a_tools &= agent_b_tools (or agent_a_tools.intersection_update(...))

# (b) SYMMETRIC DIFFERENCE ('^' or .symmetric_difference()) — ITEMS IN EITHER, BUT NOT BOTH:
exclusive_tools = agent_a_tools ^ agent_b_tools
print(exclusive_tools)               # {'search', 'python_repl'}
# In-place: agent_a_tools ^= agent_b_tools (or agent_a_tools.symmetric_difference_update(...))

# (c) DIFFERENCE ('-' or .difference()) — ITEMS IN FIRST SET BUT NOT SECOND:
unique_to_a = agent_a_tools - agent_b_tools
print(unique_to_a)                   # {'search'}
# In-place: agent_a_tools -= agent_b_tools (or agent_a_tools.difference_update(...))

# ⚠️ Operator vs Method difference:
# Operators ('&', '|', '-', '^') require BOTH operands to be sets:
# print(agent_a_tools & ["search"])  # TypeError: unsupported operand type(s) for &: 'set' and 'list'
# Methods accept ANY iterable:
print(agent_a_tools.intersection(["search", "other"])) # {'search'} (works!)
```

#### 7. Creating sets from other types using `set()`

Pass any iterable to the `set()` constructor to convert it into a set and deduplicate items automatically.

```python
# (a) The empty set gotcha:
empty_set = set()                    # ✅ Correct way to create an empty set
empty_dict = {}                      # ⚠️ Gotcha: '{}' creates an empty DICT, not a set!

# (b) From a list or tuple (instantly deduplicates):
nums = [1, 2, 2, 3, 3, 3]
print(set(nums))                     # {1, 2, 3}
print(list(set(nums)))               # [1, 2, 3] — list -> set -> list (dedup pattern)
tuple_data = (10, 20, 20, 30)
print(set(tuple_data))               # {10, 20, 30}

# (c) From a string (splits into unique individual characters):
chars = set("banana")
print(chars)                         # {'b', 'a', 'n'}

# (d) From a dictionary (extracts unique KEYS):
person = {"name": "Ada", "role": "admin"}
print(set(person))                   # {'name', 'role'}
```

#### 8. Storing Custom Objects in Sets (Identity vs Value Deduplication)

Sets can hold custom objects, but you must understand how Python tests for uniqueness:

- **Default behavior (Identity Hashing):** By default, user-defined class instances are hashed by their memory address (`id()`). Two distinct instances with identical fields will **not** collapse as duplicates!
- **Value-based Deduplication:** Use `@dataclass(frozen=True)` (or define `__hash__` and `__eq__`) so the set compares their actual data instead of their memory address.

```python
# 1. Standard class: deduplicates by identity (memory address id()):
class Document:
    def __init__(self, doc_id: int, text: str):
        self.doc_id = doc_id
        self.text = text

d1 = Document(101, "Intro to LLMs")
d2 = Document(101, "Intro to LLMs")        # identical data, but separate memory object!

doc_set = {d1, d2}
print(len(doc_set))                        # 2! (id(d1) != id(d2), so both are kept)

# 2. Frozen dataclass: deduplicates by VALUE:
from dataclasses import dataclass

@dataclass(frozen=True)
class FrozenDoc:
    doc_id: int
    text: str

f1 = FrozenDoc(101, "Intro to LLMs")
f2 = FrozenDoc(101, "Intro to LLMs")       # identical values
frozen_doc_set = {f1, f2}
print(len(frozen_doc_set))                 # 1! (Duplicates collapse by value)
print(frozen_doc_set)                      # {FrozenDoc(doc_id=101, text='Intro to LLMs')}
```

**Why sets are fast:** checking `x in big_list` scans every item ($O(n)$); `x in big_set` jumps almost instantly ($O(1)$) regardless of size. For "have I seen this already?" checks, sets win.

### 5.6 frozenset — the immutable set

Because a normal `set` is mutable (you can `.add()` or `.discard()` items), Python considers it
**unhashable**. That means you **cannot** use a standard set as a dictionary key, nor can you put a
set inside another set:

```python
# This fails with TypeError: unhashable type: 'set':
# bad_key = {"read", "write"}
# roles = {bad_key: "Editor"} 
```

The solution is **`frozenset`** — an unchangeable set created by passing any iterable to `frozenset()`:

```python
# Create a frozenset:
fs = frozenset(["read", "write", "read"])  # duplicates collapse, just like a set
print(fs)                                  # frozenset({'read', 'write'})

# 1. It is immutable — no adding or removing:
# fs.add("delete")                         # AttributeError: 'frozenset' object has no attribute 'add'

# 2. It supports all membership and set algebra operations:
print("read" in fs)                        # True
other = frozenset(["write", "execute"])
print(fs & other)                          # frozenset({'write'})  (intersection)

# 3. Because it is immutable, it is HASHABLE — perfect for dict keys:
role_permissions = {
    frozenset(["read"]): "Viewer",
    frozenset(["read", "write"]): "Editor",
    frozenset(["read", "write", "admin"]): "Administrator",
}

user_claims = frozenset(["write", "read"]) # order doesn't matter!
print(role_permissions[user_claims])       # 'Editor'

# 4. You can also store frozensets inside another set (a set of sets):
groups = {frozenset([1, 2]), frozenset([3, 4])}
```

## 🚀 Stage 3 — In Practice / Why It Matters

Dicts are the backbone of AI code: an LLM message is `{"role": "user", "content": "..."}`, API
responses are nested dicts, configuration is a dict. Sets are perfect for deduplicating retrieved
document IDs or tracking "which chunks have we already used." `frozenset` is often used when caching
function results where the lookup key is an unordered set of tags, filters, or permission flags.

**Common beginner mistakes (the reasoning):**
1. **`KeyError` from `dict[key]`** on a missing key — use `.get(key, default)` when a key might be
   absent. *Reason:* `[]` assumes the key exists; `.get` doesn't.
2. **Assuming dict iteration gives values** — `for x in d:` gives **keys**. Use `d.items()` for
   pairs or `d.values()` for values.
3. **Trying to use a list or set as a key** — keys must be immutable and hashable (str, int, tuple,
   frozenset). *Reason:* a key's hash code must never change while sitting in a dict.
4. **Relying on set order** — sets are unordered; don't index them (`myset[0]` is an error).
5. **Using `{}` to create an empty set** — `{}` creates an empty **dictionary** (`dict`), not a set! Always use `set()`.
6. **Trying to use `+` to combine sets** — `s1 + s2` raises `TypeError`. Use `s1 | s2` (new set) or `s1 |= s2` / `s1.update()` (in-place).
7. **Expecting `s.pop()` to return the first or last item** — sets have no sequence order; `pop()` returns an *arbitrary* item and raises `KeyError` if empty.
8. **Expecting `s.remove()` to fail silently** — `remove()` raises `KeyError` if the item is absent; use `discard()` for safe removal.
9. **Chaining `[]` on nested dictionaries** — `user["profile"]["theme"]` crashes with `KeyError` if `"profile"` is missing. Use safe chained navigation: `(user.get("profile") or {}).get("theme", "light")`.
10. **Confusing `.get()` with `.setdefault()`** — `d.get("k", [])` only reads and returns `[]` without altering the dictionary; `d.setdefault("k", [])` actively inserts `"k": []` into `d`.

### 🤖 Sneak Peek: How Sets Power AI Agents & LangGraph (Phase 3)

1. **Cycle Detection & Visited State Tracking (`s.add()` / `in`):**
   In LangGraph workflows with conditional loops, agents can get caught in infinite reasoning loops.
   A `visited_states: set[str]` checks node IDs in $O(1)$ constant time, aborting or routing to fallback if a state repeats.
2. **RAG Context Deduplication (`set()` / `intersection`):**
   When retrieving document chunks from multiple indexes (e.g. hybrid dense vector search + keyword search),
   retrieved IDs often overlap. Taking the `intersection` (`dense_ids & keyword_ids`) isolates high-confidence consensus chunks.
3. **Incremental Ingestion via Difference (`all_docs - indexed_docs`):**
   When syncing knowledge bases, set difference (`all_ids - indexed_ids`) isolates only the brand-new documents
   that need embedding generation, preventing expensive duplicate API calls.

### Try it yourself
Build a dict `inventory = {"apples": 3, "pears": 5}`. Safely print the count of `"bananas"` as `0`
if absent, then add 2 bananas, then print all item→count pairs.
Then create a `frozenset` of your favorite AI tools and test if `"python"` is inside.

## ⚖️ Variations & When to Use (Dictionary & Set Efficiency Guide)

### Dictionary Operations

| Operation | Syntax | Mutates Original? | Time Cost (Avg) | ✅ When to Use | AI / LangGraph Application |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lookup / Set** | `d[k]` / `d[k] = v` | ✅ In-place (write) | $O(1)$ | Direct read/write when key is guaranteed | Reading known state keys e.g. `state["messages"]` |
| **Safe Read** | `d.get(k, default)` | ❌ Read-only | $O(1)$ | Reading optional keys without crashing | Reading optional hyperparameters: `cfg.get("seed", 42)` |
| **Read or Insert** | `d.setdefault(k, def)` | ✅ In-place (if missing) | $O(1)$ | Grouping items or initializing nested structures | Grouping messages by role or initializing node checkpoints |
| **Safe Pop** | `d.pop(k, default)` | ✅ In-place | $O(1)$ | Extracting and removing an optional key | Stripping API keys or internal tokens before logging |
| **Dict Merge** | `d1 \| d2` | ❌ New dict | $O(n+m)$ | Combining configs without mutating inputs | Merging default model config with user-supplied overrides |
| **Dict Update** | `d1 \|= d2` / `.update()` | ✅ In-place | $O(k)$ | Bulk applying new values in-place | Merging tool outputs directly into agent state |
| **Key Check** | `k in d` | ❌ Read-only | $O(1)$ | Fast constant-time existence guard | Checking if an embedding or response is cached |

### Set Operations

| Operation | Operator Syntax | Method Syntax | Mutates Original? | Time Cost (Avg) | ✅ When to Use | AI / LangGraph Application |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Add Single** | — | `s.add(x)` | ✅ In-place | $O(1)$ | Adding one hashable element | Recording a newly visited agent state or chunk ID |
| **Update Batch** | `s \|= other` | `s.update(iter)` | ✅ In-place | $O(k)$ | Adding many items in-place with deduplication | Ingesting a batch of doc IDs into a cache |
| **Discard (Safe)** | — | `s.discard(x)` | ✅ In-place | $O(1)$ | Removing an item when absence is acceptable (no error) | Dropping a tool from an active permissions pool |
| **Remove (Strict)** | — | `s.remove(x)` | ✅ In-place | $O(1)$ | Removing an item that *must* exist (raises `KeyError`) | Strict state machines where missing ID is a bug |
| **Pop Arbitrary** | — | `s.pop()` | ✅ In-place | $O(1)$ | Removing any item when order is completely irrelevant | Draining an unvisited web-crawler URL queue |
| **Clear All** | — | `s.clear()` | ✅ In-place | $O(n)$ | Emptying set while keeping same memory object | Resetting state between agent sessions |
| **Union** | `s1 \| s2` | `s1.union(iter)` | ❌ New set | $O(n+m)$ | Combining all unique items across two collections | Merging tools or tags from parallel agent branches |
| **Intersection** | `s1 & s2` | `s1.intersection(iter)` | ❌ New set | $O(\min(n, m))$ | **Keeping only duplicates/overlaps** present in both | Finding document IDs agreed upon by both Dense & BM25 search |
| **Difference** | `s1 - s2` | `s1.difference(iter)` | ❌ New set | $O(n)$ | Items in first set that are NOT in the second | Finding un-embedded documents: `all_docs - indexed_docs` |
| **Symmetric Diff** | `s1 ^ s2` | `s1.symmetric_difference(iter)` | ❌ New set | $O(n+m)$ | Items in either set, but **not in both** (exclusive items) | Detecting configuration drift between two agent versions |
| **Membership** | `x in s` | — | ❌ Read-only | $O(1)$ | Checking presence in constant time | Fast duplicate check before invoking an expensive LLM |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `KeyError: 'email'` | `d["email"]` on a missing key | Use `d.get("email")` or `d.get("email", default)` |
| `KeyError: 'profile'` on nested access | Intermediate dictionary key is missing | Use safe navigation: `(user.get("profile") or {}).get("theme", "light")` |
| `AttributeError: 'NoneType' object has no attribute 'get'` | Chained `.get()` failed because intermediate key exists with value `None` | Use `(d.get("key") or {}).get("sub_key", default)` |
| `TypeError: unhashable type: 'list'` | Used list as dict key/set item, or tried `s.add([1, 2])` | Use tuple for keys, or `s.update([1, 2])` to add multiple items |
| `TypeError: unhashable type: 'set'` | Used a mutable set as a dict key or inside a set | Use an immutable `frozenset(my_set)` |
| `TypeError: 'set' object is not subscriptable` | `myset[0]` — sets aren't ordered | Convert to a list (`list(myset)[0]`) if you need indexing |
| `s = {}` creates a dict, not a set | `{}` literal syntax is reserved for empty dicts | Use `s = set()` to create an empty set |
| `TypeError: unsupported operand type(s) for +: 'set' and 'set'` | Used `+` to merge sets | Use `s1 \| s2` (new set) or `s1.update(s2)` / `s1 \|= s2` (in-place) |
| `KeyError: 'chunk_99'` on `s.remove()` | Item does not exist in set | Use `s.discard("chunk_99")` to remove without errors |
| `KeyError: 'pop from an empty set'` | Called `s.pop()` on an empty set | Check `if s:` before calling `.pop()` |
| `TypeError: unsupported operand type(s) for &: 'set' and 'list'` | Operator used with non-set | Convert non-set to set (`s & set(lst)`) or use method `s.intersection(lst)` |
| Loop gives keys, not values | `for x in d:` yields **keys** | Use `d.items()` (pairs) or `d.values()` |

## 📌 Quick Reference

```python
# Dicts — Lookup, Mutation & Merging
d = {"a": 1}; d["b"] = 2; d.get("z", 0); d.update({"c": 3}); d.pop("a", None)
val = d.setdefault("tags", []).append("ai")  # inserts 'tags': [] if missing, then appends
merged = d1 | d2                             # merge into new dict (Python 3.9+)
d1 |= d2                                     # in-place dict merge
safe_val = (user.get("meta") or {}).get("theme", "dark")  # safe nested lookup
for k, v in d.items(): ...

# Sets — Creation & Mutation
s = {1, 2}; s.add(3); s.discard(1); 3 in s
s.update([3, 4, 4, 5])             # in-place unpack & collapse duplicates -> {..., 3, 4, 5}
s.remove(x)                        # removes x (KeyError if missing); s.discard(x) ignores missing
s.pop()                            # removes and returns an arbitrary item (unordered!)
s.clear()                          # empties set in-place -> set()
empty_s = set()                    # empty set (NOTE: {} creates an empty dict!)
set("banana")                      # {'b', 'a', 'n'} (from string)
list(set(items))                   # deduplicate a list or tuple

# Sets — Algebra (Returns brand-new set)
a | b                              # union (combines all unique elements)
a & b                              # intersection (keeps ONLY common duplicates/overlap)
a - b                              # difference (items in a but not in b)
a ^ b                              # symmetric difference (items in either, but NOT both)

# Sets — In-Place Algebra
a |= b; a &= b; a -= b; a ^= b

# Frozenset (Immutable & Hashable)
fs = frozenset([1, 2])             # valid dict key or set item

# Objects in Collections
# Dict values: any object; Dict keys & Sets: require hashable objects
# @dataclass(frozen=True) collapses duplicates in sets by value (default class hashes by id)
```

## 🛑 STOP — Self-Check

Why might you choose `.get("age")` over `["age"]`, and what does each do when the key is missing?

<details><summary>Answer</summary>

Both read a value by key when it exists. The difference is the **missing-key behaviour**:
`person["age"]` raises a **`KeyError`** (crashes) if `"age"` isn't there, while
`person.get("age")` returns **`None`** (or a default you pass, e.g. `.get("age", 0)`). Use `.get`
when a key is optional and you'd rather handle absence gracefully than crash.
</details>
