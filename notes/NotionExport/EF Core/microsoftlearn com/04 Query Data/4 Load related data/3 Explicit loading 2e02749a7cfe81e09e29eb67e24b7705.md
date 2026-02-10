# 3. Explicit loading

# Explicit Loading of Related Data

**Explicit Loading** allows you to manually load related entities for an already tracked entity at a later time. This is useful when you only need related data under specific conditions.

## 1. Basic Explicit Loading

Use the `Entry` API to load collections or individual references.

```csharp
var blog = await context.Blogs.SingleAsync(b => b.Id == 1);

// Load a collection
await context.Entry(blog)
    .Collection(b => b.Posts)
    .LoadAsync();

// Load a single reference
await context.Entry(blog)
    .Reference(b => b.Owner)
    .LoadAsync();

```

## 2. Querying Navigation Properties

The `Query()` method provides access to the underlying LINQ query used for a navigation property. This allows you to perform operations on the related data **without loading it all into memory**.

### Running Aggregates

Calculate counts or sums on the server side:

```csharp
int postCount = await context.Entry(blog)
    .Collection(b => b.Posts)
    .Query()
    .CountAsync();

```

### Applying Filters

Load only a subset of related data into the collection:

```csharp
await context.Entry(blog)
    .Collection(b => b.Posts)
    .Query()
    .Where(p => p.Rating > 4)
    .ToListAsync();

```

## 3. Key Takeaways

- **Tracking Required:** Explicit loading only works for entities already tracked by the `DbContext`.
- **Database Roundtrips:** Each `Load()` call results in a separate database request.
- **Efficiency:** Use `Query()` to minimize data transfer when you only need a subset or a count of related data.