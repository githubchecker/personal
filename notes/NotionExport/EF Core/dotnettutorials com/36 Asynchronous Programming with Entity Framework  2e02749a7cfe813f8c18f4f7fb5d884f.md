# 36. Asynchronous Programming with Entity Framework Core

# Asynchronous Programming in EF Core

Asynchronous programming is essential for building scalable and responsive applications. It allows your application to perform I/O-bound tasks (like database queries) without blocking the thread that initiated the request.

---

### Why Use Async?

- **Scalability**: In ASP.NET Core, async allow threads to return to the thread pool while waiting for the database, enabling the server to handle significantly more concurrent requests.
- **Responsiveness**: In UI applications (WPF/WinForms/MAUI), it prevents the “frozen” UI state during long-running database operations.
- **Throughput**: Allows for better utilization of system resources during high-traffic periods.

---

### Common Async Methods in EF Core

EF Core provides asynchronous versions of almost all methods that result in a database command. These methods are located in the `Microsoft.EntityFrameworkCore` namespace.

| Synchronous | Asynchronous Equivalent |
| --- | --- |
| `ToList()` | `ToListAsync()` |
| `FirstOrDefault()` | `FirstOrDefaultAsync()` |
| `Single()` | `SingleAsync()` |
| `Count()` | `CountAsync()` |
| `Any()` | `AnyAsync()` |
| `SaveChanges()` | `SaveChangesAsync()` |
| `Add()` | `AddAsync()`* |
- *Note: `AddAsync` is rarely needed (usually for specific key-generation scenarios). For most cases, the synchronous `Add` is preferred as it only interacts with the local context.*

---

### Implementation Example

```csharp
public async Task<List<Product>> GetActiveProductsAsync()
{
    await using var context = new MyDbContext();

    // The thread is released back to the pool while the DB executes the query
    return await context.Products
        .Where(p => p.IsActive)
        .ToListAsync();
}

public async Task UpdatePriceAsync(int id, decimal newPrice)
{
    await using var context = new MyDbContext();

    var product = await context.Products.FindAsync(id);
    if (product != null)
    {
        product.Price = newPrice;
        // Non-blocking save operation
        await context.SaveChangesAsync();
    }
}
```

---

### Critical Warning: No Thread-Safety

EF Core `DbContext` is **not thread-safe**. You cannot start multiple asynchronous operations on the same context instance at the same time.

```csharp
// ❌ WRONG: This will throw an InvalidOperationException
var task1 = context.Products.ToListAsync();
var task2 = context.Orders.ToListAsync();
await Task.WhenAll(task1, task2);

// ✅ RIGHT: Use separate context instances or execute sequentially
var products = await context.Products.ToListAsync();
var orders = await context.Orders.ToListAsync();
```

---

### Cancellation Support

All EF Core async methods accept a `CancellationToken`. This is crucial for web applications to stop database execution if the user navigates away or cancels the request.

```csharp
public async Task<List<Product>> SearchAsync(string term, CancellationToken ct)
{
    return await context.Products
        .Where(p => p.Name.Contains(term))
        .ToListAsync(ct);
}
```

---

### Best Practices

1. **Async All The Way**: Avoid “Sync over Async” (calling `.Result` or `.Wait()`), as this can lead to deadlocks. Use `await` throughout the entire call stack.
2. **Use `await using`**: Use the asynchronous disposal provided by EF Core to release resources efficiently.
3. **Find vs. Single**: Use `FindAsync` when you need to find an entity by its primary key, as it first checks the local memory before querying the database.
4. **Performance**: Async programming slightly increases overhead for very tiny, fast queries, but the scalability benefits in multi-user environments far outweigh this.