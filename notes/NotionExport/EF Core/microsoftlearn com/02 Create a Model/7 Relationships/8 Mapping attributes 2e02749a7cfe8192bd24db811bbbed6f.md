# 8. Mapping attributes

# Relationship Mapping Attributes (Data Annotations)

Data Annotations provide a declarative way to configure relationships directly within your entity classes. While the Fluent API is more powerful, these attributes cover common scenarios.

## 1. `[Required]`

Specifies that a relationship must exist by making the Foreign Key property or its shadow representation non-nullable.

- **Usage:** Apply to the FK property or the dependent navigation property.

```csharp
public class Post
{
    public int Id { get; set; }

    [Required] // Forces a non-nullable FK
    public int? BlogId { get; set; }
    public Blog Blog { get; set; }
}

```

## 2. `[ForeignKey]`

Explicitly connects a Foreign Key property to its corresponding navigation property. This is necessary when naming conventions aren't followed.

- **On Property:** Point to the navigation.
- **On Navigation:** Point to the property.

```csharp
public class Post
{
    [ForeignKey(nameof(Blog))]
    public int BlogKey { get; set; } // Foreign Key

    public Blog Blog { get; set; }   // Navigation
}

```

## 3. `[InverseProperty]`

Used when multiple navigation properties exist between the same two entities. It tells EF Core which navigations are pairs of the same relationship.

```csharp
public class Blog
{
    public int Id { get; set; }

    [InverseProperty(nameof(Post.Blog))]
    public List<Post> Posts { get; set; }

    public Post FeaturedPost { get; set; } // Separate relationship
}

public class Post
{
    public int Id { get; set; }
    public Blog Blog { get; set; }
}

```

## 4. `[DeleteBehavior]`

Configures the action taken on dependent entities when a principal is deleted.

- **Common Behaviors:** `Cascade`, `Restrict`, `SetNull`, `ClientSetNull`.

```csharp
public class Post
{
    [DeleteBehavior(DeleteBehavior.Restrict)]
    public Blog Blog { get; set; }
}

```

## 5. Summary Table

| Attribute | Location | Purpose |
| --- | --- | --- |
| `[Required]` | FK or Navigation | Makes the relationship mandatory (Not Null). |
| `[ForeignKey]` | FK or Navigation | Links a property to a navigation when names diverge. |
| `[InverseProperty]` | Navigation | Resolves ambiguous relationships between same types. |
| `[DeleteBehavior]` | Navigation | Defines cleanup behavior (e.g., Cascade Delete). |