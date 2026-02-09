# 43. Disconnected Entity Graph in Entity Framework Core

# Handling Disconnected Entity Graphs

An **Entity Graph** is a cluster of related entities that form a tree or graph structure (e.g., a `Student` containing their `Standard`, `Address`, and `Enrollments`). In disconnected scenarios like Web APIs, you often receive an entire graph in a single JSON payload and must correctly persist changes across multiple tables in one operation.

---

### Default Re-attachment Behavior

When you call a state-changing method on the **root entity** of a disconnected graph, EF Core recursively applies a state to the entire reachable graph.

| Method | Root State | Child (with PK) | Child (no PK) |
| --- | --- | --- | --- |
| **`Add()`** | `Added` | `Added` | `Added` |
| **`Update()`** | `Modified` | `Modified` | `Added` |
| **`Attach()`** | `Unchanged` | `Unchanged` | `Added` |

> Critical Note: context.Update(student) is often too aggressive for complex graphs. If the student object contains a reference to a Standard (class), EF Core will attempt to execute an UPDATE on the Standards table as well, even if nothing changed.
> 

---

### Granular Control with `TrackGraph`

The `ChangeTracker.TrackGraph` method is the professional solution for handling disconnected graphs. It traverses the entire graph and executes a custom callback for **every individual node**, allowing you to decide the state per entity.

### Scenario: Smart Upsert

A common requirement is to treat entities with Primary Keys as existing (`Unchanged` or `Modified`) and those without as new (`Added`).

```csharp
context.ChangeTracker.TrackGraph(student, node =>
{
    // node.Entry.IsKeySet is true if the Primary Key is assigned
    if (node.Entry.IsKeySet)
    {
        node.Entry.State = EntityState.Unchanged;
    }
    else
    {
        node.Entry.State = EntityState.Added;
    }
});
```

---

### Advanced Logic: Entity-Specific Rules

You can implement complex business rules by checking the type of the entity currently being traversed:

```csharp
context.ChangeTracker.TrackGraph(studentGraph, node =>
{
    var entry = node.Entry;

    if (entry.Entity is Student)
    {
        // Students are always modified if they have an ID
        entry.State = entry.IsKeySet ? EntityState.Modified : EntityState.Added;
    }
    else if (entry.Entity is Standard)
    {
        // Standards are read-only lookup data; never update them
        entry.State = EntityState.Unchanged;
    }
    else
    {
        // Everything else defaults to simple check
        entry.State = entry.IsKeySet ? EntityState.Unchanged : EntityState.Added;
    }
});
```

---

### Best Practices

1. **Beware of Reference Data**: If your graph includes “lookup” entities (e.g., `City`, `Currency`), ensure they are attached as `Unchanged`. If you accidentally mark them as `Added` or `Modified`, you risk `Duplicate Key` errors or unintended data changes.
2. **Avoid Deep Nesting**: Large graphs increase complexity and performance overhead. In modern Web APIs, prefer flatter DTOs and handle updates to child collections as separate, specific service calls.
3. **Identity Columns**: When using `Add()`, ensure you aren’t manually setting IDs for database-generated columns, as this will result in runtime exceptions.
4. **Concurrency**: Always use a Concurrency Token (like `RowVersion`) when performing mass updates on a disconnected graph to prevent overwriting other users’ changes.