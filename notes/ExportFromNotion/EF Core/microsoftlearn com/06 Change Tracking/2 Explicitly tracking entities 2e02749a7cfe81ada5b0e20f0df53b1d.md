# 2. Explicitly tracking entities

# Explicitly Tracking Entities

Each [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext) instance tracks changes made to entities. These tracked entities in turn drive the changes to the database when [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) is called.

Entity Framework Core (EF Core) change tracking works best when the same [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext) instance is used to both query for entities and update them by calling [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges). This is because EF Core automatically tracks the state of queried entities and then detects any changes made to these entities when SaveChanges is called. This approach is covered in [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/).

<aside>
💡 **TIP:** This document assumes that entity states and the basics of EF Core change tracking are understood. See [Change Tracking in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/) for more information on these topics.

</aside>

<aside>
💡 **TIP:** You can run and debug into all the code in this document by [downloading the sample code from GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/ChangeTracking/ChangeTrackingInEFCore) .

</aside>

## Introduction

Entities can be explicitly "attached" to a [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext) such that the context then tracks those entities. This is primarily useful when:

- Creating new entities that will be inserted into the database.
- Re-attaching disconnected entities that were previously queried by a different DbContext instance.

The first of these will be needed by most applications, and is primarily handled by the [DbContext.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.add) methods.

The second is only needed by applications that change entities or their relationships while the entities are not being tracked. For example, a web application may send entities to the web client where the user makes changes and sends the entities back. These entities are referred to as "disconnected" since they were originally queried from a DbContext, but were then disconnected from that context when sent to the client.

The web application must now re-attach these entities so that they are again tracked and indicate the changes that have been made such that [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges) can make appropriate updates to the database. This is primarily handled by the [DbContext.Attach](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.attach) and [DbContext.Update](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.update) methods.

<aside>
💡 **TIP:** Attaching entities to the same DbContext instance that they were queried from should not normally be needed. Do not routinely perform a no-tracking query and then attach the returned entities to the same context. This will be slower than using a tracking query, and may also result in issues such as missing shadow property values, making it harder to get right.

</aside>

### Generated versus explicit key values

