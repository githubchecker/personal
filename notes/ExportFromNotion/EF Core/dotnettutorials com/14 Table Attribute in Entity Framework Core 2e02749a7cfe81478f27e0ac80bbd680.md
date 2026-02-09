# 14. Table Attribute in Entity Framework Core

# Table Attribute in Entity Framework Core

The `[Table]` attribute explicitly defines the database table name and schema for an entity class. It is part of the `System.ComponentModel.DataAnnotations.Schema` namespace and is used to override EF Core’s default mapping conventions.

### 1. Default Mapping Conventions

By default, EF Core determines the table name using the following precedence:
1. **`DbSet<T>` Property Name**: If you have `public DbSet<Student> StudentsInfo { get; set; }`, the table will be named `StudentsInfo`.
2. **Entity Class Name**: If no `DbSet` is explicitly defined, the table name matches the class name (e.g., `Student`).
3. **Schema**: Defaults to `dbo` for SQL Server.

---

### 2. Customizing Table and Schema

The `[Table]` attribute allows you to map an entity to a specific table name and a custom database schema.

### Single Table Name

```csharp
using System.ComponentModel.DataAnnotations.Schema;

[Table("StudentInfo")] // Maps to dbo.StudentInfo
public class Student
{
    public int StudentId { get; set; }
    public string? FirstName { get; set; }
}
```

### Table Name and Schema

```csharp
[Table("StudentInfo", Schema = "Admin")] // Maps to Admin.StudentInfo
public class Student
{
    public int StudentId { get; set; }
    public string? FirstName { get; set; }
}
```

---

### 3. Practical Scenarios

The `[Table]` attribute is essential in the following cases:
* **Existing Databases**: When you must map your entities to a pre-defined database schema that doesn’t follow EF Core naming conventions.
* **Database Organization**: When you need to group related tables into specific schemas (e.g., `Admin`, `Reporting`, `Sales`) for security or logical isolation.
* **Legacy Naming**: When your organization uses specific prefixes or naming patterns (e.g., `tbl_Students`) that you don’t want to use as class names in your C# code.

### 4. Comparison with Fluent API

While the `[Table]` attribute is convenient, the Fluent API offers identical functionality within the `OnModelCreating` method of your `DbContext`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Student>()
        .ToTable("StudentInfo", schema: "Admin");
}
```

> Note: Fluent API configurations take precedence over Data Annotations if both are used.
>