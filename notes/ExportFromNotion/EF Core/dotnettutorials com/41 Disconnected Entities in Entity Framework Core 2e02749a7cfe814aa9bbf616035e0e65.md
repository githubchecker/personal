# 41. Disconnected Entities in Entity Framework Core

# Disconnected Entities in EF Core

In Entity Framework Core, an entity is **disconnected** when it is no longer being tracked by a `DbContext` instance. This is the standard scenario for modern **Web APIs**, where an entity is fetched, sent to a client as JSON, and then sent back to the server in a separate request (using a new `DbContext` instance).

---

### Connected vs. Disconnected Patterns

| Feature | Connected Pattern | Disconnected Pattern |
| --- | --- | --- |
| **Lifetime** | A single `DbContext` instance tracks the entity from load to save. | Separate `DbContext` instances are used for loading and saving. |
| **Change Tracking** | Automatic. EF Core detects changes to properties via snapshots. | **Manual**. You must explicitly tell EF Core what changed. |
| **Environment** | CLI Tools, Desktop Apps (WPF/WinForms). | **Web APIs (ASP.NET Core)**, Microservices. |

---

### How to Save Disconnected Entities

When you receive an entity from a client, the new `DbContext` instance has no internal history of that object. You must re-attach it and specify its state.

### 1. The `Update` Method

The most common approach. EF Core marks the entity as `Modified`. If the entity has navigation properties (related objects), EF Core recursively marks them as `Modified` (if they have a Primary Key) or `Added` (if they don’t).

```csharp
public void UpdateStudent(Student student)
{
    using var context = new MyDbContext();
    // Tells EF "this object exists in the DB, please update all columns"
    context.Update(student);
    context.SaveChanges();
}
```

### 2. The `Attach` Method

Re-attaches an entity in the `Unchanged` state. This is useful when you only want to update specific properties rather than the entire row.

```csharp
context.Attach(student);
// Only name will be included in the UPDATE SQL statement
context.Entry(student).Property(s => s.FirstName).IsModified = true;
context.SaveChanges();
```

### 3. Manual State Management

Setting the `State` property directly gives you absolute control over the operation.

```csharp
context.Entry(student).State = EntityState.Deleted; // Marks for deletion
context.SaveChanges();
```

---

### Comparison of Re-attachment Methods

| Method | Database Operation | Entity State |
| --- | --- | --- |
| **`Add()`** | `INSERT` | `Added` |
| **`Update()`** | `UPDATE` | `Modified` |
| **`Remove()`** | `DELETE` | `Deleted` |
| **`Attach()`** | None (initially) | `Unchanged` |

---

### Logic for Generic Scenarios

In many applications, a single “Save” method handles both new and existing records by checking for a primary key:

```csharp
public void Save(Student student)
{
    using var context = new MyDbContext();

    // If ID is 0, it's a new record
    if (student.StudentId == 0)
    {
        context.Add(student);
    }
    else // Otherwise, it's an existing record
    {
        context.Update(student);
    }

    context.SaveChanges();
}
```

### Best Practices

- **Security**: Never trust the ID sent by the client blindly. Validate that the user has permission to modify the entity with that specific ID.
- **Performance**: `context.Update()` generates a SQL statement that updates **every** column. For entities with many columns, prefer `Attach` + specific property modification to improve performance.
- **Concurrency**: Use `Timestamp` or `RowVersion` columns to ensure that save operations on disconnected entities don’t overwrite changes made by other users in the meantime.