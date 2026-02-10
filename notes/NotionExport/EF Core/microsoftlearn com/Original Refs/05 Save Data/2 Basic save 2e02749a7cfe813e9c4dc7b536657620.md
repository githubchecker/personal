# 2. Basic save

# Basic SaveChanges

[DbContext.SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) is one of two techniques for saving changes to the database with EF. With this method, you perform one or more tracked changes (add, update, delete), and then apply those changes by calling the SaveChanges method. As an alternative, [ExecuteUpdate](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalqueryableextensions.executeupdate) and [ExecuteDelete](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalqueryableextensions.executedelete) can be used without involving the change tracker. For an introductory comparison of these two techniques, see the [Overview page](https://learn.microsoft.com/en-us/ef/core/saving/) on saving data.

<aside>
💡 **TIP:** You can view this article's [sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Saving/Basics/) on GitHub.

</aside>

## Adding Data

Use the [DbSet.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.add) method to add new instances of your entity classes. The data will be inserted into the database when you call [DbContext.SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges):

```csharp
using (var context = new BloggingContext())
{
    var blog = new Blog { Url = "http://example.com" };
    context.Blogs.Add(blog);
    await context.SaveChangesAsync();
}

```

<aside>
💡 **TIP:** The Add , Attach , and Update methods all work on the full graph of entities passed to them, as described in the [Related Data](https://learn.microsoft.com/en-us/ef/core/saving/related-data) section. Alternately, the EntityEntry.State property can be used to set the state of just a single entity. For example, context.Entry(blog).State = EntityState.Modified .

</aside>

## Updating Data

EF automatically detects changes made to an existing entity that is tracked by the context. This includes entities that you load/query from the database, and entities that were previously added and saved to the database.

Simply modify the values assigned to properties and then call SaveChanges:

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs.SingleAsync(b => b.Url == "http://example.com");
    blog.Url = "http://example.com/blog";
    await context.SaveChangesAsync();
}

```

## Deleting Data

Use the [DbSet.Remove](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.remove) method to delete instances of your entity classes:

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs.SingleAsync(b => b.Url == "http://example.com/blog");
    context.Blogs.Remove(blog);
    await context.SaveChangesAsync();
}

```

If the entity already exists in the database, it will be deleted during SaveChanges. If the entity has not yet been saved to the database (that is, it is tracked as added) then it will be removed from the context and will no longer be inserted when SaveChanges is called.

## Multiple Operations in a single SaveChanges

You can combine multiple Add/Update/Remove operations into a single call to SaveChanges:

```csharp
using (var context = new BloggingContext())
{
    // seeding database
    context.Blogs.Add(new Blog { Url = "http://example.com/blog" });
    context.Blogs.Add(new Blog { Url = "http://example.com/another_blog" });
    await context.SaveChangesAsync();
}

using (var context = new BloggingContext())
{
    // add
    context.Blogs.Add(new Blog { Url = "http://example.com/blog_one" });
    context.Blogs.Add(new Blog { Url = "http://example.com/blog_two" });

    // update
    var firstBlog = await context.Blogs.FirstAsync();
    firstBlog.Url = "";

    // remove
    var lastBlog = await context.Blogs.OrderBy(e => e.BlogId).LastAsync();
    context.Blogs.Remove(lastBlog);

    await context.SaveChangesAsync();
}

```

<aside>
ℹ️ **NOTE:** For most database providers, SaveChanges is transactional. This means all the operations either succeed or fail and the operations are never be left partially applied.

</aside>