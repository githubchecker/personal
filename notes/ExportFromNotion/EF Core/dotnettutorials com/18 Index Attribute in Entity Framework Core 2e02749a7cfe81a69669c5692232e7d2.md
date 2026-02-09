# 18. Index Attribute in Entity Framework Core

# Index Attribute in Entity Framework Core

An index improves the speed of data retrieval by allowing the database to locate rows without scanning the entire table. EF Core creates some indexes by convention and allows others to be defined via attributes.

### 1. Default Indexes

By default, EF Core creates the following indexes during migrations:
* **Clustered Index**: Automatically created on the Primary Key column.
* **Non-Clustered Index**: Automatically created on Foreign Key columns to improve `JOIN` performance.

---

### 2. The [Index] Attribute

The `[Index]` attribute is part of the `Microsoft.EntityFrameworkCore` namespace and is applied at the **class level**.

### A. Basic Index and Custom Naming

By default, the index name is `IX_{TableName}_{PropertyName}`. You can override this using the `Name` property.

```csharp
using Microsoft.EntityFrameworkCore;

[Index(nameof(RegistrationNumber), Name = "Index_RegNum")]
public class Student {
    public int StudentId { get; set; }
    public int RegistrationNumber { get; set; }
}
```

### B. Unique Index

Enforce uniqueness on a non-primary key column.

```csharp
[Index(nameof(Email), IsUnique = true)]
public class User {
    public int Id { get; set; }
    public string Email { get; set; }
}
```

### C. Composite Index

A single index covering multiple columns.

```csharp
[Index(nameof(FirstName), nameof(LastName), Name = "IX_FullName")]
public class Author {
    public int Id { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
}
```

---

### 3. Index Sort Order

You can control the sort order (Ascending vs. Descending) for indexed columns.

- **Global Descending**: Apply descending order to all columns in the index.
- **Column-Specific**: Provide a `bool` array to the `IsDescending` property.

```csharp
// All columns descending
[Index(nameof(RegistrationNumber), nameof(RollNumber), AllDescending = true)]

// Specific columns (RegistrationNumber = Asc, RollNumber = Desc)
[Index(nameof(RegistrationNumber), nameof(RollNumber), IsDescending = new[] { false, true })]
public class Student {
    public int StudentId { get; set; }
    public int RegistrationNumber { get; set; }
    public int RollNumber { get; set; }
}
```

---

### 4. Multiple Indexes

You can apply multiple `[Index]` attributes to a single class.

```csharp
[Index(nameof(Email), IsUnique = true)]
[Index(nameof(LastName), nameof(FirstName))]
public class Employee {
    public int Id { get; set; }
    public string Email { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
}
```

---

### 5. Performance Considerations

| When to Index | When to Avoid |
| --- | --- |
| **WHERE Clauses**: Columns frequently used for filtering. | **Write-Heavy Tables**: Indexes slow down `INSERT`, `UPDATE`, and `DELETE`. |
| **JOIN Conditions**: Foreign keys and linking columns. | **Small Tables**: Full table scans are often faster for small datasets. |
| **ORDER BY**: Columns used for sorting results. | **Frequently Updated Columns**: Index maintenance adds overhead to every update. |
| **Uniqueness**: Enforcing unique logic (Email, Username). | **Low Cardinality**: Columns with very few distinct values (e.g., Boolean). |

---

### 6. Fluent API Alternative

```csharp
modelBuilder.Entity<Student>()
    .HasIndex(s => new { s.RegistrationNumber, s.RollNumber })
    .HasDatabaseName("IX_Reg_Roll")
    .IsUnique()
    .IsDescending(false, true);
```