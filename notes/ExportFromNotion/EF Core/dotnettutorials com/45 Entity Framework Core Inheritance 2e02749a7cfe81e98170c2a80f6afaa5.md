# 45. Entity Framework Core Inheritance

# Inheritance Mapping Strategies in EF Core

Inheritance is a core principle of Object-Oriented Programming (OOP) that allows you to share properties and behavior between classes. EF Core provides three distinct strategies to map these code hierarchies into a relational database.

---

### Summary of Strategies

| Strategy | Database Structure | Query Performance | Use Case |
| --- | --- | --- | --- |
| **TPH** (Hierarchy) | **Single table** + Discriminator | 🚀 **Fastest** (No joins) | Default; best for most apps. |
| **TPT** (Type) | **Table per class** + Joins | 🐌 **Slow** (Complex joins) | Highly normalized legacy DBs. |
| **TPC** (Concrete) | **Table per non-abstract class** | 🚀 **Fast** (No joins) | Independent tables per type. |

---

### 1. Table Per Hierarchy (TPH) - The Default

Under TPH, the entire hierarchy is mapped to a **single database table**. EF Core adds a **Discriminator** column to track which row belongs to which class.

- **Convention:** If you include a `DbSet` for the base type but none for derived types, EF Core uses TPH by default.
- **Configuration:** You can customize the discriminator name and values.

```csharp
modelBuilder.Entity<User>()
    .HasDiscriminator<string>("UserRole")
    .HasValue<Admin>("Administrator")
    .HasValue<Customer>("StandardUser");
```

---

### 2. Table Per Type (TPT)

Each class has its own dedicated table. The base table stores shared columns, while derived tables store specialized columns and a Foreign Key referencing the base.

- **Pros:** Enforce `NOT NULL` constraints on derived properties at the DB level.
- **Cons:** Any query for a derived type requires a `JOIN` with the base table.

```csharp
// To enable TPT, map each entity to its own table
modelBuilder.Entity<Car>().ToTable("Cars");
modelBuilder.Entity<Truck>().ToTable("Trucks");
```

---

### 3. Table Per Concrete Type (TPC)

Introduced in **EF Core 7.0**, TPC maps each non-abstract class to its own table. Each table contains **all** columns (both shared and specific). There is no table for the base class.

- **Pros:** Fast polymorphic queries without joins.
- **Cons:** Schema redundancy; Primary Keys must be unique across all tables in the hierarchy.

```csharp
modelBuilder.Entity<Vehicle>().UseTpcMappingStrategy();
```

---

### Performance & Design Considerations

1. **Discriminator Overhead:** In TPH, a single table can grow very wide with many nullable columns. This is usually okay for most modern databases like SQL Server or PostgreSQL.
2. **Polymorphic Queries:** If you often run `context.Base.ToList()`, TPH is fastest. TPT is significantly slower as the hierarchy grows deeper.
3. **Data Integrity:** TPT is the only strategy that allows mandatory (`NOT NULL`) columns for properties that only exist on derived types. In TPH, those columns *must* be nullable in the database.

### Decision Guide

- **Use TPH** for 90% of use cases. It provides the best performance and is easiest to manage.
- **Use TPC** when derived types are almost completely independent but share some common properties/logic.
- **Use TPT** only if required by a legacy DB schema or if you have strict normalization requirements.