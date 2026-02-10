# 4. Database Connection String in Entity Framework Core

# Database Connection Strings in EF Core

A **Connection String** is a string of characters that contains information necessary for the `DbContext` to establish a session with the database. It tells EF Core where the database is, what it’s called, and how to authenticate.

---

### Anatomy of a Connection String (SQL Server)

A typical SQL Server connection string consists of several key-value pairs:

| Key | Example | Description |
| --- | --- | --- |
| **Server** | `Server=.\SQLEXPRESS` | The network address of the SQL Server instance. |
| **Database** | `Database=EcommerceDB` | The name of the logical database to connect to. |
| **TrustServerCertificate** | `True` | Bypasses SSL certificate validation (Standard for Dev). |
| **Integrated Security** | `Trusted_Connection=True` | Uses the current Windows User account for login. |
| **SQL Authentication** | `User Id=xxx;Password=yyy` | Used when Windows Auth is not supported (e.g., Azure SQL). |

---

### Configuration Strategies

EF Core provides multiple ways to supply the connection string to the context.

### 1. Hardcoded Configuration (`OnConfiguring`)

Used primarily for learning, testing, or simple local tools. The string is written directly into the `DbContext`.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    if (!optionsBuilder.IsConfigured)
    {
        optionsBuilder.UseSqlServer("Server=.;Database=MyLocalDB;Trusted_Connection=True;TrustServerCertificate=True;");
    }
}
```

### 2. External Configuration (`appsettings.json`)

The industry-standard approach for modern .NET applications. This allows you to swap database targets (Dev, QA, Prod) without touching source code.

**appsettings.json:**

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=PROD_SERVER;Database=LiveDB;Trusted_Connection=True;Encrypt=True;"
  }
}
```

**Registration (Program.cs):**

```csharp
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));
```

### 3. Environment Variables

Critical for containerized (Docker) or cloud deployments. EF Core reads variables prefixed with `ConnectionStrings__`.

---

### Connection Resiliency

When moving to the cloud (e.g., Azure SQL), network “glitches” or transient failures are common. You can configure EF Core to automatically retry failed commands.

```csharp
options.UseSqlServer(connectionString, sqlOptions =>
{
    sqlOptions.EnableRetryOnFailure(
        maxRetryCount: 5,
        maxRetryDelay: TimeSpan.FromSeconds(10),
        errorNumbersToAdd: null);
});
```

---

### Synchronizing with the Database (Migrations)

Once your connection is configured, use EF Core Migrations to create the actual tables based on your C# classes.

| Action | dotNet CLI | Package Manager Console |
| --- | --- | --- |
| **Create Migration** | `dotnet ef migrations add Init` | `Add-Migration Init` |
| **Apply Changes** | `dotnet ef database update` | `Update-Database` |
| **Revert Last** | `dotnet ef database update <Name>` | `Update-Database <Name>` |

---

### Security Best Practices

1. **Never Check Secrets into Git:** Avoid storing production connection strings with passwords in `appsettings.json`.
2. **Use User Secrets:** Locally, use the `.NET User Secrets` tool to store your dev connection string.
3. **Managed Identity:** In Azure, use Managed Identity to eliminate the need for hardcoded db-passwords entirely.
4. **Encrypt=True:** Always enable encryption for production traffic to protect data in transit.