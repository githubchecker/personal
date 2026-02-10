# 12. Default Conventions in Entity Framework Core

# Default Conventions in Entity Framework Core

Entity Framework Core follows a “Convention over Configuration” approach. This means it uses predefined rules to determine how your C# classes map to a database schema, minimizing the need for explicit setup.

### 1. The Core Domain Model

Let’s look at a typical set of entities to understand how EF Core interprets them by default.

```csharp
public class Student {
    public int StudentId { get; set; }  // PK: Matches <EntityName>Id
    public string FirstName { get; set; }  // NVARCHAR(MAX), NOT NULL
    public string? LastName { get; set; }  // NVARCHAR(MAX), NULL
    public decimal GPA { get; set; }       // DECIMAL(18,2), Warning: Precision
    public Gender Gender { get; set; }     // Enum mapped to INT
    public virtual Address Address { get; set; } // One-to-One
    public virtual ICollection<Course> Courses { get; set; } // Many-to-Many
}

public class Teacher {
    public int Id { get; set; }            // PK: Matches "Id"
    public string FullName { get; set; }
    public decimal Salary { get; set; }
    public virtual ICollection<Course> Courses { get; set; } // One-to-Many
}

public class Course {
    public int CourseId { get; set; }
    public int TeacherId { get; set; }     // FK: Matches <PrincipalEntity>Id
    public virtual Teacher Teacher { get; set; }
    public virtual ICollection<Student> Students { get; set; }
}

public class Address {
    public int AddressId { get; set; }
    public int? StudentId { get; set; }    // Optional FK (Nullable)
    public virtual Student Student { get; set; }
}

public enum Gender { Male = 1, Female = 2 }
```

> Note on Decimal Precision: By default, decimal maps to DECIMAL(18,2). This allows only 2 digits after the decimal point. If you need more precision (e.g., for financial data), you must override this using Fluent API or Data Annotations.
> 

---

### 2. Schema and Table Conventions

- **Schema**: Defaults to the provider’s default (e.g., `dbo` for SQL Server).
- **Table Name**: Matches the `DbSet<T>` property name in your `DbContext`. If a `DbSet` is not defined but the entity is reachable via navigation, it defaults to the class name.
- **Column Order**: Columns follow the declaration order in the C# class, except the **Primary Key**, which is always placed first.

---

### 3. Key and Index Conventions

### Primary Keys

- Identified if a property is named `Id` or `<EntityName>Id`.
- Placed first in the table.
- Mapped as `IDENTITY` (auto-increment) for integer types.
- A **Clustered Index** is automatically created.

### Foreign Keys

- Identified by patterns like `<PrincipalEntityName>Id` (e.g., `TeacherId`).
- A **Non-Clustered Index** is automatically created for FK columns to optimize joins.
- **Unique Index**: Created for One-to-One relationships to ensure the dependent only links to one principal.

---

### 4. Data Type Mappings (SQL Server)

| C# Type | SQL Server Type | Nullability |
| --- | --- | --- |
| `int`, `long` | `INT`, `BIGINT` | NOT NULL |
| `int?`, `long?` | `INT`, `BIGINT` | NULL |
| `string` | `NVARCHAR(MAX)` | NULL |
| `decimal` | `DECIMAL(18,2)` | NOT NULL |
| `bool` | `BIT` | NOT NULL |
| `DateTime` | `DATETIME2` | NOT NULL |
| `byte[]` | `VARBINARY(MAX)` | NULL |
| `Enum` | `INT` | NOT NULL |

---

### 5. Relationship and Cascade Conventions

EF Core determines relationships based on the combination of navigation properties and FK properties:

- **One-to-Many**: One side has a collection (`ICollection<T>`), the other has a reference or nothing.
- **One-to-One**: Both sides have a reference property, and a unique FK exists on one side.
- **Many-to-Many**: Both sides have collection properties. EF Core 5.0+ automatically creates a junction table (e.g., `CourseStudent`).

### Cascade Delete Behavior

- **Required Relationship** (FK is NOT NULL): Defaults to `Cascade`. Deleting the principal deletes the dependents.
- **Optional Relationship** (FK is NULL): Defaults to `ClientSetNull` or `NoAction`. Deleting the principal sets the dependent’s FK to `NULL`.

| Relationship Side | Cascade Behavior |
| --- | --- |
| **Principal** | The “Parent” (e.g., `Teacher`) |
| **Dependent** | The “Child” holding the FK (e.g., `Course`) |