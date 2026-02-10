# Topic 1: Dependency Injection Mechanics

The challenge with filters is that they often exist as **Attributes** (`[MyFilter]`), but attributes are just metadata created at compile time. They are "dumb." To make them "smart," we need a bridge to the runtime Dependency Injection (DI) container.

---

### **The Core Problem: Why Standard Attributes Fail**

Let's say you want to build a filter that logs to the database. It needs a `DbContext`.

**This will crash your application:**

```csharp
// THIS CODE WILL NOT WORK
public class MyDbLoggingFilterAttribute : Attribute, IActionFilter
{
    private readonly AppDbContext _db;

    // The .NET runtime does not know how to pass a DbContext here when it
    // creates the attribute metadata for the controller.
    public MyDbLoggingFilterAttribute(AppDbContext db)
    {
        _db = db;
    }

    public void OnActionExecuting(ActionExecutingContext context)
    {
        // ... Log to _db ...
    }
    public void OnActionExecuted(ActionExecutedContext context) { }
}

[MyDbLoggingFilter(???)] // What would you even pass here?
public class MyController : ControllerBase { }

```

The error would be: *"Attributes must have a public parameterless constructor, or constructors with only simple types."*

---

### **Solution 1: `[ServiceFilter]` (The Expert's Choice)**

`ServiceFilterAttribute` is a built-in attribute that acts as a "DI Proxy." It doesn't contain any logic itself. It simply holds a `Type` and, at runtime, it asks the main DI container: "Please create an instance of this Type for me."

**The Workflow:**

**Step 1: Write a pure C# Filter Class.**
This class is now a normal class, not an attribute. It can use standard constructor injection.

```csharp
// Just a regular class, no 'Attribute' suffix.
public class DbLoggingFilter : IActionFilter
{
    private readonly AppDbContext _db;
    private readonly ILogger<DbLoggingFilter> _logger;

    public DbLoggingFilter(AppDbContext db, ILogger<DbLoggingFilter> logger)
    {
        _db = db;
        _logger = logger;
    }

    public void OnActionExecuting(ActionExecutingContext context)
    {
        // Now you have full access to your services.
        var actionName = context.ActionDescriptor.DisplayName;
        _logger.LogInformation("Action {ActionName} is executing.", actionName);
        // _db.AuditLogs.Add(...)
    }

    public void OnActionExecuted(ActionExecutedContext context) { }
}

```

**Step 2: Register the Filter in `Program.cs`.**
Since you are asking the DI container to create it, the container needs to know how. The lifetime (`Scoped`, `Transient`, `Singleton`) is respected here. `Scoped` is the most common choice for filters.

```csharp
// In Program.cs
builder.Services.AddDbContext<AppDbContext>(...);
builder.Services.AddScoped<DbLoggingFilter>(); // <-- CRITICAL STEP

```

**Step 3: Apply the `ServiceFilter` Attribute.**
You apply the generic `[ServiceFilter]` attribute and tell it *which type* to look for.

```csharp
[ApiController]
[Route("[controller]")]
[ServiceFilter(typeof(DbLoggingFilter))] // <-- The Magic Link
public class ProductsController : ControllerBase
{
    // ... actions ...
}

```

---

### **Solution 2: `[TypeFilter]` (The "Slightly Different" Sibling)**

`TypeFilterAttribute` is almost identical to `ServiceFilter` but with one key difference.

- **How it works:** It *also* asks for a `Type`. However, it creates the instance itself using `Microsoft.Extensions.DependencyInjection.ObjectFactory`. It does **not** require you to register the filter in the DI container in `Program.cs`.

**When would you use `TypeFilter`?**

1. **Convenience:** If you have many simple filters and don't want to clutter your `Program.cs` with registrations.
2. **Passing Non-DI Arguments:** `TypeFilter` has an `Arguments` property that allows you to pass simple values (like strings or enums) to your filter's constructor *in addition* to the injected services.

**Example with Arguments:**

```csharp
public class PermissionFilter : IAuthorizationFilter
{
    private readonly IPermissionService _permissionService;
    private readonly string _permissionName;

    // It takes a service (from DI) AND a simple string (from the attribute).
    public PermissionFilter(IPermissionService permissionService, string permissionName)
    {
        _permissionService = permissionService;
        _permissionName = permissionName;
    }

    public void OnAuthorization(AuthorizationFilterContext context)
    {
        if (!_permissionService.HasPermission(context.HttpContext.User, _permissionName))
        {
            context.Result = new ForbidResult();
        }
    }
}

```

**Usage:**

```csharp
[TypeFilter(typeof(PermissionFilter), Arguments = new object[] { "CanDeleteProducts" })]
[HttpDelete("{id}")]
public IActionResult DeleteProduct(int id)
{
    // ...
}

```

---

### **Solution 3: `IFilterFactory` (The Architect's Tool)**

`IFilterFactory` is the interface that `ServiceFilterAttribute` and `TypeFilterAttribute` implement behind the scenes.

You would implement this yourself if you needed incredibly complex, dynamic filter instantiation logic that depends on the current request context. This is extremely rare and only used for building reusable frameworks.

---

### **Summary of Dependency Injection**

| Feature | `ServiceFilter` | `TypeFilter` |
| --- | --- | --- |
| **How it Works** | Resolves from DI Container | Instantiates via `ObjectFactory` |
| **Requires Registration?** | **Yes** (`builder.Services.Add...`) | **No** |
| **Passes Arguments?** | No | Yes (via `Arguments` property) |
| **DI Lifetime Respected?** | Yes (`Scoped`, `Transient`) | Yes |
| **When to Use?** | **95% of the time.** Cleanest, most explicit. | When you need to pass a specific configuration value (like a permission name) directly from the attribute. |

Are you ready to proceed to **Topic 2: The Exception Filter Scope (vs. Middleware)**? This is a critical concept for error handling.