# 52. Global Query Filters in Entity Framework Core

# Global Query Filters in EF Core

**Global Query Filters** allow you to define a LINQ query predicate that EF Core automatically applies to all queries targeting a specific entity type. These filters are configured at the model level (in `OnModelCreating`) and ensure consistent data isolation without requiring manual `.Where()` clauses in every query.

---

### Primary Use Cases

- **Soft Delete:** Ensuring that records marked as “deleted” are hidden from standard application views.
- **Multi-tenancy:** Automatically restricting a user’s access to only the data belonging to their `TenantId`.
- **Access Control:** Restricting visibility based on user roles or record status (e.g., “Published” vs “Draft”).

---

### 1. Basic Implementation (Soft Delete)

A common pattern is implementing a soft delete using an `IsDeleted` flag.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    // Automatically adds 'WHERE IsDeleted = 0' to every query on the Order table
    modelBuilder.Entity<Order>()
        .HasQueryFilter(o => !o.IsDeleted);
}
```

---

### 2. Parameterized Filters (Multi-tenancy)

Global filters can reference properties defined inside your `DbContext`. This allows you to set a value (like a `TenantId`) at runtime when the context is initialized.

```csharp
public class MyDbContext : DbContext
{
    private readonly int _currentTenantId;

    public MyDbContext(int tenantId) => _currentTenantId = tenantId;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Enforces that users only see data belonging to their specific tenant
        modelBuilder.Entity<Customer>()
            .HasQueryFilter(c => c.TenantId == _currentTenantId);
    }
}
```

---

### 3. Bypassing Filters

There are scenarios where you need to see all records, regardless of the filter (e.g., an admin dashboard or a data recovery tool). Use the `.IgnoreQueryFilters()` extension method.

```csharp
// Returns all orders, including those marked as deleted
var allOrders = await context.Orders
    .IgnoreQueryFilters()
    .ToListAsync();
```

---

### 4. Combining Multiple Filters

You can combine multiple logical conditions into a single filter using standard C# operators.

```csharp
modelBuilder.Entity<Order>()
    .HasQueryFilter(o => !o.IsDeleted && o.TenantId == _currentTenantId);
```

---

### Key Considerations

1. **Navigation Properties:** If you use `.Include()` to load related data, the global filters of the *related* entities are also applied.
2. **Raw SQL Limitation:** Global filters **do not** apply to raw SQL queries performed via `.FromSqlRaw()` or `.FromSqlInterpolated()`. You must replicate the filtering logic inside your SQL string.
3. **Indexing:** Because every query will now include a `WHERE` clause on the filtered column (e.g., `IsDeleted`), you should **add an index** to that column to avoid full table scans.
4. **Shadow Properties:** Combining Global Query Filters with **Shadow Properties** is a best practice for cross-cutting concerns like “ModifiedDate” or “IsDeleted”, as it keeps the domain model clean while maintaining database functionality.

---

### Summary Table

| Goal | Technique |
| --- | --- |
| **Apply Filter** | `modelBuilder.Entity<T>().HasQueryFilter(expression)` |
| **Disable Filter** | `query.IgnoreQueryFilters()` |
| **Multi-tenancy** | Use a `DbContext` property inside the filter expression. |
| **Performance** | Ensure filtered columns are indexed in the database. |