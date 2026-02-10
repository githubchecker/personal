# 5. Foreign and principal keys

# Foreign and principal keys in relationships

All [one-to-one](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/one-to-one) and [one-to-many](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/one-to-many) relationships are defined by a foreign key on the dependent end that references a primary or alternate key on the principal end. For convenience, this primary or alternate key is known as the "principal key" for the relationship. [Many-to-many](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/one-to-many) relationships are composed of two one-to-many relationships, each of which is itself defined by a foreign key referencing a principal key.

<aside>
💡 **TIP:** The code below can be found in[ForeignAndPrincipalKeys.cs](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/Relationships/ForeignAndPrincipalKeys.cs).

</aside>

## Foreign keys

The property or properties that make up foreign key are often [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). The properties can also be configured explicitly using either [mapping attributes](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/mapping-attributes) or with HasForeignKey in the model building API. HasForeignKey can be used with a lambda expression. For example, for a foreign key made up of a single property:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey(e => e.ContainingBlogId);
}

```

Or, for a composite foreign key made up of more than one property:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey(e => new { e.ContainingBlogId1, e.ContainingBlogId2 });
}

```

<aside>
💡 **TIP:** Using lambda expressions in model building API ensures that the property use is available for code analysis and refactoring, and also provides the property type to the API for use in further chained methods.

</aside>

HasForeignKey can also be passed the name of the foreign key property as a string. For example, for a single property:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("ContainingBlogId");
}

```

Or, for a composite foreign key:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("ContainingBlogId1", "ContainingBlogId2");
}

```

Using a string is useful when:

- The property or properties are private.
- The property or properties do not exist on the entity type and should be created as [shadow properties](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties).
- The property name is calculated or constructed based on some input to the model building process.

### Non-nullable foreign key columns

As described in [Optional and required relationships](https://learn.microsoft.com/en-us/ef/core/modeling/relationships#optional-and-required-relationships), the nullability of the foreign key property determines whether a relationship is optional or required. However, a nullable foreign key property can be used for a required relationship using the [[Required]attribute](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/mapping-attributes), or by calling IsRequired in the model building API. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

Or, if the foreign key is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions), then IsRequired can be used without a call to HasForeignKey:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .IsRequired();
}

```

The end result of this is that the foreign key column in the database is made non-nullable even if the foreign key property is nullable. The same thing can be achieved by explicitly configuring the foreign key property itself as required. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .Property(e => e.BlogId)
        .IsRequired();
}

```

### Shadow foreign keys

Foreign key properties can be created as [shadow properties](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties). A shadow property exists in the EF model but does not exist on the .NET type. EF keeps track of the property value and state internally.

Shadow foreign keys are usually used when there is a desire to hide the relational concept of a foreign key from the domain model used by application code/business logic. This application code then manipulates the relationship entirely through [navigations](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/navigations).

<aside>
💡 **TIP:** If entities are going to be serialized, for example to send over a wire, then the foreign key values can be a useful way to keep the relationship information intact when the entities are not in an object/graph form. It is therefore often pragmatic to keep foreign key properties in the .NET type for this purpose. Foreign key properties can be private, which is often a good compromise to avoid exposing the foreign key while allowing its value to travel with the entity.

</aside>

Shadow foreign key properties are often [created by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). A shadow foreign key will also be created if the argument to HasForeignKey does not match any .NET property. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("MyBlogId");
}

```

By convention, a shadow foreign key gets its type from the principal key in the relationship. This type is made nullable unless the relationship is detected as or configured as required.

The shadow foreign key property can also be created explicitly, which is useful for configuring facets of the property. For example, to make the property non-nullable:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .Property<string>("MyBlogId")
        .IsRequired();

    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("MyBlogId");
}

```

<aside>
💡 **TIP:** By convention, foreign key properties inherit facets such as maximum length and Unicode support from the principal key in the relationship. It is therefore rarely necessary to explicitly configure facets on a foreign key property.

</aside>

The creation of a shadow property if the given name does not match any property of the entity type can be disabled using ConfigureWarnings. For example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder.ConfigureWarnings(b => b.Throw(CoreEventId.ShadowPropertyCreated));

