# 11. Backing fields

# Backing Fields

**Backing Fields** allow EF Core to read from and write to a field rather than a property. This is useful for maintaining encapsulation while allowing EF Core to bypass validation logic or side effects inside property getters and setters.

## 1. Discovery Conventions

EF Core automatically discovers backing fields if they follow these naming patterns (in order of precedence):

- `<camelCasePropertyName>`
- `_<camelCasePropertyName>`
- `_<PropertyName>`
- `m_<camelCasePropertyName>`
- `m_<PropertyName>`

## 2. Explicit Configuration

If your field name doesn't follow conventions, you can map it explicitly.

### Data Annotations

```csharp
public class Blog
{
    private string _validatedUrl;

    [BackingField(nameof(_validatedUrl))]
    public string Url => _validatedUrl; // Read-only property in code
}

```

### Fluent API

```csharp
modelBuilder.Entity<Blog>()
    .Property(b => b.Url)
    .HasField("_validatedUrl");

```

## 3. Property Access Modes

You can control when EF Core uses the field vs. the property using `UsePropertyAccessMode`.

| Mode | Behavior |
| --- | --- |
| `Field` | EF Core always uses the field. (Default when field is found). |
| `Property` | EF Core always uses the property (triggering logic in getters/setters). |
| `PreferField` | Uses field if available, otherwise uses property. |
| `PreferProperty` | Uses property if available, otherwise uses field. |
| `FieldDuringConstruction` | Uses field during object creation, property thereafter. |

```csharp
modelBuilder.Entity<Blog>()
    .Property(b => b.Url)
    .UsePropertyAccessMode(PropertyAccessMode.PreferFieldDuringConstruction);

```

## 4. Field-Only Properties

If an entity has a field but **no corresponding public property**, you can still map it. This is useful for internal audit data or hidden keys.

```csharp
public class Blog
{
    private string _internalSecret; // No property
    public int Id { get; set; }
}

// Map the field directly
modelBuilder.Entity<Blog>().Property<string>("_internalSecret");

// Query in LINQ
var secretBlogs = context.Blogs
    .Where(b => EF.Property<string>(b, "_internalSecret") == "Secret123");

```