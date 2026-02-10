# 8. Custom history table

# Custom Migrations History Table

By default, EF Core tracks applied migrations in a table named `__EFMigrationsHistory`. You can customize the name, schema, and structure of this table if needed.

## 1. Customizing Name and Schema

The most common requirement is renaming the table or moving it to a specific schema. Use the `MigrationsHistoryTable` method within the provider's options.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
{
    options.UseSqlServer(
        connectionString,
        x => x.MigrationsHistoryTable("__MyHistory", "dbo"));
}

```

<aside>
🛑 If you change the history table configuration **after** migrations have already been applied, you must manually rename the table in the database to match the new configuration.

</aside>

## 2. Advanced: Changing Table Structure

To change column names or other metadata facets of the history table, you must replace the `IHistoryRepository` service.

### Step A: Override the Repository

Inherit from the provider-specific implementation (e.g., `SqlServerHistoryRepository`).

```csharp
internal class MyHistoryRepository : SqlServerHistoryRepository
{
    public MyHistoryRepository(HistoryRepositoryDependencies dependencies)
        : base(dependencies) { }

    protected override void ConfigureTable(EntityTypeBuilder<HistoryRow> history)
    {
        base.ConfigureTable(history);

        // Rename the 'MigrationId' column to 'Id'
        history.Property(h => h.MigrationId).HasColumnName("Id");
    }
}

```

### Step B: Register the Service

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
{
    options.UseSqlServer(connectionString)
           .ReplaceService<IHistoryRepository, MyHistoryRepository>();
}

```

## 3. Summary

- Use `MigrationsHistoryTable` for simple name/schema changes.
- Use `IHistoryRepository` for structural column customizations.
- **Warning:** Provider-specific repository classes (like `SqlServerHistoryRepository`) are often in internal namespaces and might change in future EF Core releases.