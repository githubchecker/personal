# 5. Foreign and principal keys

# Foreign and Principal Keys

All one-to-one and one-to-many relationships are defined by a **Foreign Key (FK)** on the dependent end that references a **Principal Key** (Primary or Alternate Key) on the principal end.

## 1. Foreign Keys

### Explicit Configuration

Use the Fluent API to specify the FK property.

- **Single Property:** `.HasForeignKey(p => p.BlogId)`
- **Composite Key:** `.HasForeignKey(p => new { p.BlogId1, p.BlogId2 })`

### Shadow Foreign Keys

If the FK property is not defined in your C# class, EF Core creates a **Shadow Property**.

```csharp
modelBuilder.Entity<Post>()
    .HasOne(p => p.Blog)
    .WithMany(b => b.Posts)
    .HasForeignKey("BlogId"); // String indicates a shadow property

```

### Required vs. Optional

The nullability of the FK property determines if the relationship is required. You can override this using `.IsRequired()`.

```csharp
builder.HasOne(p => p.Blog)
    .WithMany(b => b.Posts)
    .HasForeignKey(p => p.BlogId)
    .IsRequired(); // Forces NOT NULL in database

```

## 2. Principal Keys

By default, relationships target the **Primary Key** of the principal entity. You can target an **Alternate Key** (unique column) instead.

```csharp
modelBuilder.Entity<Post>()
    .HasOne(p => p.Blog)
    .WithMany(b => b.Posts)
    .HasPrincipalKey(b => b.AlternateId); // Targets AlternateId instead of Id

```

## 3. Advanced Configuration

### Database Constraint Names

Customize the constraint name used in migrations.

```csharp
builder.HasOne(p => p.Blog)
    .WithMany(b => b.Posts)
    .HasConstraintName("FK_Custom_Post_Blog");

```

### Keyless Entities

- **As Dependent:** A keyless entity can have a Foreign Key pointing to a principal with a key.
- **As Principal:** A keyless entity **cannot** be the principal because it has no key to reference.

### Many-to-Many

Foreign keys in many-to-many relationships are defined on the **Join Entity**. You can customize them inside the `UsingEntity` call:

```csharp
builder.HasMany(p => p.Tags)
    .WithMany(t => t.Posts)
    .UsingEntity(
        l => l.HasOne(typeof(Tag)).WithMany().HasConstraintName("FK_Tag"),
        r => r.HasOne(typeof(Post)).WithMany().HasConstraintName("FK_Post")
    );

```