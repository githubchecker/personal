# 3. Create and drop APIs

# Create and Drop APIs

The `EnsureCreated` and `EnsureDeleted` APIs provide a lightweight way to manage database schemas without using Migrations. They are ideal for transient data scenarios like unit testing, local caching, or rapid prototyping.

## 1. Core APIs

### `EnsureDeleted()` / `EnsureDeletedAsync()`

Drops the entire database if it exists.

```csharp
await context.Database.EnsureDeletedAsync();

```

### `EnsureCreated()` / `EnsureCreatedAsync()`

- Creates the database if it does not exist.
- Initializes the schema (tables, indexes, etc.) **only if the database contains no tables**.

```csharp
await context.Database.EnsureCreatedAsync();

```

## 2. Important Considerations

### Conflict with Migrations

`EnsureCreated` and Migrations are **incompatible**:

- `EnsureCreated` does not track migration history (the `__EFMigrationsHistory` table is not created).
- If you use `EnsureCreated` first, subsequent Migrations will fail because they will try to create tables that already exist.

<aside>
💡 **Recommendation:** If you plan to evolve your database over time in production, start with **Migrations** from day one. Use `EnsureCreated` only for throwaway databases.

</aside>

## 3. Generating Create Scripts

You can retrieve the SQL script that `EnsureCreated` would execute using `GenerateCreateScript`. This is useful for inspection or manual execution.

```csharp
string sql = context.Database.GenerateCreateScript();

```

## 4. Advanced: Manual Schema Creation

If you have a complex scenario (e.g., multiple contexts in one database) where `EnsureCreated` stops because *some* tables exist, you can use the `IRelationalDatabaseCreator` to force table creation for a specific context.

```csharp
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage;

var databaseCreator = context.GetService<IRelationalDatabaseCreator>();
if (!databaseCreator.HasTables())
{
    databaseCreator.CreateTables();
}

```

## 5. Summary Use Cases

| Scenario | Use Migrations? | Use Create/Drop? |
| --- | --- | --- |
| **Production Web App** | **Yes** | No |
| **In-Memory Testing** | No | **Yes** |
| **Local SQLite Cache** | No | **Yes** |
| **Rapid Prototype** | No | **Yes** |