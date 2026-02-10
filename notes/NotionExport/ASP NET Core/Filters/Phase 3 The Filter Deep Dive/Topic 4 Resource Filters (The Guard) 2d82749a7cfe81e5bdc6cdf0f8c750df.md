# Topic 4: Resource Filters (The Guard)

The **Resource Filter** is the "Guard at the Gate." It's one of the most powerful and underutilized filters because of its unique position in the pipeline.

**Its Position:**

- Runs **after** `AuthorizationFilter`. (So you know *who* the user is).
- Runs **before** `Model Binding` and `ActionFilter`. (So you can stop a request *before* the framework does expensive work like allocating and deserializing a large JSON payload).

This "early but authenticated" position makes it perfect for high-impact performance and logic checks.

---

### **1. The Interfaces: `IResourceFilter` and `IAsyncResourceFilter`**

Just like Action Filters, Resource Filters have a synchronous and asynchronous version.

- `IResourceFilter`
    - `OnResourceExecuting(ResourceExecutingContext context)`
    - `OnResourceExecuted(ResourceExecutedContext context)`
- `IAsyncResourceFilter` (Recommended)
    - `OnResourceExecutionAsync(ResourceExecutingContext context, ResourceExecutionDelegate next)`

The async version uses the `next()` delegate pattern, which makes it ideal for wrapping logic around the entire action execution.

---

### **2. Production Use Case 1: High-Performance Caching**

We saw a caching example using short-circuiting in the previous topic. The Resource Filter is the *best* place to implement caching.

**Why not an Action Filter?**
If you put your caching logic in an `IActionFilter`, the framework has already spent time and memory on **Model Binding**. If a user sends a 10MB JSON payload to a `[FromBody]` parameter, you've already deserialized 10MB of data before your `OnActionExecuting` even runs.

By putting the cache check in `OnResourceExecuting`, you check the cache *before* model binding even starts. If there's a cache hit, you save significant CPU and memory allocation.

**Recap of the `IAsyncResourceFilter` Cache Implementation:**

```csharp
public class CacheResourceFilter : IAsyncResourceFilter
{
    private readonly IDistributedCache _cache;
    // Constructor to inject the cache...

    public async Task OnResourceExecutionAsync(ResourceExecutingContext context, ResourceExecutionDelegate next)
    {
        var cacheKey = context.HttpContext.Request.Path.ToString();
        var cachedResponse = await _cache.GetStringAsync(cacheKey);

        if (!string.IsNullOrEmpty(cachedResponse))
        {
            // CACHE HIT - SHORT-CIRCUIT
            // The model binder and action filter will never run for this request.
            context.Result = new ContentResult { Content = cachedResponse, ContentType = "application/json" };
            return;
        }

        // CACHE MISS - Proceed to the action
        var resultContext = await next();

        // After the action runs, cache the result
        if (resultContext.Result is OkObjectResult okResult)
        {
            await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(okResult.Value));
        }
    }
}

```

---

### **3. Production Use Case 2: Feature Flags (Disabling Endpoints)**

Imagine you have a new feature, `/api/v2/products`, that is not ready for production. You want to disable the entire controller without commenting out code or redeploying.

**The Goal:** If the "NewApiV2" feature flag is OFF, any request to that controller should return a `404 Not Found`.

**The Filter Code:**
This uses `IAsyncResourceFilter` because fetching feature flags from a provider like Azure App Configuration is an async operation.

```csharp
// Assuming you have a feature management library like Microsoft.FeatureManagement
public class FeatureGateFilter : IAsyncResourceFilter
{
    private readonly IFeatureManager _featureManager;
    private readonly string _featureName;

    public FeatureGateFilter(IFeatureManager featureManager, string featureName)
    {
        _featureManager = featureManager;
        _featureName = featureName;
    }

    public async Task OnResourceExecutionAsync(ResourceExecutingContext context, ResourceExecutionDelegate next)
    {
        // Check if the required feature is enabled.
        if (!await _featureManager.IsEnabledAsync(_featureName))
        {
            // Feature is OFF. Short-circuit with a 404.
            context.Result = new NotFoundResult();
            return;
        }

        // Feature is ON. Proceed as normal.
        await next();
    }
}

```

**Usage (with `TypeFilter` to pass the feature name):**

```csharp
[ApiController]
[Route("api/v2/products")]
// Use TypeFilter to pass the "NewProductsApi" string to the filter's constructor
[TypeFilter(typeof(FeatureGateFilter), Arguments = new object[] { "NewProductsApi" })]
public class ProductsV2Controller : ControllerBase
{
    // All actions in this controller are now protected by the feature flag.
}

```

---

### **4. Production Use Case 3: Database Transactions**

This is a classic "wrapper" use case. You want to ensure that everything that happens inside a controller action occurs within a single, atomic database transaction. If *anything* fails, the entire operation should be rolled back.

The `IAsyncResourceFilter` is perfect for this "begin-commit/rollback" logic.

**The Filter Code:**

```csharp
public class TransactionResourceFilter : IAsyncResourceFilter
{
    private readonly AppDbContext _db;

    public TransactionResourceFilter(AppDbContext db)
    {
        _db = db;
    }

    public async Task OnResourceExecutionAsync(ResourceExecutingContext context, ResourceExecutionDelegate next)
    {
        // 1. BEFORE the action: Begin the transaction
        await using var transaction = await _db.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted);

        // 2. The `next()` delegate executes the model binder, action filters,
        //    the action itself, and the result filters.
        var executedContext = await next();

        // 3. AFTER everything: Check the outcome
        if (executedContext.Exception == null && executedContext.Result is not StatusCodeResult r || (r.StatusCode >= 200 && r.StatusCode < 300))
        {
            // If there were no exceptions and the result was successful, COMMIT.
            await transaction.CommitAsync();
        }
        else
        {
            // If there was an exception or the action returned an error code, ROLLBACK.
            await transaction.RollbackAsync();
        }
    }
}

```

**Usage:** Apply with `[ServiceFilter(typeof(TransactionResourceFilter))]` on any controller that performs database writes.

---

### **Summary of Resource Filters**

| Feature | Description |
| --- | --- |
| **Position** | Runs *after* Auth, but *before* Model Binding. |
| **Best Use Cases** | **Caching**, **Feature Flags**, **Transactions**, **API Versioning Checks**. |
| **Key Advantage** | Can prevent expensive operations (like deserializing large payloads) if a request can be handled early. |

The Resource Filter is your first line of defense for application logic. It asks the question: "Is this request even worth processing further?"

Are you ready for **Topic 5: Action Filters (The Modifier)**, where we dive into manipulating the inputs and outputs of the action method itself?