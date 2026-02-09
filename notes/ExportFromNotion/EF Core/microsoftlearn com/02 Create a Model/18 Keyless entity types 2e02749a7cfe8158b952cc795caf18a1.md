# 18. Keyless entity types

# Keyless Entity Types

**Keyless Entity Types** allow you to query data that doesn't have a primary key. These are typically used for mapping database views, raw SQL query results, or tables without keys.

## 1. Defining Keyless Types

You can configure a type as keyless using the `[Keyless]` attribute or the Fluent API.

### Via Data Annotations

```csharp
[Keyless]
public class BlogPostsCount
{
    public string BlogName { get; set; }
    public int PostCount { get; set; }
}

```

### Via Fluent API

```csharp
modelBuilder.Entity<BlogPostsCount>().HasNoKey();

```

## 2. Key Characteristics

Keyless entity types differ from regular entities in the following ways:

- **Read-Only:** They are **never tracked** by the `DbContext`. Changes are not saved to the database.
- **No Identity:** They cannot have a Primary Key defined.
- **Limited Relationships:** They can only act as the **dependent** end of a relationship and cannot contain navigations to owned entities.
- **Discovery:** They are never discovered by convention; they must be explicitly configured.

## 3. Usage Scenarios

| Scenario | Description |
| --- | --- |
| **SQL Queries** | Serving as the result type for `.FromSqlRaw`. |
| **Views** | Mapping to database views that lack a PK. |
| **Tables** | Mapping to legacy tables without primary keys. |
| **Model Queries** | Mapping to a LINQ query defined in the model (Defining Query). |

## 4. Mapping to Views

Use `.ToView()` to map a keyless entity to a database view.

```csharp
modelBuilder.Entity<BlogPostsCount>()
    .HasNoKey()
    .ToView("View_BlogPostCounts");

```

## 5. Summary Table: Regular vs. Keyless Entities

| Feature | Regular Entity | Keyless Entity |
| --- | --- | --- |
| **Primary Key** | Required | **None** |
| **Change Tracking** | Yes | **No** |
| **CRUD Support** | Create, Read, Update, Delete | **Read-Only** |
| **Conventions** | Automatic Discovery | **Explicit Config Only** |
| **Relationships** | Full Support | Dependent Only |