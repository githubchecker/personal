# 32. Global Configurations in Entity Framework Core using Fluent API

# Global Configurations in Entity Framework Core

**Global Configurations** (or Model-Wide Configurations) allow you to define rules that apply across the entire data model instead of configuring individual entities or properties. This ensures consistency, reduces boilerplate, and adheres to the DRY (Don’t Repeat Yourself) principle.

---

### Implementation with Fluent API

Global configurations are typically implemented by iterating through the model metadata within the `OnModelCreating` method of your `DbContext`.

---

### 1. Setting the Default Schema

By default, SQL Server uses the `dbo` schema. You can change this for all tables in your context:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.HasDefaultSchema("Admin");
}
```

---

### 2. Default Decimal Precision

To ensure all decimal columns in the database have a consistent precision and scale (e.g., 18, 2):

```csharp
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    var properties = entityType.GetProperties()
        .Where(p => p.ClrType == typeof(decimal) || p.ClrType == typeof(decimal?));

    foreach (var property in properties)
    {
        property.SetPrecision(18);
        property.SetScale(2);
    }
}
```

---

### 3. Default Max Length for Strings

By default, EF Core maps string properties to `nvarchar(max)`. You can set a baseline limit for all string properties:

```csharp
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    var stringProperties = entityType.GetProperties()
        .Where(p => p.ClrType == typeof(string));

    foreach (var property in stringProperties)
    {
        if (property.GetMaxLength() == null)
        {
            property.SetMaxLength(255);
        }
    }
}
```

---

### 4. Mapping Enums as Strings

Storing enum names as strings in the database improves readability compared to the default integer mapping.

```csharp
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    var enumProperties = entityType.GetProperties().Where(p => p.ClrType.IsEnum);

    foreach (var property in enumProperties)
    {
        var converterType = typeof(EnumToStringConverter<>).MakeGenericType(property.ClrType);
        var converter = Activator.CreateInstance(converterType) as ValueConverter;
        property.SetValueConverter(converter);
    }
}
```

---

### 5. Global Delete Behavior

To avoid accidental data loss, you can change the default delete behavior for all relationships to `Restrict`.

```csharp
foreach (var foreignKey in modelBuilder.Model.GetEntityTypes().SelectMany(e => e.GetForeignKeys()))
{
    foreignKey.DeleteBehavior = DeleteBehavior.Restrict;
}
```

---

### 6. Automated Audit Timestamps

If your entities implement an interface like `IAudit`, you can automate the generation of timestamps.

```csharp
public interface IAudit
{
    DateTime CreatedAt { get; set; }
}

// In OnModelCreating
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    if (typeof(IAudit).IsAssignableFrom(entityType.ClrType))
    {
        modelBuilder.Entity(entityType.ClrType)
            .Property("CreatedAt")
            .HasDefaultValueSql("GETUTCDATE()")
            .ValueGeneratedOnAdd();
    }
}
```

---

### Summary: Individual vs. Global Configuration

| Feature | Individual (Fluent API) | Global (Model-Wide) |
| --- | --- | --- |
| **Effort** | High (per property) | Low (Configured once) |
| **Consistency** | Prone to error/omission | Guaranteed model-wide |
| **Maintenance** | Hard to update across apps | Single point of change |
| **Use Case** | Specialized business rules | Infrastructure/standard rules |

---

### Best Practices

- **Order Matters**: Apply global configurations first. Any subsequent individual configurations for specific entities will override the global defaults.
- **Use Interfaces**: Leverage interfaces (like `ISoftDeletable` or `IAudit`) to selectively apply global rules to specific groups of entities.
- **EF Core 6.0+ Conventions**: For complex logic, explore `ConfigureConventions`, which allows for a cleaner separation of convention logic from relationship mapping.