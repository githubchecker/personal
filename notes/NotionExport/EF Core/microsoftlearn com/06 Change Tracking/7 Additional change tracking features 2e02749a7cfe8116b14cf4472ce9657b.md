# 7. Additional change tracking features

# Additional Change Tracking Features

This document covers miscellaneous features and scenarios involving change tracking.

<aside>
💡 **TIP:** This document assumes that entity states and the basics of EF Core change tracking are understood. See [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for more information on these topics.

</aside>

<aside>
💡 **TIP:** You can run and debug into all the code in this document by [downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/ChangeTracking/AdditionalChangeTrackingFeatures) .

</aside>

## AddversusAddAsync

Entity Framework Core (EF Core) provides async methods whenever using that method may result in a database interaction. Synchronous methods are also provided to avoid overhead when using databases that do not support high performance asynchronous access.

[DbContext.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.add) and [DbSet.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.add) do not normally access the database, since these methods inherently just start tracking entities. However, some forms of value generation may access the database in order to generate a key value. The only value generator that does this and ships with EF Core is [HiLoValueGenerator](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.valuegeneration.hilovaluegenerator-1). Using this generator is uncommon; it is never configured by default. This means that the vast majority of applications should use Add, and not AddAsync.

Other similar methods like Update, Attach, and Remove do not have async overloads because they never generate new key values, and hence never need to access the database.

## AddRange,UpdateRange,AttachRange, andRemoveRange

[DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1) and [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext) provide alternate versions of Add, Update, Attach, and Remove that accept multiple instances in a single call. These methods are [AddRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.addrange), [UpdateRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.updaterange), [AttachRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.attachrange), and [RemoveRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1.removerange) respectively.

These methods are provided as a convenience. Using a "range" method has the same functionality as multiple calls to the equivalent non-range method. There is no significant performance difference between the two approaches.

<aside>
ℹ️ **NOTE:** This is different from EF6, where AddRange and Add both automatically called DetectChanges , but calling Add multiple times caused DetectChanges to be called multiple times instead of once. This made AddRange more efficient in EF6. In EF Core, neither of these methods automatically call DetectChanges .

</aside>

## DbContext versus DbSet methods

Many methods, including Add, Update, Attach, and Remove, have implementations on both [DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1) and [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext). These methods have exactly the same behavior for normal entity types. This is because the CLR type of the entity is mapped onto one and only one entity type in the EF Core model. Therefore, the CLR type fully defines where the entity fits in the model, and so the DbSet to use can be determined implicitly.

The exception to this rule is when using shared-type entity types, which are primarily used for many-to-many join entities. When using a shared-type entity type, a DbSet must first be created for the EF Core model type that is being used. Methods like Add, Update, Attach, and Remove can then be used on the DbSet without any ambiguity as to which EF Core model type is being used.

Shared-type entity types are used by default for the join entities in many-to-many relationships. A shared-type entity type can also be explicitly configured for use in a many-to-many relationship. For example, the code below configures Dictionary<string, int> as a join entity type:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder
        .SharedTypeEntity<Dictionary<string, int>>(
            "PostTag",
            b =>
            {
                b.IndexerProperty<int>("TagId");
                b.IndexerProperty<int>("PostId");
            });

    modelBuilder.Entity<Post>()
        .HasMany(p => p.Tags)
        .WithMany(p => p.Posts)
        .UsingEntity<Dictionary<string, int>>(
            "PostTag",
            j => j.HasOne<Tag>().WithMany(),
            j => j.HasOne<Post>().WithMany());
}

```

[Changing Foreign Keys and Navigations](https://learn.microsoft.com/en-us/ef/core/change-tracking/relationship-changes) shows how to associate two entities by tracking a new join entity instance. The code below does this for the Dictionary<string, int> shared-type entity type used for the join entity:

```csharp
using var context = new BlogsContext();

var post = await context.Posts.SingleAsync(e => e.Id == 3);
var tag = await context.Tags.SingleAsync(e => e.Id == 1);

var joinEntitySet = context.Set<Dictionary<string, int>>("PostTag");
var joinEntity = new Dictionary<string, int> { ["PostId"] = post.Id, ["TagId"] = tag.Id };
joinEntitySet.Add(joinEntity);

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

await context.SaveChangesAsync();

