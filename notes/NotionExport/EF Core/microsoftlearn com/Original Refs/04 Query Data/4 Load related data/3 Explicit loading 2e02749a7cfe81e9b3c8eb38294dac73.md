# 3. Explicit loading

# Explicit Loading of Related Data

## Explicit loading

You can explicitly load a navigation property via the DbContext.Entry(...) API.

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs
        .SingleAsync(b => b.BlogId == 1);

    await context.Entry(blog)
        .Collection(b => b.Posts)
        .LoadAsync();

    await context.Entry(blog)
        .Reference(b => b.Owner)
        .LoadAsync();
}

```

You can also explicitly load a navigation property by executing a separate query that returns the related entities. If change tracking is enabled, then when a query materializes an entity, EF Core will automatically set the navigation properties of the newly-loaded entity to refer to any entities already loaded, and set the navigation properties of the already-loaded entities to refer to the newly loaded entity.

## Querying related entities

You can also get a LINQ query that represents the contents of a navigation property.

This allows you to apply other operators over the query. For example, applying an aggregate operator over the related entities without loading them into memory.

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs
        .SingleAsync(b => b.BlogId == 1);

    var postCount = await context.Entry(blog)
        .Collection(b => b.Posts)
        .Query()
        .CountAsync();
}

```

You can also filter which related entities are loaded into memory.

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs
        .SingleAsync(b => b.BlogId == 1);

    var goodPosts = await context.Entry(blog)
        .Collection(b => b.Posts)
        .Query()
        .Where(p => p.Rating > 3)
        .ToListAsync();
}

```