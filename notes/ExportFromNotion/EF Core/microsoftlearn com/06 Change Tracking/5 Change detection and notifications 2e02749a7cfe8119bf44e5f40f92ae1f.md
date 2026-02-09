# 5. Change detection and notifications

# Change Detection and Notifications

Each [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext) instance tracks changes made to entities. These tracked entities in turn drive the changes to the database when [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) is called. This is covered in [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/), and this document assumes that entity states and the basics of Entity Framework Core (EF Core) change tracking are understood.

Tracking property and relationship changes requires that the DbContext is able to detect these changes. This document covers how this detection happens, as well as how to use property notifications or change-tracking proxies to force immediate detection of changes.

<aside>
💡 **TIP:** You can run and debug into all the code in this document by [downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/ChangeTracking/ChangeDetectionAndNotifications) .

</aside>

## Snapshot change tracking

By default, EF Core creates a snapshot of every entity's property values when it is first tracked by a DbContext instance. The values stored in this snapshot are then compared against the current values of the entity in order to determine which property values have changed.

This detection of changes happens when SaveChanges is called to ensure all changed values are detected before sending updates to the database. However, the detection of changes also happens at other times to ensure the application is working with up-to-date tracking information. Detection of changes can be forced at any time by calling [ChangeTracker.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges).

### When change detection is needed

Detection of changes is needed when a property or navigation has been changed without using EF Core to make this change. For example, consider loading blogs and posts and then making changes to these entities:

```csharp
using var context = new BlogsContext();
var blog = await context.Blogs.Include(e => e.Posts).FirstAsync(e => e.Name == ".NET Blog");

// Change a property value
blog.Name = ".NET Blog (Updated!)";

// Add a new entity to a navigation
blog.Posts.Add(
    new Post
    {
        Title = "Whatâs next for System.Text.Json?", Content = ".NET 5.0 was released recently and has come with many..."
    });

Console.WriteLine(context.ChangeTracker.DebugView.LongView);
context.ChangeTracker.DetectChanges();
Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

Looking at the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) before calling [ChangeTracker.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges) shows that the changes made have not been detected and hence are not reflected in the entity states and modified property data:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog (Updated!)' Originally '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}, <not found>]
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}

```

Specifically, the state of the blog entry is still Unchanged, and the new post does not appear as a tracked entity. (The astute will notice properties report their new values, even though these changes have not yet been detected by EF Core. This is because the debug view is reading current values directly from the entity instance.)

Contrast this with the debug view after calling DetectChanges:

```bash
Blog {Id: 1} Modified
  Id: 1 PK
  Name: '.NET Blog (Updated!)' Modified Originally '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}, {Id: -2147482643}]
Post {Id: -2147482643} Added
  Id: -2147482643 PK Temporary
  BlogId: 1 FK
  Content: '.NET 5.0 was released recently and has come with many...'
  Title: 'What's next for System.Text.Json?'
  Blog: {Id: 1}
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}

```

Now the blog is correctly marked as Modified and the new post has been detected and is tracked as Added.

At the start of this section we stated that detecting changes is needed when not using EF Core to make the change. This is what is happening in the code above. That is, the changes to the property and navigation are made directly on the entity instances, and not by using any EF Core methods.

Contrast this to the following code which modifies the entities in the same way, but this time using EF Core methods:

