# Phase 1: The Core Concepts (The "Why" and "How")

*(Microsoft Docs Entry Point: [Introduction to Entity Framework Core](https://learn.microsoft.com/en-us/ef/core/))*

### 1. What is an Object-Relational Mapper (O/RM)?

At its heart, Entity Framework Core is an O/RM. It solves a fundamental problem in software development known as the **"Object-Relational Impedance Mismatch."**

- **The Mismatch:** Your C# code thinks in **Objects** (classes with properties and relationships). Your SQL database thinks in **Relational Data** (tables with columns, rows, and foreign keys). These two worlds do not naturally align.
- **The O/RM's Job:** To be the **translator**. It maps your C# classes to database tables, allowing you to write database queries using a high-level language (LINQ) instead of raw SQL strings.

**Without an O/RM (The "Hard Way"):**
You would write code like this. It's verbose, error-prone (typos in column names), and vulnerable to SQL Injection if not handled carefully.

```csharp
var products = new List<Product>();
using (var connection = new SqlConnection(connectionString))
{
    var command = new SqlCommand("SELECT Id, Name, Price FROM Products WHERE IsActive = 1", connection);
    connection.Open();
    using (var reader = command.ExecuteReader())
    {
        while (reader.Read())
        {
            products.Add(new Product
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1),
                Price = reader.GetDecimal(2)
            });
        }
    }
}

```

**With EF Core (The "Smart Way"):**
The O/RM translates your clean C# code into the messy SQL for you.

```csharp
// This single line of LINQ code generates the same SQL as the block above.
var products = await _context.Products.Where(p => p.IsActive).ToListAsync();

```

---

### 2. The `DbContext` (The Gateway)

The `DbContext` is the most important class in EF Core.

- **Concept:** It represents a **session** with the database. It is a lightweight object that acts as the primary gateway for all your database interactions.
- **Function:**
    1. **Connection Management:** It manages the database connection.
    2. **Querying:** It allows you to query the database using its `DbSet<T>` properties.
    3. **Change Tracking:** It keeps track of changes made to the objects you've queried, so it knows what to `INSERT`, `UPDATE`, or `DELETE` when you call `SaveChanges`.

A typical `DbContext` looks like this:

```csharp
using Microsoft.EntityFrameworkCore;

public class AppDbContext : DbContext
{
    // The constructor required for Dependency Injection
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    // Each DbSet represents a table you can query.
    public DbSet<Product> Products { get; set; }
    public DbSet<Order> Orders { get; set; }
    public DbSet<Customer> Customers { get; set; }

    // Optional: Configure logging or specific behavior here if not in DI
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        // Helpful for debugging: Logs SQL to Console
        optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information);
    }
}

```

**Lifetime:** In an [ASP.NET](http://asp.net/) Core application, the `DbContext` is almost always registered with a **`Scoped`** lifetime. This means one `AppDbContext` instance is created per HTTP request and is shared across all services (like repositories) within that request, ensuring data consistency.

---

### 3. Entities (The Models)

Entities are the C# classes that EF Core maps to your database tables. They are simple POCOs (Plain Old C# Objects).

**The Convention over Configuration Principle:**
EF Core is smart. It follows a set of conventions to figure out your database schema without you having to configure every little detail.

- **Table Name:** By default, the table name will be the same as the `DbSet<T>` property name in your `DbContext` (e.g., `Products`).
- **Primary Key:** EF Core will automatically look for a property named `Id` or `[ClassName]Id` (e.g., `ProductId`) and configure it as the primary key.
- **Column Names:** Column names will match the property names.
- **Data Types:** EF Core maps C# types to appropriate SQL types (e.g., `string` -> `nvarchar(max)`, `int` -> `int`, `DateTime` -> `datetime2`).
- **Nullability:** Reference types that are nullable in C# (`string?`) will be nullable in the database. Non-nullable reference types (`string`) will be `NOT NULL`.

**Example Entity:**

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("AppProducts")] // Override Table Name (if different from DbSet)
public class Product
{
    // Convention: 'Id' is automatically detected as the primary key.
    public int Id { get; set; }

    // This will be an 'nvarchar(max)' NOT NULL column.
    [Required]
    [MaxLength(200)] // Good Practice: Limit string length
    public string Name { get; set; }

    // This will be a 'decimal(18,2)' NOT NULL column.
    [Column(TypeName = "decimal(18,2)")] // Explicit SQL Type
    public decimal Price { get; set; }

    // This will be an 'nvarchar(max)' NULL column because of the '?'.
    public string? Description { get; set; }

    // Enums are stored as Int by default (0, 1, 2)
    public ProductStatus Status { get; set; }

    // Navigation Property (covered in Phase 1.5)
    public List<Order> Orders { get; set; } = new();
}

public enum ProductStatus { Active, OutOfStock, Discontinued }

```

---

### 4. Installation and Setup

To get started, you need to install a few NuGet packages and configure the `DbContext` in your `Program.cs`.

**Step 1: Install NuGet Packages**
Open the terminal in your project folder.

```bash
# The core EF Core library
dotnet add package Microsoft.EntityFrameworkCore

# The provider for SQL Server
dotnet add package Microsoft.EntityFrameworkCore.SqlServer

# Tooling for migrations and scaffolding
dotnet add package Microsoft.EntityFrameworkCore.Tools

# Required for generating migrations
dotnet add package Microsoft.EntityFrameworkCore.Design

```

**Step 2: Add Connection String to `appsettings.json`**

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=MyWebAppDb;Trusted_Connection=True;TrustServerCertificate=True;"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information" // See SQL Queries in Logs
    }
  }
}

```

**Step 3: Register `DbContext` in `Program.cs`**
This is where you tell [ASP.NET](http://asp.net/) Core about your `DbContext` and how to connect to the database.

```csharp
// In Program.cs
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// --- DI Container Configuration ---

// 1. Get the connection string from configuration.
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

// 2. Register the DbContext.
// This registers it with a Scoped lifetime by default.
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseSqlServer(connectionString);

    // Development Tip: Enable sensitive data logging to see parameter values in console
    if (builder.Environment.IsDevelopment())
    {
        options.EnableSensitiveDataLogging();
        options.EnableDetailedErrors();
    }
});

builder.Services.AddControllers();

var app = builder.Build();

// ...

```

Your application is now fully wired up. The `AppDbContext` is registered and ready to be injected into your services and controllers.

---

## Phase 1.5: The "Real World" - Relationships & Migrations

---

### 1. Modeling Relationships (Code-First Command Example)

Let's assume you have the `Blog` and `Post` classes from the previous explanation.

**Your Workflow in the Terminal:**

**Step 1: Create the Initial Migration**
You've written your C# classes. Now, you tell EF Core to create the first migration.

```bash
# Ensure you are in the project directory (where .csproj is)
dotnet ef migrations add InitialCreate

```

**What Happens:**

- EF Core analyzes `AppDbContext`, `Blog`, and `Post`.
- It creates a `Migrations` folder.
- Inside, it generates two files:
    1. `_InitialCreate.cs`: Contains the `Up()` method with `CreateTable` commands for `Blogs` and `Posts`, including columns, primary keys, and foreign key constraints.
    2. `AppDbContextModelSnapshot.cs`: A C# representation of your target database schema.

**`_InitialCreate.cs` (Simplified `Up()` method):**

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.CreateTable(
        name: "Blogs",
        columns: table => new
        {
            Id = table.Column<int>(nullable: false).Annotation("SqlServer:Identity", "1, 1"),
            Url = table.Column<string>(nullable: false)
        },
        constraints: table => { table.PrimaryKey("PK_Blogs", x => x.Id); });

    migrationBuilder.CreateTable(
        name: "Posts",
        columns: table => new
        {
            Id = table.Column<int>(nullable: false).Annotation("SqlServer:Identity", "1, 1"),
            Title = table.Column<string>(nullable: false),
            BlogId = table.Column<int>(nullable: false) // The Foreign Key column
        },
        constraints: table =>
        {
            table.PrimaryKey("PK_Posts", x => x.Id);
            table.ForeignKey( // The relationship constraint
                name: "FK_Posts_Blogs_BlogId",
                column: x => x.BlogId,
                principalTable: "Blogs",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade); // If you delete a blog, delete its posts
        });
}

```

**Step 2: Apply the Migration to the Database**
This command reads the migration file and executes the SQL.

```bash
dotnet ef database update

```

**Result:** Your SQL Server now has `Blogs` and `Posts` tables, plus the `__EFMigrationsHistory` table with one entry: `_InitialCreate`. Your code and database are in perfect sync.

---

### 2. Out of Sync Scenario: Manual DB Change Disaster

Let's simulate a common problem. A DBA, unaware of your Code-First workflow, directly modifies the database.

**Step 1: The Manual Change**
The DBA runs this SQL script:

```sql
ALTER TABLE Posts ADD PublishedOn DATETIME2 NOT NULL DEFAULT GETDATE();

```

Now the `Posts` table in the database has a `PublishedOn` column. Your C# `Post` class and your EF Core `Snapshot` **do not know about this.**

**Step 2: The Developer's Change**
You now get a task to add the same feature. You add the property to your `Post` class:

```csharp
public class Post
{
    // ... other properties
    public DateTime PublishedOn { get; set; }
}

```

**Step 3: The Conflict (`add-migration`)**
You try to create a migration for your new property, as you normally would:

```bash
dotnet ef migrations add AddPublishedOnToPost

```

**What happens:** EF Core compares your *new* C# model (with `PublishedOn`) to the *old* `Snapshot` (without `PublishedOn`). It correctly determines that a `PublishedOn` column needs to be added. It generates a migration file with this `Up()` method:

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.AddColumn<DateTime>(
        name: "PublishedOn",
        table: "Posts",
        nullable: false,
        defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));
}

```

**Step 4: The Crash (`database update`)**
You try to apply this migration:

```bash
dotnet ef database update

```

**The application crashes!** You will get a `SqlException` from the database:

> Column 'PublishedOn' in table 'Posts' already exists.
> 

Your migration is trying to add a column that is already physically present in the database. You are out of sync.

### How to Fix It (The "Adopt" Strategy)

Here is the step-by-step recovery process.

**Fix Step 1: "Fake" the Migration Application**
We need to trick EF Core into thinking it has already applied this migration, even though it failed. We do this by generating a SQL script of the migration and manually adding a record to the history table.

Generate the script for your failed migration:

```bash
dotnet ef migrations script AddPublishedOnToPost

```

This will output SQL. The **most important line** is the last one:

```sql
-- This is the only line you need to run
INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
VALUES (N'20231027150000_AddPublishedOnToPost', N'8.0.0');

```

Run this `INSERT` statement directly on your database.

**Result:** The `__EFMigrationsHistory` table now says `AddPublishedOnToPost` was applied. EF Core now "believes" the `PublishedOn` column exists because of its migration.

**Fix Step 2: "Fake" the Snapshot**
Your code is now correct, and your database history is correct, but your `Snapshot` file is still from *before* this migration. We need to regenerate it.

**The "brute-force" but effective way:**

1. Temporarily delete your *latest* migration file (`..._AddPublishedOnToPost.cs`). Do NOT delete the snapshot.
2. Run `add-migration` again with the same name.
EF Core will compare your current C# model to the slightly outdated snapshot. Because you deleted the migration, it will think it needs to create it again. This time, it generates the migration and, crucially, it **updates the Snapshot file to the correct, final state.**
    
    ```bash
    dotnet ef migrations add AddPublishedOnToPost
    
    ```
    

**Your System is Now Synchronized:**

- **Code:** `Post` class has `PublishedOn`.
- **Database:** `Posts` table has `PublishedOn`.
- **History Table:** Contains the `AddPublishedOnToPost` record.
- **Snapshot:** Correctly reflects the model with the `PublishedOn` column.

You can now proceed with your next migration normally.

---

### 3. The Anatomy of a Migration (Up & Down)

When you run `dotnet ef migrations add AddPostTimestamp`, EF Core generates a single file that tells the database how to go **forward** and how to go **backward**.

**File:** `Migrations/20231027160000_AddPostTimestamp.cs`

```csharp
using System;
using Microsoft.EntityFrameworkCore.Migrations;

public partial class AddPostTimestamp : Migration
{
    // The "Forward" Button: Executed when you run 'database update'
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<DateTime>(
            name: "Timestamp",
            table: "Posts",
            nullable: false,
            defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

        // If this migration also created an index, it would be here:
        // migrationBuilder.CreateIndex(...)
    }

    // The "Undo" Button: Executed when you revert (roll back) to a previous migration
    protected override void Down(MigrationBuilder migrationBuilder)
    {
        // This MUST be the exact opposite of Up().
        // Since Up() added the column, Down() must drop it.
        migrationBuilder.DropColumn(
            name: "Timestamp",
            table: "Posts");

        // migrationBuilder.DropIndex(...)
    }
}

```

### **How to Trigger the `Down()` Method (Rolling Back)**

If you made a mistake and want to undo `AddPostTimestamp`, you command EF Core to target the **previous** migration.

**History:**

1. `InitialCreate`
2. `AddPostTimestamp` (Target to undo)

**Command:**

```bash
# Update the database to the state of 'InitialCreate'
dotnet ef database update InitialCreate

```

**Result:** EF Core detects that `AddPostTimestamp` is currently applied but you want to go back to `InitialCreate`. It runs the **`Down()`** method shown above, effectively removing the column from the database. Then you can safely delete the migration file.