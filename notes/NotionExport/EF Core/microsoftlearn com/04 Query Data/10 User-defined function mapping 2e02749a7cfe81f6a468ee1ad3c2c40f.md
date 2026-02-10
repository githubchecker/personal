# 10. User-defined function mapping

# User-Defined Function (UDF) Mapping

EF Core allows you to bridge the gap between C# code and custom SQL functions defined in your database. This enables calling complex database logic directly within LINQ queries.

## 1. Mapping Scalar Functions

To map a standard SQL scalar function:

- **Define a C# Method:** Add a method (usually static or on your `DbContext`) that returns the appropriate scalar type. The body should typically throw a `NotSupportedException` as it's only used for translation.
- **Configure in** `OnModelCreating`**:** Use `HasDbFunction` to link the method to the SQL function name.

```csharp
// C# placeholder
public int GetActivePostCount(int blogId) => throw new NotSupportedException();

// Mapping
modelBuilder.HasDbFunction(typeof(MyDbContext).GetMethod(nameof(GetActivePostCount)))
    .HasName("fn_CommentedPostCount")
    .HasSchema("dbo");

```

## 2. Table-Valued Functions (TVF)

TVFs return a result set (rows) rather than a single value. These are used in the `FROM` clause of a query and support further LINQ composition.

### Implementation

```csharp
// Define the C# method returning IQueryable
public IQueryable<Post> GetPopularPosts(int minLikes)
    => FromExpression(() => GetPopularPosts(minLikes));

// Configure the mapping
modelBuilder.HasDbFunction(typeof(MyDbContext).GetMethod(nameof(GetPopularPosts), new[] { typeof(int) }));

```

### Usage

```csharp
var posts = await context.GetPopularPosts(10)
    .Where(p => p.Title.Contains("EF Core"))
    .OrderBy(p => p.Rating)
    .ToListAsync();

```

## 3. Custom SQL Translation (`HasTranslation`)

Instead of calling a physical DB function, you can provide a custom SQL expression tree. This "inlines" the logic directly into the generated SQL command.

```csharp
modelBuilder.HasDbFunction(methodInfo)
    .HasTranslation(args =>
        new SqlBinaryExpression(
            ExpressionType.Add,
            args[0],
            new SqlConstantExpression(10, ...),
            typeof(int),
            null));

```

## 4. Performance: Propagating Nullability

If a function returns `NULL` only when its arguments are `NULL`, you can inform EF Core using `PropagatesNullability()`. This allows EF Core to simplify the generated SQL by omitting redundant null checks.

```csharp
modelBuilder.HasDbFunction(methodInfo, b =>
{
    b.HasParameter("input").PropagatesNullability();
});

```

## 5. Summary Table

| Function Type | C# Return Type | SQL Usage | Composable? |
| --- | --- | --- | --- |
| **Scalar** | `int`, `string`, etc. | `SELECT ...`, `WHERE ...` | No |
| **Table-Valued** | `IQueryable<T>` | `FROM (...)` | **Yes** |
| **Translation** | Any scalar | Inlined Logic | No |