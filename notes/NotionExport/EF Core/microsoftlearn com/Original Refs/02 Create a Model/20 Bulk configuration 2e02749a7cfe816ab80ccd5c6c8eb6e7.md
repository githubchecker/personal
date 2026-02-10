# 20. Bulk configuration

# Model bulk configuration

When an aspect needs to be configured in the same way across multiple entity types, the following techniques allow to reduce code duplication and consolidate the logic.

See the [full sample project](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/BulkConfiguration) containing the code snippets presented below.

## Bulk configuration in OnModelCreating

Every builder object returned from [ModelBuilder](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.modelbuilder) exposes a [Model](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.modelbuilder.model#microsoft-entityframeworkcore-modelbuilder-model) or Metadata property that provides a low-level access to the objects that comprise the model. In particular, there are methods that allow you to iterate over specific objects in the model and apply common configuration to them.

In the following example the model contains a custom value type Currency:

```csharp
public readonly struct Currency
{
    public Currency(decimal amount)
        => Amount = amount;

    public decimal Amount { get; }

    public override string ToString()
        => $"${Amount}";
}

```

Properties of this type are not discovered by default as the current EF provider doesn't know how to map it to a database type. This snippet of OnModelCreating adds all properties of the type Currency and configures a value converter to a supported type - decimal:

```csharp
foreach (var entityType in modelBuilder.Model.GetEntityTypes())
{
    foreach (var propertyInfo in entityType.ClrType.GetProperties())
    {
        if (propertyInfo.PropertyType == typeof(Currency))
        {
            entityType.AddProperty(propertyInfo)
                .SetValueConverter(typeof(CurrencyConverter));
        }
    }
}

```

```csharp
public class CurrencyConverter : ValueConverter<Currency, decimal>
{
    public CurrencyConverter()
        : base(
            v => v.Amount,
            v => new Currency(v))
    {
    }
}

```

### Drawbacks of the Metadata API

- Unlike [Fluent API](https://learn.microsoft.com/en-us/ef/core/modeling/#use-fluent-api-to-configure-a-model), every modification to the model needs to be done explicitly. For example, if some of the Currency properties were configured as navigations by a convention then you need to first remove the navigation referencing the CLR property before adding an entity type property for it. [#9117](https://github.com/dotnet/efcore/issues/9117) will improve this.
- The conventions run after each change. If you remove a navigation discovered by a convention then the convention will run again and could add it back. To prevent this from happening you would need to either delay the conventions until after the property is added by calling [DelayConventions()](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.iconventioncontext.delayconventions#microsoft-entityframeworkcore-metadata-conventions-iconventioncontext-delayconventions) and later disposing the returned object or to mark the CLR property as ignored using [AddIgnored](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.imutablemodel.addignored).
- Entity types might be added after this iteration happens and the configuration won't be applied to them. This can usually be prevented by placing this code at the end of OnModelCreating, but if you have two interdependent sets of configurations there might not be an order that will allow them to be applied consistently.

## Pre-convention configuration

EF Core allows the mapping configuration to be specified once for a given CLR type; that configuration is then applied to all properties of that type in the model as they are discovered. This is called "pre-convention model configuration", since it configures aspects of the model before the model building conventions are allowed to run. Such configuration is applied by overriding [ConfigureConventions](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext.configureconventions) on the type derived from [DbContext](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbcontext).

This example shows how configure all properties of type Currency to have a value converter:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder
        .Properties<Currency>()
        .HaveConversion<CurrencyConverter>();
}

```

And this example shows how to configure some facets on all properties of type string:

```csharp
configurationBuilder
    .Properties<string>()
    .AreUnicode(false)
    .HaveMaxLength(1024);

```

<aside>
ℹ️ **NOTE:** The type specified in a call fromConfigureConventionscan be a base type, an interface or a generic type definition. All matching configurations will be applied in order from the least specific:InterfaceBase typeGeneric type definitionNon-nullable value typeExact type

</aside>

<aside>
🔥 **IMPORTANT:** Pre-convention configuration is equivalent to explicit configuration that is applied as soon as a matching object is added to the model. It will override all conventions and Data Annotations. For example, with the above configuration all string foreign key properties will be created as non-unicode withMaxLengthof 1024, even when this doesn't match the principal key.

</aside>

### Ignoring types

Pre-convention configuration also allows to ignore a type and prevent it from being discovered by conventions either as an entity type or as a property on an entity type:

```csharp
configurationBuilder
    .IgnoreAny(typeof(IList<>));

```

### Default type mapping

Generally, EF is able to translate queries with constants of a type that is not supported by the provider, as long as you have specified a value converter for a property of this type. However, in queries that don't involve any properties of this type, there is no way for EF to find the correct value converter. In this case, it's possible to call [DefaultTypeMapping](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.modelconfigurationbuilder.defaulttypemapping) to add or override a provider type mapping:

```csharp
configurationBuilder
    .DefaultTypeMapping<Currency>()
    .HasConversion<CurrencyConverter>();

```

### Limitations of pre-convention configuration

- Many aspects cannot be configured with this approach. [#6787](https://github.com/dotnet/efcore/issues/6787) will expand this to more types.
- Currently the configuration is only determined by the CLR type. [#20418](https://github.com/dotnet/efcore/issues/20418) would allow custom predicates.
- This configuration is performed before a model is created. If there are any conflicts that arise when applying it, the exception stack trace will not contain the ConfigureConventions method, so it might be harder to find the cause.

## Conventions

EF Core model building conventions are classes that contain logic that is triggered based on changes being made to the model as it is being built. This keeps the model up-to-date as explicit configuration is made, mapping attributes are applied, and other conventions run. To participate in this, every convention implements one or more interfaces which determine when the corresponding method will be triggered. For example, a convention that implements [IEntityTypeAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.ientitytypeaddedconvention) will be triggered whenever a new entity type is added to the model. Likewise, a convention that implements both [IForeignKeyAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.iforeignkeyaddedconvention) and [IKeyAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.ikeyaddedconvention) will be triggered whenever either a key or a foreign key is added to the model.

Model building conventions are a powerful way to control the model configuration, but can be complex and hard to get right. In many cases, the [pre-convention model configuration](https://learn.microsoft.com/en-us/ef/core/modeling/bulk-configuration#pre-convention-configuration) can be used instead to easily specify common configuration for properties and types.

### Adding a new convention

### Example: Constrain length of discriminator properties

The [table-per-hierarchy inheritance mapping strategy](https://learn.microsoft.com/en-us/ef/core/modeling/inheritance) requires a discriminator column to specify which type is represented in any given row. By default, EF uses an unbounded string column for the discriminator, which ensures that it will work for any discriminator length. However, constraining the maximum length of discriminator strings can make for more efficient storage and queries. Let's create a new convention that will do that.

EF Core model building conventions are triggered based on changes being made to the model as it is being built. This keeps the model up-to-date as explicit configuration is made, mapping attributes are applied, and other conventions run. To participate in this, every convention implements one or more interfaces which determine when the convention will be triggered. For example, a convention that implements [IEntityTypeAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.ientitytypeaddedconvention) will be triggered whenever a new entity type is added to the model. Likewise, a convention that implements both [IForeignKeyAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.iforeignkeyaddedconvention) and [IKeyAddedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.ikeyaddedconvention) will be triggered whenever either a key or a foreign key is added to the model.

Knowing which interfaces to implement can be tricky, since configuration made to the model at one point may be changed or removed at a later point. For example, a key may be created by convention, but then later replaced when a different key is configured explicitly.

Let's make this a bit more concrete by making a first attempt at implementing the discriminator-length convention:

```csharp
public class DiscriminatorLengthConvention1 : IEntityTypeBaseTypeChangedConvention
{
    public void ProcessEntityTypeBaseTypeChanged(
        IConventionEntityTypeBuilder entityTypeBuilder,
        IConventionEntityType? newBaseType,
        IConventionEntityType? oldBaseType,
        IConventionContext<IConventionEntityType> context)
    {
        var discriminatorProperty = entityTypeBuilder.Metadata.FindDiscriminatorProperty();
        if (discriminatorProperty != null
            && discriminatorProperty.ClrType == typeof(string))
        {
            discriminatorProperty.Builder.HasMaxLength(24);
        }
    }
}

```

This convention implements [IEntityTypeBaseTypeChangedConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.ientitytypebasetypechangedconvention), which means it will be triggered whenever the mapped inheritance hierarchy for an entity type is changed. The convention then finds and configures the string discriminator property for the hierarchy.

This convention is then used by calling [Add](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.conventionsetbuilder.add) in ConfigureConventions:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder.Conventions.Add(_ =>  new DiscriminatorLengthConvention1());
}

```

<aside>
ℹ️ **NOTE:** Rather than adding an instance of the convention directly, theAddmethod accepts a factory for creating instances of the convention. This allows the convention to use dependencies from the EF Core internal service provider. Since this convention has no dependencies, the service provider parameter is named_, indicating that it is never used.

</aside>

Building the model and looking at the Post entity type shows that this has worked - the discriminator property is now configured to with a maximum length of 24:

```
 Discriminator (no field, string) Shadow Required AfterSave:Throw MaxLength(24)

```

But what happens if we now explicitly configure a different discriminator property? For example:

```csharp
modelBuilder.Entity<Post>()
    .HasDiscriminator<string>("PostTypeDiscriminator")
    .HasValue<Post>("Post")
    .HasValue<FeaturedPost>("Featured");

```

Looking at the [debug view](https://learn.microsoft.com/en-us/ef/core/modeling/#debug-view) of the model, we find that the discriminator length is no longer configured.

```
 PostTypeDiscriminator (no field, string) Shadow Required AfterSave:Throw

```

This is because the discriminator property that we configured in our convention was later removed when the custom discriminator was added. We could attempt to fix this by implementing another interface on our convention to react to the discriminator changes, but figuring out which interface to implement is not easy.

Fortunately, there is an easier approach. A lot of the time, it doesn't matter what the model looks like while it is being built, as long as the final model is correct. In addition, the configuration we want to apply often does not need to trigger other conventions to react. Therefore, our convention can implement [IModelFinalizingConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.imodelfinalizingconvention). Model finalizing conventions run after all other model building is complete, and so have access to the near-final state of the model. This is opposed to interactive conventions that react to each model change and make sure that the model is up-to-date at any point of the OnModelCreating method execution. A model finalizing convention will typically iterate over the entire model configuring model elements as it goes. So, in this case, we will find every discriminator in the model and configure it:

```csharp
public class DiscriminatorLengthConvention2 : IModelFinalizingConvention
{
    public void ProcessModelFinalizing(IConventionModelBuilder modelBuilder, IConventionContext<IConventionModelBuilder> context)
    {
        foreach (var entityType in modelBuilder.Metadata.GetEntityTypes()
                     .Where(entityType => entityType.BaseType == null))
        {
            var discriminatorProperty = entityType.FindDiscriminatorProperty();
            if (discriminatorProperty != null
                && discriminatorProperty.ClrType == typeof(string))
            {
                discriminatorProperty.Builder.HasMaxLength(24);
            }
        }
    }
}

```

After building the model with this new convention, we find that the discriminator length is now configured correctly even though it has been customized:

```
PostTypeDiscriminator (no field, string) Shadow Required AfterSave:Throw MaxLength(24)

```

We can go one step further and configure the max length to be the length of the longest discriminator value:

```csharp
public class DiscriminatorLengthConvention3 : IModelFinalizingConvention
{
    public void ProcessModelFinalizing(IConventionModelBuilder modelBuilder, IConventionContext<IConventionModelBuilder> context)
    {
        foreach (var entityType in modelBuilder.Metadata.GetEntityTypes()
                     .Where(entityType => entityType.BaseType == null))
        {
            var discriminatorProperty = entityType.FindDiscriminatorProperty();
            if (discriminatorProperty != null
                && discriminatorProperty.ClrType == typeof(string))
            {
                var maxDiscriminatorValueLength =
                    entityType.GetDerivedTypesInclusive().Select(e => ((string)e.GetDiscriminatorValue()!).Length).Max();

                discriminatorProperty.Builder.HasMaxLength(maxDiscriminatorValueLength);
            }
        }
    }
}

```

Now the discriminator column max length is 8, which is the length of "Featured", the longest discriminator value in use.

```
PostTypeDiscriminator (no field, string) Shadow Required AfterSave:Throw MaxLength(8)

```

### Example: Default length for all string properties

Let's look at another example where a finalizing convention can be used - setting a default maximum length for any string property. The convention looks quite similar to the previous example:

```csharp
public class MaxStringLengthConvention : IModelFinalizingConvention
{
    public void ProcessModelFinalizing(IConventionModelBuilder modelBuilder, IConventionContext<IConventionModelBuilder> context)
    {
        foreach (var property in modelBuilder.Metadata.GetEntityTypes()
                     .SelectMany(
                         entityType => entityType.GetDeclaredProperties()
                             .Where(
                                 property => property.ClrType == typeof(string))))
        {
            property.Builder.HasMaxLength(512);
        }
    }
}

```

This convention is pretty simple. It finds every string property in the model and sets its max length to 512. Looking in the debug view at the properties for Post, we see that all the string properties now have a max length of 512.

```
EntityType: Post
  Properties:
    Id (int) Required PK AfterSave:Throw ValueGenerated.OnAdd
    AuthorId (no field, int?) Shadow FK Index
    BlogId (no field, int) Shadow Required FK Index
    Content (string) Required MaxLength(512)
    Discriminator (no field, string) Shadow Required AfterSave:Throw MaxLength(512)
    PublishedOn (DateTime) Required
    Title (string) Required MaxLength(512)

```

<aside>
ℹ️ **NOTE:** The same can be accomplished by pre-convention configuration, but using a convention allows to further filter applicable properties and for[Data Annotations to override the configuration](https://learn.microsoft.com/en-us/ef/core/modeling/).

</aside>

Finally, before we leave this example, what happens if we use both the MaxStringLengthConvention and DiscriminatorLengthConvention3 at the same time? The answer is that it depends which order they are added, since model finalizing conventions run in the order they are added. So if MaxStringLengthConvention is added last, then it will run last, and it will set the max length of the discriminator property to 512. Therefore, in this case, it is better to add DiscriminatorLengthConvention3 last so that it can override the default max length for just discriminator properties, while leaving all other string properties as 512.

### Replacing an existing convention

Sometimes rather than removing an existing convention completely we instead want to replace it with a convention that does basically the same thing, but with changed behavior. This is useful because the existing convention will already implement the interfaces it needs to be triggered appropriately.

### Example: Opt-in property mapping

EF Core maps all public read-write properties by convention. This might not be appropriate for the way your entity types are defined. To change this, we can replace the [PropertyDiscoveryConvention](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.conventions.propertydiscoveryconvention) with our own implementation that doesn't map any property unless it is explicitly mapped in OnModelCreating or marked with a new attribute called Persist:

```csharp
[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field)]
public sealed class PersistAttribute : Attribute
{
}

```

Here is the new convention:

```csharp
public class AttributeBasedPropertyDiscoveryConvention : PropertyDiscoveryConvention
{
    public AttributeBasedPropertyDiscoveryConvention(ProviderConventionSetBuilderDependencies dependencies)
        : base(dependencies)
    {
    }

    public override void ProcessEntityTypeAdded(
        IConventionEntityTypeBuilder entityTypeBuilder,
        IConventionContext<IConventionEntityTypeBuilder> context)
        => Process(entityTypeBuilder);

    public override void ProcessEntityTypeBaseTypeChanged(
        IConventionEntityTypeBuilder entityTypeBuilder,
        IConventionEntityType? newBaseType,
        IConventionEntityType? oldBaseType,
        IConventionContext<IConventionEntityType> context)
    {
        if ((newBaseType == null
             || oldBaseType != null)
            && entityTypeBuilder.Metadata.BaseType == newBaseType)
        {
            Process(entityTypeBuilder);
        }
    }

    private void Process(IConventionEntityTypeBuilder entityTypeBuilder)
    {
        foreach (var memberInfo in GetRuntimeMembers())
        {
            if (Attribute.IsDefined(memberInfo, typeof(PersistAttribute), inherit: true))
            {
                entityTypeBuilder.Property(memberInfo);
            }
            else if (memberInfo is PropertyInfo propertyInfo
                     && Dependencies.TypeMappingSource.FindMapping(propertyInfo) != null)
            {
                entityTypeBuilder.Ignore(propertyInfo.Name);
            }
        }

        IEnumerable<MemberInfo> GetRuntimeMembers()
        {
            var clrType = entityTypeBuilder.Metadata.ClrType;

            foreach (var property in clrType.GetRuntimeProperties()
                         .Where(p => p.GetMethod != null && !p.GetMethod.IsStatic))
            {
                yield return property;
            }

            foreach (var property in clrType.GetRuntimeFields())
            {
                yield return property;
            }
        }
    }
}

```

<aside>
💡 **TIP:** When replacing a built-in convention, the new convention implementation should inherit from the existing convention class. Note that some conventions have relational or provider-specific implementations, in which case the new convention implementation should inherit from the most specific existing convention class for the database provider in use.

</aside>

The convention is then registered using the [Replace](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.conventionsetbuilder.replace) method in ConfigureConventions:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder.Conventions.Replace<PropertyDiscoveryConvention>(
        serviceProvider => new AttributeBasedPropertyDiscoveryConvention(
            serviceProvider.GetRequiredService<ProviderConventionSetBuilderDependencies>()));
}

```

<aside>
💡 **TIP:** This is a case where the existing convention has dependencies, represented by theProviderConventionSetBuilderDependenciesdependency object. These are obtained from the internal service provider usingGetRequiredServiceand passed to the convention constructor.

</aside>

Notice that this convention allows fields to be mapped (in addition to properties) so long as they are marked with [Persist]. This means we can use private fields as hidden keys in the model.

For example, consider the following entity types:

```csharp
public class LaundryBasket
{
    [Persist]
    [Key]
    private readonly int _id;

    [Persist]
    public int TenantId { get; init; }

    public bool IsClean { get; set; }

    public List<Garment> Garments { get; } = new();
}

public class Garment
{
    public Garment(string name, string color)
    {
        Name = name;
        Color = color;
    }

    [Persist]
    [Key]
    private readonly int _id;

    [Persist]
    public int TenantId { get; init; }

    [Persist]
    public string Name { get; }

    [Persist]
    public string Color { get; }

    public bool IsClean { get; set; }

    public LaundryBasket? Basket { get; set; }
}

```

The model built from these entity types is:

```
Model:
  EntityType: Garment
    Properties:
      _id (_id, int) Required PK AfterSave:Throw ValueGenerated.OnAdd
      Basket_id (no field, int?) Shadow FK Index
      Color (string) Required
      Name (string) Required
      TenantId (int) Required
    Navigations:
      Basket (LaundryBasket) ToPrincipal LaundryBasket Inverse: Garments
    Keys:
      _id PK
    Foreign keys:
      Garment {'Basket_id'} -> LaundryBasket {'_id'} ToDependent: Garments ToPrincipal: Basket ClientSetNull
    Indexes:
      Basket_id
  EntityType: LaundryBasket
    Properties:
      _id (_id, int) Required PK AfterSave:Throw ValueGenerated.OnAdd
      TenantId (int) Required
    Navigations:
      Garments (List<Garment>) Collection ToDependent Garment Inverse: Basket
    Keys:
      _id PK

```

Normally, IsClean would have been mapped, but since it is not marked with [Persist], it is now treated as an un-mapped property.

<aside>
💡 **TIP:** This convention could not be implemented as a model finalizing convention because there are existing model finalizing conventions that need to run after the property is mapped to further configure it.

</aside>

### Conventions implementation considerations

EF Core keeps track of how every piece of configuration was made. This is represented by the [ConfigurationSource](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.configurationsource) enum. The different kinds of configuration are:

- Explicit: The model element was explicitly configured in OnModelCreating
- DataAnnotation: The model element was configured using a mapping attribute (aka data annotation) on the CLR type
- Convention: The model element was configured by a model building convention

Conventions should never override configuration marked as DataAnnotation or Explicit. This is achieved by using a convention builder, for example, the [IConventionPropertyBuilder](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.iconventionpropertybuilder), which is obtained from the [Builder](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.iconventionproperty.builder#microsoft-entityframeworkcore-metadata-iconventionproperty-builder) property. For example:

```csharp
property.Builder.HasMaxLength(512);

```

Calling HasMaxLength on the convention builder will only set the max length if it was not already configured by a mapping attribute or in OnModelCreating.

Builder methods like this also have a second parameter: fromDataAnnotation. Set this to true if the convention is making the configuration on behalf of a mapping attribute. For example:

```csharp
property.Builder.HasMaxLength(512, fromDataAnnotation: true);

```

This sets the ConfigurationSource to DataAnnotation, which means that the value can now be overridden by explicit mapping on OnModelCreating, but not by non-mapping attribute conventions.

If the current configuration can't be overridden then the method will return null, this needs to be accounted for if you need to perform further configuration:

```csharp
property.Builder.HasMaxLength(512)?.IsUnicode(false);

```

Notice that if the unicode configuration can't be overridden the max length will still be set. In case when you need to configure the facets only when both calls succeed then you can preemptively check this by calling [CanSetMaxLength](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.iconventionpropertybuilder.cansetmaxlength) and [CanSetIsUnicode](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.metadata.builders.iconventionpropertybuilder.cansetisunicode):