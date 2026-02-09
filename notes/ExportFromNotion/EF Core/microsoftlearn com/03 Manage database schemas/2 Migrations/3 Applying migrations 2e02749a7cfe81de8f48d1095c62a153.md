# 3. Applying migrations

# Applying Migrations

Once migrations are created, they must be deployed to target databases. Different strategies are better suited for development vs. production environments.

## 1. SQL Scripts (Recommended for Production)

Generating SQL scripts is the safest way to deploy changes. It allows for DBA review and integration into existing deployment pipelines.

### Generating Scripts

- **Latest Migration:** `dotnet ef migrations script`
- **Specific Range:** `dotnet ef migrations script <FromMigration> <ToMigration>`
- **Idempotent Script:** `dotnet ef migrations script --idempotent`*Internal checks (via* `IF NOT EXISTS`*) ensure a migration is only applied if it's missing.*

## 2. Migration Bundles (Recommended for CI/CD)

**Migration Bundles** are self-contained executables (`efbundle`) that contain everything needed to apply migrations.

- **Benefits:** No .NET SDK or runtime required on the target server; easy to use in Docker or CI/CD pipelines.
- **Create Bundle:** `dotnet ef migrations bundle`
- **Run Bundle:** `.\efbundle.exe --connection "YourConnectionString"`

## 3. Command-Line Tools (Development)

The `database update` command applies migrations directly to the database.

| Command | .NET CLI | Package Manager Console |
| --- | --- | --- |
| **Apply All** | `dotnet ef database update` | `Update-Database` |
| **Target Version** | `dotnet ef database update <Name>` | `Update-Database <Name>` |

*Note: Updating to an earlier migration will trigger a rollback (reverting* `Down` *methods).*

## 4. Applying at Runtime (Programmatic)

You can call `context.Database.MigrateAsync()` during application startup.

```csharp
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<MyDbContext>();
    await db.Database.MigrateAsync();
}

```

<aside>
⚠️ **Production Risk:** Runtime migration is risky for multi-instance applications (concurrency), requires high DB permissions, and doesn't allow for SQL review. Scripts or Bundles are preferred for production.

</aside>

## 5. Summary Strategy

| Environment | Recommended Strategy | Reason |
| --- | --- | --- |
| **Local Dev** | `database update` | Speed and convenience. |
| **CI/CD** | `migrations bundle` | Self-contained, easy automation. |
| **Production** | `SQL Script` | DBA review, audit trail, safest. |
| **Prototyping** | `MigrateAsync()` | Quickest to get running. |