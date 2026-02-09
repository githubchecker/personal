# 4. Events

# .NET Events in EF Core

<aside>
💡 **TIP:** You can [download the events sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Miscellaneous/Events) from GitHub.

</aside>

Entity Framework Core (EF Core) exposes [.NET events](https://learn.microsoft.com/en-us/dotnet/standard/events/) to act as callbacks when certain things happen in the EF Core code. Events are simpler than [interceptors](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/interceptors) and allow more flexible registration. However, they are sync only and so cannot perform non-blocking async I/O.

Events are registered per DbContext instance. Use a [diagnostic listener](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/diagnostic-listeners) to get the same information but for all DbContext instances in the process.

## Events raised by EF Core

The following events are raised by EF Core:

| Event | When raised |
| --- | --- |
| [DbContext.SavingChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savingchanges#microsoft-entityframeworkcore-dbcontext-savingchanges) | At the start of[SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges)or[SaveChangesAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechangesasync) |
| [DbContext.SavedChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savedchanges#microsoft-entityframeworkcore-dbcontext-savedchanges) | At the end of a successful[SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges)or[SaveChangesAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechangesasync) |
| [DbContext.SaveChangesFailed](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechangesfailed#microsoft-entityframeworkcore-dbcontext-savechangesfailed) | At the end of a failed[SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges)or[SaveChangesAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechangesasync) |
| [ChangeTracker.Tracked](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.tracked#microsoft-entityframeworkcore-changetracking-changetracker-tracked) | When an entity is tracked by the context |
| [ChangeTracker.StateChanged](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.statechanged#microsoft-entityframeworkcore-changetracking-changetracker-statechanged) | When a tracked entity changes its state |

### Example: Timestamp state changes

Each entity tracked by a DbContext has an [EntityState](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entitystate). For example, the Added state indicates that the entity will be inserted into the database.

This example uses the [Tracked](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.tracked#microsoft-entityframeworkcore-changetracking-changetracker-tracked) and [StateChanged](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.statechanged#microsoft-entityframeworkcore-changetracking-changetracker-statechanged) events to detect when an entity changes state. It then stamps the entity with the current time indicating when this change happened. This results in timestamps indicating when the entity was inserted, deleted, and/or last updated.

The entity types in this example implement an interface that defines the timestamp properties:

```csharp
public interface IHasTimestamps
{
    DateTime? Added { get; set; }
    DateTime? Deleted { get; set; }
    DateTime? Modified { get; set; }
}

```

A method on the application's DbContext can then set timestamps for any entity that implements this interface:

```csharp
private static void UpdateTimestamps(object sender, EntityEntryEventArgs e)
{
    if (e.Entry.Entity is IHasTimestamps entityWithTimestamps)
    {
        switch (e.Entry.State)
        {
            case EntityState.Deleted:
                entityWithTimestamps.Deleted = DateTime.UtcNow;
                Console.WriteLine($"Stamped for delete: {e.Entry.Entity}");
                break;
            case EntityState.Modified:
                entityWithTimestamps.Modified = DateTime.UtcNow;
                Console.WriteLine($"Stamped for update: {e.Entry.Entity}");
                break;
            case EntityState.Added:
                entityWithTimestamps.Added = DateTime.UtcNow;
                Console.WriteLine($"Stamped for insert: {e.Entry.Entity}");
                break;
        }
    }
}

```

This method has the appropriate signature to use as an event handler for both the Tracked and StateChanged events. The handler is registered for both events in the DbContext constructor. Note that events can be attached to a DbContext at any time; it is not required that this happen in the context constructor.

```csharp
public BlogsContext()
{
    ChangeTracker.StateChanged += UpdateTimestamps;
    ChangeTracker.Tracked += UpdateTimestamps;
}

```

Both events are needed because new entities fire Tracked events when they are first tracked. StateChanged events are only fired for entities that change state while they are already being tracked.

The [sample](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Miscellaneous/Events) for this example contains a simple console application that makes changes to the blogging database:

```csharp
using (var context = new BlogsContext())
{
    await context.Database.EnsureDeletedAsync();
    await context.Database.EnsureCreatedAsync();

    context.Add(
        new Blog
        {
            Id = 1,
            Name = "EF Blog",
            Posts = { new Post { Id = 1, Title = "EF Core 3.1!" }, new Post { Id = 2, Title = "EF Core 5.0!" } }
        });

    await context.SaveChangesAsync();
}

using (var context = new BlogsContext())
{
    var blog = await context.Blogs.Include(e => e.Posts).SingleAsync();

    blog.Name = "EF Core Blog";
    context.Remove(blog.Posts.First());
    blog.Posts.Add(new Post { Id = 3, Title = "EF Core 6.0!" });

    await context.SaveChangesAsync();
}

```

The output from this code shows the state changes happening and the timestamps being applied:

```bash
Stamped for insert: Blog 1 Added on: 10/15/2020 11:01:26 PM
Stamped for insert: Post 1 Added on: 10/15/2020 11:01:26 PM
Stamped for insert: Post 2 Added on: 10/15/2020 11:01:26 PM
Stamped for delete: Post 1 Added on: 10/15/2020 11:01:26 PM Deleted on: 10/15/2020 11:01:26 PM
Stamped for update: Blog 1 Added on: 10/15/2020 11:01:26 PM Modified on: 10/15/2020 11:01:26 PM
Stamped for insert: Post 3 Added on: 10/15/2020 11:01:26 PM

```