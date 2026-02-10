# 3. DbContext in Entity Framework Core

# DbContext in Entity Framework Core

The **DbContext** class is the heart of Entity Framework Core. It acts as the primary coordinator between your .NET application and the underlying database. It represents a “unit of work” and a session with the database, allowing you to query, save, and track changes to your entities.

---

### Core Responsibilities

The `DbContext` handles several critical cross-cutting concerns automatically:

1. **Entity Tracking:** It monitors the state of every object (Added, Modified, Deleted, Unchanged) during its lifetime.
2. **Query Translation:** It uses a database provider to translate your LINQ queries into optimized SQL.
3. **Connection Management:** It manages opening and closing connections to the database.
4. **Transaction Management:** By default, it wraps all operations in `SaveChanges()` into a single atomic transaction.
5. **Caching:** It maintains a “Set of Objects” (First-Level Cache) to avoid redundant database trips during the same context instance.
6. **Concurrency:** It handles conflict detection when multiple users attempt to update the same record simultaneously.

---

### Implementation Example

To create your own data context, you must derive from `Microsoft.EntityFrameworkCore.DbContext` and expose your tables as `DbSet<T>` properties.

### 1. Define the Entities

```csharp
public class Patient
{
    public int Id { get; set; }
    public string Name { get; set; }
    public DateTime DateOfBirth { get; set; }
}

public class Appointment
{
    public int Id { get; set; }
    public DateTime ScheduledDate { get; set; }
    public int PatientId { get; set; } // Foreign Key
}
```

### 2. Create the Custom Context

```csharp
using Microsoft.EntityFrameworkCore;

public class ClinicDbContext : DbContext
{
    // The DbSets represent the tables in your database
    public DbSet<Patient> Patients { get; set; }
    public DbSet<Appointment> Appointments { get; set; }

    // Configuration can be done inside OnModelCreating using Fluent API
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Patient>().HasKey(p => p.Id);
    }
}
```

---

### Context Lifetime Management

In modern .NET applications (like ASP.NET Core), `DbContext` is typically registered in the **Dependency Injection (DI)** container with a **Scoped** lifetime. This means a new context instance is created for every HTTP request and disposed of when the request finishes.

### Registration in `Program.cs`:

```csharp
builder.Services.AddDbContext<ClinicDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
```

---

### Essential Methods & Properties

| Method | Purpose |
| --- | --- |
| **Set()** | Provides access to a specific table as a queryable set. |
| **Add / AddRange** | Begins tracking new objects for insertion. |
| **Update / UpdateRange** | Identifies existing objects whose properties have changed. |
| **Remove / RemoveRange** | Marks objects to be physically deleted from the table. |
| **Find / FindAsync** | Retrieves a single object by its Primary Key (checked in cache first). |
| **SaveChanges / SaveChangesAsync** | Generates SQL and persists all tracked changes to the DB. |
| **ChangeTracker** | Provides granular information about the current state of tracked objects. |
| **Database** | Provides access to raw SQL execution, migrations, and transactions. |

### Summary Best Practices

- **Keep Contexts Lean:** Avoid putting business logic inside the context; keep it focused strictly on data access and mapping.
- **Manage Disposal:** Always ensure the context is disposed of properly (either via DI or a `using` block) to free up database connections.
- **Avoid Global Contexts:** Never use a single static `DbContext` for the entire lifetime of your application, as it will lead to memory leaks and threading issues.