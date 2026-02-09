# 7. LINQ to Entities in Entity Framework Core

# LINQ to Entities in EF Core

**LINQ (Language Integrated Query)** is the primary mechanism for querying databases in Entity Framework Core. It allows you to write type-safe, expressive queries in C# that EF Core translates into optimized SQL strings tailored for your specific database provider.

---

### Core Concepts

1. **Deferred Execution:** A LINQ query is not executed when it is defined. Execution occurs only when the results are enumerated (e.g., using `foreach`, `.ToList()`, or `.ToListAsync()`).
2. **IQueryable vs. IEnumerable:**
    - **IQueryable:** Represents a query destined for the database. Filters and sorts are applied in SQL on the **Server**.
    - **IEnumerable:** Represents a collection in memory. Filtering occurs on the **Client** (your application) after all data has been fetched.
3. **Method vs. Query Syntax:** While dot-notation (Method Syntax) is more common in professional development, EF Core supports SQL-like “Query Syntax” as well.

---

### 1. Basic Filtering (Where)

Narrows down the result set based on a predicate.

```csharp
// SQL: SELECT * FROM Products WHERE Stock > 10 AND Price < 500
var affordableProducts = await context.Products
    .Where(p => p.StockQuantity > 10 && p.Price < 500)
    .ToListAsync();
```

---

### 2. Projection (Select)

Fetches only specific columns, reducing network traffic and memory usage.

```csharp
// Returns only the names and prices, rather than the full Product object
var productSummary = await context.Products
    .Select(p => new {
        p.ProductName,
        p.Price
    })
    .ToListAsync();
```

---

### 3. Sorting (OrderBy)

Organizes data based on one or more properties.

```csharp
var sortedOrders = await context.Orders
    .OrderByDescending(o => o.OrderDate)
    .ThenBy(o => o.Status)
    .ToListAsync();
```

---

### 4. Pagination (Skip & Take)

Essential for web applications to avoid overloading the browser with data.

```csharp
int pageSize = 10;
int pageNum = 2; // Second page

var page = await context.AuditLogs
    .OrderByDescending(l => l.Timestamp)
    .Skip((pageNum - 1) * pageSize) // Skip the first 10
    .Take(pageSize)                // Fetch the next 10
    .ToListAsync();
```

---

### 5. Aggregation and Grouping

Performs calculations on sets of data.

```csharp
var categoryStats = await context.Products
    .GroupBy(p => p.CategoryName)
    .Select(g => new {
        Category = g.Key,
        TotalStock = g.Sum(p => p.StockQuantity),
        AveragePrice = g.Average(p => p.Price)
    })
    .ToListAsync();
```

---

### Server-side vs. Client-side Evaluation

- **Server-side:** EF Core translates your C# logic into SQL. This is fast and efficient.
- **Client-side:** If EF Core cannot translate a custom C# method into SQL, it fetches the data into memory first.
- **Best Practice:** Always ensure filtering (`Where`) and paging (`Skip`/`Take`) happen **before** you materialize the query with `ToList()`. Materializing too early can lead to thousands of unnecessary records being loaded into your application’s memory.

### Summary Checklist

| Objective | LINQ Method |
| --- | --- |
| **Filter** | `.Where(p => ...)` |
| **Pick Columns** | `.Select(p => new { ... })` |
| **Unique Results** | `.Distinct()` |
| **First Record** | `.FirstOrDefaultAsync()` |
| **Check Existence** | `.AnyAsync(p => ...)` |
| **Count Records** | `.CountAsync()` |