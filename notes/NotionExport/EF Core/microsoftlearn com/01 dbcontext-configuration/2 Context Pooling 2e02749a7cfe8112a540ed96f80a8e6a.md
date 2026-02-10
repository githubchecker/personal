# 2. Context Pooling

# Advanced EF Core Performance Topics

This guide covers advanced techniques to optimize EF Core performance, including context pooling, query compilation, and model optimization.

## 1. DbContext Pooling

Instantiating a `DbContext` is generally light, but in extreme high-performance scenarios, the setup overhead of internal services can be significant. **DbContext Pooling** allows EF Core to reuse context instances, paying the setup cost only once at startup.

### registration in ASP.NET Core:

Replace `AddDbContext` with `AddDbContextPool`.

```csharp
builder.Services.AddDbContextPool<WeatherForecastContext>(
    o => o.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

```

- **poolSize:** Limits the number of instances retained (default: 1024).

### State Management Warning:

Pooled contexts are effectively singletons across requests. `OnConfiguring` is only called once. If your context depends on request-specific state (like a Tenant ID), use an `IDbContextFactory` to manually inject state into pooled instances.

## 2. Compiled Queries

EF Core caches queries by their expression tree shape. However, finding the correct cached query still involves a recursive comparison of the tree. **Compiled Queries** bypass this lookup by explicitly compiling a LINQ query into a .NET delegate.

### Usage:

```csharp
// Define the compiled query once
private static readonly Func<BloggingContext, int, IAsyncEnumerable<Blog>> _compiledQuery
    = EF.CompileAsyncQuery((BloggingContext context, int length) 
        => context.Blogs.Where(b => b.Url.StartsWith("http://") && b.Url.Length == length));

// Invoke the delegate
await foreach (var blog in _compiledQuery(context, 8)) { ... }

```

## 3. Query Parameterization

Query parameterization ensures that queries with the same structure reuse the same cached compilation and database query plan.

### Example:

- **Avoid (Constants):** `context.Posts.Where(p => p.Title == "post1")` leads to re-compilation for every new title.
- **Prefer (Parameters):** `context.Posts.Where(p => p.Title == postTitle)` compiles once and uses a SQL parameter.

<aside>
ℹ️ Constant queries are fine for values that never change, but dynamic values should always be parameterized to avoid "Plan Cache Pollution."

</aside>

## 4. Compiled Models

For apps with hundreds of entities, model initialization can slow down the first database operation. **Compiled Models** pre-build the EF model at design-time to eliminate this runtime cost.

### Generation:

```bash
dotnet ef dbcontext optimize

```

### Usage:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .UseModel(MyCompiledModels.BlogsContextModel.Instance)
        .UseSqlite(@"Data Source=test.db");

```

- **Limitations:** Global query filters, lazy loading, and change-tracking proxies are **not supported** in compiled models.

## 5. Dynamically-Constructed Queries

When building queries at runtime via the `Expression` API, ensure you use **Parameter Nodes** instead of **Constants**.

- **Wrong:** `Expression.Constant(url)` causes re-compilation every time `url` changes.
- **Right:** Wrap the value in a lambda to create a parameter node that EF Core can recognize.

## 6. Reducing Runtime Overhead

For ultra-low-latency applications, consider these extreme optimizations:

- **Disable Thread Safety Checks:** Setting `EnableThreadSafetyChecks` to false saves a small amount of overhead (Use only if you are 100% sure your threading is correct).
- **PooledDbContextFactory:** Using the factory directly avoids the slight DI overhead of `AddDbContextPool`.
- **Memory Cache Limit:** EF Core uses `IMemoryCache` (default 10,240 items) for query/model caching. Scale this via `AddMemoryCache` if needed.