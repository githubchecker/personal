# Functions [UDF]

Here is the comprehensive **Beginner to Expert** guide to **User-Defined Functions (UDF)** in SQL Server.

---

# 📘 Phase 1: The Basics (What & Why)

**Definition:** A Function is a saved logic routine that accepts parameters, performs a calculation, and **must return a value**.

- Think of it like a Helper Method in C# (`public int CalculateTax()`).
- Unlike Stored Procedures, Functions are designed for **computation**, not business logic flow.

### The 2 Iron Rules

1. **Must Return Value:** Every path of code must hit a `RETURN` statement.
2. **No Side Effects:** A function **cannot** change the database state.
    - ❌ No `INSERT`, `UPDATE`, `DELETE` on permanent tables.
    - ❌ No `RAND()` or `NEWID()` (Side-effecting generators).

---

# ⚙️ Phase 2: Scalar Functions (Single Value)

**Concept:** Returns a single value (Int, Varchar, Date, Money).

- **Syntax:** `CREATE FUNCTION dbo.Name ... RETURNS INT`

### Example

```sql
CREATE FUNCTION dbo.ufn_CalculateTax (@Amount MONEY)
RETURNS MONEY
WITH SCHEMABINDING -- Expert Tip: Helps performance slightly
AS
BEGIN
    DECLARE @Tax MONEY;
    SET @Tax = @Amount * 0.15;

    RETURN @Tax;
END

```

### ⚠️ The "RBAR" Performance Trap (Important!)

Scalar functions are notoriously slow when used in a `SELECT` list over millions of rows.

- **Behavior:** SQL Server forces execution **Row-By-Agonizing-Row (RBAR)**. It switches context between the SQL Engine and the Calculation Engine for every single row.
- **Modern Fix:** SQL Server 2019+ introduced "Scalar UDF Inlining" which fixes this automatically in many cases.

---

# 📑 Phase 3: Table-Valued Functions (TVF)

This is where the magic happens. There are two very different types of TVFs, and knowing the difference separates beginners from experts.

### 1. Inline TVF (The "Parameterized View") 🏆

This is the **High Performance** option. It contains a **single** `SELECT` statement.

- **Behavior:** The SQL Optimizer "pastes" the function's logic directly into the outer query. It does not look like a function to the engine; it looks like a subquery.
- **Syntax:** No `BEGIN/END` block. Just `RETURN SELECT`.

```sql
CREATE FUNCTION dbo.ufn_GetOrdersByDate_Inline (@OrderDate DATE)
RETURNS TABLE
AS
RETURN
(
    SELECT OrderId, CustomerId, TotalDue
    FROM Sales.Orders
    WHERE OrderDate = @OrderDate
);

```

### 2. Multi-Statement TVF (The "Black Box") 🐢

This acts like a Stored Procedure that outputs a table variable. It allows logic (`IF/ELSE`, Loops).

- **Behavior:** It creates a Table Variable (`@T`), fills it, and passes it back.
- **Performance Warning:** It is opaque to the Optimizer.
    - Legacy SQL assumes it returns **1 Row** (bad estimation).
    - Newer SQL (2014+) assumes **100 Rows** (better, but often wrong).
    - It generally prevents parallel execution.

```sql
CREATE FUNCTION dbo.ufn_GetOrders_Multi (@OrderDate DATE)
RETURNS @OutputTable TABLE (OrderId INT, Total MONEY) -- Defines structure
AS
BEGIN
    -- Logic Allowed!
    IF @OrderDate < '2000-01-01'
        INSERT INTO @OutputTable SELECT OrderId, TotalDue FROM Archives;
    ELSE
        INSERT INTO @OutputTable SELECT OrderId, TotalDue FROM Orders;

    RETURN;
END

```

---

# 🔗 Phase 4: Using `CROSS APPLY` (Advanced)

---

To join a Table to a Function (TVF), you cannot use a standard `INNER JOIN`. You must use `CROSS APPLY`.

**Scenario:** For every User, call the function `GetRecentOrders(User.Id)`.

```sql
SELECT
    U.UserName,
    Orders.OrderId,
    Orders.Total
FROM Users U
-- "Run this function for every row in U"
CROSS APPLY dbo.ufn_GetOrdersByDate_Inline(U.CreatedDate) AS Orders
WHERE U.Active = 1;

```

---

# 🛡️ Phase 5: Limitations & Workarounds (Expert)

### 1. The "Non-Deterministic" Ban

Functions are supposed to be consistent. You strictly **cannot** use `NEWID()` (Random GUID) inside a function because it changes every time.

