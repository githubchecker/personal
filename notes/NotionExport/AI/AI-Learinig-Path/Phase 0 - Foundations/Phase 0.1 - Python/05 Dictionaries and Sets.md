# 05 — Dictionaries & Sets

> Phase 0 · Module 0.1 · Lesson 5 of 16

## 🗺️ Stage 0 — Concept Map

Lists store items by **position**. But often you want to look something up by **name** — a price
by product, a score by user. That's a **dictionary**, the most-used data structure in real Python.
A **set** is its cousin: an unordered bag of **unique** items. Both build on what you know and
power configuration, JSON data, and the `messages`/metadata you'll send to AI models.

## 🔑 New Terms (plain English)

- **Dictionary (dict)** — stores **key → value** pairs; you look things up by key.
- **Key** — the unique label you look up (must be immutable: str/int/tuple).
- **Value** — the data stored under a key (can be anything).
- **Set** — an unordered collection of **unique** items.
- **Membership** — testing whether something is present: `x in collection`.

## 🎈 Stage 1 — The Simple Idea (analogy: a real dictionary, and a bag of unique marbles)

A **dictionary (dict)** is like a word dictionary: you look up a **key** (the word) to get its
**value** (the definition). Lookups are by key, not position, and they're instant.

A **set** is a bag of marbles where duplicates are impossible — toss in two identical marbles and
only one remains. Order isn't tracked; membership is.

**The "Aha!":** dict = "look up a value by its key"; set = "a collection that automatically removes
duplicates and answers 'is this in here?' very fast."

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

### 5.4 Nesting (this is what JSON looks like)

```python
# Dicts hold lists and other dicts — exactly the shape of API/JSON data.
user = {
    "name": "Ada",
    "roles": ["admin", "editor"],          # a list value
    "address": {"city": "London", "zip": "EC1"},  # a dict value
}
print(user["roles"][0])            # 'admin'
print(user["address"]["city"])     # 'London'
```

### 5.5 Sets — unique, fast membership

```python
tags = {"python", "ai", "python"}   # duplicates collapse
print(tags)                          # {'python', 'ai'}  (order not guaranteed)

tags.add("ml")
tags.discard("ai")                   # remove if present (no error if absent)
print("ml" in tags)                  # True — membership is very fast

# Deduplicate a list instantly by converting to a set and back:
nums = [1, 2, 2, 3, 3, 3]
print(list(set(nums)))               # [1, 2, 3]

# Set algebra:
a = {1, 2, 3}
b = {3, 4}
print(a | b)   # union        {1, 2, 3, 4}
print(a & b)   # intersection {3}
print(a - b)   # difference   {1, 2}
```

**Why sets are fast:** checking `x in big_list` scans every item; `x in big_set` jumps almost
instantly regardless of size. For "have I seen this already?" checks, sets win.

## 🚀 Stage 3 — In Practice / Why It Matters

Dicts are the backbone of AI code: an LLM message is `{"role": "user", "content": "..."}`, API
responses are nested dicts, configuration is a dict. Sets are perfect for deduplicating retrieved
document IDs or tracking "which chunks have we already used."

**Common beginner mistakes (the reasoning):**
1. **`KeyError` from `dict[key]`** on a missing key — use `.get(key, default)` when a key might be
   absent. *Reason:* `[]` assumes the key exists; `.get` doesn't.
2. **Assuming dict iteration gives values** — `for x in d:` gives **keys**. Use `d.items()` for
   pairs or `d.values()` for values.
3. **Trying to use a list as a key** — keys must be immutable (str, int, tuple), not lists.
   *Reason:* a key's identity must be stable.
4. **Relying on set order** — sets are unordered; don't index them (`myset[0]` is an error).

### Try it yourself
Build a dict `inventory = {"apples": 3, "pears": 5}`. Safely print the count of `"bananas"` as `0`
if absent, then add 2 bananas, then print all item→count pairs.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `KeyError: 'email'` | `d["email"]` on a missing key | Use `d.get("email")` or `d.get("email", default)` |
| `TypeError: unhashable type: 'list'` | Used a list as a dict key / set item | Use an immutable key (str/int/tuple) |
| `TypeError: 'set' object is not subscriptable` | `myset[0]` — sets aren't ordered | Convert to a list if you need indexing |
| Loop gives keys, not values | `for x in d:` yields **keys** | Use `d.items()` (pairs) or `d.values()` |

## 📌 Quick Reference

```python
d = {"a": 1}
d["b"] = 2; d.get("z", 0); d.update({"c": 3}); d.pop("a")
for k, v in d.items(): ...
s = {1, 2}; s.add(3); s.discard(1); 3 in s
a | b      a & b      a - b        # union / intersection / difference
list(set(items))                   # deduplicate a list
```

## 🛑 STOP — Self-Check

Why might you choose `.get("age")` over `["age"]`, and what does each do when the key is missing?

<details><summary>Answer</summary>

Both read a value by key when it exists. The difference is the **missing-key behaviour**:
`person["age"]` raises a **`KeyError`** (crashes) if `"age"` isn't there, while
`person.get("age")` returns **`None`** (or a default you pass, e.g. `.get("age", 0)`). Use `.get`
when a key is optional and you'd rather handle absence gracefully than crash.
</details>
