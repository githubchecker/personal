# Phase 3: Saving and Changing Data

Of course. This phase is about the CUD part of CRUD (Create, Update, Delete). While querying is about reading, this is about modifying the state of your database. The key to mastering this is understanding EF Core's "Change Tracker."

---

### **1. The Change Tracker (EF Core's "Memory")**

The `DbContext` is not just a query tool; it's a state management system. Every time you fetch an entity from the database using a normal query (i.e., without `AsNoTracking()`), the `DbContext` keeps a "snapshot" of its original values. This is called **tracking**.

**The States of an Entity:**
The Change Tracker assigns a state to every entity it knows about:

- **`Detached`**: The `DbContext` is not aware of this entity. (e.g., a new DTO from an API request).
- **`Unchanged`**: The entity has been loaded from the DB, and its property values have not been modified.
- **`Modified`**: The entity has been loaded, and at least one of its property values has changed.
- **`Added`**: The entity is new and has been marked for insertion into the database.
- **`Deleted`**: The entity exists in the database but has been marked for deletion.

When you call `SaveChanges()`, the `DbContext` scans all tracked entities and generates the appropriate SQL for any entity that is **not** in the `Unchanged` state.

---

### **2. Adding, Updating, and Deleting Data**

### **Adding a New Record (`Added` state)**

This is the most straightforward operation. You create a new instance of your C# entity, add it to the `DbSet`, and save.

**Example: Creating a new Product**

```csharp
[HttpPost]
public async Task<IActionResult> CreateProduct([FromBody] CreateProductDto dto)
{
    // 1. Create a new entity instance. It is currently 'Detached'.
    var newProduct = new Product
    {
        Name = dto.Name,
        Price = dto.Price,
        IsAvailable = true
    };

    // 2. Add it to the DbSet. The Change Tracker now marks its state as 'Added'.
    _context.Products.Add(newProduct);

    // 3. SaveChanges() sees the 'Added' entity and generates an INSERT statement.
    await _context.SaveChangesAsync();

    // After SaveChanges, EF Core receives the new ID from the database
    // and updates the 'newProduct.Id' property.
    return CreatedAtAction("GetById", new { id = newProduct.Id }, newProduct);
}

```

### **Updating an Existing Record (`Modified` state)**

There are two main scenarios for updating.

**Scenario A: The "Connected" Update (Read then Modify)**
This is the standard and safest way. You load the entity, modify it, and save.

```csharp
[HttpPut("{id}")]
public async Task<IActionResult> UpdateProduct(int id, [FromBody] UpdateProductDto dto)
{
    // 1. LOAD: Fetch the entity. It is now 'Unchanged'.
    var product = await _context.Products.FindAsync(id);

    if (product == null) return NotFound();

    // 2. MODIFY: Change its properties in memory. The Change Tracker
    // compares the new values to its snapshot and automatically sets the state to 'Modified'.
    product.Name = dto.Name;
    product.Price = dto.Price;

    // 3. SAVE: SaveChanges() sees the 'Modified' state and generates an
    // UPDATE statement for only the changed properties.
    await _context.SaveChangesAsync();

    return NoContent(); // 204 No Content is standard for a successful PUT
}

```

**Scenario B: The "Disconnected" Update (No Read)**
This is common in web APIs where you receive a DTO and want to update a record without first fetching it. You tell EF Core to "attach" an object and treat it as modified.

```csharp
[HttpPut("{id}")]
public async Task<IActionResult> UpdateProductDisconnected(int id, [FromBody] UpdateProductDto dto)
{
    // Create an entity with the ID from the route and data from the DTO.
    // It is currently 'Detached'.
    var productToUpdate = new Product
    {
        Id = id,
        Name = dto.Name,
        Price = dto.Price
    };

    // 'Update()' tells the Change Tracker: "I don't care what's in the DB.
    // Mark this entire entity as 'Modified'."
    _context.Products.Update(productToUpdate);

    // SaveChanges() generates an UPDATE statement that sets ALL properties of the entity,
    // which can be inefficient if only one field changed.
    await _context.SaveChangesAsync();

    return NoContent();
}

```

- **Warning:** The `Update()` method is less efficient and can be risky if your DTO doesn't include all properties, as it might overwrite existing fields with default values.

