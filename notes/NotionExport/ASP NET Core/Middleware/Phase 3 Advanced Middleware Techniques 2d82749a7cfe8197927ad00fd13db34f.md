# Phase 3: Advanced Middleware Techniques

---

This phase covers how middleware can **react** to the pipeline, branch its logic, and interact with the endpoint information that the routing middleware discovers.

---

### **1. Branching the Pipeline (`Map` and `MapWhen`)**

So far, we have used `app.Use()`, which applies a middleware to *every single request*. This is often wasteful. For example, why run a JWT validation middleware on a request for a CSS file?

You can create branches in your pipeline that are only executed for specific requests.

### **`app.Map(path, builder => { ... })`**

- **What it does:** Creates a branch in the pipeline that is only executed if the request path **starts with** the specified path segment.
- **Use Case:** Creating a completely separate pipeline for a specific section of your site, like an admin portal.

**Example: A Separate Pipeline for `/api`**

```csharp
var app = builder.Build();

app.UseHttpsRedirection();

// This branch is ONLY for requests starting with /api
app.Map("/api", apiApp =>
{
    // Middleware inside this branch does not affect the main pipeline.
    apiApp.UseAuthentication();
    apiApp.UseAuthorization();

    // You must also configure routing/endpoints inside the branch.
    apiApp.UseRouting();
    apiApp.UseEndpoints(endpoints =>
    {
        endpoints.MapControllers();
    });
});

// This is the "else" branch for all other requests (e.g., '/')
app.UseStaticFiles();
app.MapGet("/", () => "This is the public website.");

app.Run();

```

### **`app.MapWhen(predicate, builder => { ... })`**

- **What it does:** This is a more powerful version of `Map`. It branches the pipeline if a custom predicate (a function that returns `true` or `false`) is met. You can check anything: headers, query strings, IP address, etc.
- **Use Case:** Applying a specific authentication scheme only for certain hosts.

**Example: Different Logic for Beta Testers**

```csharp
app.MapWhen(
    context => context.Request.Headers.ContainsKey("X-Is-Beta-User"),
    betaApp =>
    {
        betaApp.Use(async (ctx, next) =>
        {
            // Do something special for beta users
            await next(ctx);
        });
    }
);

// All other requests continue down the main pipeline as normal.
app.UseRouting();
// ...

```

---

### **2. Accessing Endpoint Info AFTER Routing**

This is the key point you raised. Middleware registered *before* `app.UseRouting()` is "dumb"—it doesn't know what endpoint will eventually handle the request.

Middleware registered **after** `app.UseRouting()` is "smart"—it can inspect the endpoint and change its behavior.

**The Magic:** `HttpContext.GetEndpoint()`

**The Scenario:** You want to create a middleware that logs a special message, but only when the request is hitting an action method that has a specific attribute (`[Loggable]`).

### **Step 1: The Marker Attribute**

This is a simple attribute that doesn't do anything itself; it just acts as a tag.

```csharp
[AttributeUsage(AttributeTargets.Method)]
public class LoggableAttribute : Attribute { }

```

### **Step 2: The Endpoint-Aware Middleware**

This middleware must be placed **after** `app.UseRouting()`.

```csharp
public class EndpointAwareLoggingMiddleware
{
    private readonly RequestDelegate _next;

    public EndpointAwareLoggingMiddleware(RequestDelegate next) { _next = next; }

    public async Task InvokeAsync(HttpContext context, ILogger<EndpointAwareLoggingMiddleware> logger)
    {
        // Get the endpoint that routing selected.
        var endpoint = context.GetEndpoint();

        if (endpoint != null)
        {
            // Check if the endpoint's metadata contains our attribute.
            var loggableAttribute = endpoint.Metadata.GetMetadata<LoggableAttribute>();

            if (loggableAttribute != null)
            {
                logger.LogInformation("SPECIAL LOG: This endpoint ({EndpointName}) is marked as loggable!", endpoint.DisplayName);
            }
        }

        await _next(context);
    }
}

```

### **Step 3: Correct Pipeline Order and Controller**

```csharp
// Program.cs
// ...
app.UseRouting(); // <-- Routing runs first

app.UseMiddleware<EndpointAwareLoggingMiddleware>(); // <-- Now this middleware can see the result

app.UseAuthorization();
app.MapControllers();

// MyController.cs
[ApiController]
public class MyController : ControllerBase
{
    [HttpGet("/public")]
    public IActionResult GetPublic() => Ok("Public data");

    [HttpGet("/private")]
    [Loggable] // <-- Our marker attribute
    public IActionResult GetPrivate() => Ok("Private, loggable data");
}

```

**Result:** When you call `/private`, you will see the "SPECIAL LOG" message. When you call `/public`, you will not.

---

### **3. `IEndpointFilter` vs. Middleware (A Preview)**

The technique above (using `GetEndpoint()`) is powerful but can be verbose. This is exactly the problem that **Endpoint Filters** (which we'll cover in the Minimal API section) were designed to solve.

- **Middleware:** Runs on the **request pipeline**. It can be scoped to a path (`/api`), but it is harder to scope to a *specific* endpoint without manual checks (`GetEndpoint()`).
- **Endpoint Filter:** Is applied directly to an **endpoint or group of endpoints**. It is inherently endpoint-aware.

This distinction will become very clear in the next part.

### **Revised Summary of Middleware**

- **Branching:** Use `Map` and `MapWhen` to create separate, isolated middleware pipelines for different parts of your application.
- **Endpoint Awareness:** A middleware placed **after** `app.UseRouting()` can use `HttpContext.GetEndpoint()` to access the metadata of the selected controller action or minimal API endpoint, allowing for highly specific, conditional logic.
- **Terminal Middleware:** Middleware that doesn't call `next()` stops the pipeline (e.g., `app.Run()`).

Now that we have a deep understanding of the pipeline's structure and its branching/contextual capabilities, we are fully equipped for **Part 2: Mastering Minimal APIs**.

Ready to proceed?