```

### Foreign key constraint names

By convention foreign key constraints are named FK_. For composite foreign keys,  becomes an underscore separated list of foreign key property names.

This can be changed in the model building API using HasConstraintName. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey(e => e.BlogId)
        .HasConstraintName("My_BlogId_Constraint");
}

```

<aside>
💡 **TIP:** The constraint name is not used by the EF runtime. It is only used when creating a database schema using[EF Core Migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/).

</aside>

### Indexes for foreign keys

By convention, EF creates a database index for the property or properties of a foreign key. See [Model building conventions](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions) for more information about the types of indexes created by convention.

<aside>
💡 **TIP:** Relationships are defined in the EF model between entity types included in that model. Some relationships may need to reference an entity type in the model of a different context--for example, when using the[BoundedContext pattern](https://www.martinfowler.com/bliki/BoundedContext.html). In these situation, the foreign key column(s) should be mapped to normal properties, and these properties can then be manipulated manually to handle changes to the relationship.

</aside>

## Principal keys

By convention, foreign keys are constrained to the primary key at the principal end of the relationship. However, an alternate key can be used instead. This is achieved using HasPrincipalKey on the model building API. For example, for a single property foreign key:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey(e => e.AlternateId);
}

```

Or for a composite foreign key with multiple properties:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey(e => new { e.AlternateId1, e.AlternateId2 });
}

```

HasPrincipalKey can also be passed the name of the alternate key property as a string. For example, for a single property key:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey("AlternateId");
}

```

Or, for a composite key:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey("AlternateId1", "AlternateId2");
}

```

<aside>
ℹ️ **NOTE:** The order of the properties in the principal and foreign key must match. This is also the order in which the key is defined in the database schema. It does not have to be the same as the order of the properties in the entity type or the columns in the table.

</aside>

There is no need to call HasAlternateKey to define the alternate key on the principal entity; this is done automatically when HasPrincipalKey is used with properties that are not the primary key properties. However, HasAlternateKey can be used for further configure the alternate key, such as to set its database constraint name. See [Keys](https://learn.microsoft.com/en-us/ef/core/modeling/keys) for more information.

## Relationships to keyless entities

Every relationship must have a foreign key that references a principal (primary or alternate) key. This means that a [keyless entity type](https://learn.microsoft.com/en-us/ef/core/modeling/keyless-entity-types) cannot act as the principal end of a relationship, since there is no principal key for the foreign keys to reference.

<aside>
💡 **TIP:** An entity type cannot have an alternate key but no primary key. In this case, the alternate key (or one of the alternate keys, if there are several) must be promoted to the primary key.

</aside>

However, keyless entity types can still have foreign keys defined, and hence can act as the dependent end of a relationship. For example, consider these types, where Tag has no key:

```csharp
public class Tag
{
    public string Text { get; set; } = null!;
    public int PostId { get; set; }
    public Post Post { get; set; } = null!;
}

public class Post
{
    public int Id { get; set; }
}

```

Tag can be configured at the dependent end of the relationship:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Tag>()
        .HasNoKey();

    modelBuilder.Entity<Post>()
        .HasMany<Tag>()
        .WithOne(e => e.Post);
}

```

<aside>
ℹ️ **NOTE:** EF does not support navigations pointing to keyless entity types. See[GitHub Issue #30331](https://github.com/dotnet/efcore/issues/30331).

</aside>

## Foreign keys in many-to-many relationships

In [many-to-many relationships](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/many-to-many), the foreign keys are defined on the join entity type and mapped to foreign key constraints in the join table. Everything described above can also be applied to these join entity foreign keys. For example, setting the database constraint names:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasMany(e => e.Tags)
        .WithMany(e => e.Posts)
        .UsingEntity(
            l => l.HasOne(typeof(Tag)).WithMany().HasConstraintName("TagForeignKey_Constraint"),
            r => r.HasOne(typeof(Post)).WithMany().HasConstraintName("PostForeignKey_Constraint"));
}

```