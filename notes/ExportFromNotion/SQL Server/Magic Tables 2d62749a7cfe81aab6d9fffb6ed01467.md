# Magic Tables

In SQL Server, the term **"Magic Tables"** is a common nickname for the **Pseudo-tables** named **`INSERTED`** and **`DELETED`**.

These are not physical tables saved on a hard drive. They are **logical views** of the rows currently affected by a transaction, existing **only** within the memory of a specific operation (Triggers or the `OUTPUT` clause).

Here is the Beginner to Expert breakdown.

---

# 🎩 Phase 1: The Concept

When you perform a Data Manipulation (DML) operation (`INSERT`, `UPDATE`, `DELETE`), SQL Server temporarily creates these two tables in memory to hold the data before it is permanently committed to the physical table.

### The Behavior Matrix

| Operation | 🟢 `INSERTED` Table | 🔴 `DELETED` Table | Logic |
| --- | --- | --- | --- |
| **INSERT** | Contains the **NEW** rows. | **Empty**. | You added data; there is no "old" data. |
| **DELETE** | **Empty**. | Contains the **OLD** rows. | You removed data; there is no "new" data. |
| **UPDATE** | Contains the **NEW** value. | Contains the **OLD** value. | An Update is treated physically as a Delete of the old row followed by an Insert of the new row. |

---

# ⚡ Phase 2: Usage in Triggers (Classic)

The most common use of Magic Tables is inside **Triggers** for Auditing or Business Logic validation.

### Scenario: Auditing Price Changes

We want to log when a product price changes, saving both the Old Price and the New Price.

```sql
CREATE TRIGGER trg_AuditPriceChange
ON Products
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- We JOIN 'Inserted' and 'Deleted' on the Primary Key
    -- to compare the Before vs After state.
    INSERT INTO AuditLog (ProductID, OldPrice, NewPrice, ChangeDate)
    SELECT
        i.ProductId,
        d.Price,  -- Value from DELETED table (Old)
        i.Price,  -- Value from INSERTED table (New)
        GETDATE()
    FROM inserted i
    INNER JOIN deleted d ON i.ProductId = d.ProductId
    WHERE i.Price <> d.Price; -- Only log if value actually changed
END

```

---

# 📤 Phase 3: Usage in `OUTPUT` Clause (Modern)

You don't always need a heavy Trigger to access these tables. You can use the `OUTPUT` clause in standard queries to return the modified data immediately to C# or save it to a temp table.

### 1. Returning the Identity of an Insert

Standard SQL allows `SELECT SCOPE_IDENTITY()`, but that only handles 1 row. Magic Tables handle bulk inserts.

```sql
-- Insert 5 rows and immediately get their new IDs back
INSERT INTO Users (Name)
OUTPUT inserted.Id, inserted.Name -- 🎩 Accessing Magic Table
VALUES ('Alice'), ('Bob'), ('Charlie');

```

### 2. Archiving Deleted Data

Instead of a Trigger, you can move deleted rows to an Archive table in one shot.

```sql
DELETE FROM Orders
OUTPUT deleted.OrderId, deleted.Amount, GETDATE() -- 🎩 Accessing Magic Table
INTO Orders_Archive -- Pushes the magic data into a real table
WHERE OrderDate < '2020-01-01';

```

---

# 🧠 Phase 4: `MERGE` Statements (Expert)

The `MERGE` statement (Upsert) is unique because it can Insert, Update, and Delete all at once. Therefore, **both** Magic Tables are populated simultaneously.

- If `INSERTED` has data and `DELETED` is NULL -> It was an **Insert**.
- If `INSERTED` is NULL and `DELETED` has data -> It was a **Delete**.
- If `INSERTED` has data and `DELETED` has data -> It was an **Update**.

```sql
MERGE TargetTable AS T
USING SourceTable AS S ON T.Id = S.Id
WHEN MATCHED THEN UPDATE SET Val = S.Val
WHEN NOT MATCHED THEN INSERT (Val) VALUES (S.Val)
OUTPUT $action, inserted.Val, deleted.Val; -- 🎩 Logs what happened

```

---

# 🛑 Phase 5: Limitations & Caveats

1. **Read-Only:** You cannot `UPDATE inserted` or `DELETE FROM deleted`. They are strictly for reading.
2. **Scope:** They cease to exist the nanosecond the Trigger or SQL Statement completes. You cannot access them later.
3. **No `UPDATED` Table:** Beginners often ask for an `UPDATED` magic table. It doesn't exist. You must logic it out by comparing `INSERTED` vs `DELETED`.
4. **Columns:** The structure matches the table *trigger is firing on*. If your physical table has 5 columns, the magic tables have the exact same 5 columns.
5. **Text/Image Types:** In very old versions of SQL, accessing `TEXT`/`NTEXT` blobs in triggers was hard. In modern SQL (`VARCHAR(MAX)`), it works seamlessly.

---

# 📝 Summary Diagram

If you run: `UPDATE Employee SET Salary = 5000 WHERE ID = 1` (Old salary was 4000).

**SQL Server memory looks like this during the execution:**

| Table | ID | Salary | State |
| --- | --- | --- | --- |
| **Actual Table** | 1 | 5000 | (The Result) |
| **🔴 DELETED** | 1 | 4000 | (The Snapshot Before) |
| **🟢 INSERTED** | 1 | 5000 | (The Snapshot After) |

You use these two logical tables to calculate difference (`5000 - 4000`) or validation.