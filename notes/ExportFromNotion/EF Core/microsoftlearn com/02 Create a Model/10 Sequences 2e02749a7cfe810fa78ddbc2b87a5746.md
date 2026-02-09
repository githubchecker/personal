# 10. Sequences

# Database Sequences

A **Sequence** generates unique, sequential numeric values in a relational database. Unlike `IDENTITY` columns, sequences are independent objects and can be shared across multiple tables.

## 1. Defining a Sequence

Use `HasSequence` to define a sequence in your model. You can specify the data type, start value, and increment.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.HasSequence<int>("OrderBatchNumbers", schema: "shared")
        .StartsAt(100)
        .IncrementsBy(10);
}

```

## 2. Using a Sequence for Properties

To use a sequence for a property, configure it to use a default value SQL expression. Note that the SQL syntax is provider-specific.

### SQL Server Example

```csharp
modelBuilder.Entity<Order>()
    .Property(o => o.OrderNumber)
    .HasDefaultValueSql("NEXT VALUE FOR shared.OrderBatchNumbers");

```

## 3. Key Characteristics

- **Independence:** Multiple tables can draw values from the same sequence.
- **Data Types:** Usually supported for `int`, `long`, `short`, and `byte`.
- **Hi-Lo Pattern:** EF Core can use sequences to implement the Hi-Lo value generation pattern, which improves performance by reducing database roundtrips.