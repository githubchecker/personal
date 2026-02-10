# Error Handling

Here is a comprehensive guide to **Error Handling in SQL Server**, moving from syntax to complex architectural patterns like Nested SPs, Retries, and C# integration.

---

# 🛑 Phase 1: How to Raise Errors

Before you can catch an error, you must understand how to generate one.

### 1. The Modern Standard: `THROW` (Recommended)

Introduced in SQL 2012. It is compliant with SQL standards and easier to use.

- **Syntax:** `THROW [error_number], [message], [state];`
- **Re-Throwing:** Using `THROW;` inside a `CATCH` block re-throws the exact original error.
- **Constraint:** `error_number` must be > 50000.
- **Vital Rule:** The statement **before** `THROW` must be terminated with a semicolon `;`.

```sql
-- Example
IF NOT EXISTS (SELECT 1 FROM Users WHERE Id = 1)
BEGIN
    ;THROW 51000, 'User ID not found.', 1;
END

```

### 2. The Legacy Method: `RAISERROR`

Older, more complex, but offers flexibility (like string substitution `printf` style).

- **Syntax:** `RAISERROR ('Message', Severity, State)`
- **Severity:**
    - `0-10`: Information (Does not jump to CATCH block).
    - `11-19`: Errors (Jumps to CATCH block).
    - `20-25`: Fatal system errors.

```sql
-- Example
DECLARE @UserId INT = 5;
RAISERROR ('User %d does not exist', 16, 1, @UserId);
-- Result: "User 5 does not exist"

```

---

# 🛡️ Phase 2: The `TRY...CATCH` Block

This is the structure used to handle exceptions gracefully without crashing the script.

### 1. Basic Syntax and Helper Functions

Inside the `CATCH` block, you use system functions to understand *what* happened.

- **`ERROR_NUMBER()`**: The internal ID (e.g., 2627 for Primary Key Violation).
- **`ERROR_MESSAGE()`**: The text description.
- **`ERROR_SEVERITY()`**: How bad it is.
- **`ERROR_STATE()`**: Where exactly it happened (internal).
- **`ERROR_PROCEDURE()`**: Name of the SP/Trigger.
- **`ERROR_LINE()`**: Line number.

### 2. Full Implementation Pattern

```sql
BEGIN TRY
    -- 🟢 Happy Path: Division by zero error
    SELECT 1 / 0;
END TRY
BEGIN CATCH
    -- 🔴 Exception Handling
    SELECT
        ERROR_NUMBER() AS ErrorCode,
        ERROR_MESSAGE() AS Msg,
        ERROR_LINE() AS LineNum;

    -- Log to table (Optional)
    -- INSERT INTO ErrorLog ...

    -- Bubble up error to C# (Important!)
    ;THROW;
END CATCH

```

---

# 🏗️ Phase 3: Nested Stored Procedures & Transactions

This is where most developers struggle. If a Child SP rolls back, it kills the **entire** transaction chain, causing Error 266 ("Transaction count mismatch") in the Parent SP.

### The Safe Nested Pattern

You must check if a transaction is *already* active before starting a new one.

- **Logic Flow:**
    1. Check `@@TRANCOUNT`.
    2. If `> 0`, perform a **Savepoint** (Partial Save).
    3. If `= 0`, start a real `BEGIN TRANSACTION`.
    4. In Catch, rollback only to the Savepoint (if nested) or fully (if root).

