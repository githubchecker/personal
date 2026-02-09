# 2. Entity Types

# Entity Types

An **Entity Type** is a .NET class that EF Core maps to a database table. EF Core uses these types to perform CRUD operations and manage the database schema via migrations.

## 1. Including Types in the Model

Types are included in the EF Core model through:

- **DbSet Properties:** e.g., `public DbSet<Blog> Blogs { get; set; }`.
- **Navigation Discovery:** Types found by recursively exploring navigation properties of already-included entities.
- **Manual Registration:** Using `modelBuilder.Entity<Type>()` in `OnModelCreating`.

## 2. Excluding Types

To prevent a class from being mapped to a table:

- **Data Annotations:** Use `[NotMapped]`.
- **Fluent API:** Use `modelBuilder.Ignore<TypeName>()`.

### Excluding from Migrations

You can include an entity in the model (to query it) but prevent migrations from creating/managing its table:

```csharp
modelBuilder.Entity<User>()
    .ToTable("AspNetUsers", t => t.ExcludeFromMigrations());

```

## 3. Table and Schema Mapping

### Table Name

By default, the table name matches the `DbSet` property name or the class name.

- **Fluent API:** `modelBuilder.Entity<Blog>().ToTable("blogs");`
- **Data Annotations:** `[Table("blogs")]`

### Database Schema

Organize tables into schemas (e.g., `dbo`, `blogging`).

- **Specific Table:** `modelBuilder.Entity<Blog>().ToTable("blogs", schema: "blogging");`
- **Default Schema (Model-wide):** `modelBuilder.HasDefaultSchema("blogging");`

## 4. Advanced Mappings

### Views

Map an entity to a database view. EF assumes the view exists and won't create it via migrations.

```csharp
modelBuilder.Entity<BlogReport>()
    .ToView("BlogSummaryView", schema: "reports");

```

### Table-Valued Functions (TVF)

Map an entity to a parameterless function.

```csharp
modelBuilder.Entity<ActiveBlogs>().ToFunction("GetActiveBlogs");

```

### Table Comments

Document your schema by adding comments to the database tables.

- **Fluent API:** `modelBuilder.Entity<Blog>().ToTable(t => t.HasComment("Primary blog store"));`
- **Data Annotations:** `[Comment("Primary blog store")]`

## 5. Shared-Type Entities

You can map multiple entity types to the same CLR type (e.g., `Dictionary<string, object>`). Each must have a unique name.

```csharp
modelBuilder.SharedTypeEntity<Dictionary<string, object>>("AuditLog", builder =>
{
    builder.Property<int>("Id");
    builder.Property<string>("Details");
});

// Access via Set
var logs = context.Set<Dictionary<string, object>>("AuditLog");

```