By default, integer and GUID [key properties](https://learn.microsoft.com/en-us/ef/core/modeling/keys) are configured to use [automatically generated key values](https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties). This has a major advantage for change tracking: an unset key value indicates that the entity is "new". By "new", we mean that it has not yet been inserted into the database.

Two models are used in the following sections. The first is configured to not use generated key values:

```csharp
public class Blog
{
    [DatabaseGenerated(DatabaseGeneratedOption.None)]
    public int Id { get; set; }

    public string Name { get; set; }

    public IList<Post> Posts { get; } = new List<Post>();
}

public class Post
{
    [DatabaseGenerated(DatabaseGeneratedOption.None)]
    public int Id { get; set; }

    public string Title { get; set; }
    public string Content { get; set; }

    public int? BlogId { get; set; }
    public Blog Blog { get; set; }
}

```

Non-generated (i.e. explicitly set) key values are shown first in each example because everything is very explicit and easy to follow. This is then followed by an example where generated key values are used:

```csharp
public class Blog
{
    public int Id { get; set; }
    public string Name { get; set; }

    public IList<Post> Posts { get; } = new List<Post>();
}

public class Post
{
    public int Id { get; set; }
    public string Title { get; set; }
    public string Content { get; set; }

    public int? BlogId { get; set; }
    public Blog Blog { get; set; }
}

```

Notice that the key properties in this model need no additional configuration here since using generated key values is the [default for simple integer keys](https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties).

## Inserting new entities

### Explicit key values

An entity must be tracked in the Added state to be inserted by [SaveChanges](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.savechanges). Entities are typically put in the Added state by calling one of [DbContext.Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.add), [DbContext.AddRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.addrange), [DbContext.AddAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.addasync), [DbContext.AddRangeAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.addrangeasync), or the equivalent methods on [DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1).

<aside>
💡 **TIP:** These methods all work in the same way in the context of change tracking. See [Additional Change Tracking Features](https://learn.microsoft.com/en-us/ef/core/change-tracking/miscellaneous) for more information.

</aside>

For example, to start tracking a new blog:

```csharp
context.Add(
    new Blog { Id = 1, Name = ".NET Blog", });

```

Inspecting the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) following this call shows that the context is tracking the new entity in the Added state:

```bash
Blog {Id: 1} Added
  Id: 1 PK
  Name: '.NET Blog'
  Posts: []

```

However, the Add methods don't just work on an individual entity. They actually start tracking an entire graph of related entities, putting them all to the Added state. For example, to insert a new blog and associated new posts:

```csharp
context.Add(
    new Blog
    {
        Id = 1,
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Id = 1,
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Id = 2,
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            }
        }
    });

```

The context is now tracking all these entities as Added:

```bash
Blog {Id: 1} Added
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}]
Post {Id: 1} Added
  Id: 1 PK
  BlogId: 1 FK
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: 1}
Post {Id: 2} Added
  Id: 2 PK
  BlogId: 1 FK
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: 1}

```

Notice that explicit values have been set for the Id key properties in the examples above. This is because the model here has been configured to use explicitly set key values, rather than automatically generated key values. When not using generated keys, the key properties must be explicitly set before calling Add. These key values are then inserted when SaveChanges is called. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p0='1' (DbType = String), @p1='.NET Blog' (Size = 9)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Blogs" ("Id", "Name")
VALUES (@p0, @p1);

-- Executed DbCommand (0ms) [Parameters=[@p2='1' (DbType = String), @p3='1' (DbType = String), @p4='Announcing the release of EF Core 5.0, a full featured cross-platform...' (Size = 72), @p5='Announcing the Release of EF Core 5.0' (Size = 37)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("Id", "BlogId", "Content", "Title")
VALUES (@p2, @p3, @p4, @p5);

-- Executed DbCommand (0ms) [Parameters=[@p0='2' (DbType = String), @p1='1' (DbType = String), @p2='F# 5 is the latest version of F#, the functional programming language...' (Size = 72), @p3='Announcing F# 5' (Size = 15)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("Id", "BlogId", "Content", "Title")
VALUES (@p0, @p1, @p2, @p3);

```

All of these entities are tracked in the Unchanged state after SaveChanges completes, since these entities now exist in the database:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}]
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

### Generated key values

As mentioned above, integer and GUID [key properties](https://learn.microsoft.com/en-us/ef/core/modeling/keys) are configured to use [automatically generated key values](https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties) by default. This means that the application must not set any key value explicitly. For example, to insert a new blog and posts all with generated key values:

```csharp
context.Add(
    new Blog
    {
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            }
        }
    });

```

As with explicit key values, the context is now tracking all these entities as Added:

```bash
Blog {Id: -2147482644} Added
  Id: -2147482644 PK Temporary
  Name: '.NET Blog'
  Posts: [{Id: -2147482637}, {Id: -2147482636}]
Post {Id: -2147482637} Added
  Id: -2147482637 PK Temporary
  BlogId: -2147482644 FK Temporary
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...'
  Title: 'Announcing the Release of EF Core 5.0'
  Blog: {Id: -2147482644}
Post {Id: -2147482636} Added
  Id: -2147482636 PK Temporary
  BlogId: -2147482644 FK Temporary
  Content: 'F# 5 is the latest version of F#, the functional programming...'
  Title: 'Announcing F# 5'
  Blog: {Id: -2147482644}

```

Notice in this case that [temporary key values](https://learn.microsoft.com/en-us/ef/core/change-tracking/miscellaneous#temporary-values) have been generated for each entity. These values are used by EF Core until SaveChanges is called, at which point real key values are read back from the database. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p0='.NET Blog' (Size = 9)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Blogs" ("Name")
VALUES (@p0);
SELECT "Id"
FROM "Blogs"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

-- Executed DbCommand (0ms) [Parameters=[@p1='1' (DbType = String), @p2='Announcing the release of EF Core 5.0, a full featured cross-platform...' (Size = 72), @p3='Announcing the Release of EF Core 5.0' (Size = 37)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("BlogId", "Content", "Title")
VALUES (@p1, @p2, @p3);
SELECT "Id"
FROM "Posts"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

-- Executed DbCommand (0ms) [Parameters=[@p0='1' (DbType = String), @p1='F# 5 is the latest version of F#, the functional programming language...' (Size = 72), @p2='Announcing F# 5' (Size = 15)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("BlogId", "Content", "Title")
VALUES (@p0, @p1, @p2);
SELECT "Id"
FROM "Posts"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

```

After SaveChanges completes, all of the entities have been updated with their real key values and are tracked in the Unchanged state since they now match the state in the database:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}]
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

This is exactly the same end-state as the previous example that used explicit key values.

<aside>
💡 **TIP:** An explicit key value can still be set even when using generated key values. EF Core will then attempt to insert using this key value. Some database configurations, including SQL Server with Identity columns, do not support such inserts and will throw ( [see these docs for a workaround](https://learn.microsoft.com/en-us/ef/core/providers/sql-server/value-generation#inserting-explicit-values-into-identity-columns) ).

</aside>

## Attaching existing entities

### Explicit key values

Entities returned from queries are tracked in the Unchanged state. The Unchanged state means that the entity has not been modified since it was queried. A disconnected entity, perhaps returned from a web client in an HTTP request, can be put into this state using either [DbContext.Attach](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.attach), [DbContext.AttachRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.attachrange), or the equivalent methods on [DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1). For example, to start tracking an existing blog:

```csharp
context.Attach(
    new Blog { Id = 1, Name = ".NET Blog", });

```

<aside>
ℹ️ **NOTE:** The examples here are creating entities explicitly with new for simplicity. Normally the entity instances will have come from another source, such as being deserialized from a client, or being created from data in an HTTP Post.

</aside>

Inspecting the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) following this call shows that the entity is tracked in the Unchanged state:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: []

```

Just like Add, Attach actually sets an entire graph of connected entities to the Unchanged state. For example, to attach an existing blog and associated existing posts:

```csharp
context.Attach(
    new Blog
    {
        Id = 1,
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Id = 1,
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Id = 2,
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            }
        }
    });