- **Workaround:** Pass the `NEWID()` or random value in as a **Parameter** from the caller.

### 2. No `TRY...CATCH`

If a Function fails (e.g., Divide by Zero), the **entire statement** executing it crashes. You cannot catch errors internally.

- **Defense:** Use `NULLIF` (e.g., `a / NULLIF(b, 0)`).

### 3. Schema Binding

Use `WITH SCHEMABINDING` whenever possible.

- **Syntax:** `CREATE FUNCTION ... WITH SCHEMABINDING AS ...`
- **Effect:** Prevents users from Dropping or Altering tables that the function relies on. It also signals the optimizer that the underlying schema is stable, which can slightly boost performance.

---

# 💡 Phase 6: Expert Summary Recommendation

1. **Logic:**
    - If you need to change data (`INSERT/UPDATE`) -> **Stored Procedure**.
    - If you need to calculate a value -> **Scalar Function**.
    - If you need a result set based on a parameter -> **TVF**.
2. **Performance:**
    - Always try to use **Inline TVFs**. They are blazing fast.
    - Avoid **Multi-Statement TVFs** for large datasets; they are performance bottlenecks.
    - Be careful with **Scalar Functions** in the `WHERE` clause (prevents index usage).
3. **Modern SQL:**
    - If using SQL Server 2019 or later, enable database compatibility level 150 to get **FROID (Scalar UDF Inlining)**, which automatically fixes the slowness of many old Scalar Functions.

# ⚔️ Phase 7: Stored Procedures vs Functions

This is the definitive, deep-dive comparison between **Stored Procedures (SP)** and **User-Defined Functions (UDF)** in SQL Server.

---

# 🏆 The Master Comparison Matrix

| Feature | 🏛️ Stored Procedure (SP) | 🧮 User-Defined Function (UDF) |
| --- | --- | --- |
| **Primary Purpose** | **Execution Logic** (Do something, change state). | **Computation Logic** (Calculate and Return). |
| **How to Call** | `EXEC dbo.Name` (Standalone). | In `SELECT`, `WHERE`, `JOIN` (Part of Query). |
| **Return Data** | Multiple Result Sets, Integer (Status), Output Params. | **MUST** return a value (Scalar) or a Table. |
| **DML (Insert/Update)** | ✅ Allowed on any table. | ❌ **NOT** Allowed on database tables. |
| **DDL (Create/Drop)** | ✅ Allowed (Tables, Indexes). | ❌ **NOT** Allowed. |
| **Error Handling** | ✅ `TRY...CATCH` supported. | ❌ Not supported. Crash kills the query. |
| **Transactions** | ✅ `BEGIN/COMMIT/ROLLBACK` supported. | ❌ Not supported. |
| **Temp Storage** | ✅ `#TempTables` (Local) & `@Variables`. | ❌ `@Variables` only. No `#TempTables`. |
| **Dynamic SQL** | ✅ `sp_executesql` supported. | ❌ Not supported. |
| **Non-Deterministic** | ✅ Can use `NEWID()`, `RAND()`. | ❌ Banned (mostly). |
| **Calling** | Can call other SPs and UDFs. | Can call UDFs. **Cannot** call SPs. |

---

# 🛠️ 1. Invocation & Usage Scenarios

### Stored Procedure

- **Independent Batch:** An SP runs as an independent "batch" of work.
- **Call Method:** Requires the `EXECUTE` command.
- **Chaining:** Can be executed via `INSERT INTO ... EXEC`.
- **Scenario:** Process an order, update inventory, validate a user, clean up old data.

### Function

- **Expression Dependent:** A UDF is executed **inline** as part of a larger SQL Statement.
- **Call Method:** Used in `SELECT`, `WHERE`, `HAVING`, or `FROM` clauses (with `CROSS APPLY`).
- **Scenario:** Format a date, split a string, calculate tax based on an amount, filter rows based on complex logic.

---

# ⚡ 2. Performance & Optimization (Internals)

This is the biggest differentiator for Experts.

### Stored Procedure

- **Plan Caching:** When run, SQL Server calculates an "Execution Plan" and caches it.
- **Parameter Sniffing:** It "sniffs" the inputs of the first run to build the plan. This is usually efficient but can sometimes cause performance issues if data distribution varies wildly.

### Function (Three Types, Three Behaviors)

1. **Scalar UDF (Returns single value):**
    - 🔴 **Slow (RBAR):** By default, runs "Row By Row." If you Select 1M rows, the function executes 1M distinct times.
    - *Note:* SQL Server 2019+ attempts to "Inline" these automatically to fix performance.
