# Performace Tunning

This is the "Expert Level" workflow for identifying bottlenecks in a Production environment and designing the perfect Index to fix them.

---

# 🕵️ Phase 1: Identification (Finding the Culprit)

In Production, you cannot just guess. You need hard evidence. Here are the 4 ways to find slow queries, ranked from "Quick check" to "Deep Analysis".

### 1. The "Right Now" Check (`sp_WhoIsActive`)

If the server is slow **currently**, don't use standard Activity Monitor. Use Adam Machanic's community-standard stored procedure: **`sp_WhoIsActive`**.

- **What it does:** Shows exactly what is running, how long it has been running, and **which SQL statement inside the SP** is stuck.
- **Action:** Look at the `sql_text` and `wait_info` columns.

### 2. The "Time Machine" (Query Store) 🏆

*Available in SQL 2016+ (Standard/Enterprise).*
This is the **Best Practice** tool.

- **How to access:** SSMS > Database > Query Store > **Top Resource Consuming Queries**.
- **Metric to check:** Switch view to "Total Duration" or "Total CPU".
- **Why it's king:** It keeps history. You can see a query that was fast yesterday but is slow today (Plan Regression).

### 3. The "Dmvs" (Dynamic Management Views)

If you don't have Query Store or 3rd party tools, query the server's memory directly.

**The "Top 10 Expensive Queries" Script:**

```sql
SELECT TOP 10
    SUBSTRING(t.text, (qs.statement_start_offset/2)+1,
        ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(t.text)
        ELSE qs.statement_end_offset END - qs.statement_start_offset)/2) + 1) AS StatementText,
    qs.total_worker_time AS TotalCPU,
    qs.total_logical_reads AS TotalReads, -- 💡 High Reads = Index Opportunity
    qs.execution_count,
    qp.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) t
CROSS APPLY sys.dm_exec_query_plan(qs.plan_handle) qp
ORDER BY qs.total_worker_time DESC; -- OR ORDER BY qs.total_logical_reads DESC

```

- **Note:** If `TotalReads` is high but `execution_count` is low, that's your bottleneck.

---

# 🔬 Phase 2: Analysis (Reading the Map)

Once you have the slow Query, you must open the **Execution Plan**.

- *In SSMS:* Highlight query -> Right Click -> "Display Estimated Execution Plan" (or Ctrl+L).

### 1. The Warning Signs (Red Flags) 🚩

Look for these specific operators in the diagram:

- **Table Scan / Clustered Index Scan:**
    - *Meaning:* SQL is reading **every single row** in the table.
    - *Fix:* Needs a `WHERE` clause index.
- **Key Lookup (The Bridge):**
    - *Meaning:* SQL found the row in your Non-Clustered index, but the index didn't have all the columns needed (e.g., `SELECT *`), so it jumped back to the Clustered Index to fetch the rest.
    - *Fix:* Add the missing columns to the **`INCLUDE`** list of the index.
- **Sort / Hash Match (Spills):**
    - *Meaning:* SQL ran out of memory to do the join/sort and wrote data to the hard drive (`tempdb`). This is terribly slow.
    - *Fix:* Proper indexing on `JOIN` or `ORDER BY` columns to provide pre-sorted data.

### 2. Missing Index Hints (Green Text)

- Sometimes SSMS displays green text: *"Missing Index (Impact 98%)"*.
- **Expert Warning:** Do **NOT** blindly create these.
    - They are often incomplete.
    - They might suggest creating a new index that is almost identical to an existing one (Resulting in Duplicate Indexes).
    - *Use them as a hint, but design it yourself.*

---

# 🛠️ Phase 3: The Index Tuning Strategy

When designing an index to make a specific query fast, use the **E-S-R-I** Method.

### 1. Equality (=)

Columns used in exact matches go **First** in the Index Key.

- `WHERE UserID = 100`

### 2. Sort / Range (>, <, ORDER BY)

Columns used for Ranges or Sorting go **Second**.

- `WHERE Date > '2023-01-01'` or `ORDER BY CreatedDate`
- *Why?* Indexes are stored sorted. SQL can zoom to the Equality match, then just read down the list for the Range.

### 3. Return (The `INCLUDE`)

Columns that appear in the `SELECT` list but are not being filtered/sorted go in the **`INCLUDE`** section.

- This makes the index "Covering".

### 4. Inequality (<>)

Columns using `NOT EQUAL` usually cannot use indexes efficiently. Keep them out of the key if possible.

