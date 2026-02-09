# 5. CRUD Operations in Entity Framework Core

# CRUD Operations in EF Core

**CRUD** (Create, Read, Update, Delete) operations are the foundational tasks of any data-driven application. In Entity Framework Core, these operations are managed by the `DbContext`, which translates your C# object interactions into optimized SQL commands.

---

### Connected vs. Disconnected Scenarios

Understanding the state of your context is critical for CRUD:
* **Connected Scenario:** You use the **same instance** of the `DbContext` to retrieve, modify, and save an entity. The context automatically tracks the object’s changes.
* **Disconnected Scenario:** You retrieve an entity in one request, close the context, and try to save modifications in a **new context instance**. This is the standard behavior in Web APIs and requires manual re-attachment or state handling.

---

### 1. Create (Insert)

To insert data, instantiate your entity, add it to the `DbSet`, and call `SaveChanges()`.

```csharp
using var context = new ClinicContext();

var patient = new Patient { Name = "Alice Smith", Email = "alice@example.com" };

// Marks the entity state as 'Added'
context.Patients.Add(patient);

// Executes SQL: INSERT INTO Patients ...
await context.SaveChangesAsync();
```

---

### 2. Read (Select)

Reading data is performant and flexible using LINQ.

```csharp
// 1. Get all records
var allPatients = await context.Patients.ToListAsync();

// 2. Get a single record by ID (checks cache first)
var patient = await context.Patients.FindAsync(1);

// 3. Filter with conditions
var activePatients = await context.Patients
    .Where(p => p.IsActive)
    .OrderBy(p => p.Name)
    .ToListAsync();
```

---

### 3. Update

In a **connected** scenario, EF Core tracks modified properties automatically. It generates an optimized `UPDATE` statement that only updates the columns that actually changed.

```csharp
var patient = await context.Patients.FindAsync(1);

if (patient != null)
{
    patient.Email = "newemail@example.com";

    // SaveChanges detects the modification
    await context.SaveChangesAsync();
}
```

---

### 4. Delete

Deleting a record marks it as `Deleted` in the change tracker.

```csharp
var patient = await context.Patients.FindAsync(10);

if (patient != null)
{
    context.Patients.Remove(patient);
    await context.SaveChangesAsync();
}
```

---

### Optimized Bulk Operations (EF Core 7+)

For large datasets, loading every entity into memory just to modify it is slow. Modern EF Core supports high-performance, set-based operations.

| Task | Traditional Way | Modern High-Performance (EF 7+) |
| --- | --- | --- |
| **Mass Update** | Loop + `SaveChanges()` | `.ExecuteUpdate(s => ...)` |
| **Mass Delete** | Loop + `RemoveRange()` | `.ExecuteDelete()` |

**Example (Bulk Delete):**

```csharp
// Instantly deletes all inactive patients without fetching them first
await context.Patients
    .Where(p => !p.IsActive)
    .ExecuteDeleteAsync();
```

---

### Pro Tips for CRUD

- **AsNoTracking:** Use `.AsNoTracking()` for read-only queries. It disables the change tracker, making queries faster and reducing memory footprint.
- **Async Everything:** Always use the `Async` versions of methods (`SaveChangesAsync`, `ToListAsync`) in web applications to maintain scalability.
- **Transactional Integrity:** `SaveChanges()` automatically wraps multiple operations into a single transaction. If one fails, they all roll back.