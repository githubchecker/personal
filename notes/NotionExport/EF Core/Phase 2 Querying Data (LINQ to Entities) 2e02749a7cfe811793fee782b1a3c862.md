# Phase 2: Querying Data (LINQ to Entities)

*(Microsoft Docs Entry Point: [Querying Data in EF Core](https://learn.microsoft.com/en-us/ef/core/querying/))*

The primary way you'll query your database with EF Core is through **LINQ (Language Integrated Query)**. EF Core's LINQ provider is a sophisticated translator that converts your C# query expressions into efficient SQL.

---

### **1. Basic Queries with LINQ**

To run these examples, assume we have a `ProductsController` with an `AppDbContext` injected.

```csharp
[ApiController]
[Route("[controller]")]
public class ProductsController : ControllerBase
{
    private readonly AppDbContext _context;

    public ProductsController(AppDbContext context)
    {
        _context = context;
    }
    // ... actions go here
}

```

### **Core Methods:**

- **`Where()`**: Filters data based on a condition (translates to a `WHERE` clause).
- **`OrderBy()` / `OrderByDescending()`**: Sorts data (translates to `ORDER BY`).
- **`Select()`**: Shapes the output (translates to selecting specific columns).

### **Execution Methods (Causes the query to run):**

- **`ToList()` / `ToListAsync()`**: Executes the query and returns a list of results.
- **`First()` / `FirstOrDefault()`**: Executes and returns the *first* matching item. `First()` throws an exception if nothing is found; `FirstOrDefault()` returns `null`.
- **`Single()` / `SingleOrDefault()`**: Executes and returns the *only* matching item. Throws an exception if zero or *more than one* item is found. `SingleOrDefault()` returns `null` if zero are found but still throws if more than one is found.

**Example: Finding and Sorting Products**

```csharp
[HttpGet]
public async Task<IActionResult> GetAvailableProducts(string searchTerm)
{
    // Build the query. NO database call has been made yet.
    var query = _context.Products
        .Where(p => p.IsAvailable && p.Name.Contains(searchTerm))
        .OrderBy(p => p.Price);

    // EXECUTE the query against the database.
    var products = await query.ToListAsync();

    return Ok(products);
}

```

---

### **2. Deferred Execution (A Critical Concept)**

EF Core **defers execution** of your query. In the example above, the line `var query = ...` does **not** hit the database. It simply builds an *Expression Tree* in memory.

The SQL query is only generated and sent to the database when you call an execution method like `ToListAsync()`, `FirstOrDefaultAsync()`, or when you iterate over the query in a `foreach` loop.

**Why is this important?**
It allows you to build up a complex query dynamically.

**Example: Dynamic Filtering**

```csharp
[HttpGet("search")]
public async Task<IActionResult> Search(string? name, decimal? maxPrice)
{
    // Start with the base query
    IQueryable<Product> query = _context.Products;

    // Dynamically add WHERE clauses
    if (!string.IsNullOrEmpty(name))
    {
        query = query.Where(p => p.Name.Contains(name));
    }
    if (maxPrice.HasValue)
    {
        query = query.Where(p => p.Price <= maxPrice.Value);
    }

    // The final SQL will only include the WHERE clauses that were added.
    var results = await query.ToListAsync();
    return Ok(results);
}

```

---

### **3. Loading Related Data (Joins)**

By default, EF Core does **not** load related entities. If you load a `Blog`, its `Posts` collection will be empty. You must explicitly tell EF Core to load them.

---

### **1. Eager Loading (`.Include()` and `.ThenInclude()`)**

This is the **default, recommended, and most explicit** way to load related data.

- **Concept:** You tell EF Core exactly what related data you need *at the time you write the query*.
- **How it Works:** EF Core generates a single, often complex, SQL query with `JOIN` statements to pull all the requested data from the database in one roundtrip.
- **Pros:**
    - **Efficient:** All data is retrieved in a single database call, preventing the N+1 problem.
    - **Explicit:** The code clearly states its data requirements. There are no surprises.
- **Cons:**
    - Can lead to very large queries ("Cartesian Explosion") if you include many one-to-many relationships, potentially fetching a lot of redundant parent data.

### **Code Example (Recap)**

To get a Blog, all of its Posts, and each Post's Tags:

```csharp
[HttpGet("blogs/{id}")]
public async Task<IActionResult> GetBlogWithPostsAndTags(int id)
{
    var blog = await _context.Blogs
        .Include(b => b.Posts)         // Eagerly load the Posts collection
            .ThenInclude(p => p.Tags)  // For each Post, also load its Tags
        .AsNoTracking() // Good practice for read-only queries
        .FirstOrDefaultAsync(b => b.Id == id);

    if (blog == null) return NotFound();

    // The entire object graph (Blog -> Posts -> Tags) is fully populated.
    return Ok(blog);
}

```

---

### **2. Explicit Loading**

This method is useful when you have already loaded an entity and you **later decide** you need some of its related data.

- **Concept:** You load the parent entity first. Later, in a separate piece of code, you explicitly issue another query to load a specific navigation property for that entity.
- **How it Works:** It uses the `_context.Entry(entity).Collection()` or `_context.Entry(entity).Reference()` methods. The entity must be tracked by the `DbContext`.
- **Pros:**
    - **Conditional Loading:** You only load the related data if you actually need it (e.g., based on an `if` condition), saving bandwidth if it's not needed.
- **Cons:**
    - **Multiple Database Roundtrips:** It always results in at least two separate queries to the database.

### **Code Example**

Imagine a scenario where you only load a blog's posts if a specific query parameter is true.

```csharp
[HttpGet("blogs/{id}/conditional")]
public async Task<IActionResult> GetBlogConditionally(int id, bool includePosts = false)
{
    // Query 1: Get the parent blog.
    // The entity is now being TRACKED by the DbContext.
    var blog = await _context.Blogs.FindAsync(id);

    if (blog == null) return NotFound();

    if (includePosts)
    {
        // "For this specific 'blog' entity, please go back to the database
        // and populate its 'Posts' collection."
        // Query 2: A separate query is sent to the database.
        // SQL generated: SELECT * FROM Posts WHERE BlogId = @p0
        await _context.Entry(blog)
            .Collection(b => b.Posts)
            .LoadAsync();
    }

    // If includePosts is true, blog.Posts is now populated.
    // If false, it remains empty.
    return Ok(blog);
}

```

---

### **3. Lazy Loading**

This is a powerful but dangerous feature that can lead to severe performance problems if not used carefully. It is **generally discouraged** in web applications.

- **Concept:** The related data is transparently loaded from the database the **first time you access the navigation property**.
- **How it Works:** It requires two things:
    1. **Proxies:** You install the `Microsoft.EntityFrameworkCore.Proxies` package and use `.UseLazyLoadingProxies()` in your `DbContext` configuration.
    2. **Virtual Properties:** All navigation properties in your entities must be marked as `virtual`. EF Core will then create a dynamic proxy class at runtime that overrides these properties to add the database-loading logic.
- **Pros:**
    - **Convenience:** The code "just works." You don't have to think about `Include` statements.
- **Cons:**
    - **The N+1 Query Problem:** This is the killer. If you load 10 blogs and then loop through them to display each blog's title, you will execute **11 database queries** (1 for the blogs, and 1 for each of the 10 posts).
    - **Hidden Performance Costs:** It's not obvious from the code when a database query is being triggered. A simple property access can hide a slow network call.
    - **Serialization Issues:** If you return an entity with lazy-loading enabled from an API, the JSON serializer might try to access every property, triggering a cascade of database queries and potentially trying to serialize your entire database.

### **Setup and Code Example**

**Step 1: Configure `DbContext`**

```csharp
// Install: dotnet add package Microsoft.EntityFrameworkCore.Proxies
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString)
           .UseLazyLoadingProxies()); // Enable the feature

```

**Step 2: Modify Entities**
Navigation properties **must** be `virtual`.

```csharp
public class Blog
{
    public int Id { get; set; }
    public string Url { get; set; }

    // Must be virtual for lazy loading to work.
    public virtual ICollection<Post> Posts { get; set; }
}

```

**Step 3: The Dangerous Code (N+1 Problem)**

```csharp
[HttpGet("blogs/lazy")]
public async Task<IActionResult> GetBlogsAndPostsLazy()
{
    // --- QUERY 1 ---
    // SQL: SELECT * FROM Blogs
    var blogs = await _context.Blogs.ToListAsync();

    // Imagine this is in a Razor view or some other logic
    foreach (var blog in blogs)
    {
        // DANGER: The first time this line is hit for EACH blog,
        // a NEW query is sent to the database.
        // --- QUERY 2, 3, 4, ... N+1 ---
        // SQL: SELECT * FROM Posts WHERE BlogId = @p0
        var firstPostTitle = blog.Posts.FirstOrDefault()?.Title;
        Console.WriteLine($"Blog '{blog.Url}' has a post titled '{firstPostTitle}'");
    }

    return Ok(blogs); // Also dangerous due to serialization issues.
}

```

### **Summary Table**

| Method | When is Data Loaded? | # of DB Queries | Primary Use Case | Recommendation |
| --- | --- | --- | --- | --- |
| **Eager (`Include`)** | Upfront, in the initial query. | **One.** | You know you will always need the related data. | **Best Practice.** |
| **Explicit (`.LoadAsync`)** | On demand, after the parent is loaded. | **Multiple.** | You only need the related data in specific, conditional cases. | Good for conditional logic. |
| **Lazy (`virtual`)** | The first time a property is accessed. | **N+1 (Potentially many).** | Rapid prototyping, desktop applications (WinForms/WPF). | **Avoid in Web APIs.** |

This detailed breakdown covers the mechanics, pros, and cons of all three loading strategies, giving you the knowledge to choose the right one for any situation.

---

### **4. Projections (`.Select()`)**

Returning full entity objects to the client is often wasteful and can be a security risk (e.g., exposing a `User.PasswordHash` property). **Projections** allow you to shape the query result into a custom object or DTO.

EF Core is smart enough to translate your `Select` into a SQL statement that only retrieves the columns you actually need.

**Example: Returning a lightweight DTO**

```csharp
public class ProductSummaryDto
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
}

[HttpGet("summaries")]
public async Task<IActionResult> GetProductSummaries()
{
    var summaries = await _context.Products
        .Where(p => p.IsAvailable)
        .Select(p => new ProductSummaryDto // Project into the DTO
        {
            Id = p.Id,
            Name = p.Name,

            Price = p.Price
        })
        .ToListAsync();

    // EF Core generates: SELECT Id, Name, Price FROM Products WHERE IsAvailable = 1
    // It does not fetch the 'Description' or other columns.
    return Ok(summaries);
}

```

---

### **5. Raw SQL Queries**

You are absolutely correct. My previous example was too simplistic. Interacting with raw SQL and stored procedures involves several distinct methods depending on whether you are querying data, executing commands, or getting return values.

Let's do a deep dive into the raw SQL capabilities of EF Core, with clear examples for each scenario.

---

### **The Three Main Methods for Raw SQL**

EF Core provides three primary methods for executing raw SQL, each designed for a different purpose:

1. **`FromSql` / `FromSqlInterpolated`:** For executing a raw SQL query that **returns entity data**. The shape of the `SELECT` statement must match the entity model that the `DbSet<T>` represents.
2. **`SqlQuery` / `SqlQueryRaw`:** For executing a raw SQL query that can return **any type of data**, including scalar types (like `int` or `string`) or non-entity C# objects. This is new and more flexible than `FromSql`.
3. **`ExecuteSql` / `ExecuteSqlInterpolated`:** For executing a **non-query command** (like `UPDATE`, `DELETE`, `INSERT`, or a stored procedure that performs an action) and getting back the number of rows affected.

**A Critical Note on `...Interpolated` vs `...Raw`:**

- **`...Interpolated` (e.g., `FromSqlInterpolated`):** Use this! It leverages C# string interpolation (`$""`) and automatically converts your variables into safe `DbParameter` objects, **preventing SQL injection**.
- **`...Raw` (e.g., `FromSqlRaw`):** This is the "unsafe" version. You must manually create `SqlParameter` objects. Only use this for highly complex scenarios where the interpolated version isn't flexible enough.

---

### **1. Querying Entity Data (`FromSql`)**

Use this when your `SELECT` statement returns columns that perfectly match the properties of an entity EF Core knows about.

**The Scenario:** You have a complex query with a CTE (Common Table Expression) that LINQ cannot generate, but it returns a list of `Product` entities.

```csharp
[HttpGet("complex-products")]
public async Task<IActionResult> GetComplexProducts(string categoryName)
{
    // The C# variable 'categoryName' is automatically parameterized to prevent SQL injection.
    // The SELECT list must include all columns that the Product entity expects.
    var products = await _context.Products
        .FromSql($"-- Some complex SQL \\n WITH RankedProducts AS (...) \\n SELECT Id, Name, Price FROM Products WHERE Category = {categoryName}")
        .ToListAsync();

    return Ok(products);
}

```

**Calling a Stored Procedure that returns Entities:**
Assume `[dbo].[GetProducts]` returns `Id`, `Name`, `Price`.

```csharp
[HttpGet("products-from-sp")]
public async Task<IActionResult> GetProductsFromSproc()
{
    var products = await _context.Products
        .FromSql($"EXECUTE [dbo].[GetProducts]")
        .ToListAsync();

    return Ok(products);
}

```

---

### **2. Querying ANY Data (`SqlQuery`)**

This is a newer, more flexible method that is not tied to a `DbSet<T>`. It can return any C# class, record, or even primitive types.

**The Scenario:** You want to return a custom DTO that is a mix of data from several tables, and it is not an entity in your `DbContext`.

**The DTO:**

```csharp
public class ProductSearchResult
{
    public int ProductId { get; set; }
    public string ProductName { get; set; }
    public string CategoryName { get; set; }
}

```

**The Action:**

```csharp
[HttpGet("product-search")]
public async Task<IActionResult> GetProductSearchResults()
{
    // Note that we are calling Database.SqlQuery, not a DbSet.
    // The type <ProductSearchResult> tells EF Core how to map the result set.
    // The column names in the SELECT must match the property names in the DTO.
    var results = await _context.Database
        .SqlQuery<ProductSearchResult>(
            $"SELECT p.Id as ProductId, p.Name as ProductName, c.Name as CategoryName FROM Products p JOIN Categories c ON p.CategoryId = c.Id")
        .ToListAsync();

    return Ok(results);
}

```

**Getting a single value (Scalar):**

```csharp
[HttpGet("product-count")]
public async Task<IActionResult> GetProductCount()
{
    var count = await _context.Database
        .SqlQuery<int>($"SELECT COUNT(*) FROM Products")
        .SingleAsync();

    return Ok(count);
}

```

---

### **3. Executing Commands (`ExecuteSql`)**

Use this for any SQL that **does not** return a result set, like `UPDATE`, `DELETE`, or stored procedures that perform actions.

**The Scenario:** You need to run a batch update to deactivate all products in a certain category. (Note: `ExecuteUpdate` in modern EF Core is better for this, but this demonstrates the raw SQL approach).

**The Action:**

```csharp
[HttpPost("deactivate-category")]
public async Task<IActionResult> DeactivateCategory(string categoryName)
{
    // The return value is the number of rows affected by the command.
    int rowsAffected = await _context.Database
        .ExecuteSqlAsync($"UPDATE Products SET IsAvailable = 0 WHERE Category = {categoryName}");

    return Ok(new { Message = $"{rowsAffected} products were deactivated." });
}

```

**Calling a Stored Procedure with Output Parameters:**
This is a more advanced scenario where you need to get a value back from the SP.

**The Stored Procedure:**

```sql
CREATE PROCEDURE [dbo].[CreateProduct]
    @Name NVARCHAR(100),
    @Price DECIMAL(18,2),
    @NewProductId INT OUTPUT
AS
BEGIN
    INSERT INTO Products (Name, Price) VALUES (@Name, @Price);
    SET @NewProductId = SCOPE_IDENTITY();
END

```

**The C# Code:**
You have to drop down to using `SqlParameter` objects for `OUTPUT` parameters.

```csharp
[HttpPost]
public async Task<IActionResult> CreateProductWithSproc([FromBody] CreateProductDto dto)
{
    // 1. Create a parameter for the output value.
    var newProductIdParam = new SqlParameter
    {
        ParameterName = "@NewProductId",
        SqlDbType = System.Data.SqlDbType.Int,
        Direction = System.Data.ParameterDirection.Output
    };

    // 2. Execute the stored procedure.
    await _context.Database.ExecuteSqlRawAsync(
        "EXEC [dbo].[CreateProduct] @Name, @Price, @NewProductId OUTPUT",
        new SqlParameter("@Name", dto.Name),
        new SqlParameter("@Price", dto.Price),
        newProductIdParam // Pass the output parameter
    );

    // 3. Read the value from the output parameter after execution.
    var newId = (int)newProductIdParam.Value;

    return CreatedAtAction("GetById", new { id = newId }, new { Id = newId });
}

```

### **Summary of Raw SQL Methods**

| Method | Returns | Primary Use Case | SQL Injection Safety |
| --- | --- | --- | --- |
| **`DbSet<T>.FromSql()`** | `IQueryable<T>` of an **Entity** | Querying for your existing EF Core entities with complex SQL. | **Safe** with string interpolation (`$""`). |
| **`Database.SqlQuery<T>()`** | `IQueryable<T>` of **Any Type** | Querying for DTOs or scalar values (counts, sums). | **Safe** with string interpolation. |
| **`Database.ExecuteSql()`** | `int` (rows affected) | `UPDATE`, `DELETE`, `INSERT`, action-based Stored Procedures. | **Safe** with string interpolation. |

This provides a complete toolkit for interacting with your database using raw SQL when LINQ to Entities doesn't fit the bill, all while maintaining type safety and preventing SQL injection.