---

# 🚀 Phase 4: A Practical Example

**The Slow Query:**

```sql
SELECT Phone, Address
FROM Users
WHERE Department = 'IT'          -- Equality
  AND JoinDate > '2022-01-01'    -- Range
ORDER BY JoinDate;               -- Sort

```

**Step 1: Analyze Predicates**

- **Equality:** `Department`
- **Range/Sort:** `JoinDate`
- **Select (Payload):** `Phone`, `Address`

**Step 2: Designing the Wrong Index**

```sql
-- ❌ Bad Design
CREATE INDEX IX_Wrong ON Users(JoinDate, Department);

```

*Why?* The data is sorted by Date first.

1. SQL finds '2022-01-02'. Is Dept 'IT'? Maybe.
2. SQL finds '2022-01-03'. Is Dept 'IT'? Maybe.
3. It has to scan the whole date range checking Departments.

**Step 3: Designing the Right Index**

```sql
-- ✅ Correct Design (ESRI Method)
CREATE INDEX IX_Users_Dept_Join
ON Users(Department, JoinDate)   -- 1. Equality, 2. Range
INCLUDE (Phone, Address);        -- 3. The Payload (Covering)

```

*Why?* The data is sorted by Department first.

1. SQL zooms straight to the 'IT' section.
2. Inside 'IT', the dates are *already* sorted!
3. It grabs the range instantly.
4. It grabs Phone/Address from the `INCLUDE` without touching the table.
5. **Result:** Instant results.

---

# 🛑 Phase 5: Common Traps (Why Queries are still slow)

Even with an Index, the query might not use it. Here is why:

### 1. Implicit Conversions (Data Type Mismatch)

If your column is `VARCHAR` but your C# sends `NVARCHAR` (Unicode):

- `WHERE Phone = N'555-0100'`
- **Result:** SQL converts the *Table* data to match the parameter. It cannot use the Index. **Full Table Scan occurs.**
- *Fix:* Match data types strictly.

### 2. Functions on Columns (SARGability)

- **Bad:** `WHERE LEFT(Name, 3) = 'Bob'`
    - SQL must run `LEFT()` on every row. Index ignored.
- **Good:** `WHERE Name LIKE 'Bob%'`
    - SQL can use the Index.

### 3. Parameter Sniffing

If the query is fast for small dates but slow for large dates, the Cached Plan is optimized for the wrong dataset.

- *Fix:* Update Statistics or use `OPTION (RECOMPILE)`.

### 4. Stale Statistics

SQL thinks a table has 100 rows, but it actually has 1,000,000. It picks a "Nested Loop" join (good for small data) instead of a "Hash Match" (good for big data).

- *Fix:* `UPDATE STATISTICS TableName`.

---

# 📝 Summary Workflow

1. **Find It:** Use **Query Store** (History) or `sys.dm_exec_query_stats` (Current Cache).
2. **Explain It:** Look at Execution Plan for **Scans** and **Key Lookups**.
3. **Design It:** Put **Equality** columns first, **Range** second, **Select** cols in Include.
4. **Check It:** Watch out for Implicit Conversions and Function calls in WHERE clauses.

# Order of Index Matters?

This is one of the most important concepts in Database Design. If you understand **why** the order matters, you understand how B-Trees work.

Here is the deep dive into **Index Ordering, Compound Indexes, and the Left-Based Rule.**

---

# 📚 Part 1: Why `Department` had to go first?

In the previous example:

```sql
WHERE Department = 'IT'          -- Equality (=)
  AND JoinDate > '2022-01-01'    -- Range (>)
ORDER BY JoinDate;               -- Sort

```

The correct index was **`(Department, JoinDate)`**.
Here is the visual proof using actual data to explain why `(JoinDate, Department)` fails.

### ❌ Scenario A: Index on `(JoinDate, Department)`

Imagine the index looks like this on the hard drive (Sorted by Date first):

| JoinDate (Key 1) | Department (Key 2) |
| --- | --- |
| 2022-01-01 | Admin |
| 2022-01-01 | **IT** |
| 2022-01-01 | Sales |
| 2022-01-02 | **IT** |
| 2022-01-02 | Marketing |
| 2022-01-03 | **IT** |

**What SQL Server must do:**

1. **Seek:** It can jump to `2022-01-01`. Good.
2. **Filter:** It reads row 1 ('Admin'). Not 'IT'. Skip.
3. It reads row 2 ('IT'). Keep.
4. It reads row 3 ('Sales'). Skip.
5. **Result:** The 'IT' department is **scattered** randomly throughout the dates. SQL has to physically check every single row in the date range to find the 'IT' department.

