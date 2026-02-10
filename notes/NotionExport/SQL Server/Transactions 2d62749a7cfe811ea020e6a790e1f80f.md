# Transactions

Here is a comprehensive guide to mastering **Transactions in SQL Server**, structured to take you from a Beginner to an Expert level.

[SAVE TRANSACTION (Transact-SQL) - SQL Server | Microsoft Learn](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/save-transaction-transact-sql?view=sql-server-ver17)

---

# 📘 Phase 1: The Foundation (Beginner)

A **Transaction** is a logical unit of work that contains one or more SQL statements. The rule is simple: either **all** statements succeed, or **none** of them do.

### 1. The Golden Rules (ACID Properties)

Every transaction in SQL Server adheres to four properties:

- **A - Atomicity**
    - **Definition:** The "All or Nothing" rule.
    - **Details:**
        - If one part of the transaction fails, the entire transaction fails.
- **C - Consistency**
    - **Definition:** Data Integrity.
    - **Details:**
        - The database must be in a valid state before and after the transaction (e.g., constraints, foreign keys must be satisfied).
- **I - Isolation**
    - **Definition:** Privacy between users.
    - **Details:**
        - An uncompleted transaction should not be visible to other concurrent transactions (depending on isolation level).
- **D - Durability**
    - **Definition:** Permanence.
    - **Details:**
        - Once a transaction is committed, the data is saved permanently, even if the power fails immediately after.

### 2. Basic Syntax

There are three main commands you must know:

- **Commands**
    - `BEGIN TRANSACTION` (or `BEGIN TRAN`): Starts the boundary.
    - `COMMIT TRANSACTION`: Saves changes permanently.
    - `ROLLBACK TRANSACTION`: Undoes all changes since the `BEGIN`.

**Example: The Classic Bank Transfer**

```sql
-- 1. Start the transaction
BEGIN TRANSACTION;

-- 2. Deduct $100 from Alice (Updates row, locks row)
UPDATE Accounts SET Balance = Balance - 100 WHERE Name = 'Alice';

-- 3. Add $100 to Bob
UPDATE Accounts SET Balance = Balance + 100 WHERE Name = 'Bob';

-- 4. Check for errors, if okay, Save.
-- (Simplified logic for beginner)
COMMIT TRANSACTION;

```

---

# 📙 Phase 2: The Mechanics (Intermediate)

At this stage, you learn how to handle errors and manage transaction nesting.

### 1. Error Handling (Best Practice)

You should never blindly `COMMIT`. Always wrap transactions in a `TRY...CATCH` block.

- **Logic Flow**
    - **Inside `TRY`**: Run your `UPDATE`/`INSERT`. If all succeed, `COMMIT`.
    - **Inside `CATCH`**: Check if a transaction is active, then `ROLLBACK` to clean up.

**Professional Template:**

```sql
BEGIN TRY
    BEGIN TRANSACTION; -- 🟢 Start

    -- Your Critical SQL Work
    UPDATE Inventory SET Qty = Qty - 1 WHERE ProductID = 10;
    INSERT INTO Sales (ProductID, Qty) VALUES (10, 1);

    COMMIT TRANSACTION; -- 🟢 Success: Save data
END TRY
BEGIN CATCH
    -- 🔴 Failure: Something went wrong
    IF @@TRANCOUNT > 0
    BEGIN
        ROLLBACK TRANSACTION; -- Undo everything
    END

    -- Return error message
    SELECT ERROR_MESSAGE() AS ErrorInfo;
END CATCH

```

### 2. Nested Transactions & Savepoints

SQL Server transaction nesting is often misunderstood.

- **`@@TRANCOUNT` Variable**
    - Returns the number of active transactions for the current connection.
    - **Behavior:**
        - `BEGIN TRAN` increments `@@TRANCOUNT` by 1.
        - `COMMIT` decrements `@@TRANCOUNT` by 1.
        - **Crucial:** The transaction is only written to disk when `@@TRANCOUNT` reaches **0**.
- **`ROLLBACK` Behavior**
    - A single `ROLLBACK` undoes **ALL** nested transactions and resets `@@TRANCOUNT` to 0 immediately.
