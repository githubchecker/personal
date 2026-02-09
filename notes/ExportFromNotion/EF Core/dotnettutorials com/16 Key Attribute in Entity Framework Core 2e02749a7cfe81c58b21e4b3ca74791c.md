# 16. Key Attribute in Entity Framework Core

# Key Attribute in Entity Framework Core

A Primary Key uniquely identifies each record in a table, ensuring both **Uniqueness** and **Nullability** (NOT NULL) constraints. EF Core uses either conventions or explicit attributes to define these keys.

### 1. Default Naming Convention

By default, EF Core automatically identifies a property as a primary key if its name is:
* `Id`
* `<EntityName>Id` (e.g., `StudentId` for a `Student` entity)

```csharp
public class Student {
    public int StudentId { get; set; } // Automatically identified as PK
    public string? Name { get; set; }
}
```

---

### 2. The [Key] Attribute

If your primary key property does not follow the default naming convention, you must use the `[Key]` attribute from the `System.ComponentModel.DataAnnotations` namespace.

```csharp
using System.ComponentModel.DataAnnotations;

public class Student {
    [Key]
    public int RegistrationNumber { get; set; } // Explicitly marked as PK
    public string? Name { get; set; }
}
```

---

### 3. Composite Primary Keys

A composite key consists of multiple columns. **The `[Key]` attribute cannot be used for composite keys.** You have two options:

### A. [PrimaryKey] Attribute (EF Core 7.0+)

This attribute is applied at the **class level**.

```csharp
using Microsoft.EntityFrameworkCore;

[PrimaryKey(nameof(PassportNumber), nameof(CountryCode))]
public class Citizen {
    public string PassportNumber { get; set; }
    public string CountryCode { get; set; }
    public string FullName { get; set; }
}
```

### B. Fluent API (All EF Core versions)

This is defined in the `OnModelCreating` method of your `DbContext`.

```csharp
modelBuilder.Entity<Citizen>()
    .HasKey(c => new { c.PassportNumber, c.CountryCode });
```

---

### 4. Special Key Types

### GUID as Primary Key

GUIDs are useful for distributed systems where collision-free IDs must be generated without a central database round-trip.

```csharp
public class Student {
    [Key]
    public Guid StudentId { get; set; } // EF Core can auto-generate these
    public string? Name { get; set; }
}
```

### String as Primary Key

You can use strings as keys, but they will **not** be identity columns by default. You are responsible for ensuring their uniqueness and providing values.

```csharp
public class Course {
    [Key]
    public string CourseCode { get; set; } // e.g., "CS101"
    public string Title { get; set; }
}
```

---

### 5. Identity and Auto-Increment

- **Integer Keys**: By default, EF Core configures single-property integer keys (`int`, `long`, `short`) as `IDENTITY` (auto-increment) in SQL Server.
- **Composite Keys**: EF Core **disables** identity increments for composite keys by default.
- **Non-Integer Keys**: Strings and GUIDs are not identity columns, though EF Core can often generate GUID values on the client or server side.

### Summary Table

| Requirement | Approach |
| --- | --- |
| Single PK (Standard Name) | Convention (`Id` or `EntityId`) |
| Single PK (Custom Name) | `[Key]` Attribute |
| Composite PK | `[PrimaryKey]` (v7.0+) or Fluent API |
| Key-less Entity | `.HasNoKey()` in Fluent API |