# 2. Custom templates

# Custom Scaffolding Templates (T4)

Starting with EF Core 7, you can customize the code generated during reverse engineering using **T4 text templates**. This allows you to apply specific coding styles, architectural patterns, or UI-framework requirements (like WPF's `ObservableCollection`) directly to the generated output.

## 1. Setup

To start customizing, you must first add the default EF Core templates to your project.

### Step A: Install the Template Package

```bash
dotnet new install Microsoft.EntityFrameworkCore.Templates

```

### Step B: Add Templates to Your Project

Run this command from your project root:

```bash
dotnet new ef-templates

```

This creates a `CodeTemplates/EFCore/` directory containing:

- `DbContext.t4`: Controls the generation of the `DbContext` class.
- `EntityType.t4`: Controls the generation of individual entity classes.

## 2. Using T4 Templates

EF Core automatically detects and uses any `.t4` files in the `CodeTemplates` folder when you run the `scaffold` command.

### Common Template Syntax

- **Directives (**`<#@ ... #>`**)**: Configure the template (e.g., set namespaces or assembly references).
- **Control Blocks (**`<# ... #>`**)**: Execute C# logic to decide what to generate.
- **Expression Blocks (**`<#= ... #>`**)**: Evaluate a C# expression and insert the result into the text.

## 3. Example Customizations

### Changing `List<T>` to `ObservableCollection<T>`

In `EntityType.t4`, find the code block generating collection navigations and replace `List` with `ObservableCollection`:

```csharp
// Before:
public virtual ICollection<<#= targetType #>> <#= nav.Name #> { get; } = new List<<#= targetType #>>();

// After:
public virtual ICollection<<#= targetType #>> <#= nav.Name #> { get; } = new ObservableCollection<<#= targetType #>>();

```

### Splitting Configuration into Separate Classes

By default, all configuration is in `OnModelCreating`. You can use an `EntityTypeConfiguration.t4` template to generate separate `IEntityTypeConfiguration<T>` classes for each entity, keeping the `DbContext` file cleaner.

### Generating Many-to-Many Join Entities

By default, EF Core hides the join table for simple many-to-many relationships. You can comment out the short-circuit condition in `EntityType.t4` to force the generation of an explicit join entity.

```csharp
<#
    // if (EntityType.IsSimpleManyToManyJoinEntityType()) { return ""; }
#>

```

## 4. Maintenance and Best Practices

- **Update Templates:** When upgrading EF Core versions, update your templates (`dotnet new update`) to ensure they include the latest bug fixes and metadata properties.
- **Partial Classes:** Even with custom templates, continue using **partial classes** for logic that shouldn't be controlled by the database schema (e.g., helper methods or business logic).
- **Source Control:** Always check your customized `.t4` files into version control so the team generates consistent code.