# 11. Global query filters

# Global Query Filters

Global query filters allow attaching a filter to an entity type and having that filter applied whenever a query on that entity type is executed; think of them as an additional LINQ Where operator that's added whenever the entity type is queried. Such filters are useful in a variety of cases.

<aside>
💡 **TIP:** You can view this article's [sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Querying/QueryFilters) on GitHub.

</aside>

## Basic example - soft deletion

In some scenarios, rather than deleting a row from the database, it's preferable to instead set an IsDeleted flag to mark the row as deleted; this pattern is called soft deletion. Soft deletion allows rows to be undeleted if needed, or to preserve an audit trail where deleted rows are still accessible. Global query filters can be used to filter out soft-deleted rows by default, while still allowing you to access them in specific places by disabling the filter for a specific query.

To enable soft deletion, let's add an IsDeleted property to our Blog type:

```csharp
public class Blog
{
    public int Id { get; set; }
    public bool IsDeleted { get; set; }

    public string Name { get; set; }
}

```

We now set up a global query filter, using the [HasQueryFilter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.entitytypebuilder-1.hasqueryfilter) API in OnModelCreating:

```csharp
modelBuilder.Entity<Blog>().HasQueryFilter(b => !b.IsDeleted);

```

We can now query our Blog entities as usual; the configured filter will ensure that all queries will - by default - filter out all instances where IsDeleted is true.

Note that at this point, you must manually set IsDeleted in order to soft-delete an entity. For a more end-to-end solution, you can override your context type's SaveChangesAsync method to add logic which goes over all entities which the user deleted, and changes them to be modified instead, setting the IsDeleted property to true:

```csharp
public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
{
    ChangeTracker.DetectChanges();

    foreach (var item in ChangeTracker.Entries<Blog>().Where(e => e.State == EntityState.Deleted))
    {
        item.State = EntityState.Modified;
        item.CurrentValues["IsDeleted"] = true;
    }

    return await base.SaveChangesAsync(cancellationToken);
}

```

This allows you to use EF APIs that delete an entity instance as usual and have them get soft-deleted instead.

## Using context data - multi-tenancy

Another mainstream scenario for global query filters is multi-tenancy, where your application stores data belonging to different users in the same table. In such cases, there's usually a tenant ID column which associates the row to a specific tenant, and global query filters can be used to automatically filter for the rows of the current tenant. This provides strong tenant isolation for your queries by default, removing the need to think of filtering for the tenant in each and every query.

Unlike with soft deletion, multi-tenancy requires knowing the current tenant ID; this value is usually determined e.g. when the user authenticates over the web. For EF's purposes, the tenant ID must be available on the context instance, so that the global query filter can refer to it and use it when querying. Let's accept a tenantId parameter in our context type's constructor, and reference that from our filter:

```csharp
public class MultitenancyContext(string tenantId) : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Blog>().HasQueryFilter(b => b.TenantId == tenantId);
    }
}

```

This forces anyone constructing a context to specify its associated tenant ID, and ensures that only Blog entities with that ID are returned from queries by default.

