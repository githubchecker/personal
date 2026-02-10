# Index Basics

Here is the comprehensive **Beginner to Expert** guide to **Indexes** in SQL Server. This is the #1 concept to master for performance tuning.

---

# 📘 Phase 1: The Foundation (Analogy)

### The Textbook Analogy

Imagine a Phone Book containing 1,000,000 names.

1. **No Index (Heap):**
    - If the names are written in random order, to find "Zack," you must read **every single line** from page 1 to the end.
    - **SQL Term:** Table Scan (🐢 Very Slow).
2. **Clustered Index:**
    - The phone book *data itself* is physically sorted alphabetically A-Z. To find "Zack," you flip straight to the 'Z' section.
    - **SQL Term:** Clustered Index Seek (🚀 Fast).
3. **Non-Clustered Index:**
    - At the back of the book, there is a separate list: "List of Phone Numbers by Street Name." It gives you the page number where the person lives.
    - **SQL Term:** Non-Clustered Index (🚗 Fast, but extra step).

---

# ⚔️ Phase 2: The Two Titans (Clustered vs. Non-Clustered)

### 1. Clustered Index (The Skeleton)

- **Definition:** It stores the **actual data rows** sorted by the Key column.
- **Limit:** Max **1** per table (Because data can only be physically sorted in one order).
- **Behavior:**
    - When you create a **Primary Key**, SQL Server automatically creates a Clustered Index on that column (unless you specify otherwise).
    - The "Leaf Node" of this index **IS** the data page.

```sql
-- Data is now physically saved on disk sorted by EmployeeID
CREATE CLUSTERED INDEX IX_EmployeeID ON Employees(EmployeeID);

```

### 2. Non-Clustered Index (The Map)

- **Definition:** A separate physical structure containing the Index Key and a **Pointer** to the row in the Clustered Index.
- **Limit:** You can have up to **999** per table (SQL 2008+).
- **Behavior:**
    - Used for finding data by columns other than the Primary Key (e.g., `LastName`, `Email`).
    - The "Leaf Node" is a **pointer**.

```sql
-- A separate list sorted by LastName
CREATE NONCLUSTERED INDEX IX_LastName ON Employees(LastName);

```

---

# 🧠 Phase 3: Internals (B-Tree Structure)

SQL Server uses a **Balanced Tree (B-Tree)** structure to navigate data efficiently.

### The Tree Structure

1. **Root Node:** The entry point. "Are you looking for A-M or N-Z?"
2. **Intermediate Levels:** Narrows it down. "Are you looking for N-R or S-Z?"
3. **Leaf Nodes:** The destination.
    - **In Clustered:** The actual data row (`SELECT *`).
    - **In Non-Clustered:** The Primary Key ID (e.g., ID 501).

### The "Key Lookup" (The Silent Killer) 🩸

If you search using a Non-Clustered Index, but you ask for columns *not* in that index, SQL has to jump:

1. Index seeks to find `LastName = 'Smith'`. Finds `ID = 501`.
2. **Jump** to Clustered Index using `ID = 501` to get the `Address` column.
- *Cost:* This "Jump" (Key Lookup) is expensive. If you do it for 1,000 rows, it kills performance.

---

# 🛡️ Phase 4: Optimization Techniques (Expert)

### 1. Covering Index (`INCLUDE`)

To fix the "Key Lookup" cost, you can store extra data in the leaf level of the non-clustered index without sorting by it.

**Scenario:** `SELECT Address FROM Employees WHERE LastName = 'Smith'`

**Without Include:**

1. Find Smith (Non-Clustered).
2. Jump to Clustered to get Address (Expensive).

**With Include:**

```sql
CREATE NONCLUSTERED INDEX IX_LastName_Includes
ON Employees(LastName)
INCLUDE (Address); -- 🟢 Stored directly in the index leaf!

```

1. Find Smith.
2. `Address` is sitting right there. **No Jump needed.** This is a **Covered Query**.

### 2. Filtered Index

Why index NULLs or archived data if you never query them?
**Definition:** An index with a `WHERE` clause. Saves storage space and maintenance cost.

```sql
CREATE NONCLUSTERED INDEX IX_ActiveUsers
ON Users(Email)
WHERE IsActive = 1; -- 🟢 Only indexes active users

```

### 3. Columnstore Index (Analytic Powerhouse)

Introduced in newer SQL versions (2012+).

- **Format:** Stores data **Vertically** (by column) instead of Horizontally (by row).
- **Use Case:** Data Warehousing. Aggregating millions of rows (`SUM`, `AVG`).
- **Compression:** Massive (10x compression).

---

# 🏗️ Phase 5: Operations & Maintenance

### 1. Seek vs. Scan (How to read the Plan)

When looking at an Execution Plan:

- 🟢 **Index Seek:** SQL went directly to the specific row. (Sniper shot).
- 🔴 **Index Scan:** SQL read the entire index from start to finish because the index wasn't helpful enough or the query was non-sargable (e.g., `WHERE Name LIKE '%Bob'`).
- 🔴 **Table Scan:** SQL read the whole raw table (Heap). No index existed.

### 2. The "Write Penalty"

Every index you add speeds up `SELECT` but slows down `INSERT/UPDATE/DELETE`.

- Why? Because when you `INSERT` a row, SQL has to write to the table **AND** update every single Non-Clustered index.
- **Balance:** Don't over-index.

### 3. Fragmentation & Fill Factor

As you insert/delete, pages get messy (split).

- **Reorganize:** Lightweight cleanup (defrags leaf level). Use when fragmentation is 5-30%.
- **Rebuild:** Nuclear option. Drops and recreates the index fresh. Use when > 30%.
- **Fill Factor:** A setting (0-100) that tells SQL to leave empty space on index pages to accommodate future inserts without splitting pages. (Standard practice: 80-90 for dynamic tables).

---

# 📝 Phase 6: Index Strategy Cheat Sheet

| Query Type | Recommended Index |
| --- | --- |
| `WHERE ID = 5` (PK) | **Clustered Index** (Default) |
| `WHERE Name = 'Bob'` | **Non-Clustered Index** on Name |
| `WHERE Name = 'Bob'` and select Address | **Non-Clustered** on Name **INCLUDE** (Address) |
| `WHERE Date > '2020'` (Range) | **Clustered** (Best for ranges) or Non-Clustered |
| `WHERE IsActive = 1 AND Type = 'Admin'` | **Filtered Index** (If highly selective) |
| Report: `SUM(Sales) GROUP BY Year` | **Columnstore Index** |

### 💡 Final Expert Tip: SARGable Queries

An index is useless if your query is not **SARGable** (Search ARGument able).

- **Bad (Index Scan):** `WHERE YEAR(OrderDate) = 2023`
    - SQL has to run the function `YEAR()` on every row to check.
- **Good (Index Seek):** `WHERE OrderDate >= '2023-01-01' AND OrderDate < '2024-01-01'`
    - SQL can look at the raw index data range directly.