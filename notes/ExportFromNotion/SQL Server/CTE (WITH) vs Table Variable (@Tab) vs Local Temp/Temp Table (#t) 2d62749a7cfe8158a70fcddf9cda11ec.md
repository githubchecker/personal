# Temp Table (#t)

Here is the comprehensive **Beginner to Expert** guide to **Temporary Tables** in SQL Server.

---

# 📘 Phase 1: The Basics (What are they?)

**Definition:** A Temporary Table looks, acts, and feels exactly like a real physical table (Standard Table), but it lives in the **`tempdb`** system database and is automatically deleted when you are done with it.

### 1. The Syntax (Two ways to create)

There are two primary methods to spawn a Temp Table.

**Method A: Create & Fill (Explicit)**
Best for long scripts where you need to define data types strictly.

```sql
CREATE TABLE #UserStats (
    Id INT PRIMARY KEY,
    UserName VARCHAR(50),
    LoginCount INT
);

INSERT INTO #UserStats (Id, UserName, LoginCount)
SELECT Id, Name, Logins FROM Users;

```

**Method B: SELECT INTO (Implicit)**
Best for speed and ad-hoc analysis. SQL creates the structure automatically based on the source columns.

```sql
SELECT Id, Name, Logins
INTO #UserStats
FROM Users
WHERE Logins > 100;

```

---

# 📑 Phase 2: Local vs. Global (The Syntax Difference)

The number of hash symbols (`#`) determines who can see the table.

### 1. Local Temp Tables (`#MyTable`)

- **Symbol:** Single Hash `#`
- **Visibility:**
    - Visible to the **Current Session** (Connection) that created it.
    - Visible to any **Child Stored Procedure** called by that session.
- **Lifecycle:** Automatically dropped when the Session closes or the SP finishes.
- **Usage:** 99% of your work will use this.

### 2. Global Temp Tables (`##MyTable`)

- **Symbol:** Double Hash `##`
- **Visibility:** Visible to **ALL users** and **ALL sessions** on the server.
- **Lifecycle:** Dropped when the creator disconnects **AND** no other sessions are actively referencing it.
- **Usage:** Extremely rare. Used for sharing data between separate applications or rapid troubleshooting across connections.

---

# 🚀 Phase 3: Performance Features (Why use them?)

Temp tables are heavy machinery compared to Variables (`@Table`), but they are smarter.

### 1. Statistics (The Superpower)

Unlike Table Variables (which SQL guesses have 1 row), **Temp Tables have full Statistics (Histograms).**

- **Why it matters:** If you put 1,000,000 rows into a Temp Table, the SQL Optimizer *knows* there are 1M rows. It will choose a smart execution plan (like Hash Match).
- **Result:** Temp Tables are usually much faster for large datasets.

### 2. Indexes

You can add indexes to Temp Tables just like real tables to speed up joins.

```sql
CREATE TABLE #Orders (OrderId INT, Amount MONEY);
-- Boost performance for later Joins
CREATE CLUSTERED INDEX IX_TempOrders ON #Orders(OrderId);

```

---

# 🕵️ Phase 4: Internals (Expert Details)

### 1. Naming Collisions (Under the Hood)

If you create `CREATE TABLE #Data`, and your colleague also runs `CREATE TABLE #Data` at the same time, they do **not** conflict.

- **How?** inside `tempdb`, SQL Server renames them systematically:
    - Your Table: `#Data________________________________0000000001`
    - Colleague: `#Data________________________________0000000002`
- This is why strict naming conventions for temp tables aren't strictly necessary for safety (only for readability).

### 2. Transaction Logs

- **Myth:** "Temp Tables are in RAM so they are not logged."
- **Fact:** Temp tables **are** logged in the `tempdb` Transaction Log.
    - However, they function in `SIMPLE` recovery mode automatically.
    - They log enough to support `ROLLBACK`, but they do not log enough to support Database Recovery (Redo), making them faster than permanent tables.

### 3. Temp Table Caching

This is a high-level performance tweak SQL Server does automatically.

- If you create a Temp Table inside a Stored Procedure, SQL Server might **not** actually drop the object when the SP finishes.
- Instead, it "truncates" the data and keeps the empty shell (metadata) cached.
- Next time you call the SP, it reuses the shell instead of creating a new object from scratch (reducing CPU load).
- **Constraint:** If you perform DDL on the temp table (like adding columns/indexes *after* creation), Caching is disabled. *Best practice: Define all indexes inside the `CREATE TABLE` syntax (SQL 2014+).*

---

# 🛑 Phase 5: Common Pitfalls & Recompilation

### 1. The "Recompilation" Issue

When you create a Temp Table inside an SP, SQL Server sometimes has to pause and "Recompile" the execution plan because the schema has changed during the execution.

- **Performance Hit:** Frequent recompiles increase CPU.
- **Solution:** Table Variables (`@Tab`) do not cause recompilation. If the dataset is small (<100 rows), switch to a Table Variable.

### 2. Deferred Name Resolution

You can write an SP that references a `#Table` that doesn't exist yet.

```sql
CREATE PROC dbo.MyProc AS
BEGIN
   -- #Stats doesn't exist yet, but this compiles fine!
   SELECT * FROM #Stats;
END

```

This works because checks for Temp Tables are delayed until Runtime.

---

# 💡 Phase 6: Best Practice Summary

1. **Scope Passing:**
    - If `Parent SP` creates `#Tab`, then `Child SP` can see and modify `#Tab`. This is the standard way to pass massive datasets between procedures without using input parameters.
2. **Explicit Drop:**
    - SQL drops local temp tables automatically, but it is considered professional coding style to explicitly drop them at the end of your script to free up `tempdb` resources immediately.
    
    ```sql
    IF OBJECT_ID('tempdb..#MyTable') IS NOT NULL
        DROP TABLE #MyTable;
    
    ```
    
3. **Choose Wisely:**
    - **< 100 Rows:** Use Table Variable `@Tab` (Memory efficient, no recompiles).
    - **> 100 Rows:** Use Temp Table `#Tab` (Statistics allow for better Index usage and Query Plans).
    - **Need Transaction Rollback?** Use `#Tab` (It respects rollback). Table variables do not.