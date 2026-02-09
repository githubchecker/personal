# 25. ConcurrencyCheck Attribute in Entity Framework Core

# ConcurrencyCheck Attribute in Entity Framework Core

The `[ConcurrencyCheck]` attribute in Entity Framework Core (EF Core) is used to implement **Optimistic Concurrency** on specific properties. Like the `[Timestamp]` attribute, it helps detect if a record has changed since it was last read, but it offers more flexibility by allowing concurrency checks on any data type.

This attribute is part of the `System.ComponentModel.DataAnnotations` namespace.

---

### What is the [ConcurrencyCheck] Attribute?

When you mark a property with `[ConcurrencyCheck]`, EF Core includes that property in the `WHERE` clause of `UPDATE` and `DELETE` commands.

Unlike `[Timestamp]`, which is limited to a single `byte[]` property per entity, `[ConcurrencyCheck]`:
* Can be applied to **multiple properties** in the same entity.
* Works with **any data type** (string, int, decimal, DateTime, etc.).
* Does not require a specific database column type like `rowversion`.

### Example Definition

```csharp
using System.ComponentModel.DataAnnotations;

public class Student
{
    public int StudentId { get; set; }

    [ConcurrencyCheck]
    public string Name { get; set; } // Monitored for concurrent changes

    [ConcurrencyCheck]
    public string Email { get; set; } // Monitored for concurrent changes

    public string Branch { get; set; } // No concurrency check for this field
}
```

---

### How it Works (SQL Behavior)

When you update an entity, EF Core includes the original values (the values as they were when you first fetched the entity) of the concurrency-checked properties in the `WHERE` clause:

```sql
UPDATE Students SET Name = @NewName, Branch = @NewBranch
WHERE StudentId = @Id
  AND Name = @OriginalName
  AND Email = @OriginalEmail;
```

If another user has changed the `Name` or `Email` in the database, the `WHERE` clause will fail to match any rows, and EF Core will throw a `DbUpdateConcurrencyException`.

---

### Fluent API Alternative

You can configure a property as a concurrency token using the Fluent API in the `OnModelCreating` method of your `DbContext`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Student>()
        .Property(s => s.Name)
        .IsConcurrencyToken();

    modelBuilder.Entity<Student>()
        .Property(s => s.Email)
        .IsConcurrencyToken();
}
```

---

### ConcurrencyCheck vs. Timestamp

| Feature | [ConcurrencyCheck] | [Timestamp] |
| --- | --- | --- |
| **Data Type** | Any (string, int, decimal, etc.) | `byte[]` only |
| **Multiplicity** | Can be applied to multiple properties. | Limited to one per entity. |
| **Database Mapping** | Uses existing data types. | Maps to `rowversion` in SQL Server. |
| **Manual vs Auto** | Compares the actual value of properties. | Compares an auto-incrementing version. |
| **Performance** | Slightly slower if many properties are used. | Highly efficient row-level check. |

### When to Use

- **Specific Fields**: Use `[ConcurrencyCheck]` if you only want to protect specific fields (e.g., a bank account `Balance`) while allowing other fields (e.g., `Address`) to be updated freely.
- **No RowVersion Column**: Use it if your database schema cannot be modified to add a new `rowversion` column.
- **Database Compatibility**: Ideal for databases that do not support automatic row versioning features.