### ✅ Scenario B: Index on `(Department, JoinDate)`

Imagine the index looks like this (Sorted by Department first):

| Department (Key 1) | JoinDate (Key 2) |
| --- | --- |
| Admin | 2022-01-01 |
| ... | ... |
| **IT** | **2022-01-01** |
| **IT** | **2022-01-02** |
| **IT** | **2022-01-03** |
| ... | ... |
| Sales | 2022-01-01 |

**What SQL Server must do:**

1. **Seek:** It jumps directly to the **'IT'** block.
2. **Logic:** Because the Index is sorted by `Dept`, then `Date`: **Inside the 'IT' block, the Dates are already sorted.**
3. **Action:** It grabs the continuous chunk of rows where Date > '2022-01-01'.
4. **Bonus:** The results are already sorted by `JoinDate`. **Zero sorting required.**

> The Golden Rule: Equality (=) supports the Range (>, <). If you put Range first, you break the grouping for the Equality.
> 

---

# 📉 Part 2: Should we use indexes for `ORDER BY`?

**YES.**

An `ORDER BY` clause is one of the most expensive operations in a database because sorting takes CPU and Memory (`SORT` operator).

If you have an index covering the column you want to sort by:

1. SQL Server doesn't need to sort.
2. It simply scans the index leaves (which are always physically sorted).
3. The execution plan shows a stream of data. The "Sort" cost is **0%**.

**Caveat:** The index order must match the sort order exactly (or be the exact reverse).

- Index: `(A, B)`
- Query: `ORDER BY A, B` -> **Free Sort**.
- Query: `ORDER BY B, A` -> **Index Cannot help** (Must manually sort).

---

# ⛓️ Part 3: The "Left-Based" Rule (Partial Key Usage)

You asked: *"Does part of the key not be used in Compound index?"*

This is known as the **Left-Most Prefix Rule**.

Imagine an Index on **`(Country, State, City)`**.

### What works (Index Seek)?

SQL can navigate the B-Tree efficiently if you provide:

1. `Country` (First column).
2. `Country` AND `State` (First and Second).
3. `Country` AND `State` AND `City` (All three).

### What fails (Index Scan)?

SQL **cannot** Seek (Jump) if you skip the leading column.

1. `WHERE City = 'New York'`
    - **Why:** 'New York' exists in the US, but maybe also in the UK? The index is sorted by Country first. SQL has to read the **Whole Index** (Scan) to find every 'New York'.
2. `WHERE State = 'California'`
    - **Why:** Without knowing the Country, 'California' is not at the start of the list.

### ❓ Can it be used partially?

**Technically, Yes, but purely for data retrieval, not for finding.**
If you have an Index on `(A, B)` and run `SELECT A, B FROM T WHERE B = 5`.

1. SQL cannot "Seek" (Jump) to `5` because `A` is missing.
2. **However**, SQL prefers to read this Non-Clustered Index (which is small) rather than the whole Table (which is huge).
3. This is called a **Non-Clustered Index SCAN**. It scans every leaf of the index. It is faster than a Table Scan, but slower than an Index Seek.

---

# 🧠 Expert Summary: The Order of Operations

When creating a Compound Index `(Col1, Col2, Col3)`, the effectiveness stops the moment you break the "ESRI" chain.

| Query `WHERE` clause | Index `(A, B, C)` usage | Why? |
| --- | --- | --- |
| `A=1` | **Seek** on A | Perfect start. |
| `A=1 AND B=2` | **Seek** on A, then B | Perfect chain. |
| `A=1 AND B>2 AND C=3` | **Seek** on A, then B | `B` is a Range/Inequality. The sort order for `C` is no longer guaranteed after a range. `C` becomes just a filter "residue". |
| `B=2` | **Scan** (Slow) | Leftmost column `A` is missing. |
| `A=1 ORDER BY B` | **Seek** A, Return Sorted | Logic matches index sort. |
| `A=1 ORDER BY C` | **Seek** A, then **Sort** (CPU) | We skipped B, so C is not sorted. |

### Conclusion for your interview/knowledge:

1. **Equality (=)** columns go first to "Group" the data.
2. **Range (>, <)** or **Order By** columns go next to utilize the sorted nature of that group.
3. If you put Range First, the Equality column is no longer grouped, forcing a Scan.