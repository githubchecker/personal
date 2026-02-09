# 20. NotMapped Attribute in Entity Framework Core

# NotMapped Attribute in Entity Framework Core

The `[NotMapped]` attribute in Entity Framework Core (EF Core) is used to specify that an entity class or a property should be excluded from database mapping. When applied, EF Core ignores these elements during schema generation and CRUD operations (Insert, Update, Delete, and Query).

This attribute is part of the `System.ComponentModel.DataAnnotations.Schema` namespace.

---

### [NotMapped] on Properties

By default, EF Core maps every public property with a getter and a setter to a column in the database. Use the `[NotMapped]` attribute to exclude properties that are only needed for internal logic, UI display, or temporary data storage.

### Example: Calculated Properties

In many cases, properties like `FullName` or `Age` can be derived from other fields like `FirstName`, `LastName`, or `DateOfBirth`. Storing these in the database is redundant and can lead to data inconsistency.

```csharp
using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace EFCoreDemo.Entities
{
    public class Employee
    {
        public int EmployeeId { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public DateTime DateOfBirth { get; set; }
        public DateTime DateOfJoining { get; set; }

        // Calculated property: Not mapped to database
        [NotMapped]
        public string FullName => $"{FirstName} {LastName}";

        // Calculated property: Not mapped to database
        [NotMapped]
        public int Age
        {
            get
            {
                var today = DateTime.Today;
                var age = today.Year - DateOfBirth.Year;
                if (DateOfBirth.Date > today.AddYears(-age)) age--;
                return age;
            }
        }

        // Logic-only property: Not mapped to database
        [NotMapped]
        public bool IsVeteranEmployee => (DateTime.Today.Year - DateOfJoining.Year) >= 10;
    }
}
```

### Why use [NotMapped] on Properties?

- **Up-to-Date Values**: Calculating values like `Age` on the fly ensures they are always accurate without needing periodic database updates.
- **Avoid Redundant Data**: Prevents storing information that can be easily recreated from existing columns, saving storage space.
- **UI/Application State**: Useful for properties that track temporary states (e.g., `IsSelected`, `ValidationErrorMessage`) which have no meaning in a database.

**Note**: EF Core automatically ignores properties that do not have both a `get` and `set` accessor. For example, `public string FullName => $"{FirstName} {LastName}";` (an expression-bodied member) is ignored by default. However, explicitly adding `[NotMapped]` is recommended for clarity.

---

### [NotMapped] on Classes

The `[NotMapped]` attribute can also be applied to an entire class. This tells EF Core to never create a database table for this class, even if it is referenced as a navigation property in other entities or included as a `DbSet` in your `DbContext`.

### Example: Reporting and DTOs

Imagine a scenario where you want to generate a summary report. You can create a class to hold the report data without creating a corresponding table in the database.

```csharp
using System.ComponentModel.DataAnnotations.Schema;

namespace EFCoreDemo.Entities
{
    [NotMapped]
    public class DepartmentExpenseReport
    {
        public string DepartmentName { get; set; }
        public decimal TotalExpenses { get; set; }
        public int NumberOfTransactions { get; set; }
    }
}
```

### Why use [NotMapped] on Classes?

- **Data Transfer Objects (DTOs)**: When using classes purely for grouping results from complex LINQ queries or raw SQL.
- **Helper Classes**: For classes that encapsulate business logic or data transformations but don’t represent a persistent entity.
- **Domain Models vs. Persistence Models**: To prevent domain-specific logic classes from accidentally leaking into the database schema.

---

### Fluent API Alternative

If you prefer to keep your entity classes clean of data annotations, you can use the Fluent API in the `OnModelCreating` method of your `DbContext`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    // Exclude a property from mapping
    modelBuilder.Entity<Employee>().Ignore(e => e.FullName);
    modelBuilder.Entity<Employee>().Ignore(e => e.Age);

    // Exclude an entire class from mapping
    modelBuilder.Ignore<DepartmentExpenseReport>();
}
```

---

### Summary of Benefits

1. **Data Integrity**: Prevents “stale” data by ensuring calculated values are derived from the source of truth at runtime.
2. **Schema Simplicity**: Keeps the database schema focused on persistence, avoiding “pollution” from UI-specific or logic-specific fields.
3. **Flexibility**: Allows models to be rich with business logic (methods and properties) while maintaining a clean mapping to the persistence layer.
4. **Performance**: Reduces the size of database rows and the overhead of transferring unnecessary data during queries.