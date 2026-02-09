# 10. Lazy Loading in Entity Framework Core

# Lazy Loading in Entity Framework Core

Lazy Loading is a technique where related entities are only loaded from the database when they are accessed for the first time, rather than when the primary entity is initially retrieved.

### 1. Requirements for Lazy Loading

EF Core does not support lazy loading by default. To enable it, you must follow these three steps:

1. **Install the Proxy Package**: Add `Microsoft.EntityFrameworkCore.Proxies` to your project.
2. **Enable Proxies in DbContext**: Call `.UseLazyLoadingProxies()` in your `OnConfiguring` method.
3. **Use `virtual` Navigation Properties**: All navigation properties in your entity classes must be marked as `virtual`.

---

### 2. Implementation Example

### Enabling in DbContext

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options) {
    options.UseLazyLoadingProxies()
           .UseSqlServer("Server=... ;Database=StudentDB; ...");
}
```

### Entity Configuration

```csharp
public class Student {
    public int StudentId { get; set; }
    public string FirstName { get; set; }

    // Must be virtual for Lazy Loading
    public virtual Branch Branch { get; set; }
    public virtual Address Address { get; set; }
}
```

### Consumption (Triggers multiple queries)

```csharp
using var context = new EFCoreDbContext();

// Query 1: Fetches only Student data
var student = context.Students.FirstOrDefault(s => s.StudentId == 1);

// Query 2: Triggered by accessing the 'Branch' property
Console.WriteLine($"Branch: {student.Branch?.BranchName}");

// Query 3: Triggered by accessing the 'Address' property
Console.WriteLine($"City: {student.Address?.City}");
```

---

### 3. Internal Working: Proxy Objects

When `UseLazyLoadingProxies()` is enabled, EF Core generates **Dynamic Proxy Classes** at runtime that inherit from your entity classes. These proxies override the `virtual` navigation properties with logic similar to this:

```csharp
public class StudentProxy : Student {
    private Branch _branch;
    public override Branch Branch {
        get {
            if (_branch == null) {
                // Logic to query DB for Branch
                _branch = context.Branches.FirstOrDefault(b => b.BranchId == this.BranchId);
            }
            return _branch;
        }
        set => _branch = value;
    }
}
```

---

### 4. Managing Lazy Loading State

You can programmatically enable or disable lazy loading for specific operations using the `ChangeTracker`:

- **Disable Globally (DbContext Constructor)**:
`this.ChangeTracker.LazyLoadingEnabled = false;`
- **Toggle Mid-Execution**:
`csharp context.ChangeTracker.LazyLoadingEnabled = false; // Navigation property access will now return null if not already loaded var branch = student.Branch;`

---

### 5. Eager vs. Lazy Loading Comparison

| Feature | Eager Loading (`Include`) | Lazy Loading (Proxies + `virtual`) |
| --- | --- | --- |
| **SQL Join** | Uses `JOIN` in a single query | Issues separate `SELECT` queries as needed |
| **Round Trips** | One round trip | Multiple round trips (**N+1 Problem**) |
| **Over-fetching** | May load unneeded data | Only loads what is accessed |
| **Performance** | Better for batch processing | Better for specific user-triggered interactions |

### Best Practices

- **Avoid N+1**: Do not use lazy loading inside loops. Use Eager Loading if you need related data for a collection of entities.
- **Serialization**: Lazy loading proxies can cause issues with JSON serialization (infinite loops or circular references). Disable lazy loading or use DTOs for API responses.
- **Web Apps**: Lazy loading is generally discouraged in web applications because the `DbContext` is often disposed of before the view/template accesses the navigation properties.