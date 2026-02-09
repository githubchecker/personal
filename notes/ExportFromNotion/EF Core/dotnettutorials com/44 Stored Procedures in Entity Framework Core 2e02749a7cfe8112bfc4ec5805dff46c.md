# 44. Stored Procedures in Entity Framework Core

# Stored Procedures and Raw SQL

While EF Core’s LINQ provider is powerful, there are scenarios where hand-written SQL or existing **Stored Procedures** (SPs) are required for performance or complex logic. EF Core provides two primary sets of methods for these tasks: one for fetching data (Queries) and another for data manipulation (Commands).

---

### Summary of Execution Methods

| Method Type | Method Name | Use Case | Returns |
| --- | --- | --- | --- |
| **Query** | `FromSqlInterpolated` | SPs or SQL that return rows. | `IQueryable<T>` |
| **Command** | `ExecuteSqlInterpolated` | `INSERT`, `UPDATE`, `DELETE`, or SPs with no results. | Rows Affected |

---

### 1. Fetching Data with Stored Procedures

To map a procedure’s output directly back into your entity objects, use `FromSqlInterpolated`.

```csharp
var minAge = 18;
// Secure: Parameters are automatically handled
var students = await context.Students
    .FromSqlInterpolated($"EXEC spGetStudentsByAge {minAge}")
    .ToListAsync();
```

**Constraints on Queries:**
* **Column Matching:** The SP must return all columns that match the configuration of the entity type.
* **No Composition:** You cannot chain LINQ operators like `.OrderBy()` or `.Where()` after a Stored Procedure call; the SQL is executed exactly as defined.
* **No Joins:** Stored Procedures cannot return related entities via `Include`.

---

### 2. Executing Operations (Commands)

For procedures that modify data (Update, Delete, Insert) without returning a result set, use the `Database` facade.

```csharp
var studentId = 12;
var newBranch = "Mathematics";

int rows = await context.Database.ExecuteSqlInterpolatedAsync(
    $"EXEC spUpdateStudentBranch @Id={studentId}, @Branch={newBranch}"
);
```

---

### 3. Advanced: Output Parameters

String interpolation does not support `OUTPUT` parameters. For these, you must use the `Raw` version and provide explicit `SqlParameter` objects.

```csharp
var idParam = new SqlParameter
{
    ParameterName = "NewId",
    SqlDbType = System.Data.SqlDbType.Int,
    Direction = System.Data.ParameterDirection.Output
};

await context.Database.ExecuteSqlRawAsync(
    "EXEC spInsertUser @Name='Alice', @UserId=@NewId OUTPUT",
    idParam
);

int newId = (int)idParam.Value;
```

---

### Security: Interpolated vs. Raw

- **Interpolated (`$"{val}"`)**: **Recommended**. EF Core treats the interpolated string values as parameters, effectively preventing **SQL Injection**.
- **Raw**: Useful for truly dynamic SQL (e.g., dynamically picking a table name). **Warning:** Never use string concatenation (`"..." + val`) with raw methods, as it exposes the application to SQL injection.

---

### Best Practices

1. **EF Core 8 `SqlQuery`**: If your SP returns data that doesn’t match an entity (e.g., a summary report), use the modern `Database.SqlQuery<T>(...)` method to map directly to a simple DTO/class.
2. **Maintenance**: Stored Procedures are not “tracked” by EF Core. If you change a column name in your code, you must manually update the Stored Procedure in the database.
3. **Migrations**: To include a Stored Procedure in your deployment, add it to a migration using `migrationBuilder.Sql("CREATE PROCEDURE...")`.
4. **Logging**: EF Core logs all raw SQL and SP calls. Monitor these in development to ensure they are executing as expected.