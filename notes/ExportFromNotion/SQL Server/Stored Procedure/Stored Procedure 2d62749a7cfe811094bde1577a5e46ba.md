# Stored Procedure

Here is the comprehensive **Beginner to Expert** guide to **Stored Procedures (SP)** in SQL Server.

---

# 📘 Phase 1: The Foundation (Beginner)

**Definition:** A Stored Procedure is a pre-compiled collection of SQL statements saved under a name. Think of it as a **Method** in C# (`public void DoWork()`) that lives inside the database.

### 1. Basic Syntax

```sql
-- Create (run once)
CREATE PROCEDURE dbo.usp_GetUsers
AS
BEGIN
    SET NOCOUNT ON; -- Recommended Best Practice (See Phase 2)

    SELECT * FROM Users;
END
GO

-- Execute
EXEC dbo.usp_GetUsers;

```

### 2. The "Big Three" Benefits

1. **Security:** You can give a user permission to `EXEC` the procedure **without** giving them `SELECT/INSERT` access to the underlying tables.
2. **Network Performance:** Instead of sending 50 lines of SQL text over the network from C# to SQL, you send just the name (`Exec GetUsers`).
3. **Maintainability:** If table logic changes (e.g., column rename), you fix the SP. You don't have to recompile/redeploy the C# application.

---

# ⚙️ Phase 2: Parameters & Data Flow (Intermediate)

Understanding how to get data **IN** and **OUT** is critical.

### 1. The 3 Types of Data Return

1. **Select Sets:** Returning raw rows (Standard).
2. **Return Value:** Returns an **Integer only**. Used primarily for Status Codes (0 = Success, 1 = Fail).
3. **Output Parameters:** Returns specific values (Int, String, Date) back to the caller variables.

### 2. Comprehensive Example

```sql
CREATE PROCEDURE dbo.usp_UpdateStock
    @ProductId INT,           -- Input
    @QtySold INT,             -- Input
    @NewStockLevel INT OUTPUT -- Output
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Validation Logic
    IF NOT EXISTS (SELECT 1 FROM Products WHERE Id = @ProductId)
    BEGIN
        RETURN 1; -- 🔴 Return 1: "Product Not Found"
    END

    -- 2. Business Logic
    UPDATE Products
    SET Stock = Stock - @QtySold
    WHERE Id = @ProductId;

    -- 3. Set the Output
    SELECT @NewStockLevel = Stock
    FROM Products
    WHERE Id = @ProductId;

    RETURN 0; -- 🟢 Return 0: "Success"
END

```

---

# 🕵️ Phase 3: Control & Options (Advanced)

### 1. `SET NOCOUNT ON`

**Always write this** as the first line of your SP.

- **What it does:** Suppresses the *"1 row(s) affected"* message returned by SQL.
- **Why?**
    - **Network:** Saves slight bandwidth.
    - **Tools:** Prevents [ADO.NET](http://ado.net/) or Hibernate from getting confused (some tools treat the "rows affected" message as a Result Set).

### 2. `WITH ENCRYPTION`

- `CREATE PROCEDURE ... WITH ENCRYPTION AS ...`
- Obfuscates the text so users cannot right-click -> "Modify" to see the code.
- *Warning:* It is not a strong security measure (easily decrypted by tools), but prevents casual snooping.

### 3. Execution Context (`EXECUTE AS`)

By default, an SP runs under the permissions of the **User calling it**. You can change this using **Impersonation**.

- **`WITH EXECUTE AS OWNER`**: The SP runs with the permissions of the person who *created* the SP.
    - *Use Case:* Allow a junior user to Truncate a table (via the SP) without giving them actual `ALTER` permissions on the table.

---

# 🧠 Phase 4: Internals & Performance (Expert)

This is the most critical section for high-performance systems.

### 1. The Query Plan Lifecycle

When you run an SP for the very first time:

1. **Parse:** Check syntax.
2. **Resolve:** Check if tables/columns exist.
3. **Compile:** The Optimizer looks at the **Input Parameters** used in the first run and creates the best execution plan (Cache).
4. **Execute:** Run the code.

**Subsequent runs:** It skips 1-3 and reuses the Plan from Cache (Fast!).

### 2. The "Parameter Sniffing" Problem (Killer Issue)

Because the plan is saved based on the *first* value passed, you can get a "bad" plan stuck in cache.

- **Scenario:**
    - **Run 1:** `@Date = '2020-01-01'` (Old date). Returns 10 rows. Optimizer picks a **Seek** (Fast). Plan is cached.
    - **Run 2:** `@Date = '2024-01-01'` (Today). Returns 10 rows. Uses cached **Seek**. (Good).
    - **Run 3:** `@Date = NULL` (Or a wide range). Returns 1,000,000 rows.
    - **Result:** It tries to use the **Seek** (optimized for 10 rows) on 1 million rows. Performance crawls.

### 3. How to fix Parameter Sniffing

**Option A: Local Variable (The Blinder)**
Copy the parameter to a local variable. The optimizer cannot "sniff" the value during compilation, so it creates a generic "Average" plan.

```sql
CREATE PROC GetSales @Date DATETIME
AS
BEGIN
    DECLARE @SafeDate DATETIME = @Date; -- Optimizer goes blind here
    SELECT * FROM Sales WHERE OrderDate = @SafeDate;
END

```

**Option B: Recompile**
Force a new plan every time.

```sql
-- At statement level (Preferred)
SELECT * FROM Sales WHERE OrderDate = @Date OPTION (RECOMPILE);

-- At SP Level (Nuclear option - High CPU)
CREATE PROC ... WITH RECOMPILE

```

**Option C: Optimize For**
Hardcode the optimizer's assumptions.

```sql
SELECT * FROM Sales
WHERE OrderDate = @Date
OPTION (OPTIMIZE FOR (@Date = '2024-01-01'));

```

---

# 🛑 Phase 5: Dynamic SQL (Injection Warning)

Sometimes you need to build the `WHERE` clause dynamically based on user input.

**❌ BAD (SQL Injection Risk)**

```sql
-- If @User input is:  'admin'; DROP TABLE Users; --
EXEC ('SELECT * FROM Users WHERE Name = ' + @User)

```

**✅ GOOD (sp_executesql)**
Use `sp_executesql` which supports parameters, treating the input strictly as a value, not executable code.

```sql
DECLARE @SQL NVARCHAR(MAX) = N'SELECT * FROM Users WHERE Name = @NameParam';
EXEC sp_executesql @SQL, N'@NameParam VARCHAR(50)', @NameParam = @User;

```

---

# 📋 Summary Checklist

1. **Syntax:** Always use `SET NOCOUNT ON`.
2. **Naming:** Use `usp_` or `proc_`. Avoid `sp_` (System Procedures), as SQL checks the Master DB first, causing a slight perf hit.
3. **Data:** Use `OUTPUT` parameters for single values, `SELECT` for lists.
4. **Perf:** Be aware of Parameter Sniffing. If an SP suddenly goes slow after months of working fine, it's likely a sniffing issue (Updating Statistics usually fixes it temporarily).
5. **Security:** Always use `sp_executesql` for dynamic strings.