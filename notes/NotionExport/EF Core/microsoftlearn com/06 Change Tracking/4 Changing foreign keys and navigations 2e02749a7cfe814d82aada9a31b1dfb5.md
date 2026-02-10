# 4. Changing foreign keys and navigations

# Changing Foreign Keys and Navigations

## Overview of foreign keys and navigations

Relationships in an Entity Framework Core (EF Core) model are represented using foreign keys (FKs). An FK consists of one or more properties on the dependent or child entity in the relationship. This dependent/child entity is associated with a given principal/parent entity when the values of the foreign key properties on the dependent/child match the values of the alternate or primary key (PK) properties on the principal/parent.

Foreign keys are a good way to store and manipulate relationships in the database, but are not very friendly when working with multiple related entities in application code. Therefore, most EF Core models also layer "navigations" over the FK representation. Navigations form C#/.NET references between entity instances that reflect the associations found by matching foreign key values to primary or alternate key values.

Navigations can be used on both sides of the relationship, on one side only, or not at all, leaving only the FK property. The FK property can be hidden by making it a [shadow property](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties). See [Relationships](https://learn.microsoft.com/en-us/ef/core/modeling/relationships) for more information on modelling relationships.

<aside>
💡 **TIP:** This document assumes that entity states and the basics of EF Core change tracking are understood. See [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for more information on these topics.

</aside>

<aside>
💡 **TIP:** You can run and debug into all the code in this document by [downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/ChangeTracking/ChangingFKsAndNavigations) .

</aside>

### Example model

The following model contains four entity types with relationships between them. The comments in the code indicate which properties are foreign keys, primary keys, and navigations.

```csharp
public class Blog
{
    public int Id { get; set; } // Primary key
    public string Name { get; set; }

    public IList<Post> Posts { get; } = new List<Post>(); // Collection navigation
    public BlogAssets Assets { get; set; } // Reference navigation
}

public class BlogAssets
{
    public int Id { get; set; } // Primary key
    public byte[] Banner { get; set; }

    public int? BlogId { get; set; } // Foreign key
    public Blog Blog { get; set; } // Reference navigation
}

public class Post
{
    public int Id { get; set; } // Primary key
    public string Title { get; set; }
    public string Content { get; set; }

    public int? BlogId { get; set; } // Foreign key
    public Blog Blog { get; set; } // Reference navigation

    public IList<Tag> Tags { get; } = new List<Tag>(); // Skip collection navigation
}

public class Tag
{
    public int Id { get; set; } // Primary key
    public string Text { get; set; }

    public IList<Post> Posts { get; } = new List<Post>(); // Skip collection navigation
}

```

The three relationships in this model are:

- Each blog can have many posts (one-to-many):
- Blog is the principal/parent.
- Post is the dependent/child. It contains the FK property Post.BlogId, the value of which must match the Blog.Id PK value of the related blog.
- Post.Blog is a reference navigation from a post to the associated blog. Post.Blog is the inverse navigation for Blog.Posts.
- Blog.Posts is a collection navigation from a blog to all the associated posts. Blog.Posts is the inverse navigation for Post.Blog.
- Each blog can have one assets (one-to-one):
- Blog is the principal/parent.
- BlogAssets is the dependent/child. It contains the FK property BlogAssets.BlogId, the value of which must match the Blog.Id PK value of the related blog.
- BlogAssets.Blog is a reference navigation from the assets to the associated blog. BlogAssets.Blog is the inverse navigation for Blog.Assets.
- Blog.Assets is a reference navigation from the blog to the associated assets. Blog.Assets is the inverse navigation for BlogAssets.Blog.
- Each post can have many tags and each tag can have many posts (many-to-many):
- Many-to-many relationships are a further layer over two one-to-many relationships. Many-to-many relationships are covered later in this document.
- Post.Tags is a collection navigation from a post to all the associated tags. Post.Tags is the inverse navigation for Tag.Posts.
- Tag.Posts is a collection navigation from a tag to all the associated posts. Tag.Posts is the inverse navigation for Post.Tags.

See [Relationships](https://learn.microsoft.com/en-us/ef/core/modeling/relationships) for more information on how to model and configure relationships.

## Relationship fixup

EF Core keeps navigations in alignment with foreign key values and vice versa. That is, if a foreign key value changes such that it now refers to a different principal/parent entity, then the navigations are updated to reflect this change. Likewise, if a navigation is changed, then the foreign key values of the entities involved are updated to reflect this change. This is called "relationship fixup".

### Fixup by query

Fixup first occurs when entities are queried from the database. The database has only foreign key values, so when EF Core creates an entity instance from the database it uses the foreign key values to set reference navigations and add entities to collection navigations as appropriate. For example, consider a query for blogs and its associated posts and assets:

```csharp
using var context = new BlogsContext();

var blogs = await context.Blogs
    .Include(e => e.Posts)
    .Include(e => e.Assets)
    .ToListAsync();

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

For each blog, EF Core will first create a Blog instance. Then, as each post is loaded from the database its Post.Blog reference navigation is set to point to the associated blog. Likewise, the post is added to the Blog.Posts collection navigation. The same thing happens with BlogAssets, except in this case both navigations are references. The Blog.Assets navigation is set to point to the assets instance, and the BlogAsserts.Blog navigation is set to point to the blog instance.

Looking at the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) after this query shows two blogs, each with one assets and two posts being tracked:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: {Id: 1}
  Posts: [{Id: 1}, {Id: 2}]
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Assets: {Id: 2}
  Posts: [{Id: 3}, {Id: 4}]
BlogAssets {Id: 1} Unchanged
  Id: 1 PK
  Banner: <null>
  BlogId: 1 FK
  Blog: {Id: 1}
BlogAssets {Id: 2} Unchanged
  Id: 2 PK
  Banner: <null>
  BlogId: 2 FK
  Blog: {Id: 2}
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
  Tags: []
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}
  Tags: []
Post {Id: 3} Unchanged
  Id: 3 PK
  BlogId: 2 FK
  Content: 'If you are focused on squeezing out the last bits of perform...'
  Title: 'Disassembly improvements for optimized managed debugging'
  Blog: {Id: 2}
  Tags: []
Post {Id: 4} Unchanged
  Id: 4 PK
  BlogId: 2 FK
  Content: 'Examine when database queries were executed and measure how ...'
  Title: 'Database Profiling with Visual Studio'
  Blog: {Id: 2}
  Tags: []

```

The debug view shows both key values and navigations. Navigations are shown using the primary key values of the related entities. For example, Posts: [{Id: 1}, {Id: 2}] in the output above indicates that the Blog.Posts collection navigation contains two related posts with primary keys 1 and 2 respectively. Similarly, for each post associated with the first blog, the Blog: {Id: 1} line indicates that the Post.Blog navigation references the Blog with primary key 1.

### Fixup to locally tracked entities

Relationship fixup also happens between entities returned from a tracking query and entities already tracked by the DbContext. For example, consider executing three separate queries for blogs, posts, and assets:

```csharp
using var context = new BlogsContext();

var blogs = await context.Blogs.ToListAsync();
Console.WriteLine(context.ChangeTracker.DebugView.LongView);

var assets = await context.Assets.ToListAsync();
Console.WriteLine(context.ChangeTracker.DebugView.LongView);

var posts = await context.Posts.ToListAsync();
Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

Looking again at the debug views, after the first query only the two blogs are tracked:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: <null>
  Posts: []
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Assets: <null>
  Posts: []

```

The Blog.Assets reference navigations are null, and the Blog.Posts collection navigations are empty because no associated entities are currently being tracked by the context.

After the second query, the Blogs.Assets reference navigations have been fixed up to point to the newly tracked BlogAsset instances. Likewise, the BlogAssets.Blog reference navigations are set to point to the appropriate already tracked Blog instance.

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: {Id: 1}
  Posts: []
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Assets: {Id: 2}
  Posts: []
BlogAssets {Id: 1} Unchanged
  Id: 1 PK
  Banner: <null>
  BlogId: 1 FK
  Blog: {Id: 1}
BlogAssets {Id: 2} Unchanged
  Id: 2 PK
  Banner: <null>
  BlogId: 2 FK
  Blog: {Id: 2}

```

Finally, after the third query, the Blog.Posts collection navigations now contain all related posts, and the Post.Blog references point to the appropriate Blog instance:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: {Id: 1}
  Posts: [{Id: 1}, {Id: 2}]
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Assets: {Id: 2}
  Posts: [{Id: 3}, {Id: 4}]
BlogAssets {Id: 1} Unchanged
  Id: 1 PK
  Banner: <null>
  BlogId: 1 FK
  Blog: {Id: 1}
BlogAssets {Id: 2} Unchanged
  Id: 2 PK
  Banner: <null>
  BlogId: 2 FK
  Blog: {Id: 2}
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
  Tags: []
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}
  Tags: []
Post {Id: 3} Unchanged
  Id: 3 PK
  BlogId: 2 FK
  Content: 'If you are focused on squeezing out the last bits of perform...'
  Title: 'Disassembly improvements for optimized managed debugging'
  Blog: {Id: 2}
  Tags: []
Post {Id: 4} Unchanged
  Id: 4 PK
  BlogId: 2 FK
  Content: 'Examine when database queries were executed and measure how ...'
  Title: 'Database Profiling with Visual Studio'
  Blog: {Id: 2}
  Tags: []

```

This is the same end-state as was achieved with the original single query, since EF Core fixed up navigations as entities were tracked, even when coming from multiple different queries.

<aside>
ℹ️ **NOTE:** Fixup never causes more data to be returned from the database. It only connects entities that are already returned by the query or already tracked by the DbContext. See [Identity Resolution in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/identity-resolution) for information about handling duplicates when serializing entities.

</aside>

## Changing relationships using navigations

The easiest way to change the relationship between two entities is by manipulating a navigation, while leaving EF Core to fixup the inverse navigation and FK values appropriately. This can be done by:

- Adding or removing an entity from a collection navigation.
- Changing a reference navigation to point to a different entity, or setting it to null.

### Adding or removing from collection navigations

For example, let's move one of the posts from the Visual Studio blog to the .NET blog. This requires first loading the blogs and posts, and then moving the post from the navigation collection on one blog to the navigation collection on the other blog:

```csharp
using var context = new BlogsContext();

var dotNetBlog = await context.Blogs.Include(e => e.Posts).SingleAsync(e => e.Name == ".NET Blog");
var vsBlog = await context.Blogs.Include(e => e.Posts).SingleAsync(e => e.Name == "Visual Studio Blog");

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

var post = vsBlog.Posts.Single(e => e.Title.StartsWith("Disassembly improvements"));
vsBlog.Posts.Remove(post);
dotNetBlog.Posts.Add(post);

context.ChangeTracker.DetectChanges();
Console.WriteLine(context.ChangeTracker.DebugView.LongView);

await context.SaveChangesAsync();

```

<aside>
💡 **TIP:** A call to [ChangeTracker.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges) is needed here because accessing the debug view does not cause [automatic detection of changes](https://learn.microsoft.com/en-us/ef/core/change-tracking/change-detection) .

</aside>

This is the debug view printed after running the code above:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: <null>
  Posts: [{Id: 1}, {Id: 2}, {Id: 3}]
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Assets: <null>
  Posts: [{Id: 4}]
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
  Tags: []
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}
  Tags: []
Post {Id: 3} Modified
  Id: 3 PK
  BlogId: 1 FK Modified Originally 2
  Content: 'If you are focused on squeezing out the last bits of perform...'
  Title: 'Disassembly improvements for optimized managed debugging'
  Blog: {Id: 1}
  Tags: []
Post {Id: 4} Unchanged
  Id: 4 PK
  BlogId: 2 FK
  Content: 'Examine when database queries were executed and measure how ...'
  Title: 'Database Profiling with Visual Studio'
  Blog: {Id: 2}
  Tags: []

```

The Blog.Posts navigation on the .NET Blog now has three posts (Posts: [{Id: 1}, {Id: 2}, {Id: 3}]). Likewise, the Blog.Posts navigation on the Visual Studio blog only has one post (Posts: [{Id: 4}]). This is to be expected since the code explicitly changed these collections.

More interestingly, even though the code did not explicitly change the Post.Blog navigation, it has been fixed-up to point to the Visual Studio blog (Blog: {Id: 1}). Also, the Post.BlogId foreign key value has been updated to match the primary key value of the .NET blog. This change to the FK value is then persisted to the database when SaveChanges is called:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p1='3' (DbType = String), @p0='1' (Nullable = true) (DbType = String)], CommandType='Text', CommandTimeout='30']
UPDATE "Posts" SET "BlogId" = @p0
WHERE "Id" = @p1;
SELECT changes();

```

### Changing reference navigations

In the previous example, a post was moved from one blog to another by manipulating the collection navigation of posts on each blog. The same thing can be achieved by instead changing the Post.Blog reference navigation to point to the new blog. For example:

```csharp
var post = vsBlog.Posts.Single(e => e.Title.StartsWith("Disassembly improvements"));
post.Blog = dotNetBlog;

```

The debug view after this change is exactly the same as it was in the previous example. This is because EF Core detected the reference navigation change and then fixed up the collection navigations and FK value to match.

## Changing relationships using foreign key values

In the previous section, relationships were manipulated by navigations leaving foreign key values to be updated automatically. This is the recommended way to manipulate relationships in EF Core. However, it is also possible to manipulate FK values directly. For example, we can move a post from one blog to another by changing the Post.BlogId foreign key value:

```csharp
var post = vsBlog.Posts.Single(e => e.Title.StartsWith("Disassembly improvements"));
post.BlogId = dotNetBlog.Id;

```

Notice how this is very similar to changing the reference navigation, as shown in the previous example.

The debug view after this change is again exactly the same as was the case for the previous two examples. This is because EF Core detected the FK value change and then fixed up both the reference and collection navigations to match.

<aside>
💡 **TIP:** Do not write code to manipulate all navigations and FK values each time a relationship changes. Such code is more complicated and must ensure consistent changes to foreign keys and navigations in every case. If possible, just manipulate a single navigation, or maybe both navigations. If needed, just manipulate FK values. Avoid manipulating both navigations and FK values.

</aside>

## Fixup for added or deleted entities

### Adding to a collection navigation

EF Core performs the following actions when it [detects](https://learn.microsoft.com/en-us/ef/core/change-tracking/change-detection) that a new dependent/child entity has been added to a collection navigation:

- If the entity is not tracked, then it is tracked. (The entity will usually be in the Added state. However, if the entity type is configured to use generated keys and the primary key value is set, then the entity is tracked in the Unchanged state.)
- If the entity is associated with a different principal/parent, then that relationship is severed.
- The entity becomes associated with the principal/parent that owns the collection navigation.
- Navigations and foreign key values are fixed up for all entities involved.

Based on this we can see that to move a post from one blog to another we don't actually need to remove it from the old collection navigation before adding it to the new one. So the code from the example above can be changed from:

```csharp
var post = vsBlog.Posts.Single(e => e.Title.StartsWith("Disassembly improvements"));
vsBlog.Posts.Remove(post);
dotNetBlog.Posts.Add(post);

```

To:

```csharp
var post = vsBlog.Posts.Single(e => e.Title.StartsWith("Disassembly improvements"));
dotNetBlog.Posts.Add(post);

```

EF Core sees that the post has been added to a new blog and automatically removes it from the collection on the first blog.

### Removing from a collection navigation

Removing a dependent/child entity from the collection navigation of the principal/parent causes severing of the relationship to that principal/parent. What happens next depends on whether the relationship is optional or required.

### Optional relationships

By default for optional relationships, the foreign key value is set to null. This means that the dependent/child is no longer associated with any principal/parent. For example, let's load a blog and posts and then remove one of the posts from the Blog.Posts collection navigation:

```csharp
var post = dotNetBlog.Posts.Single(e => e.Title == "Announcing F# 5");
dotNetBlog.Posts.Remove(post);

```

Looking at the [change tracking debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) after this change shows that:

- The Post.BlogId FK has been set to null (BlogId:  FK Modified Originally 1)
- The Post.Blog reference navigation has been set to null (Blog: )
- The post has been removed from Blog.Posts collection navigation (Posts: [{Id: 1}])

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Assets: <null>
  Posts: [{Id: 1}]
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
  Tags: []
Post {Id: 2} Modified
  Id: 2 PK
  BlogId: <null> FK Modified Originally 1
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: <null>
  Tags: []

```

Notice that the post is not marked as Deleted. It is marked as Modified so that the FK value in the database will be set to null when SaveChanges is called.

### Required relationships

Setting the FK value to null is not allowed (and is usually not possible) for required relationships. Therefore, severing a required relationship means that the dependent/child entity must be either re-parented to a new principal/parent, or removed from the database when SaveChanges is called to avoid a referential constraint violation. This is known as "deleting orphans", and is the default behavior in EF Core for required relationships.

For example, let's change the relationship between blog and posts to be required and then run the same code as in the previous example:

```csharp
var post = dotNetBlog.Posts.Single(e => e.Title == "Announcing F# 5");
dotNetBlog.Posts.Remove(post);

```

Looking at the debug view after this change shows that:

- The post has been marked as Deleted such that it will be deleted from the database when SaveChanges is called.
- The Post.Blog reference navigation has been set to null (Blog: ).