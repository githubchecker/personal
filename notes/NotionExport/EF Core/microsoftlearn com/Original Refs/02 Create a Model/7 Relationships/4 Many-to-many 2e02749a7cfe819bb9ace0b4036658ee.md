# 4. Many-to-many

# Many-to-many relationships

Many-to-many relationships are used when any number entities of one entity type is associated with any number of entities of the same or another entity type. For example, a Post can have many associated Tags, and each Tag can in turn be associated with any number of Posts.

## Understanding many-to-many relationships

Many-to-many relationships are different from [one-to-many](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/one-to-many) and [one-to-one](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/one-to-one) relationships in that they cannot be represented in a simple way using just a foreign key. Instead, an additional entity type is needed to "join" the two sides of the relationship. This is known as the "join entity type" and maps to a "join table" in a relational database. The entities of this join entity type contain pairs of foreign key values, where one of each pair points to an entity on one side of the relationship, and the other points to an entity on the other side of the relationship. Each join entity, and therefore each row in the join table, therefore represents one association between the entity types in the relationship.

EF Core can hide the join entity type and manage it behind the scenes. This allows the navigations of a many-to-many relationship to be used in a natural manner, adding or removing entities from each side as needed. However, it is useful to understand what is happening behind the scenes so that their overall behavior, and in particular the mapping to a relational database, makes sense. Let's start with a relational database schema setup to represent a many-to-many relationship between posts and tags:

```sql
CREATE TABLE "Posts" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Posts" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "Tags" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Tags" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "PostTag" (
    "PostsId" INTEGER NOT NULL,
    "TagsId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostsId", "TagsId"),
    CONSTRAINT "FK_PostTag_Posts_PostsId" FOREIGN KEY ("PostsId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagsId" FOREIGN KEY ("TagsId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

In this schema, PostTag is the join table. It contains two columns: PostsId, which is a foreign key to the primary key of the Posts table, and TagsId, which is a foreign key to primary key of the Tags table. Each row in this table therefore represents an association between one Post and one Tag.

A simplistic mapping for this schema in EF Core consists of three entity types--one for each table. If each of these entity types are represented by a .NET class, then those classes might look the following:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<PostTag> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<PostTag> PostTags { get; } = [];
}

public class PostTag
{
    public int PostsId { get; set; }
    public int TagsId { get; set; }
    public Post Post { get; set; } = null!;
    public Tag Tag { get; set; } = null!;
}

```

Notice that in this mapping there is no many-to-many relationship, but rather two one-to-many relationships, one for each of the foreign keys defined in the join table. This is not an unreasonable way to map these tables, but doesn't reflect the intent of the join table, which is to represent a single many-to-many relationship, rather than two one-to-many relationships.

EF allows for a more natural mapping through the introduction of two collection navigations, one on Post containing its related Tags, and an inverse on Tag containing its related Posts. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<PostTag> PostTags { get; } = [];
    public List<Tag> Tags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<PostTag> PostTags { get; } = [];
    public List<Post> Posts { get; } = [];
}

public class PostTag
{
    public int PostsId { get; set; }
    public int TagsId { get; set; }
    public Post Post { get; set; } = null!;
    public Tag Tag { get; set; } = null!;
}

```

<aside>
💡 **TIP:** These new navigations are known as "skip navigations", because they skip over the join entity to provide direct access to the other side of the many-to-many relationship.

</aside>

As is shown in the example above, a many-to-many relationship can be mapped in this way--that is, with a .NET class for the join entity, and with both navigations for the two one-to-many relationships and skip navigations exposed on the entity types. However, EF can manage the join entity transparently, without a .NET class defined for it, and without navigations for the two one-to-many relationships. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
}

```

Indeed, EF [model building conventions](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions) will, by default, map the Post and Tag types shown here to the three tables in the database schema at the top of this section. This mapping, without explicit use of the join type, is what is typically meant by the term "many-to-many".

## Examples

The following sections contain examples of many-to-many relationships, including the configuration needed to achieve each mapping.

<aside>
💡 **TIP:** The code for all the examples below can be found in[ManyToMany.cs](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/Relationships/ManyToMany.cs).

</aside>

## Basic many-to-many

In the most basic case for a many-to-many, the entity types on each end of the relationship both have a collection navigation. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
}

```

This relationship is [mapped by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). Even though it is not needed, an equivalent explicit configuration for this relationship is shown below as a learning tool:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts);
}

```