```

Notice that [DbContext.Set(String)](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.set#microsoft-entityframeworkcore-dbcontext-set-1(system-string)) is used to create a DbSet for the PostTag entity type. This DbSet can then be used to call Add with the new join entity instance.

<aside>
🔥 **IMPORTANT:** The CLR type used for join entity types by convention may change in future releases to improve performance. Do not depend on any specific join entity type unless it has been explicitly configured as is done for Dictionary<string, int> in the code above.

</aside>

## Property versus field access

Access to entity properties uses the backing field of the property by default. This is efficient and avoids triggering side effects from calling property getters and setters. For example, this is how lazy-loading is able to avoid triggering infinite loops. See [Backing Fields](https://learn.microsoft.com/en-us/ef/core/modeling/backing-field) for more information on configuring backing fields in the model.

Sometimes it may be desirable for EF Core to generate side-effects when it modifies property values. For example, when data binding to entities, setting a property may generate notifications to the U.I. which do not happen when setting the field directly. This can be achieved by changing the [PropertyAccessMode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.propertyaccessmode) for:

- All entity types in the model using [ModelBuilder.UsePropertyAccessMode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.modelbuilder.usepropertyaccessmode)
- All properties and navigations of a specific entity type using [EntityTypeBuilder.UsePropertyAccessMode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.entitytypebuilder-1.usepropertyaccessmode)
- A specific property using [PropertyBuilder.UsePropertyAccessMode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.propertybuilder.usepropertyaccessmode)
- A specific navigation using [NavigationBuilder.UsePropertyAccessMode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.navigationbuilder.usepropertyaccessmode)

Property access modes Field and PreferField will cause EF Core to access the property value through its backing field. Likewise, Property and PreferProperty will cause EF Core to access the property value through its getter and setter.

If Field or Property are used and EF Core cannot access the value through the field or property getter/setter respectively, then EF Core will throw an exception. This ensures EF Core is always using field/property access when you think it is.

On the other hand, the PreferField and PreferProperty modes will fall back to using the property or backing field respectively if it is not possible to use the preferred access. PreferField is the default. This means EF Core will use fields whenever it can, but will not fail if a property must be accessed through its getter or setter instead.

FieldDuringConstruction and PreferFieldDuringConstruction configure EF Core to use of backing fields only when creating entity instances. This allows queries to be executed without getter and setter side effects, while later property changes by EF Core will cause these side effects.

The different property access modes are summarized in the following table:

| PropertyAccessMode | Preference | Preference creating entities | Fallback | Fallback creating entities |
| --- | --- | --- | --- | --- |
| Field | Field | Field | Throws | Throws |
| Property | Property | Property | Throws | Throws |
| PreferField | Field | Field | Property | Property |
| PreferProperty | Property | Property | Field | Field |
| FieldDuringConstruction | Property | Field | Field | Throws |
| PreferFieldDuringConstruction | Property | Field | Field | Property |

## Temporary values

EF Core creates temporary key values when tracking new entities that will have real key values generated by the database when SaveChanges is called. See [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for an overview of how these temporary values are used.

### Accessing temporary values

Temporary values are stored in the change tracker and not set onto entity instances directly. However, these temporary values are exposed when using the various mechanisms for [Accessing Tracked Entities](https://learn.microsoft.com/en-us/ef/core/change-tracking/entity-entries). For example, the following code accesses a temporary value using [EntityEntry.CurrentValues](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.entityentry.currentvalues):

```csharp
using var context = new BlogsContext();

var blog = new Blog { Name = ".NET Blog" };

context.Add(blog);

Console.WriteLine($"Blog.Id set on entity is {blog.Id}");
Console.WriteLine($"Blog.Id tracked by EF is {context.Entry(blog).Property(e => e.Id).CurrentValue}");

```

The output from this code is:

```bash
Blog.Id set on entity is 0
Blog.Id tracked by EF is -2147482643

```

[PropertyEntry.IsTemporary](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.istemporary) can be used to check for temporary values.

### Manipulating temporary values

It is sometimes useful to explicitly work with temporary values. For example, a collection of new entities might be created on a web client and then serialized back to the server. Foreign key values are one way to set up relationships between these entities. The following code uses this approach to associate a graph of new entities by foreign key, while still allowing real key values to be generated when SaveChanges is called.

```csharp
var blogs = new List<Blog> { new Blog { Id = -1, Name = ".NET Blog" }, new Blog { Id = -2, Name = "Visual Studio Blog" } };

var posts = new List<Post>
{
    new Post
    {
        Id = -1,
        BlogId = -1,
        Title = "Announcing the Release of EF Core 5.0",
        Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
    },
    new Post
    {
        Id = -2,
        BlogId = -2,
        Title = "Disassembly improvements for optimized managed debugging",
        Content = "If you are focused on squeezing out the last bits of performance for your .NET service or..."
    }
};

using var context = new BlogsContext();