<aside>
ℹ️ **NOTE:** This sample only showed basic multi-tenancy concepts needed in order to demonstrate global query filters. For more information on multi-tenancy and EF, see [multi-tenancy in EF Core applications](https://learn.microsoft.com/en-us/ef/core/miscellaneous/multitenancy) .

</aside>

## Using multiple query filters

Calling [HasQueryFilter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.entitytypebuilder-1.hasqueryfilter) with a simple filter overwrites any previous filter, so multiple filters cannot be defined on the same entity type in this way:

```csharp
modelBuilder.Entity<Blog>().HasQueryFilter(b => !b.IsDeleted);
// The following overwrites the previous query filter:
modelBuilder.Entity<Blog>().HasQueryFilter(b => b.TenantId == tenantId);

```

### EF 10+

<aside>
ℹ️ **NOTE:** This feature is being introduced in EF Core 10.0 (in preview).

</aside>

In order to define multiple query filters on the same entity type, they must be named:

```csharp
modelBuilder.Entity<Blog>()
    .HasQueryFilter("SoftDeletionFilter", b => !b.IsDeleted)
    .HasQueryFilter("TenantFilter", b => b.TenantId == tenantId);

```

This allows you to manage each filter separately, including selectively disabling one but not the other.

### Older versions

Prior to EF 10, you can attach multiple filters to an entity type by calling [HasQueryFilter](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.entitytypebuilder-1.hasqueryfilter) once and combining your filters using the && operator:

```csharp
modelBuilder.Entity<Blog>().HasQueryFilter(b => !b.IsDeleted && b.TenantId == tenantId);

```

This unfortunately does not allow to selectively disable a single filter.

## Disabling filters

Filters may be disabled for individual LINQ queries by using the [IgnoreQueryFilters](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.ignorequeryfilters) operator:

```csharp
var allBlogs = await context.Blogs.IgnoreQueryFilters().ToListAsync();

```

If multiple named filters are configured, this disables all of them. To selectively disable specific filters (starting with EF 10), pass the list of filter names to be disabled:

```csharp
var allBlogs = await context.Blogs.IgnoreQueryFilters(["SoftDeletionFilter"]).ToListAsync();

```

## Query filters and required navigations

<aside>
🛑 **CAUTION:** Using required navigation to access entity which has global query filter defined may lead to unexpected results.

</aside>

Required navigations in EF imply that the related entity is always present. Since inner joins may be used to fetch related entities, if a required related entity is filtered out by the query filter, the parent entity may get filtered out as well. This can result in unexpectedly retrieving fewer elements than expected.

To illustrate the problem, we can use Blog and Post entities and configure them as follows:

```csharp
modelBuilder.Entity<Blog>().HasMany(b => b.Posts).WithOne(p => p.Blog).IsRequired();
modelBuilder.Entity<Blog>().HasQueryFilter(b => b.Url.Contains("fish"));

```

The model can be seeded with the following data:

```csharp
db.Blogs.Add(
    new Blog
    {
        Url = "http://sample.com/blogs/fish",
        Posts =
        [
            new() { Title = "Fish care 101" },
            new() { Title = "Caring for tropical fish" },
            new() { Title = "Types of ornamental fish" }
        ]
    });

db.Blogs.Add(
    new Blog
    {
        Url = "http://sample.com/blogs/cats",
        Posts =
        [
            new() { Title = "Cat care 101" },
            new() { Title = "Caring for tropical cats" },
            new() { Title = "Types of ornamental cats" }
        ]
    });

```

The problem can be observed when executing the following two queries:

```csharp
var allPosts = await db.Posts.ToListAsync();
var allPostsWithBlogsIncluded = await db.Posts.Include(p => p.Blog).ToListAsync();

```

With the above setup, the first query returns all 6 Post instances, but the second query returns only 3. This mismatch occurs because the Include method in the second query loads the related Blog entities. Since the navigation between Blog and Post is required, EF Core uses INNER JOIN when constructing the query:

```sql
SELECT [p].[PostId], [p].[BlogId], [p].[Content], [p].[IsDeleted], [p].[Title], [t].[BlogId], [t].[Name], [t].[Url]
FROM [Posts] AS [p]
INNER JOIN (
    SELECT [b].[BlogId], [b].[Name], [b].[Url]
    FROM [Blogs] AS [b]
    WHERE [b].[Url] LIKE N'%fish%'
) AS [t] ON [p].[BlogId] = [t].[BlogId]

```

Use of the INNER JOIN filters out all Post rows whose related Blog rows have been filtered out by a query filter. This problem can be addressed by configuring the navigation as optional navigation instead of required, causing EF to generate a LEFT JOIN instead of an INNER JOIN:

```csharp
modelBuilder.Entity<Blog>().HasMany(b => b.Posts).WithOne(p => p.Blog).IsRequired(false);
modelBuilder.Entity<Blog>().HasQueryFilter(b => b.Url.Contains("fish"));

```

An alternative approach is to specify consistent filters on both Blog and Post entity types; once matching filters are applied to both Blog and Post, Post rows that could end up in unexpected state are removed and both queries return 3 results.

```csharp
modelBuilder.Entity<Blog>().HasMany(b => b.Posts).WithOne(p => p.Blog).IsRequired();
modelBuilder.Entity<Blog>().HasQueryFilter(b => b.Url.Contains("fish"));
modelBuilder.Entity<Post>().HasQueryFilter(p => p.Blog.Url.Contains("fish"));

```

## Query filters and IEntityTypeConfiguration

If your query filter needs to access a tenant ID or similar contextual information, [IEntityTypeConfiguration](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.ientitytypeconfiguration-1) can pose an additional complication as unlike with OnModelCreating, there's no instance of your context type readily available to reference from the query filter. As a workaround, add a dummy context to your configuration type and reference that as follows:

```csharp
private sealed class CustomerEntityConfiguration : IEntityTypeConfiguration<Customer>
{
    private readonly SomeDbContext _context = null!;

    public void Configure(EntityTypeBuilder<Customer> builder)
    {
        builder.HasQueryFilter(d => d.TenantId == _context.TenantId);
    }
}

```

## Limitations

Global query filters have the following limitations:

- Filters can only be defined for the root entity type of an inheritance hierarchy.
- Currently EF Core does not detect cycles in global query filter definitions, so you should be careful when defining them. If specified incorrectly, cycles could lead to infinite loops during query translation.