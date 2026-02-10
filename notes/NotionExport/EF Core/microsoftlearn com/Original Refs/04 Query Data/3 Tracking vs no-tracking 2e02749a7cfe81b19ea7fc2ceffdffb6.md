# 3. Tracking vs. no-tracking

# Tracking vs. No-Tracking Queries

Tracking behavior controls if Entity Framework Core keeps information about an entity instance in its change tracker. If an entity is tracked, any changes detected in the entity are persisted to the database during SaveChanges. EF Core also fixes up navigation properties between the entities in a tracking query result and the entities that are in the change tracker.

<aside>
ℹ️ **NOTE:** [Keyless entity types](https://learn.microsoft.com/en-us/ef/core/modeling/keyless-entity-types) are never tracked. Wherever this article mentions entity types, it refers to entity types which have a key defined.

</aside>

<aside>
💡 **TIP:** You can view this article's [sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Querying/Tracking) on GitHub.

</aside>

## Tracking queries

By default, queries that return entity types are tracking. A tracking query means any changes to entity instances are persisted by SaveChanges. In the following example, the change to the blogs rating is detected and persisted to the database during SaveChanges:

```csharp
var blog = await context.Blogs.SingleOrDefaultAsync(b => b.BlogId == 1);
blog.Rating = 5;
await context.SaveChangesAsync();

```

When the results are returned in a tracking query, EF Core checks if the entity is already in the context. If EF Core finds an existing entity, then the same instance is returned, which can potentially use less memory and be faster than a no-tracking query. EF Core doesn't overwrite current and original values of the entity's properties in the entry with the database values. If the entity isn't found in the context, EF Core creates a new entity instance and attaches it to the context. Query results don't contain any entity which is added to the context but not yet saved to the database.

## No-tracking queries

No-tracking queries are useful when the results are used in a read-only scenario. They're generally quicker to execute because there's no need to set up the change tracking information. If the entities retrieved from the database don't need to be updated, then a no-tracking query should be used. An individual query can be set to be no-tracking. A no-tracking query also give results based on what's in the database disregarding any local changes or added entities.

```csharp
var blogs = await context.Blogs
    .AsNoTracking()
    .ToListAsync();

```

The default tracking behavior can be changed at the context instance level:

```csharp
context.ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;

var blogs = await context.Blogs.ToListAsync();

```

The next section explains when a no-tracking query might be less efficient than a tracking query.

## Identity resolution

Since a tracking query uses the change tracker, EF Core does identity resolution in a tracking query. When materializing an entity, EF Core returns the same entity instance from the change tracker if it's already being tracked. If the result contains the same entity multiple times, the same instance is returned for each occurrence. No-tracking queries:

- Don't use the change tracker and don't do identity resolution.
- Return a new instance of the entity even when the same entity is contained in the result multiple times.

Tracking and no-tracking can be combined in the same query. That is, you can have a no-tracking query, which does identity resolution in the results. Just like [AsNoTracking](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.asnotracking) queryable operator, we've added another operator [AsNoTrackingWithIdentityResolution(IQueryable)](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.asnotrackingwithidentityresolution#microsoft-entityframeworkcore-entityframeworkqueryableextensions-asnotrackingwithidentityresolution-1(system-linq-iqueryable((-0)))). There's also associated entry added in the [QueryTrackingBehavior](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.querytrackingbehavior) enum. When the query to use identity resolution is configured with no tracking, a stand-alone change tracker is used in the background when generating query results so each instance is materialized only once. Since this change tracker is different from the one in the context, the results are not tracked by the context. After the query is enumerated fully, the change tracker goes out of scope and garbage collected as required.

```csharp
var blogs = await context.Blogs
    .AsNoTrackingWithIdentityResolution()
    .ToListAsync();

```

## Configuring the default tracking behavior

If you find yourself changing the tracking behavior for many queries, you may want to change the default instead:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder
        .UseSqlServer(@"Server=(localdb)\mssqllocaldb;Database=EFQuerying.Tracking;Trusted_Connection=True;ConnectRetryCount=0")
        .UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
}

```

This makes all your queries no-tracking by default. You can still add [AsTracking](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.astracking) to make specific queries tracking.

## Tracking and custom projections

Even if the result type of the query isn't an entity type, EF Core will still track entity types contained in the result by default. In the following query, which returns an anonymous type, the instances of Blog in the result set will be tracked.

```csharp
var blog = context.Blogs
    .Select(
        b =>
            new { Blog = b, PostCount = b.Posts.Count() });

```

If the result set contains entity types coming out from LINQ composition, EF Core will track them.

```csharp
var blog = context.Blogs
    .Select(
        b =>
            new { Blog = b, Post = b.Posts.OrderBy(p => p.Rating).LastOrDefault() });

```

If the result set doesn't contain any entity types, then no tracking is done. In the following query, we return an anonymous type with some of the values from the entity (but no instances of the actual entity type). There are no tracked entities coming out of the query.

```csharp
var blog = context.Blogs
    .Select(
        b =>
            new { Id = b.BlogId, b.Url });

```

EF Core supports doing client evaluation in the top-level projection. If EF Core materializes an entity instance for client evaluation, it will be tracked. Here, since we're passing blog entities to the client method StandardizeURL, EF Core will track the blog instances too.

```csharp
var blogs = await context.Blogs
    .OrderByDescending(blog => blog.Rating)
    .Select(
        blog => new { Id = blog.BlogId, Url = StandardizeUrl(blog) })
    .ToListAsync();

```

```csharp
public static string StandardizeUrl(Blog blog)
{
    var url = blog.Url.ToLower();

    if (!url.StartsWith("http://"))
    {
        url = string.Concat("http://", url);
    }

    return url;
}

```

EF Core doesn't track the keyless entity instances contained in the result. But EF Core tracks all the other instances of entity types with a key according to rules above.

## Previous versions

Before version 3.0, EF Core had some differences in how tracking was done. Notable differences are as follows:

- As explained in the [Client vs Server Evaluation](https://learn.microsoft.com/en-us/ef/core/querying/client-eval) page, EF Core supported client evaluation in any part of the query before version 3.0. Client evaluation caused materialization of entities, which weren't part of the result. So EF Core analyzed the result to detect what to track. This design had certain differences as follows:
- Client evaluation in the projection, which caused materialization but didn't return the materialized entity instance wasn't tracked. The following example didn't track blog entities.

```csharp
var blogs = await context.Blogs
    .OrderByDescending(blog => blog.Rating)
    .Select(
        blog => new { Id = blog.BlogId, Url = StandardizeUrl(blog) })
    .ToListAsync();

```

- EF Core didn't track the objects coming out of LINQ composition in certain cases. The following example didn't track Post.

```csharp
var blog = context.Blogs
    .Select(
        b =>
            new { Blog = b, Post = b.Posts.OrderBy(p => p.Rating).LastOrDefault() });

```

- Whenever query results contained keyless entity types, the whole query was made non-tracking. That means that entity types with keys, which are in the result weren't being tracked either.
- EF Core used to do identity resolution in no-tracking queries. It used weak references to keep track of entities that had already been returned. So if a result set contained the same entity multiples times, you would get the same instance for each occurrence. Though if a previous result with the same identity went out of scope and got garbage collected, EF Core returned a new instance.