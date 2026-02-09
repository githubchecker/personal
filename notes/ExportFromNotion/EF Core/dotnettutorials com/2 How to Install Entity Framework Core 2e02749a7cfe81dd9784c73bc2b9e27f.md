# 2. How to Install Entity Framework Core

# Installing Entity Framework Core

Entity Framework Core (EF Core) is a highly modular framework. Unlike its predecessor (EF 6), it is not bundled with the .NET runtime. Instead, you only install the specific components your project needs, which reduces the final application size and improves performance.

To use EF Core, you must install two categories of NuGet packages:
1. **A Database Provider:** To connect to a specific database (SQL Server, SQLite, etc.).
2. **EF Core Tools:** To manage migrations and database schema updates.

---

### 1. EF Core Database Providers

The provider package contains the logic to translate LINQ queries into the specific SQL dialect of your database.

| Database | NuGet Package Name |
| --- | --- |
| **SQL Server** | `Microsoft.EntityFrameworkCore.SqlServer` |
| **SQLite** | `Microsoft.EntityFrameworkCore.Sqlite` |
| **PostgreSQL** | `Npgsql.EntityFrameworkCore.PostgreSQL` |
| **MySQL** | `Pomelo.EntityFrameworkCore.MySql` |
| **Cosmos DB** | `Microsoft.EntityFrameworkCore.Cosmos` |
| **In-Memory** | `Microsoft.EntityFrameworkCore.InMemory` (For testing) |

### Installation Commands:

- **Package Manager Console:** `Install-Package <PackageName>`
- **dotNet CLI:** `dotnet add package <PackageName>`

---

### 2. EF Core Tools

The tools package provides the commands needed for design-time tasks such as creating migrations, updating the database schema, or scaffolding code from an existing database.

### The Tools Package

- **NuGet Package:** `Microsoft.EntityFrameworkCore.Tools`
- **Purpose:** Enables PowerShell commands in Visual Studio (e.g., `Add-Migration`, `Update-Database`).

### The .NET CLI Tool (Global/Local)

To use EF Core commands in a terminal (outside Visual Studio), you also need the global tool:

```bash
dotnet tool install --global dotnet-ef
```

---

### Summary of Installation Commands

If you are building an application with **SQL Server**, run these commands in your project directory:

**Option A: Using .NET CLI (Recommended)**

```bash
# Add SQL Server Provider
dotnet add package Microsoft.EntityFrameworkCore.SqlServer

# Add Tools support
dotnet add package Microsoft.EntityFrameworkCore.Design
```

**Option B: Using Package Manager Console (Visual Studio)**

```powershell
# Add SQL Server Provider
Install-Package Microsoft.EntityFrameworkCore.SqlServer

# Add Tools support
Install-Package Microsoft.EntityFrameworkCore.Tools
```

---

### Verifying the Installation

You can verify the successfully installed packages by checking your `.csproj` file. It should contain entries similar to this:

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.x.x" />
  <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.x.x" />
</ItemGroup>
```

Once installed, your environment is ready to define the `DbContext` and start modeling your data.