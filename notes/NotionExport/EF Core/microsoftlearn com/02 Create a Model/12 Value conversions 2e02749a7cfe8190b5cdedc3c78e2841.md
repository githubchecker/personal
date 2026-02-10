# 12. Value conversions

# Value Conversions

**Value Converters** allow you to transform property values when reading from or writing to the database. Typical use cases include encrypting strings, converting enums to strings, or serializing objects to JSON.

## 1. Basic Configuration

A converter is defined by two expressions: **Model to Provider** and **Provider to Model**.

```csharp
modelBuilder.Entity<Rider>()
    .Property(e => e.Mount)
    .HasConversion(
        v => v.ToString(), // Model to Provider
        v => (EquineBeast)Enum.Parse(typeof(EquineBeast), v)); // Provider to Model

```

### Pre-defined Conversions

EF Core has many built-in converters. You can often trigger them by just specifying the target type:

```csharp
// Converts Enum to String automatically
modelBuilder.Entity<Rider>().Property(e => e.Mount).HasConversion<string>();

// Converts Bool to 0/1 automatically
modelBuilder.Entity<User>().Property(e => e.IsActive).HasConversion<int>();

```

## 2. Bulk (Pre-convention) Configuration

To apply a converter to all properties of a specific type across the entire model:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder
        .Properties<Currency>()
        .HaveConversion<CurrencyConverter>();
}

```

## 3. Built-in Converters Summary

| Model Type | Provider Type | Behavior |
| --- | --- | --- |
| `bool` | `int` | 0 / 1 mapping |
| `bool` | `string` | "Y" / "N" (use `BoolToStringConverter`) |
| `Enum` | `string` | Enum names stored as text |
| `Enum` | `int` | Underlying numeric value |
| `Uri` | `string` | Standard URI string |
| `Guid` | `string` | Formatted GUID string |
| `DateTime` | `long` | Ticks or encoded binary |

## 4. Advanced Use Cases

### JSON Serialization (Composite Objects)

Converters can map a complex object to a single column (e.g., JSON).*Note: Requires a* `ValueComparer` *for mutable types.*

```csharp
modelBuilder.Entity<Order>()
    .Property(e => e.Price)
    .HasConversion(
        v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null),
        v => JsonSerializer.Deserialize<Money>(v, (JsonSerializerOptions)null));

```

### Type-Safe Keys

Prevent accidental misuse of primitive IDs by wrapping them in structs.

```csharp
public readonly struct BlogKey(int id) { public int Id { get; } = id; }

modelBuilder.Entity<Blog>().Property(e => e.Id)
    .HasConversion(v => v.Id, v => new BlogKey(v));

```

### DateTime forced to UTC

Ensure all dates read from the database have the `DateTimeKind.Utc` flag.

```csharp
modelBuilder.Entity<Post>().Property(e => e.PublishedOn)
    .HasConversion(v => v, v => DateTime.SpecifyKind(v, DateTimeKind.Utc));

```

## 5. Converter Mapping Hints

You can provide hints to the database provider about the target column facets (size, unicode, etc.) inside the converter.

```csharp
var converter = new ValueConverter<EquineBeast, string>(
    v => v.ToString(),
    v => (EquineBeast)Enum.Parse(typeof(EquineBeast), v),
    new ConverterMappingHints(size: 20, unicode: false));

```

## 6. Limitations

- **Nulls:** Converters cannot currently transform `null` values.
- **Multiple Columns:** A converter can only map to a single column.
- **Context Access:** Converters cannot access the `DbContext` instance.
- **LINQ Performance:** You cannot query members of a converted object (e.g., `Where(o => o.Price.Amount > 10)` fails if `Price` is serialized JSON).