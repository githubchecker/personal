# 21. Alternating models with same DbContext

# Alternating Models with the same DbContext

By default, EF Core builds and caches the model the first time a `DbContext` type is used. If your `OnModelCreating` logic depends on a property of the context (e.g., a "tenant ID" or a "feature flag"), you must inform EF Core how to cache different versions of the model.

## 1. The Problem

The following logic will fail to reflect changes because EF Core caches the model based purely on the `DbContext` type:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    if (UseLegacySchema)
    {
        modelBuilder.Entity<User>().ToTable("OldUsers");
    }
    else
    {
        modelBuilder.Entity<User>().ToTable("Users");
    }
}

```

## 2. The Solution: `IModelCacheKeyFactory`

To support dynamic models, implement `IModelCacheKeyFactory` to generate a cache key that includes the variable property.

```csharp
public class DynamicModelCacheKeyFactory : IModelCacheKeyFactory
{
    public object Create(DbContext context, bool designTime)
        => context is MyDbContext myContext
            ? (context.GetType(), myContext.UseLegacySchema, designTime)
            : (object)context.GetType();

    // Required for older EF Core versions
    public object Create(DbContext context) => Create(context, false);
}

```

## 3. Registering the Factory

Register the factory in `OnConfiguring` using `ReplaceService`.

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder
        .UseSqlServer(connectionString)
        .ReplaceService<IModelCacheKeyFactory, DynamicModelCacheKeyFactory>();
}

```

## 4. Key Takeaways

- **Performance:** Creating many models can impact startup performance and memory usage. Only use this if the physical schema actually differs.
- **Design Time:** Ensure your factory handles the `designTime` flag to support migrations correctly.
- **Immutability:** The property used for caching (e.g., `UseLegacySchema`) should ideally be set once during context initialization and not changed during the context lifetime.