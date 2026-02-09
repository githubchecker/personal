# 4. Many-to-many

# Many-to-Many Relationships

A **Many-to-Many** relationship occurs when multiple entities on one side are associated with multiple entities on the other (e.g., a `Post` has many `Tags`, and a `Tag` belongs to many `Posts`). This is implemented via a **Join Table**.

## 1. Basic Mapping (By Convention)

Since EF Core 5.0, many-to-many relationships can be mapped without an explicit join class if you only need clear navigation.

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = []; // Skip navigation
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = []; // Skip navigation
}

```

## 2. Explicit Configuration with `UsingEntity`

Use `UsingEntity` to customize the join table name, columns, or add additional data (payload).

### Custom Join Table Name

```csharp
modelBuilder.Entity<Post>()
    .HasMany(p => p.Tags)
    .WithMany(t => t.Posts)
    .UsingEntity("PostTagsJoinTable");

```

### Join Entity with Payload (Additional Data)

Define a separate class for the join entity to store extra fields like `CreatedOn`.

```csharp
public class PostTag
{
    public int PostId { get; set; }
    public int TagId { get; set; }
    public DateTime JoinedAt { get; set; }
}

modelBuilder.Entity<Post>()
    .HasMany(p => p.Tags)
    .WithMany(t => t.Posts)
    .UsingEntity<PostTag>(
        l => l.HasOne<Tag>().WithMany(),
        r => r.HasOne<Post>().WithMany(),
        j => { j.Property(pt => pt.JoinedAt).HasDefaultValueSql("getutcdate()"); }
    );

```

## 3. Navigations to the Join Entity

You can expose navigations to the join type while still keeping the convenience of skip navigations.

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<PostTag> PostTags { get; } = []; // Explicit navigation to join table
}

```

## 4. Advanced Scenarios

### Unidirectional Many-to-Many

If one side doesn't need a collection, leave the `WithMany()` argument empty:

```csharp
modelBuilder.Entity<Post>()
    .HasMany(p => p.Tags)
    .WithMany(); 

```

### Self-Referencing Many-to-Many

Used for relationships like `Person.Friends` or `Person.Followers`.

```csharp
public class Person
{
    public int Id { get; set; }
    public List<Person> Following { get; } = [];
    public List<Person> Followers { get; } = [];
}

modelBuilder.Entity<Person>()
    .HasMany(p => p.Following)
    .WithMany(p => p.Followers);

```

### Custom Primary Key for Join Table

By default, the join table uses a composite key of both Foreign Keys. You can add a separate PK:

```csharp
public class PostTag
{
    public int Id { get; set; } // Separate PK
    public int PostId { get; set; }
    public int TagId { get; set; }
}

```

### Alternate Keys

You can constrain the join table's foreign keys to **Alternate Keys** instead of Primary Keys using `.HasPrincipalKey()`.

## 5. Delete Behavior

Many-to-many relationships use **Cascade Delete** by default on both sides of the join table. If a `Post` is deleted, its corresponding `PostTag` entries are removed, but the `Tag` itself remains.