### **Deleting a Record (`Deleted` state)**

Similar to a connected update, you must first load the entity to mark it for deletion.

```csharp
[HttpDelete("{id}")]
public async Task<IActionResult> DeleteProduct(int id)
{
    // 1. LOAD: Fetch the entity to be deleted.
    var product = await _context.Products.FindAsync(id);

    if (product == null) return NotFound();

    // 2. MARK FOR DELETION: The Change Tracker sets its state to 'Deleted'.
    _context.Products.Remove(product);

    // 3. SAVE: SaveChanges() sees the 'Deleted' state and generates a DELETE statement.
    await _context.SaveChangesAsync();

    return NoContent();
}

```

*Note: For batch deletions, `ExecuteDeleteAsync()` (covered later) is far more performant.*

---

### **3. `SaveChanges()` and `SaveChangesAsync()` (The Transaction)**

This method is the heart of CUD operations. When you call `SaveChanges()`:

1. **Begins a Transaction:** EF Core automatically starts a database transaction.
2. **Inspects Tracker:** It looks at all tracked entities.
3. **Generates SQL:** It generates the necessary `INSERT`, `UPDATE`, and `DELETE` statements.
4. **Executes Batch:** It sends these statements to the database as a single command batch.
5. **Commits/Rolls Back:**
    - If the database successfully executes all commands, EF Core commits the transaction.
    - If **any** command fails, EF Core rolls back the entire transaction. All changes are undone.

This transactional behavior is crucial for data integrity. If you are saving a new `Order` and its `OrderLineItems`, `SaveChanges` ensures that you don't end up with an order that has no items. Either everything succeeds, or everything fails.

---

### **Summary of Phase 3**

- The **Change Tracker** is EF Core's brain, tracking the state of your entities.
- **`Add()`**, **`Update()`**, and **`Remove()`** are methods that tell the Change Tracker to change an entity's state.
- **`SaveChanges()`** is the method that inspects the states and executes the actual SQL inside a **transaction**.
- **Connected** updates (load then modify) are generally safer and more efficient than **disconnected** updates.

## Bulk Update and Delete Optimizations

Of course. You're pointing to one of the most significant performance enhancements in modern EF Core. Before EF7, updating a batch of records was inefficient. The new `ExecuteUpdate` and `ExecuteDelete` methods completely change the game.

Let's do a deep dive, comparing the "old way" with the new, efficient "batch way."

---

### **The "Old Way": The `SaveChanges` Loop (Inefficient)**

Before EF Core 7, if you wanted to update all products in a certain category, you had to perform these steps:

1. **LOAD:** Execute a `SELECT` statement to pull all matching products from the database into the `DbContext`'s memory.
2. **TRACK:** The `DbContext`'s Change Tracker would start monitoring each of these loaded entities.
3. **MODIFY:** Loop through each entity in your C# code and change its property. The Change Tracker marks each one as `Modified`.
4. **SAVE:** Call `SaveChanges()`. EF Core's Change Tracker inspects every tracked entity, finds the ones marked `Modified`, and generates a separate `UPDATE` statement **for each individual entity**.

**The Code (The "Slow" Way):**

```csharp
[HttpPost("old-way-discount")]
public async Task<IActionResult> ApplyDiscountTheOldWay(string category)
{
    // 1. LOAD: Sends a SELECT query to the database.
    // If 1000 products match, 1000 objects are loaded into RAM.
    var productsToUpdate = await _context.Products
        .Where(p => p.Category == category)
        .ToListAsync();

    // 3. MODIFY: Loop in C# code.
    foreach (var product in productsToUpdate)
    {
        product.Price *= 0.9m; // Apply a 10% discount
    }

    // 4. SAVE: Sends 1000 separate UPDATE statements to the database.
    // UPDATE Products SET Price = @p0 WHERE Id = @p1
    // UPDATE Products SET Price = @p0 WHERE Id = @p2
    // ... (1000 times)
    int recordsAffected = await _context.SaveChangesAsync();

    return Ok($"{recordsAffected} products were updated.");
}

```

**The Problems:**

- **High Memory Usage:** You have to load every single entity into memory, even if you only want to change one field.
- **High Network Chattiness:** Sending thousands of individual `UPDATE` statements is slow and puts a heavy load on the database server.

---

