# 29. One-to-Many Relationships in Entity Framework Core

# One-to-Many Relationships in Entity Framework Core

A **One-to-Many (1:N)** relationship occurs when one record in the principal table is associated with zero or more records in the dependent table. For example, one `Order` can have many `OrderItems`, but each `OrderItem` belongs to only one `Order`.

---

### Navigation Properties

In a 1:N relationship, the entities are characterized by their navigation properties:

- **Principal Entity (The “One”)**: Contains a **Collection Navigation Property** (e.g., `ICollection<OrderItem>`). It represents the owner side of the relationship.
- **Dependent Entity (The “Many”)**: Contains a **Reference Navigation Property** (e.g., `Order`) and a **Foreign Key** property. It represents the items that link back to the principal.

---

### 1. Configuration by Convention

EF Core automatically discovers 1:N relationships if you use common naming patterns for your properties.

```csharp
public class Order
{
    public int Id { get; set; }
    public DateTime OrderDate { get; set; }

    // Collection Navigation Property
    public ICollection<OrderItem> OrderItems { get; set; }
}

public class OrderItem
{
    public int Id { get; set; }
    public string ProductName { get; set; }

    // Foreign Key (Convention: <PrincipalClassName>Id)
    public int OrderId { get; set; }
    public Order Order { get; set; } // Reference Navigation Property
}
```

---

### 2. Configuration with Data Annotations

The `[ForeignKey]` attribute can be used to explicitly define which property holds the relationship link.

```csharp
public class OrderItem
{
    public int Id { get; set; }
    public string ProductName { get; set; }

    public int OrderId { get; set; }

    [ForeignKey("OrderId")]
    public Order Order { get; set; }
}
```

---

### 3. Configuration with Fluent API (Recommended)

The Fluent API is the most flexible approach, allowing you to chain configurations and specify advanced settings like delete behaviors.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>()
        .HasMany(o => o.OrderItems) // "One" has many
        .WithOne(oi => oi.Order)    // "Many" has one
        .HasForeignKey(oi => oi.OrderId) // Specify the FK
        .OnDelete(DeleteBehavior.Cascade); // Set delete behavior
}
```

---

### Delete Behaviors

The `OnDelete` method defines the “Cascading” action that occurs when a principal record is deleted.

| Behavior | Description |
| --- | --- |
| **Cascade** | Deleting the parent automatically deletes all associated children. (Default for required relationships). |
| **SetNull** | Deleting the parent sets the children’s foreign keys to `NULL`. (Requires a nullable FK). |
| **Restrict** | Prevents the parent from being deleted if child records exist. |
| **NoAction** | No action is taken at the DB level; attempts to delete the parent usually result in a database constraint error. |
| **ClientSetNull** | EF Core sets the FK to `NULL` in memory for tracked entities, but no cascading action is defined in the database. |

---

### When to Use One-to-Many Relationships

- **Hierarchical Data**: Categories and Products, Blogs and Posts, Departments and Employees.
- **Logical Ownership**: When items logically “belong” to a group (e.g., Line items on an Invoice).
- **Data Grouping**: When you need to aggregate data (e.g., calculating the total weight of items in a specific Shipment).