- **Savepoints (`SAVE TRANSACTION`)**
    - Allows partial rollbacks within a transaction.
        - Useful for complex logic where you want to fail one step but keep previous steps.

---

# 📕 Phase 3: Control & Concurrency (Advanced)

Here we deal with **Isolation Levels**. This controls how transactions interact with *other* users trying to read/write the same data simultaneously.

### 1. Concurrency Problems

Before choosing an isolation level, understand what you are preventing:

- **Problems**
    - **Dirty Read:** Reading data that is currently being updated by another transaction but not yet committed.
        - *Risk:* The other transaction might Rollback, meaning you read data that never legally existed.
    - **Non-Repeatable Read:** You read a row twice in one transaction, but the data changed between reads.
    - **Phantom Read:** You run a query (e.g., `WHERE Qty > 10`), but a new row appears (is inserted) by someone else while you are still running.

### 2. Isolation Levels (Least to Most Restrictive)

You set this via `SET TRANSACTION ISOLATION LEVEL <LEVEL>`.

- **Level 1: READ UNCOMMITTED** (🟢 Fastest, 🔴 Least Safe)
    - **Behavior:** Allows **Dirty Reads**. It does not issue shared locks to prevent other transactions from modifying data read by the current transaction.
        - **Use Case:** Reporting queries where 100% accuracy isn't needed, but speed is vital (`NOLOCK`).
- **Level 2: READ COMMITTED** (🟡 SQL Server Default)
    - **Behavior:** You cannot read Dirty data. You must wait for others to commit updates before you can read their rows.
        - **Note:** Does not prevent Non-Repeatable reads or Phantoms.
- **Level 3: REPEATABLE READ**
    - **Behavior:** Locks the rows you read so no one can **Update** or **Delete** them until you finish.
        - **Side Effect:** Increased blocking of other users.
- **Level 4: SERIALIZABLE** (🔴 Slowest, 🟢 Most Safe)
    - **Behavior:** Places a range lock on the dataset. No one can Update, Delete, OR **Insert** new rows that fall into your query range.
        - **Use Case:** Strict financial calculations.
- **Level 5: SNAPSHOT**
    - **Behavior:** Uses **Row Versioning** (stores old versions in `tempdb`).
        - **Benefit:** Readers do not block Writers, and Writers do not block Readers. You read the data as it existed at the start of your transaction.

---

# ⬛ Phase 4: Internals & Tuning (Expert)

### 1. `XACT_STATE()` vs `@@TRANCOUNT`

- **Why switch?**
    - `@@TRANCOUNT` only tells you the nesting level.
    - `XACT_STATE()` tells you the **health** of the transaction.
        - `1`: Active and committable.
        - `0`: No transaction.
        - `1`: **Doomed Transaction**. An error occurred that makes the transaction uncommittable. You *must* rollback.

**Expert Error Handling Pattern:**

```sql
BEGIN CATCH
    -- Check state before deciding action
    IF (XACT_STATE()) = -1
    BEGIN
        PRINT '🔴 The transaction is in an uncommittable state.' +
              'Rolling back transaction.'
        ROLLBACK TRANSACTION;
    END;

    IF (XACT_STATE()) = 1
    BEGIN
        PRINT '🟡 The transaction is committable but an error occurred.' +
              'Committing anyway (rare) or Rolling back.'
        ROLLBACK TRANSACTION;
    END;
END CATCH

```

### 2. Deadlocks

- **Definition:** A situation where two transactions are waiting for each other to give up a lock.
    - User A has Lock on Table 1, wants Table 2.
    - User B has Lock on Table 2, wants Table 1.
    - **Result:** SQL Server chooses a "victim" (usually the one less expensive to rollback) and kills it with Error 1205.
- **How to minimize:**
    - Access objects in the same order in all stored procedures.
    - Keep transactions short and fast.
    - Use `SNAPSHOT` isolation or `READ COMMITTED SNAPSHOT (RCSI)` to reduce read locks.

### 3. Transaction Log Internals (WAL)

