# 9. Inheritance

# Inheritance Mapping Strategy

EF Core provides three primary strategies for mapping .NET inheritance hierarchies to a relational database.

## 1. Table-Per-Hierarchy (TPH) - Default

All classes in the hierarchy are mapped to a **single table**. A **Discriminator** column identifies the type of each row.

- **Pros:** Excellent performance, simple schema.
- **Cons:** Columns for derived properties must be nullable.

### Configuration

```csharp
modelBuilder.Entity<Blog>()
    .HasDiscriminator<string>("blog_type")
    .HasValue<Blog>("base")
    .HasValue<RssBlog>("rss");

```

## 2. Table-Per-Type (TPT)

Each type in the hierarchy is mapped to its **own table**. The base table contains common properties, and derived tables contain specific properties linked via Foreign Keys.

- **Pros:** Normalized database schema.
- **Cons:** Significantly slower due to complex joins; indexes cannot span inherited/declared properties.

### Configuration

```csharp
modelBuilder.Entity<Blog>().UseTptMappingStrategy();

```

## 3. Table-Per-Concrete-Type (TPC) - EF Core 7+

Only concrete types (not abstract ones) get their own tables. Each table contains **all** properties (inherited + declared).

- **Pros:** Fast for leaf-type queries; no joins; no nullable columns required for derived types.
- **Cons:** Denormalized; Primary Key generation requires sequences to avoid conflicts across tables.

### Configuration

```csharp
modelBuilder.Entity<Blog>().UseTpcMappingStrategy();

```

### Key Generation in TPC

Because IDs must be unique across all tables in the hierarchy, TPC usually requires a **Database Sequence**:

```sql
[Id] int DEFAULT (NEXT VALUE FOR [BlogSequence])

```

## 4. Summary Comparison

| Strategy | Tables | Performance | Best For... |
| --- | --- | --- | --- |
| **TPH** | One | **Fastest** | Most common scenarios; polymorphic queries. |
| **TPC** | Many (Concrete) | Fast | Domain-driven designs; when derived types have many unique fields. |
| **TPT** | Many (All) | Slow | Legacy databases; strict normalization requirements. |

## 5. Advanced Configuration

### Shared Columns (TPH Only)

Map properties with different names in code to the same column in the database:

```csharp
modelBuilder.Entity<Blog>().Property(b => b.Url).HasColumnName("Url");
modelBuilder.Entity<RssBlog>().Property(b => b.Url).HasColumnName("Url");

```

### Discriminator Mapping

You can map the discriminator to a regular property if you need to access it in your code:

```csharp
modelBuilder.Entity<Blog>()
    .HasDiscriminator(b => b.BlogType);

```