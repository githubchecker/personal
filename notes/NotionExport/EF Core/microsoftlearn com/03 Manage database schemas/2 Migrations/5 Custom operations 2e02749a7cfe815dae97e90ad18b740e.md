# 5. Custom operations

# Custom Migration Operations

When the built-in `MigrationBuilder` APIs are insufficient, you can extend them to support custom database operations like creating users, managing permissions, or configuring server-specific settings.

## 1. Using `MigrationBuilder.Sql()` (Simplest)

The easiest way to add a custom operation is to create an extension method that calls `Sql()`. You can check `migrationBuilder.ActiveProvider` to handle different databases.

```csharp
public static OperationBuilder<SqlOperation> CreateUser(
    this MigrationBuilder migrationBuilder, string name, string password)
{
    var sql = migrationBuilder.ActiveProvider switch
    {
        "Microsoft.EntityFrameworkCore.SqlServer" => 
            $"CREATE USER {name} WITH PASSWORD = '{password}';",
        "Npgsql.EntityFrameworkCore.PostgreSQL" => 
            $"CREATE USER {name} WITH PASSWORD '{password}';",
        _ => throw new NotSupportedException("Provider not supported.")
    };

    return migrationBuilder.Sql(sql);
}

// Usage in Migration file:
migrationBuilder.CreateUser("AdminUser", "SafePassword123");

```

## 2. Using `MigrationOperation` (Decoupled)

For more complex scenarios where you want to decouple the operation's intent from the SQL generation, you can define a custom `MigrationOperation`.

### Step A: Define the Operation

```csharp
public class CreateUserOperation : MigrationOperation
{
    public string Name { get; set; }
    public string Password { get; set; }
}

```

### Step B: Extension Method

```csharp
public static OperationBuilder<CreateUserOperation> CreateUser(
    this MigrationBuilder migrationBuilder, string name, string password)
{
    var operation = new CreateUserOperation { Name = name, Password = password };
    migrationBuilder.Operations.Add(operation);
    return new OperationBuilder<CreateUserOperation>(operation);
}

```

### Step C: Generate SQL

Override the `IMigrationsSqlGenerator` for your database provider to handle the new operation.

```csharp
public class MySqlGenerator : SqlServerMigrationsSqlGenerator
{
    public MySqlGenerator(MigrationsSqlGeneratorDependencies deps, ICommandBatchPreparer preparer) 
        : base(deps, preparer) { }

    protected override void Generate(MigrationOperation operation, IModel model, MigrationCommandListBuilder builder)
    {
        if (operation is CreateUserOperation userOp)
        {
            builder.Append($"CREATE USER {userOp.Name} WITH PASSWORD = '{userOp.Password}'").EndCommand();
        }
        else
        {
            base.Generate(operation, model, builder);
        }
    }
}

```

### Step D: Register the Generator

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
    => options.UseSqlServer(connectionString)
              .ReplaceService<IMigrationsSqlGenerator, MySqlGenerator>();

```

## 3. Summary

| Method | Complexity | Use Case |
| --- | --- | --- |
| `Sql()` **Extension** | Low | Simple one-off commands or provider-specific logic. |
| `MigrationOperation` | High | Creating reusable plugins or supporting multiple providers cleanly. |