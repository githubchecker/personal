# 2. Managing migrations

# Managing Migrations

This guide covers common tasks for maintaining your EF Core migrations throughout the development lifecycle.

## 1. Adding and Removing Migrations

### Add a Migration

Creates code to sync the database with your current model.

- **CLI:** `dotnet ef migrations add <Name>`
- **Files Created:**
- `TIMESTAMP_Name.Designer.cs`: Metadata for EF Core.
- `ModelSnapshot.cs`: Snapshot for calculating the next delta.

### Remove a Migration

Deletes the **latest** migration that hasn't been applied to a database yet.

- **CLI:** `dotnet ef migrations remove`
- **Warning:** Do not remove migrations that are already checked into source control or applied to shared environments.

## 2. Customizing Migration Code

Sometimes EF Core generates code that might cause data loss. You should manually edit the `Up` method in these cases.

### Renaming a Column

EF Core often detects a rename as a `Drop` + `Add`. To preserve data, change it to `RenameColumn`.

```csharp
// Manual edit in Up() method:
migrationBuilder.RenameColumn(
    name: "OldName",
    table: "Customers",
    newName: "FullName");

```

### Data Migration with Raw SQL

Use `migrationBuilder.Sql` to move data or apply logic before dropping old columns.

```csharp
migrationBuilder.AddColumn<string>(name: "FullName", table: "Customer", nullable: true);
migrationBuilder.Sql("UPDATE Customer SET FullName = FirstName + ' ' + LastName;");
migrationBuilder.DropColumn(name: "FirstName", table: "Customer");
migrationBuilder.DropColumn(name: "LastName", table: "Customer");

```

### Managing Non-Table Objects

You can use `migrationBuilder.Sql` to manage Stored Procedures, Views, Triggers, or Full-Text Search.

## 3. Maintenance Commands

### List Migrations

Shows a history of all migrations in the project.

- **CLI:** `dotnet ef migrations list`

### Check for Pending Changes (EF 8+)

Verifies if the C# model matches the latest migration snapshot.

- **CLI:** `dotnet ef migrations has-pending-model-changes`
- **C#:** `context.Database.HasPendingModelChanges()` (useful for unit tests).

## 4. Resetting (Squashing) Migrations

If your migrations history becomes too large, you can "squash" them into a single initial migration:

- **Delete** the `Migrations` folder.
- **Clear** the `__EFMigrationsHistory` table in your database.
- **Add** a new initial migration (`dotnet ef migrations add Initial`).
- **Update** the `__EFMigrationsHistory` manually if the database already exists, to mark the new migration as "applied".

<aside>
⚠️ Squashing loses all custom SQL code and history preserved in previous migration files. Apply with caution.

</aside>