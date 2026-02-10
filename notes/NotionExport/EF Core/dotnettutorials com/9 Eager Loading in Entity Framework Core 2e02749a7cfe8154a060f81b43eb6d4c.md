# 9. Eager Loading in Entity Framework Core

# Eager Loading in Entity Framework Core

Eager Loading allows related entities to be loaded along with the main entity in a single database query using SQL JOINs. This approach prevents the **N+1 Query Problem** and minimizes database round trips.

### 1. Mechanisms for Eager Loading

EF Core uses two primary methods to implement eager loading:
* **`Include()`**: Loads a direct related entity or collection (e.g., Student → Branch).
* **`ThenInclude()`**: Loads nested related entities (e.g., Student → Courses → Subjects).

---

### 2. Comprehensive Example

The following example demonstrates loading multiple levels of relationships (one-to-one, one-to-many, and many-to-many) in a single query.

```csharp
using var context = new EFCoreDbContext();

var student = context.Students
    .Where(s => s.StudentId == 1)
    .Include(s => s.Branch)               // One-to-Many relationship
    .Include(s => s.Address)              // One-to-One relationship
    .Include(s => s.Courses)              // Many-to-Many relationship
        .ThenInclude(c => c.Subjects)     // Nested Many-to-Many (Courses → Subjects)
    .FirstOrDefault();

if (student != null)
{
    Console.WriteLine($"Student: {student.FirstName} {student.LastName}");
    Console.WriteLine($"Branch: {student.Branch?.BranchLocation}");
    Console.WriteLine($"Address: {student.Address?.Street ?? "N/A"}");

    foreach (var course in student.Courses)
    {
        Console.WriteLine($"Course: {course.Name}");
        foreach (var sub in course.Subjects)
        {
            Console.WriteLine($"  - Subject: {sub.SubjectName}");
        }
    }
}
```

---

### 3. SQL Translation: INNER JOIN vs. LEFT JOIN

EF Core automatically determines the JOIN type based on the relationship’s nullability:

- **INNER JOIN**: Used when the relationship is **required** (non-nullable foreign key). For example, if `BranchId` in the Student entity is `int`, EF Core uses an `INNER JOIN` because every student must have a branch.
- **LEFT JOIN**: Used when the relationship is **optional** (nullable foreign key). For example, if `StudentId` in the Address entity is `int?`, EF Core uses a `LEFT JOIN` to ensure students without addresses are still included in the result.

---

### 4. Best Practices

- **Type Safety**: Always use Lambda expressions (e.g., `.Include(s => s.Address)`) instead of string-based includes to benefit from compile-time checking and IntelliSense.
- **Performance**: While Eager Loading reduces the number of queries, including too many levels or large collections can lead to “Cartesian Product” issues, where the result set grows exponentially. Use with caution for very deep graphs.
- **Filtering**: You can filter the included collections (EF Core 5.0+):
`csharp .Include(s => s.Courses.Where(c => c.IsActive))`

### When to Use Eager Loading

1. **Immediate Need**: When you know you will access the related data immediately after the main query.
2. **Flat Data**: When dealing with relatively flat models to avoid complex joins.
3. **Avoid N+1**: To prevent the performance degradation caused by fetching child records in a loop (Lazy Loading).