foreach (var blog in blogs)
{
    context.Add(blog).Property(e => e.Id).IsTemporary = true;
}

foreach (var post in posts)
{
    context.Add(post).Property(e => e.Id).IsTemporary = true;
}

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

await context.SaveChangesAsync();

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

Notice that:

- Negative numbers are used as temporary key values; this is not required, but is a common convention to prevent key clashes.
- The Post.BlogId FK property is assigned the same negative value as the PK of the associated blog.
- The PK values are marked as temporary by setting [IsTemporary](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.changetracking.propertyentry.istemporary) after each entity is tracked. This is necessary because any key value supplied by the application is assumed to be a real key value.

Looking at the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) before calling SaveChanges shows that the PK values are marked as temporary and posts are associated with the correct blogs, including fixup of navigations:

```bash
Blog {Id: -2} Added
  Id: -2 PK Temporary
  Name: 'Visual Studio Blog'
  Posts: [{Id: -2}]
Blog {Id: -1} Added
  Id: -1 PK Temporary
  Name: '.NET Blog'
  Posts: [{Id: -1}]
Post {Id: -2} Added
  Id: -2 PK Temporary
  BlogId: -2 FK
  Content: 'If you are focused on squeezing out the last bits of perform...'
  Title: 'Disassembly improvements for optimized managed debugging'
  Blog: {Id: -2}
  Tags: []
Post {Id: -1} Added
  Id: -1 PK Temporary
  BlogId: -1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: -1}

```

After calling [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges), these temporary values have been replaced by real values generated by the database:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}]
Blog {Id: 2} Unchanged
  Id: 2 PK
  Name: 'Visual Studio Blog'
  Posts: [{Id: 2}]
Post {Id: 1} Unchanged
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
  Tags: []
Post {Id: 2} Unchanged
  Id: 2 PK
  BlogId: 2 FK
  Content: 'If you are focused on squeezing out the last bits of perform...'
  Title: 'Disassembly improvements for optimized managed debugging'
  Blog: {Id: 2}
  Tags: []

```

## Working with default values

EF Core allows a property to get its default value from the database when [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) is called. Like with generated key values, EF Core will only use a default from the database if no value has been explicitly set. For example, consider the following entity type:

```csharp
public class Token
{
    public int Id { get; set; }
    public string Name { get; set; }
    public DateTime ValidFrom { get; set; }
}

```

The ValidFrom property is configured to get a default value from the database:

```csharp
modelBuilder
    .Entity<Token>()
    .Property(e => e.ValidFrom)
    .HasDefaultValueSql("CURRENT_TIMESTAMP");

```

When inserting an entity of this type, EF Core will let the database generate the value unless an explicit value has been set instead. For example:

```csharp
using var context = new BlogsContext();

context.AddRange(
    new Token { Name = "A" },
    new Token { Name = "B", ValidFrom = new DateTime(1111, 11, 11, 11, 11, 11) });

await context.SaveChangesAsync();

Console.WriteLine(context.ChangeTracker.DebugView.LongView);

```

Looking at the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) shows that the first token had ValidFrom generated by the database, while the second token used the value explicitly set:

```bash
Token {Id: 1} Unchanged
  Id: 1 PK
  Name: 'A'
  ValidFrom: '12/30/2020 6:36:06 PM'
Token {Id: 2} Unchanged
  Id: 2 PK
  Name: 'B'
  ValidFrom: '11/11/1111 11:11:11 AM'

```

<aside>
ℹ️ **NOTE:** Using database default values requires that the database column has a default value constraint configured. This is done automatically by EF Core migrations when using [HasDefaultValueSql](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalpropertybuilderextensions.hasdefaultvaluesql) or [HasDefaultValue](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalpropertybuilderextensions.hasdefaultvalue) . Make sure to create the default constraint on the column in some other way when not using EF Core migrations.

</aside>

### Using nullable properties

EF Core is able to determine whether or not a property has been set by comparing the property value to the CLR default for the that type. This works well in most cases, but means that the CLR default cannot be explicitly inserted into the database. For example, consider an entity with an integer property:

```csharp
public class Foo1
{
    public int Id { get; set; }
    public int Count { get; set; }
}

```

Where that property is configured to have a database default of -1:

```csharp
modelBuilder
    .Entity<Foo1>()
    .Property(e => e.Count)
    .HasDefaultValue(-1);

```

The intention is that the default of -1 will be used whenever an explicit value is not set. However, setting the value to 0 (the CLR default for integers) is indistinguishable to EF Core from not setting any value, this means that it is not possible to insert 0 for this property. For example:

```csharp
using var context = new BlogsContext();

