# 7. Pagination

# Pagination

Pagination is the process of retrieving large datasets in smaller "pages." There are two primary techniques: **Offset-based** and **Keyset-based**.

## 1. Offset Pagination (Skip and Take)

This is the most common and intuitive method, using the `.Skip()` and `.Take()` operators.

```csharp
var pageSize = 10;
var pageNumber = 3;

var results = await context.Posts
    .OrderBy(p => p.Id)
    .Skip((pageNumber - 1) * pageSize)
    .Take(pageSize)
    .ToListAsync();

```

### Shortcomings

- **Performance:** The database must still scan and discard all "skipped" rows. Performance degrades significantly as you navigate to deeper pages.
- **Inconsistency:** If records are added or deleted while a user is paginating, items may be shown twice or skipped entirely.

## 2. Keyset Pagination (Seek-based)

Keyset pagination uses a `WHERE` clause to "seek" to the next set of rows based on the last value retrieved from the previous page.

```csharp
var lastFetchedId = 55;

var results = await context.Posts
    .OrderBy(p => p.Id)
    .Where(p => p.Id > lastFetchedId)
    .Take(10)
    .ToListAsync();

```

### Benefits

- **Performance:** Extremely efficient with a primary key or indexed columns (O(log N) instead of O(N)).
- **Stability:** Concurrent additions or deletions in earlier pages do not affect the current page's results.

### Limitations

- **No Random Access:** Users cannot "jump" to Page 50 directly; they can only move to the "Next" or "Previous" page.

## 3. Best Practices

### Ensure Unique Ordering

Always order by a column (or combination of columns) that is **unique**. If multiple rows have the same value in your sort column, the database might return them in a different order for each query, causing items to be skipped or repeated across pages.

```csharp
// Unsafe: multiple posts can have the same date
.OrderBy(p => p.Date) 

// Safe: unique combination
.OrderBy(p => p.Date).ThenBy(p => p.Id)

```

### Use Composite Indexes

For keyset pagination with multiple sort keys, define a composite index in your model to ensure the database can efficiently perform the seek operation.

```csharp
modelBuilder.Entity<Post>().HasIndex(p => new { p.Date, p.Id });

```

## 4. Comparison Summary

| Feature | Offset Pagination | Keyset Pagination |
| --- | --- | --- |
| **Logic** | Fixed offsets (`Skip`) | Value-based (`Where >`) |
| **Performance** | Law (Scan-heavy) | High (Index-seek) |
| **UX** | Random access (Go to Page X) | Continuous / Sequential |
| **Stability** | Sensitive to concurrent data | Consistent results |