Even with this explicit configuration, many aspects of the relationship are still configured by convention. A more complete explicit configuration, again for learning purposes, is:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity(
            "PostTag",
            r => r.HasOne(typeof(Tag)).WithMany().HasForeignKey("TagsId").HasPrincipalKey(nameof(Tag.Id)),
            l => l.HasOne(typeof(Post)).WithMany().HasForeignKey("PostsId").HasPrincipalKey(nameof(Post.Id)),
            j => j.HasKey("PostsId", "TagsId"));
}

```

<aside>
🔥 **IMPORTANT:** Please don't attempt to fully configure everything even when it is not needed. As can be seen above, the code gets complicated quickly and its easy to make a mistake. And even in the example above there are many things in the model that are still configured by convention. It's not realistic to think that everything in an EF model can always be fully configured explicitly.

</aside>

Regardless of whether the relationship is built by convention or using either of the shown explicit configurations, the resulting mapped schema (using SQLite) is:

```sql
CREATE TABLE "Posts" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Posts" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "Tags" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Tags" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "PostTag" (
    "PostsId" INTEGER NOT NULL,
    "TagsId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostsId", "TagsId"),
    CONSTRAINT "FK_PostTag_Posts_PostsId" FOREIGN KEY ("PostsId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagsId" FOREIGN KEY ("TagsId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

<aside>
💡 **TIP:** When using a Database First flow to[scaffold a DbContext from an existing database](https://learn.microsoft.com/en-us/ef/core/managing-schemas/scaffolding/), EF Core 6 and later looks for this pattern in the database schema and scaffolds a many-to-many relationship as described in this document. This behavior can be changed through use of a[custom T4 template](https://learn.microsoft.com/en-us/ef/core/managing-schemas/scaffolding/templates). For other options, see[Many-to-many relationships without mapped join entities are now scaffolded](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-6.0/breaking-changes#many-to-many).

</aside>

<aside>
🔥 **IMPORTANT:** Currently, EF Core usesDictionary<string, object>to represent join entity instances for which no .NET class has been configured. However, to improve performance, a different type may be used in a future EF Core release. Do not depend on the join type beingDictionary<string, object>unless this has been explicitly configured.

</aside>

## Many-to-many with named join table

In the previous example, the join table was named PostTag by convention. It can be given an explicit name with UsingEntity. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity("PostsToTagsJoinTable");
}

```

Everything else about the mapping remains the same, with only the name of the join table changing:

```sql
CREATE TABLE "PostsToTagsJoinTable" (
    "PostsId" INTEGER NOT NULL,
    "TagsId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostsToTagsJoinTable" PRIMARY KEY ("PostsId", "TagsId"),
    CONSTRAINT "FK_PostsToTagsJoinTable_Posts_PostsId" FOREIGN KEY ("PostsId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostsToTagsJoinTable_Tags_TagsId" FOREIGN KEY ("TagsId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Many-to-many with join table foreign key names

Following on from the previous example, the names of the foreign key columns in the join table can also be changed. There are two ways to do this. The first is to explicitly specify the foreign key property names on the join entity. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity(
            r => r.HasOne(typeof(Tag)).WithMany().HasForeignKey("TagForeignKey"),
            l => l.HasOne(typeof(Post)).WithMany().HasForeignKey("PostForeignKey"));
}

```

The second way is to leave the properties with their by-convention names, but then map these properties to different column names. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity(
            j =>
            {
                j.Property("PostsId").HasColumnName("PostForeignKey");
                j.Property("TagsId").HasColumnName("TagForeignKey");
            });
}

```

In either case, the mapping remains the same, with only the foreign key column names changed:

```sql
CREATE TABLE "PostTag" (
    "PostForeignKey" INTEGER NOT NULL,
    "TagForeignKey" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostForeignKey", "TagForeignKey"),
    CONSTRAINT "FK_PostTag_Posts_PostForeignKey" FOREIGN KEY ("PostForeignKey") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagForeignKey" FOREIGN KEY ("TagForeignKey") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

<aside>
💡 **TIP:** Although not shown here, the previous two examples can be combined to map change the join table name and its foreign key column names.

</aside>

## Many-to-many with class for join entity

So far in the examples, the join table has been automatically mapped to a [shared-type entity type](https://learn.microsoft.com/en-us/ef/core/modeling/entity-types#shared-type-entity-types). This removes the need for a dedicated class to be created for the entity type. However, it can be useful to have such a class so that it can be referenced easily, especially when navigations or a payload (A "payload" is any additional data in the join table. For example, the timestamp in which an entry in the join table is created.) are added to the class, as is shown in later examples below. To do this, first create a type PostTag for the join entity in addition to the existing types for Post and Tag:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
}

public class PostTag
{
    public int PostId { get; set; }
    public int TagId { get; set; }
}

```

<aside>
💡 **TIP:** The class can have any name, but it is common to combine the names of the types at either end of the relationship.

</aside>

Now the UsingEntity method can be used to configure this as the join entity type for the relationship. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>();
}

```

The PostId and TagId are automatically picked up as the foreign keys and are configured as the composite primary key for the join entity type. The properties to use for the foreign keys can be explicitly configured for cases where they don't match the EF convention. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>(
            r => r.HasOne<Tag>().WithMany().HasForeignKey(e => e.TagId),
            l => l.HasOne<Post>().WithMany().HasForeignKey(e => e.PostId));
}

```

The mapped database schema for the join table in this example is structurally equivalent to the previous examples, but with some different column names:

```sql
CREATE TABLE "PostTag" (
    "PostId" INTEGER NOT NULL,
    "TagId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostId", "TagId"),
    CONSTRAINT "FK_PostTag_Posts_PostId" FOREIGN KEY ("PostId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagId" FOREIGN KEY ("TagId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Many-to-many with navigations to join entity

Following on from the previous example, now that there is a class representing the join entity, it becomes easy to add navigations that reference this class. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class PostTag
{
    public int PostId { get; set; }
    public int TagId { get; set; }
}

```

<aside>
🔥 **IMPORTANT:** As shown in this example, navigations to the join entity type can be usedin addition tothe skip navigations between the two ends of the many-to-many relationship. This means that the skip navigations can be used to interact with the many-to-many relationship in a natural manner, while the navigations to the join entity type can be used when greater control over the join entities themselves is needed. In a sense, this mapping provides the best of both worlds between a simple many-to-many mapping, and a mapping that more explicitly matches the database schema.

</aside>

Nothing needs to be changed in the UsingEntity call, since the navigations to the join entity are picked up by convention. Therefore, the configuration for this example is the same as for the last example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>();
}

```

The navigations can be configured explicitly for cases where they cannot be determined by convention. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>(
            r => r.HasOne<Tag>().WithMany(e => e.PostTags),
            l => l.HasOne<Post>().WithMany(e => e.PostTags));
}

```

The mapped database schema is not affected by including navigations in the model:

```sql
CREATE TABLE "PostTag" (
    "PostId" INTEGER NOT NULL,
    "TagId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostId", "TagId"),
    CONSTRAINT "FK_PostTag_Posts_PostId" FOREIGN KEY ("PostId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagId" FOREIGN KEY ("TagId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Many-to-many with navigations to and from join entity

The previous example added navigations to the join entity type from the entity types at either end of the many-to-many relationship. Navigations can also be added in the other direction, or in both directions. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class PostTag
{
    public int PostId { get; set; }
    public int TagId { get; set; }
    public Post Post { get; set; } = null!;
    public Tag Tag { get; set; } = null!;
}

```

Nothing needs to be changed in the UsingEntity call, since the navigations to the join entity are picked up by convention. Therefore, the configuration for this example is the same as for the last example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>();
}

```

The navigations can be configured explicitly for cases where they cannot be determined by convention. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>(
            r => r.HasOne<Tag>(e => e.Tag).WithMany(e => e.PostTags),
            l => l.HasOne<Post>(e => e.Post).WithMany(e => e.PostTags));
}

```

The mapped database schema is not affected by including navigations in the model:

```sql
CREATE TABLE "PostTag" (
    "PostId" INTEGER NOT NULL,
    "TagId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostId", "TagId"),
    CONSTRAINT "FK_PostTag_Posts_PostId" FOREIGN KEY ("PostId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagId" FOREIGN KEY ("TagId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Many-to-many with navigations and changed foreign keys

The previous example showed a many-to-many with navigations to and from the join entity type. This example is the same, except that the foreign key properties used are also changed. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class PostTag
{
    public int PostForeignKey { get; set; }
    public int TagForeignKey { get; set; }
    public Post Post { get; set; } = null!;
    public Tag Tag { get; set; } = null!;
}

```

Again, the UsingEntity method is used to configure this:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>(
            r => r.HasOne<Tag>(e => e.Tag).WithMany(e => e.PostTags).HasForeignKey(e => e.TagForeignKey),
            l => l.HasOne<Post>(e => e.Post).WithMany(e => e.PostTags).HasForeignKey(e => e.PostForeignKey));
}

