# Transaction Isolation Levels

# SQL Server Transaction Management

## 1. The Dirty Read Concurrency Problem

A **Dirty Read** occurs when a transaction reads data that has been modified by another transaction that has not yet committed. If the first transaction rolls back, the second transaction has read data that "never existed" effectively.

### The Scenario

1. **Transaction A** begins and updates a row.
2. **Transaction B** reads that same row *before* Transaction A commits.
3. **Transaction A** rolls back its changes.
4. **Result:** Transaction B holds inconsistent/incorrect data.

---

### Transaction 1: The Update & Rollback

This transaction updates a Product's Quantity to 5, waits for 15 seconds (simulating processing), and then rolls back (simulating a failure like "Insufficient Funds").

```sql
BEGIN TRANSACTION
  -- 1. Modify the data
  UPDATE Products SET Quantity = 5 WHERE Id = 1001

  -- 2. Simulate processing delay
  WAITFOR DELAY '00:00:15'

  -- 3. Something went wrong! Undo everything.
  ROLLBACK TRANSACTION

```

---

### Transaction 2: Reading Uncommitted Data

By default, SQL Server protects you from this (`READ COMMITTED`). It will pause Transaction 2 until Transaction 1 finishes.

To force a **Dirty Read**, we must explicitly lower the isolation level to `READ UNCOMMITTED`.

```sql
-- DANGER: Explicitly allowing dirty reads
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

SELECT * FROM Products WHERE Id = 1001
-- Result: You see Quantity = 5 (which will shortly disappear)

```

---

### The `NOLOCK` Hint

A common shortcut in SQL Server is the `(NOLOCK)` table hint. This is functionally equivalent to `READ UNCOMMITTED` but scoped to a single table in a query.

**Query:**

```sql
SELECT * FROM Products (NOLOCK) WHERE Id = 1001

```

**Definition:**
The `NOLOCK` hint instructs the query engine to ignore any Exclusive locks placed by other transactions. It reads whatever is currently in memory, regardless of its committed state.

**Why use it?**

- **Performance:** It prevents queries from being blocked by updates. In heavy-read environments, this stops "Reporting" queries from slowing down "Transactional" writes.

