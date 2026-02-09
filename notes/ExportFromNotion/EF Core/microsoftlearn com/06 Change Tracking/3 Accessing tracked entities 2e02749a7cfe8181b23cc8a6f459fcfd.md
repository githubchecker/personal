# 3. Accessing tracked entities

# Accessing Tracked Entities

There are four main APIs for accessing entities tracked by a [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext):

- [DbContext.Entry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.entry) returns an [EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1) instance for a given entity instance.
- [ChangeTracker.Entries](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.changetracker.entries) returns [EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1) instances for all tracked entities, or for all tracked entities of a given type.
- [DbContext.Find](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.find), [DbContext.FindAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.findasync), [DbSet.Find](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.find), and [DbSet.FindAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.findasync) find a single entity by primary key, first looking in tracked entities, and then querying the database if needed.
- [DbSet.Local](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.local#microsoft-entityframeworkcore-dbset-1-local) returns actual entities (not EntityEntry instances) for entities of the entity type represented by the DbSet.

Each of these is described in more detail in the sections below.

<aside>
💡 **TIP:** This document assumes that entity states and the basics of EF Core change tracking are understood. See [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for more information on these topics.

</aside>

<aside>
💡 **TIP:** You can run and debug into all the code in this document by [downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/ChangeTracking/AccessingTrackedEntities) .

</aside>

## Using DbContext.Entry and EntityEntry instances

For each tracked entity, Entity Framework Core (EF Core) keeps track of:

- The overall state of the entity. This is one of Unchanged, Modified, Added, or Deleted; see [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for more information.
- The relationships between tracked entities. For example, the blog to which a post belongs.
- The "current values" of properties.
- The "original values" of properties, when this information is available. Original values are the property values that existed when entity was queried from the database.
- Which property values have been modified since they were queried.
- Other information about property values, such as whether or not the value is [temporary](https://learn.microsoft.com/en-us/ef/core/change-tracking/miscellaneous#temporary-values).

Passing an entity instance to [DbContext.Entry](https://learn.microsoft.com/en-us/dotnet/api/system.data.entity.dbcontext.entry) results in an [EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1) providing access to this information for the given entity. For example:

```csharp
using var context = new BlogsContext();

var blog = await context.Blogs.SingleAsync(e => e.Id == 1);
var entityEntry = context.Entry(blog);

```

The following sections show how to use an EntityEntry to access and manipulate entity state, as well as the state of the entity's properties and navigations.

### Working with the entity

The most common use of [EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1) is to access the current [EntityState](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entitystate) of an entity. For example:

```csharp
var currentState = context.Entry(blog).State;
if (currentState == EntityState.Unchanged)
{
    context.Entry(blog).State = EntityState.Modified;
}

```

The Entry method can also be used on entities that are not yet tracked. This does not start tracking the entity; the state of the entity is still Detached. However, the returned EntityEntry can then be used to change the entity state, at which point the entity will become tracked in the given state. For example, the following code will start tracking a Blog instance as Added:

```csharp
var newBlog = new Blog();
Debug.Assert(context.Entry(newBlog).State == EntityState.Detached);

context.Entry(newBlog).State = EntityState.Added;
Debug.Assert(context.Entry(newBlog).State == EntityState.Added);

```

<aside>
💡 **TIP:** Unlike in EF6, setting the state of an individual entity will not cause all connected entities to be tracked. This makes setting the state this way a lower-level operation than calling Add , Attach , or Update , which operate on an entire graph of entities.

</aside>

The following table summarizes ways to use an EntityEntry to work with an entire entity:

| EntityEntry member | Description |
| --- | --- |
| [EntityEntry.State](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.state#microsoft-entityframeworkcore-changetracking-entityentry-state) | Gets and sets the[EntityState](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entitystate)of the entity. |
| [EntityEntry.Entity](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.entity#microsoft-entityframeworkcore-changetracking-entityentry-entity) | Gets the entity instance. |
| [EntityEntry.Context](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.context#microsoft-entityframeworkcore-changetracking-entityentry-context) | The[DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext)that is tracking this entity. |
| [EntityEntry.Metadata](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.metadata#microsoft-entityframeworkcore-changetracking-entityentry-metadata) | [IEntityType](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.ientitytype)metadata for the type of entity. |
| [EntityEntry.IsKeySet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.iskeyset#microsoft-entityframeworkcore-changetracking-entityentry-iskeyset) | Whether or not the entity has had its key value set. |
| [EntityEntry.Reload()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.reload#microsoft-entityframeworkcore-changetracking-entityentry-reload) | Overwrites property values with values read from the database. |
| [EntityEntry.DetectChanges()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.detectchanges#microsoft-entityframeworkcore-changetracking-entityentry-detectchanges) | Forces detection of changes for this entity only; see[Change Detection and Notifications](https://learn.microsoft.com/en-us/ef/core/change-tracking/change-detection). |

### Working with a single property

Several overloads of [EntityEntry.Property](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1.property) allow access to information about an individual property of an entity. For example, using a strongly-typed, fluent-like API:

```csharp
PropertyEntry<Blog, string> propertyEntry = context.Entry(blog).Property(e => e.Name);

```

The property name can instead be passed as a string. For example:

```csharp
PropertyEntry<Blog, string> propertyEntry = context.Entry(blog).Property<string>("Name");

```

The returned [PropertyEntry<TEntity,TProperty>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry-2) can then be used to access information about the property. For example, it can be used to get and set the current value of the property on this entity:

```csharp
string currentValue = context.Entry(blog).Property(e => e.Name).CurrentValue;
context.Entry(blog).Property(e => e.Name).CurrentValue = "1unicorn2";

```

Both of the Property methods used above return a strongly-typed generic [PropertyEntry<TEntity,TProperty>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry-2) instance. Using this generic type is preferred because it allows access to property values without [boxing value types](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/types/boxing-and-unboxing). However, if the type of entity or property is not known at compile-time, then a non-generic [PropertyEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry) can be obtained instead:

```csharp
PropertyEntry propertyEntry = context.Entry(blog).Property("Name");

```

This allows access to property information for any property regardless of its type, at the expense of boxing value types. For example:

```csharp
object blog = await context.Blogs.SingleAsync(e => e.Id == 1);

object currentValue = context.Entry(blog).Property("Name").CurrentValue;
context.Entry(blog).Property("Name").CurrentValue = "1unicorn2";

```

The following table summarizes property information exposed by PropertyEntry:

| PropertyEntry member | Description |
| --- | --- |
| [PropertyEntry<TEntity,TProperty>.CurrentValue](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry-2.currentvalue#microsoft-entityframeworkcore-changetracking-propertyentry-2-currentvalue) | Gets and sets the current value of the property. |
| [PropertyEntry<TEntity,TProperty>.OriginalValue](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry-2.originalvalue#microsoft-entityframeworkcore-changetracking-propertyentry-2-originalvalue) | Gets and sets the original value of the property, if available. |
| [PropertyEntry<TEntity,TProperty>.EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry-2.entityentry#microsoft-entityframeworkcore-changetracking-propertyentry-2-entityentry) | A back reference to the[EntityEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1)for the entity. |
| [PropertyEntry.Metadata](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.metadata#microsoft-entityframeworkcore-changetracking-propertyentry-metadata) | [IProperty](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.iproperty)metadata for the property. |
| [PropertyEntry.IsModified](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.ismodified#microsoft-entityframeworkcore-changetracking-propertyentry-ismodified) | Indicates whether this property is marked as modified, and allows this state to be changed. |
| [PropertyEntry.IsTemporary](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.istemporary#microsoft-entityframeworkcore-changetracking-propertyentry-istemporary) | Indicates whether this property is marked as[temporary](https://learn.microsoft.com/en-us/ef/core/change-tracking/miscellaneous#temporary-values#temporary-values), and allows this state to be changed. |

Notes:

- The original value of a property is the value that the property had when the entity was queried from the database. However, original values are not available if the entity was disconnected and then explicitly attached to another DbContext, for example with Attach or Update. In this case, the original value returned will be the same as the current value.
- [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) will only update properties marked as modified. Set [IsModified](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.ismodified#microsoft-entityframeworkcore-changetracking-propertyentry-ismodified) to true to force EF Core to update a given property value, or set it to false to prevent EF Core from updating the property value.
- [Temporary values](https://learn.microsoft.com/en-us/ef/core/change-tracking/miscellaneous) are typically generated by EF Core [value generators](https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties). Setting the current value of a property will replace the temporary value with the given value and mark the property as not temporary. Set [IsTemporary](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.istemporary#microsoft-entityframeworkcore-changetracking-propertyentry-istemporary) to true to force a value to be temporary even after it has been explicitly set.

### Working with a single navigation

Several overloads of [EntityEntry.Reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1.reference), [EntityEntry.Collection](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1.collection), and [EntityEntry.Navigation](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.navigation) allow access to information about an individual navigation.

Reference navigations to a single related entity are accessed through the [Reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1.reference) methods. Reference navigations point to the "one" sides of one-to-many relationships, and both sides of one-to-one relationships. For example:

```csharp
ReferenceEntry<Post, Blog> referenceEntry1 = context.Entry(post).Reference(e => e.Blog);
ReferenceEntry<Post, Blog> referenceEntry2 = context.Entry(post).Reference<Blog>("Blog");
ReferenceEntry referenceEntry3 = context.Entry(post).Reference("Blog");

```

Navigations can also be collections of related entities when used for the "many" sides of one-to-many and many-to-many relationships. The [Collection](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry-1.collection) methods are used to access collection navigations. For example:

```csharp
CollectionEntry<Blog, Post> collectionEntry1 = context.Entry(blog).Collection(e => e.Posts);
CollectionEntry<Blog, Post> collectionEntry2 = context.Entry(blog).Collection<Post>("Posts");
CollectionEntry collectionEntry3 = context.Entry(blog).Collection("Posts");

```

Some operations are common for all navigations. These can be accessed for both reference and collection navigations using the [EntityEntry.Navigation](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.navigation) method. Note that only non-generic access is available when accessing all navigations together. For example:

```csharp
NavigationEntry navigationEntry = context.Entry(blog).Navigation("Posts");

```

The following table summarizes ways to use [ReferenceEntry<TEntity,TProperty>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.referenceentry-2), [CollectionEntry<TEntity,TRelatedEntity>](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.collectionentry-2), and [NavigationEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry):

| NavigationEntry member | Description |
| --- | --- |
| [MemberEntry.CurrentValue](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.memberentry.currentvalue#microsoft-entityframeworkcore-changetracking-memberentry-currentvalue) | Gets and sets the current value of the navigation. This is the entire collection for collection navigations. |
| [NavigationEntry.Metadata](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry.metadata#microsoft-entityframeworkcore-changetracking-navigationentry-metadata) | [INavigationBase](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.inavigationbase)metadata for the navigation. |
| [NavigationEntry.IsLoaded](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry.isloaded#microsoft-entityframeworkcore-changetracking-navigationentry-isloaded) | Gets or sets a value indicating whether the related entity or collection has been fully loaded from the database. |
| [NavigationEntry.Load()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry.load#microsoft-entityframeworkcore-changetracking-navigationentry-load) | Loads the related entity or collection from the database; see[Explicit Loading of Related Data](https://learn.microsoft.com/en-us/ef/core/querying/related-data/explicit). |
| [NavigationEntry.Query()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry.query#microsoft-entityframeworkcore-changetracking-navigationentry-query) | The query EF Core would use to load this navigation as anIQueryablethat can be further composed; see[Explicit Loading of Related Data](https://learn.microsoft.com/en-us/ef/core/querying/related-data/explicit). |

### Working with all properties of an entity

[EntityEntry.Properties](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.properties#microsoft-entityframeworkcore-changetracking-entityentry-properties) returns an [IEnumerable](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.ienumerable-1) of [PropertyEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry) for every property of the entity. This can be used to perform an action for every property of the entity. For example, to set any DateTime property to DateTime.Now:

```csharp
foreach (var propertyEntry in context.Entry(blog).Properties)
{
    if (propertyEntry.Metadata.ClrType == typeof(DateTime))
    {
        propertyEntry.CurrentValue = DateTime.Now;
    }
}

```

In addition, EntityEntry contains several methods to get and set all property values at the same time. These methods use the [PropertyValues](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyvalues) class, which represents a collection of properties and their values. PropertyValues can be obtained for current or original values, or for the values as currently stored in the database. For example:

```csharp
var currentValues = context.Entry(blog).CurrentValues;
var originalValues = context.Entry(blog).OriginalValues;
var databaseValues = await context.Entry(blog).GetDatabaseValuesAsync();

```

These PropertyValues objects are not very useful on their own. However, they can be combined to perform common operations needed when manipulating entities. This is useful when working with data transfer objects and when resolving [optimistic concurrency conflicts](https://learn.microsoft.com/en-us/ef/core/saving/concurrency). The following sections show some examples.

### Setting current or original values from an entity or DTO

The current or original values of an entity can be updated by copying values from another object. For example, consider a BlogDto data transfer object (DTO) with the same properties as the entity type:

```csharp
public class BlogDto
{
    public int Id { get; set; }
    public string Name { get; set; }
}

```

This can be used to set the current values of a tracked entity using [PropertyValues.SetValues](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyvalues.setvalues):

```csharp
var blogDto = new BlogDto { Id = 1, Name = "1unicorn2" };

context.Entry(blog).CurrentValues.SetValues(blogDto);

```

This technique is sometimes used when updating an entity with values obtained from a service call or a client in an n-tier application. Note that the object used does not have to be of the same type as the entity so long as it has properties whose names match those of the entity. In the example above, an instance of the DTO BlogDto is used to set the current values of a tracked Blog entity.

Note that properties will only be marked as modified if the value set differs from the current value.

### Setting current or original values from a dictionary

The previous example set values from an entity or DTO instance. The same behavior is available when property values are stored as name/value pairs in a dictionary. For example:

```csharp
var blogDictionary = new Dictionary<string, object> { ["Id"] = 1, ["Name"] = "1unicorn2" };

context.Entry(blog).CurrentValues.SetValues(blogDictionary);

```

### Setting current or original values from the database

The current or original values of an entity can be updated with the latest values from the database by calling [GetDatabaseValues()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.getdatabasevalues#microsoft-entityframeworkcore-changetracking-entityentry-getdatabasevalues) or [GetDatabaseValuesAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.getdatabasevaluesasync) and using the returned object to set current or original values, or both. For example:

```csharp
var databaseValues = await context.Entry(blog).GetDatabaseValuesAsync();
context.Entry(blog).CurrentValues.SetValues(databaseValues);
context.Entry(blog).OriginalValues.SetValues(databaseValues);

```

### Creating a cloned object containing current, original, or database values

The PropertyValues object returned from CurrentValues, OriginalValues, or GetDatabaseValues can be used to create a clone of the entity using [PropertyValues.ToObject()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyvalues.toobject#microsoft-entityframeworkcore-changetracking-propertyvalues-toobject). For example:

```csharp
var clonedBlog = (await context.Entry(blog).GetDatabaseValuesAsync()).ToObject();

```

Note that ToObject returns a new instance that is not tracked by the DbContext. The returned object also does not have any relationships set to other entities.

The cloned object can be useful for resolving issues related to concurrent updates to the database, especially when data binding to objects of a certain type. See [optimistic concurrency](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) for more information.

### Working with all navigations of an entity

[EntityEntry.Navigations](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.navigations#microsoft-entityframeworkcore-changetracking-entityentry-navigations) returns an [IEnumerable](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.ienumerable-1) of [NavigationEntry](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.navigationentry) for every navigation of the entity. [EntityEntry.References](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.references#microsoft-entityframeworkcore-changetracking-entityentry-references) and [EntityEntry.Collections](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.collections#microsoft-entityframeworkcore-changetracking-entityentry-collections) do the same thing, but restricted to reference or collection navigations respectively. This can be used to perform an action for every navigation of the entity. For example, to force loading of all related entities:

```csharp
foreach (var navigationEntry in context.Entry(blog).Navigations)
{
    navigationEntry.Load();
}

```

### Working with all members of an entity

Regular properties and navigation properties have different state and behavior. It is therefore common to process navigations and non-navigations separately, as shown in the sections above. However, sometimes it can be useful to do something with any member of the entity, regardless of whether it is a regular property or navigation. [EntityEntry.Member](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.member) and [EntityEntry.Members](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.members#microsoft-entityframeworkcore-changetracking-entityentry-members) are provided for this purpose. For example:

```csharp
foreach (var memberEntry in context.Entry(blog).Members)
{
    Console.WriteLine(
        $"Member {memberEntry.Metadata.Name} is of type {memberEntry.Metadata.ClrType.ShortDisplayName()} and has value {memberEntry.CurrentValue}");
}

```

Running this code on a blog from the sample generates the following output:

```bash
Member Id is of type int and has value 1
Member Name is of type string and has value .NET Blog
Member Posts is of type IList<Post> and has value System.Collections.Generic.List`1[Post]

```

<aside>
💡 **TIP:** The [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) shows information like this. The debug view for the entire change tracker is generated from the individual [EntityEntry.DebugView](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.debugview#microsoft-entityframeworkcore-changetracking-entityentry-debugview) of each tracked entity.

</aside>

## Find and FindAsync

[DbContext.Find](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.find), [DbContext.FindAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.findasync), [DbSet.Find](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.find), and [DbSet.FindAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.findasync) are designed for efficient lookup of a single entity when its primary key is known. Find first checks if the entity is already tracked, and if so returns the entity immediately. A database query is only made if the entity is not tracked locally. For example, consider this code that calls Find twice for the same entity:

```csharp
using var context = new BlogsContext();

Console.WriteLine("First call to Find...");
var blog1 = await context.Blogs.FindAsync(1);

Console.WriteLine($"...found blog {blog1.Name}");

Console.WriteLine();
Console.WriteLine("Second call to Find...");
var blog2 = await context.Blogs.FindAsync(1);
Debug.Assert(blog1 == blog2);

Console.WriteLine("...returned the same instance without executing a query.");

```

The output from this code (including EF Core logging) when using SQLite is:

```bash
First call to Find...
info: 12/29/2020 07:45:53.682 RelationalEventId.CommandExecuted[20101] (Microsoft.EntityFrameworkCore.Database.Command)
      Executed DbCommand (1ms) [Parameters=[@__p_0='1' (DbType = String)], CommandType='Text', CommandTimeout='30']
      SELECT "b"."Id", "b"."Name"
      FROM "Blogs" AS "b"
      WHERE "b"."Id" = @__p_0
      LIMIT 1
...found blog .NET Blog

Second call to Find...
...returned the same instance without executing a query.

```

Notice that the first call does not find the entity locally and so executes a database query. Conversely, the second call returns the same instance without querying the database because it is already being tracked.

Find returns null if an entity with the given key is not tracked locally and does not exist in the database.

### Composite keys

Find can also be used with composite keys. For example, consider an OrderLine entity with a composite key consisting of the order ID and the product ID:

```csharp
public class OrderLine
{
    public int OrderId { get; set; }
    public int ProductId { get; set; }

    //...
}

```

The composite key must be configured in [DbContext.OnModelCreating](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.onmodelcreating) to define the key parts and their order. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .Entity<OrderLine>()
        .HasKey(e => new { e.OrderId, e.ProductId });
}

```