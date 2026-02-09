# 31. Self-Referential Relationship in Entity Framework Core

# Self-Referential Relationships in Entity Framework Core

A **Self-Referential Relationship** (also known as a **Recursive Relationship**) occurs when an entity has a navigation property pointing to another instance of its own type. This is primarily used to represent hierarchical data within a single table.

---

### Common Scenarios

- **Organizational Charts**: An `Employee` reports to a `Manager`, who is also an `Employee`.
- **Category Trees**: A `Category` belongs to a `ParentCategory`.
- **Reply Systems**: A `Comment` is a reply to a parent `Comment`.

---

### 1. Configuration by Convention

EF Core automatically discovers self-referencing relationships if you use standard naming patterns.

```csharp
public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; }

    // Foreign Key (Must be nullable for the hierarchy root)
    public int? ManagerId { get; set; }

    // Reference Navigation Property (The "One" side / Parent)
    public Employee Manager { get; set; }

    // Collection Navigation Property (The "Many" side / Children)
    public ICollection<Employee> Subordinates { get; set; }
}
```

---

### 2. Configuration with Data Annotations

Use `[ForeignKey]` and `[InverseProperty]` if property names do not follow conventions or if you want to be explicit.

```csharp
public class Category
{
    public int Id { get; set; }
    public string Name { get; set; }

    public int? ParentCategoryId { get; set; }

    [ForeignKey("ParentCategoryId")]
    public Category Parent { get; set; }

    [InverseProperty("Parent")]
    public ICollection<Category> Subcategories { get; set; }
}
```

---

### 3. Configuration with Fluent API (Recommended)

The Fluent API is useful for specifying delete behaviors and handling complex hierarchies.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Employee>()
        .HasOne(e => e.Manager)
        .WithMany(m => m.Subordinates)
        .HasForeignKey(e => e.ManagerId)
        .OnDelete(DeleteBehavior.Restrict); // Recommended to avoid cycle errors
}
```

---

### Key Technical Considerations

- **Nullability**: The Foreign Key (e.g., `ManagerId`) **must be nullable** (`int?`). If it were required, you could never insert the “Root” node (the top-level instance that has no parent).
- **Delete Behavior**: Circular or multiple cascade paths are often prohibited by relational databases. Using `DeleteBehavior.Restrict` or `NoAction` is usually required to prevent errors during table creation or record deletion.
- **Loading Hierarchies**: While `Include()` can load immediate children, deep hierarchies often require multiple `.ThenInclude()` calls or loading the entire hierarchy into memory to reconstruct the tree.

---

### When to Use

- When data is **inherently recursive** (items contain items of the same type).
- When you need an **arbitrarily deep hierarchy**.
- When properties and behaviors are identical between the parent and child (otherwise, consider Table-per-Hierarchy inheritance).