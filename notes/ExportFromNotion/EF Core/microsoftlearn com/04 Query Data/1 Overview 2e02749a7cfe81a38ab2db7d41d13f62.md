# 1. Overview

# Querying Data Overview

Entity Framework Core utilizes **LINQ (Language-Integrated Query)** to interact with the database. This allows you to write strongly-typed queries in C# that are automatically translated by database providers into SQL (for relational databases) or other appropriate query languages.

## 1. How it Works

- **LINQ Expression:** You write a query using C# syntax (e.g., `.Where()`, `.Select()`).
- **Translation:** EF Core's query engine translates the LINQ expression into a database-specific command.
- **Execution:** The command is sent to the database. Results are streamed back and materialized into C# objects (entities).
- **Tracking:** By default, returned entities are tracked by the `DbContext` for future updates.

## 2. Common Query Patterns

### Loading All Entities

```csharp
var blogs = await context.Blogs.ToListAsync();

```

### Loading a Single Entity

- `SingleAsync`: Throws an exception if 0 or >1 matches are found.
- `FirstAsync` **/** `FirstOrDefaultAsync`: Returns the first match or null.

```csharp
var blog = await context.Blogs.FirstOrDefaultAsync(b => b.Id == 1);

```

### Filtering and Projection

```csharp
var dotnetBlogs = await context.Blogs
    .Where(b => b.Url.Contains("dotnet")) // Filter
    .Select(b => new { b.Title, b.Url })    // Project (Optimization)
    .ToListAsync();

```

## 3. Key Concepts to Remember

- **Deferred Execution:** The query is not executed until you iterate over the results (e.g., using `foreach`) or call a terminal method like `ToList`, `Count`, or `First`.
- **Server-Side Execution:** EF Core attempts to execute as much logic as possible on the database server to minimize data transfer.
- **Freshness:** Queries always hit the database to get the latest data, even if the entity already exists in the local `DbContext` cache.