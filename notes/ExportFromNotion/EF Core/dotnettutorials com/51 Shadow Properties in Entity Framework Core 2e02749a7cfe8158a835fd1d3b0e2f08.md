# 51. Shadow Properties in Entity Framework Core

# Shadow Properties in EF Core

**Shadow Properties** are properties that exist in the EF Core model and the database schema but are **not defined in your C# entity class**. They allow you to store and retrieve data without polluting your domain models with infrastructure-specific fields.

---

### Common Use Cases

- **Auditing:** Storing `CreatedAt` or `LastModifiedAt` timestamps.
- **Soft Deletes:** Maintaining an `IsDeleted` flag to hide records without removing them.
- **Hidden Foreign Keys:** Maintaining database relationships without exposing the FK property in the C# class.
- **Metadata:** Storing row version numbers or synchronization flags.

---

### 1. Configuration (Fluent API)

Shadow properties can only be configured in the `OnModelCreating` method. You cannot define them using Data Annotations.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    // Define a DateTime shadow property
    modelBuilder.Entity<BlogPost>()
        .Property<DateTime>("LastUpdated");

    // Define a boolean shadow property for soft deletes with a default value
    modelBuilder.Entity<User>()
        .Property<bool>("IsDeleted")
        .HasDefaultValue(false);
}
```

---

### 2. Accessing Shadow Properties

Because these properties are not in the class, you cannot access them via `entity.PropertyName`. Instead, use the `ChangeTracker` or `Entry` API.

### Setting a Value Manually:

```csharp
context.Entry(myPost).Property("LastUpdated").CurrentValue = DateTime.UtcNow;
```

### Automating with SaveChanges (Common Audit Pattern):

The most powerful way to use shadow properties is to automate them by overriding `SaveChanges`.

```csharp
public override int SaveChanges()
{
    var entries = ChangeTracker.Entries()
        .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);

    foreach (var entry in entries)
    {
        // Automatically set the timestamp for modified entities
        entry.Property("LastUpdated").CurrentValue = DateTime.UtcNow;
    }

    return base.SaveChanges();
}
```

---

### 3. Querying Shadow Properties

To refer to a shadow property in a LINQ query, use the `EF.Property<T>` static method.

```csharp
// Filter entities using a shadow property
var deletedUsers = await context.Users
    .Where(u => EF.Property<bool>(u, "IsDeleted") == true)
    .ToListAsync();

// Project a shadow property into an anonymous type or DTO
var postSummary = await context.Posts
    .Select(p => new {
        p.Title,
        LastUpdate = EF.Property<DateTime>(p, "LastUpdated")
    })
    .ToListAsync();
```

---

### Summary Checklist

| Task | Syntax |
| --- | --- |
| **Defining** | `modelBuilder.Entity<T>().Property<Type>("Name")` |
| **Updating** | `context.Entry(entity).Property("Name").CurrentValue = value` |
| **Querying** | `EF.Property<Type>(entity, "Name")` |
| **Metadata** | `entry.Metadata.FindProperty("Name").IsShadowProperty()` |

### Best Practices

- **Clarity:** Use them sparingly. Extensive use makes it difficult for other developers to understand the full database schema by looking at the POCO classes.
- **Infrastructure Only:** Reserve shadow properties for infrastructure concerns (auditing, soft deletes) rather than core business logic.
- **Global Filters:** Combine shadow properties like `IsDeleted` with **Global Query Filters** so that you don’t have to manually filter out “deleted” records in every query.