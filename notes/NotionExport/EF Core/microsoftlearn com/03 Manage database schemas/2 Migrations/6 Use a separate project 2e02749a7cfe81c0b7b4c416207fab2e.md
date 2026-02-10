# 6. Use a separate project

# Using a Separate Migrations Project

You may want to store your migrations in a different project (Class Library) than the one containing your `DbContext`. This is common in clean architecture or when managing multiple sets of migrations for different environments.

## 1. Setup Steps

- **Create a Class Library:** This project will host your migration files.
- **Add References:**
- The Startup project (e.g., Web API) needs a reference to the **Migrations project**.
- **Configure the DbContext:** In your startup configuration, specify the assembly name where the migrations are located.

```csharp
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(
        connectionString,
        x => x.MigrationsAssembly("MyProject.Migrations")));

```

## 2. Managing Migrations

When running migrations commands, you must explicitly specify the **Target Project** (where files are created/modified) and the **Startup Project** (where the app runs from).

### .NET CLI

```bash
dotnet ef migrations add InitialCreate --project MyProject.Migrations --startup-project MyProject.API

```

### Package Manager Console (VS)

```powershell
Add-Migration InitialCreate -Project MyProject.Migrations -StartupProject MyProject.API

```

## 3. Handling Circular Dependencies

In some cases, the Startup project referencing the Migrations project (which references the DbContext project) might create a circular dependency if the DbContext project also references the Startup project.

**Solution:** Ensure the dependency flow matches the architecture:

- `Startup` -> `Migrations` -> `DbContext`
- Or, use the `--project` flag to ensure the migrations are added to the correct physical folder regardless of references.

## 4. Key Takeaways

- **First Migration:** If you have no existing migrations, it is often easier to create the first one in the DbContext project and then move the files to the Migrations project.
- **Portability:** Moving migrations to a separate assembly makes it easier to use they in multiple startup projects (e.g., a Web App and a background Worker service).