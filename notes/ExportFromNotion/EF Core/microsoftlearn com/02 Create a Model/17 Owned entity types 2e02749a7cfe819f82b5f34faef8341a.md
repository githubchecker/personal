# 17. Owned entity types

# Owned Entity Types

**Owned Entity Types** (or "Owned Entities") are types that can only appear on navigation properties of other entity types. They represent a "part-of" relationship where the owned entity has no independent identity outside its owner (similar to Domain Driven Design's **Aggregates**).

## 1. Defining Owned Types

You can configure a type as owned using the `[Owned]` attribute or the Fluent API.

### Via Data Annotations

```csharp
[Owned]
public class Address
{
    public string Street { get; set; }
    public string City { get; set; }
}

public class Order
{
    public int Id { get; set; }
    public Address ShippingAddress { get; set; } // Owned
}

```

### Via Fluent API

```csharp
modelBuilder.Entity<Order>().OwnsOne(o => o.ShippingAddress);

```

## 2. Storage Mapping

### Table Splitting (Default)

By default, owned types are stored in the **same table** as the owner. EF Core renames the columns following the pattern `Navigation_Property`.

- Example: `ShippingAddress_Street`, `ShippingAddress_City`.

You can customize these names:

```csharp
modelBuilder.Entity<Order>().OwnsOne(o => o.ShippingAddress, sa =>
{
    sa.Property(p => p.Street).HasColumnName("ShipStreet");
});

```

### Separate Tables

Owned types can also be stored in a **separate table**. EF Core will automatically link them using a Foreign Key that also acts as the Primary Key.

```csharp
modelBuilder.Entity<Order>().OwnsOne(o => o.ShippingAddress, sa =>
{
    sa.ToTable("OrderAddresses");
});

```

## 3. Collections of Owned Types (`OwnsMany`)

To model a collection of owned entities, use `OwnsMany`. These are always stored in a separate table because multiple instances exist for a single owner.

```csharp
public class Distributor
{
    public int Id { get; set; }
    public ICollection<Address> ServiceLocations { get; set; }
}

modelBuilder.Entity<Distributor>().OwnsMany(d => d.ServiceLocations);

```

## 4. Nested Owned Types

Owned types can own other types, allowing for deep object graphs.

```csharp
modelBuilder.Entity<Order>().OwnsOne(o => o.Details, od =>
{
    od.OwnsOne(d => d.BillingAddress);
    od.OwnsOne(d => d.ShippingAddress);
});

```

## 5. Key Characteristics & Limitations

### Characteristics

- **Automatic Inclusion:** Owned types are always included in queries; you don't need `.Include()`.
- **Identity:** `OwnsOne` uses a shadow primary key that matches the owner's ID.

### Limitations

- **No** `DbSet<T>`**:** You cannot query owned types directly through a `DbSet`.
- **No Sharing:** An instance of an owned type cannot be shared between two owners.
- **No Inheritance:** Owned types do not support inheritance hierarchies.