```

The mapped database schema is now:

```sql
CREATE TABLE "PostTag" (
    "PostForeignKey" INTEGER NOT NULL,
    "TagForeignKey" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostForeignKey", "TagForeignKey"),
    CONSTRAINT "FK_PostTag_Posts_PostForeignKey" FOREIGN KEY ("PostForeignKey") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagForeignKey" FOREIGN KEY ("TagForeignKey") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Unidirectional many-to-many

It is not necessary to include a navigation on both sides of the many-to-many relationship. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
}

```

EF needs some configuration to know that this should be a many-to-many relationship, rather than a one-to-many. This is done using HasMany and WithMany, but with no argument passed on the side without a navigation. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany();
}

```

Removing the navigation does not affect the database schema:

```sql
CREATE TABLE "Posts" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Posts" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "Tags" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Tags" PRIMARY KEY AUTOINCREMENT);

CREATE TABLE "PostTag" (
    "PostId" INTEGER NOT NULL,
    "TagsId" INTEGER NOT NULL,
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostId", "TagsId"),
    CONSTRAINT "FK_PostTag_Posts_PostId" FOREIGN KEY ("PostId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagsId" FOREIGN KEY ("TagsId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

## Many-to-many and join table with payload

In the examples so far, the join table has been used only to store the foreign key pairs representing each association. However, it can also be used to store information about the association--for example, the time it was created. In such cases it is best to define a type for the join entity and add the "association payload" properties to this type. It is also common to create navigations to the join entity in addition to the "skip navigations" used for the many-to-many relationship. These additional navigations allow the join entity to be easily referenced from code, thereby facilitating reading and/or changing the payload data. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
    public List<PostTag> PostTags { get; } = [];
}

public class PostTag
{
    public int PostId { get; set; }
    public int TagId { get; set; }
    public DateTime CreatedOn { get; set; }
}

```

