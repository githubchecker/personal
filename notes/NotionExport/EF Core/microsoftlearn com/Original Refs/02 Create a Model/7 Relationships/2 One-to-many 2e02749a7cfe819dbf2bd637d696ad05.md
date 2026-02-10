# 2. One-to-many

# One-to-many relationships

One-to-many relationships are used when a single entity is associated with any number of other entities. For example, a Blog can have many associated Posts, but each Post is associated with only one Blog.

This document is structured around lots of examples. The examples start with common cases, which also introduce concepts. Later examples cover less common kinds of configuration. A good approach here is to understand the first few examples and concepts, and then go to the later examples based on your specific needs. Based on this approach, we will start with simple "required" and "optional" one-to-many relationships.

<aside>
💡 **TIP:** The code for all the examples below can be found in[OneToMany.cs](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/Relationships/OneToMany.cs).

</aside>

## Required one-to-many

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

A one-to-many relationship is made up from:

- One or more [primary or alternate key](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/foreign-and-principal-keys#principal-keys) properties on the principal entity; that is the "one" end of the relationship. For example, Blog.Id.
- One or more [foreign key](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/foreign-and-principal-keys#foreign-keys) properties on the dependent entity; that is the "many" end of the relationship. For example, Post.BlogId.
- Optionally, a [collection navigation](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/navigations#collection-navigations) on the principal entity referencing the dependent entities. For example, Blog.Posts.
- Optionally, a [reference navigation](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/navigations#reference-navigations) on the dependent entity referencing the principal entity. For example, Post.Blog.

So, for the relationship in this example:

- The foreign key property Post.BlogId is not nullable. This makes the relationship "required" because every dependent (Post) must be related to some principal (Blog), since its foreign key property must be set to some value.
- Both entities have navigations pointing to the related entity or entities on the other side of the relationship.

<aside>
ℹ️ **NOTE:** A required relationship ensures that every dependent entity must be associated with some principal entity. However, a principal entity canalwaysexist without any dependent entities. That is, a required relationship doesnotindicate that there will always be at least one dependent entity. There is no way in the EF model, and also no standard way in a relational database, to ensure that a principal is associated with a certain number of dependents. If this is needed, then it must be implemented in application (business) logic. See[Required navigations](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/navigations#required-navigations)for more information.

</aside>

<aside>
💡 **TIP:** A relationship with two navigations, one from dependent to principal, and an inverse from principal to dependents, is known as a bidirectional relationship.

</aside>

This relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). That is:

- Blog is discovered as the principal in the relationship, and Post is discovered as the dependent.
- Post.BlogId is discovered as a foreign key of the dependent referencing the Blog.Id primary key of the principal. The relationship is discovered as required because Post.BlogId is not nullable.
- Blog.Posts is discovered as the collection navigation.
- Post.Blog is discovered as the reference navigation.

<aside>
🔥 **IMPORTANT:** When using[C# nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/tutorials/nullable-reference-types), the reference navigation must be nullable if the foreign key property is nullable. If the foreign key property is non-nullable, then the reference navigation may be nullable or not. In this case,Post.BlogIdis non-nullable andPost.Blogis also non-nullable. The= null!;construct is used to mark this as intentional for the C# compiler, since EF typically sets theBloginstance and it cannot be null for a fully loaded relationship. See[Working with Nullable Reference Types](https://learn.microsoft.com/en-us/ef/core/miscellaneous/nullable-reference-types)for more information.

</aside>

For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

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

In the example above, configuration of the relationships starts with HasMany on the principal entity type (Blog) and then follows this with WithOne. As with all relationships, it is exactly equivalent to start with dependent entity type (Post) and use HasOne followed by WithMany. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasOne(e => e.Blog)
        .WithMany(e => e.Posts)
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

Neither of these options is better than the other; they both result in exactly the same configuration.

<aside>
💡 **TIP:** It is never necessary to configure a relationship twice, once starting from the principal, and then again starting from the dependent. Also, attempting to configure the principal and dependent halves of a relationship separately generally does not work. Choose to configure each relationship from either one end or the other and then write the configuration code only once.

</aside>

## Optional one-to-many

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int? BlogId { get; set; } // Optional foreign key property
    public Blog? Blog { get; set; } // Optional reference navigation to principal
}

```

This is the same as the previous example, except that the foreign key property and navigation to the principal are now nullable. This makes the relationship "optional" because a dependent (Post) can exist without being related to any principal (Blog).

<aside>
🔥 **IMPORTANT:** When using[C# nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/tutorials/nullable-reference-types), the reference navigation must be nullable if the foreign key property is nullable. In this case,Post.BlogIdis nullable, soPost.Blogmust be nullable too. See[Working with Nullable Reference Types](https://learn.microsoft.com/en-us/ef/core/miscellaneous/nullable-reference-types)for more information.

</aside>

As before, this relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey(e => e.BlogId)
        .IsRequired(false);
}

```

## Required one-to-many with shadow foreign key

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

In some cases, you may not want a foreign key property in your model, since foreign keys are a detail of how the relationship is represented in the database, which is not needed when using the relationship in a purely object-oriented manner. However, if entities are going to be serialized, for example to send over a wire, then the foreign key values can be a useful way to keep the relationship information intact when the entities are not in an object form. It is therefore often pragmatic to keep foreign key properties in the .NET type for this purpose. Foreign key properties can be private, which is often a good compromise to avoid exposing the foreign key while allowing its value to travel with the entity.

Following on from the previous two examples, this example removes the foreign key property from the dependent entity type. EF therefore creates a [shadow foreign key property](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties) called BlogId of type int.

An important point to note here is that [C# nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/tutorials/nullable-reference-types) are being used, so the nullability of the reference navigation is used to determine whether or not the foreign key property is nullable, and therefore whether the relationship is optional or required. If nullable reference types are not being used, then the shadow foreign key property will be nullable by default, making the relationship optional by default. In this case, use IsRequired to force the shadow foreign key property to be non-nullable and make the relationship required.

As before, this relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("BlogId")
        .IsRequired();
}

```

## Optional one-to-many with shadow foreign key

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public Blog? Blog { get; set; } // Optional reference navigation to principal
}

```

Like the previous example, the foreign key property has been removed from the dependent entity type. EF therefore creates a [shadow foreign key property](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties) called BlogId of type int?. Unlike the previous example, this time the foreign key property is created as nullable because [C# nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/tutorials/nullable-reference-types) are being used and the navigation on the dependent entity type is nullable. This makes the relationship optional.

When C# nullable reference types are not being used, then the foreign key property will also, by default, be created as nullable. This means relationships with automatically created shadow properties are optional by default.

As before, this relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasForeignKey("BlogId")
        .IsRequired(false);
}

```

## One-to-many without navigation to principal

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
}

```

For this example, the foreign key property has been re-introduced, but the navigation on the dependent has been removed.

<aside>
💡 **TIP:** A relationship with only one navigation, one from dependent to principal or one from principal to dependent(s), but not both, is known as a unidirectional relationship.

</aside>

As before, this relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne()
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

Notice that the call to WithOne has no arguments. This is the way to tell EF that there is no navigation from Post to Blog.

If configuration starts from the entity with no navigation, then the type of the entity on the other end of the relationship must be explicitly specified using the generic HasOne<>() call. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasOne<Blog>()
        .WithMany(e => e.Posts)
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

## One-to-many without navigation to principal and with shadow foreign key

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
}

```

This example combines two of the previous examples by removing both the foreign key property and the navigation on the dependent.

This relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions) as an optional relationship. Since there is nothing in the code that could be used to indicate that it should be required, some minimal configuration using IsRequired is needed to create a required relationship. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne()
        .IsRequired();
}

```

A more complete configuration can be used to explicitly configure the navigation and foreign key name, with an appropriate call to IsRequired() or IsRequired(false) as needed. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne()
        .HasForeignKey("BlogId")
        .IsRequired();
}

```

## One-to-many without navigation to dependents

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

The previous two examples had navigations from the principal to dependents, but no navigation from the dependent to principal. For the next couple of examples, the navigation on the dependent is re-introduced, while the navigation on the principal is removed instead.

As before, this relationship is [discovered by convention](https://learn.microsoft.com/en-us/ef/core/modeling/relationships/conventions). For cases where the navigations, foreign key, or required/optional nature of the relationship are not discovered by convention, these things can be configured explicitly. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Post>()
        .HasOne(e => e.Blog)
        .WithMany()
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

Notice again that WithMany() is called with no arguments to indicate that there is no navigation in this direction.

If configuration starts from the entity with no navigation, then the type of the entity on the other end of the relationship must be explicitly specified using the generic HasMany<>() call. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany<Post>()
        .WithOne(e => e.Blog)
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

## One-to-many with no navigations

Occasionally, it can be useful to configure a relationship with no navigations. Such a relationship can only be manipulated by changing the foreign key value directly.

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
}

```

This relationship is not discovered by convention, since there are no navigations indicating that the two types are related. It can be configured explicitly in OnModelCreating. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany<Post>()
        .WithOne();
}

```

With this configuration, the Post.BlogId property is still detected as the foreign key by convention, and the relationship is required because the foreign key property is not nullable. The relationship can be made "optional" by making the foreign key property nullable.

A more complete explicit configuration of this relationship is::

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany<Post>()
        .WithOne()
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

## One-to-many with alternate key

In all the examples so far, the foreign key property on the dependent is constrained to the primary key property on the principal. The foreign key can instead be constrained to a different property, which then becomes an alternate key for the principal entity type. For example:

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public int AlternateId { get; set; } // Alternate key as target of the Post.BlogId foreign key
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

This relationship is not discovered by convention, since EF will always, by convention, create a relationship to the primary key. It can be configured explicitly in OnModelCreating using a call to HasPrincipalKey. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey(e => e.AlternateId);
}

```

HasPrincipalKey can be combined with other calls to explicitly configure the navigations, foreign key properties, and required/optional nature. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .HasPrincipalKey(e => e.AlternateId)
        .HasForeignKey(e => e.BlogId)
        .IsRequired();
}