```csharp
using var context = new BlogsContext();
var blog = await context.Blogs.Include(e => e.Posts).FirstAsync(e => e.Name == ".NET Blog");

// Change a property value
context.Entry(blog).Property(e => e.Name).CurrentValue = ".NET Blog (Updated!)";

// Add a new entity to the DbContext
context.Add(
    new Post
    {
        Blog = blog,
        Title = "Whatâs next for System.Text.Json?",
        Content = ".NET 5.0 was released recently and has come with many..."
    });

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

In this case the change tracker debug view shows that all entity states and property modifications are known, even though detection of changes has not happened. This is because [PropertyEntry.CurrentValue](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.currentvalue#microsoft-entityframeworkcore-changetracking-propertyentry-currentvalue) is an EF Core method, which means that EF Core immediately knows about the change made by this method. Likewise, calling [DbContext.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.add) allows EF Core to immediately know about the new entity and track it appropriately.

<aside>
💡 **TIP:** Don't attempt to avoid detecting changes by always using EF Core methods to make entity changes. Doing so is often more cumbersome and performs less well than making changes to entities in the normal way. The intention of this document is to inform as to when detecting changes is needed and when it is not. The intention is not to encourage avoidance of change detection.

</aside>

### Methods that automatically detect changes

[DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges) is called automatically by methods where doing so is likely to impact the results. These methods are:

- [DbContext.SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) and [DbContext.SaveChangesAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechangesasync), to ensure that all changes are detected before updating the database.
- [ChangeTracker.Entries()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.entries#microsoft-entityframeworkcore-changetracking-changetracker-entries) and [ChangeTracker.Entries()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.entries#microsoft-entityframeworkcore-changetracking-changetracker-entries-1), to ensure entity states and modified properties are up-to-date.
- [ChangeTracker.HasChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.haschanges#microsoft-entityframeworkcore-changetracking-changetracker-haschanges), to ensure that the result is accurate.
- [ChangeTracker.CascadeChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.cascadechanges#microsoft-entityframeworkcore-changetracking-changetracker-cascadechanges), to ensure correct entity states for principal/parent entities before cascading.
- [DbSet.Local](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.local#microsoft-entityframeworkcore-dbset-1-local), to ensure that the tracked graph is up-to-date.

There are also some places where detection of changes happens on only a single entity instance, rather than on the entire graph of tracked entities. These places are:

- When using [DbContext.Entry](https://learn.microsoft.com/en-us/dotnet/api/system.data.entity.dbcontext.entry), to ensure that the entity's state and modified properties are up-to-date.
- When using [EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry) methods such as Property, Collection, Reference or Member to ensure property modifications, current values, etc. are up-to-date.
- When a dependent/child entity is going to be deleted because a required relationship has been severed. This detects when an entity should not be deleted because it has been re-parented.

Local detection of changes for a single entity can be triggered explicitly by calling [EntityEntry.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.detectchanges#microsoft-entityframeworkcore-changetracking-entityentry-detectchanges).

<aside>
ℹ️ **NOTE:** Local detect changes can miss some changes that a full detection would find. This happens when cascading actions resulting from undetected changes to other entities have an impact on the entity in question. In such situations the application may need to force a full scan of all entities by explicitly calling [ChangeTracker.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges) .

</aside>

### Disabling automatic change detection

The performance of detecting changes is not a bottleneck for most applications. However, detecting changes can become a performance problem for some applications that track thousands of entities. (The exact number will dependent on many things, such as the number of properties in the entity.) For this reason the automatic detection of changes can be disabled using [ChangeTracker.AutoDetectChangesEnabled](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.autodetectchangesenabled#microsoft-entityframeworkcore-changetracking-changetracker-autodetectchangesenabled). For example, consider processing join entities in a many-to-many relationship with payloads:

```csharp
public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
{
    foreach (var entityEntry in ChangeTracker.Entries<PostTag>()) // Detects changes automatically
    {
        if (entityEntry.State == EntityState.Added)
        {
            entityEntry.Entity.TaggedBy = "ajcvickers";
            entityEntry.Entity.TaggedOn = DateTime.Now;
        }
    }

    try
    {
        ChangeTracker.AutoDetectChangesEnabled = false;
        return await base.SaveChangesAsync(cancellationToken); // Avoid automatically detecting changes again here
    }
    finally
    {
        ChangeTracker.AutoDetectChangesEnabled = true;
    }
}

```

As we know from the previous section, both [ChangeTracker.Entries()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.entries#microsoft-entityframeworkcore-changetracking-changetracker-entries-1) and [DbContext.SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) automatically detect changes. However, after calling Entries, the code does not then make any entity or property state changes. (Setting normal property values on Added entities does not cause any state changes.) The code therefore disables unnecessary automatic change detection when calling down into the base SaveChanges method. The code also makes use of a try/finally block to ensure that the default setting is restored even if SaveChanges fails.

<aside>
💡 **TIP:** Do not assume that your code must disable automatic change detection to perform well. This is only needed when profiling an application tracking many entities indicates that performance of change detection is an issue.

</aside>

### Detecting changes and value conversions

To use snapshot change tracking with an entity type, EF Core must be able to:

- Make a snapshot of each property value when the entity is tracked
- Compare this value to the current value of the property
- Generate a hash code for the value

This is handled automatically by EF Core for types that can be directly mapped to the database. However, when a [value converter is used to map a property](https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions), then that converter must specify how to perform these actions. This is achieved with a value comparer, and is described in detail in the [Value Comparers](https://learn.microsoft.com/en-us/ef/core/modeling/value-comparers) documentation.

## Notification entities

Snapshot change tracking is recommended for most applications. However, applications that track many entities and/or make many changes to those entities may benefit from implementing entities that automatically notify EF Core when their property and navigation values change. These are known as "notification entities".

### Implementing notification entities

Notification entities make use of the [INotifyPropertyChanging](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.inotifypropertychanging) and [INotifyPropertyChanged](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.inotifypropertychanged) interfaces, which are part of the .NET base class library (BCL). These interfaces define events that must be fired before and after changing a property value. For example:

```csharp
public class Blog : INotifyPropertyChanging, INotifyPropertyChanged
{
    public event PropertyChangingEventHandler PropertyChanging;
    public event PropertyChangedEventHandler PropertyChanged;

