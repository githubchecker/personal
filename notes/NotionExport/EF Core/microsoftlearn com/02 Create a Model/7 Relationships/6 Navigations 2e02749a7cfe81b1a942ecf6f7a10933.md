# 6. Navigations

# Relationship Navigations

Navigations provide an object-oriented view for interacting with related entities without manually managing Foreign Key values.

## 1. Types of Navigations

### Reference Navigations

Represent the "one" side of a relationship.

- **Rules:** Must have a setter (private is fine). Should not be initialized to a non-null default.
- **NRT:** Must be nullable for optional relationships.

```csharp
public Blog? Blog { get; set; } // Reference Navigation

```

### Collection Navigations

Represent the "many" side of a relationship.

- **Rules:** Must implement `ICollection<T>` (e.g., `List<T>`, `HashSet<T>`). No setter required.
- **Tip:** Initialize inline to avoid null checks.

```csharp
public ICollection<Post> Posts { get; } = new List<Post>(); // Collection Navigation

```

## 2. Best Practices for Collections

### Choosing a Collection Type

- `List<T>`**:** Efficient for small sets; maintains stable ordering.
- `HashSet<T>`**:** Faster lookups for large sets; no stable ordering. **Important:** Use `ReferenceEqualityComparer`.

### Encapsulation Pattern

Expose navigations as `IEnumerable<T>` to prevent external modification, while EF Core uses the backing field.

```csharp
public class Blog
{
    private readonly List<Post> _posts = new();
    public IEnumerable<Post> Posts => _posts;

    public void AddPost(Post post) => _posts.Add(post);
}

```

## 3. Configuring Navigations

Use the `.Navigation()` method for settings specific to the property itself (rather than the relationship).

### Property Access Mode

Force EF to use the property's setter/getter instead of the backing field:

```csharp
modelBuilder.Entity<Blog>()
    .Navigation(b => b.Posts)
    .UsePropertyAccessMode(PropertyAccessMode.Property);

```

### Required Navigations

By default, a principal can exist without dependents. However, in **Table Splitting** or **Owned Types**, you can force the dependent to exist:

```csharp
modelBuilder.Entity<Blog>()
    .Navigation(b => b.Header)
    .IsRequired();

```

## 4. Key Considerations

- **No Shared Navigations:** A navigation can belong to only one relationship.
- **Virtual Navigations:** Only required for **Lazy Loading** or **Change-Tracking Proxies**.
- **Reference Equality:** Collections must use reference equality semantics. Do not override `Equals` in entity types unless you use `ReferenceEqualityComparer` in sets.