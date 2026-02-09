# 33. Entity Configurations using Entity Framework Core Fluent API

# Entity Configurations in EF Core (Fluent API)

While **Global Configurations** apply rules to the entire model, **Entity Configurations** allow you to define settings specific to individual entity types (classes). This is the primary way to map your C# classes to specific database tables and constraints.

---

### 1. Table and Schema Mapping

By default, EF Core maps an entity to a table with the same name as the class or the `DbSet`. Use `ToTable` to override this name or specify a database schema.

```csharp
modelBuilder.Entity<Customer>()
    .ToTable("Customers", schema: "Sales");
```

---

### 2. Primary Keys

EF Core identifies primary keys by convention (properties named `Id` or `CustomerId`). Use `HasKey` for custom names or composite keys.

### Single Primary Key

```csharp
modelBuilder.Entity<Customer>()
    .HasKey(c => c.EmailIdentifier);
```

### Composite Primary Key

```csharp
modelBuilder.Entity<OrderItem>()
    .HasKey(oi => new { oi.OrderId, oi.ProductId });
```

---

### 3. Indexes

Indexes improve search performance. You can configure them as unique, composite, or filtered.

```csharp
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.Email)
    .IsUnique();

// Composite Index with Include Columns (Covering Index)
modelBuilder.Entity<Order>()
    .HasIndex(o => new { o.OrderDate, o.Status })
    .IncludeProperties(o => o.TotalAmount);

// Filtered Index
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.SubscriptionId)
    .HasFilter("[IsActive] = 1");
```

---

### 4. Alternate Keys (Unique Constraints)

An alternate key enforces a unique constraint on properties other than the primary key. Unlike simple unique indexes, alternate keys can be used as the target of a foreign key relationship.

```csharp
modelBuilder.Entity<Employee>()
    .HasAlternateKey(e => e.PassportNumber)
    .HasName("AK_Employee_Passport");
```

---

### 5. Ignoring Entities

Use `Ignore` to prevent a class from being mapped to a database table, even if it is referenced in your code.

```csharp
modelBuilder.Ignore<PriceCalculator>();
```

---

### 6. Owned Entities (Value Objects)

Owned entities are types that do not have their own identity and exist only as part of a parent entity. Their properties are mapped to columns in the parent’s table by default.

```csharp
public class User
{
    public int Id { get; set; }
    public Address HomeAddress { get; set; } // Owned Type
}

// Configuration
modelBuilder.Entity<User>()
    .OwnsOne(u => u.HomeAddress);
```

---

### 7. Cascade Delete Behavior

Define how related records should be handled when a principal record is deleted.

```csharp
modelBuilder.Entity<Order>()
    .HasMany(o => o.Items)
    .WithOne(i => i.Order)
    .OnDelete(DeleteBehavior.Cascade);
```

| Behavior | Description |
| --- | --- |
| **Cascade** | Deleting the parent deletes all children automatically. |
| **Restrict** | Deletion of the parent is prohibited if children exist. |
| **SetNull** | Deleting the parent sets the child’s foreign key to NULL. |
| **NoAction** | The database does nothing; referential integrity is checked by the DB. |

---

### Organizing Configurations

For large projects, it is recommended to keep `OnModelCreating` clean by moving configurations into separate classes.

```csharp
public class CustomerConfiguration : IEntityTypeConfiguration<Customer>
{
    public void Configure(EntityTypeBuilder<Customer> builder)
    {
        builder.ToTable("Customers", "Sales");
        builder.HasKey(c => c.CustomerId);
        builder.HasIndex(c => c.Email).IsUnique();
    }
}

// In DbContext
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfiguration(new CustomerConfiguration());
    // OR apply all configurations in an assembly:
    // modelBuilder.ApplyConfigurationsFromAssembly(typeof(MyContext).Assembly);
}
```