```

The context is now tracking all these entities as Unchanged:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}]
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

Calling SaveChanges at this point will have no effect. All the entities are marked as Unchanged, so there is nothing to update in the database.

### Generated key values

As mentioned above, integer and GUID [key properties](https://learn.microsoft.com/en-us/ef/core/modeling/keys) are configured to use [automatically generated key values](https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties) by default. This has a major advantage when working with disconnected entities: an unset key value indicates that the entity has not yet been inserted into the database. This allows the change tracker to automatically detect new entities and put them in the Added state. For example, consider attaching this graph of a blog and posts:

```csharp
context.Attach(
    new Blog
    {
        Id = 1,
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Id = 1,
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Id = 2,
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            },
            new Post
            {
                Title = "Announcing .NET 5.0",
                Content = ".NET 5.0 includes many enhancements, including single file applications, more..."
            },
        }
    });

```

The blog has a key value of 1, indicating that it already exists in the database. Two of the posts also have key values set, but the third does not. EF Core will see this key value as 0, the CLR default for an integer. This results in EF Core marking the new entity as Added instead of Unchanged:

```bash
Blog {Id: 1} Unchanged
  Id: 1 PK
  Name: '.NET Blog'
  Posts: [{Id: 1}, {Id: 2}, {Id: -2147482636}]
Post {Id: -2147482636} Added
  Id: -2147482636 PK Temporary
  BlogId: 1 FK
  Content: '.NET 5.0 includes many enhancements, including single file a...'
  Title: 'Announcing .NET 5.0'
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

```

Calling SaveChanges at this point does nothing with the Unchanged entities, but inserts the new entity into the database. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p0='1' (DbType = String), @p1='.NET 5.0 includes many enhancements, including single file applications, more...' (Size = 80), @p2='Announcing .NET 5.0' (Size = 19)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("BlogId", "Content", "Title")
VALUES (@p0, @p1, @p2);
SELECT "Id"
FROM "Posts"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

```

The important point to notice here is that, with generated key values, EF Core is able to automatically distinguish new from existing entities in a disconnected graph. In a nutshell, when using generated keys, EF Core will always insert an entity when that entity has no key value set.

## Updating existing entities

### Explicit key values

[DbContext.Update](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.update), [DbContext.UpdateRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.updaterange), and the equivalent methods on [DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1) behave exactly as the Attach methods described above, except that entities are put into the Modified instead of the Unchanged state. For example, to start tracking an existing blog as Modified:

```csharp
context.Update(
    new Blog { Id = 1, Name = ".NET Blog", });

```

Inspecting the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) following this call shows that the context is tracking this entity in the Modified state:

