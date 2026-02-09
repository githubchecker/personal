# 3. One-to-one

# One-to-One Relationships

A **One-to-One** relationship occurs when a principal entity is associated with at most one dependent entity (e.g., a `Blog` has one `BlogHeader`).

## 1. Defining Principal and Dependent

In a one-to-one relationship, one entity must be the **dependent** (holding the Foreign Key), and the other the **principal** (holding the Target Key).

- **Tip:** The entity that cannot exist without the other is typically the dependent (e.g., a `BlogHeader` requires a `Blog`).

## 2. Configuration Patterns

### Required One-to-One

- **Convention:** Non-nullable FK property in the dependent class.

```csharp
modelBuilder.Entity<Blog>()
    .HasOne(b => b.Header)
    .WithOne(h => h.Blog)
    .HasForeignKey<BlogHeader>(h => h.BlogId)
    .IsRequired();

```

### Optional One-to-One

- **Convention:** Nullable FK property in the dependent class.

```csharp
modelBuilder.Entity<Blog>()
    .HasOne(b => b.Header)
    .WithOne(h => h.Blog)
    .HasForeignKey<BlogHeader>(h => h.BlogId)
    .IsRequired(false);

```

### Primary Key to Primary Key (PK-to-PK)

The dependent uses its own Primary Key as the Foreign Key to the principal.

```csharp
modelBuilder.Entity<BlogHeader>()
    .HasOne(h => h.Blog)
    .WithOne(b => b.Header)
    .HasForeignKey<BlogHeader>(h => h.Id);

```

## 3. Navigations and Shadow Keys

### Unidirectional Relationships

If a navigation property exists on only one side, use `WithOne()` without arguments:

```csharp
modelBuilder.Entity<Blog>()
    .HasOne(b => b.Header)
    .WithOne(); // No navigation back to Blog

```

### Shadow Foreign Keys

If the FK property is not in the CLR class, EF creates a shadow property. Always specify the dependent type in the generic `HasForeignKey<T>` call:

```csharp
modelBuilder.Entity<Blog>()
    .HasOne(b => b.Header)
    .WithOne(h => h.Blog)
    .HasForeignKey<BlogHeader>("BlogId");

```

## 4. Advanced Scenarios

### Alternate and Composite Keys

- **Alternate Key:** `builder.HasPrincipalKey<Blog>(b => b.AlternateId);`
- **Composite Key:**

### Self-Referencing One-to-One

Used for relationships like a `Person` and their `Spouse`:

```csharp
modelBuilder.Entity<Person>()
    .HasOne(p => p.Spouse)
    .WithOne()
    .HasForeignKey<Person>(p => p.SpouseId);

```

### Cascade Delete

By default, required one-to-one relationships use **Cascade Delete**. To prevent this:

```csharp
builder.HasOne(b => b.Header)
    .WithOne(h => h.Blog)
    .OnDelete(DeleteBehavior.Restrict);

```