It is also common to use generated values for payload properties--for example, a database timestamp that is automatically set when the association row is inserted. This requires some minimal configuration. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity<PostTag>(
            j => j.Property(e => e.CreatedOn).HasDefaultValueSql("CURRENT_TIMESTAMP"));
}

```

The result maps to a entity type schema with a timestamp set automatically when a row is inserted:

```sql
CREATE TABLE "PostTag" (
    "PostId" INTEGER NOT NULL,
    "TagId" INTEGER NOT NULL,
    "CreatedOn" TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    CONSTRAINT "PK_PostTag" PRIMARY KEY ("PostId", "TagId"),
    CONSTRAINT "FK_PostTag_Posts_PostId" FOREIGN KEY ("PostId") REFERENCES "Posts" ("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_PostTag_Tags_TagId" FOREIGN KEY ("TagId") REFERENCES "Tags" ("Id") ON DELETE CASCADE);

```

<aside>
💡 **TIP:** The SQL shown here is for SQLite. On SQL Server/Azure SQL, use.HasDefaultValueSql("GETUTCDATE()")and forTEXTreaddatetime.

</aside>

## Custom shared-type entity type as a join entity

The previous example used the type PostTag as the join entity type. This type is specific to the posts-tags relationship. However, if you have multiple join tables with the same shape, then the same CLR type can be used for all of them. For example, imagine that all our join tables have a CreatedOn column. We can map these using JoinType class mapped as a [shared-type entity type](https://learn.microsoft.com/en-us/ef/core/modeling/entity-types#shared-type-entity-types):

```csharp
public class JoinType
{
    public int Id1 { get; set; }
    public int Id2 { get; set; }
    public DateTime CreatedOn { get; set; }
}

```

This type can then be referenced as the join entity type by multiple different many-to-many relationships. For example:

```csharp
public class Post
{
    public int Id { get; set; }
    public List<Tag> Tags { get; } = [];
    public List<JoinType> PostTags { get; } = [];
}

public class Tag
{
    public int Id { get; set; }
    public List<Post> Posts { get; } = [];
    public List<JoinType> PostTags { get; } = [];
}

public class Blog
{
    public int Id { get; set; }
    public List<Author> Authors { get; } = [];
    public List<JoinType> BlogAuthors { get; } = [];
}

public class Author
{
    public int Id { get; set; }
    public List<Blog> Blogs { get; } = [];
    public List<JoinType> BlogAuthors { get; } = [];
}

```