```bash
Blog {Id: 1} Modified
  Id: 1 PK
  Name: '.NET Blog' Modified
  Posts: []

```

Just like with Add and Attach, Update actually marks an entire graph of related entities as Modified. For example, to attach an existing blog and associated existing posts as Modified:

```csharp
context.Update(
    new Blog
    {
        Id = 1,
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Id = 1,
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Id = 2,
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            }
        }
    });

```

The context is now tracking all these entities as Modified:

```bash
Blog {Id: 1} Modified
  Id: 1 PK
  Name: '.NET Blog' Modified
  Posts: [{Id: 1}, {Id: 2}]
Post {Id: 1} Modified
  Id: 1 PK
  BlogId: 1 FK Modified Originally <null>
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...' Modified
  Title: 'Announcing the Release of EF Core 5.0' Modified
  Blog: {Id: 1}
Post {Id: 2} Modified
  Id: 2 PK
  BlogId: 1 FK Modified Originally <null>
  Content: 'F# 5 is the latest version of F#, the functional programming...' Modified
  Title: 'Announcing F# 5' Modified
  Blog: {Id: 1}

```

Calling SaveChanges at this point will cause updates to be sent to the database for all these entities. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p1='1' (DbType = String), @p0='.NET Blog' (Size = 9)], CommandType='Text', CommandTimeout='30']
UPDATE "Blogs" SET "Name" = @p0
WHERE "Id" = @p1;
SELECT changes();

-- Executed DbCommand (0ms) [Parameters=[@p3='1' (DbType = String), @p0='1' (DbType = String), @p1='Announcing the release of EF Core 5.0, a full featured cross-platform...' (Size = 72), @p2='Announcing the Release of EF Core 5.0' (Size = 37)], CommandType='Text', CommandTimeout='30']
UPDATE "Posts" SET "BlogId" = @p0, "Content" = @p1, "Title" = @p2
WHERE "Id" = @p3;
SELECT changes();

-- Executed DbCommand (0ms) [Parameters=[@p3='2' (DbType = String), @p0='1' (DbType = String), @p1='F# 5 is the latest version of F#, the functional programming language...' (Size = 72), @p2='Announcing F# 5' (Size = 15)], CommandType='Text', CommandTimeout='30']
UPDATE "Posts" SET "BlogId" = @p0, "Content" = @p1, "Title" = @p2
WHERE "Id" = @p3;
SELECT changes();

```

### Generated key values

As with Attach, generated key values have the same major benefit for Update: an unset key value indicates that the entity is new and has not yet been inserted into the database. As with Attach, this allows the DbContext to automatically detect new entities and put them in the Added state. For example, consider calling Update with this graph of a blog and posts:

```csharp
context.Update(
    new Blog
    {
        Id = 1,
        Name = ".NET Blog",
        Posts =
        {
            new Post
            {
                Id = 1,
                Title = "Announcing the Release of EF Core 5.0",
                Content = "Announcing the release of EF Core 5.0, a full featured cross-platform..."
            },
            new Post
            {
                Id = 2,
                Title = "Announcing F# 5",
                Content = "F# 5 is the latest version of F#, the functional programming language..."
            },
            new Post
            {
                Title = "Announcing .NET 5.0",
                Content = ".NET 5.0 includes many enhancements, including single file applications, more..."
            },
        }
    });

```

As with the Attach example, the post with no key value is detected as new and set to the Added state. The other entities are marked as Modified:

```bash
Blog {Id: 1} Modified
  Id: 1 PK
  Name: '.NET Blog' Modified
  Posts: [{Id: 1}, {Id: 2}, {Id: -2147482633}]
Post {Id: -2147482633} Added
  Id: -2147482633 PK Temporary
  BlogId: 1 FK
  Content: '.NET 5.0 includes many enhancements, including single file a...'
  Title: 'Announcing .NET 5.0'
  Blog: {Id: 1}
Post {Id: 1} Modified
  Id: 1 PK
  BlogId: 1 FK Modified Originally <null>
  Content: 'Announcing the release of EF Core 5.0, a full featured cross...' Modified
  Title: 'Announcing the Release of EF Core 5.0' Modified
  Blog: {Id: 1}
