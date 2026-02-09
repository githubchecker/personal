# 11. Explicit Loading in Entity Framework Core

# Explicit Loading in Entity Framework Core

Explicit Loading is a technique where related entities are manually loaded after the main entity has already been retrieved from the database. Unlike Lazy Loading, which happens automatically upon property access, Explicit Loading requires an intentional call to the `Load()` method.

### 1. Core Methods for Explicit Loading

EF Core provides specific methods to access and load related data:
* **`Entry()`**: Accesses the tracking information for a specific entity.
* **`Reference()`**: For loading a single related entity (e.g., `Student.Branch`).
* **`Collection()`**: For loading a collection of related entities (e.g., `Student.Courses`).
* **`Load()`**: Triggers the actual SQL query to fetch the data.

---

### 2. Comprehensive Example

The following example demonstrates how to explicitly load both a reference and a collection for a retrieved entity.

```csharp
using var context = new EFCoreDbContext();

// 1. Initial Load: Only fetches Student data
var student = context.Students.FirstOrDefault(s => s.StudentId == 1);

if (student != null)
{
    Console.WriteLine($"Student: {student.FirstName} {student.LastName}");

    // 2. Explicitly load a Reference (One-to-Many)
    context.Entry(student).Reference(s => s.Branch).Load();
    Console.WriteLine($"Branch: {student.Branch?.BranchLocation}");

    // 3. Explicitly load a Collection (Many-to-Many)
    context.Entry(student).Collection(s => s.Courses).Load();
    foreach (var course in student.Courses)
    {
        Console.WriteLine($"Enrolled Course: {course.Name}");
    }
}
```

---

### 3. Redundancy and the Change Tracker

When you call `.Load()`, EF Core first checks its internal **Change Tracker**:
* If the related entity is **already tracked** (loaded previously in the same context instance), EF Core skips the database query.
* If the entity is **not tracked**, EF Core issues a `SELECT` query.

This behavior protects against redundant database round trips if the same relationship is “loaded” multiple times in different parts of your logic.

---

### 4. Comparison of Loading Strategies

### Why use Explicit Loading?

- **Partial Data**: You only load related data for a specific branch of logic (e.g., only load Address if “Show Details” is clicked).
    
    
    | Strategy | When it Loads | SQL Execution | Best For |
    | --- | --- | --- | --- |
    | **Eager** | Immediately | One query with `JOIN`s | When data is always needed. |
    | **Lazy** | On property access | Multiple queries (Automatic) | Interactive UI or simple scripts. |
    | **Explicit** | When `.Load()` is called | Multiple queries (Manual) | When data is conditionally needed. |
- **Filtering**: You can apply filters directly to the related data before loading:
`csharp context.Entry(student) .Collection(s => s.Courses) .Query() // Access the underlying IQueryable .Where(c => c.IsActive) .Load();`
- **Performance Tuning**: It provides granular control over database traffic without the overhead of Proxies required by Lazy Loading.