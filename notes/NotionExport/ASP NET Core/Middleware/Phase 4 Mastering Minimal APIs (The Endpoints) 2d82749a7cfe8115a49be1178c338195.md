# Phase 4: Mastering Minimal APIs (The Endpoints)

*(Microsoft Docs Entry Point: [Tutorial: Create a minimal web API with ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/tutorials/min-api))*

Minimal APIs, introduced in .NET 6, provide a streamlined, low-ceremony way to build fast and lightweight HTTP APIs. They are an alternative to using full MVC controllers.

---

### **The Basics of Endpoints**

### **1. `Program.cs` as the Entry Point**

In the new hosting model, your entire application is configured and run from `Program.cs`. This is made possible by a C# feature called "top-level statements," which eliminates the need for a `Main` method and `Startup` class.

The two key objects are:

- `WebApplicationBuilder builder`: Used to configure services for Dependency Injection (DI).
- `WebApplication app`: Used to configure the middleware pipeline and define endpoints.

```csharp
// 1. Setup DI, Configuration, Logging, etc.
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IProductService, ProductService>();

// 2. Build the app (which gives you the middleware pipeline host)
var app = builder.Build();

// 3. Configure the pipeline and map endpoints
app.MapGet("/", () => "Hello World!");

// 4. Run the app
app.Run();

```

### **2. Routing with `Map...` Methods**

Instead of using attributes in a controller class (`[HttpGet]`, `[HttpPost]`), you define your routes directly on the `WebApplication` object.

- **`MapGet(pattern, handler)`**
- **`MapPost(pattern, handler)`**
- **`MapPut(pattern, handler)`**
- **`MapDelete(pattern, handler)`**

The `handler` is a delegate (usually a lambda expression) that contains your endpoint's logic.

**Example: A Simple CRUD API**

```csharp
// GET /products
app.MapGet("/products", () => { /* get all products */ });

// GET /products/123
app.MapGet("/products/{id}", (int id) => { /* get product with specific id */ });

// POST /products
app.MapPost("/products", (ProductDto product) => { /* create a new product */ });

// PUT /products/123
app.MapPut("/products/{id}", (int id, ProductDto product) => { /* update a product */ });

// DELETE /products/123
app.MapDelete("/products/{id}", (int id) => { /* delete a product */ });

```

**Route Parameter Constraints:**
You can add constraints just like in MVC to help the routing engine.

```csharp
// This route will only match if 'id' is a valid integer.
app.MapGet("/products/{id:int}", (int id) => { /* ... */ });

```

### **3. Dependency Injection in Handlers**

This is one of the most powerful features of Minimal APIs. You can request any service registered in the DI container simply by adding it as a parameter to your route handler lambda. The framework will automatically inject it for you.

**Example: Injecting a Service and `HttpContext`**

```csharp
// In Program.cs
builder.Services.AddScoped<IProductService, ProductService>();

// The endpoint handler
app.MapGet("/products", (IProductService productService, HttpContext httpContext) =>
{
    // The framework provides instances of both.
    var userAgent = httpContext.Request.Headers.UserAgent;
    var products = productService.GetAll();
    return products;
});

```

For clarity, especially when you have many injected parameters, you can use the `[FromServices]` attribute, but it's not required.

```csharp
app.MapGet("/products", ([FromServices] IProductService service) => { /* ... */ });

```

### **4. Returning Responses (`Results` class)**

While you *can* return a raw object (which defaults to a `200 OK` with a JSON body), it's best practice to be explicit about your HTTP status codes.

The `Microsoft.AspNetCore.Http.Results` static class provides helper methods for this. This is the Minimal API equivalent of `Ok()`, `NotFound()`, and `BadRequest()` in a `ControllerBase`.

**Example: Handling Different Outcomes**

```csharp
app.MapGet("/products/{id:int}", (int id, IProductService service) =>
{
    var product = service.GetById(id);

    if (product == null)
    {
        // Returns a 404 Not Found status code
        return Results.NotFound(new { Message = $"Product with ID {id} not found." });
    }

    // Returns a 200 OK with the product as a JSON body
    return Results.Ok(product);
});

```

**Common `Results` helpers:**

- `Results.Ok(object)`
- `Results.NotFound()`
- `Results.BadRequest(object)`
- `Results.NoContent()` (for `204 No Content`)
- `Results.Problem()` (for detailed `500` errors, RFC 7807 compliant)
- `Results.Accepted()` (for `202 Accepted`)
- `Results.Redirect()`

---

### **Summary of Phase 4**

- All configuration and routing now live in `Program.cs`.
- You use `MapGet`, `MapPost`, etc., to define your API's routes.
- **Dependency Injection is done via method parameters** in your lambda handlers.
- Use the `Results` static class to be explicit about your HTTP status codes and responses.

Are you ready to move to **Phase 4: Advanced Input & Output**, where we'll cover model binding in more detail and introduce strongly typed results?