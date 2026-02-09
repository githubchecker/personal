# 16. Advanced table mapping

# Advanced Table Mapping

EF Core provides powerful features for non-standard table mappings, allowing you to split entities across tables or consolidate multiple entities into a single table.

## 1. Table Splitting (Table Sharing)

Table Splitting allows multiple entity types to be mapped to a **single row** in a single table. This is useful for performance (lazy-loading large columns) or domain encapsulation.

### Requirements

- Entities must share the same **Primary Key** columns.
- One entity must have a relationship with the other.

### Example

```csharp
// Summary entity
public class Order {
    public int Id { get; set; }
    public DetailedOrder Details { get; set; }
}

// Detailed entity with large columns
public class DetailedOrder {
    public int Id { get; set; }
    public string LargeBlob { get; set; }
}

// Configuration
modelBuilder.Entity<Order>(ob => {
    ob.ToTable("Orders");
    ob.HasOne(o => o.Details).WithOne().HasForeignKey<DetailedOrder>(o => o.Id);
});

modelBuilder.Entity<DetailedOrder>().ToTable("Orders");

```

## 2. Entity Splitting

Entity Splitting allows a **single entity** type to be mapped to rows in **two or more tables**.

### Example: Splitting `Customer` into three tables

```csharp
modelBuilder.Entity<Customer>(entity => {
    entity.ToTable("Customers"); // Main table
    
    entity.SplitToTable("CustomerAddresses", table => {
        table.Property(c => c.Id).HasColumnName("CustomerId");
        table.Property(c => c.Address);
    });

    entity.SplitToTable("CustomerPhones", table => {
        table.Property(c => c.Id).HasColumnName("CustomerId");
        table.Property(c => c.PhoneNumber);
    });
});

```

*Note: Fragments are not optional; every row in the main table must have a corresponding row in the split tables.*

## 3. Table-Specific Facet Configuration (EF 7+)

When properties are mapped to multiple tables (e.g., in TPT or TPC inheritance), EF Core allows you to specify different column names for each table.

```csharp
modelBuilder.Entity<Animal>().UseTpcMappingStrategy();

modelBuilder.Entity<Cat>().ToTable("Cats", t => {
    t.Property(c => c.Id).HasColumnName("CatId");
    t.Property(c => c.Breed).HasColumnName("CatBreed");
});

modelBuilder.Entity<Dog>().ToTable("Dogs", t => {
    t.Property(d => d.Id).HasColumnName("DogId");
    t.Property(d => d.Breed).HasColumnName("DogBreed");
});

```

## 4. Summary

| Feature | Description | Use Case |
| --- | --- | --- |
| **Table Splitting** | Multiple entities -> One table | Encapsulation, Performance. |
| **Entity Splitting** | One entity -> Multiple tables | Normalizing an existing legacy schema. |
| **Facet Config** | Diff names for same prop in diff tables | TPT/TPC key naming conventions. |