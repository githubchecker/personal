# 11. Global query filters

# Global Query Filters

**Global Query Filters** are LINQ predicates applied automatically to all queries for a specific entity type. They are commonly used for **Soft Deletes** and **Multi-Tenancy**.

## 1. Using Query Filters

### Soft Deletes

Instead of permanently deleting data, you can set a flag and filter it out by default.

```csharp
// Model
public class Blog {
    public int Id { get; set; }
    public bool IsDeleted { get; set; }
}

// Configuration
modelBuilder.Entity<Blog>().HasQueryFilter(b => !b.IsDeleted);

// Usage: Blogs where IsDeleted is true are automatically excluded
var blogs = await context.Blogs.ToListAsync();

```

### Multi-Tenancy

Ensure users only see data belonging to their organization by referencing a property on the `DbContext`.

```csharp
modelBuilder.Entity<TenantData>().HasQueryFilter(t => t.TenantId == _currentTenantId);

```

## 2. Managing Multiple Filters

- **Pre-EF Core 10:** You can only define **one** filter per entity. To use multiple criteria, combine them with the `&&` operator.
- **EF Core 10+:** Support for **Named Filters** allows you to add multiple independent filters to a single entity.

## 3. Disabling Filters

To bypass all global filters for a specific query, use `IgnoreQueryFilters()`.

```csharp
// Returns ALL blogs, including soft-deleted ones
var allBlogs = await context.Blogs.IgnoreQueryFilters().ToListAsync();

```

*Note: In EF Core 10+, you can selectively ignore specific named filters:* `.IgnoreQueryFilters(["DeletedFilter"])`*.*

## 4. Important Considerations (Gotchas)

### Required Navigations and Inner Joins

If an entity has a required relationship (mapped via `INNER JOIN`) to a filtered entity, the parent entity will also be hidden if the child is filtered out.

**Solution:**

- Make the navigation **optional** (uses `LEFT JOIN`).
- Apply a consistent query filter to both the parent and child entities.

### Performance

EF Core applies these filters during translation. Ensure the columns used in filters (like `IsDeleted` or `TenantId`) are **indexed** to maintain query performance.

## 5. Limitations

- **Inheritance:** Filters can only be defined on the **root entity** of an inheritance hierarchy.
- **Cycles:** Avoid defining filters that reference each other in a circular way, as this can lead to infinite loops during query translation.