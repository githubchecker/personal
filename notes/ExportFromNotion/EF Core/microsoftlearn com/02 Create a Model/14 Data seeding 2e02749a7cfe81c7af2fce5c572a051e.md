# 14. Data seeding

# Data Seeding

Data seeding is the process of populating a database with an initial set of data. EF Core provides several ways to achieve this, depending on whether the data is static or dynamic.

## 1. UseSeeding (EF 9+) - Recommended

EF 9 introduced `UseSeeding` and `UseAsyncSeeding`, which are the recommended ways to seed data. These methods are called during `EnsureCreated`, `Migrate`, and `database update` commands.

- **Benefits:** Protected by migration locking; one dedicated location for seeding logic.
- **Tip:** Implement both synchronous and asynchronous versions to ensure compatibility with CLI tools.

```csharp
optionsBuilder
    .UseSqlServer(connectionString)
    .UseSeeding((context, _) =>
    {
        if (!context.Set<Blog>().Any(b => b.Url == "http://test.com"))
        {
            context.Set<Blog>().Add(new Blog { Url = "http://test.com" });
            context.SaveChanges();
        }
    });

```

## 2. Model Managed Data (`HasData`)

You can include data directly in your model configuration. EF Core Migrations will then automatically generate the necessary SQL to sync the database.

- **Best for:** Static lookup data (e.g., zip codes, categories).
- **Constraints:** Requires explicit Primary Key values; data is captured in migration snapshots.

```csharp
modelBuilder.Entity<Country>().HasData(
    new Country { CountryId = 1, Name = "USA" },
    new Country { CountryId = 2, Name = "Canada" }
);

```

## 3. Custom Initialization Logic

Perform seeding by calling `context.SaveChanges()` manually when the application starts.

```csharp
using (var context = new MyContext())
{
    await context.Database.EnsureCreatedAsync();
    // Your seeding logic here...
}

```

*Note: Be careful with concurrency when running multiple instances of the app.*

## 4. Manual Migration Customization

If `HasData` is too restrictive, you can manually add SQL commands or `InsertData` calls inside your migration's `Up` method.

```csharp
migrationBuilder.InsertData(
    table: "Countries",
    columns: new[] { "Id", "Name" },
    values: new object[,] { { 1, "USA" }, { 2, "Canada" } }
);

```

## 5. Comparison Summary

| Method | Best For... | Managed By | Explicit PKs? |
| --- | --- | --- | --- |
| `UseSeeding` | General Seed / Environment Specific | Context Config | No |
| `HasData` | Constant Static Data | Migrations | **Yes** |
| **Custom Code** | Complex logic / external APIs | App Startup | No |
| **Manual SQL** | Large batches / RAW DB scripts | Migrations | No |