# 8. How to Design Database using EF Core Code First Approach

# Database Design with EF Core Code-First

**Code-First** is the most popular development workflow in Entity Framework Core. It allows developers to focus on the domain logic and C# entity classes, while EF Core automatically handles the generation and synchronization of the database schema.

---

### Phase 1: Designing the Domain Entities

In a Code-First approach, your database design starts with C# classes. Below is a sample design for a **University Management System** involving Professors, Students, and Courses.

### The Entity Models

```csharp
public class Professor
{
    public int Id { get; set; } // Automatically becomes PK (Identity)
    public string Name { get; set; }
    public string Department { get; set; }

    // One Professor can teach many Courses
    public ICollection<Course> Courses { get; set; }
}

public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; }
    public DateTime EnrollmentDate { get; set; }

    // Many Students can enroll in many Courses
    public ICollection<Course> EnrolledCourses { get; set; }
}

public class Course
{
    public int Id { get; set; }
    public string Title { get; set; }

    // Foreign Key and Navigation Property for Professor
    public int ProfessorId { get; set; }
    public Professor Professor { get; set; }

    // Many Courses can have many Students
    public ICollection<Student> Students { get; set; }
}
```

---

### Phase 2: Understanding Default Conventions

EF Core follows “Convention over Configuration” to determine how the database should look:

- **Primary Keys:** Properties named `Id` or `[ClassName]Id` are automatically recognized as Primary Keys.
- **Identity Columns:** Integer primary keys are automatically set to `IDENTITY(1,1)` (auto-incrementing) in SQL Server.
- **Foreign Keys:** Properties like `ProfessorId` are automatically linked to the `Professor` table as Foreign Keys.
- **Nullability:**
    - **Nullable:** Types like `string`, `int?`, and `DateTime?` are created as `NULL` columns.
    - **Required:** Value types like `int`, `double`, and `bool` are created as `NOT NULL` columns.

---

### Phase 3: The DbContext (The Bridge)

The `DbContext` is the central piece where these entities are registered to be mapped to database tables.

```csharp
public class UniversityContext : DbContext
{
    public DbSet<Professor> Professors { get; set; }
    public DbSet<Student> Students { get; set; }
    public DbSet<Course> Courses { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder options)
    {
        options.UseSqlServer("Server=.;Database=UniversityDB;Trusted_Connection=True;TrustServerCertificate=True;");
    }
}
```

---

### Phase 4: Synchronizing via Migrations

Once your code is defined, use EF Core Migrations to build the physical database.

1. **Create Migration:** Analyzes your C# code and generates a “blueprint” for the schema.
`bash dotnet ef migrations add InitialUniversityDesign`
2. **Update Database:** Executes the generated SQL against your server.
`bash dotnet ef database update`

---

### Advantages of the Code-First Design

- **Version Control:** Your database schema is stored in source control (Git) alongside your code.
- **Productivity:** You can refactor C# properties, and EF Core handles the complex SQL `ALTER TABLE` or `RENAME COLUMN` commands.
- **Clean Domain:** You don’t need to switch between SQL Server Management Studio and Visual Studio; you define everything in C#.

### Summary of Relationship Mapping

| Relationship | Implementation | Result in DB |
| --- | --- | --- |
| **One-to-Many** | `ICollection` on one side, `Ref` on the other. | Foreign Key in the ‘Many’ table. |
| **Many-to-Many** | `ICollection` on both sides. | Automatic Junction Table (e.g., `CourseStudent`). |
| **One-to-One** | `Ref` properties on both sides. | Foreign Key with Unique Index in the dependent table. |