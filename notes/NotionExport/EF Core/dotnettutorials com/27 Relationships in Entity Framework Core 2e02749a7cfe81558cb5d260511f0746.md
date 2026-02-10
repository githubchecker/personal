# 27. Relationships in Entity Framework Core

# Relationships Between Entities in Entity Framework Core

In Entity Framework Core (EF Core), relationships define how entities (classes) relate to one another, reflecting the structure of the underlying relational database.

---

### Key Terminology

When two entities are related, EF Core identifies them using the following terms:

- **Principal Entity**: The “parent” entity in the relationship. It contains the primary key that the other entity references.
- **Dependent Entity**: The “child” entity in the relationship. It contains the foreign key property.
- **Principal Key**: The property (usually the Primary Key) that uniquely identifies the principal entity.
- **Foreign Key (FK)**: The property in the dependent entity used to store the principal key’s value, establishing the link.
- **Navigation Property**: A property on an entity that allows you to access related entities or collections.

---

### Navigation Properties

Navigation properties are used to navigate between related data in your code.

1. **Reference Navigation Property**: Holds a reference to a single related entity. (Used in 1:1 and N:1 relationships).
    - *Example*: `public Blog Blog { get; set; }`
2. **Collection Navigation Property**: Holds a collection of related entities. (Used in 1:N and N:N relationships).
    - *Example*: `public ICollection<Post> Posts { get; set; }`

---

### Types of Relationships

### 1. One-to-One (1:1)

Each record in the principal table is linked to exactly one record in the dependent table.

```csharp
public class User
{
    public int UserId { get; set; }
    public UserProfile Profile { get; set; } // Reference Navigation
}

public class UserProfile
{
    public int UserProfileId { get; set; }
    public int UserId { get; set; } // Foreign Key
    public User User { get; set; } // Reference Navigation
}
```

### 2. One-to-Many (1:N)

A single record in the principal table can be related to multiple records in the dependent table.

```csharp
public class Blog
{
    public int BlogId { get; set; }
    public ICollection<Post> Posts { get; set; } // Collection Navigation
}

public class Post
{
    public int PostId { get; set; }
    public int BlogId { get; set; } // Foreign Key
    public Blog Blog { get; set; } // Reference Navigation
}
```

### 3. Many-to-Many (N:N)

Multiple records in the first table relate to multiple records in the second. Since EF Core 5.0, this can be implemented with collection navigations on both sides without an explicit join entity class.

```csharp
public class Student
{
    public int StudentId { get; set; }
    public ICollection<Course> Courses { get; set; } // Collection Navigation
}

public class Course
{
    public int CourseId { get; set; }
    public ICollection<Student> Students { get; set; } // Collection Navigation
}
```

### 4. Self-Referencing

An entity has a relationship with itself (e.g., an Employee who has a Manager, where the Manager is also an Employee).

```csharp
public class Employee
{
    public int EmployeeId { get; set; }
    public string Name { get; set; }
    public int? ManagerId { get; set; } // Self-referencing Foreign Key
    public Employee Manager { get; set; } // Principal
    public ICollection<Employee> Subordinates { get; set; } // Dependents
}
```

---

### Required vs. Optional Relationships

The nullability of the Foreign Key property determines if the relationship is required or optional:

- **Required Relationship**: The Foreign Key is **non-nullable** (e.g., `int BlogId`). The dependent entity cannot exist without a principal.
- **Optional Relationship**: The Foreign Key is **nullable** (e.g., `int? BlogId`). The dependent entity can exist without a reference to a principal.

---

### Mapping and Conventions

EF Core can often discover these relationships automatically by analyzing your navigation properties. When conventions are insufficient, you can use:
* **Data Annotations**: `[ForeignKey]`, `[InverseProperty]`.
* **Fluent API**: `.HasOne()`, `.HasMany()`, `.WithOne()`, `.WithMany()`.