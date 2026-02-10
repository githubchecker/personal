# 15. Column Attribute in Entity Framework Core

# Column Attribute in Entity Framework Core

The `[Column]` attribute allows you to customize how individual properties map to database columns. It is part of the `System.ComponentModel.DataAnnotations.Schema` namespace and allows you to override default naming, data types, and column positioning.

### 1. Core Properties

- **`Name`**: Specifies a custom column name in the database.
- **`TypeName`**: Defines the specific database data type (e.g., `varchar(100)`, `decimal(10,4)`, `datetime2`).
- **`Order`**: Sets the zero-based position of the column.
    - **Note**: The `Order` property only affects the schema when the table is **first created**. It is ignored by EF Core Migrations when updating an existing table.

---

### 2. Comprehensive Example

The following example demonstrates how to use all three properties of the `[Column]` attribute in a single entity.

```csharp
using System.ComponentModel.DataAnnotations.Schema;

[Table("StudentInfo", Schema = "Admin")]
public class Student
{
    [Column("ID", Order = 0)]
    public int StudentId { get; set; }

    [Column("FirstName", Order = 1, TypeName = "nvarchar(100)")]
    public string? FirstName { get; set; }

    [Column("LName", Order = 2)] // Maps LastName property to LName column
    public string? LastName { get; set; }

    [Column("DOB", Order = 3, TypeName = "datetime2")]
    public DateTime DateOfBirth { get; set; }

    [Column("MobileNum", Order = 4)]
    public string? Mobile { get; set; }
}
```

### 3. Key Technical Behaviors

- **Precedence**: EF Core prioritizes the `Name` parameter in the `[Column]` attribute over the C# property name.
- **Type Precision**: Using `TypeName = "datetime2"` is a common performance optimization for SQL Server, as it provides higher precision and a larger date range than the standard `datetime`.
- **Order Limitations**: If you apply `Order` to an existing table and run a migration, you will see a warning. EF Core does not reorder columns in an existing SQL table because many database engines (like SQL Server) do not support this operation natively without rebuilding the table.

---

### 4. Summary: When to Use

| Feature | Use Case |
| --- | --- |
| **Custom Name** | When mapping to a legacy database or following strict naming conventions (e.g., `LName` instead of `LastName`). |
| **TypeName** | To specify precision for `decimal` or choosing between `nchar`/`nvarchar`/`varchar`. |
| **Order** | Primarily during greenfield development to ensure the Primary Key and important metadata appear at the start of the table. |

### 5. Fluent API Alternative

```csharp
modelBuilder.Entity<Student>()
    .Property(s => s.LastName)
    .HasColumnName("LName")
    .HasColumnType("nvarchar(100)")
    .HasColumnOrder(2);
```