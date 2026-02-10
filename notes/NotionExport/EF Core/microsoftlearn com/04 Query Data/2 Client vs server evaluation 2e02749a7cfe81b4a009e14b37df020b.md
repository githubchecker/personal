# 2. Client vs. server evaluation

# Client vs. Server Evaluation

EF Core attempts to evaluate as much of a query as possible on the database server. However, some logic (like custom C# methods) cannot be translated to SQL and must be executed on the client (in-memory).

## 1. The Rule (EF Core 3.0+)

- **Server Evaluation:** Everything in `.Where()`, `.OrderBy()`, `.Join()`, etc., **must** be translatable to SQL. If EF Core encounters something it cannot translate, it throws a runtime exception.
- **Client Evaluation:** Occurs **only** in the final `.Select()` projection.

### Allowed: Client Eval in Projection

```csharp
var blogs = await context.Blogs
    .OrderByDescending(b => b.Rating)
    .Select(b => new { 
        Id = b.Id, 
        UserFriendlyUrl = StandardizeUrl(b.Url) // Native C# method call
    })
    .ToListAsync();

```

### Prohibited: Client Eval in Filter

```csharp
// This throws an exception because StandardizeUrl cannot be translated to SQL
var blogs = await context.Blogs
    .Where(b => StandardizeUrl(b.Url).Contains("dotnet"))
    .ToListAsync();

```

## 2. Forcing Client Evaluation

If a query operator has no SQL translation or you have a small dataset, you can explicitly move evaluation to the client by calling `.AsEnumerable()` or `.AsAsyncEnumerable()`.

```csharp
var blogs = await context.Blogs
    .AsAsyncEnumerable() // Everything after this runs on the client
    .Where(b => StandardizeUrl(b.Url).Contains("dotnet"))
    .ToListAsync();

```

<aside>
⚠️ **Performance Warning:** Forcing client evaluation pulls all rows from the database into memory before filtering. Only do this if the data set is small or you have no other choice.

</aside>

## 3. Avoiding Memory Leaks

EF Core caches compiled query plans. If your client-side projection references instance data or complex constants, they might be held in memory indefinitely.

- **Prefer Static Methods:** Use `static` methods for projection logic to avoid capturing the whole instance of a class.
- **Pass Scalar Arguments:** Instead of passing a whole object to a method in `Select`, pass only the specific primitive values required.

## 4. Summary

| Aspect | Server Evaluation | Client Evaluation |
| --- | --- | --- |
| **Location** | Where, OrderBy, Join, GroupBy | **Only in final Select** |
| **Translation** | Translated to SQL | Executed in .NET |
| **Performance** | High (filtered at source) | Low (all data transferred) |
| **Error Handling** | Throws if untranslatable | Handled by C# runtime |