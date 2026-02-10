# 5. Split queries

# Single vs. Split Queries

EF Core can load related data using either a single SQL query (default) or multiple SQL queries (**Split Queries**). Each approach has distinct performance and consistency trade-offs.

## 1. Single Queries (Default)

EF Core uses SQL `JOIN`s to retrieve related data in one round-trip.

### Issues with Single Queries

- **Cartesian Explosion:** When you include multiple sibling collections (e.g., `Blogs` including both `Posts` and `Contributors`), the database returns a cross product. If a blog has 10 posts and 10 contributors, it returns 100 rows for that one blog.
- **Data Duplication:** Parent table data is repeated in every row of the child table, which is inefficient if the parent has large columns (e.g., text or blobs).

## 2. Split Queries (`AsSplitQuery`)

Split queries generate a separate SQL statement for each included collection navigation.

```csharp
var blogs = await context.Blogs
    .Include(b => b.Posts)
    .Include(b => b.Contributors)
    .AsSplitQuery() // Executes 3 SQL commands
    .ToListAsync();

```

### Benefits

- Prevents Cartesian explosion.
- Minimizes data duplication for large parent entities.

## 3. Trade-offs and Considerations

| Feature | Single Query | Split Query |
| --- | --- | --- |
| **Roundtrips** | 1 (Best performance for low latency) | Multiple (Higher latency overhead) |
| **Consistency** | Strong (Atomic snapshot) | Weak (Data may change between queries) |
| **Memory** | Low (Streamed from DB) | Higher (Often requires buffering results) |
| **Scaling** | Poor for multi-collection includes | Excellent for multi-collection includes |

### Mandatory: Unique Ordering

When using `Skip`/`Take` with split queries, you **must** ensure the `OrderBy` clause yields a unique order (e.g., by adding a Primary Key to the sort). Without unique ordering, paging may result in inconsistent data across the split SQL batches.

### Global Configuration

You can set split queries as the default behavior for a `DbContext`:

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder options)
{
    options.UseSqlServer(connectionString, o => 
        o.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery));
}

```

## 4. Summary Recommendation

- **Use Single Query** for simple relationships or when data consistency is paramount.
- **Use Split Query** when including multiple large collections or if you notice performance degrades due to massive cross products (Cartesian explosion).