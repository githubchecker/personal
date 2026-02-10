# UNION vs UNION ALL

Here is the comprehensive breakdown of **UNION** vs **UNION ALL** in SQL Server. These are "Set Operators" used to combine results from two different SELECT statements into a single result set vertically.

---

# ⚔️ The Quick Comparison

| Feature | UNION (The Filter) | UNION ALL (The Aggregator) |
| --- | --- | --- |
| **Duplicates** | 🛑 **Removes** Duplicate Rows | 🟢 **Keeps** All Rows (including duplicates) |
| **Sorting** | 🟡 Implicitly sorts (to find dupes) | 🟢 No sorting (Appends data as-is) |
| **Performance** | 🔴 Slower (High CPU cost) | 🟢 Faster (Minimal Cost) |
| **Usage** | When unique distinct list is needed | When total count or raw data is needed |

---

# ➕ 1. UNION ALL (The Speed King)

`UNION ALL` simply takes the result of Query A and pastes the result of Query B directly underneath it.

- **Behavior**
    - It does **not** check if the data already exists.
    - It does **not** re-arrange the order of rows.
- **Performance (Internals)**
    - In the Execution Plan, this uses a simple **Concatenation** operator.
    - **Cost:** Extremely low. It effectively streams rows from both inputs to the output.

**Example Logic:**

- List A: `[Red, Blue]`
- List B: `[Blue, Green]`
- **UNION ALL Result:** `[Red, Blue, Blue, Green]`

---

# 🧹 2. UNION (The Cleaner)

`UNION` combines the lists but performs a cleanup operation to ensure no row appears twice.

- **Behavior**
    - It compares every row from Query A against Query B.
    - If a row is identical (all columns match), it is discarded.
- **Performance (Internals)**
    - In the Execution Plan, this requires a **Distinct Sort** or **Hash Match** operation.
    - **Cost:** Higher CPU and Memory usage.
    - *Warning:* On massive datasets (millions of rows), converting a `UNION ALL` to a `UNION` can degrade performance from milliseconds to minutes.

**Example Logic:**

- List A: `[Red, Blue]`
- List B: `[Blue, Green]`
- **UNION Result:** `[Red, Blue, Green]` (Second 'Blue' is removed)

---

# 📋 3. Strict Requirements (The Rules)

For either of these to work, three rules must be met:

- **1. Column Count**
    - Both queries must return the **exact same number** of columns.
        - *Invalid:* `SELECT Id FROM A` UNION `SELECT Id, Name FROM B`
- **2. Data Types**
    - Corresponding columns must have **compatible** data types.
        - *Valid:* `INT` vs `BIGINT` (Implicit conversion works).
        - *Invalid:* `INT` vs `GUID` (Error).
- **3. Column Names**
    - The column names in the Final Result set are taken from the **first** SELECT statement.
- **4. Sorting**
    - `ORDER BY` cannot be used inside the individual queries. It can only be used once at the very **end**.

---

# 💻 Phase 4: Practical Code Examples

Let's assume we have two tables: `Customers_USA` and `Customers_EU`.

### A. The Setup

- **USA Table:** { 'Alice', 'Bob' }
- **EU Table:** { 'Bob', 'Charlie' }
- *(Note: 'Bob' is in both tables)*

### B. Using UNION ALL (Preserve Duplicates)

```sql
SELECT Name FROM Customers_USA
UNION ALL
SELECT Name FROM Customers_EU;

```

**Result:**

1. Alice
2. Bob
3. Bob (Duplicate preserved)
4. Charlie

### C. Using UNION (Remove Duplicates)

```sql
SELECT Name FROM Customers_USA
UNION
SELECT Name FROM Customers_EU;

```

**Result:**

1. Alice
2. Bob (Unique)
3. Charlie

### D. Correct usage of ORDER BY

```sql
-- ❌ Wrong
SELECT Name FROM USA ORDER BY Name
UNION ALL
SELECT Name FROM EU;

-- ✅ Correct
SELECT Name FROM USA
UNION ALL
SELECT Name FROM EU
ORDER BY Name; -- Applies to the merged result

```

---

# 🧠 Phase 5: Expert Tips

### 1. The "Performance Trap"

Developers often lazily use `UNION` because "it looks cleaner" or they just want the list.

- **Best Practice:** Always default to **UNION ALL**.
- **Reason:** Only switch to `UNION` if you effectively *require* distinct values. Why pay the "Sorting Tax" if you don't need to?

### 2. Identifying the Source

Since `UNION` merges data, you often lose track of which table the data came from. A common pattern is adding a custom column:

```sql
SELECT Id, Name, 'USA' AS Source FROM Customers_USA
UNION ALL
SELECT Id, Name, 'Europe' AS Source FROM Customers_EU

```

### 3. INTERSECT and EXCEPT

While `UNION` adds rows, these related operators reduce them:

- **UNION:** A + B
- **INTERSECT:** Rows that exist in **Both** A and B.
- **EXCEPT:** Rows in A that are **Not** in B.