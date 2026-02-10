# 7. Multiple providers

# Migrations with Multiple Providers

The [EF Core Tools](https://learn.microsoft.com/en-us/ef/core/cli/) only scaffold migrations for the active provider. Sometimes, however, you may want to use more than one provider (for example Microsoft SQL Server and SQLite) with your DbContext. Handle this by maintaining multiple sets of migrations--one for each provider--and adding a migration to each for every model change.

## Using multiple context types

One way to create multiple migration sets is to use one DbContext type per provider.

```csharp
class SqliteBlogContext : BlogContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseSqlite("Data Source=my.db");
}

```

Specify the context type when adding new migrations.

### .NET CLI

```bash
dotnet ef migrations add InitialCreate --context BlogContext --output-dir Migrations/SqlServerMigrations
dotnet ef migrations add InitialCreate --context SqliteBlogContext --output-dir Migrations/SqliteMigrations

```

### Visual Studio

```powershell
Add-Migration InitialCreate -Context BlogContext -OutputDir Migrations\SqlServerMigrations
Add-Migration InitialCreate -Context SqliteBlogContext -OutputDir Migrations\SqliteMigrations

```

<aside>
💡 **TIP:** You don't need to specify the output directory for subsequent migrations since they are created as siblings to thelast one.

</aside>

## Using one context type

It's also possible to use one DbContext type. This currently requires moving the migrations into a separate assembly. Please refer to [Using a Separate Migrations Project](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/projects) for instructions on setting up your projects.

<aside>
💡 **TIP:** You can view this article's [sample on GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Schemas/TwoProjectMigrations) .

</aside>

You can pass arguments into the app from the tools. This can enable a more streamlined workflow that avoids having to make manual changes to the project when running the tools.

Here's one pattern that works well when using a [Generic Host](https://learn.microsoft.com/en-us/dotnet/core/extensions/generic-host).

```csharp
public static IHostBuilder CreateHostBuilder(string[] args)
    => Host.CreateDefaultBuilder(args)
        .ConfigureServices(
            (hostContext, services) =>
            {
                services.AddHostedService<Worker>();

                // Set the active provider via configuration
                var configuration = hostContext.Configuration;
                var provider = configuration.GetValue("Provider", "SqlServer");

                services.AddDbContext<BlogContext>(
                    options => _ = provider switch
                    {
                        "Sqlite" => options.UseSqlite(
                            configuration.GetConnectionString("SqliteConnection"),
                            x => x.MigrationsAssembly("SqliteMigrations")),

                        "SqlServer" => options.UseSqlServer(
                            configuration.GetConnectionString("SqlServerConnection"),
                            x => x.MigrationsAssembly("SqlServerMigrations")),

                        _ => throw new Exception($"Unsupported provider: {provider}")
                    });
            });

```

Since the default host builder reads configuration from command-line arguments, you can specify the provider when running the tools.

### .NET CLI

```bash
dotnet ef migrations add MyMigration --project ../SqlServerMigrations -- --provider SqlServer
dotnet ef migrations add MyMigration --project ../SqliteMigrations -- --provider Sqlite

```

<aside>
💡 **TIP:** The -- token directs dotnet ef to treat everything that follows as an argument and not try to parse them as options. Any extra arguments not used by dotnet ef are forwarded to the app.

</aside>

### Visual Studio

```powershell
Add-Migration MyMigration -Args "--provider SqlServer"
Add-Migration MyMigration -Args "--provider Sqlite"

```