# 7. Multiple providers

# Migrations with Multiple Providers

EF Core tools scaffold migrations based on the *active* provider. If you want to support multiple database providers (e.g., SQL Server and SQLite), you must maintain separate sets of migrations.

## 1. Using Multiple Context Types

The simplest way is to create a derived `DbContext` for each provider and specify the output directory for their migrations.

```csharp
public class SqliteBlogContext : BlogContext 
{ 
    /* UseSqlite in OnConfiguring */ 
}

public class SqlServerBlogContext : BlogContext 
{ 
    /* UseSqlServer in OnConfiguring */ 
}

```

### Scaffolding

- **SQL Server:** `dotnet ef migrations add Initial --context SqlServerBlogContext --output-dir Migrations/SqlServer`
- **SQLite:** `dotnet ef migrations add Initial --context SqliteBlogContext --output-dir Migrations/Sqlite`

## 2. Using One Context Type (Conditional)

You can use a single `DbContext` and toggle the provider based on configuration or command-line arguments. This usually requires moving migrations into separate assemblies.

### Startup Configuration

```csharp
services.AddDbContext<BlogContext>(options =>
{
    var provider = configuration["Provider"];
    _ = provider switch
    {
        "Sqlite" => options.UseSqlite(conn, x => x.MigrationsAssembly("SqliteMigrations")),
        "SqlServer" => options.UseSqlServer(conn, x => x.MigrationsAssembly("SqlServerMigrations")),
        _ => throw new Exception("Unknown provider")
    };
});

```

### Scaffolding with Arguments

You can pass custom arguments to your app's entry point to select the provider during design-time.

- **CLI:** `dotnet ef migrations add MyMigration -- --provider Sqlite`
- **PMC:** `Add-Migration MyMigration -Args "--provider Sqlite"`

*Note: The* `--` *token in the CLI tells* `dotnet ef` *to pass the remaining arguments directly to your application's* `Program.Main`*.*

## 3. Summary of Strategies

| Strategy | Pros | Cons |
| --- | --- | --- |
| **Multiple Contexts** | Simple to implement, no complex logic. | Redundant context classes. |
| **Single Context** | Cleanest model, high reusability. | Requires conditional DI setup and CLI arguments. |

## 4. Key Takeaways

- **Provider Differences:** Ensure your `OnModelCreating` configuration is compatible across all target providers (e.g., avoid SQL Server-specific data types if supporting SQLite).
- **Manual Review:** Always review both generated migrations to ensure the schema changes are equivalent and correct for each database engine.