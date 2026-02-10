# 9. Database functions

# Database Functions

Database functions are the equivalent of C# methods executed on the database server. EF Core translates LINQ calls into these functions to optimize performance and leverage database-specific logic.

## 1. Automatic Built-in Mappings

EF Core automatically translates many standard .NET methods into their SQL counterparts.

| .NET Method | SQL (SQL Server) |
| --- | --- |
| `string.ToLower()` | `LOWER()` |
| `string.Length` | `LEN()` |
| `Math.Abs(x)` | `ABS()` |
| `DateTime.Now` | `GETDATE()` |
| `??` (Coalesce) | `COALESCE()` |

## 2. `EF.Functions` (Provider-Specific)

`EF.Functions` provides access to database-specific functions that have no direct .NET equivalent. These are defined as extension methods and can only be used in LINQ queries.

```csharp
// Use SQL LIKE for pattern matching
var blogs = await context.Blogs
    .Where(b => EF.Functions.Like(b.Url, "http://%dotnet%"))
    .ToListAsync();

// Use Free-Text Search (SQL Server specific)
var posts = await context.Posts
    .Where(p => EF.Functions.FreeText(p.Content, "database performance"))
    .ToListAsync();

```

## 3. Categories of Functions

- **Scalar Functions:** Take primitive values and return a single value (e.g., `Math.Round`).
- **Aggregate Functions:** Operate on a collection of rows and return a summary value (e.g., `Count`, `Sum`).
- **Table-Valued Functions (TVF):** Return a set of rows and are used in the `FROM` clause of a query.
- **Niladic Functions:** Parameter-less functions invoked without parentheses (e.g., `USER_NAME()` in some dialects).

## 4. User-Defined Functions (UDFs)

You can map custom C# methods to your own functions defined in the database.

- **Define a Method:** Add a static method to your `DbContext`.
- **Register in** `OnModelCreating`**:**

```csharp
modelBuilder.HasDbFunction(typeof(MyDbContext).GetMethod(nameof(GetPostCount)))
    .HasName("fn_GetPostCount");

```

- **Usage:**

```csharp
var authors = await context.Authors
    .Select(a => new { a.Name, Posts = MyDbContext.GetPostCount(a.Id) })
    .ToListAsync();

```

## 5. Key Takeaways

- **Server-Side Execution:** Database functions run on the server, minimizing the amount of data transferred to the client.
- **Provider Dependencies:** `EF.Functions` are often provider-specific and will throw an exception if used with an unsupported database.
- **Null Handling:** C# and SQL often have different null logic; EF Core attempts to bridge this gap during translation.