- **Write-Ahead Logging:**
    - Modifications are written to the **Log File (LDF)** *before* they are written to the actual Data File (MDF).
    - This ensures ACID durability. If the server crashes, SQL Server runs "Recovery" upon restart:
        - **Redo Phase:** Replays commited transactions found in the log.
        - **Undo Phase:** Rolls back uncommitted transactions found in the log.

---

### Summary Checklist

1. **Beginner:** Always use `BEGIN`, `COMMIT`, `ROLLBACK`.
2. **Intermediate:** Always wrap in `TRY...CATCH` and check `@@TRANCOUNT`.
3. **Advanced:** Choose the right Isolation Level. Default is okay, `READ UNCOMMITTED` is for reporting, `SERIALIZABLE` is for strict consistency.
4. **Expert:** Monitor Locking/Blocking, understand `XACT_STATE()`, and keep transactions as short as possible to avoid Deadlocks.

## **Examples**

The following example shows how to use a transaction savepoint to roll back only the modifications made by a stored procedure if an active transaction is started before the stored procedure is executed.

SQL

```sql
USE AdventureWorks2022;
GO
IF EXISTS (SELECT name FROM sys.objects
           WHERE name = N'SaveTranExample')
    DROP PROCEDURE SaveTranExample;
GO
CREATE PROCEDURE SaveTranExample
    @InputCandidateID INT
AS
    -- Detect whether the procedure was called
    -- from an active transaction and save
    -- that for later use.
    -- In the procedure, @TranCounter = 0
    -- means there was no active transaction
    -- and the procedure started one.
    -- @TranCounter > 0 means an active
    -- transaction was started before the
    -- procedure was called.
    DECLARE @TranCounter INT;
    SET @TranCounter = @@TRANCOUNT;
    IF @TranCounter > 0
        -- Procedure called when there is
        -- an active transaction.
        -- Create a savepoint to be able
        -- to roll back only the work done
        -- in the procedure if there is an
        -- error.
        SAVE TRANSACTION ProcedureSave;
    ELSE
        -- Procedure must start its own
        -- transaction.
        BEGIN TRANSACTION;
    -- Modify database.
    BEGIN TRY
        DELETE HumanResources.JobCandidate
            WHERE JobCandidateID = @InputCandidateID;
        -- Get here if no errors; must commit
        -- any transaction started in the
        -- procedure, but not commit a transaction
        -- started before the transaction was called.
        IF @TranCounter = 0
            -- @TranCounter = 0 means no transaction was
            -- started before the procedure was called.
            -- The procedure must commit the transaction
            -- it started.
            COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        -- An error occurred; must determine
        -- which type of rollback will roll
        -- back only the work done in the
        -- procedure.
        IF @TranCounter = 0
            -- Transaction started in procedure.
            -- Roll back complete transaction.
            ROLLBACK TRANSACTION;
        ELSE
            -- Transaction started before procedure
            -- called, do not roll back modifications
            -- made before the procedure was called.
            IF XACT_STATE() <> -1
                -- If the transaction is still valid, just
                -- roll back to the savepoint set at the
                -- start of the stored procedure.
                ROLLBACK TRANSACTION ProcedureSave;
                -- If the transaction is uncommitable, a
                -- rollback to the savepoint is not allowed
                -- because the savepoint rollback writes to
                -- the log. Just return to the caller, which
                -- should roll back the outer transaction.

        -- After the appropriate rollback, echo error
        -- information to the caller.
        DECLARE @ErrorMessage NVARCHAR(4000);
        DECLARE @ErrorSeverity INT;
        DECLARE @ErrorState INT;

        SELECT @ErrorMessage = ERROR_MESSAGE();
        SELECT @ErrorSeverity = ERROR_SEVERITY();
        SELECT @ErrorState = ERROR_STATE();

        RAISERROR (@ErrorMessage, -- Message text.
                   @ErrorSeverity, -- Severity.
                   @ErrorState -- State.
                   );
    END CATCH
GO
```

[Transaction Isolation Levels](Transactions/Transaction%20Isolation%20Levels%202d62749a7cfe81b1bbbcf4e24c030357.md)