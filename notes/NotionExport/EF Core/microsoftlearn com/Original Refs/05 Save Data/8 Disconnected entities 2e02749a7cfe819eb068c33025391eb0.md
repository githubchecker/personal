# 8. Disconnected entities

# Disconnected entities

A DbContext instance will automatically track entities returned from the database. Changes made to these entities will then be detected when SaveChanges is called and the database will be updated as needed. See [Basic Save](https://learn.microsoft.com/en-us/ef/core/saving/basic) and [Related Data](https://learn.microsoft.com/en-us/ef/core/saving/related-data) for details.

However, sometimes entities are queried using one context instance and then saved using a different instance. This often happens in "disconnected" scenarios such as a web application where the entities are queried, sent to the client, modified, sent back to the server in a request, and then saved. In this case, the second context instance needs to know whether the entities are new (should be inserted) or existing (should be updated).

<aside>
💡 **TIP:** You can view this article's [sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Saving/Disconnected/) on GitHub.

</aside>

<aside>
💡 **TIP:** EF Core can only track one instance of any entity with a given primary key value. The best way to avoid this being an issue is to use a short-lived context for each unit-of-work such that the context starts empty, has entities attached to it, saves those entities, and then the context is disposed and discarded.

</aside>

## Identifying new entities

### Client identifies new entities

The simplest case to deal with is when the client informs the server whether the entity is new or existing. For example, often the request to insert a new entity is different from the request to update an existing entity.

The remainder of this section covers the cases where it is necessary to determine in some other way whether to insert or update.

### With auto-generated keys

The value of an automatically generated key can often be used to determine whether an entity needs to be inserted or updated. If the key has not been set (that is, it still has the CLR default value of null, zero, etc.), then the entity must be new and needs inserting. On the other hand, if the key value has been set, then it must have already been previously saved and now needs updating. In other words, if the key has a value, then the entity was queried, sent to the client, and has now come back to be updated.

It is easy to check for an unset key when the entity type is known:

```csharp
public static bool IsItNew(Blog blog)
    => blog.BlogId == 0;

```

However, EF also has a built-in way to do this for any entity type and key type:

```csharp
public static bool IsItNew(DbContext context, object entity)
    => !context.Entry(entity).IsKeySet;

```

<aside>
💡 **TIP:** Keys are set as soon as entities are tracked by the context, even if the entity is in the Added state. This helps when traversing a graph of entities and deciding what to do with each, such as when using the TrackGraph API. The key value should only be used in the way shown here before any call is made to track the entity.

</aside>

### With other keys

Some other mechanism is needed to identify new entities when key values are not generated automatically. There are two general approaches to this:

- Query for the entity
- Pass a flag from the client

To query for the entity, just use the Find method:

```csharp
public static async Task<bool> IsItNew(BloggingContext context, Blog blog)
    => (await context.Blogs.FindAsync(blog.BlogId)) == null;

```

It is beyond the scope of this document to show the full code for passing a flag from a client. In a web app, it usually means making different requests for different actions, or passing some state in the request then extracting it in the controller.

## Saving single entities

If it is known whether or not an insert or update is needed, then either Add or Update can be used appropriately:

```csharp
public static async Task Insert(DbContext context, object entity)
{
    context.Add(entity);
    await context.SaveChangesAsync();
}

public static async Task Update(DbContext context, object entity)
{
    context.Update(entity);
    await context.SaveChangesAsync();
}

```

However, if the entity uses auto-generated key values, then the Update method can be used for both cases:

```csharp
public static async Task InsertOrUpdate(DbContext context, object entity)
{
    context.Update(entity);
    await context.SaveChangesAsync();
}

```

The Update method normally marks the entity for update, not insert. However, if the entity has an auto-generated key, and no key value has been set, then the entity is instead automatically marked for insert.

If the entity is not using auto-generated keys, then the application must decide whether the entity should be inserted or updated: For example:

```csharp
public static async Task InsertOrUpdate(BloggingContext context, Blog blog)
{
    var existingBlog = await context.Blogs.FindAsync(blog.BlogId);
    if (existingBlog == null)
    {
        context.Add(blog);
    }
    else
    {
        context.Entry(existingBlog).CurrentValues.SetValues(blog);
    }

    await context.SaveChangesAsync();
}

```

The steps here are:

- If Find returns null, then the database doesn't already contain the blog with this ID, so we call Add mark it for insertion.
- If Find returns an entity, then it exists in the database and the context is now tracking the existing entity
- We then use SetValues to set the values for all properties on this entity to those that came from the client.
- The SetValues call will mark the entity to be updated as needed.

<aside>
💡 **TIP:** SetValues will only mark as modified the properties that have different values to those in the tracked entity. This means that when the update is sent, only those columns that have actually changed will be updated. (And if nothing has changed, then no update will be sent at all.)

</aside>

## Working with graphs

### Identity resolution

As noted above, EF Core can only track one instance of any entity with a given primary key value. When working with graphs the graph should ideally be created such that this invariant is maintained, and the context should be used for only one unit-of-work. If the graph does contain duplicates, then it will be necessary to process the graph before sending it to EF to consolidate multiple instances into one. This may not be trivial where instances have conflicting values and relationships, so consolidating duplicates should be done as soon as possible in your application pipeline to avoid conflict resolution.

### All new/all existing entities

An example of working with graphs is inserting or updating a blog together with its collection of associated posts. If all the entities in the graph should be inserted, or all should be updated, then the process is the same as described above for single entities. For example, a graph of blogs and posts created like this:

```csharp
var blog = new Blog
{
    Url = "http://sample.com", Posts = new List<Post> { new Post { Title = "Post 1" }, new Post { Title = "Post 2" }, }
};

```

can be inserted like this:

```csharp
public static async Task InsertGraph(DbContext context, object rootEntity)
{
    context.Add(rootEntity);
    await context.SaveChangesAsync();
}

```

The call to Add will mark the blog and all the posts to be inserted.

Likewise, if all the entities in a graph need to be updated, then Update can be used:

```csharp
public static async Task UpdateGraph(DbContext context, object rootEntity)
{
    context.Update(rootEntity);
    await context.SaveChangesAsync();
}

```

The blog and all its posts will be marked to be updated.

### Mix of new and existing entities

With auto-generated keys, Update can again be used for both inserts and updates, even if the graph contains a mix of entities that require inserting and those that require updating:

```csharp
public static async Task InsertOrUpdateGraph(DbContext context, object rootEntity)
{
    context.Update(rootEntity);
    await context.SaveChangesAsync();
}

```

Update will mark any entity in the graph, blog or post, for insertion if it does not have a key value set, while all other entities are marked for update.

As before, when not using auto-generated keys, a query and some processing can be used:

```csharp
public static async Task InsertOrUpdateGraph(BloggingContext context, Blog blog)
{
    var existingBlog = await context.Blogs
        .Include(b => b.Posts)
        .FirstOrDefaultAsync(b => b.BlogId == blog.BlogId);

    if (existingBlog == null)
    {
        context.Add(blog);
    }
    else
    {
        context.Entry(existingBlog).CurrentValues.SetValues(blog);
        foreach (var post in blog.Posts)
        {
            var existingPost = existingBlog.Posts
                .FirstOrDefault(p => p.PostId == post.PostId);

            if (existingPost == null)
            {
                existingBlog.Posts.Add(post);
            }
            else
            {
                context.Entry(existingPost).CurrentValues.SetValues(post);
            }
        }
    }

    await context.SaveChangesAsync();
}

```

## Handling deletes

Delete can be tricky to handle since often the absence of an entity means that it should be deleted. One way to deal with this is to use "soft deletes" such that the entity is marked as deleted rather than actually being deleted. Deletes then becomes the same as updates. Soft deletes can be implemented using [query filters](https://learn.microsoft.com/en-us/ef/core/querying/filters).

For true deletes, a common pattern is to use an extension of the query pattern to perform what is essentially a graph diff. For example:

```csharp
public static async Task InsertUpdateOrDeleteGraph(BloggingContext context, Blog blog)
{
    var existingBlog = await context.Blogs
        .Include(b => b.Posts)
        .FirstOrDefaultAsync(b => b.BlogId == blog.BlogId);

    if (existingBlog == null)
    {
        context.Add(blog);
    }
    else
    {
        context.Entry(existingBlog).CurrentValues.SetValues(blog);
        foreach (var post in blog.Posts)
        {
            var existingPost = existingBlog.Posts
                .FirstOrDefault(p => p.PostId == post.PostId);

            if (existingPost == null)
            {
                existingBlog.Posts.Add(post);
            }
            else
            {
                context.Entry(existingPost).CurrentValues.SetValues(post);
            }
        }

        foreach (var post in existingBlog.Posts)
        {
            if (!blog.Posts.Any(p => p.PostId == post.PostId))
            {
                context.Remove(post);
            }
        }
    }

    await context.SaveChangesAsync();
}

```

## TrackGraph

Internally, Add, Attach, and Update use graph-traversal with a determination made for each entity as to whether it should be marked as Added (to insert), Modified (to update), Unchanged (do nothing), or Deleted (to delete). This mechanism is exposed via the TrackGraph API. For example, let's assume that when the client sends back a graph of entities it sets some flag on each entity indicating how it should be handled. TrackGraph can then be used to process this flag:

```csharp
public static async Task SaveAnnotatedGraph(DbContext context, object rootEntity)
{
    context.ChangeTracker.TrackGraph(
        rootEntity,
        n =>
        {
            var entity = (EntityBase)n.Entry.Entity;
            n.Entry.State = entity.IsNew
                ? EntityState.Added
                : entity.IsChanged
                    ? EntityState.Modified
                    : entity.IsDeleted
                        ? EntityState.Deleted
                        : EntityState.Unchanged;
        });

    await context.SaveChangesAsync();
}

```

The flags are only shown as part of the entity for simplicity of the example. Typically the flags would be part of a DTO or some other state included in the request.