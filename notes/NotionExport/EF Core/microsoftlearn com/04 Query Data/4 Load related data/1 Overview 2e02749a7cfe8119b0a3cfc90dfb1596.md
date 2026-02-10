# 1. Overview

# Loading Related Data

EF Core provides three primary patterns for loading related entities through navigation properties. Choosing the right pattern is essential for balancing performance and convenience.

## 1. Eager Loading

Related data is loaded from the database as part of the **initial query**.

- **Mechanism:** Uses the `.Include()` and `.ThenInclude()` methods.
- **Result:** A single (or split) query retrieves everything at once.
- **Best For:** Most scenarios where you know exactly which related data you need.

## 2. Explicit Loading

Related data is loaded from the database **manually** at a later time.

- **Mechanism:** Uses the `Entry(...)` API (e.g., `context.Entry(blog).Collection(b => b.Posts).Load()`).
- **Result:** Separate round-trips to the database occur when requested.
- **Best For:** Scenarios where you only need related data conditionally based on logic.

## 3. Lazy Loading

Related data is loaded **automatically** the first time the navigation property is accessed.

- **Mechanism:** Requires proxies or special interfaces; generally disabled by default.
- **Result:** Transparent, on-demand loading.
- **Best For:** Complex object graphs where predicting usage is difficult.
- **Warning:** Can lead to the "N+1 query problem" if used inside loops.

## 4. Comparison Summary

| Pattern | Data Retrieved | Performance | Effort |
| --- | --- | --- | --- |
| **Eager** | Initial Query | High (Minimal roundtrips) | Manual (`Include`) |
| **Explicit** | On Demand | Moderate (Multiple roundtrips) | Manual (`Load`) |
| **Lazy** | On Property Access | Low (Risk of N+1) | Automatic |