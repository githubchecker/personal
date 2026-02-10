# 8. SQL queries

# SQL Queries

EF Core allows you to execute raw SQL queries when LINQ is insufficient or you need to call database-specific features like stored procedures.

## 1. Querying Entities (`FromSql`)

The `FromSql` method starts a LINQ query based on raw SQL. Results can be tracked and composed upon.

```csharp
var blogs = await context.Blogs
    .FromSql($"SELECT * FROM dbo.Blogs WHERE Rating > {minRating}")
    .Include(b => b.Posts)
    .ToListAsync();

```

### Key Variations

- `FromSql`: Recommended for most cases using string interpolation (Safe from SQL injection).
- `FromSqlInterpolated`: Explicit version for older EF Core versions.
- `FromSqlRaw`: Used for dynamic SQL or when parameters cannot be used (e.g., dynamic table names). **Warning:** Highly vulnerable to SQL injection if used improperly.

## 2. Querying Scalars (`SqlQuery`)

Use `Database.SqlQuery` to retrieve non-entity types (e.g., primitive types or simple objects).

```csharp
var ids = await context.Database
    .SqlQuery<int>($"SELECT BlogId FROM Blogs")
    .ToListAsync();

```

<aside>
💡 **LINQ Composition:** If you want to chain LINQ operators after `SqlQuery`, you must alias the SQL result column as `Value`.

</aside>

## 3. Executing Commands (`ExecuteSql`)

Use `ExecuteSql` for commands that do not return data, such as `UPDATE`, `DELETE`, or calls to non-querying stored procedures.

```csharp
int rowsAffected = await context.Database
    .ExecuteSqlAsync($"UPDATE Blogs SET Rating = 5 WHERE Url LIKE '%dotnet%'");

```

## 4. Parameterization and Security

Always prefer interpolated strings (`$"..."`) with `FromSql` or `ExecuteSql`. EF Core automatically converts these into database parameters, preventing SQL injection.

```csharp
var user = "johndoe";
// SAFE: 'user' is parameterized
context.Blogs.FromSql($"SELECT * FROM Blogs WHERE Author = {user}"); 

// UNSAFE: String concatenation is vulnerable
context.Blogs.FromSqlRaw("SELECT * FROM Blogs WHERE Author = '" + user + "'");

```

## 5. Summary and Limitations

| Feature | Returns Entities? | Compasable? | Best For |
| --- | --- | --- | --- |
| `FromSql` | Yes | Yes (if SELECT) | Complex entity reads. |
| `SqlQuery` | No | Yes (via `Value`) | Scalar returns (Int, String). |
| `ExecuteSql` | No | No | Updates / Deletes. |

### Limitations

- **Column Mapping:** SQL results must return columns that exactly match the entity property mappings.
- **All Properties:** The query must return data for **all** mapped properties of the entity.
- **Subqueries:** LINQ composition on top of SQL only works if the SQL is a single `SELECT` statement that can be wrapped as a subquery.