### **The "New Way": `ExecuteUpdate` (The Batch Method - EF Core 7+)**

The `ExecuteUpdate` method bypasses the Change Tracker entirely. It translates your LINQ `Where` clause directly into the `WHERE` clause of a single SQL `UPDATE` statement.

**Concept:** Instead of bringing the data to the application to change it, you send the change instruction directly to the database.

**The Workflow:**

1. **DEFINE:** Use a LINQ query to specify *which rows* to update.
2. **EXECUTE:** Chain the `.ExecuteUpdateAsync()` method, providing the changes to be made.
3. **TRANSLATE:** EF Core generates a **single SQL `UPDATE` statement** and sends it to the database.

**The Code (The "Fast" Way):**

```csharp
[HttpPost("new-way-discount")]
public async Task<IActionResult> ApplyDiscountWithExecuteUpdate(string category)
{
    // 1. DEFINE the filter. No data is loaded from the DB.
    var query = _context.Products.Where(p => p.Category == category);

    // 2. EXECUTE the batch update.
    int recordsAffected = await query.ExecuteUpdateAsync(setters => setters
        // For each matching product, set its Price property to the new value.
        .SetProperty(p => p.Price, p => p.Price * 0.9m)
        // You can set multiple properties at once.
        .SetProperty(p => p.LastUpdated, DateTime.UtcNow)
    );

    // EF Core generates a single, efficient SQL statement:
    // UPDATE [p]
    // SET [p].[Price] = [p].[Price] * 0.9, [p].[LastUpdated] = GETUTCDATE()
    // FROM [Products] AS [p]
    // WHERE [p].[Category] = @category

    return Ok($"{recordsAffected} products were updated in a single batch.");
}

```

**Key Advantages:**

- **Extremely Low Memory Usage:** No entities are ever loaded into your application's memory.
- **Blazing Fast:** A single, optimized SQL statement is sent to the database. The performance difference is astronomical for large updates (milliseconds vs. many seconds).
- **No Change Tracker:** You don't need to call `SaveChanges()`. The method executes immediately.

---

### **`ExecuteDelete` (The Batch Delete Method)**

This works exactly the same way as `ExecuteUpdate`, but for deletions.

**The "Old Way" (Slow):**

```csharp
// 1. LOAD all logs older than 30 days.
var oldLogs = await _context.Logs.Where(l => l.Timestamp < DateTime.UtcNow.AddDays(-30)).ToListAsync();

// 2. REMOVE them from the change tracker.
_context.Logs.RemoveRange(oldLogs);

// 3. SAVE: Sends N individual DELETE statements.
await _context.SaveChangesAsync();

```

**The "New Way" with `ExecuteDelete` (Fast):**

```csharp
[HttpPost("cleanup-logs")]
public async Task<IActionResult> CleanupOldLogs()
{
    // Define which logs to delete.
    var query = _context.Logs.Where(l => l.Timestamp < DateTime.UtcNow.AddDays(-30));

    // Execute as a single batch DELETE statement.
    int recordsAffected = await query.ExecuteDeleteAsync();

    // EF Core generates:
    // DELETE FROM [l]
    // FROM [Logs] AS [l]
    // WHERE [l].[Timestamp] < DATEADD(day, -30, GETUTCDATE())

    return Ok($"{recordsAffected} old logs were deleted.");
}

```

---

### **Important Considerations and Limitations**

1. **Bypasses Change Tracker:** This is a key feature, but also a warning. `ExecuteUpdate` does not automatically update any entities that are already loaded in your `DbContext`'s memory. The in-memory objects will become stale. It's best to use this method in a fresh `DbContext` scope where no related entities are being tracked.
2. **No Concurrency Tokens:** These methods currently do not honor concurrency tokens (`[Timestamp]`), as no entities are loaded to check the token against.
3. **Database-Side Logic Only:** The logic you provide in `SetProperty` must be translatable to SQL. You can't call a C# helper method inside it. For example, `p => p.Price * 0.9m` works, but `p => MyCSharpHelper.CalculateDiscount(p.Price)` will fail.

**Verdict:** For any bulk CUD (Create, Update, Delete) operation, the `ExecuteUpdate` and `ExecuteDelete` methods are the modern, high-performance, and recommended approach in EF Core 7 and newer.