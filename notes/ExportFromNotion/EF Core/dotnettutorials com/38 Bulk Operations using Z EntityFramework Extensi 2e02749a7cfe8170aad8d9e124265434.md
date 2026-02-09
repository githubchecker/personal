# 38. Bulk Operations using Z.EntityFramework.Extensions.EFCore Extension

# Bulk Operations with Z.EntityFramework.Extensions

For scenarios requiring extreme performance or specialized operations like **Upserts**, the `Z.EntityFramework.Extensions.EFCore` library is an industry-standard choice. It enhances the `DbContext` with methods that bypass the standard EF Core change tracker for mass operations.

---

### Key Extension Methods

| Method | Description |
| --- | --- |
| **BulkInsert** | Inserts thousands of rows in seconds using internal `SqlBulkCopy`. |
| **BulkUpdate** | Updates multiple rows in a single database round-trip. |
| **BulkDelete** | Deletes matching records directly in the database. |
| **BulkMerge** | **Upsert**: Updates existing records and inserts new ones in one command. |
| **BulkSaveChanges** | An optimized replacement for `SaveChanges` that batches all pending changes. |

---

### 1. Installation

Install the package via the .NET CLI or NuGet Package Manager:

```bash
dotnet add package Z.EntityFramework.Extensions.EFCore
```

---

### 2. Bulk Insert

Perfect for initial data seeding, migrations, or large file imports. Unlike the native `AddRange`, this method does not load entities into the change tracker.

```csharp
var students = new List<Student> { /* Multiple thousands of items */ };

using var context = new MyDbContext();
// No need to call SaveChanges() after this
await context.BulkInsertAsync(students);
```

---

### 3. Bulk Merge (Upsert)

This is one of the library’s most powerful features. It automatically matches records based on their Primary Key (or a custom property) to determine whether to perform an `UPDATE` or an `INSERT`.

```csharp
var syncList = new List<Student>
{
    new Student { StudentId = 1, Name = "Existing Updated Name" }, // Will update ID 1
    new Student { Name = "Freshly Created Student" }               // Will insert
};

await context.BulkMergeAsync(syncList);
```

---

### 4. Bulk SaveChanges

Use this if you have a mix of inserts, updates, and deletes already tracked in your context. It provides a massive performance boost over the native `SaveChanges()` for large sets.

```csharp
// Perform various operations on the context
context.Students.Remove(oldStudent);
context.Students.Add(newStudent);
existingStudent.Name = "New Name";

// Batches all different operations into a single round-trip
await context.BulkSaveChangesAsync();
```

---

### Comparison: Native EF Core (7+) vs. Z.Extensions

| Scenario | Native EF Core | Z.Extensions |
| --- | --- | --- |
| **Large Inserts** | Good (Batching) | **Fastest** (Native Bulk Copy) |
| **Large Updates** | `ExecuteUpdate` (Set-based) | `BulkUpdate` (Set-based) |
| **Upsert** | ❌ Not supported | **✅ Supported** (`BulkMerge`) |
| **Flexibility** | Standard SQL | Advanced Tuning (Audit, Identity, etc.) |

---

### Best Practices & Licensing

- **Licensing**: This library is **commercial**. A trial or community license is required. For open-source projects, consider if EF Core 7’s `ExecuteUpdate/Delete` covers your needs first.
- **Transaction Safety**: All bulk methods are transactional. If one row fails (e.g., constraint violation), the entire batch usually rolls back.
- **Bypassing Logic**: Be aware that because these methods often bypass the Change Tracker, `DbContext` events (like `SavingChanges`) or logic inside `OnModelCreating` related to tracking might not be triggered.