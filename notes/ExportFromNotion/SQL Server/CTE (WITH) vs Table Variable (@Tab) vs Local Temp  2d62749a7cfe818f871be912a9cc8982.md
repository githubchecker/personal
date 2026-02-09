# CTE (WITH)	vs Table Variable (@Tab) vs Local Temp (#Tab) vs Global Temp (##Tab)

Here is the definitive guide to Temporary Data structures in SQL Server. This decision is one of the most common performance bottlenecks in SQL development.

---

# 🏆 The Comparison Matrix

| Feature | **CTE** (`WITH`) | **Table Variable** (`@Tab`) | **Local Temp** (`#Tab`) | **Global Temp** (`##Tab`) |
| --- | --- | --- | --- | --- |
| **Object Type** | Logical View (Code Alias) | Variable | Physical Table | Physical Table |
| **Location** | Memory (Query Only) | `tempdb` | `tempdb` | `tempdb` |
| **Scope/Life** | Next Statement **Only** | Current Batch | Current Session | All Sessions (Until disconnected) |
| **Statistics** | Derived from Base Table | 🔴 None (Always est. 1 row) | 🟢 Full Histograms | 🟢 Full Histograms |
| **Indexing** | 🔴 None | 🟡 PK / Unique Only | 🟢 Fully Indexable | 🟢 Fully Indexable |
| **Transaction** | Part of Query Trans | 🔴 **Cannot Rollback** | 🟢 Rolls back | 🟢 Rolls back |

---

# 📑 1. Common Table Expression (CTE)

**Concept:** A "Disposable View". It is not data stored in a table; it is just a named query that SQL Server expands inline when running.

### Details

- **Syntax:** `WITH MyCTE AS (SELECT...) SELECT * FROM MyCTE`
- **Performance:**
    - It does **not** persist data. If you query a CTE twice, it runs the underlying logic twice.
    - **The Optimizer:** Treats it exactly like a subquery/view. It uses the statistics of the underlying real tables.
- **Recursive Power:** The **only** one in this list that can call itself (great for Hierarchies/Org Charts).

**Use When:**

- You need to break a complex query into readable chunks.
- You need Recursion.
- You only need the result **once**.

---

# 📦 2. Table Variable (`DECLARE @t`)

**Concept:** A structure that holds data like a table but behaves like a local variable (`int`, `varchar`).

### Details

- **Syntax:** `DECLARE @MyTable TABLE (Id INT)`
- **Storage Myth:** Many believe this lives in RAM. **False.** It lives in `tempdb`, just like Temp Tables.
- **The Fatal Flaw (Cardinality):**
    - SQL Server **does not maintain statistics** for Table Variables.
    - The Optimizer assumes the table has **1 Row**, regardless of whether it has 10 or 10 million.
    - *Result:* Bad execution plans for large datasets (e.g., doing a Nested Loop join instead of a Hash Join).
- **Transaction Behavior (Expert Tip):**
    - They are **NOT affected by Rollbacks**.
    - If you `BEGIN TRAN`, Insert into `@Table`, then `ROLLBACK`, the data in `@Table` **stays**. This is excellent for logging errors during a rollback scenario.

**Use When:**

- You have very small data (< 100 rows).
- You need to save data *past* a Transaction Rollback (e.g., Logging error details).
- You cannot lock data (Table Variables rarely participate in locking).

---

# 📄 3. Local Temporary Table (`CREATE #t`)

**Concept:** A physical table created in `tempdb` with a scope limited to the current connection (Session).

### Details

- **Syntax:** `CREATE TABLE #MyTable` or `SELECT * INTO #MyTable`
- **Suffix:** SQL Server automatically appends a suffix (e.g., `#MyTable____0000001`) internally to distinguish it from other users' temp tables.
- **Scope & Nesting:**
    - Visible to the **Current Session**.
    - Visible to **Child Stored Procedures** (if Parent creates `#Tab`, Child calls can read/write it).
    - Deleted automatically when the session closes or the SP finishes.
- **Performance:**
    - Maintains **Full Statistics**.
    - Supports `CREATE INDEX` after population.
    - Better for large datasets than Table Variables.
- **The Downside:**
    - Creating them inside a Stored Procedure can cause **Recompilation** of that SP (SQL has to pause to understand the new table structure).

**Use When:**

- You have > 100 rows of intermediate data.
- You need to add Indexes to improve performance.
- You are passing data "down" to Child SPs.

---

# 🌍 4. Global Temporary Table (`CREATE ##t`)

**Concept:** A physical table in `tempdb` visible to **everyone** on the server.

### Details

- **Syntax:** `CREATE TABLE ##MyGlobalTable` (Two hashes).
- **Scope:**
    - Shared across **all users** and **all sessions**.
    - **Death:** Dropped only when:
        1. The session that created it disconnects.
        2. **AND** no other sessions are currently querying it.
- **Concurrency Issues:**
    - Since everyone sees it, locking becomes a nightmare. If User A locks `##Table` for an update, User B is blocked.

**Use When:**

- **Rarely.**
- Integration scenarios: You have a C# App uploading data and a separate Reporting Job needs to grab that specific cached dataset immediately.
- Troubleshooting: Sharing a result set with a colleague instantly without creating a permanent table.

---

# 🔮 Expert Summary: Which one to pick?

1. **Readability / One-time use?**
    - 👉 **CTE**. Don't create storage if you just need to organize code.
2. **Less than 100 Rows?**
    - 👉 **Table Variable** (`@t`). Fast, cleans up instantly, no locking overhead.
3. **More than 100 Rows / Complex Joins?**
    - 👉 **Local Temp Table** (`#t`). You need the Statistics and Indexes for speed.
4. **Need data to survive a `ROLLBACK`?**
    - 👉 **Table Variable**. The only survivor.
5. **Need to pass data *out* of an SP to a Parent SP?**
    - 👉 **Local Temp Table**. Parent creates `#t`, calls Child, Child fills `#t`. (Table variables can't move between SPs unless passed as `READONLY` parameters).

[CTE](CTE%20(WITH)%20vs%20Table%20Variable%20(@Tab)%20vs%20Local%20Temp%20/CTE%202d62749a7cfe81759c18d4e53184b62d.md)

[Temp Table (#t)](CTE%20(WITH)%20vs%20Table%20Variable%20(@Tab)%20vs%20Local%20Temp%20/Temp%20Table%20(#t)%202d62749a7cfe8158a70fcddf9cda11ec.md)

[Data Passing SP to SP/UDF](CTE%20(WITH)%20vs%20Table%20Variable%20(@Tab)%20vs%20Local%20Temp%20/Data%20Passing%20SP%20to%20SP%20UDF%202d62749a7cfe81a7be04c0e8f548d433.md)