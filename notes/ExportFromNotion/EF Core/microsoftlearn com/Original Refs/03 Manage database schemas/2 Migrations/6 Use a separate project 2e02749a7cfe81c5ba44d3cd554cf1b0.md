# 6. Use a separate project

# Using a Separate Migrations Project

You may want to store your migrations in a different project than the one containing your DbContext. You can also use this strategy to maintain multiple sets of migrations, for example, one for development and another for release-to-release upgrades.

<aside>
💡 **TIP:** You can view this article's [sample on GitHub](https://github.com/dotnet/EntityFramework.Docs/tree/main/samples/core/Schemas/ThreeProjectMigrations) .

</aside>

## Steps

- Create a new class library.
- Add a reference to your DbContext project.
- Move the migrations and model snapshot files to the class library.

<aside>
💡 **TIP:** If you have no existing migrations, generate one in the project containing the DbContext then move it.This is important because if the migrations project does not contain an existing migration, the Add-Migration command will be unable to find the DbContext.

</aside>

- Configure the migrations assembly:

```csharp
services.AddDbContext<ApplicationDbContext>(
    options =>
        options.UseSqlServer(
            Configuration.GetConnectionString("DefaultConnection"),
            x => x.MigrationsAssembly("WebApplication1.Migrations")));

```

- Add a reference to your migrations project from the startup project.

```xml
<ItemGroup>
  <ProjectReference Include="..\WebApplication1.Migrations\WebApplication1.Migrations.csproj" />
</ItemGroup>

```

If this causes a circular dependency, you can update the base output path of the migrations project instead:

```xml
<PropertyGroup>
  <BaseOutputPath>..\WebApplication1\bin\</BaseOutputPath>
</PropertyGroup>

```

If you did everything correctly, you should be able to add new migrations to the project.

### .NET CLI

```bash
dotnet ef migrations add NewMigration --project WebApplication1.Migrations

```

### Visual Studio

```powershell
Add-Migration NewMigration -Project WebApplication1.Migrations

```