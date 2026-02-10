# 48. Table Per Concrete Type Inheritance in Entity Framework Core

# Table Per Concrete Type (TPC) Inheritance

**Table Per Concrete Type (TPC)** is an inheritance strategy introduced in **EF Core 7.0**. Under this pattern, **every non-abstract class in the hierarchy is mapped to its own separate table**, and each table contains every property belonging to that class—including those inherited from the base.

---

### How TPC Works

TPC acts as a middle ground between TPH and TPT:
* **Standalone Tables:** Each concrete class has a full, standalone table containing all relevant data.
* **No Base Table:** The abstract base class does not exist in the database.
* **No Joins:** Querying for a specific type is extremely efficient because all properties are in a single table (unlike TPT).
* **No Sparse Columns:** There are no “junk” nullable columns from other derived types (unlike TPH).

---

### Implementation Example: Billing System

### 1. Define the Entities

Mark the base class as `abstract` to prevent EF Core from attempting to create a table for it.

```csharp
public abstract class Invoice
{
    public int Id { get; set; }
    public decimal Amount { get; set; }
    public DateTime BillingDate { get; set; }
}

public class UtilityBill : Invoice
{
    public string MeterNumber { get; set; }
}

public class SubscriptionService : Invoice
{
    public string ServiceName { get; set; }
}
```

### 2. Configure TPC Mapping

Use the `UseTpcMappingStrategy()` method on the base entity in your `OnModelCreating` override.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Invoice>().UseTpcMappingStrategy();
}
```

---

### Critical: Managing Primary Keys

In TPC, if you use standard `Identity` columns, each table will independently generate IDs starting from 1. This would cause ID collisions across the hierarchy, breaking polymorphic relationships.

**The Solution: Database Sequences**
You must configure a shared sequence so that every table in the hierarchy pulls from the same pool of unique IDs.

```csharp
// 1. Create the sequence
modelBuilder.HasSequence<int>("InvoiceIds");

// 2. Configure the base property to use it
modelBuilder.Entity<Invoice>()
    .UseTpcMappingStrategy()
    .Property(e => e.Id)
    .HasDefaultValueSql("NEXT VALUE FOR InvoiceIds");
```

---

### Query Behavior

- **Specific Queries:** `context.UtilityBills.ToList()` is a simple `SELECT * FROM UtilityBills`. No joins are needed.
- **Polymorphic Queries:** `context.Invoices.ToList()` results in a `UNION ALL` query that combines results from all concrete tables.

---

### Pros and Cons of TPC

| Advantages | Disadvantages |
| --- | --- |
| **High Performance:** Queries for specific derived types are as fast as standard non-inherited queries. | **Schema Redundancy:** Common columns (like `Amount`) are duplicated across multiple tables. |
| **Database Integrity:** You can use `NOT NULL` constraints on all properties without sparse table issues. | **PK Complexity:** Requires manual configuration of shared database sequences to avoid ID collisions. |
| **Cleaner Schema:** Avoids the “giant table” problem of TPH while avoiding the “join penalty” of TPT. | **Migration Overhead:** Adding a property to the base class generates schema changes for every derived table. |

### Summary Recommendation

TPC is an excellent choice for **EF Core 7+ and 8+** applications where derived types have significant differences but share common metadata. It offers the best balance of query performance and database normalization, provided you are comfortable managing shared Primary Key sequences.