Post {Id: 2} Modified
  Id: 2 PK
  BlogId: 1 FK Modified Originally <null>
  Content: 'F# 5 is the latest version of F#, the functional programming...' Modified
  Title: 'Announcing F# 5' Modified
  Blog: {Id: 1}

```

Calling SaveChanges at this point will cause updates to be sent to the database for all the existing entities, while the new entity is inserted. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p1='1' (DbType = String), @p0='.NET Blog' (Size = 9)], CommandType='Text', CommandTimeout='30']
UPDATE "Blogs" SET "Name" = @p0
WHERE "Id" = @p1;
SELECT changes();

-- Executed DbCommand (0ms) [Parameters=[@p3='1' (DbType = String), @p0='1' (DbType = String), @p1='Announcing the release of EF Core 5.0, a full featured cross-platform...' (Size = 72), @p2='Announcing the Release of EF Core 5.0' (Size = 37)], CommandType='Text', CommandTimeout='30']
UPDATE "Posts" SET "BlogId" = @p0, "Content" = @p1, "Title" = @p2
WHERE "Id" = @p3;
SELECT changes();

-- Executed DbCommand (0ms) [Parameters=[@p3='2' (DbType = String), @p0='1' (DbType = String), @p1='F# 5 is the latest version of F#, the functional programming language...' (Size = 72), @p2='Announcing F# 5' (Size = 15)], CommandType='Text', CommandTimeout='30']
UPDATE "Posts" SET "BlogId" = @p0, "Content" = @p1, "Title" = @p2
WHERE "Id" = @p3;
SELECT changes();

-- Executed DbCommand (0ms) [Parameters=[@p0='1' (DbType = String), @p1='.NET 5.0 includes many enhancements, including single file applications, more...' (Size = 80), @p2='Announcing .NET 5.0' (Size = 19)], CommandType='Text', CommandTimeout='30']
INSERT INTO "Posts" ("BlogId", "Content", "Title")
VALUES (@p0, @p1, @p2);
SELECT "Id"
FROM "Posts"
WHERE changes() = 1 AND "rowid" = last_insert_rowid();

```

This is a very easy way to generate updates and inserts from a disconnected graph. However, it results in updates or inserts being sent to the database for every property of every tracked entity, even when some property values may not have been changed. Don't be too scared by this; for many applications with small graphs, this can be an easy and pragmatic way of generating updates. That being said, other more complex patterns can sometimes result in more efficient updates, as described in [Identity Resolution in EF Core](https://learn.microsoft.com/en-us/ef/core/change-tracking/identity-resolution).

## Deleting existing entities

For an entity to be deleted by SaveChanges it must be tracked in the Deleted state. Entities are typically put in the Deleted state by calling one of [DbContext.Remove](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.remove), [DbContext.RemoveRange](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.removerange), or the equivalent methods on [DbSet](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1). For example, to mark an existing post as Deleted:

```csharp
context.Remove(
    new Post { Id = 2 });

```

Inspecting the [change tracker debug view](https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views) following this call shows that the context is tracking the entity in the Deleted state:

```bash
Post {Id: 2} Deleted
  Id: 2 PK
  BlogId: <null> FK
  Content: <null>
  Title: <null>
  Blog: <null>

```

This entity will be deleted when SaveChanges is called. For example, when using SQLite:

```sql
-- Executed DbCommand (0ms) [Parameters=[@p0='2' (DbType = String)], CommandType='Text', CommandTimeout='30']
DELETE FROM "Posts"
WHERE "Id" = @p0;
SELECT changes();

```

After SaveChanges completes, the deleted entity is detached from the DbContext since it no longer exists in the database. The debug view is therefore empty because no entities are being tracked.

## Deleting dependent/child entities

Deleting dependent/child entities from a graph is more straightforward than deleting principal/parent entities. See the next section and [Changing Foreign Keys and Navigations](https://learn.microsoft.com/en-us/ef/core/change-tracking/relationship-changes) for more information.

It is unusual to call Remove on an entity created with new. Further, unlike Add, Attach and Update, it is uncommon to call Remove on an entity that isn't already tracked in the Unchanged or Modified state. Instead it is typical to track a single entity or graph of related entities, and then call Remove on the entities that should be deleted. This graph of tracked entities is typically created by either:

- Running a query for the entities
- Using the Attach or Update methods on a graph of disconnected entities, as described in the preceding sections.