**The Risks (Why it's dangerous):**

1. **Dirty Reads:** Reading data that is about to be rolled back.
2. **Unrepeatable Reads:** Running the same query twice in the same logic might return different results.

---

## 2. The Lost Update Concurrency Problem

The **Lost Update** problem occurs when two or more transactions read and update the same data concurrently, but due to insufficient locking, one update overwrites the other.

### The Scenario

1. **Transaction A** reads a row.
2. **Transaction B** reads the *same* row (seeing the same initial value).
3. **Transaction A** updates the row and commits.
4. **Transaction B** updates the row (based on the initial value it read) and commits.
5. **Result:** The changes made by **Transaction A are overwritten (lost)** by Transaction B. The final state corresponds only to Transaction B's logic, completely ignoring Transaction A's contribution.

### Transaction 1: The Slow Reader

This transaction reads the quantity, waits for 10 seconds (holding onto the old value), subtracts 1, and updates.

```sql
-- Transaction 1
BEGIN TRANSACTION
  DECLARE @QunatityAvailable int

  -- 1. Read initial value (e.g., 10)
  SELECT @QunatityAvailable = Quantity FROM Products WHERE Id = 1001

  -- 2. Wait (Simulate slow user or processing)
  WAITFOR DELAY '00:00:10'

  -- 3. Calculate new value based on OLD read (10 - 1 = 9)
  SET @QunatityAvailable = @QunatityAvailable - 1

  -- 4. Update
  UPDATE Products SET Quantity = @QunatityAvailable WHERE Id = 1001
  Print @QunatityAvailable
COMMIT TRANSACTION

```

### Transaction 2: The Fast Reader

This transaction runs *while Transaction 1 is waiting*. It reads the *same* initial value, subtracts 2, and updates.

```sql
-- Transaction 2 (Run this immediately after starting Transaction 1)
BEGIN TRANSACTION
  DECLARE @QunatityAvailable int

  -- 1. Read initial value (Still 10, because T1 hasn't updated yet)
  SELECT @QunatityAvailable = Quantity FROM Products WHERE Id = 1001

  -- 2. Calculate new value based on OLD read (10 - 2 = 8)
  SET @QunatityAvailable = @QunatityAvailable - 2

  -- 3. Update (Sets DB to 8)
  UPDATE Products SET Quantity = @QunatityAvailable WHERE Id = 1001
  Print @QunatityAvailable
COMMIT TRANSACTION

```

**The Outcome:**

1. T2 sets Quantity to **8**.
2. T1 finishes waiting, calculated **9** (10-1), and overwrites 8 with **9**.

---

## 3. The Non-Repeatable Read Concurrency Problem

The **Non-Repeatable Read** problem occurs when a transaction reads the same row twice and gets a different value each time.

### The Scenario

1. **Transaction 1** reads a row (e.g., Price = $100).
2. **Transaction 2** updates that same row (e.g., Sets Price = $150) and commits.
3. **Transaction 1** reads the *same* row again.
4. **Result:** Transaction 1 sees a different value ($150) than it saw the first time ($100).

### Transaction 1: The Inconsistent Reader

This transaction reads a value, waits, and reads it again. Because the Isolation Level is `READ COMMITTED` (default), it releases the lock after the first read.

```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION
  -- 1. First Read: Gets original value (e.g., 10)
  SELECT Quantity FROM Products WHERE Id = 1001

  -- 2. Wait (allowing other transactions to slip in)
  -- Do Some work
  WAITFOR DELAY '00:00:15'

  -- 3. Second Read: Gets NEW value (e.g., 5)
  SELECT Quantity FROM Products WHERE Id = 1001
COMMIT TRANSACTION

```

### Transaction 2: The Interrupter

This transaction updates the row *while Transaction 1 is waiting*.

```sql
-- Transaction 2 (Run this while T1 is waiting)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION
  -- Update the value to 5
  UPDATE Products SET Quantity = 5 WHERE Id = 1001
COMMIT TRANSACTION

```

**The Outcome:**

---

## 4. The Phantom Read Concurrency Problem

The **Phantom Read** problem occurs when a transaction reads rows that match a search condition, and then a second transaction inserts *new* rows that match that same condition. When the first transaction re-executes the query, it sees "phantom" rows that weren't there before.

### The Scenario

1. **Transaction 1** asks: "How many employees are in the 'Sales' department?" (Count = 10).
2. **Transaction 2** inserts a *new* employee into the 'Sales' department and commits.
3. **Transaction 1** asks again: "How many employees are in the 'Sales' department?" (Count = 11).
4. **Result:** The data changed essentially "underneath" the first transaction.

### Why it Matters

This problem breaks the consistency of aggregate calculations (SUM, COUNT, AVG). It can lead to incorrect data analysis (e.g., generating a report that misses data or includes data that shouldn't be there yet) or flawed decision making.

**Distinction:**

- **Non-Repeatable Read:** A specific *row's value* changes.
- **Phantom Read:** The *set of rows* returned by a query changes (rows appear/disappear).

### Transaction 1: The Haunted Query

This transaction counts 'Male' employees, waits, and counts again. Notice it uses `REPEATABLE READ`, which forces Shared Locks to be held until the transaction ends. This stops *updates* but does NOT stop *inserts*.

```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION
  -- 1. First Count (e.g., 5 Males)
  SELECT * FROM Employees WHERE Gender = 'Male'

  -- 2. Wait
  WAITFOR DELAY '00:00:10'

  -- 3. Second Count (e.g., 6 Males)
  SELECT * FROM Employees WHERE Gender = 'Male'
COMMIT TRANSACTION

```

### Transaction 2: The Phantom Creator

This transaction inserts a new row that matches the criteria of Transaction 1's query.

```sql
-- Transaction 2
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION
  -- Insert a new Male employee
  INSERT INTO Employees VALUES (1005, 'Sambit', 'Male')
COMMIT TRANSACTION

```

**The Outcome:**
Because `REPEATABLE READ` only locks *existing* rows, it cannot lock the "gap" where the new row is inserted. Transaction 1 sees the new row appear out of nowhere in its second query.

---

## 5. Solving the Dirty Read Problem (Read Committed)

To prevent Dirty Reads, you must use any transaction level higher than `READ UNCOMMITTED`. The default for SQL Server is **Read Committed**.

### Transaction 2: The Safe Reader

```sql
-- Transaction 2
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
SELECT * FROM Products WHERE Id = 1001

```

**The Outcome:**
If potentially dirty data is being modified by Transaction 1, Transaction 2 will **WAIT** (blocking) until Transaction 1 completes. It never reads uncommitted data.

### Deep Dive: How Read Committed Works

**1. Shared Locks (Reads):**

- **Behavior:** Acquires a Shared Lock when reading.
- **Duration:** Held **only while data is being read**. Released immediately after the read completes. This ensures no one is modifying the row *while* you are reading it.

**2. Exclusive Locks (Writes):**

- **Behavior:** Acquires an Exclusive Lock when writing.
- **Duration:** Held until the transaction ends. This prevents others from reading (Shared Lock) or writing (Exclusive Lock) until you are done.

---

## 6. Solving the Lost Update Problem (Repeatable Read)

Read Uncommitted and Read Committed isolation levels are vulnerable to Lost Updates. To fix this, we can use **Repeatable Read**, **Snapshot**, or **Serializable**.

### The Fix: Repeatable Read

`REPEATABLE READ` uses additional locking on rows read by the current transaction, preventing those rows from being updated by others until the transaction completes.

### Transaction 1: The Protected Reader

```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION
  DECLARE @QunatityAvailable int
  SELECT @QunatityAvailable = Quantity FROM Products WHERE Id = 1001

  -- Hold the lock for 10 seconds
  WAITFOR DELAY '00:00:10'

  SET @QunatityAvailable = @QunatityAvailable - 1
  UPDATE Products SET Quantity = @QunatityAvailable WHERE Id = 1001
  Print @QunatityAvailable
COMMIT TRANSACTION

```

### Transaction 2: The Blocked Writer (Deadlock Victim)

```sql
-- Transaction 2
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION
  DECLARE @QunatityAvailable int
  SELECT @QunatityAvailable = Quantity FROM Products WHERE Id = 1001

  SET @QunatityAvailable = @QunatityAvailable - 2
  UPDATE Products SET Quantity = @QunatityAvailable WHERE Id = 1001
  Print @QunatityAvailable
COMMIT TRANSACTION

```

**The Outcome:**

1. **Transaction 1** starts, reads (Shared Lock), and waits.
2. **Transaction 2** starts, reads (Shared Lock).
3. **Transaction 2** tries to Update (needs Exclusive Lock). It **BLOCKS** because T1 still holds the Shared Lock.
4. **Transaction 1** wakes up and tries to Update (needs Exclusive Lock). It **BLOCKS** because T2 holds a Shared Lock.
5. **Result:** **DEADLOCK**. SQL Server detects the cycle and kills one transaction (usually T2) as the "Deadlock Victim".
6. T1 succeeds. T2 fails safely (no lost update). Rerunning T2 afterwards works correctly on the updated data.

### Deep Dive: How Repeatable Read Works

**1. Shared Locks (Reads):**

- **Behavior:** When data is read, SQL Server applies Shared Locks.
- **Duration:** Unlike `READ COMMITTED` (release immediately), `REPEATABLE READ` **holds Shared Locks until the transaction finishes**. This guarantees that no one else can modify the data you are looking at.

**2. Exclusive Locks (Writes):**

- **Behavior:** Required for INSERT/UPDATE/DELETE.
- **Duration:** Held until commit/rollback (standard for all levels).

**Key Trade-offs:**

- **Blocking:** Because Shared Locks are held longer, the potential for blocking (and deadlocks, as seen above) increases significantly.

---

## 7. Solving the Phantom Read Problem (Serializable)

To prevent Phantom Reads (new rows appearing in range queries), you must use the **Serializable** or **Snapshot** isolation level.

### The Fix: Serializable

The `SERIALIZABLE` isolation level places a **Range Lock** on the dataset. In our example, if you query `WHERE Gender = 'Male'`, SQL Server locks that specific filter criteria. No one can insert a *new* male employee until you are done.

### Transaction 1: The Strict Reader

```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE
BEGIN TRANSACTION
  -- Acquires Range Lock on Gender='Male'
  SELECT * FROM Employees WHERE Gender = 'Male'

  -- Do Some work (10s)
  WAITFOR DELAY '00:00:10'

  -- Re-execute query. Result is guaranteed to be identical.
  SELECT * FROM Employees WHERE Gender = 'Male'
COMMIT TRANSACTION

```

**The Outcome:**
If potentially occurring phantoms (Transaction 2 inserting 'Male') tries to run, it is **blocked** until Transaction 1 completes.

### How Does SERIALIZABLE Prevent Phantom Reads?

In SQL Server, the Serializable isolation level is the highest level of isolation that prevents non-repeatable reads, phantom reads, and other concurrency issues. Here is how it works:

### 1. Range Locks (The Primary Mechanism)

The primary mechanism by which Serializable prevents phantom reads is through **Range Locks**. Range locking is a technique where SQL Server locks a range of keys in an index, preventing other transactions from inserting, updating, or deleting rows within that range until the lock is released.

- **Key Range Locks:** Locks placed on a range of keys within an index. They ensure that no other transaction can insert a new row that would fall within the range that the current transaction is reading.
- **Locking Strategy:** When a transaction reads data using a range query (e.g., `WHERE Gender = 'Male'`), SQL Server automatically places range locks on the index entries representing that range. This prevents others from inserting *new* 'Male' rows.

### 2. Shared and Exclusive Locks

- **Shared Locks for Read Operations:** When data is read, SQL Server places shared locks on the accessed data. Unlike lower levels, these locks are **kept until the transaction is completed**.
- **Exclusive Locks for Write Operations:** For writes, exclusive locks are used and held until the transaction is completed.

### 3. Duration of Locks

All locks (shared, exclusive, and range) are held until the transaction is **complete** (committed or rolled back), not just for the duration of the individual operation. This ensures consistency throughout the transaction.

### Summary of Trade-offs

While Serializable provides the highest level of data consistency, it comes with trade-offs:

- **Concurrency:** Extensive locking leads to increased blocking.
- **Throughput:** Reduced throughput as transactions wait for locks.
- **Deadlocks:** Higher probability of deadlocks.

---

### Summary Table

| Isolation Level | Dirty Read | Lost Update | Non-Repeatable Read | Phantom Read |
| --- | --- | --- | --- | --- |
| **Read Uncommitted** | Yes | Yes | Yes | Yes |
| **Read Committed** | No | Yes | Yes | Yes |
| **Repeatable Read** | No | No | No | Yes |
| **Snapshot** | No | No | No | No |

---

## 8. Snapshot Isolation Level

Snapshot Isolation offers a way to avoid locking and blocking by providing each transaction with a consistent "snapshot" of the data as it existed at the start of the transaction. It uses **Row Versioning** in `TempDB` instead of locking resources.

There are two modes:

1. **ALLOW_SNAPSHOT_ISOLATION**: (Discussed here) Transactions must explicitly ask for `SNAPSHOT` isolation.
2. **READ_COMMITTED_SNAPSHOT**: Changes the default behavior of `READ COMMITTED` to use versioning.

### Enabling Snapshot Isolation

This is a database-level setting.

```sql
ALTER DATABASE ProductDB SET ALLOW_SNAPSHOT_ISOLATION ON;

```

**How It Works:**

1. **Writes:** When a row is updated, SQL Server stores the *original* version of the row in the Version Store (TempDB) with a transaction sequence number.
2. **Reads:** When a snapshot transaction reads that row, it ignores the current "dirty" or "locked" version. Instead, it traverses the version chain in TempDB to find the version that existed *before* the current transaction started.
3. **Result:** Readers do not block Writers, and Writers do not block Readers.

### Example Scenario

**Step 1: Setup**

```sql
-- Transaction 1 (Snapshot)
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
BEGIN TRANSACTION;
  -- Reads quantity (e.g., 10)
  SELECT Quantity FROM Products WHERE ProductID = 1;

```

**Step 2: Concurrent Modification**

```sql
-- Transaction 2 (Read Committed)
BEGIN TRANSACTION;
  -- Updates quantity to 5
  UPDATE Products SET Quantity = 5 WHERE ProductID = 1;
COMMIT TRANSACTION;

```

**Step 3: Verification**

```sql
-- Transaction 1 (Still Open)
  -- Reads quantity AGAIN
  SELECT Quantity FROM Products WHERE ProductID = 1;
COMMIT TRANSACTION;

```

**Outcome:**
Transaction 1 **still sees the value 10**, even though T2 has committed 5 to the database. T1 sees the "Snapshot" of the world as of its start time.

---

### Lost Update Prevention (Conflict Detection)

Snapshot Isolation prevents Lost Updates not by locking, but by **Conflict Detection**.

**Scenario:**

1. **T1 (Snapshot)** reads Qty=100.
2. **T2 (Snapshot)** reads Qty=100.
3. **T1** updates Qty to 150 and Commits.
4. **T2** attempts to update Qty to 120.

**Result:**
SQL Server detects that the row T2 is trying to update *has changed* since T2's snapshot began. T2 fails immediately with:

> Snapshot isolation transaction aborted due to update conflict...
> 

---

### Comparison: Serializable vs. Snapshot

Both prevent all concurrency anomalies (Dirty, Lost, Non-Repeatable, Phantom), but in different ways.

| Feature | Serializable | Snapshot |
| --- | --- | --- |
| **Mechanism** | **Pessimistic Locking**. Locks rows and ranges ranges to prevent others from changing data. | **Optimistic Row Versioning**. Uses TempDB to keep old versions of data. |
| **Blocking** | **High**. Readers block writers, writers block readers. | **Low**. Readers do not block writers. |
| **Resources** | Uses memory for locks. | Uses **TempDB** for version store. |
| **Concurrency** | **Low**. Serialization reduces parallel throughput. | **High**. Great for read-heavy systems. |

---

## 9. Read Committed Snapshot Isolation (RCSI)

RCSI is a variation of the default `READ COMMITTED` level. Instead of using locks to prevent Dirty Reads, it uses **Row Versioning**.

### The Problem with Standard Read Committed

In standard Read Committed:

1. **Readers Block Writers:** If you are reading a row (holding a shared lock), no one can update it.
2. **Writers Block Readers:** If someone is updating a row (holding an exclusive lock), you cannot read it until they finish.

### The Solution: RCSI

RCSI changes the behavior of `READ COMMITTED` to be non-blocking.

- **Writers** still take exclusive locks (to prevent lost updates).
- **Readers** do **NOT** take shared locks. Instead, they read the *last committed version* of the row from TempDB.

### Enabling RCSI

This is a database-level setting. Unlike `ALLOW_SNAPSHOT_ISOLATION`, this changes the *default* behavior for the entire database.

```sql
ALTER DATABASE ProductDB SET READ_COMMITTED_SNAPSHOT ON;

```

**Crucial Difference:**

- You do **NOT** need to change your code to `SET TRANSACTION ISOLATION LEVEL SNAPSHOT`.
- Any query running as `READ COMMITTED` (the default) automatically starts using row versioning.

### Example: Blocking vs. Non-Blocking

**Scenario:** Transaction 1 updates a row but sleeps before committing. Transaction 2 tries to read it.

### A. Standard Read Committed (Blocking)

```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION
  UPDATE Products SET Quantity = 5 WHERE Id = 1001
  WAITFOR DELAY '00:00:15' -- Holds Exclusive Lock
COMMIT TRANSACTION

-- Transaction 2 (Run concurrently)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION
  SELECT * FROM Products WHERE Id = 1001 -- BLOCKED! Waits for T1.
COMMIT TRANSACTION

```

### B. With RCSI Enabled (Non-Blocking)

```sql
-- Transaction 1
BEGIN TRANSACTION
  UPDATE Products SET Quantity = 5 WHERE Id = 1001
  WAITFOR DELAY '00:00:15'
COMMIT TRANSACTION

-- Transaction 2
BEGIN TRANSACTION
  -- DOES NOT BLOCK.
  -- Returns the 'Old' value (10) because T1 hasn't committed yet.
  SELECT * FROM Products WHERE Id = 1001
COMMIT TRANSACTION

```

### Key Differences: RCSI vs Snapshot Isolation

| Feature | Read Committed Snapshot (RCSI) | Snapshot Isolation |
| --- | --- | --- |
| **Enabling** | `ALTER DB SET READ_COMMITTED_SNAPSHOT ON` | `ALTER DB SET ALLOW_SNAPSHOT_ISOLATION ON` |
| **Code Change** | **None** (Changes default behavior) | Must use `SET TRANSACTION ISOLATION LEVEL SNAPSHOT` |
| **Consistency** | **Statement-Level**. Each *statement* sees the latest committed data at the start of *that statement*. | **Transaction-Level**. The entire *transaction* sees data as it was at the start of the *transaction*. |
| **Conflicts** | No update conflicts (Writers block Writers). | Update conflicts possible (Optimistic). |

---

## 10. Deep Dive: Snapshot Isolation vs. RCSI

While both use Row Versioning, they behaviorally distinct in critical ways.

### 1. Update Conflicts (The "First Committer Wins" Rule)

- **Snapshot Isolation:** Optimistic. If T1 updates a row, and T2 tries to update the *same* row (and T2 started *after* T1 committed), T2 will fail with an **Update Conflict**.
- **RCSI:** Pessimistic locking for writes. T2 will simply **Wait** (Block) until T1 finishes. Once T1 commits, T2 overwrites the data (or uses the new data). **No error occurs.**

### Example: Snapshot Isolation (Conflict Error)

```sql
-- Transaction 1 (Snapshot)
UPDATE Products SET Quantity = 5 WHERE Id = 1001;
-- (Holds lock, does not commit yet)

-- Transaction 2 (Snapshot)
UPDATE Products SET Quantity = 8 WHERE Id = 1001;
-- (BLOCKS waiting for T1)

-- T1 Commits
COMMIT;

-- T2 Wakes up -> DETECTS CHANGE -> ERROR!
-- Msg 3960: usage of Snapshot isolation ... update conflict.

```

### Example: RCSI (Wait & Proceed)

```sql
-- Transaction 1 (RCSI)
UPDATE Products SET Quantity = 5 WHERE Id = 1001;

-- Transaction 2 (RCSI)
UPDATE Products SET Quantity = 8 WHERE Id = 1001;
-- (BLOCKS waiting for T1)

-- T1 Commits
COMMIT;

-- T2 Wakes up -> Proceeds to overwrite with 8. Success.

```

---

### 2. Read Consistency (Transaction vs Statement Level)

This is the most subtle but dangerous difference.

- **Snapshot Isolation:** **Transaction-Level Consistency**. All queries in the transaction see the data exactly as it was at the **start of the transaction**.
- **RCSI:** **Statement-Level Consistency**. Each query sees the data as it was at the **start of that specific statement**.

### The Proof: The "Phantom" Update

Imagine T1 runs two SELECT statements. In between them, T2 updates the data.

**Setup:** Quantity = 10.

**Scenario A: RCSI (Statement Level)**

```sql
-- Transaction 1 (RCSI)
BEGIN TRANSACTION
  -- 1. First Read.
  SELECT Quantity FROM Products WHERE Id = 1001; -- Result: 10

  -- >> Transaction 2 runs and commits UPDATE to 5 <<

  -- 2. Second Read.
  -- RCSI sees the NEW committed data because this is a NEW statement.
  SELECT Quantity FROM Products WHERE Id = 1001; -- Result: 5
COMMIT TRANSACTION

```

*Result:* **Inconsistent reads** within the same transaction (Non-Repeatable Read).

**Scenario B: Snapshot Isolation (Transaction Level)**

```sql
-- Transaction 1 (Snapshot)
BEGIN TRANSACTION
  -- 1. First Read.
  SELECT Quantity FROM Products WHERE Id = 1001; -- Result: 10

  -- >> Transaction 2 runs and commits UPDATE to 5 <<

  -- 2. Second Read.
  -- Snapshot ignores the new data. It sees data as of T1 START time.
  SELECT Quantity FROM Products WHERE Id = 1001; -- Result: 10
COMMIT TRANSACTION

```

*Result:* **Consistent reads** (Repeatable Read).

### Summary

| Feature | Read Committed Snapshot (RCSI) | Snapshot Isolation |
| --- | --- | --- |
| **Consistency Scope** | **Statement** (Variable) | **Transaction** (Fixed) |
| **Update Conflicts** | No (Blocks and overwrites) | Yes (Throws Error) |
| **App Change?** | None (Just DB Config) | Code must set `ISOLATION LEVEL SNAPSHOT` |
| **Distributed Transactions** | Supported | Not Supported |