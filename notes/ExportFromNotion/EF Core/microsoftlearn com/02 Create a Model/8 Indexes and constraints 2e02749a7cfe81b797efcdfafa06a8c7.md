# 8. Indexes and constraints

# Indexes and Constraints

Indexes improve lookup performance, while constraints ensure data integrity. EF Core allows you to configure both using Data Annotations or the Fluent API.

## 1. Indexes

By default, EF Core creates indexes for all **Foreign Keys**. You can define additional indexes explicitly.

### Basic and Composite Indexes

- **Single Column:** `.HasIndex(b => b.Url)`
- **Composite Index:** `.HasIndex(p => new { p.FirstName, p.LastName })`

### Unique Indexes

Enforce uniqueness on a column or set of columns.

```csharp
[Index(nameof(Url), IsUnique = true)]
public class Blog { ... }

// OR Fluent API
modelBuilder.Entity<Blog>()
    .HasIndex(b => b.Url)
    .IsUnique();

```

### Sort Order

Specify ascending (default) or descending order for index columns.

```csharp
modelBuilder.Entity<Blog>()
    .HasIndex(b => new { b.Url, b.Rating })
    .IsDescending(false, true); // Ascending for Url, Descending for Rating

```

## 2. Advanced Index Features (Provider-Specific)

### Index Filters (SQL Server)

Create a **Partial Index** by indexing only a subset of rows.

```csharp
modelBuilder.Entity<Blog>()
    .HasIndex(b => b.Url)
    .HasFilter("[Url] IS NOT NULL");

```

### Included Columns (SQL Server)

Include non-key columns in the index to allow "index-only" queries (Covering Indexes).

```csharp
modelBuilder.Entity<Post>()
    .HasIndex(p => p.Url)
    .IncludeProperties(p => new { p.Title, p.PublishedOn });

```

## 3. Constraints

### Check Constraints

Define arbitrary conditions that must be met for every row in a table.

```csharp
modelBuilder.Entity<Product>()
    .ToTable(t => t.HasCheckConstraint("CK_Product_Discount", "[Price] > [DiscountedPrice]"));

```

## 4. Configuration Summary

| Feature | Attribute | Fluent API |
| --- | --- | --- |
| **Index** | `[Index(nameof(Prop))]` | `.HasIndex(e => e.Prop)` |
| **Unique** | `IsUnique = true` | `.IsUnique()` |
| **Descending** | `IsDescending = true` | `.IsDescending()` |
| **Index Name** | `Name = "IX_Custom"` | `.HasDatabaseName("IX_Custom")` |
| **Filter** | N/A | `.HasFilter("...")` |
| **Included Cols** | N/A | `.IncludeProperties(...)` |
| **Check Constraint** | N/A | `.HasCheckConstraint(...)` |