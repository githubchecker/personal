# 35. Non-Primary Key Table in EF Core using Fluent API

# Keyless Entity Types (Tables without Primary Keys)

In standard relational design, every table should have a primary key. However, Entity Framework Core allows you to map classes to database objects that do not have a primary key, such as **database views** or **logging tables**. These are known as **Keyless Entity Types**.

---

### Common Use Cases

- **Database Views**: Mapping to a view that doesn’t have a unique identifier.
- **Log/Audit Tables**: High-volume, append-only tables where uniqueness isn’t enforced for performance reasons.
- **Raw SQL Queries**: Returning custom data shapes from a stored procedure or complex SQL query that don’t match an existing entity.

---

### Configuration with Fluent API

To define an entity as keyless, use the `HasNoKey()` method in `OnModelCreating`.

```csharp
public class CategorySummary
{
    public string CategoryName { get; set; }
    public int ProductCount { get; set; }
}

// In DbContext
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<CategorySummary>()
        .HasNoKey()
        .ToView("View_CategorySummary"); // Often mapped to a view
}
```

---

### Key Characteristics and Limitations

| Feature | Keyed Entities | Keyless Entities |
| --- | --- | --- |
| **Change Tracking** | Supported by `DbContext` | **Never tracked** |
| **CRUD Operations** | Supported (`Add`, `Remove`) | **Read-only** via `DbSet` |
| **Identity** | Required (PK) | None |
| **Navigation Props** | Full Support | Restricted (Can’t be the dependent end) |

---

### Data Operations

### 1. Querying

You can query keyless entities just like any other `DbSet`. They are always returned as “No-Tracking” queries.

```csharp
var results = await context.CategorySummaries.ToListAsync();
```

### 2. Modifications

Since EF Core does not track keyless entities, standard methods like `Add()` or `Update()` will not work. You must use **Raw SQL** or Stored Procedures for modifications:

```csharp
await context.Database.ExecuteSqlRawAsync(
    "INSERT INTO Logs (Message, CreatedAt) VALUES ({0}, {1})",
    "Initial Startup", DateTime.UtcNow);
```

---

### Comparison with Keyed Entities

Keyed entities are for data that has a clear identity and lifecycle (Create, Read, Update, Delete). Keyless entities are for **data shapes** or **read-only snapshots** where identity is not required or available.

### Best Practices

- **Use for Views**: Keyless entities are the primary way to map to non-updatable database views.
- **Prefer Keys for Tables**: Even for logs, adding a simple `int` or `Guid` primary key is usually better than using a keyless entity, as it allows for standard EF Core features like batching and testing.
- **Read-Only**: Treat keyless entities as read-only models in your application logic.