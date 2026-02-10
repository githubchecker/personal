# 15. Entity type constructors

# Entity Type Constructors

EF Core can instantiate entities using parameterized constructors. This allows for immutable properties, value validation during creation, and service injection (e.g., for lazy loading).

## 1. Mapping Properties to Parameters

EF Core matches constructor parameters to mapped properties based on **name** (case-insensitive) and **type**.

```csharp
public class Blog
{
    // EF Core will call this and pass 'id' and 'name' from the database
    public Blog(int id, string name)
    {
        Id = id;
        Name = name;
    }

    public int Id { get; }      // Read-only
    public string Name { get; }  // Read-only
    public string? Description { get; set; } // Set normally after construction
}

```

### Core Rules

- **Naming:** Properties can be `PascalCase` while parameters are `camelCase`.
- **Navigations:** Navigation properties (e.g., `List<Post>`) **cannot** be set via constructors.
- **Accessibility:** Constructors can be `public`, `private`, or `protected`. Note that **Lazy-Loading Proxies** require a `public` or `protected` constructor.

## 2. Read-Only Properties and Private Setters

For properties that shouldn't be changed after creation:

- **Private Setters:** Recommended for properties with database-generated values (like Primary Keys).
- **True Read-Only:** Map them explicitly in `OnModelCreating` if they don't have setters, as they aren't discovered by convention.

```csharp
public class Blog
{
    public Blog(string name) => Name = name;
    public string Name { get; } // True read-only
}

// Fluent API configuration is required for true read-only
modelBuilder.Entity<Blog>().Property(b => b.Name);

```

## 3. Injecting Services

EF Core can inject specific "internal" services into entity constructors:

- `DbContext`**:** The current context instance.
- `ILazyLoader`**:** Service for manual lazy loading.
- `IEntityType`**:** Metadata for the current entity type.

```csharp
public class Blog
{
    private readonly MyDbContext _context;

    public Blog(MyDbContext context) => _context = context;

    public int GetPostCount() => _context.Posts.Count(p => p.BlogId == Id);
}

```

<aside>
⚠️ **Anti-Pattern Warning:** Injecting `DbContext` directly into entities couples your domain model to EF Core and is generally discouraged.

</aside>

## 4. Key Takeaways

- Use constructors to enforce **immutability** in your domain model.
- EF Core prefers the constructor with the most matching parameters.
- If no matching parameterized constructor is found, the **parameterless constructor** is used.