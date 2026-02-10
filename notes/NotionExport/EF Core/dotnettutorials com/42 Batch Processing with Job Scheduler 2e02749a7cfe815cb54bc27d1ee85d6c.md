# 42. Batch Processing with Job Scheduler

# Batch Processing with a Job Scheduler

Batch processing refers to the execution of a series of tasks on a large volume of data without manual intervention. In EF Core applications, this is typically implemented using **Disconnected Entities** within a background worker or a scheduled job.

---

### Why Use a Job Scheduler?

- **Automation**: Process recurring tasks like payroll, report generation, or data synchronization.
- **Resource Management**: Move heavy database operations to off-peak hours to maintain application responsiveness.
- **Isolation**: Decouple long-running tasks from the main request-response cycle of a Web API.

---

### The Pattern: Short-Lived Contexts

In a background job that processes thousands of records, keeping a single `DbContext` instance open for the entire duration is a **memory leak risk**. EF Core continues to track every object added to its internal cache. Instead, follow the “Scope-per-Batch” pattern:

```csharp
public async Task RunBillingJobAsync()
{
    const int batchSize = 500;

    // Fetch IDs first to avoid keeping a large query open
    var pendingInvoiceIds = await GetPendingIdsAsync();

    foreach (var chunk in pendingInvoiceIds.Chunk(batchSize))
    {
        // 1. Create a fresh context for this specific batch
        using var context = new MyDbContext();

        // 2. Load the batch (AsNoTracking if only reading)
        var invoices = await context.Invoices
            .Where(i => chunk.Contains(i.Id))
            .ToListAsync();

        // 3. Process logic
        foreach (var invoice in invoices)
        {
            invoice.Process();
            context.Update(invoice); // Mark as Modified (Disconnected Entity)
        }

        // 4. Save Changes and Dispose context to free memory
        await context.SaveChangesAsync();
    }
}
```

---

### Common Scheduling Technologies

| Technology | Best For | Description |
| --- | --- | --- |
| **Windows Task Scheduler** | On-premise simple tasks | Runs a .exe file at specific intervals. |
| **Hangfire / Quartz.NET** | Integrated .NET Jobs | Runs inside your app; supports retries, persistence, and dashboards. |
| **Azure Functions** | Cloud-native Serverless | Triggered by Timers or Queues; highly scalable. |
| **Worker Services** | Long-running processes | Built-in .NET `BackgroundService` with `ExecuteAsync`. |

---

### Best Practices for EF Core Jobs

1. **Use `AsNoTracking` for Reading**: When a job only needs to read data to trigger other events (like sending emails), use `.AsNoTracking()` to reduce overhead.
2. **Graceful Shutdown**: Background jobs should handle `CancellationToken` to avoid data corruption if the application or server restarts mid-process.
3. **Idempotency**: Design your job so that if it fails and restarts, it can safely resume without duplicating work (e.g., check if an email was already sent before sending).
4. **Logging & Auditing**: Use a dedicated `JobLog` table to record when a job started, ended, how many rows it succeeded on, and any exceptions that occurred.
5. **Timeout Management**: Long-running database commands may need a higher `CommandTimeout` configured in the `DbContext`.
`csharp context.Database.SetCommandTimeout(300); // 5 minutes`