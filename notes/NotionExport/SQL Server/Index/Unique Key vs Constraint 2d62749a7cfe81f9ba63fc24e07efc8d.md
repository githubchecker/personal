# Unique Key vs Constraint

To manually enforce Uniqueness without adding a "Logical Constraint" to the table metadata, you use a **Unique Index**.

In SQL Server, a Unique Constraint is effectively just a wrapper around a Unique Index. By skipping the constraint wrapper, you get the same behavior (no duplicates allowed) but with more flexibility (options like `INCLUDE`, `WHERE`, and `FILLFACTOR`).

---

# 🔑 The Method: `CREATE UNIQUE INDEX`

Instead of `ALTER TABLE... ADD CONSTRAINT`, you use `CREATE INDEX` with the `UNIQUE` keyword.

### 1. Basic Syntax

This enforces that every value in `Email` must be distinct.

```sql
CREATE UNIQUE NONCLUSTERED INDEX IX_Users_Email
ON Users(Email);

```

- **Behavior:** If you try to insert `alice@test.com` twice, SQL Server throws Error 2601 ("Cannot insert duplicate key row...").
- **Result:**
    - Does it look like a Key in SSMS? **No** (It won't be under the "Keys" folder).
    - Does it enforce uniqueness? **Yes** (Strictly).

---

# 🧠 Comparison: Constraint vs. Index

Why would you choose the Index method over the standard Constraint?

| Feature | Unique Constraint (`ADD CONSTRAINT`) | Unique Index (`CREATE UNIQUE INDEX`) |
| --- | --- | --- |
| **Object Type** | Logical Business Rule | Physical Storage Structure |
| **Flexibility** | 🔴 Low (Basic Uniqueness only) | 🟢 **High** (Filtering, Includes, etc.) |
| **Included Columns** | 🔴 No (`INCLUDE` not supported) | 🟢 Yes (Can use `INCLUDE` for perf) |
| **Filtering** | 🔴 No (Checks every row) | 🟢 Yes (Can check subset `WHERE...`) |
| **Error Message** | Violation of UNIQUE KEY constraint | Cannot insert duplicate key row in object |

---

# 🚀 Expert Use Cases (Why you normally do this)

The main reason Experts use `CREATE UNIQUE INDEX` directly is to enable features that Constraints simply do not support.

### 1. The "Ignore NULLs" Pattern (Filtered Unique Index)

In standard SQL Server, a Unique Constraint treats `NULL` as a value.

- **Constraint Rule:** You can have only **ONE** row with `NULL`.
- **Problem:** Often you want "Email must be unique, but multiple users can have `NULL` (no email)."

**Solution: The Filtered Unique Index**
This allows infinite `NULL`s, but enforces uniqueness on actual data.

```sql
CREATE UNIQUE NONCLUSTERED INDEX IX_Mobile_UniqueNotNull
ON Users(MobileNumber)
WHERE MobileNumber IS NOT NULL; -- 🟢 The Magic Line

```

### 2. Performance Tuning (`INCLUDE`)

A Constraint validates uniqueness but doesn't help queries fetch extra data. An Index can do both.

**Scenario:** Enforce Unique Email, but also make `SELECT Email, PhoneNumber FROM Users` instant.

```sql
CREATE UNIQUE NONCLUSTERED INDEX IX_Email_IncludePhone
ON Users(Email)
INCLUDE (PhoneNumber); -- 🟢 Makes the query 'Covered'

```

---

# 📝 Summary Checklist

- **To create a Constraint:** Use `ALTER TABLE ... ADD CONSTRAINT UQ_Name UNIQUE...`
    - *Best for:* Documentation and standard Business Logic.
- **To create it Manually (Index):** Use `CREATE UNIQUE INDEX IX_Name ...`
    - *Best for:* Performance (`INCLUDE`), handling NULL logic (`WHERE`), or advanced tuning options.