# 20. Bulk configuration

# Model Bulk Configuration

When you need to apply the same configuration across multiple entities or properties, EF Core provides several bulk configuration strategies to reduce duplication and centralize logic.

## 1. Bulk Configuration in `OnModelCreating`

You can manually iterate over the model metadata and apply configuration. This is usually done at the end of `OnModelCreating`.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    foreach (var entityType in modelBuilder.Model.GetEntityTypes())
    {
        // Example: Set a shadow 'LastUpdated' property for every entity
        modelBuilder.Entity(entityType.Name).Property<DateTime>("LastUpdated");
    }
}

```

## 2. Pre-convention Configuration (EF 6+ / EF Core 6+)

By overriding `ConfigureConventions`, you can define configuration once for a specific CLR type. This is applied as properties are discovered.

- **Precedence:** Overrides both Conventions and Data Annotations.
- **Scope:** Can target specific types, base types, or interfaces.

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    // Apply a value converter to all 'Currency' properties
    configurationBuilder.Properties<Currency>().HaveConversion<CurrencyConverter>();

    // Set default facets for all strings
    configurationBuilder.Properties<string>().AreUnicode(false).HaveMaxLength(512);

    // Completely ignore specific types
    configurationBuilder.IgnoreAny(typeof(IList<>));
}

```

## 3. Model Building Conventions

Conventions are classes that react to model changes (interactive) or run at the end (finalizing).

### Finalizing Conventions

Use `IModelFinalizingConvention` to apply logic to the near-final state of the model.

```csharp
public class MaxStringLengthConvention : IModelFinalizingConvention
{
    public void ProcessModelFinalizing(IConventionModelBuilder modelBuilder, IConventionContext<IConventionModelBuilder> context)
    {
        foreach (var property in modelBuilder.Metadata.GetEntityTypes()
                     .SelectMany(e => e.GetDeclaredProperties())
                     .Where(p => p.ClrType == typeof(string)))
        {
            // Set max length only if it wasn't already configured explicitly
            property.Builder.HasMaxLength(512);
        }
    }
}

```

### Registration

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder.Conventions.Add(_ => new MaxStringLengthConvention());
}

```

## 4. Comparing Approaches

| Strategy | Best For... | Reacts to Changes? | Overrides Annotations? |
| --- | --- | --- | --- |
| `Metadata API` | One-off manual logic at the end. | No | Yes |
| `Pre-convention` | Simple type-based mapping (e.g., Converters). | Yes | **Yes** |
| `Finalizing Conv.` | Complex conditions on the final model. | No | No |
| `Interactive Conv.` | Deep integration/replacing EF behavior. | **Yes** | No |

## 5. Summary

- Use **Pre-convention configuration** for simple type-to-database mappings (converters, length, unicode).
- Use **Conventions** when you need more granular control or want to respect Data Annotations.
- Use **Metadata API** in `OnModelCreating` only if other methods don't support your specific scenario.