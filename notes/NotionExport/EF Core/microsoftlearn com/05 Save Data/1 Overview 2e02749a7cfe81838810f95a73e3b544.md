# 1. Overview

# Saving Data

While querying allows you to read data from the database, saving data means adding new entities to the database, removing entities, or modifying the properties of existing entities in some way. Entity Framework Core (EF Core) supports two fundamental approaches for saving data to the database.

## Approach 1: change tracking and SaveChanges

In many scenarios, your program needs to query some data from the database, perform some modification on it, and save those modifications back; this is sometimes referred to as a "unit of work". For example, let's assume that you have a set of Blogs, and you'd like to change the Url property of one of them. In EF, this is typically done as follows:

```csharp
using (var context = new BloggingContext())
{
    var blog = await context.Blogs.SingleAsync(b => b.Url == "http://example.com");
    blog.Url = "http://example.com/blog";
    await context.SaveChangesAsync();
}

```

The code above performs the following steps:

- It uses a regular LINQ query to load an entity from the database (see [Query data](https://learn.microsoft.com/en-us/ef/core/querying/)). EF's queries are tracking by default, meaning that EF tracks the loaded entities in its internal change tracker.
- The loaded entity instance is manipulated as usual, by assigning a .NET property. EF isn't involved in this step.
- Finally, [DbContext.SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) is called. At this point, EF automatically detects any changes by comparing the entities with a snapshot from the moment they were loaded. Any detected changes are persisted to the database; when using a relational database, this typically involves sending e.g. a SQL UPDATE to update the relevant rows.

Note that the above described a typical update operation for existing data, but similar principles hold for adding and removing entities. You interact with EF's change tracker by calling [DbSet.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.add) and [Remove](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.remove), causing the changes to be tracked. EF then applies all tracked changes to the database when [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) is called (e.g. via SQL INSERT and DELETE when using a relational database).

[SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) offers the following advantages:

- You don't need to write code to track which entities and properties changed - EF does this automatically for you, and only updates those properties in the database, improving performance. Imagine if your loaded entities are bound to a UI component, allowing users to change any property they wish; EF takes away the burden of figuring out which entities and properties were actually changed.
- Saving changes to the database can sometimes be complicated! For example, if you want to add a Blog and some Posts for that blog, you may need to fetch the database-generated key for the inserted Blog before you can insert the Posts (since they need to refer to the Blog). EF does all this for you, taking away the complexity.
- EF can detect concurrency issues, such as when a database row has been modified by someone else between your query and [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges). More details are available in [Concurrency conflicts](https://learn.microsoft.com/en-us/ef/core/saving/concurrency).
- On databases which support it, [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) automatically wraps multiple changes in a transaction, ensuring your data stays consistent if a failure occurs. More details are available in [Transactions](https://learn.microsoft.com/en-us/ef/core/saving/transactions).
- [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) also batches together multiple changes in many cases, significantly reducing the number of database roundtrips and greatly improving performance. More details are available in [Efficient updating](https://learn.microsoft.com/en-us/ef/core/performance/efficient-updating#batching).

For more information and code samples on basic [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) usage, see [Basic SaveChanges](https://learn.microsoft.com/en-us/ef/core/saving/basic). For more information on EF's change tracking, see the [Change tracking overview](https://learn.microsoft.com/en-us/ef/core/change-tracking/).

## Approach 2: ExecuteUpdate and ExecuteDelete ("bulk update")

While change tracking and [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) are a powerful way to save changes, they do have certain disadvantages.

First, [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) requires that you query and track all the entities you will be modifying or deleting. If you need to, say, delete all Blogs with a rating below a certain threshold, you must query, materialize and track a potentially huge number of rows, and have [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) generate a DELETE statement for each and every one of them. Relational databases provide a far more efficient alternative: a single DELETE command can be sent, specifying which rows to delete via a WHERE clause, but the [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) model doesn't allow for generating that.

To support this "bulk update" scenario, you can use [ExecuteDelete](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalqueryableextensions.executedelete) as follows:

```csharp
context.Blogs.Where(b => b.Rating < 3).ExecuteDelete();

```

This allows you to express a SQL DELETE statement via regular LINQ operators - similar to a regular LINQ query - causing the following SQL to be executed against the database:

```sql
DELETE FROM [b]
FROM [Blogs] AS [b]
WHERE [b].[Rating] < 3

```

This executes very efficiently in the database, without loading any data from the database or involving EF's change tracker. Similarly, [ExecuteUpdate](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalqueryableextensions.executeupdate) allows you to express a SQL UPDATE statement.

Even if you aren't changing entities in bulk, you may know exactly which properties of which entity you want to change. Using the change tracking API to perform the change can be overly complex, requiring creating an entity instance, tracking it via [Attach](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.attach), making your changes and finally calling [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges). For such scenarios, ExecuteUpdate and ExecuteDelete can be a considerably simpler way to express the same operation.

Finally, both change tracking and [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges) itself impose a certain runtime overhead. If you're writing a high performance application, ExecuteUpdate and ExecuteDelete allow you to avoid both these components and efficiently generate the statement you want.

However, note that ExecuteUpdate and ExecuteDelete also have certain limitations:

- These methods execute immediately, and currently cannot be batched with other operations. On the other hand, [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges), can batch multiple operations together.
- Since change tracking isn't involved, it's your responsibility to know exactly which entities and properties need to be changed. This may mean more manual, low-level code tracking what needs to change and what doesn't.
- In addition, since change tracking isn't involved, these methods do not automatically apply [Concurrency Control](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) when persisting changes. However, you can still explicitly add a Where clause to implement concurrency control yourself.
- Only updating and deleting is currently supported; insertion must be done via [DbSet.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.add) and [SaveChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges#microsoft-entityframeworkcore-dbcontext-savechanges).

For more information and code samples, see [ExecuteUpdateandExecuteDelete](https://learn.microsoft.com/en-us/ef/core/saving/execute-insert-update-delete).

## Summary

Following are a few guidelines for when to use which approach. Note that these aren't absolute rules, but provide a useful rules of thumb:

- If you don't know in advance which changes will take place, use SaveChanges; it will automatically detect which changes need to be applied. Example scenarios:
- "I want to load a Blog from the database and display a form allowing the user to change it"
- If you need to manipulate a graph of objects (i.e. multiple interconnected objects), use SaveChanges; it will figure out the proper ordering of the changes and how to link everything together.
- "I want to update a blog, changing some of its posts and deleting others"
- If you wish to change a potentially large number of entities based on some criterion, use ExecuteUpdate and ExecuteDelete. Example scenarios:
- "I want to give all employees a raise"
- "I want to delete all blogs whose name starts with X"
- If you already know exactly which entities you wish to modify and how you wish to change them, use ExecuteUpdate and ExecuteDelete. Example scenarios:
- "I want to delete the blog whose name is 'Foo'"
- "I want to change the name of the blog with Id 5 to 'Bar'"