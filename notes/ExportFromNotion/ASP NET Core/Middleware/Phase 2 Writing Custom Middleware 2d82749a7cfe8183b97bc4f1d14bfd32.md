# Phase 2: Writing Custom Middleware

There are three primary ways to create custom middleware in [ASP.NET](http://asp.net/) Core, each with its own advantages. We'll progress from the simplest to the most powerful and scalable.

---

### **1. Inline Middleware (`app.Use`)**

This is the quickest way to add simple middleware logic, written directly in `Program.cs` using a lambda expression.

**Best For:**

- Simple request logging.
- Adding a custom response header.
- Quickly debugging the request pipeline.

**The Syntax:**
The `app.Use()` method takes a delegate that accepts two parameters: `HttpContext` and the `RequestDelegate next`.

**Example: A Simple Request Logger**

```csharp
// In Program.cs
var app = builder.Build();

// --- Middleware Pipeline ---

app.Use(async (context, next) =>
{
    // 1. Code here runs ON THE WAY IN.
    var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
    logger.LogInformation("Request IN: {Method} {Path}", context.Request.Method, context.Request.Path);

    // 2. Pass control to the next middleware in the pipeline.
    await next(context);

    // 3. Code here runs ON THE WAY OUT (after the endpoint has executed).
    logger.LogInformation("Response OUT: {StatusCode}", context.Response.StatusCode);
});

app.MapGet("/", () => "Hello World!");

app.Run();

```

When you run this and navigate to the home page, your console will show:

```
info: Program[0]
      Request IN: GET /
info: Program[0]
      Response OUT: 200

```

---

### **2. Convention-Based Middleware Class**

Inline middleware gets messy for anything more than a few lines. The next step is to move the logic into its own class. This pattern relies on a "convention" (a specific class structure) rather than an interface.

**Best For:**

- Middleware that is reusable and has its own logic.
- Middleware that requires **singleton** or **transient** dependencies injected via its constructor.

**The Convention:**

1. The class must have a public constructor that accepts a `RequestDelegate` parameter.
2. The class must have a public method named `InvokeAsync` that accepts an `HttpContext`.

**Example: A Tenant ID Middleware**
Let's create a middleware that reads a `X-Tenant-Id` header and adds it to the `HttpContext.Items` collection, so downstream services can access it.

**Step 1: Create the Middleware Class**

```csharp
public class TenantIdMiddleware
{
    private readonly RequestDelegate _next;

    // The RequestDelegate is required by the convention.
    public TenantIdMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    // You can inject Singleton or Transient services here. Scoped services are problematic.
    public async Task InvokeAsync(HttpContext context, ILogger<TenantIdMiddleware> logger)
    {
        if (context.Request.Headers.TryGetValue("X-Tenant-Id", out var tenantId))
        {
            // Store the tenant ID for other parts of the app to use.
            context.Items["TenantId"] = tenantId.ToString();
            logger.LogInformation("Request is for Tenant: {TenantId}", tenantId);
        }
        else
        {
            logger.LogWarning("X-Tenant-Id header not found.");
        }

        // Call the next middleware in the pipeline.
        await _next(context);
    }
}

```

**Step 2: Create a Clean Extension Method for Registration**
This is a best practice to keep `Program.cs` clean.

```csharp
public static class TenantIdMiddlewareExtensions
{
    public static IApplicationBuilder UseTenantIdMiddleware(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<TenantIdMiddleware>();
    }
}

```

**Step 3: Register in `Program.cs`**

```csharp
// In Program.cs
var app = builder.Build();

app.UseRouting();
app.UseTenantIdMiddleware(); // <-- Clean and simple registration
app.UseAuthorization();

```

---

### **3. Factory-Based Middleware (`IMiddleware`) (The Expert's Choice)**

This is the most powerful and robust pattern. It solves a major limitation of convention-based middleware: **dependency injection of scoped services.**

Convention-based middleware is created as a singleton, so it **cannot** take a scoped service (like a `DbContext`) in its constructor. The `IMiddleware` pattern fixes this.

**Best For:**

- Middleware that needs to interact with a database (`DbContext`).
- Middleware with a complex lifecycle or dependencies that should be `Scoped`.
- Ensuring your middleware follows best practices for testability and DI.

**The Workflow:**

**Step 1: Implement the `IMiddleware` Interface**
The class no longer has a `RequestDelegate` in its constructor. It has its own dependencies. The `InvokeAsync` method signature is defined by the interface.

```csharp
public class ScopedLoggingMiddleware : IMiddleware
{
    private readonly AppDbContext _db; // <-- Injected Scoped Service!
    private readonly ILogger<ScopedLoggingMiddleware> _logger;

    public ScopedLoggingMiddleware(AppDbContext db, ILogger<ScopedLoggingMiddleware> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        // Now you can perform DB operations.
        var userCount = await _db.Users.CountAsync();
        _logger.LogInformation("Current user count is {Count}", userCount);

        await next(context);
    }
}

```

**Step 2: Register the Middleware in `Program.cs`**
You must register the middleware class itself with the DI container. The lifetime you choose (`Scoped`, `Transient`) will be respected.

```csharp
// In Program.cs
builder.Services.AddDbContext<AppDbContext>(...);
builder.Services.AddScoped<ScopedLoggingMiddleware>(); // <-- Register the middleware itself

```

**Step 3: Use it in the Pipeline**
Instead of `app.UseMiddleware<T>()`, you still call it the same way. The framework is smart enough to use the `IMiddlewareFactory` to resolve your registered class from the DI container for each request.

```csharp
var app = builder.Build();
app.UseMiddleware<ScopedLoggingMiddleware>();

```

### **Summary of Phase 2**

| Pattern | DI Support | Lifetime | When to Use |
| --- | --- | --- | --- |
| **Inline (`app.Use`)** | Manual (`context.RequestServices`) | Singleton | Quick, simple, non-reusable logic. |
| **Convention-Based** | Constructor (Singleton/Transient only) | Singleton | Most common for simple, reusable logic without scoped dependencies. |
| **Factory-Based (`IMiddleware`)** | **Constructor (All lifetimes)** | Per-request (`Scoped`/`Transient`) | **The correct choice** for any middleware that needs a `DbContext` or other scoped services. |

Are you ready to transition to **Part 2: Mastering Minimal APIs**, where we will apply this pipeline knowledge to build endpoints?