```sql
CREATE PROCEDURE dbo.UpdateUserSafely
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @TranName VARCHAR(20) = 'MySavePoint';
    DECLARE @IsInnerTransaction BIT = 0;

    -- 1. Check transaction depth
    IF @@TRANCOUNT > 0
    BEGIN
        -- We are inside another SP's transaction.
        -- Create a savepoint, do NOT start a new transaction.
        SAVE TRANSACTION @TranName;
        SET @IsInnerTransaction = 1;
    END
    ELSE
    BEGIN
        -- We are the root. Start a real transaction.
        BEGIN TRANSACTION;
    END

    BEGIN TRY
        -- 🟢 DO WORK
        UPDATE Users SET LastLogin = GETDATE();

        -- 🟢 Commit only if we started the transaction
        IF @IsInnerTransaction = 0
        BEGIN
            COMMIT TRANSACTION;
        END
    END TRY
    BEGIN CATCH
        -- 🔴 Handle Rollback
        IF @IsInnerTransaction = 1
        BEGIN
            -- Only undo THIS SP's work, leave the Parent SP alone
            ROLLBACK TRANSACTION @TranName;
        END
        ELSE
        BEGIN
            -- We are the root. Doom the whole thing.
            -- Check XACT_STATE in case connection is already dead
            IF @@TRANCOUNT > 0
                ROLLBACK TRANSACTION;
        END

        -- Tell the caller (and C#) something went wrong
        ;THROW;
    END CATCH
END

```

---

# 🔁 Phase 4: Partial Saves & Retry Logic

### 1. Partial Saves (Savepoints)

Using the `SAVE TRANSACTION` syntax above allows you to fail one part of a process without rolling back previous successful steps within the same transaction.

### 2. Retry Logic (Deadlock Handling)

If you encounter **Error 1205 (Deadlock)**, SQL Server picked your process as a victim. The correct response is to retry the operation automatically.

**T-SQL Retry Loop Example:**

```sql
DECLARE @RetryCount INT = 1;
DECLARE @MaxRetries INT = 3;
DECLARE @Success BIT = 0;

WHILE @RetryCount <= @MaxRetries AND @Success = 0
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Dangerous work
        UPDATE Stock SET Qty = Qty - 1 WHERE Id = 100;

        COMMIT TRANSACTION;
        SET @Success = 1; -- 🟢 Exit Loop
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;

        -- Check for Deadlock (1205) or Snapshot Conflict (3960)
        IF ERROR_NUMBER() IN (1205, 3960)
        BEGIN
            SET @RetryCount = @RetryCount + 1;
            -- Wait 50ms before retrying to let other lock release
            WAITFOR DELAY '00:00:00.050';
        END
        ELSE
        BEGIN
            -- Real error (Syntax, Constraints), do not retry
            ;THROW;
        END
    END CATCH
END

```

---

# 💻 Phase 5: Handling in C# ([ADO.NET](http://ado.net/) & EF Core)

When SQL Server executes a `;THROW` or `RAISERROR(..., 16, ...)`, it throws an exception in .NET.

### 1. Catching in [ADO.NET](http://ado.net/)

The native `SqlException` class contains the specific SQL details.

```csharp
try
{
    using (SqlConnection conn = new SqlConnection("..."))
    {
        conn.Open();
        SqlCommand cmd = new SqlCommand("dbo.UpdateUserSafely", conn);
        cmd.CommandType = CommandType.StoredProcedure;
        cmd.ExecuteNonQuery();
    }
}
catch (SqlException ex)
{
    // 🔴 Loop through errors (SQL can return multiple errors)
    foreach (SqlError err in ex.Errors)
    {
        Console.WriteLine($"Msg: {err.Message}");
        Console.WriteLine($"Code: {err.Number}"); // e.g., 50000 or 1205

        // Custom Logic
        if (err.Number == 1205)
        {
             // Logic to retry C# call
        }
        if (err.Number >= 50000)
        {
             // This is a custom business error raised by ;THROW
             ShowUserMessage(err.Message);
        }
    }
}

```

### 2. Catching in Entity Framework Core

EF Core wraps the SQL exception inside a `DbUpdateException` (usually). You must drill down to the `InnerException`.

```csharp
try
{
    context.Database.ExecuteSqlRaw("EXEC dbo.UpdateUserSafely");
    // OR
    context.SaveChanges();
}
catch (DbUpdateException dbEx)
{
    // 🟡 Unwrap to find SQL specifics
    var sqlEx = dbEx.InnerException as SqlException;

    if (sqlEx != null)
    {
        if (sqlEx.Number == 2627)
        {
            Console.WriteLine("Duplicate Record found!");
        }
        else
        {
            Console.WriteLine($"SQL Error: {sqlEx.Message}");
        }
    }
}
catch (Exception ex)
{
    // General C# error
}

```

