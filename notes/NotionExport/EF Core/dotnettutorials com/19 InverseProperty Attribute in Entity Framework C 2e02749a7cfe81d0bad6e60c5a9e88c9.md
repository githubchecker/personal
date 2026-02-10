# 19. InverseProperty Attribute in Entity Framework Core

# InverseProperty Attribute in Entity Framework Core

The `[InverseProperty]` attribute is used to explicitly define relationships when multiple navigation properties exist between the same two entities. It helps EF Core resolve ambiguities that the default conventions cannot handle.

### 1. The Relationship Ambiguity Problem

By default, EF Core can automatically pair navigation properties if there is only one relationship between two entities. However, if there are multiple relationships (e.g., a `Course` has both an `OnlineTeacher` and an `OfflineTeacher`), EF Core cannot determine which collection in the `Teacher` class corresponds to which reference in the `Course` class.

### Example Scenario:

- **Teacher**: Has `OnlineCourses` and `OfflineCourses`.
- **Course**: Has `OnlineTeacher` and `OfflineTeacher`.

Without explicit configuration, trying to add a migration for the above will result in an error: *“Unable to determine the relationship represented by navigation property…”*

---

### 2. Using [InverseProperty] on the Dependent Entity

You can resolve the ambiguity by decorating the reference navigation properties in the **Dependent Entity** (`Course`) with the name of the corresponding collection in the Principal Entity (`Teacher`).

```csharp
using System.ComponentModel.DataAnnotations.Schema;

public class Course {
    public int Id { get; set; }
    public string Name { get; set; }

    public int? OnlineTeacherId { get; set; }
    [InverseProperty("OnlineCourses")] // Pairs with OnlineCourses in Teacher
    public Teacher? OnlineTeacher { get; set; }

    public int? OfflineTeacherId { get; set; }
    [InverseProperty("OfflineCourses")] // Pairs with OfflineCourses in Teacher
    public Teacher? OfflineTeacher { get; set; }
}

public class Teacher {
    public int Id { get; set; }
    public string Name { get; set; }
    public ICollection<Course> OnlineCourses { get; set; }
    public ICollection<Course> OfflineCourses { get; set; }
}
```

---

### 3. Using [InverseProperty] on the Principal Entity

Alternatively, you can apply the attribute to the collection properties in the **Principal Entity** (`Teacher`), specifying the name of the reference property in the Dependent Entity.

```csharp
public class Teacher {
    public int Id { get; set; }
    public string Name { get; set; }

    [InverseProperty("OnlineTeacher")] // Pairs with OnlineTeacher in Course
    public ICollection<Course> OnlineCourses { get; set; }

    [InverseProperty("OfflineTeacher")] // Pairs with OfflineTeacher in Course
    public ICollection<Course> OfflineCourses { get; set; }
}

public class Course {
    public int Id { get; set; }
    public string Name { get; set; }
    public Teacher? OnlineTeacher { get; set; }
    public Teacher? OfflineTeacher { get; set; }
}
```

---

### 4. Key Behaviors

- **Placement**: You only need to apply the attribute to **one side** of the relationship (either Principal or Dependent).
- **Parameter**: The attribute takes a single `string` parameter which MUST match the exact name of the navigation property on the related entity.
- **Metadata**: This attribute only defines the *relationship*. To specify a custom column name for the foreign key, you should still use the `[ForeignKey]` attribute.

### 5. Summary: When to Use

| Scenario | Recommendation |
| --- | --- |
| **Single Relationship** | Use Conventions (No attribute needed). |
| **Multiple Relationships** | **Required**. Use `[InverseProperty]` to map specific paths (e.g., `CreatedBy` vs `ModifiedBy`). |
| **Self-Referencing** | Often required for parent-child relationships within the same table. |

### 6. Fluent API Alternative

```csharp
modelBuilder.Entity<Course>()
    .HasOne(c => c.OnlineTeacher)
    .WithMany(t => t.OnlineCourses)
    .HasForeignKey(c => c.OnlineTeacherId);

modelBuilder.Entity<Course>()
    .HasOne(c => c.OfflineTeacher)
    .WithMany(t => t.OfflineCourses)
    .HasForeignKey(c => c.OfflineTeacherId);
```