# 21. Required Attribute in Entity Framework Core

# Required Attribute in Entity Framework Core

The `[Required]` attribute in Entity Framework Core (EF Core) is used to specify that a property must contain data. When this attribute is applied to a property, EF Core maps it to a **NOT NULL** column in the database, ensuring that the database does not accept null values for that field.

This attribute is part of the `System.ComponentModel.DataAnnotations` namespace.

---

### Default EF Core Behavior (Nullability)

By default, EF Core determines the nullability of a column based on the C# type of the property:

- **Non-nullable types**: Types like `int`, `DateTime`, `bool`, and non-nullable reference types (if enabled) are mapped as `NOT NULL`.
- **Nullable types**: Types like `int?`, `DateTime?`, or nullable reference types (e.g., `string?`) are mapped as `NULL`.

```csharp
namespace EFCoreDemo.Entities
{
    public class Student
    {
        public int StudentId { get; set; }   // NOT NULL (non-nullable value type)
        public string? Name { get; set; }    // NULL (nullable reference type)
        public string? Address { get; set; }  // NULL
        public int RollNumber { get; set; }   // NOT NULL
    }
}
```

---

### Using the [Required] Attribute

To force a nullable property to be treated as `NOT NULL` in the database, apply the `[Required]` attribute.

```csharp
using System.ComponentModel.DataAnnotations;

namespace EFCoreDemo.Entities
{
    public class Student
    {
        public int StudentId { get; set; }

        [Required]
        public string? Name { get; set; } // Now mapped as NOT NULL

        public string? Address { get; set; } // Remains NULL
        public int RollNumber { get; set; }
    }
}
```

### Database Schema Effect

When you apply `[Required]`, the generated migration will include a NOT NULL constraint:

```sql
CREATE TABLE [Students] (
    [StudentId] int NOT NULL IDENTITY,
    [Name] nvarchar(max) NOT NULL, -- Created as NOT NULL
    [Address] nvarchar(max) NULL,
    [RollNumber] int NOT NULL,
    CONSTRAINT [PK_Students] PRIMARY KEY ([StudentId])
);
```

---

### Validation and Runtime Behavior

If you attempt to save an entity that violates the `[Required]` constraint, EF Core will throw a `DbUpdateException` because the database refuses to accept the `NULL` value.

```csharp
using var context = new EFCoreDbContext();
var student = new Student { Address = "123 Main St", RollNumber = 101 }; // Name is null

try
{
    context.Add(student);
    context.SaveChanges();
}
catch (DbUpdateException ex)
{
    Console.WriteLine("Error: The Name field is required.");
}
```

---

### Handling Empty Strings

The `[Required]` attribute includes an `AllowEmptyStrings` property. By default, it is set to `false`, but it is important to understand its limitations:

- **Database Level**: Setting `AllowEmptyStrings = false` does **not** affect the database schema. A `NOT NULL` column will still accept an empty string (`""`) because an empty string is not a null value.
- **Application Level**: This property is primarily used by validation frameworks (like ASP.NET Core MVC or Web API) to validate models during data entry.

To restrict empty strings at the database level, you would typically use Fluent API check constraints or custom validation logic before calling `SaveChanges`.

---

### Fluent API Alternative

Instead of using data annotations, you can configure a property as required using the Fluent API in the `OnModelCreating` method:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Student>()
        .Property(s => s.Name)
        .IsRequired();
}
```

The `IsRequired()` method achieves the same result as the `[Required]` attribute, making the column `NOT NULL` in the database.

---

### When to Use [Required]

1. **Data Integrity**: For essential fields like usernames, emails, or names that must always be present.
2. **Mandatory Relationships**: To ensure that a foreign key property in a dependent entity always points to a principal entity.
3. **Logical Constraints**: When business rules dictate that a piece of information is mandatory for the entity’s validity.