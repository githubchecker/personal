# 46. Table Per Hierarchy Inheritance in Entity Framework Core

# Table Per Hierarchy (TPH) Inheritance

**Table Per Hierarchy (TPH)** is the default inheritance mapping strategy in EF Core. Under this pattern, an entire inheritance hierarchy is stored in a **single database table**.

---

### Core Concept: The Discriminator

Because multiple classes share one table, EF Core adds a **Discriminator** column. This column stores a value (usually a string) that tells EF Core which class to instantiate for that specific row.

- **Shared Columns:** Properties defined in the base class (e.g., `Amount`, `Date`) are mapped to standard columns.
- **Derived Columns:** Properties unique to derived classes (e.g., `CardNumber`) are also mapped to columns in the same table. These **must** be nullable in the database because they will contain `NULL` for any row representing a different derived type.

---

### Implementation Example: Payment Systems

### 1. Define the Entities

Use an `abstract` base class for shared logic and derived classes for specific implementations.

```csharp
public abstract class Payment
{
    public int Id { get; set; }
    public decimal Amount { get; set; }
    public DateTime Date { get; set; }
}

public class CardPayment : Payment
{
    public string? CardNumber { get; set; } // Must be nullable ?
    public string? CardHolder { get; set; }
}

public class UPIPayment : Payment
{
    public string? UpiId { get; set; }      // Must be nullable ?
}
```

### 2. Configure the Discriminator

While EF Core provides defaults, using Fluent API to explicitly define the discriminator is recommended for clarity.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Payment>()
        .HasDiscriminator<string>("PaymentMethod")
        .HasValue<CardPayment>("CreditCard")
        .HasValue<UPIPayment>("UPI");
}
```

---

### Resulting Database Schema

A single table named `Payments` is created. Notice the “widening” of the table to accommodate all possible properties:

| Id | Amount | Date | **PaymentMethod** | CardNumber | UpiId |
| --- | --- | --- | --- | --- | --- |
| 1 | 150.00 | 2023-10-01 | **CreditCard** | 4111… | NULL |
| 2 | 20.00 | 2023-10-02 | **UPI** | NULL | john@upi |

---

### Operations with TPH

### Reading Data (Polymorphism)

You can query the base type to retrieve all mixed types in a single list. EF Core uses the discriminator to materialize the correct C# objects.

```csharp
// Returns a mixed list of CardPayment and UPIPayment objects
var allPayments = await context.Payments.ToListAsync();

// Use OfType<T> to filter at the database level
var upiOnly = await context.Payments.OfType<UPIPayment>().ToListAsync();
```

### Logic with Pattern Matching

When processing a list of polymorphic results, use C# pattern matching to access type-specific properties.

```csharp
foreach (var p in allPayments)
{
    if (p is CardPayment card)
    {
        Console.WriteLine($"Card Number: {card.CardNumber}");
    }
}
```

---

### Pros and Cons of TPH

| Advantages | Disadvantages |
| --- | --- |
| **Performance:** Fastest strategy as it requires zero JOINs for polymorphic queries. | **Data Density:** Can result in a very “sparse” table with many NULL values. |
| **Simplicity:** Only one table to manage, index, and back up. | **Database Integrity:** Cannot enforce `NOT NULL` constraints on derived properties at the DB level. |
| **Refactoring:** Adding or removing a type is a simple schema change (one column addition). | **Table Width:** Very wide tables can eventually impact storage and scan performance. |

### Summary Recommendation

TPH is the **best choice for most applications**. It offers the highest performance and the simplest database schema. Use it whenever the derived types share many properties or when query performance across all types is a priority.