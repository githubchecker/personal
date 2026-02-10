# DELETE vs TRUNCATE

Here is a comprehensive breakdown of **DELETE vs TRUNCATE** in SQL Server, ranging from basic differences to expert-level internals.

---

# ⚔️ The High-Level Battle: DELETE vs TRUNCATE

| Feature | DELETE (The Scalpel) | TRUNCATE (The Sledgehammer) |
| --- | --- | --- |
| **Command Type** | DML (Data Manipulation Language) | DDL (Data Definition Language) - *Effectively* |
| **Filtering** | Allowed (`WHERE` clause) | **NOT** Allowed (Removes Everything) |
| **Speed** | Slow (Row-by-row) | Fast (Page Deallocation) |
| **Identity Column** | Retains current Identity value | **Resets** Identity back to seed |
| **Triggers** | Fires `ON DELETE` Triggers | **Does NOT** fire Triggers |
| **Foreign Keys** | Works (if constraints allow) | **Fails** if referenced by FK |
| **Permissions** | Requires `DELETE` permission | Requires `ALTER` permission (Higher) |

---

# 🔍 Phase 1: DELETE (The Precise Method)

`DELETE` is used when you need control. You use it to remove specific records or when business logic (Triggers) needs to execute.

- **1. Mechanics (Row-by-Row)**
    - SQL Server reads each row, locks it, logs it, and marks it as "ghosted".
    - It consumes significant transaction log space because **every single row's data is written to the Log file** in case you need to restore.
- **2. Fragmentation**
    - `DELETE` does not typically release the allocated storage space on the hard drive immediately; it just marks rows as empty inside the data pages.
- **3. Syntax**
    
    ```sql
    -- Deletes specific rows
    DELETE FROM Employees WHERE Department = 'HR';
    
    -- Deletes all rows (Slow)
    DELETE FROM Employees;
    
    ```
    

---

# 🔨 Phase 2: TRUNCATE (The Reset Button)

`TRUNCATE` is used for a fresh start. It is optimized for performance and cleaning tables completely.

- **1. Mechanics (Page Deallocation)**
    - Instead of touching data rows, SQL Server goes to the **GAM/SGAM/IAM** (Allocation Maps) and simply says "These pages are no longer owned by this table."
    - It is "minimally logged." It only logs the *page deallocations*, not the actual data content.
- **2. Identity Reset**
    - If you have an `Id INT IDENTITY(1,1)`, `TRUNCATE` resets the counter back to 1. `DELETE` continues from the last number (e.g., 1001).
- **3. Foreign Key Restriction**
    - You cannot `TRUNCATE` a table if *another* table points to it via a Foreign Key (even if the other table is empty).
    - *Workaround:* You must Drop Constraint -> Truncate -> Recreate Constraint.

---

# 🛑 Phase 3: The "Rollback" Myth (Interview Favorite)

A common misconception is that `TRUNCATE` cannot be rolled back because it is not logged. **This is FALSE.**

- **The Reality:** Both `DELETE` and `TRUNCATE` can be rolled back if wrapped in a Transaction.
- **Why?** Even though `TRUNCATE` doesn't log the *data*, it logs the *allocation units*. To rollback, SQL Server simply re-assigns those pages back to the table.

**Proof:**

```sql
BEGIN TRANSACTION;
    -- 1. Table has 1 million rows
    SELECT COUNT(*) FROM BigTable;

    -- 2. Wipes data instantly (Log file grows very slightly)
    TRUNCATE TABLE BigTable;

    -- 3. Count is now 0
    SELECT COUNT(*) FROM BigTable;

ROLLBACK TRANSACTION;

-- 4. Magic! 1 million rows are back.
SELECT COUNT(*) FROM BigTable;

```

---

# 🧠 Phase 4: Internals (Expert Details)

### 1. Locking Differences

- **DELETE:**
    - Acquires **Row Locks** (Key Locks).
    - If deleting thousands of rows, lock escalation may occur (Row -> Page -> Table), causing blocking issues for other users.
- **TRUNCATE:**
    - Acquires a **Schema Modification (Sch-M) Lock** on the table.
    - This blocks *all* other access (Read/Write) to the table instantly until completed.

### 2. Storage & High Water Mark (HWM)

The **High Water Mark** indicates how many pages a table is using.

- **DELETE:** Does **not** reset the HWM. If you have a 10GB table and Delete all rows, the file size (`.mdf`) usually stays at 10GB (empty space reserved).
- **TRUNCATE:** Resets the HWM. It effectively frees the storage back to the database OS (or shrinks the structure inside the file).

### 3. Indexed Views

- You **cannot** `TRUNCATE` a table if it is part of an **Indexed View**.

---

# 💡 Summary Recommendation

- **Use `DELETE` When:**
    - You need to filter data (`WHERE`).
    - You have Foreign Keys referencing the table.
    - You need to fire Triggers (audit logs, cleanup logic).
- **Use `TRUNCATE` When:**
    - You need to completely wipe a staging/temp table.
    - You need speed (milliseconds vs. minutes).
    - You want to reset the Identity column `(1, 1)`.