# 49. Transactions in Entity Framework Core

# Transactions in EF Core

A **Transaction** ensures that a group of database operations is treated as a single, atomic unit of work. This follows the **ACID** principle: either all operations succeed and are committed together, or if any part fails, the entire set is rolled back, leaving the database in its original state.

---

### 1. Implicit Transactions (Default Behavior)

By default, every call to `context.SaveChanges()` is automatically wrapped in a transaction by EF Core. If any single update, insert, or delete within that call fails, the entire batch is rolled back.

```csharp
context.Orders.Add(newOrder);
context.OrderItems.AddRange(items);
// Both additions are automatically saved within a single transaction
await context.SaveChangesAsync();
```

---

### 2. Manual Transactions (Explicit Control)

You should use manual transactions if your workflow requires:
* Multiple separate calls to `SaveChangesAsync()`.
* A mix of EF Core operations and raw SQL commands within one unit of work.
* The need to commit data based on external logic results.

```csharp
// Use BeginTransactionAsync for non-blocking I/O
using var transaction = await context.Database.BeginTransactionAsync();

try
{
    // Operation 1
    context.Orders.Add(newOrder);
    await context.SaveChangesAsync();

    // Operation 2: Custom logic or raw SQL
    await context.Database.ExecuteSqlInterpolatedAsync($"UPDATE Inventory SET Stock = Stock - 1 WHERE Id = {prodId}");

    // Finalize all operations
    await transaction.CommitAsync();
}
catch (Exception)
{
    // Undo all changes in this block
    await transaction.RollbackAsync();
}
```

---

### 3. Distributed Transactions (`TransactionScope`)

When your unit of work spans **multiple DbContext instances** (pointing to different databases), use the `TransactionScope` class. This provides a “manager” that coordinates the commit across different resources.

```csharp
using var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled);

// DB 1: Shared transaction
using (var db1 = new OrderContext()) { db1.Orders.Add(o); await db1.SaveChangesAsync(); }

// DB 2: Shared transaction
using (var db2 = new AuditContext()) { db2.Logs.Add(l); await db2.SaveChangesAsync(); }

scope.Complete(); // Marks both operations as successful
```

---

### Isolation Levels

You can control the lock-level of a transaction by specifying an `IsolationLevel`. This prevents issues like **Dirty Reads** (reading uncommitted data from other users).

```csharp
using var tx = await context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
```

---

### Best Practices

1. **Keep it Brief:** Hold transactions open for the shortest time possible to avoid row locking and deadlocks.
2. **Prefer Async:** Always use `SaveChangesAsync()`, `CommitAsync()`, and `RollbackAsync()` in Web APIs to maintain high scalability.
3. **Scoped Contexts:** For most web apps, avoid `TransactionScope` unless actually spanning multiple databases. A single `DbContext` per request is usually sufficient.
4. **Idempotency:** Ensure that if a transaction fails and is retried, it doesn’t create duplicate records (especially in payment processing).