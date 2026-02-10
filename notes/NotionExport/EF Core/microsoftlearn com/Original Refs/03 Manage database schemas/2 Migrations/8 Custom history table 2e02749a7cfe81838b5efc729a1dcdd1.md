# 8. Custom history table

# Custom Migrations History Table

By default, EF Core keeps track of which migrations have been applied to the database by recording them in a table named__EFMigrationsHistory. For various reasons, you may want to customize this table to better suit your needs.

<aside>
🔥 **IMPORTANT:** If you customize the Migrations history table after applying migrations, you are responsible for updating theexisting table in the database.

</aside>

## Schema and table name

You can change the schema and table name using the MigrationsHistoryTable() method in OnConfiguring() (orConfigureServices() on ASP.NET Core). Here is an example using the SQL Server EF Core provider.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
    => options.UseSqlServer(
        _connectionString,
        x => x.MigrationsHistoryTable("__MyMigrationsHistory", "mySchema"));

```

## Other changes

To configure additional aspects of the table, override and replace the provider-specificIHistoryRepository service. Here is an example of changing the MigrationId column name to Id on SQL Server.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
    => options
        .UseSqlServer(_connectionString)
        .ReplaceService<IHistoryRepository, MyHistoryRepository>();

```

<aside>
⚠️ **WARNING:** SqlServerHistoryRepository is inside an internal namespace and may change in future releases.

</aside>

```csharp
internal class MyHistoryRepository : SqlServerHistoryRepository
{
    public MyHistoryRepository(HistoryRepositoryDependencies dependencies)
        : base(dependencies)
    {
    }

    protected override void ConfigureTable(EntityTypeBuilder<HistoryRow> history)
    {
        base.ConfigureTable(history);

        history.Property(h => h.MigrationId).HasColumnName("Id");
    }
}

```