# 6. Shadow and indexer properties

# Shadow and Indexer Properties

EF Core allows you to define properties that are not physically present in your C# entity class. These are categorised into **Shadow Properties** and **Indexer Properties**.

## 1. Shadow Properties

Shadow properties exist only in the EF Core model and the Change Tracker, but not in your .NET class. They are useful for data that shouldn't be exposed in the domain model (e.g., `LastUpdated` audit fields or hidden Foreign Keys).

### Foreign Key Shadow Properties

If you define a navigation property without a corresponding Foreign Key property, EF Core creates a shadow property automatically.

```csharp
public class Post
{
    public int Id { get; set; }
    public Blog Blog { get; set; } // Shadow property 'BlogId' created automatically
}

```

### Explicit Configuration

Use the Fluent API to define a shadow property:

```csharp
modelBuilder.Entity<Blog>()
    .Property<DateTime>("LastUpdated");

```

### Accessing Shadow Properties

- **In Code:** `context.Entry(myBlog).Property("LastUpdated").CurrentValue = DateTime.Now;`
- **In LINQ:** `context.Blogs.OrderBy(b => EF.Property<DateTime>(b, "LastUpdated"));`

## 2. Indexer Properties

Indexer properties are backed by an indexer in the .NET class. This allows you to add properties to the entity type without changing the class definition.

### Configuration

```csharp
modelBuilder.Entity<Blog>().IndexerProperty<DateTime>("LastUpdated");

public class Blog
{
    private readonly Dictionary<string, object> _data = new();
    public int Id { get; set; }

    // Indexer to back the dynamic properties
    public object this[string key]
    {
        get => _data[key];
        set => _data[key] = value;
    }
}

```

## 3. Property Bag Entity Types

A **Property Bag** is an entity type that contains *only* indexer properties. Currently, only `Dictionary<string, object>` is supported. This is useful for dynamic schemas.

### Configuration

```csharp
modelBuilder.SharedTypeEntity<Dictionary<string, object>>("Blog", builder =>
{
    builder.Property<int>("BlogId");
    builder.Property<string>("Url");
    builder.Property<DateTime>("LastUpdated");
});

// Access via Set
public DbSet<Dictionary<string, object>> Blogs => Set<Dictionary<string, object>>("Blog");

```

### Limitations

- No support for shadow properties.
- No support for inheritance or indexer-based navigations.
- Cannot use types other than `Dictionary<string, object>` as property bags.