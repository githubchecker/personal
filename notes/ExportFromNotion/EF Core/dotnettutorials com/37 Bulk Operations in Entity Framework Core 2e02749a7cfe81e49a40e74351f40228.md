# 37. Bulk Operations in Entity Framework Core

# Bulk Operations in EF Core

When working with large datasets, processing records individually creates performance bottlenecks due to excessive database round-trips and change-tracking memory consumption. EF Core provides several mechanisms to optimize these operations.

---

### 1. Command Batching (Automatic)

EF Core automatically groups multiple `INSERT`, `UPDATE`, or `DELETE` commands into a single round-trip when you call `SaveChanges()`.
* **Default Batch Size**: For SQL Server, the default is **42** statements per batch.
* **Customization**: You can adjust this in your `DbContext` configuration.

```csharp
optionsBuilder.UseSqlServer(connectionString, sqlOptions =>
{
    sqlOptions.MaxBatchSize(100);
});
```

---

### 2. Set-Based Operations (EF Core 7.0+)

The most significant advancement in recent EF Core versions is the introduction of **ExecuteUpdate** and **ExecuteDelete**. These allow you to perform bulk modifications directly in the database without loading entities into memory.

### Bulk Delete

Deletes all matching records in a single SQL statement.

```csharp
// Deletes all inactive products directly in the DB
await context.Products
    .Where(p => !p.IsActive)
    .ExecuteDeleteAsync();
```

### Bulk Update

Updates specific properties for all matching records in a single SQL statement.

```csharp
// Increases prices by 10% for a specific category
await context.Products
    .Where(p => p.Category == "Electronics")
    .ExecuteUpdateAsync(s => s.SetProperty(p => p.Price, p => p.Price * 1.1m));
```

---

### 3. Bulk Inserts with `AddRange`

`AddRange` batches your inserts into groups (e.g., using the `MERGE` statement in SQL Server). However, it still adds every entity to the **Change Tracker**, which can consume significant memory for very large collections.

```csharp
var newProducts = new List<Product> { /* 1000 items */ };
context.Products.AddRange(newProducts);
await context.SaveChangesAsync();
```

---

### Comparison: Tracking vs. Set-Based Operations

| Feature | `SaveChanges()` (Tracking) | `ExecuteUpdate/Delete` (Set-Based) |
| --- | --- | --- |
| **Performance** | Slower (Overhead per row) | **Ultra-Fast** (Single command) |
| **Memory Usage** | High (Change tracking) | **Low** (No tracking) |
| **Concurrency** | Supports Concurrency Tokens | **Ignored** (Direct DB change) |
| **Audit/Logic** | C# logic/events triggered | Database-level only |

---

### When to Use External Libraries?

For massive data ingestion (e.g., millions of rows), even `AddRange` can be slow. Libraries like `EFCore.BulkExtensions` utilize the database-specific bulk copy utilities (e.g., `SqlBulkCopy` for SQL Server) to achieve maximum possible throughput.

---

### Best Practices for Large Data Imports

1. **Disable Change Tracking**: If you must use `AddRange` for thousands of items, disable automatic detection to save CPU cycles:
`context.ChangeTracker.AutoDetectChangesEnabled = false;`
2. **Manual Partitioning (Chunking)**: For massive imports, save changes in smaller chunks and clear the tracker to free up RAM.

```csharp

foreach (var batch in largeDataList.Chunk(1000))
{
    context.Products.AddRange(batch);
    await context.SaveChangesAsync();
    context.ChangeTracker.Clear(); // Free memory for the next batch
}
```

1. **Prefer Set-Based**: Use `ExecuteDelete` and `ExecuteUpdate` whenever possible for bulk maintenance tasks.