# 9. Inheritance

# Inheritance

EF can map a .NET type hierarchy to a database. This allows you to write your .NET entities in code as usual, using base and derived types, and have EF seamlessly create the appropriate database schema, issue queries, etc. The actual details of how a type hierarchy is mapped are provider-dependent; this page describes inheritance support in the context of a relational database.

## Entity type hierarchy mapping

By convention, EF will not automatically scan for base or derived types; this means that if you want a CLR type in your hierarchy to be mapped, you must explicitly specify that type on your model. For example, specifying only the base type of a hierarchy will not cause EF Core to implicitly include all of its sub-types.

The following sample exposes a DbSet for Blog and its subclass RssBlog. If Blog has any other subclass, it will not be included in the model.

```csharp
internal class MyContext : DbContext
{
    public DbSet<Blog> Blogs { get; set; }
    public DbSet<RssBlog> RssBlogs { get; set; }
}

public class Blog
{
    public int BlogId { get; set; }
    public string Url { get; set; }
}

public class RssBlog : Blog
{
    public string RssUrl { get; set; }
}

```

<aside>
ℹ️ **NOTE:** Database columns are automatically made nullable as necessary when using TPH mapping. For example, theRssUrlcolumn is nullable because regularBloginstances do not have that property.

</aside>

If you don't want to expose a DbSet for one or more entities in the hierarchy, you can also use the Fluent API to ensure they are included in the model.

<aside>
💡 **TIP:** If you don't rely on[conventions](https://learn.microsoft.com/en-us/ef/core/modeling/#built-in-conventions), you can specify the base type explicitly usingHasBaseType. You can also use.HasBaseType((Type)null)to remove an entity type from the hierarchy.

</aside>

## Table-per-hierarchy and discriminator configuration

By default, EF maps the inheritance using the table-per-hierarchy (TPH) pattern. TPH uses a single table to store the data for all types in the hierarchy, and a discriminator column is used to identify which type each row represents.

The model above is mapped to the following database schema (note the implicitly created Discriminator column, which identifies which type of Blog is stored in each row).

You can configure the name and type of the discriminator column and the values that are used to identify each type in the hierarchy:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasDiscriminator<string>("blog_type")
        .HasValue<Blog>("blog_base")
        .HasValue<RssBlog>("blog_rss");
}

```

In the examples above, EF added the discriminator implicitly as a [shadow property](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties) on the base entity of the hierarchy. This property can be configured like any other:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .Property("blog_type")
        .HasMaxLength(200);
}

```

Finally, the discriminator can also be mapped to a regular .NET property in your entity:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasDiscriminator(b => b.BlogType);

    modelBuilder.Entity<Blog>()
        .Property(e => e.BlogType)
        .HasMaxLength(200)
        .HasColumnName("blog_type");
        
    modelBuilder.Entity<RssBlog>();
}

```

When querying for derived entities, which use the TPH pattern, EF Core adds a predicate over discriminator column in the query. This filter makes sure that we don't get any additional rows for base types or sibling types not in the result. This filter predicate is skipped for the base entity type since querying for the base entity will get results for all the entities in the hierarchy. When materializing results from a query, if we come across a discriminator value, which isn't mapped to any entity type in the model, we throw an exception since we don't know how to materialize the results. This error only occurs if your database contains rows with discriminator values, which aren't mapped in the EF model. If you have such data, then you can mark the discriminator mapping in EF Core model as incomplete to indicate that we should always add filter predicate for querying any type in the hierarchy. IsComplete(false) call on the discriminator configuration marks the mapping to be incomplete.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasDiscriminator()
        .IsComplete(false);
}

```

### Shared columns

By default, when two sibling entity types in the hierarchy have a property with the same name, they will be mapped to two separate columns. However, if their type is identical they can be mapped to the same database column:

```csharp
public class MyContext : DbContext
{
    public DbSet<BlogBase> Blogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Blog>()
            .Property(b => b.Url)
            .HasColumnName("Url");

        modelBuilder.Entity<RssBlog>()
            .Property(b => b.Url)
            .HasColumnName("Url");
    }
}

public abstract class BlogBase
{
    public int BlogId { get; set; }
}

public class Blog : BlogBase
{
    public string Url { get; set; }
}

public class RssBlog : BlogBase
{
    public string Url { get; set; }
}

```

<aside>
ℹ️ **NOTE:** Relational database providers, such as SQL Server, will not automatically use the discriminator predicate when querying shared columns when using a cast. The queryUrl = (blog as RssBlog).Urlwould also return theUrlvalue for the siblingBlogrows. To restrict the query toRssBlogentities you need to manually add a filter on the discriminator, such asUrl = blog is RssBlog ? (blog as RssBlog).Url : null.

</aside>

## Table-per-type configuration

In the TPT mapping pattern, all the types are mapped to individual tables. Properties that belong solely to a base type or derived type are stored in a table that maps to that type. Tables that map to derived types also store a foreign key that joins the derived table with the base table.

```csharp
modelBuilder.Entity<Blog>().ToTable("Blogs");
modelBuilder.Entity<RssBlog>().ToTable("RssBlogs");

```

<aside>
💡 **TIP:** Instead of callingToTableon each entity type you can callmodelBuilder.Entity().UseTptMappingStrategy()on each root entity type and the table names will be generated by EF.

</aside>

