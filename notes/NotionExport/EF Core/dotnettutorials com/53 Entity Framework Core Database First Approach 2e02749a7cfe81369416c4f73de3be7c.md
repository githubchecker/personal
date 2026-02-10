# 53. Entity Framework Core Database First Approach

# EF Core Database First Approach

The **Database First** approach (also known as Reverse Engineering) is a workflow where your code-based data access layer is generated from an existing database schema. This is ideal for legacy systems, shared databases managed by DBAs, or projects where the database design precedes application development.

---

### 1. Prerequisites

To use Database First, install the following NuGet packages:
* `Microsoft.EntityFrameworkCore.SqlServer` (or your specific provider)
* `Microsoft.EntityFrameworkCore.Design` (Required for CLI tools)
* `Microsoft.EntityFrameworkCore.Tools` (Required for Package Manager Console)

---

### 2. Scaffolding the Model

Scaffolding scans your database and generates a `DbContext` and its corresponding entity POCO classes.

### Using .NET CLI (Recommended)

```bash
dotnet ef dbcontext scaffold "Server=.\SQLEXPRESS;Database=EcommerceDB;Trusted_Connection=True;TrustServerCertificate=True" Microsoft.EntityFrameworkCore.SqlServer --output-dir Models --context MyEcommerceContext
```

### Using Package Manager Console (PMC)

```powershell
Scaffold-DbContext "Server=.\SQLEXPRESS;Database=EcommerceDB;Trusted_Connection=True;TrustServerCertificate=True" Microsoft.EntityFrameworkCore.SqlServer -OutputDir Models -Context MyEcommerceContext
```

---

### 3. Working with Generated Code

### The Role of Partial Classes

The scaffolded classes are marked as `partial`. **Never edit generated files directly**, as they will be completely overwritten if you re-scaffold the database later.

To add calculated properties or custom logic, create a new partial class file in the same namespace:

```csharp
// Custom logic in a separate file (e.g., Product.Custom.cs)
public partial class Product
{
    public string FinalPriceDisplay => $"{Price:C} (In Stock: {StockQuantity})";
}
```

### Mapping Database Views

EF Core scaffolds database views as **Keyless Entity Types**. They can be queried like normal tables but do not support tracking or updates.

```csharp
var salesReport = await context.SalesSummaryView
    .Where(v => v.Year == 2023)
    .ToListAsync();
```

---

### 4. Handling Stored Procedures and Functions

Scaffolding does **not** automatically generate C# methods for stored procedures or scalar functions. These must be manually integrated:

- **Stored Procedures:** Call them using `FromSqlRaw`.
- **Scalar Functions:** Map them using the `[DbFunction]` attribute in a partial version of your DbContext.

```csharp
// Calling a Stored Procedure
var results = await context.Products
    .FromSqlRaw("EXEC GetProductsByCategory @CategoryId = {0}", 5)
    .ToListAsync();
```

---

### 5. Managing Schema Changes

When the database schema is updated (e.g., adding a column), you must re-scaffold the model. Use the `--force` (CLI) or `-Force` (PMC) flag to overwrite the old files.

```bash
dotnet ef dbcontext scaffold ... --force
```

---

### Best Practices

1. **Output Organization:** Use the `-output-dir` flag to keep your model files organized in a specific folder.
2. **Schema Filtering:** Use the `-table` flag to scaffold only the tables your application actually uses, rather than the entire database.
3. **Connection Security:** After scaffolding, move the connection string from the generated `OnConfiguring` method into `appsettings.json` and use Dependency Injection.
4. **No Direct Edits:** Always use partial classes or separate configuration files for overrides to prevent losing work during re-scaffolding.