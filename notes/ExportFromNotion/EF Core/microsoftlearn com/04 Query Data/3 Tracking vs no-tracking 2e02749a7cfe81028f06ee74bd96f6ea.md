# 3. Tracking vs. no-tracking

# Tracking vs. No-Tracking Queries

Tracking behavior determines if EF Core maintains a reference to an entity in its **Change Tracker**. This behavior affects performance, memory usage, and the ability to save changes.

## 1. Tracking Queries (Default)

By default, queries that return entity types are tracking.

- **Change Detection:** Any modifications to tracked entities are persisted to the database when `context.SaveChangesAsync()` is called.
- **Identity Resolution:** If the same entity is retrieved multiple times (or already exists in the context), EF Core returns the **same object instance**.

```csharp
var blog = await context.Blogs.FirstAsync(b => b.Id == 1);
blog.Rating = 5; 
await context.SaveChangesAsync(); // Update is sent to DB

```

## 2. No-Tracking Queries (`AsNoTracking`)

Use no-tracking queries for read-only scenarios.

- **Performance:** Faster and uses less memory because the change tracker is bypassed.
- **No Persistence:** Changes made to these entities are **not** detected by the `DbContext`.

```csharp
var blogs = await context.Blogs
    .AsNoTracking()
    .ToListAsync();

```

### Identity Resolution in No-Tracking

By default, `AsNoTracking` returns a **new instance** for every row, even if the same ID appears multiple times in the results. To get consistent instances without context tracking, use:

```csharp
var blogs = await context.Blogs
    .AsNoTrackingWithIdentityResolution()
    .ToListAsync();

```

## 3. Projections and Tracking

Tracking behavior depends on what the query returns:

| Query Return | Tracking Behavior |
| --- | --- |
| **Full Entity** (`Blog`) | **Tracked** (unless `AsNoTracking` used) |
| **Anonymous with Entity** (`new { Blog = b, ... }`) | **Tracked** (The `b` instance is tracked) |
| **Scalar Properties** (`new { b.Id, b.Name }`) | **Not Tracked** |
| **Keyless Entities** | **Never Tracked** |

## 4. Default Tracking Behavior

You can change the default for the entire `DbContext` instance:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
}

```

*Note: You can still override this locally using* `.AsTracking()` *for specific queries.*

## 5. Summary

- **Use Tracking** when you intend to modify the retrieved data and save it back to the database.
- **Use No-Tracking** for read-only displays, exports, or data processing where performance is critical.
- **Use Identity Resolution** with no-tracking when your result set contains many repeating identical entities (to save memory).