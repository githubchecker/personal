# 2. Eager loading

# Eager Loading of Related Data

**Eager Loading** retrieves related data from the database as part of the initial query. This is achieved using the `.Include()` and `.ThenInclude()` methods.

## 1. Basic Inclusion

Use `Include` to load directly related entities or collections.

```csharp
var blogs = await context.Blogs
    .Include(b => b.Posts)    // Collection
    .Include(b => b.Owner)    // Reference
    .ToListAsync();

```

## 2. Including Multiple Levels

Use `ThenInclude` to drill down into further levels of relationships.

```csharp
var blogs = await context.Blogs
    .Include(b => b.Posts)
        .ThenInclude(p => p.Author)
            .ThenInclude(a => a.Photo)
    .ToListAsync();

```

## 3. Filtered Include

You can filter, sort, or paginate the related data directly within the `Include` method.

```csharp
var blogs = await context.Blogs
    .Include(b => b.Posts
        .Where(p => p.IsPublished)
        .OrderByDescending(p => p.CreatedOn)
        .Take(5))
    .ToListAsync();

```

<aside>
⚠️ **Navigation Fixup:** In tracking queries, EF Core might show entities in the collection that don't match your filter if they were already loaded into the `DbContext` earlier. Use `AsNoTracking()` to avoid this.

</aside>

## 4. Include on Derived Types

If a navigation exists only on a derived type in an inheritance hierarchy, use a cast or `as` operator.

```csharp
var people = await context.People
    .Include(p => (p as Student).School)
    .ToListAsync();

```

## 5. Model-Level Auto-Include

You can configure a navigation to be included **automatically** in every query via the Fluent API.

```csharp
modelBuilder.Entity<Blog>().Navigation(b => b.Owner).AutoInclude();

```

### Bypassing Auto-Include

To skip auto-included data for a specific query, use `IgnoreAutoIncludes()`.

```csharp
var blogs = await context.Blogs.IgnoreAutoIncludes().ToListAsync();

```

## 6. Performance and Optimization

- **Cartesian Explosion:** Eager loading multiple collections in a single query can result in a massive result set (Cartesian product).
- **Solution:** Consider using **Split Queries** (`.AsSplitQuery()`) for complex relationships to retrieve related data in separate SQL batches.
- **Fixup:** EF Core automatically links entities that are already being tracked, even if not explicitly included.