    private int _id;

    public int Id
    {
        get => _id;
        set
        {
            PropertyChanging?.Invoke(this, new PropertyChangingEventArgs(nameof(Id)));
            _id = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Id)));
        }
    }

    private string _name;

    public string Name
    {
        get => _name;
        set
        {
            PropertyChanging?.Invoke(this, new PropertyChangingEventArgs(nameof(Name)));
            _name = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Name)));
        }
    }

    public IList<Post> Posts { get; } = new ObservableCollection<Post>();
}

```

In addition, any collection navigations must implement INotifyCollectionChanged; in the example above this is satisfied by using an [ObservableCollection](https://learn.microsoft.com/en-us/dotnet/api/system.collections.objectmodel.observablecollection-1) of posts. EF Core also ships with an [ObservableHashSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.observablehashset-1) implementation that has more efficient lookups at the expense of stable ordering.

Most of this notification code is typically moved into an unmapped base class. For example:

```csharp
public class Blog : NotifyingEntity
{
    private int _id;

    public int Id
    {
        get => _id;
        set => SetWithNotify(value, out _id);
    }

    private string _name;

    public string Name
    {
        get => _name;
        set => SetWithNotify(value, out _name);
    }

    public IList<Post> Posts { get; } = new ObservableCollection<Post>();
}

public abstract class NotifyingEntity : INotifyPropertyChanging, INotifyPropertyChanged
{
    protected void SetWithNotify<T>(T value, out T field, [CallerMemberName] string propertyName = "")
    {
        NotifyChanging(propertyName);
        field = value;
        NotifyChanged(propertyName);
    }

    public event PropertyChangingEventHandler PropertyChanging;
    public event PropertyChangedEventHandler PropertyChanged;

    private void NotifyChanged(string propertyName)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));

    private void NotifyChanging(string propertyName)
        => PropertyChanging?.Invoke(this, new PropertyChangingEventArgs(propertyName));
}

```

### Configuring notification entities

There is no way for EF Core to validate that INotifyPropertyChanging or INotifyPropertyChanged are fully implemented for use with EF Core. In particular, some uses of these interfaces do so with notifications only on certain properties, rather than on all properties (including navigations) as required by EF Core. For this reason, EF Core does not automatically hook into these events.

Instead, EF Core must be configured to use these notification entities. This is usually done for all entity types by calling [ModelBuilder.HasChangeTrackingStrategy](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.modelbuilder.haschangetrackingstrategy). For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.HasChangeTrackingStrategy(ChangeTrackingStrategy.ChangingAndChangedNotifications);
}

```

(The strategy can also be set differently for different entity types using [EntityTypeBuilder.HasChangeTrackingStrategy](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.entitytypebuilder.haschangetrackingstrategy), but this is usually counterproductive since DetectChanges is still required for those types that are not notification entities.)

Full notification change tracking requires that both INotifyPropertyChanging and INotifyPropertyChanged are implemented. This allows original values to be saved just before the property value is changed, avoiding the need for EF Core to create a snapshot when tracking the entity. Entity types that implement only INotifyPropertyChanged can also be used with EF Core. In this case, EF still creates a snapshot when tracking an entity to keep track of original values, but then uses the notifications to detect changes immediately, rather than needing DetectChanges to be called.

The different [ChangeTrackingStrategy](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetrackingstrategy) values are summarized in the following table.

| ChangeTrackingStrategy | Interfaces needed | Needs DetectChanges | Snapshots original values |
| --- | --- | --- | --- |
| Snapshot | None | Yes | Yes |
| ChangedNotifications | INotifyPropertyChanged | No | Yes |
| ChangingAndChangedNotifications | INotifyPropertyChanged and INotifyPropertyChanging | No | No |
| ChangingAndChangedNotificationsWithOriginalValues | INotifyPropertyChanged and INotifyPropertyChanging | No | Yes |

