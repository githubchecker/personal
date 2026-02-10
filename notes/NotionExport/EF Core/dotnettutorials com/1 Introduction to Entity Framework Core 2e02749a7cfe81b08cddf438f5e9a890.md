# 1. Introduction to Entity Framework Core

# Introduction to Entity Framework Core

**Entity Framework Core (EF Core)** is an open-source, lightweight, extensible, and cross-platform version of Microsoft’s Entity Framework data access technology. It is a modern **Object-Relational Mapper (ORM)** that allows .NET developers to interact with databases using .NET objects, significantly reducing the amount of manual data-access code required.

---

### What is an ORM?

**Object-Relational Mapping (ORM)** is a technique used to bridge the gap between the Object-Oriented world (C#, Java) and the Relational Database world (SQL Server, PostgreSQL).

In traditional data access (like ADO.NET), you have to manually map table rows to class objects and write raw SQL strings. An ORM automates this by:
1. **Modeling:** Creating classes that represent database tables.
2. **Mapping:** Linking class properties to table columns.
3. **SQL Generation:** Translating LINQ (C#) queries into optimized SQL.
4. **Tracking:** Monitoring changes to objects and reflecting them in the database upon saving.

---

### Key Features of EF Core

| Feature | Description |
| --- | --- |
| **Cross-Platform** | Runs on Windows, Linux, and macOS. |
| **Provider-Based** | Supports SQL Server, SQLite, MySQL, PostgreSQL, Cosmos DB, and more. |
| **Performance** | Optimized query generation and efficient change tracking. |
| **Migrations** | Automatically manages database schema changes as your code evolves. |
| **LINQ Support** | Write queries in type-safe C# instead of raw SQL strings. |
| **Extensible** | Allows developers to hook into the pipeline for custom behavior. |

---

### Development Workflows

EF Core supports two primary workflows for building your data layer:

### 1. Code-First Approach (Recommended)

You define your domain classes and relationships in C# first. EF Core then generates the database schema automatically based on your code.
* **Best for:** New projects where you want total control over the domain model.
* **Tooling:** Uses “Migrations” to keep the DB in sync with the code.

### 2. Database-First Approach

You start with an existing database. EF Core “reverse engineers” the schema to generate the DbContext and entity classes for you.
* **Best for:** Legacy systems or projects where the database is managed by a separate team of DBAs.
* **Tooling:** Uses the `Scaffold-DbContext` command.

---

### How EF Core Works: The Architecture

1. **Application Code:** Your C# logic and LINQ queries.
2. **DbContext:** The heart of EF Core. It represents a session with the database.
3. **Provider:** A database-specific driver (e.g., `Microsoft.EntityFrameworkCore.SqlServer`) that translates EF Core commands into specific SQL dialects.
4. **Database:** The physical storage (SQL Server, MySQL, etc.).

---

### EF Core vs. EF 6.x

EF Core is a complete rewrite of the older Entity Framework 6. It is not just an update; it is a more modular and performant framework designed for the modern cloud and microservices era.

| Capability | EF 6.x | EF Core |
| --- | --- | --- |
| **Platform** | Windows Only (.NET Framework) | Cross-Platform (.NET Core, 5, 6, 7+) |
| **Performance** | Standard | High (Optimized for speed) |
| **Lazy Loading** | Built-in | Optional (via package) |
| **New Features** | Limited updates | Constant innovation (TPC, JSON support, etc.) |

---

### Prerequisites

To get started with EF Core, you should have a basic understanding of:
1. **C# Programming:** Familiarity with classes, properties, and generics.
2. **Relational Databases:** Understanding of tables, primary keys, and foreign keys.
3. **NuGet:** Basic knowledge of managing packages in .NET.