# Sql Server  > 2016

Here is the comprehensive guide on **Passing Large Data** both internally within SQL Server (Parent to Child) and externally from C# ([ADO.NET/EF](http://ado.net/EF) Core) to SQL.

---

# 🔄 Part 1: SQL to SQL (Parent SP to Child SP/Function)

When a Parent Stored Procedure has a large dataset (e.g., 10,000+ rows) that a Child SP needs to process, you have two primary options.

### 1. The Local Temp Table (🏆 The Performance King)

This is the standard, most performant way for **Stored Procedures**.

- **Mechanism:** Parent creates `#Table`. Child references `#Table`.
- **Why?** Passing a temp table name is effectively zero cost (Pointer passing). The data doesn't move.
- **Permissions:** Child SP automatically inherits access to the Parent's local temp tables.

**Parent SP:**

```sql
CREATE PROC dbo.ParentSP
AS
BEGIN
    -- 1. Create and Fill
    CREATE TABLE #ProcessingData (Id INT PRIMARY KEY, Val VARCHAR(100));
    INSERT INTO #ProcessingData SELECT Id, Name FROM LargeTable;

    -- 2. Call Child (No parameters needed!)
    EXEC dbo.ChildSP;

    -- 3. Cleanup
    DROP TABLE #ProcessingData;
END

```

**Child SP:**

```sql
CREATE PROC dbo.ChildSP
AS
BEGIN
    -- ⚠️ Dependency Warning: This SP will crash if run alone
    -- because #ProcessingData won't exist.
    IF OBJECT_ID('tempdb..#ProcessingData') IS NOT NULL
    BEGIN
        SELECT * FROM #ProcessingData; -- Read/Write allowed
    END
END

```

### 2. Table-Valued Parameters (TVP) (👔 The Formal Way)

Best for cleaner interfaces, safety, and passing data to **Functions**.

- **Pros:** Strongly typed. You know exactly what the schema is.
- **Cons:** **Read-Only** inside the destination. You cannot modify rows in a TVP parameter.

**Step A: Create the Type (One Time)**

```sql
CREATE TYPE dbo.MyBigList AS TABLE (
    Id INT PRIMARY KEY,
    Val VARCHAR(100)
);

```

**Step B: The Child SP (Accepts TVP)**

```sql
CREATE PROCEDURE dbo.ChildSP_WithTVP
    @InputData dbo.MyBigList READONLY -- 'READONLY' is mandatory
AS
BEGIN
    SELECT * FROM @InputData;
END

```

**Step C: The Parent SP**

```sql
DECLARE @MyData dbo.MyBigList;

INSERT INTO @MyData (Id, Val)
SELECT Id, Name FROM SourceTable;

EXEC dbo.ChildSP_WithTVP @InputData = @MyData;

```

### 3. Passing Data to Functions

**Functions are restrictive.**

- You **cannot** access `#TempTables` inside a SQL Function.
- **Solution:** You **MUST** use **TVPs** (Table-Valued Parameters).

```sql
CREATE FUNCTION dbo.CalculateTotal (@ListData dbo.MyBigList READONLY)
RETURNS INT
AS
BEGIN
    DECLARE @Total INT;
    SELECT @Total = SUM(Id) FROM @ListData;
    RETURN @Total;
END

```

---

# 💻 Part 2: C# to SQL Server (The Gateway)

Passing 50,000 rows one by one in a loop is a performance killer. Here are the 3 ways to do it in bulk.

### 🥇 Method 1: Table-Valued Parameters (TVP)

**Best for:** Passing data **to a Stored Procedure** for complex logic.
**Speed:** Extremely Fast.

**SQL Side:***(Requires the `CREATE TYPE dbo.MyBigList...` from Part 1 above)*

**C# ([ADO.NET](http://ado.net/)) Side:**

```csharp
// 1. Create a DataTable matching the SQL Type
DataTable dt = new DataTable();
dt.Columns.Add("Id", typeof(int));
dt.Columns.Add("Val", typeof(string));

// Fill it (e.g., from a list)
dt.Rows.Add(1, "Alice");
dt.Rows.Add(2, "Bob");

using (SqlConnection conn = new SqlConnection("ConnectionString..."))
{
    conn.Open();
    using (SqlCommand cmd = new SqlCommand("dbo.ChildSP_WithTVP", conn))
    {
        cmd.CommandType = CommandType.StoredProcedure;

        // 2. Define the Parameter
        SqlParameter tvpParam = cmd.Parameters.AddWithValue("@InputData", dt);
        tvpParam.SqlDbType = SqlDbType.Structured; // Vital!
        tvpParam.TypeName = "dbo.MyBigList";       // Vital: Must match SQL Type name

        cmd.ExecuteNonQuery();
    }
}

```

**C# (EF Core):**
EF Core still struggles with TVPs natively without extra configuration. Usually, you drop to raw SQL:

```csharp
var dtParameter = new SqlParameter("@InputData", dt); -- (Same DataTable as above)
dtParameter.SqlDbType = SqlDbType.Structured;
dtParameter.TypeName = "dbo.MyBigList";

context.Database.ExecuteSqlRaw("EXEC dbo.ChildSP_WithTVP @InputData", dtParameter);

```

### 🥈 Method 2: JSON (The Modern Standard)

**Best for:** Flexible schema, Web APIs, EF Core 7/8+.
**Speed:** Fast, but high CPU usage on SQL Server (Parsing). Slightly slower than TVP for massive data.

**C# Side:**
Simply Serialize your Object List to a string.

```csharp
var myUsers = new List<User> { ... };
string jsonString = JsonSerializer.Serialize(myUsers);

// Pass as standard NVARCHAR(MAX)
cmd.Parameters.AddWithValue("@JsonInput", jsonString);

```

**SQL Side (Stored Procedure):**
Use `OPENJSON` to convert text back to a table.

```sql
CREATE PROC dbo.ImportJsonUsers
    @JsonInput NVARCHAR(MAX)
AS
BEGIN
    INSERT INTO Users (Name, Age)
    SELECT Name, Age
    FROM OPENJSON(@JsonInput)
    WITH (
        Name VARCHAR(50) '$.Name',
        Age INT '$.Age'
    );
END

```

### 🥉 Method 3: SqlBulkCopy (The Speed of Light)

**Best for:** Just dumping data into a table.
**Cons:** You cannot run logic *while* inserting. It just inserts.
**Pattern:** Bulk Insert to a "Staging Table" -> Call SP to process Staging Table.

```csharp
using (SqlBulkCopy bulk = new SqlBulkCopy(connectionString))
{
    bulk.DestinationTableName = "dbo.StagingTable";

    // Optional: Mappings if names differ
    bulk.ColumnMappings.Add("SourceId", "DestId");

    // Write directly from DataTable or DataReader
    bulk.WriteToServer(myDataTable);
}
// Call SP afterwards to process the data

```

---

# 📊 Summary Decision Matrix

| Source | Target | Scenario | Best Solution |
| --- | --- | --- | --- |
| **Parent SP** | **Child SP** | 10k+ rows, need Read/Write | **#TempTable** |
| **Parent SP** | **Child SP** | Strict Interface / Read-Only | **TVP** |
| **Parent SP** | **Function** | Any Data | **TVP** (Only option) |
| **C#** | **SP** | Need to run logic (Merge/Update) | **TVP** (Recommended) |
| **C#** | **SP** | Flexible schema / Web App | **JSON** |
| **C#** | **Table** | Raw Data Dump (Millions of rows) | **SqlBulkCopy** |