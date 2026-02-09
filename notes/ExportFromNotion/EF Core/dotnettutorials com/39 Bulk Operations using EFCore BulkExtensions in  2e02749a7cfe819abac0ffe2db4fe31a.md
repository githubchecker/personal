# 39. Bulk Operations using EFCore.BulkExtensions in Entity Framework Core

# Bulk Operations with EFCore.BulkExtensions

`EFCore.BulkExtensions` is a high-performance, open-source library that extends EF Core with mass data operation capabilities. It is designed for scenarios where you need to process thousands of records efficiently, significantly outperforming standard change-tracked operations.

---

### Key Extension Methods

| Method | Description |
| --- | --- |
| **BulkInsert** | Inserts large datasets using the database’s native bulk-copy mechanism. |
| **BulkUpdate** | Updates many records by matching primary keys without loading them into memory. |
| **BulkDelete** | Deletes large sets of data based on a list of entities or keys. |
| **BulkInsertOrUpdate** | **Upsert**: Performs an update if the record exists (by PK) or an insert if it doesn’t. |
| **BulkRead** | Efficiently loads entities from the database based on a list of partial objects. |

---

### 1. Installation

Install the package via the .NET CLI:

```bash
dotnet add package EFCore.BulkExtensions
```

---

### 2. Bulk Insert

Standard `AddRange` creates multiple batched `INSERT` statements. `BulkInsert` uses `SqlBulkCopy` (for SQL Server), which is orders of magnitude faster for large datasets.

```csharp
var students = new List<Student> { /* 10,000+ items */ };

using var context = new MyDbContext();
// Directly streams data to the server
await context.BulkInsertAsync(students);
```

---

### 3. Bulk Update and Delete

These methods perform mass updates or deletes based on the Primary Keys of the entities provided in the list.

```csharp
// Updates matching rows in the DB based on StudentId
await context.BulkUpdateAsync(studentsToModify);

// Deletes matching rows in the DB based on StudentId
await context.BulkDeleteAsync(studentsToRemove);
```

---

### 4. Bulk Insert or Update (Upsert)

This method simplifies synchronization logic. It checks if the record exists in the database; if so, it updates it; otherwise, it inserts a new one.

```csharp
var mixedList = new List<Student>
{
    new Student { StudentId = 5, Name = "Existing Updated" },
    new Student { Name = "Brand New Record" }
};

await context.BulkInsertOrUpdateAsync(mixedList);
```

---

### 5. Advanced Configuration (`BulkConfig`)

You can tune the behavior of these operations using the `BulkConfig` object.

```csharp
var config = new BulkConfig
{
    BatchSize = 5000,
    PropertiesToExclude = new List<string> { nameof(Student.Branch) },
    EnableShadowProperties = true
};

await context.BulkInsertAsync(students, config);
```

---

### Comparison: EF Core Native vs. BulkExtensions

| Feature | EF Core `SaveChanges()` | EF Core `ExecuteUpdate` | `EFCore.BulkExtensions` |
| --- | --- | --- | --- |
| **Insert** | Scalable Batching | N/A | **Ultra-Fast Bulk Copy** |
| **Update** | Individual Row Tracking | **Set-Based** (Where Clause) | **List-Based** (Specific IDs) |
| **Upsert** | ❌ Manual Logic | ❌ Manual Logic | **✅ Native Support** |
| **Tracking** | Tracked | Not Tracked | Not Tracked |

---

### Best Practices

- **Performance Monitoring**: Use these methods when dealing with >1000 records. For small sets, the overhead of setting up a bulk operation might not be worth it.
- **Change Tracker**: These operations bypass the EF Core change tracker. If you need your local context to reflect the changes made on the server, you must reload the entities.
- **Index Impact**: Mass operations can cause index fragmentation. Consider rebuilding or reorganizing indexes after massive data imports.