var fooA = new Foo1 { Count = 10 };
var fooB = new Foo1 { Count = 0 };
var fooC = new Foo1();

context.AddRange(fooA, fooB, fooC);
await context.SaveChangesAsync();

Debug.Assert(fooA.Count == 10);
Debug.Assert(fooB.Count == -1); // Not what we want!
Debug.Assert(fooC.Count == -1);

```

Notice that the instance where Count was explicitly set to 0 is still gets the default value from the database, which is not what we intended. An easy way to deal with this is to make the Count property nullable:

```csharp
public class Foo2
{
    public int Id { get; set; }
    public int? Count { get; set; }
}

```

This makes the CLR default null, instead of 0, which means 0 will now be inserted when explicitly set:

```csharp
using var context = new BlogsContext();

var fooA = new Foo2 { Count = 10 };
var fooB = new Foo2 { Count = 0 };
var fooC = new Foo2();

context.AddRange(fooA, fooB, fooC);
await context.SaveChangesAsync();

Debug.Assert(fooA.Count == 10);
Debug.Assert(fooB.Count == 0);
Debug.Assert(fooC.Count == -1);

```

### Using nullable backing fields

The problem with making the property nullable that it may not be conceptually nullable in the domain model. Forcing the property to be nullable therefore compromises the model.

The property can be left non-nullable, with only the backing field being nullable. For example:

```csharp
public class Foo3
{
    public int Id { get; set; }

    private int? _count;

    public int Count
    {
        get => _count ?? -1;
        set => _count = value;
    }
}

```

This allows the CLR default (0) to be inserted if the property is explicitly set to 0, while not needing to expose the property as nullable in the domain model. For example:

```csharp
using var context = new BlogsContext();

var fooA = new Foo3 { Count = 10 };
var fooB = new Foo3 { Count = 0 };
var fooC = new Foo3();

context.AddRange(fooA, fooB, fooC);
await context.SaveChangesAsync();

Debug.Assert(fooA.Count == 10);
Debug.Assert(fooB.Count == 0);
Debug.Assert(fooC.Count == -1);

```

### Nullable backing fields for bool properties

This pattern is especially useful when using bool properties with store-generated defaults. Since the CLR default for bool is "false", it means that "false" cannot be inserted explicitly using the normal pattern. For example, consider a User entity type:

```csharp
public class User
{
    public int Id { get; set; }
    public string Name { get; set; }

    private bool? _isAuthorized;

    public bool IsAuthorized
    {
        get => _isAuthorized ?? true;
        set => _isAuthorized = value;
    }
}

```

The IsAuthorized property is configured with a database default value of "true":

```csharp
modelBuilder
    .Entity<User>()
    .Property(e => e.IsAuthorized)
    .HasDefaultValue(true);

```

The IsAuthorized property can be set to "true" or "false" explicitly before inserting, or can be left unset in which case the database default will be used:

```csharp
using var context = new BlogsContext();

var userA = new User { Name = "Mac" };
var userB = new User { Name = "Alice", IsAuthorized = true };
var userC = new User { Name = "Baxter", IsAuthorized = false }; // Always deny Baxter access!

context.AddRange(userA, userB, userC);

await context.SaveChangesAsync();

```

The output from SaveChanges when using SQLite shows that the database default is used for Mac, while explicit values are set for Alice and Baxter:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p0='Mac' (Size = 3)], CommandType='Text', CommandTimeout='30']
INSERT INTO "User" ("Name")
VALUES (@p0);
SELECT "Id", "IsAuthorized"
FROM "User"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

-- Executed DbCommand (0ms) [Parameters=[@p0='True' (DbType = String), @p1='Alice' (Size = 5)], CommandType='Text', CommandTimeout='30']
INSERT INTO "User" ("IsAuthorized", "Name")
VALUES (@p0, @p1);
SELECT "Id"
FROM "User"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

-- Executed DbCommand (0ms) [Parameters=[@p0='False' (DbType = String), @p1='Baxter' (Size = 6)], CommandType='Text', CommandTimeout='30']
INSERT INTO "User" ("IsAuthorized", "Name")
VALUES (@p0, @p1);
SELECT "Id"
FROM "User"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

```

### Schema defaults only

Sometimes it is useful to have defaults in the database schema created by EF Core migrations without EF Core ever using these values for inserts. This can be achieved by configuring the property as [PropertyBuilder.ValueGeneratedNever](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.propertybuilder.valuegeneratednever) For example:

```csharp
modelBuilder
    .Entity<Bar>()
    .Property(e => e.Count)
    .HasDefaultValue(-1)
    .ValueGeneratedNever();

```