2. **Multi-Statement TVF (Returns @Table):**
    - 🔴 **Opaque:** The SQL Optimizer cannot see inside the logic. It assumes the function returns very few rows (Bad Cardinality Estimation), leading to bad execution plans.
3. **Inline TVF (Returns TABLE directly):**
    - 🟢 **Fast:** The Optimizer treats this like a "View." It unfolds the logic and merges it into the main query. **These are highly recommended.**

---

# 🛑 3. Side Effects & Modifying Data (The Iron Rule)

### Stored Procedure

Designed to change the database state.

- Can `UPDATE` Tables.
- Can `INSERT` into Log tables.
- Can `DELETE` records.
- Can call external systems (Send Email, Write to File via xp_cmdshell).

### Function

Designed to be **Read-Only** regarding the database state.

- **Iron Rule:** A `SELECT` statement should not alter the data it is reading.
- ❌ Cannot modify physical tables.
- ❌ Cannot change Session settings (`SET NOCOUNT ON`).
- **Exception:** You **can** insert/update a *Table Variable* (`@T`) that is declared *inside* the function, because that data only exists within the function's scope.

---

# 🧱 4. Temporary Data Handling

### Stored Procedure

- **Temp Tables (`#Tab`):** Supported and recommended. Uses `tempdb`, supports parallel writes, statistics, and indexes.
- **Table Variables (`@Tab`):** Supported.

### Function

- **Temp Tables (`#Tab`):** ❌ **Strictly Forbidden**. Usage causes compilation errors.
- **Table Variables (`@Tab`):** ✅ Supported. This is the only way to handle sets of data inside a Multi-Statement Function.

---

# 🛡️ 5. Error Handling & Transactions

### Stored Procedure

- **Safety:** You can wrap logic in `BEGIN TRY... BEGIN CATCH`.
- **Recovery:** You can handle specific errors (Deadlocks) and implement Retry Logic.
- **Atomicity:** You can control your own Transactions (`BEGIN TRAN`, `COMMIT`, `ROLLBACK`).

### Function

- **No Safety Net:** If a line inside a Function fails (e.g., Divide by Zero), the **entire SQL statement** calling that function stops immediately.
- **Transactions:** A function participates in the caller's transaction but cannot start or end one itself.

---

# 🧩 6. Determinism & Limitations

### Non-Deterministic Functions

- **SP:** Allowed to use `NEWID()`, `RAND()`, `GETDATE()` anywhere.
- **UDF:**
    - ❌ Cannot use `NEWID()` (Side-effecting random).
    - ❌ Cannot use `RAND()` (Side-effecting).
    - ✅ Can use `GETDATE()` (Allowed in newer SQL versions, previously restricted).

### Dynamic SQL

- **SP:** Can construct SQL strings and execute them (`sp_executesql`).
- **UDF:** **Strictly Forbidden**. A function must be static code. You cannot dynamically change the table you are selecting from inside a UDF.

---

# 📝 7. Returns (Output)

### Stored Procedure

Flexible output options:

1. **Zero or More Result Sets:** Can return 5 different SELECT statements to C#.
2. **Output Parameters:** `OUT` variables for scalars.
3. **Return Value:** Only `INTEGER` (Legacy use for status codes).

### Function

Rigid output:

1. **Scalar:** Must return exactly one value (Int, String, etc.).
2. **Table:** Must return a set of rows (which can then be joined).
3. **XML/JSON:** Can return data types containing structure.
- *Limitation:* Cannot return multiple result sets.

---

# 💡 Final Decision Guide: Which to use?

| Scenario | 🏆 Winner | Why? |
| --- | --- | --- |
| **Logic requires INSERT/UPDATE/DELETE** | **Stored Procedure** | Functions strictly cannot do this. |
| **Need to reuse logic in a `WHERE` clause** | **Function** | SPs cannot be called inside a `WHERE` clause. |
| **Returning massive datasets for reports** | **Stored Procedure** | Better performance plans & temp table support. |
| **Parameterized View (Security)** | **Inline TVF** | Fast, acts like a View but accepts inputs. |
| **Formatting Dates/Strings** | **Scalar Function** | Keeps code DRY (Don't Repeat Yourself). |
| **Complex looping with temp data** | **Stored Procedure** | Functions are bad at loops; SPs handle temp tables better. |
| **Used by C# Application** | **Stored Procedure** | SPs provide a secure API layer over your tables. |