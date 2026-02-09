# 17. ForeignKey Attribute in Entity Framework Core

# ForeignKey Attribute in Entity Framework Core

A Foreign Key (FK) establishes a relationship between two tables, ensuring referential integrity. In EF Core, relationships are defined using **Principal** and **Dependent** entities.

- **Principal Entity (Parent)**: Contains the Primary Key.
- **Dependent Entity (Child)**: Contains the Foreign Key referencing the Principal.

### 1. Default Naming Convention

By default, EF Core identifies a property as a Foreign Key if it follows the pattern `<NavigationPropertyName><PrincipalPrimaryKeyName>` or `<NavigationPropertyName>Id`.

```csharp
public class Department {
    public int Id { get; set; }
    public string Name { get; set; }
    public ICollection<Employee> Employees { get; set; }
}

public class Employee {
    public int Id { get; set; }
    public string Name { get; set; }

    // Relationship by Convention
    public int DepartmentId { get; set; }   // Foreign Key
    public Department Department { get; set; } // Navigation Property
}
```

---

### 2. Using the [ForeignKey] Attribute

The `[ForeignKey]` attribute from `System.ComponentModel.DataAnnotations.Schema` allows you to override conventions when your property names do not match the expected patterns.

You can apply the attribute in two ways:

### A. On the Scalar Property

Specify the name of the related **Navigation Property**.

```csharp
public class Employee {
    public int Id { get; set; }

    [ForeignKey("Department")] // Refers to the navigation property below
    public int DeptRefId { get; set; }

    public Department Department { get; set; }
}
```

### B. On the Navigation Property

Specify the name of the related **Scalar Foreign Key**.

```csharp
public class Employee {
    public int Id { get; set; }

    public int DeptRefId { get; set; }

    [ForeignKey("DeptRefId")] // Refers to the scalar property above
    public Department Department { get; set; }
}
```

---

### 3. Composite Foreign Keys

When the Principal entity has a composite primary key, the Dependent entity must have a composite foreign key. To map this via data annotations, apply the attribute to the **Navigation Property** and provide a comma-separated list of the scalar properties.

```csharp
// Principal Entity
[PrimaryKey(nameof(OrderId), nameof(StoreId))]
public class Order {
    public int OrderId { get; set; }
    public int StoreId { get; set; }
    public ICollection<OrderItem> Items { get; set; }
}

// Dependent Entity
public class OrderItem {
    public int Id { get; set; }

    public int OrderId { get; set; }
    public int StoreId { get; set; }

    [ForeignKey("OrderId, StoreId")] // Maps both properties as a composite FK
    public Order Order { get; set; }
}
```

---

### 4. Shadow Foreign Keys

If you define a navigation property but **omit** the scalar foreign key property in your C# class, EF Core will automatically create a “Shadow Property” in the database.

```csharp
public class Employee {
    public int Id { get; set; }
    public Department Department { get; set; } // EF Core creates 'DepartmentId' in DB
}
```

- **Accessing Shadow Keys**: Use `context.Entry(employee).Property("DepartmentId").CurrentValue`.

---

### 5. Summary: When to Use

| Scenario | Recommendation |
| --- | --- |
| **Standard Names** | Use Conventions (Cleanest code). |
| **Legacy DB / Custom Names** | Use `[ForeignKey]` on the scalar or navigation property. |
| **Composite Keys** | Use `[ForeignKey("Prop1, Prop2")]` on the navigation property. |
| **Multiple Relationships** | Use `[ForeignKey]` to disambiguate when two properties point to the same entity (e.g., `CreatedBy` and `ModifiedBy` both pointing to `User`). |