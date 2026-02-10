# 11. Backing fields

# Backing Fields

Backing fields allow EF to read and/or write to a field rather than a property. This can be useful when encapsulation in the class is being used to restrict the use of and/or enhance the semantics around access to the data by application code, but the value should be read from and/or written to the database without using those restrictions/enhancements.

## Basic configuration

By convention, the following fields will be discovered as backing fields for a given property (listed in precedence order).

- _
- _
- m_
- m_

In the following sample, the Url property is configured to have _url as its backing field:

```csharp
public class Blog
{
    private string _url;

    public int BlogId { get; set; }

    public string Url
    {
        get { return _url; }
        set { _url = value; }
    }
}

```

Note that backing fields are only discovered for properties that are included in the model. For more information on which properties are included in the model, see [Including & Excluding Properties](https://learn.microsoft.com/en-us/ef/core/modeling/entity-properties#included-and-excluded-properties).

You can also configure backing fields by using a [Data Annotations](https://learn.microsoft.com/en-us/ef/core/modeling/#use-data-annotations-to-configure-a-model) or the [Fluent API](https://learn.microsoft.com/en-us/ef/core/modeling/#use-fluent-api-to-configure-a-model), e.g. if the field name doesn't correspond to the above conventions:

### Data Annotations

```csharp
public class Blog
{
    private string _validatedUrl;

    public int BlogId { get; set; }

    [BackingField(nameof(_validatedUrl))]
    public string Url
    {
        get { return _validatedUrl; }
    }

    public void SetUrl(string url)
    {
        // put your validation code here

        _validatedUrl = url;
    }
}

```

### Fluent API

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .Property(b => b.Url)
        .HasField("_validatedUrl");
}

```

## Field and property access

By default, EF will always read and write to the backing field - assuming one has been properly configured - and will never use the property. However, EF also supports other access patterns. For example, the following sample instructs EF to write to the backing field only while materializing, and to use the property in all other cases:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Blog>()
        .Property(b => b.Url)
        .HasField("_validatedUrl")
        .UsePropertyAccessMode(PropertyAccessMode.PreferFieldDuringConstruction);
}

```

See the [PropertyAccessMode enum](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.propertyaccessmode) for the complete set of supported options.

## Field-only properties

You can also create a conceptual property in your model that does not have a corresponding CLR property in the entity class, but instead uses a field to store the data in the entity. This is different from [Shadow Properties](https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties), where the data is stored in the change tracker, rather than in the entity's CLR type. Field-only properties are commonly used when the entity class uses methods instead of properties to get/set values, or in cases where fields shouldn't be exposed at all in the domain model (e.g. primary keys).

You can configure a field-only property by providing a name in the Property(...) API:

```csharp
internal class MyContext : DbContext
{
    public DbSet<Blog> Blogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Blog>()
            .Property("_validatedUrl");
    }
}

public class Blog
{
    private string _validatedUrl;

    public int BlogId { get; set; }

    public string GetUrl()
    {
        return _validatedUrl;
    }

    public void SetUrl(string url)
    {
        using (var client = new HttpClient())
        {
            var response = client.GetAsync(url).Result;
            response.EnsureSuccessStatusCode();
        }

        _validatedUrl = url;
    }
}

```

EF will attempt to find a CLR property with the given name, or a field if a property isn't found. If neither a property nor a field are found, a shadow property will be set up instead.

You may need to refer to a field-only property from LINQ queries, but such fields are typically private. You can use the EF.Property(...) method in a LINQ query to refer to the field:

```csharp
var blogs = db.blogs.OrderBy(b => EF.Property<string>(b, "_validatedUrl"));

```