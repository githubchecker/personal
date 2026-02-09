# 14. Data seeding

# Data Seeding

Data seeding is the process of populating a database with an initial set of data.

There are several ways this can be accomplished in EF Core:

- [Configuration options data seeding (UseSeeding)](https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#use-seeding-method)
- [Custom initialization logic](https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#custom-initialization-logic)
- [Model managed data (HasData)](https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#model-seed-data)
- [Manual migration customization](https://learn.microsoft.com/en-us/ef/core/modeling/data-seeding#manual-migration-customization)

## Configuration optionsUseSeedingandUseAsyncSeedingmethods

EF 9 introduced UseSeeding and UseAsyncSeeding methods, which provide a convenient way of seeding the database with initial data. These methods aim to improve the experience of using custom initialization logic (explained below). They provide one clear location where all the data seeding code can be placed. Moreover, the code inside UseSeeding and UseAsyncSeeding methods is protected by the [migration locking mechanism](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-9.0/whatsnew#concurrent-migrations) to prevent concurrency issues.

The new seeding methods are called as part of [EnsureCreated](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.storage.idatabasecreator.ensurecreated#microsoft-entityframeworkcore-storage-idatabasecreator-ensurecreated) operation, [Migrate](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.relationaldatabasefacadeextensions.migrate) and dotnet ef database update command, even if there are no model changes and no migrations were applied.

<aside>
💡 **TIP:** UsingUseSeedingandUseAsyncSeedingis the recommended way of seeding the database with initial data when working with EF Core.

</aside>

These methods can be set up in the [options configuration step](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/#dbcontextoptions). Here is an example:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    => optionsBuilder
        .UseSqlServer(@"Server=(localdb)\mssqllocaldb;Database=EFDataSeeding;Trusted_Connection=True;ConnectRetryCount=0")
        .UseSeeding((context, _) =>
        {
            var testBlog = context.Set<Blog>().FirstOrDefault(b => b.Url == "http://test.com");
            if (testBlog == null)
            {
                context.Set<Blog>().Add(new Blog { Url = "http://test.com" });
                context.SaveChanges();
            }
        })
        .UseAsyncSeeding(async (context, _, cancellationToken) =>
        {
            var testBlog = await context.Set<Blog>().FirstOrDefaultAsync(b => b.Url == "http://test.com", cancellationToken);
            if (testBlog == null)
            {
                context.Set<Blog>().Add(new Blog { Url = "http://test.com" });
                await context.SaveChangesAsync(cancellationToken);
            }
        });

```

<aside>
ℹ️ **NOTE:** UseSeedingis called from theEnsureCreatedmethod, andUseAsyncSeedingis called from theEnsureCreatedAsyncmethod. When using this feature, it is recommended to implement bothUseSeedingandUseAsyncSeedingmethods using similar logic, even if the code using EF is asynchronous. EF Core tooling currently relies on the synchronous version of the method and will not seed the database correctly if theUseSeedingmethod is not implemented.

</aside>

## Custom initialization logic

A straightforward and powerful way to perform data seeding is to use [DbContext.SaveChangesAsync()](https://learn.microsoft.com/en-us/ef/core/saving/) before the main application logic begins execution. It is recommended to use UseSeeding and UseAsyncSeeding for that purpose, however sometimes using these methods is not a good solution. An example scenario is when seeding requires using two different contexts in one transaction. Below is a code sample performing custom initialization in the application directly:

```csharp
using (var context = new DataSeedingContext())
{
    await context.Database.EnsureCreatedAsync();

    var testBlog = await context.Blogs.FirstOrDefaultAsync(b => b.Url == "http://test.com");
    if (testBlog == null)
    {
        context.Blogs.Add(new Blog { Url = "http://test.com" });
        await context.SaveChangesAsync();
    }
}

```

<aside>
⚠️ **WARNING:** The seeding code should not be part of the normal app execution as this can cause concurrency issues when multiple instances are running and would also require the app having permission to modify the database schema.

</aside>

Depending on the constraints of your deployment the initialization code can be executed in different ways:

- Running the initialization app locally
- Deploying the initialization app with the main app, invoking the initialization routine and disabling or removing the initialization app.

This can usually be automated by using [publish profiles](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/visual-studio-publish-profiles).

## Model managed data

Data can also be associated with an entity type as part of the model configuration. Then, EF Core [migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/) can automatically compute what insert, update or delete operations need to be applied when upgrading the database to a new version of the model.

<aside>
⚠️ **WARNING:** Migrations only considers model changes when determining what operation should be performed to get the managed data into the desired state. Thus any changes to the data performed outside of migrations might be lost or cause an error.

</aside>

As an example, this will configure managed data for a Country in OnModelCreating:

```csharp
modelBuilder.Entity<Country>(b =>
{
    b.Property(x => x.Name).IsRequired();
    b.HasData(
        new Country { CountryId = 1, Name = "USA" },
        new Country { CountryId = 2, Name = "Canada" },
        new Country { CountryId = 3, Name = "Mexico" });
});

```

To add entities that have a relationship the foreign key values need to be specified:

```csharp
modelBuilder.Entity<City>().HasData(
    new City { Id = 1, Name = "Seattle", LocatedInId = 1 },
    new City { Id = 2, Name = "Vancouver", LocatedInId = 2 },
    new City { Id = 3, Name = "Mexico City", LocatedInId = 3 },
    new City { Id = 4, Name = "Puebla", LocatedInId = 3 });

```

When managing data for many-to-many navigations, the join entity needs to be configured explicitly. If the entity type has any properties in shadow state (e.g. the LanguageCountry join entity below), an anonymous class can be used to provide the values:

```csharp
modelBuilder.Entity<Language>(b =>
{
    b.HasData(
        new Language { Id = 1, Name = "English" },
        new Language { Id = 2, Name = "French" },
        new Language { Id = 3, Name = "Spanish" });

    b.HasMany(x => x.UsedIn)
        .WithMany(x => x.OfficialLanguages)
        .UsingEntity(
            "LanguageCountry",
            r => r.HasOne(typeof(Country)).WithMany().HasForeignKey("CountryId").HasPrincipalKey(nameof(Country.CountryId)),
            l => l.HasOne(typeof(Language)).WithMany().HasForeignKey("LanguageId").HasPrincipalKey(nameof(Language.Id)),
            je =>
            {
                je.HasKey("LanguageId", "CountryId");
                je.HasData(
                    new { LanguageId = 1, CountryId = 2 },
                    new { LanguageId = 2, CountryId = 2 },
                    new { LanguageId = 3, CountryId = 3 });
            });
});

```

Owned entity types can be configured in a similar fashion:

```csharp
modelBuilder.Entity<Language>().OwnsOne(p => p.Details).HasData(
    new { LanguageId = 1, Phonetic = false, Tonal = false, PhonemesCount = 44 },
    new { LanguageId = 2, Phonetic = false, Tonal = false, PhonemesCount = 36 },
    new { LanguageId = 3, Phonetic = true, Tonal = false, PhonemesCount = 24 });

```

See the [full sample project](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Modeling/DataSeeding) for more context.

Once the data has been added to the model, [migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/) should be used to apply the changes.

<aside>
💡 **TIP:** If you need to apply migrations as part of an automated deployment you can[create a SQL script](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying#sql-scripts)that can be previewed before execution.

</aside>

Alternatively, you can use context.Database.EnsureCreatedAsync() to create a new database containing the managed data, for example for a test database or when using the in-memory provider or any non-relational database. Note that if the database already exists, EnsureCreatedAsync() will neither update the schema nor managed data in the database. For relational databases you shouldn't call EnsureCreatedAsync() if you plan to use Migrations.

<aside>
ℹ️ **NOTE:** Populating the database using theHasDatamethod used to be referred to as "data seeding". This naming sets incorrect expectations, as the feature has a number of limitations and is only appropriate for specific types of data. That is why we decided to rename it to "model managed data".UseSeedingandUseAsyncSeedingmethods should be used for general purpose data seeding.

</aside>

### Limitations of model managed data

This type of data is managed by migrations and the script to update the data that's already in the database needs to be generated without connecting to the database. This imposes some restrictions:

- The primary key value needs to be specified even if it's usually generated by the database. It will be used to detect data changes between migrations.
- Previously inserted data will be removed if the primary key is changed in any way.

Therefore this feature is most useful for static data that's not expected to change outside of migrations and does not depend on anything else in the database, for example ZIP codes.

If your scenario includes any of the following it is recommended to use UseSeeding and UseAsyncSeeding methods described in the first section:

- Temporary data for testing
- Data that depends on database state
- Data that is large (seeding data gets captured in migration snapshots, and large data can quickly lead to huge files and degraded performance).
- Data that needs key values to be generated by the database, including entities that use alternate keys as the identity
- Data that requires custom transformation (that is not handled by [value conversions](https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions)), such as some password hashing
- Data that requires calls to external API, such as ASP.NET Core Identity roles and users creation
- Data that isn't fixed and deterministic, such as seeding to DateTime.Now.

## Manual migration customization

When a migration is added the changes to the data specified with HasData are transformed to calls to InsertData(), UpdateData(), and DeleteData(). One way of working around some of the limitations of HasData is to manually add these calls or [custom operations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/operations) to the migration instead.

```csharp
migrationBuilder.InsertData(
    table: "Countries",
    columns: new[] { "CountryId", "Name" },
    values: new object[,]
    {
        { 1, "USA" },
        { 2, "Canada" },
        { 3, "Mexico" }
    });

migrationBuilder.InsertData(
    table: "Languages",
    columns: new[] { "Id", "Name", "Details_PhonemesCount", "Details_Phonetic", "Details_Tonal" },
    values: new object[,]
    {
        { 1, "English", 44, false, false },
        { 2, "French", 36, false, false },
        { 3, "Spanish", 24, true, false }
    });

migrationBuilder.InsertData(
    table: "Cites",
    columns: new[] { "Id", "LocatedInId", "Name" },
    values: new object[,]
    {
        { 1, 1, "Seattle" },
        { 2, 2, "Vancouver" },
        { 3, 3, "Mexico City" },
        { 4, 3, "Puebla" }
    });

migrationBuilder.InsertData(
    table: "LanguageCountry",
    columns: new[] { "CountryId", "LanguageId" },
    values: new object[,]
    {
        { 2, 1 },
        { 2, 2 },
        { 3, 3 }
    });

```