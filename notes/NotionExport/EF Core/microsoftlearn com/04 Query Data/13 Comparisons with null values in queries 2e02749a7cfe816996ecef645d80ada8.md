# 13. Comparisons with null values in queries

# Comparisons with Null Values

C# uses **2-valued logic** (true, false), while SQL databases use **3-valued logic** (true, false, NULL). When translating LINQ, EF Core adds safety checks to ensure that queries behave according to C# expectations.

## 1. Safety Checks in Translation

In SQL, any comparison with `NULL` (e.g., `Id <> NULL`) results in `NULL`, which is treated as false. In C#, `42 != null` is true. EF Core resolves this by adding conditional logic to the generated SQL.

### Example: Non-Equality (`!=`)

```csharp
// LINQ
context.Entities.Where(e => e.Id != e.NullableInt);

```

```sql
-- Generated SQL (includes null safety)
SELECT * FROM Entities 
WHERE ([Id] <> [NullableInt]) OR [NullableInt] IS NULL

```

The `OR [NullableInt] IS NULL` ensures the C# behavior (returning rows where one side is null) is maintained.

## 2. Performance Implications

Comparing nullable columns results in more complex SQL than comparing required (non-nullable) columns.

- **Prefer Required Columns:** Mark columns as `.IsRequired()` whenever possible to eliminate the need for `IS NULL` checks.
- **Explicit Null Checks:** Manually filtering out nulls in your query can help EF Core simplify the translation.

## 3. Relational Null Semantics (Opt-Out)

If you prefer the raw database behavior (where `NULL` comparisons are always `NULL`), you can disable EF Core's safety logic. This produces simpler SQL but may yield unexpected results compared to standard C# logic.

### Enabling Relational Semantics

```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder.UseSqlServer(connectionString, o => o.UseRelationalNulls());
}

```

<aside>
⚠️ With `UseRelationalNulls`, a query like `Where(e => e.Prop1 == e.Prop2)` will **not** return rows where both values are `NULL`, because `NULL = NULL` is false in standard SQL.

</aside>

## 4. Summary Table

| Feature | Standard EF Null Logic | Relational Null Semantics |
| --- | --- | --- |
| **Philosophy** | Matches C# behavior. | Matches SQL/DB behavior. |
| **SQL Complexity** | High (extra `IS NULL` checks). | Low (direct comparison). |
| `NULL == NULL` | Returns `true`. | Returns `false`. |
| **Recommended For** | General application development. | Performance-critical read-only apps. |