### Using notification entities

Notification entities behave like any other entities, except that making changes to the entity instances do not require a call to [ChangeTracker.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.detectchanges#microsoft-entityframeworkcore-changetracking-changetracker-detectchanges) to detect these changes. For example:

```csharp
using var context = new BlogsContext();
var blog = await context.Blogs.Include(e => e.Posts).FirstAsync(e => e.Name == ".NET Blog");

// Change a property value
blog.Name = ".NET Blog (Updated!)";

// Add a new entity to a navigation
blog.Posts.Add(
    new Post
    {
        Title = "Whatâs next for System.Text.Json?", Content = ".NET 5.0 was released recently and has come with many..."
    });

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

With normal entities, the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) showed that these changes were not detected until DetectChanges was called. Looking at the debug view when notification entities are used shows that these changes have been detected immediately:

```bash
Blog {Id: 1} Modified
  Id: 1 PK
  Name: '.NET Blog (Updated!)' Modified
  Posts: [{Id: 1}, {Id: 2}, {Id: -2147482643}]
Post {Id: -2147482643} Added
  Id: -2147482643 PK Temporary
  BlogId: 1 FK
  Content: '.NET 5.0 was released recently and has come with many...'
  Title: 'What's next for System.Text.Json?'
  Blog: {Id: 1}
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}

```

## Change-tracking proxies

EF Core can dynamically generate proxy types that implement [INotifyPropertyChanging](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.inotifypropertychanging) and [INotifyPropertyChanged](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.inotifypropertychanged). This requires installing the [Microsoft.EntityFrameworkCore.Proxies](https://www.nuget.org/packages/Microsoft.EntityFrameworkCore.Proxies/) NuGet package, and enabling change-tracking proxies with [UseChangeTrackingProxies](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.proxiesextensions.usechangetrackingproxies) For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.UseChangeTrackingProxies();

```

Creating a dynamic proxy involves creating a new, dynamic .NET type (using the [Castle.Core](https://www.nuget.org/packages/Castle.Core/) proxies implementation), which inherits from the entity type and then overrides all property setters. Entity types for proxies must therefore be types that can be inherited from and must have properties that can be overridden. Also, collection navigations created explicitly must implement [INotifyCollectionChanged](https://learn.microsoft.com/en-us/dotnet/api/system.collections.specialized.inotifycollectionchanged) For example:

```csharp
public class Blog
{
    public virtual int Id { get; set; }
    public virtual string Name { get; set; }

    public virtual IList<Post> Posts { get; } = new ObservableCollection<Post>();
}

public class Post
{
    public virtual int Id { get; set; }
    public virtual string Title { get; set; }
    public virtual string Content { get; set; }

    public virtual int BlogId { get; set; }
    public virtual Blog Blog { get; set; }
}

```

One significant downside to change-tracking proxies is that EF Core must always track instances of the proxy, never instances of the underlying entity type. This is because instances of the underlying entity type will not generate notifications, which means changes made to these entities will be missed.

EF Core creates proxy instances automatically when querying the database, so this downside is generally limited to tracking new entity instances. These instances must be created using the [CreateProxy](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.proxiesextensions.createproxy) extension methods, and not in the normal way using new. This means the code from the previous examples must now make use of CreateProxy:

```csharp
using var context = new BlogsContext();
var blog = await context.Blogs.Include(e => e.Posts).FirstAsync(e => e.Name == ".NET Blog");

// Change a property value
blog.Name = ".NET Blog (Updated!)";

// Add a new entity to a navigation
blog.Posts.Add(
    context.CreateProxy<Post>(
        p =>
        {
            p.Title = "Whatâs next for System.Text.Json?";
            p.Content = ".NET 5.0 was released recently and has come with many...";
        }));

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

## Change tracking events

EF Core fires the [ChangeTracker.Tracked](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.tracked#microsoft-entityframeworkcore-changetracking-changetracker-tracked) event when an entity is tracked for the first time. Future entity state changes result in [ChangeTracker.StateChanged](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.statechanged#microsoft-entityframeworkcore-changetracking-changetracker-statechanged) events. See [.NET Events in EF Core](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/events) for more information.

<aside>
ℹ️ **NOTE:** The StateChanged event is not fired when an entity is first tracked, even though the state has changed from Detached to one of the other states. Make sure to listen for both StateChanged and Tracked events to get all relevant notifications.

</aside>