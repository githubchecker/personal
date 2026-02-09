# Child SP Created Temp table. Can parent access?

**No, the Parent CANNOT access a Local Temp Table (`#Table`) created by the Child.**

Here is the technical reason and the proof.

### 🛑 The Rule of Scope (Stack)

- **Parent -> Child (Downstream):** ✅ Works. Children inherit the Parent's scope.
- **Child -> Parent (Upstream):** ❌ Fails. Local temp tables are **destroyed** the exact millisecond the Child SP finishes execution. By the time control returns to the Parent, the table no longer exists in `tempdb`.

---

### 💻 The Proof (Code that Fails)

**1. The Child (Creator)**

```sql
CREATE PROCEDURE dbo.ChildSP
AS
BEGIN
    -- Created inside Child scope
    CREATE TABLE #HiddenData (ID INT);
    INSERT INTO #HiddenData VALUES (1);

    PRINT 'Child finished.';
    -- 💀 #HiddenData is DROPped automatically right here
END

```

**2. The Parent (The Victim)**

```sql
CREATE PROCEDURE dbo.ParentSP
AS
BEGIN
    EXEC dbo.ChildSP;

    -- 🛑 ERROR: Invalid object name '#HiddenData'.
    SELECT * FROM #HiddenData;
END

```

---

### 🔓 The Workarounds (How to fix it)

If you need the Child to generate data for the Parent, you have two professional options:

### Option A: "Parent Creates, Child Fills" (Best Practice 🏆)

The Parent creates the empty table structure *before* calling the Child. Because visibility flows down, the Child can see it and fill it.

```sql
-- PARENT
CREATE PROCEDURE dbo.ParentSP AS
BEGIN
    CREATE TABLE #SharedData (ID INT); -- Created Here
    EXEC dbo.ChildSP;                  -- Child Fills it
    SELECT * FROM #SharedData;         -- Data exists!
END

-- CHILD
CREATE PROCEDURE dbo.ChildSP AS
BEGIN
    INSERT INTO #SharedData VALUES (1); -- Accessing Parent's table
END

```

### Option B: Global Temp Table (Risky)

Use `##GlobalData` (Double Hash). It survives the Child finishing.

- **Warning:** Dangerous in multi-user environments (concurrency/locking).

### Option C: `INSERT INTO ... EXEC`

The Child simply `SELECT`s the data (returning a result set), and the Parent captures it.

- **Constraint:** Works well only if the Child returns exactly **one** result set.

```sql
-- PARENT
DECLARE @Captured TABLE (ID INT);
INSERT INTO @Captured
EXEC dbo.ChildSP; -- Child performs a simple SELECT

```