### Summary of C# Integration

1. **Severity < 11:** treated as "InfoMessages" in [ADO.NET](http://ado.net/). Use `conn.InfoMessage += ...` event to capture them; they do **not** throw a catchable Exception.
2. **Severity >= 11:** Stops execution and jumps to C# `catch`.
3. **`XACT_ABORT` Warning:** If you use `SET XACT_ABORT ON` in SQL, a T-SQL error usually creates a Severe failure, immediately terminating the connection, sometimes preventing `catch` blocks inside SQL from running, passing the error straight to C#.

# IF Child Does Not use Savepoints

If the Child SP performs a standard `ROLLBACK TRANSACTION` (without a Savepoint), it causes a **Catastrophic Rollback** for the Parent.

Here is the specific sequence of events and why it is dangerous:

### 1. The "Atom Bomb" Effect

In SQL Server, **nested transactions do not exist physically**; they only exist logically via a counter (`@@TRANCOUNT`).

- A `BEGIN TRAN` adds +1 to the counter.
- A `COMMIT` subtracts -1 from the counter.
- **A `ROLLBACK` resets the counter immediately to 0**, regardless of how high the number was.

**Result:** If the Child rolls back, **it undoes the Parent's work too**, and the transaction completely disappears.

### 2. The "Transaction Count Mismatch" (Error 266)

When the Child finishes and returns control to the Parent, the Parent is usually unaware that the transaction has been destroyed.

1. The Parent tries to `COMMIT`, resulting in **Error 3902** ("The COMMIT TRANSACTION request has no corresponding BEGIN TRANSACTION").
2. Or, if the Parent reaches the `END` of its code block, SQL Server compares `@@TRANCOUNT` at the start vs. the end. Since it dropped to 0 unexpectedly, SQL throws **Error 266**.

---

### 💥 Step-by-Step Visualization

| Step | Actor | Action | `@@TRANCOUNT` | Status |
| --- | --- | --- | --- | --- |
| 1 | **Parent** | `BEGIN TRAN` | **1** | Transaction Active |
| 2 | **Parent** | Inserts Record 'A' | **1** | 'A' is locked (Temp) |
| 3 | **Parent** | Calls **Child SP** | **1** |  |
| 4 | **Child** | `BEGIN TRAN` (Nested) | **2** | Counter increases |
| 5 | **Child** | Error occurs! Jumps to Catch | **2** |  |
| 6 | **Child** | `ROLLBACK TRANSACTION` | **0** 💀 | **EVERYTHING (A) IS DELETED** |
| 7 | **Child** | Finishes/Throws Error | **0** | Returns to Parent |
| 8 | **Parent** | Resumes code... | **0** | **Problem Begins Here** |
| 9 | **Parent** | `COMMIT` or Procedure Exit | **0** | 💥 **Error 266 / 3902** |

---

### 💻 Code Example: The Failure

**The Child SP (No Savepoint)**

```sql
CREATE PROCEDURE dbo.ChildSP_Unsafe
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION; -- @@TRANCOUNT goes from 1 -> 2

        -- Simulate Error
        SELECT 1 / 0;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        -- ❌ DANGER: This rolls back EVERYTHING (Parent included)
        ROLLBACK TRANSACTION; -- @@TRANCOUNT goes from 2 -> 0

        -- Throws error back to Parent
        ;THROW;
    END CATCH
END

```

**The Parent SP**

```sql
CREATE PROCEDURE dbo.ParentSP
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION; -- @@TRANCOUNT = 1

        -- 1. Do Parent Work
        INSERT INTO Logs (Msg) VALUES ('Parent Started');

        -- 2. Call Child
        EXEC dbo.ChildSP_Unsafe;

        -- 3. We never reach here because Child threw error
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        PRINT 'Parent Catch Block Reached';

        -- 4. Parent Checks Transaction
        -- ERROR 3902 happens here if we try to rollback what is already gone
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        -- RESULT: The 'Parent Started' log is LOST.
        PRINT ERROR_MESSAGE();
    END CATCH
END

```

### ❓ How to handle this in C#?

Since the transaction is already dead, your C# handling depends on *where* the error is caught.

1. **In the SQL `CATCH` block of the Parent:**
You must check `IF @@TRANCOUNT > 0` before issuing a Rollback. If you blindly issue `ROLLBACK` in the Parent's catch block after the Child already did it, you will get the error:
    
    > Currently there is no transaction since the previous roll back...
    > 
2. **In C# ([ADO.NET/EF](http://ado.net/EF) Core):**
You will receive a `SqlException`.
    - You might see the original error (Division by zero).
    - You might effectively see **Error 266** ("Transaction count after EXECUTE indicates a mismatch...").
    - **Action:** You do not need to call `Rollback()` in C# code if the connection is closed or the transaction is effectively zombie. However, standard practice is wrapping the C# transaction in a `using` block, which will simply attempt to dispose of the transaction safely.

### Summary

If you do **not** use Savepoints in a Child SP:

1. The Child's Rollback kills the **entire** unit of work (Parent + Child).
2. The Parent SP usually crashes with **Error 266** upon exit.
3. Partial error recovery (saving the Parent's work while failing the Child) is **impossible**.

# Error Propagation

Here is a detailed breakdown of how **Error Propagation** works in SQL Server across **Stored Procedures**, **Triggers**, and **Functions**. Understanding this is vital because each object type behaves differently when an error occurs.

---

# 🔄 1. Stored Procedures (Chain Reaction)

Stored Procedures give you the most control. Errors here propagate (bubble up) based on whether you catch them or if a transaction setting forces a hard stop.

### The Propagation Flow

**Client (C#)** calls **Parent SP**, which calls **Child SP**.

- **Default Behavior (Legacy/Unsafe):**
    - If the Child hits an error (e.g., `Constraint Violation`), SQL Server often terminates *only* that statement.
    - The Child SP **continues** to the next line.
    - The Parent SP **continues**.
    - **Result:** Data inconsistency (Partially committed data).
- **With `TRY...CATCH` (Modern/Safe):**
    - The Error jumps immediately to the `CATCH` block of the current scope (Child).
    - If the Child does a `;THROW`, it bubbles up to the **Parent's CATCH block**.
    - If the Parent does a `;THROW`, it bubbles up to **C#**.

### ⚙️ The Game Changer: `SET XACT_ABORT ON`

This is a crucial setting for error propagation.

- **Definition:** It instructs SQL Server to immediately **Rollback** the entire transaction and stop execution if *any* error occurs.
- **Propagation:**
    - With `ON`: A Child error instantly stops everything and throws a hard exception to the Client (bypassing subsequent code, though `CATCH` blocks still catch it).

---

# ⚡ 2. Triggers (The Nuclear Option)

Triggers are special because they execute **within the same transaction context** as the statement that fired them.

### The Rules of Propagation

1. **Joined at the Hip:**
    - The `INSERT`/`UPDATE` statement and the `TRIGGER` are one single atomic unit.
2. **Error Behavior:**
    - If an unhandled error occurs in a Trigger, the **Batch is Aborted**.
    - **🔴 Key Concept:** You cannot "fail" a trigger but "keep" the insert. If the Trigger dies, the Insert is rolled back.
3. **Explicit Rollback:**
    - It is common logic to check a rule in a trigger and manually issue `ROLLBACK TRANSACTION; RAISERROR(...)`.
    - **Propagation:** This creates a **Batch Abort** error (Error 3609: "The transaction ended in the trigger...").

### Can you use `TRY...CATCH` in Triggers?

- **Yes, but with limits.**
    - You can catch an error inside a trigger to log it.
    - However, if the error is severe, or if you issue a `ROLLBACK` inside the catch, the error propagates to the application as a Transaction/Batch termination error, not just a simple message.

**Example of Trigger Propagation:**

```sql
CREATE TRIGGER trg_ProtectData ON Sales
AFTER INSERT
AS
BEGIN
    IF EXISTS (SELECT 1 FROM inserted WHERE Qty < 0)
    BEGIN
        -- 🔴 Stops the Insert, Rolls back Trans, Throws Exception to Client
        ROLLBACK TRANSACTION;
        THROW 51000, 'Quantity cannot be negative', 1;
        RETURN;
    END
END

```

---

# 📐 3. User-Defined Functions (The Rigid Logic)

Functions (Scalar or Table-Valued) are the strictest objects regarding errors.

### 🔴 The Major Restriction: NO `TRY...CATCH`

- **Rule:** You strictly **cannot** use `TRY...CATCH` blocks inside a UDF.
- **Consequence:** There is no error *handling* in a UDF, only error *avoidance*.

### Propagation Behavior

1. **Runtime Errors (e.g., Divide by Zero, Conversion Failure):**
    - If a UDF encounters an error, it immediately **terminates the entire SQL statement** calling it.
    - The error bubbles straight to the Client/Calling SP. You cannot intercept it mid-query.
2. **Example:**
    - `SELECT dbo.MyFunc(Column) FROM BigTable`
    - If row 1,000,000 fails inside the function, the entire `SELECT` fails. No rows are returned.

### How to Handle It? (Defensive Coding)

Since you can't Catch, you must check before execution.

**Unsafe UDF:**

```sql
CREATE FUNCTION dbo.GetRatio (@A INT, @B INT) RETURNS DECIMAL(10,2)
AS BEGIN
    -- 🔴 If @B is 0, this query crashes immediately.
    RETURN @A / @B
END

```

**Safe UDF (Error Swallowing):**

```sql
CREATE FUNCTION dbo.GetRatioSafe (@A INT, @B INT) RETURNS DECIMAL(10,2)
AS BEGIN
    -- 🟢 Check first. Return NULL (or 0) to prevent crash propagation.
    RETURN CASE
             WHEN @B = 0 THEN NULL
             ELSE @A / @B
           END
END

```

---

# 📊 Summary Comparison Table

| Feature | Stored Procedure (SP) | Trigger | Function (UDF) |
| --- | --- | --- | --- |
| **Support TRY...CATCH?** | ✅ Yes (Fully Supported) | ✅ Yes (But failure aborts batch) | ❌ **NO** (Syntax Error) |
| **Default Propagation** | Continues to next line (usually) | Aborts the Trigger + The Command | Aborts the Calling Statement |
| **Transaction Context** | Can start its own or join parent | Locked to the calling command | Read-Only (mostly), No Trans logic |
| **If logic fails...** | Can `ROLLBACK`, `SAVE` or Log | Implicitly `ROLLBACKS` parent | Crashes the Query executing it |
| **Best Handling Strategy** | `TRY...CATCH` + `THROW` | `ROLLBACK` + `THROW` | `NULLIF` / `CASE` checks |

### 🎯 Practical Advice for Developers

1. **SP:** Always use `SET XACT_ABORT ON` and `TRY...CATCH` so errors propagate quickly and cleanly.
2. **Triggers:** Keep them minimal. If an error occurs here, your `INSERT/UPDATE` from C# will receive a `SqlException` stating the transaction ended in the trigger.
3. **Functions:** Never assume input is valid. You must code defensively (e.g., `NULLIF(Col, 0)`) because you cannot catch the exception once the function starts running.

[**RAISERROR vs THROW**](Error%20Handling/RAISERROR%20vs%20THROW%202d62749a7cfe81459a35f11ee59b57be.md)

[**TRY...CATCH**](Error%20Handling/TRY%20CATCH%202d62749a7cfe8104bdd3c9b37a56ef0d.md)