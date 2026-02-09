# Index vs Constraint

Here is the comprehensive guide to **Index Types** and the crucial (often misunderstood) relationship between **Constraints and Indexes** in SQL Server.

---

# 📚 Part 1: Types of Indexes in SQL Server

We can categorize indexes based on **Storage Structure** (How they look on disk) and **Properties** (How they behave).

### A. The Structural Core (Storage)

| Type | Limit | Description | Analogy |
| --- | --- | --- | --- |
| **1. Clustered Index** | **1 per Table** | Sorts the **physical data rows** of the table. The leaf nodes contain the actual data. | A Phone Book (Sorted A-Z). The data *is* the index. |
| **2. Non-Clustered Index** | **999 per Table** | A separate structure. Leaf nodes contain the Key + a **Pointer** (Locator) to the actual data row in the Clustered Index (or Heap). | The Index at the back of a text book. |
| **3. Heap (No Index)** | N/A | A table with **No Clustered Index**. Data is stored unordered, wherever space is available. | A pile of receipts in a shoebox. |

### B. The Specialized / Advanced Types

### 4. Unique Index

- **Behavior:** Ensures that the indexed column contains no duplicate values.
- **Note:** If you try to insert a duplicate, SQL throws an error.
- **Internals:** SQL uses this to enforce `PRIMARY KEY` and `UNIQUE` constraints.

### 5. Filtered Index

- **Definition:** A Non-Clustered Index with a `WHERE` clause.
- **Use Case:** Your `Users` table has 1M rows, but only 500 are `IsActive = 1`.
- **Code:** `CREATE INDEX IX_Active ON Users(Email) WHERE IsActive = 1`
- **Benefit:** The index is tiny (only 500 rows) and ultra-fast.

### 6. Covering Index (using `INCLUDE`)

- **Definition:** A Non-Clustered Index that extends its leaf level to carry non-key columns.
- **Goal:** To satisfy a query completely (**Cover** it) without jumping to the Clustered Index (Key Lookup).
- **Code:** `CREATE INDEX IX_Name ON Users(Name) INCLUDE (Address, Phone)`

### 7. Columnstore Index (The Analytics Beast)

- **Definition:** Stores data **Column-wise** instead of Row-wise.
- **Usage:** Data Warehousing, Reporting.
- **Stats:** Can compress data by 10x. Perfect for `SUM`, `AVG` over millions of rows.

### 8. XML, Spatial, & Full-Text Indexes

- **XML Index:** Specifically for `XML` data types (shreds XML tags for searching).
- **Spatial Index:** For Geography (Lat/Long) and Geometry data.
- **Full-Text Index:** For complex text searching (Searching "run" finds "running", "ran").

---

# 🔗 Part 2: Constraints vs. Indexes (The Relationship)

This is a critical concept. Beginners often confuse **Logical Rules** (Constraints) with **Physical Structures** (Indexes).

### 1. Primary Key Constraint (PK)

- **The Logic:** "This column must be Unique and Not Null."
- **The Auto-Index:** By default, creating a PK automatically creates a **Clustered Index**.
    - *Can I change this?* Yes. You can declare a PK as `NONCLUSTERED`, but you must manually create a Clustered index elsewhere.
    - *Advice:* 99% of the time, keep your PK as the Clustered Index (on an Identity Column).

### 2. Unique Key Constraint (UK)

- **The Logic:** "This column must be Unique (NULL is allowed once)."
- **The Auto-Index:** SQL automatically creates a **Non-Clustered Unique Index** to physically enforce this rule.
    - *Why?* To check if a value exists quickly before inserting, SQL needs an index. It cannot scan the whole table for every insert.

### 3. Foreign Key Constraint (FK) 🚨 **CRITICAL WARNING** 🚨

- **The Logic:** "Values in this column must exist in the Parent Table."
- **The Auto-Index:** **NONE.** SQL Server does **NOT** automatically index Foreign Keys.
- **The Danger:**
    - If you delete a Parent row, SQL must check the Child table to ensure no orphans exist.
    - Without an index on the Child FK, SQL must do a **Table Scan** on the Child table.
    - **Result:** Deadlocks and massive performance hits on Delete/Update.
- **Expert Rule:** **ALWAYS manually create a Non-Clustered Index on your Foreign Key columns.**

### Summary Matrix

| Constraint Type | Logical Rule | Creates Index Automatically? | Type Created (Default) |
| --- | --- | --- | --- |
| **Primary Key** | Unique + No Nulls | ✅ **Yes** | Clustered Index |
| **Unique Key** | Unique | ✅ **Yes** | Non-Clustered Unique Index |
| **Foreign Key** | Referential Integrity | ❌ **NO** | N/A (Manual Creation Required) |
| **Check** | Data Validation | ❌ **NO** | N/A |

---

# 🛠️ Practical Examples

### Scenario 1: Primary Key (The Default)

```sql
CREATE TABLE Customers (
    CustID INT PRIMARY KEY, -- 1. Creates Constraint "PK_Customers"
                            -- 2. Creates Clustered Index "PK_Customers"
    Name VARCHAR(50)
);

```

### Scenario 2: Unique Constraint (Email)

```sql
ALTER TABLE Customers
ADD CONSTRAINT UK_Email UNIQUE (Email);
-- 1. Creates Logical Constraint "UK_Email"
-- 2. Creates Physical Non-Clustered Unique Index "UK_Email"

```

### Scenario 3: Foreign Key (The Silent Performance Killer)

```sql
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY,
    CustID INT FOREIGN KEY REFERENCES Customers(CustID)
);
-- ⚠️ Problem: CustID is constrained, but NOT Indexed.
-- If you DELETE FROM Customers WHERE CustID = 1...
-- SQL must SCAN the entire Orders table to look for CustID = 1.

-- ✅ Solution: Create the index manually
CREATE NONCLUSTERED INDEX IX_Orders_CustID ON Orders(CustID);

```

---

# 🧠 Expert Internals: Constraint Names vs. Index Names

When you create a constraint, you can name it. If you don't, SQL generates a random name (e.g., `PK__Table__3214EC07...`).

1. **Best Practice:** Always name your constraints explicitly.
2. **Dropping:**
    - You cannot `DROP INDEX` if it was created by a Constraint (PK or Unique).
    - You must `ALTER TABLE DROP CONSTRAINT`. When you drop the Constraint, the Index is auto-deleted.

**Example:**

```sql
-- ❌ This fails if the index backs a PK
DROP INDEX PK_Employees ON Employees;

-- ✅ This works
ALTER TABLE Employees DROP CONSTRAINT PK_Employees;

```