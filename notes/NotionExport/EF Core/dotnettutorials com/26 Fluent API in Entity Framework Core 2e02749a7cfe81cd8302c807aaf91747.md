# 26. Fluent API in Entity Framework Core

# Fluent API in Entity Framework Core

Fluent API in Entity Framework Core (EF Core) is a powerful way to configure entity classes and their relationships. It uses a **fluent interface** (method chaining) within the `DbContext` to define mappings, providing more flexibility and control than Data Annotation attributes.

---

### What is the Fluent API?

While Data Annotations use attributes directly on your entity classes, the Fluent API keeps your domain models clean by centralizing configurations in your `DbContext`.

**Key characteristics:**
* **Location**: Configured inside the `OnModelCreating` method of your `DbContext`.
* **Precedence**: Fluent API configurations always **override** Data Annotation attributes and default conventions.
* **Scope**: Supports advanced configurations that attributes cannot handle (e.g., Shadow Properties, many-to-many relationships, etc.).

---

### Basic Implementation

To use the Fluent API, you override the `OnModelCreating` method in your `DbContext` class and use the `ModelBuilder` object:

```csharp
using Microsoft.EntityFrameworkCore;

public class SchoolContext : DbContext
{
    public DbSet<Student> Students { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // 1. Entity level configuration
        modelBuilder.Entity<Student>()
            .ToTable("StudentInfo")
            .HasKey(s => s.StudentId);

        // 2. Property level configuration
        modelBuilder.Entity<Student>()
            .Property(s => s.Name)
            .IsRequired()
            .HasMaxLength(50);

        modelBuilder.Entity<Student>()
            .Property(s => s.Email)
            .HasColumnName("EmailAddress");
    }
}
```

---

### Why Use Fluent API?

1. **Separation of Concerns**: Keeps your entity classes “POCO” (Plain Old CLR Objects) without database-specific logic.
2. **Advanced Features**: Some mappings (like Composite Keys or complex relationships) can **only** be configured via Fluent API.
3. **Readability**: Multiple configurations for a single property can be chained together clearly.
4. **Centralization**: All database mapping logic is located in one place, making it easier to manage.

---

### Configuration Levels

Fluent API configurations are typically categorized into three levels:

### 1. Model Configuration (Global)

Applies settings across the entire model or sets defaults for all entities.
* *Examples*: `HasDefaultSchema()`, ignoring specific types globally.

### 2. Entity Configuration

Configures settings specific to a class/table.
* *Examples*: `ToTable()`, `HasKey()`, `HasIndex()`, `HasQueryFilter()`.

### 3. Property Configuration

Configures settings for individual properties (columns).
* *Examples*: `HasColumnName()`, `HasMaxLength()`, `IsRequired()`, `HasDefaultValue()`, `HasComputedColumnSql()`.

---

### Comparison: Data Annotations vs. Fluent API

| Feature | Data Annotations | Fluent API |
| --- | --- | --- |
| **Location** | Applied directly in Entity classes. | Centralized in `OnModelCreating`. |
| **Precedence** | Lower. | Higher (Overrides attributes). |
| **Model Purity** | Pollutes domain models with DB logic. | Keeps domain models clean. |
| **Capability** | Limited to basic mapping tasks. | Provides full control over all EF Core features. |
| **Availability** | Not all features have attributes. | Every feature is accessible. |