# 40. Bulk Operations Performance Benchmark in Entity Framework Core

# Bulk Operations Performance Benchmark

When dealing with thousands of records, choosing the right method for data manipulation can be the difference between seconds and minutes of execution time. This benchmark compares the primary approaches available in the Entity Framework Core ecosystem.

---

### Comparison Matrix

| Approach | Technology | Change Tracking | Network Round-trips | Ideal Use Case |
| --- | --- | --- | --- | --- |
| **Native EF Core** | `AddRange` / `SaveChanges` | **Enabled** | Batched (Default 42/batch) | Small transactional sets (<100 rows) |
| **Native EF Core 7+** | `ExecuteUpdate` / `Delete` | **None** | Single (Set-based) | Maintenance & mass cleanup |
| **EFCore.BulkExtensions** | `SqlBulkCopy` / `MERGE` | **None** | Single | High-volume ingestion & Upserts |
| **Z.EntityFramework** | Native Bulk Utilities | **Optional** | Single | Enterprise-scale synchronization |

---

### Benchmark Analysis (Relative Performance)

*The following observations are based on processing datasets of 10,000+ entities:*

### 1. Bulk Insert

- **Native EF Core**: 🐌 **Slow**. Every entity is added to the Change Tracker, consuming significant memory and CPU. Commands are batched but still treated as individual inserts.
- **Bulk Extensions**: 🚀 **Ultra-Fast**. These libraries utilize the database’s native bulk-loading utilities (like `SqlBulkCopy` for SQL Server), which stream data directly into the table.

### 2. Bulk Update

- **Native EF Core**: 🐌 **Slow**. Requires loading entities into memory, modifying them, and sending `UPDATE` statements for every row.
- **EF Core 7+ (`ExecuteUpdate`)**: 🚀 **Very Fast**. Translates your LINQ query directly into a single SQL `UPDATE` statement.
- **Bulk Extensions**: 🚀 **Fast**. Extremely efficient for “List-based” updates (e.g., updating thousands of records from a modified collection).

### 3. Bulk Delete

- **Native EF Core**: 🐌 **Slow**. Must track every deletion in memory.
- **EF Core 7+ (`ExecuteDelete`)**: 🚀 **Very Fast**. Executes a single `DELETE FROM...WHERE` command in the database.
- **Bulk Extensions**: 🚀 **Fast**. Efficiently deletes based on a collection of keys or objects.

---

### Key Takeaways

1. **Change Tracking Overhead**: The primary performance bottleneck in native EF Core for large datasets is **Change Tracking**. Tracking thousands of object states in memory is expensive.
2. **Round-Trip Reduction**: Every round-trip to the database adds latency. Bulk libraries and modern `Execute` methods minimize this to one (or very few) trips.
3. **Modern EF Core (7+) vs. Libraries**: For simple “Update all records where X” or “Delete all records where Y”, the built-in `ExecuteUpdate/Delete` methods are world-class and often remove the need for 3rd party libraries.
4. **Upserts and Ingestion**: Third-party libraries like `EFCore.BulkExtensions` are still the gold standard for **Massive Inserts** and **Upserts** (BulkMerge), which are not yet fully handled as optimized set-based operations in native EF Core.

### Summary Recommendation

- **Transactional Work**: Use standard `SaveChanges()` to maintain data integrity and concurrency checks.
- **Direct Modifications**: Use `ExecuteUpdate()` or `ExecuteDelete()` for high-speed maintenance.
- **Data Ingestion**: Use `EFCore.BulkExtensions` or `Z.EntityFramework` for importing CSVs, large API payloads, or initial data seeds.