# 6. Entity States in Entity Framework Core

# Entity States and Change Tracking in EF Core

The **Change Tracker** is the internal heart of Entity Framework Core. It monitors every entity retrieved or added to the `DbContext` and keeps track of its current “status.” This status, known as the **EntityState**, determines exactly which SQL command EF Core will generate when you call `SaveChanges()`.

---

### The 1. The 5 Possible Entity States

Every entity managed by a context is in exactly one of the following five states:

| EntityState | Description | SaveChanges Action |
| --- | --- | --- |
| **Added** | The object is new to the context and does not exist in the database. | Executes `INSERT` |
| **Unchanged** | The object has been loaded and no properties have been modified. | Does nothing |
| **Modified** | One or more properties of the loaded object have been changed. | Executes `UPDATE` |
| **Deleted** | The object exists in the database but is marked for removal. | Executes `DELETE` |
| **Detached** | The object is not being monitored by the `DbContext`. | Does nothing |

---

### 2. How Change Tracking Works (Snapshot Tracking)

By default, EF Core uses **Snapshot Tracking**:
1. **Capture:** When an entity is retrieved via a query, EF Core takes a “snapshot” of its original property values.
2. **Compare:** When `SaveChanges()` is called, EF Core compares the current values of the object against the original snapshot.
3. **Detect:** If values differ, the state is automatically set to `Modified`. If no changes are found, it remains `Unchanged`.

---

### 3. Practical State Transitions

### Insertion: `Added`

```csharp
var branch = new Branch { Name = "Health" }; // Initial State: Detached
context.Branches.Add(branch);               // Current State: Added
await context.SaveChangesAsync();            // Post-Save State: Unchanged
```

### Update: `Modified`

In a connected scenario, change detection is automatic.

```csharp
var branch = await context.Branches.FirstAsync(); // Initial State: Unchanged
branch.Name = "Emergency Services";              // Current State: Modified
await context.SaveChangesAsync();                 // Post-Save State: Unchanged
```

### Deletion: `Deleted`

```csharp
var branch = await context.Branches.FirstAsync();
context.Branches.Remove(branch);      // Current State: Deleted
await context.SaveChangesAsync();      // Post-Save State: Detached
```

---

### 4. Advanced: Manual State Management

In disconnected scenarios (like Web APIs), you may receive an object from the client that the context is not tracking. You can force a specific state:

```csharp
var userUpdate = new User { Id = 10, Email = "new@example.com" };

// Option A: Attach and track as modified
context.Entry(userUpdate).State = EntityState.Modified;

// Option B: Mark a single property as modified
context.Users.Attach(userUpdate);
context.Entry(userUpdate).Property(u => u.Email).IsModified = true;
```

---

### 5. Performance Tuning: `AsNoTracking`

For operations that only read data (e.g., generating a report or a list), tracking is unnecessary overhead. Disabling it improves performance and reduces memory usage because EF Core won’t create original snapshots.

```csharp
var reportData = await context.Products
    .AsNoTracking()
    .Where(p => p.Price > 100)
    .ToListAsync(); // State: Detached
```

---

### Summary Checklist

| Context Scenario | Best Action |
| --- | --- |
| **Querying for Read only** | Use `.AsNoTracking()`. |
| **Updating single entity** | Retrieve, change property, call `SaveChanges()`. |
| **Re-saving external data** | Use `context.Update()` or set `State = Modified`. |
| **Checking current state** | Use `context.Entry(entity).State`. |