<aside>
💡 **TIP:** To configure different column names for the primary key columns in each table see[Table-specific facet configuration](https://learn.microsoft.com/en-us/ef/core/modeling/table-splitting#table-specific-facet-configuration).

</aside>

EF will create the following database schema for the model above.

```sql
CREATE TABLE [Blogs] (
    [BlogId] int NOT NULL IDENTITY,
    [Url] nvarchar(max) NULL,
    CONSTRAINT [PK_Blogs] PRIMARY KEY ([BlogId])
);

CREATE TABLE [RssBlogs] (
    [BlogId] int NOT NULL,
    [RssUrl] nvarchar(max) NULL,
    CONSTRAINT [PK_RssBlogs] PRIMARY KEY ([BlogId]),
    CONSTRAINT [FK_RssBlogs_Blogs_BlogId] FOREIGN KEY ([BlogId]) REFERENCES [Blogs] ([BlogId]) ON DELETE NO ACTION
);

```

<aside>
ℹ️ **NOTE:** If the primary key constraint is renamed the new name will be applied to all the tables mapped to the hierarchy, future EF versions will allow renaming the constraint only for a particular table when[issue 19970](https://github.com/dotnet/efcore/issues/19970)is fixed.

</aside>

If you are employing bulk configuration you can retrieve the column name for a specific table by calling [GetColumnName(IProperty, StoreObjectIdentifier)](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationalpropertyextensions.getcolumnname#microsoft-entityframeworkcore-relationalpropertyextensions-getcolumnname(microsoft-entityframeworkcore-metadata-iproperty-microsoft-entityframeworkcore-metadata-storeobjectidentifier@)).

```csharp
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    var tableIdentifier = StoreObjectIdentifier.Create(entityType, StoreObjectType.Table);

    Console.WriteLine($"{entityType.DisplayName()}\t\t{tableIdentifier}");
    Console.WriteLine(" Property\tColumn");

    foreach (var property in entityType.GetProperties())
    {
        var columnName = property.GetColumnName(tableIdentifier.Value);
        Console.WriteLine($" {property.Name,-10}\t{columnName}");
    }

    Console.WriteLine();
}

```

<aside>
⚠️ **WARNING:** In many cases, TPT shows inferior performance when compared to TPH.[See the performance docs for more information](https://learn.microsoft.com/en-us/ef/core/performance/modeling-for-performance#inheritance-mapping).

</aside>

<aside>
🛑 **CAUTION:** Columns for a derived type are mapped to different tables, therefore composite FK constraints and indexes that use both the inherited and declared properties cannot be created in the database.

</aside>

## Table-per-concrete-type configuration

In the TPC mapping pattern, all the types are mapped to individual tables. Each table contains columns for all properties on the corresponding entity type. This addresses some common performance issues with the TPT strategy.

<aside>
💡 **TIP:** The EF Team demonstrated and talked in depth about TPC mapping in an episode of the[.NET Data Community Standup](https://aka.ms/efstandups). As with all Community Standup episodes, you can[watch the TPC episode now on YouTube](https://youtu.be/HaL6DKW1mrg).

</aside>

```csharp
modelBuilder.Entity<Blog>().UseTpcMappingStrategy()
    .ToTable("Blogs");
modelBuilder.Entity<RssBlog>()
    .ToTable("RssBlogs");

```

<aside>
💡 **TIP:** Instead of callingToTableon each entity type just callingmodelBuilder.Entity().UseTpcMappingStrategy()on each root entity type will generate the table names by convention.

</aside>

<aside>
💡 **TIP:** To configure different column names for the primary key columns in each table see[Table-specific facet configuration](https://learn.microsoft.com/en-us/ef/core/modeling/table-splitting#table-specific-facet-configuration).

</aside>

EF will create the following database schema for the model above.

```sql
CREATE TABLE [Blogs] (
    [BlogId] int NOT NULL DEFAULT (NEXT VALUE FOR [BlogSequence]),
    [Url] nvarchar(max) NULL,
    CONSTRAINT [PK_Blogs] PRIMARY KEY ([BlogId])
);

CREATE TABLE [RssBlogs] (
    [BlogId] int NOT NULL DEFAULT (NEXT VALUE FOR [BlogSequence]),
    [Url] nvarchar(max) NULL,
    [RssUrl] nvarchar(max) NULL,
    CONSTRAINT [PK_RssBlogs] PRIMARY KEY ([BlogId])
);

```

### TPC database schema

The TPC strategy is similar to the TPT strategy except that a different table is created for every concrete type in the hierarchy, but tables are not created for abstract types - hence the name âtable-per-concrete-typeâ. As with TPT, the table itself indicates the type of the object saved. However, unlike TPT mapping, each table contains columns for every property in the concrete type and its base types. TPC database schemas are denormalized.

For example, consider mapping this hierarchy:

```csharp
public abstract class Animal
{
    protected Animal(string name)
    {
        Name = name;
    }

    public int Id { get; set; }
    public string Name { get; set; }
    public abstract string Species { get; }

    public Food? Food { get; set; }
}

public abstract class Pet : Animal
{
    protected Pet(string name)
        : base(name)
    {
    }

    public string? Vet { get; set; }

    public ICollection<Human> Humans { get; } = new List<Human>();
}

public class FarmAnimal : Animal
{
    public FarmAnimal(string name, string species)
        : base(name)
    {
        Species = species;
    }

    public override string Species { get; }

    [Precision(18, 2)]
    public decimal Value { get; set; }

    public override string ToString()
        => $"Farm animal '{Name}' ({Species}/{Id}) worth {Value:C} eats {Food?.ToString() ?? "<Unknown>"}";
}

public class Cat : Pet
{
    public Cat(string name, string educationLevel)
        : base(name)
    {
        EducationLevel = educationLevel;
    }

    public string EducationLevel { get; set; }
    public override string Species => "Felis catus";

    public override string ToString()
        => $"Cat '{Name}' ({Species}/{Id}) with education '{EducationLevel}' eats {Food?.ToString() ?? "<Unknown>"}";
}

public class Dog : Pet
{
    public Dog(string name, string favoriteToy)
        : base(name)
    {
        FavoriteToy = favoriteToy;
    }

    public string FavoriteToy { get; set; }
    public override string Species => "Canis familiaris";

    public override string ToString()
        => $"Dog '{Name}' ({Species}/{Id}) with favorite toy '{FavoriteToy}' eats {Food?.ToString() ?? "<Unknown>"}";
}

public class Human : Animal
{
    public Human(string name)
        : base(name)
    {
    }

    public override string Species => "Homo sapiens";

    public Animal? FavoriteAnimal { get; set; }
    public ICollection<Pet> Pets { get; } = new List<Pet>();

    public override string ToString()
        => $"Human '{N
```

When using SQL Server, the tables created for this hierarchy are:

```sql
CREATE TABLE [Cats] (
    [Id] int NOT NULL DEFAULT (NEXT VALUE FOR [AnimalSequence]),
    [Name] nvarchar(max) NOT NULL,
    [FoodId] uniqueidentifier NULL,
    [Vet] nvarchar(max) NULL,
    [EducationLevel] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_Cats] PRIMARY KEY ([Id]));

CREATE TABLE [Dogs] (
    [Id] int NOT NULL DEFAULT (NEXT VALUE FOR [AnimalSequence]),
    [Name] nvarchar(max) NOT NULL,
    [FoodId] uniqueidentifier NULL,
    [Vet] nvarchar(max) NULL,
    [FavoriteToy] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_Dogs] PRIMARY KEY ([Id]));

CREATE TABLE [FarmAnimals] (
    [Id] int NOT NULL DEFAULT (NEXT VALUE FOR [AnimalSequence]),
    [Name] nvarchar(max) NOT NULL,
    [FoodId] uniqueidentifier NULL,
    [Value] decimal(18,2) NOT NULL,
    [Species] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_FarmAnimals] PRIMARY KEY ([Id]));

CREATE TABLE [Humans] (
    [Id] int NOT NULL DEFAULT (NEXT VALUE FOR [AnimalSequence]),
    [Name] nvarchar(max) NOT NULL,
    [FoodId] uniqueidentifier NULL,
    [FavoriteAnimalId] int NULL,
    CONSTRAINT [PK_Humans] PRIMARY KEY ([Id]));

```

Notice that:

- There are no tables for the Animal or Pet types, since these are abstract in the object model. Remember that C# does not allow instances of abstract types, and there is therefore no situation where an abstract type instance will be saved to the database.
- The mapping of properties in base types is repeated for each concrete type. For example, every table has a Name column, and both Cats and Dogs have a Vet column.
- Saving some data into this database results in the following:

Cats table

| Id | Name | FoodId | Vet | EducationLevel |
| --- | --- | --- | --- | --- |
| 1 | Alice | 99ca3e98-b26d-4a0c-d4ae-08da7aca624f | Pengelly | MBA |
| 2 | Mac | 99ca3e98-b26d-4a0c-d4ae-08da7aca624f | Pengelly | Preschool |
| 8 | Baxter | 5dc5019e-6f72-454b-d4b0-08da7aca624f | Bothell Pet Hospital | BSc |

Dogs table

| Id | Name | FoodId | Vet | FavoriteToy |
| --- | --- | --- | --- | --- |
| 3 | Toast | 011aaf6f-d588-4fad-d4ac-08da7aca624f | Pengelly | Mr. Squirrel |

FarmAnimals table

| Id | Name | FoodId | Value | Species |
| --- | --- | --- | --- | --- |
| 4 | Clyde | 1d495075-f527-4498-d4af-08da7aca624f | 100.00 | Equus africanus asinus |

Humans table

| Id | Name | FoodId | FavoriteAnimalId |
| --- | --- | --- | --- |
| 5 | Wendy | 5418fd81-7660-432f-d4b1-08da7aca624f | 2 |
| 6 | Arthur | 59b495d4-0414-46bf-d4ad-08da7aca624f | 1 |
| 9 | Katie | null | 8 |

Notice that unlike with TPT mapping, all the information for a single object is contained in a single table. And, unlike with TPH mapping, there is no combination of column and row in any table where that is never used by the model. We'll see below how these characteristics can be important for queries and storage.

### Key generation

The inheritance mapping strategy chosen has consequences for how primary key values are generated and managed. Keys in TPH are easy, since each entity instance is represented by a single row in a single table. Any kind of key value generation can be used, and no additional constraints are needed.

For the TPT strategy, there is always a row in the table mapped to the base type of the hierarchy. Any kind of key generation can be used on this row, and the keys for other tables are linked to this table using foreign key constraints.

Things get a bit more complicated for TPC. First, itâs important to understand that EF Core requires that all entities in a hierarchy have a unique key value, even if the entities have different types. For example, using our example model, a Dog cannot have the same Id key value as a Cat. Second, unlike TPT, there is no common table that can act as the single place where key values live and can be generated. This means a simple Identity column cannot be used.

For databases that support sequences, key values can be generated by using a single sequence referenced in the default constraint for each table. This is the strategy used in the TPC tables shown above, where each table has the following:

```sql
[Id] int NOT NULL DEFAULT (NEXT VALUE FOR [AnimalSequence])

```

AnimalSequence is a database sequence created by EF Core. This strategy is used by default for TPC hierarchies when using the EF Core database provider for SQL Server. Database providers for other databases that support sequences should have a similar default. Other key generation strategies that use sequences, such as Hi-Lo patterns, may also be used with TPC.

While standard Identity columns don't work with TPC, it is possible to use Identity columns if each table is configured with an appropriate seed and increment such that the values generated for each table will never conflict. For example:

```csharp
modelBuilder.Entity<Cat>().ToTable("Cats", tb => tb.Property(e => e.Id).UseIdentityColumn(1, 4));
modelBuilder.Entity<Dog>().ToTable("Dogs", tb => tb.Property(e => e.Id).UseIdentityColumn(2, 4));
modelBuilder.Entity<FarmAnimal>().ToTable("FarmAnimals", tb => tb.Property(e => e.Id).UseIdentityColumn(3, 4));
modelBuilder.Entity<Human>().ToTable("Humans", tb => tb.Property(e => e.Id).UseIdentityColumn(4, 4));

```

<aside>
🔥 **IMPORTANT:** Using this strategy makes it harder to add derived types later as it requires the total number of types in the hierarchy to be known beforehand.

</aside>

SQLite does not support sequences or Identity seed/increment, and hence integer key value generation is not supported when using SQLite with the TPC strategy. However, client-side generation or globally unique keys - such as GUIDs - are supported on any database, including SQLite.

### Foreign key constraints

The TPC mapping strategy creates a denormalized SQL schema - this is one reason why some database purists are against it. For example, consider the foreign key column FavoriteAnimalId. The value in this column must match the primary key value of some animal. This can be enforced in the database with a simple FK constraint when using TPH or TPT. For example:

```sql
CONSTRAINT [FK_Animals_Animals_FavoriteAnimalId] FOREIGN KEY ([FavoriteAnimalId]) REFERENCES [Animals] ([Id])

```

But when using TPC, the primary key for any given animal is stored in the table corresponding to the concrete type of that animal. For example, a cat's primary key is stored in the Cats.Id column, while a dog's primary key is stored in the Dogs.Id column, and so on. This means an FK constraint cannot be created for this relationship.

In practice, this is not a problem as long as the application does not attempt to insert invalid data. For example, if all the data is inserted by EF Core and uses navigations to relate entities, then it is guaranteed that the FK column will contain valid PK values at all times.

## Summary and guidance

In summary, TPH is usually fine for most applications, and is a good default for a wide range of scenarios, so don't add the complexity of TPC if you don't need it. Specifically, if your code will mostly query for entities of many types, such as writing queries against the base type, then lean towards TPH over TPC.

That being said, TPC is also a good mapping strategy to use when your code will mostly query for entities of a single leaf type and your benchmarks show an improvement compared with TPH.

Use TPT only if constrained to do so by external factors.