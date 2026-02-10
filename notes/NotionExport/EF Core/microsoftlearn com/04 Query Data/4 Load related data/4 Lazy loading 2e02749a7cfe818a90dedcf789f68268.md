# 4. Lazy loading

# Lazy Loading of Related Data

**Lazy Loading** automatically fetches related data from the database the first time a navigation property is accessed.

## 1. Using Proxies (Recommended for Simplicity)

This is the easiest implementation but requires all navigation properties to be `virtual`.

### Setup

- Install the NuGet package: `Microsoft.EntityFrameworkCore.Proxies`.
- Enable it in your `DbContext` configuration:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
    => options.UseLazyLoadingProxies().UseSqlServer(connectionString);

```

### Entity Requirements

- The entity class must be `public` and not `sealed`.
- All navigation properties must be `virtual`.

```csharp
public class Blog
{
    public int Id { get; set; }
    public virtual ICollection<Post> Posts { get; set; } // Lazy loaded
}

```

## 2. Using `ILazyLoader` (No Proxies)

This approach is more complex but avoids the need for `virtual` properties and works with standard POCOs. It injects a loader service into the entity constructor.

```csharp
public class Blog
{
    private ICollection<Post> _posts;
    private ILazyLoader LazyLoader { get; set; }

    private Blog(ILazyLoader lazyLoader) => LazyLoader = lazyLoader;

    public ICollection<Post> Posts
    {
        get => LazyLoader.Load(this, ref _posts);
        set => _posts = value;
    }
}

```

## 3. Important Considerations

- **N+1 Query Problem:** Accessing a lazy-loaded property inside a `foreach` loop triggers a separate database query for **every row**.
- **Ghost Queries:** Properties can be accessed unexpectedly (e.g., by a debugger, a mapper like AutoMapper, or a serializer), triggering unintended database calls.
- **Context Lifetime:** The `DbContext` that loaded the parent entity **must still be alive** (not disposed) when the lazy navigation property is accessed, or an exception will occur.

## 4. Summary comparison

| Feature | Proxies | `ILazyLoader` |
| --- | --- | --- |
| **Effort** | Low | High |
| **Requirements** | Virtual properties | Constructor injection |
| **Entity Cleanliness** | Proxied at runtime | Dependent on EF Abstractions |
| **Best For** | General purpose | Clean POCOs or complex logic |