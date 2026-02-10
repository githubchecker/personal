# 24. TimeStamp Attribute in Entity Framework Core

# TimeStamp Attribute in Entity Framework Core

The `[Timestamp]` attribute in Entity Framework Core (EF Core) is used to implement **Optimistic Concurrency**. it allows the application to detect if a record has been modified by another user since it was last fetched, preventing accidental data overwrites.

This attribute is part of the `System.ComponentModel.DataAnnotations` namespace.

---

### What is the [Timestamp] Attribute?

When you apply the `[Timestamp]` attribute to a `byte[]` property, EF Core configures it as a **Concurrency Token**.

- **Database Mapping**: In SQL Server, it maps to the `rowversion` data type.
- **Automatic Updates**: The database automatically generates a new, unique value for this column every time a row is inserted or updated.
- **Concurrency Check**: During `UPDATE` or `DELETE` operations, EF Core includes the `rowversion` in the `WHERE` clause. if the value in the database has changed, the operation affects zero rows, and EF Core throws a concurrency exception.

### Example Definition

```csharp
using System.ComponentModel.DataAnnotations;

public class Product
{
    public int ProductId { get; set; }
    public string Name { get; set; }
    public int StockQuantity { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; } // Managed by the database
}
```

---

### The Concurrency Problem (Without Timestamp)

Consider a scenario in a multi-user environment:
1. **User A** reads a product with `Stock = 10`.
2. **User B** reads the same product with `Stock = 10`.
3. **User A** updates stock to `7` and saves. (Database Stock is now 7).
4. **User B**, unaware of A’s change, updates stock to `3` (based on his initial read) and saves.
5. **Result**: Database stock becomes `3`. User A’s update is completely lost. This is called a “Last one wins” scenario.

---

### The Solution (With Timestamp)

With the `[Timestamp]` attribute, the workflow changes:
1. **User A** reads product (RowVersion: `0x001`).
2. **User B** reads same product (RowVersion: `0x001`).
3. **User A** saves. Database updates RowVersion to `0x002`. (Success).
4. **User B** tries to save. EF Core sends the following SQL:
`sql     UPDATE Products SET StockQuantity = 3      WHERE ProductId = 1 AND RowVersion = 0x001;`
5. **Conflict**: Since the database RowVersion is now `0x002`, the query fails to find the record. EF Core throws a `DbUpdateConcurrencyException`.

---

### Handling Concurrency Exceptions

In a real application, you should catch the `DbUpdateConcurrencyException` to manage the conflict, such as by reloading the latest data or notifying the user.

```csharp
try
{
    context.SaveChanges();
}
catch (DbUpdateConcurrencyException ex)
{
    // Handle the conflict
    foreach (var entry in ex.Entries)
    {
        var proposedValues = entry.CurrentValues;
        var databaseValues = entry.GetDatabaseValues();

        if (databaseValues == null)
        {
            // Record was deleted
            Console.WriteLine("The record was deleted by another user.");
        }
        else
        {
            // Update original values to match DB and decide how to proceed
            entry.OriginalValues.SetValues(databaseValues);
            Console.WriteLine("Record was modified by another user. Conflict detected.");
        }
    }
}
```

---

### Fluent API Alternative

You can achieve the same behavior using the Fluent API in the `OnModelCreating` method of your `DbContext`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Property(p => p.RowVersion)
        .IsRowVersion();
}
```

---

### Key Takeaways

| Feature | Requirement / Behavior |
| --- | --- |
| **Data Type** | Must be applied to a `byte[]` property. |
| **Limit** | Only one `[Timestamp]` property is allowed per entity. |
| **Database Generation** | Values are automatically managed by the database (read-only for the app). |
| **Concurrency Mode** | Implements Optimistic Concurrency. |
| **SQL Server Mapping** | Maps to `rowversion` (deprecated `timestamp` alias). |