```

## One-to-many with composite foreign key

In all the examples so far, the primary or alternate key property of the principal consisted of a single property. Primary or alternate keys can also be formed from more than one property--these are known as ["composite keys"](https://learn.microsoft.com/en-us/ef/core/modeling/keys). When the principal of a relationship has a composite key, then the foreign key of the dependent must also be a composite key with the same number of properties. For example:

```csharp
// Principal (parent)
public class Blog
{
    public int Id1 { get; set; } // Composite key part 1
    public int Id2 { get; set; } // Composite key part 2
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId1 { get; set; } // Required foreign key property part 1
    public int BlogId2 { get; set; } // Required foreign key property part 2
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

This relationship is discovered by convention. However, the composite key itself needs to be configured explicitly::

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasKey(e => new { e.Id1, e.Id2 });
}

```

<aside>
🔥 **IMPORTANT:** A composite foreign key value is considered to benullif any of its property values are null. A composite foreign key with one property null and another non-null will not be considered a match for a primary or alternate key with the same values. Both will be considerednull.

</aside>

Both HasForeignKey and HasPrincipalKey can be used to explicitly specify keys with multiple properties. For example:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>(
        nestedBuilder =>
        {
            nestedBuilder.HasKey(e => new { e.Id1, e.Id2 });

            nestedBuilder.HasMany(e => e.Posts)
                .WithOne(e => e.Blog)
                .HasPrincipalKey(e => new { e.Id1, e.Id2 })
                .HasForeignKey(e => new { e.BlogId1, e.BlogId2 })
                .IsRequired();
        });
}

```

<aside>
💡 **TIP:** In the code above, the calls toHasKeyandHasManyhave been grouped together into a nested builder. Nested builders remove the need to callEntity<>()multiple times for the same entity type, but are functionally equivalent to callingEntity<>()multiple times.

</aside>

## Required one-to-many without cascade delete

```csharp
// Principal (parent)
public class Blog
{
    public int Id { get; set; }
    public ICollection<Post> Posts { get; } = new List<Post>(); // Collection navigation containing dependents
}

// Dependent (child)
public class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; } // Required foreign key property
    public Blog Blog { get; set; } = null!; // Required reference navigation to principal
}

```

By convention, required relationships are configured to [cascade delete](https://learn.microsoft.com/en-us/ef/core/saving/cascade-delete); this means that when the principal is deleted, all of its dependents are deleted as well, since dependents cannot exist in the database without a principal. It's possible to configure EF to throw an exception instead of automatically deleting dependent rows that can no longer exist:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .HasMany(e => e.Posts)
        .WithOne(e => e.Blog)
        .OnDelete(DeleteBehavior.Restrict);
}

```

## Self-referencing one-to-many