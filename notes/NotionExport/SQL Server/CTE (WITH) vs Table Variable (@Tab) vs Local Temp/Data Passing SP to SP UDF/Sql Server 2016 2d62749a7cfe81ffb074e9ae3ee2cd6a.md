# Sql Server  < 2016

Since you are on **Legacy SQL Server 2008** and specifically want to **avoid Table-Valued Parameters (TVP)**, your options are limited to techniques that rely on scope inheritance or string serialization.

Here are the 4 standard "Old School" patterns used before TVPs became mainstream.

---

# 🥇 Option 1: Local Temporary Tables (`#Table`) (The Best Option)

In SQL Server, **Scope Inheritance** allows a Child SP to see any temporary table created by its Parent SP.

**How it works:**

1. Parent creates `#Temp`.
2. Parent calls Child.
3. Child "blindly" selects from `#Temp` (even though it's not defined inside the Child).
4. It works because they share the same Connection/Session.

**Performance:** Best (Full statistics, indexing support).

**Parent SP:**

```sql
CREATE PROCEDURE dbo.ParentSP
AS
BEGIN
    -- 1. Create the #Temp table structure explicitely
    CREATE TABLE #ContextData (
        CustomerId INT PRIMARY KEY,
        Amount MONEY
    );

    -- 2. Populate it
    INSERT INTO #ContextData (CustomerId, Amount)
    SELECT CustomerId, TotalDue FROM Sales.SalesOrderHeader WHERE TotalDue > 5000;

    -- 3. Call Child (No parameters passed)
    EXEC dbo.ChildSP;

    -- 4. Clean up (Optional, happens automatically at end of session)
    DROP TABLE #ContextData;
END

```

**Child SP:**

```sql
CREATE PROCEDURE dbo.ChildSP
AS
BEGIN
    -- ⚠️ ERROR TRAP: Check if table exists to avoid crashing if run alone
    IF OBJECT_ID('tempdb..#ContextData') IS NULL
    BEGIN
        RAISERROR('This SP must be called by ParentSP', 16, 1);
        RETURN;
    END

    -- Direct access
    SELECT * FROM #ContextData;

    -- You can even modify it, and Parent sees the changes
    UPDATE #ContextData SET Amount = Amount + 10;
END

```

---

# 🥈 Option 2: XML Parameter

Before JSON exists (2016) and before people liked TVPs, **XML** was the standard way to pass complex datasets as a single variable.

**How it works:**

1. Serialize data to XML in Parent (`FOR XML`).
2. Pass as `VARCHAR(MAX)` or `XML` type.
3. Parse in Child (`.nodes`).

**Performance:** Slower (CPU overhead for XML parsing), but safe and isolated.

**Parent SP:**

```sql
CREATE PROCEDURE dbo.ParentSP_XML
AS
BEGIN
    DECLARE @XmlData XML;

    -- Convert Table Data to XML
    SET @XmlData = (
        SELECT Id, UserName
        FROM Users
        FOR XML PATH('User'), ROOT('Users')
    );
    -- Format looks like: <Users><User><Id>1</Id><UserName>Bob</UserName></User>...</Users>

    EXEC dbo.ChildSP_XML @Payload = @XmlData;
END

```

**Child SP:**

```sql
CREATE PROCEDURE dbo.ChildSP_XML
    @Payload XML
AS
BEGIN
    -- Shred XML back to a Table format
    SELECT
        T.c.value('(Id)[1]', 'INT') AS UserId,
        T.c.value('(UserName)[1]', 'VARCHAR(50)') AS Name
    FROM @Payload.nodes('/Users/User') AS T(c);
END

```

---

# 🥉 Option 3: "Process Keyed" Staging Table

If the data is too massive for XML parsing, you use a standard permanent table that acts as a buffer.

**How it works:**

1. Create a permanent table `Staging_ProcessData`.
2. Add a `SessionGUID` (UniqueIdentifier) column.
3. Parent Generates a GUID, inserts data tagged with that GUID.
4. Parent passes *only the GUID* to the Child.
5. Child selects `WHERE SessionGUID = @Guid`.

**Pros:** Easy to debug (data is persistent).
**Cons:** Bloats transaction log; requires cleanup jobs.

**Structure:**

```sql
-- One time setup
CREATE TABLE GlobalStagingTable (
    ProcessId UNIQUEIDENTIFIER, -- The Key
    DataColumn1 VARCHAR(50),
    DataColumn2 INT
);
CREATE CLUSTERED INDEX IX_Staging ON GlobalStagingTable(ProcessId);

```

**Parent SP:**

```sql
CREATE PROC ParentSP
AS
BEGIN
    DECLARE @MyBatchID UNIQUEIDENTIFIER = NEWID();

    INSERT INTO GlobalStagingTable (ProcessId, DataColumn1, DataColumn2)
    SELECT @MyBatchID, Name, Age FROM SourceTable;

    EXEC ChildSP @BatchID = @MyBatchID;

    -- Cleanup after return
    DELETE FROM GlobalStagingTable WHERE ProcessId = @MyBatchID;
END

```

---

# ⚠️ Option 4: Global Temp Tables (`##Table`)

*Not Recommended, but possible.*

Using `##Table` (double hash) allows data to be seen by the Child SP. However, unlike `#Local`, this is seen by **every connection**.

- **Risk:** If two users run `ParentSP` at the exact same time, User B might Drop the table while User A is reading it, or User B receives User A's data.
- **Workaround:** You have to name the table dynamically using Dynamic SQL (e.g., `##MyTable_User123`), which makes the code messy and prone to injection attacks. **Avoid this if possible.**

---

# 🚧 Option 5: Delimited String (The "List" approach)

If you only need to pass a **List of IDs** (not complex multi-column data), you can pass a CSV string.

**Note:** SQL 2008 **does not** have `STRING_SPLIT`. You must create a custom Function to split the string.

**Parent SP:**

```sql
DECLARE @IdList VARCHAR(MAX) = '1,5,10,20,500';
EXEC ChildSP @Ids = @IdList;

```

**Child SP:**

```sql
CREATE PROC ChildSP @Ids VARCHAR(MAX)
AS
BEGIN
    -- Using a custom XML trick to split strings in SQL 2008
    DECLARE @xml XML = CAST('<x>' + REPLACE(@Ids, ',', '</x><x>') + '</x>' AS XML);

    SELECT N.value('.', 'INT') AS Id
    FROM @xml.nodes('x') AS T(N);
END

```

### Recommendation

1. **#Local Temp Table:** Use this 95% of the time. It performs best.
2. **XML:** Use this if you need encapsulation (not relying on hidden table dependencies) and data volume is moderate.