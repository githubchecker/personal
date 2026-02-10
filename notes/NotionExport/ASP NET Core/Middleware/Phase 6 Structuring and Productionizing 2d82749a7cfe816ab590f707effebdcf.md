# Phase 6: Structuring and Productionizing

This phase is about applying architectural patterns to your minimal API to keep it from becoming a single, massive, unreadable `Program.cs` file.

---

### **1. Endpoint Grouping (`MapGroup`)**

As your API grows, you'll have dozens of `app.Map...()` calls. Grouping them makes your code more organized and allows you to apply common configurations to a set of related endpoints.

**The "Messy" Way (Without Groups):**

```csharp
app.MapGet("/products", ...).RequireAuthorization("read_access");
app.MapGet("/products/{id}", ...).RequireAuthorization("read_access");
app.MapPost("/products", ...).RequireAuthorization("write_access");

app.MapGet("/orders", ...).RequireAuthorization("read_access");
app.MapGet("/orders/{id}", ...).RequireAuthorization("read_access");
app.MapPost("/orders", ...).RequireAuthorization("write_access");

```

**The "Clean" Way (With `MapGroup`):**
The `MapGroup` method creates a builder that allows you to configure a common prefix and apply shared middleware or filters to all endpoints within the group.

```csharp
// --- Product Endpoints ---
var productsApi = app.MapGroup("/products")
    .WithTags("Products API"); // Group in Swagger UI

// Apply a read policy to all GET endpoints in this group
productsApi.MapGet("/", ...).RequireAuthorization("read_access");
productsApi.MapGet("/{id}", ...).RequireAuthorization("read_access");

// Apply a write policy to POST
productsApi.MapPost("/", ...).RequireAuthorization("write_access");

// --- Order Endpoints ---
var ordersApi = app.MapGroup("/orders")
    .WithTags("Orders API")
    .RequireAuthorization(); // Secure all endpoints in this group by default

// This endpoint is at GET /orders and requires auth
ordersApi.MapGet("/", ...);
// This endpoint is at GET /orders/{id} and requires auth
ordersApi.MapGet("/{id}", ...);
// This endpoint is at POST /orders and requires auth
ordersApi.MapPost("/", ...);

```

---

### **2. Endpoint Filters (`IEndpointFilter`)**

This is the **minimal API equivalent of MVC Action Filters**. It's a powerful way to implement cross-cutting concerns like validation or logging for a specific endpoint or group without writing full middleware.

**The Scenario:** You want to validate a `ProductDto` before it's processed, but you're using a minimal validation library instead of FluentValidation's automatic integration.

**Step 1: Create the Filter Class**
An endpoint filter is a class that implements `IEndpointFilter`. The `InvokeAsync` method gives you the context and a `next` delegate.

```csharp
public class ProductValidationFilter : IEndpointFilter
{
    private readonly IValidator<ProductDto> _validator;

    public ProductValidationFilter(IValidator<ProductDto> validator)
    {
        _validator = validator;
    }

    public async ValueTask<object?> InvokeAsync(EndpointFilterInvocationContext context, EndpointFilterDelegate next)
    {
        // 1. Find the argument to validate
        var productDto = context.GetArgument<ProductDto>(0); // Get the first argument

        var validationResult = await _validator.ValidateAsync(productDto);

        if (!validationResult.IsValid)
        {
            // 2. Short-circuit the request if validation fails
            return Results.ValidationProblem(validationResult.ToDictionary());
        }

        // 3. Call the next filter or the endpoint handler itself
        return await next(context);
    }
}

```

**Step 2: Apply the Filter**
You can apply filters to individual endpoints or to an entire group.

```csharp
var productsApi = app.MapGroup("/products");

// Apply the filter to a single endpoint
productsApi.MapPost("/", (ProductDto product) => { /* create logic */ })
           .AddEndpointFilter<ProductValidationFilter>();

// Or, apply a filter to ALL endpoints in the group
var secureGroup = app.MapGroup("/secure").AddEndpointFilter<MyAuthFilter>();

```

---

### **3. Authentication and Authorization**

Securing endpoints is done with a fluent API, which is much cleaner than attributes in many cases.

**Applying Authorization:**

```csharp
// This endpoint is public
app.MapGet("/public", () => "Hello, public world!");

// This endpoint requires any authenticated user
app.MapGet("/private", () => "Hello, authenticated user!")
   .RequireAuthorization();

// This endpoint requires the user to have the "Admin" role
app.MapGet("/admin", () => "Hello, admin!")
   .RequireAuthorization(policy => policy.RequireRole("Admin"));

// This endpoint uses a pre-defined policy from Program.cs
app.MapGet("/vip", () => "Hello, VIP!")
   .RequireAuthorization("VipPolicy");

```

---

### **4. OpenAPI (Swagger) Integration**

To make your minimal API usable, you need good documentation. You can provide rich metadata for Swagger/OpenAPI using extension methods.

```csharp
app.MapPost("/products", (ProductDto product) => { /* logic */ })
   .WithName("CreateProduct") // Sets the unique OperationId for code generation
   .WithTags("Products API")  // Groups it in the Swagger UI
   .WithSummary("Creates a new product.")
   .WithDescription("Creates a new product in the catalog from the provided data.")
   .Produces<Product>(StatusCodes.Status201Created) // Describes a successful response
   .Produces(StatusCodes.Status400BadRequest)       // Describes a possible error response
   .WithOpenApi(operation =>
   {
        // For advanced, direct manipulation of the OpenAPI operation object
        operation.Deprecated = true;
        return operation;
   });

```

---

### **5. Testing Minimal APIs**

Testing minimal APIs is a first-class experience using `WebApplicationFactory`. This class from the `Microsoft.AspNetCore.Mvc.Testing` package allows you to create an in-memory test server that runs your application's pipeline.

**Example: An Integration Test using xUnit**

```csharp
public class ProductsApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public ProductsApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task GetProducts_ReturnsSuccessStatusCode()
    {
        // ARRANGE
        // Create an HttpClient that sends requests to your in-memory app
        var client = _factory.CreateClient();

        // ACT
        var response = await client.GetAsync("/products");

        // ASSERT
        response.EnsureSuccessStatusCode(); // Throws if status code is not 2xx
        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("ProductName", content);
    }

    [Fact]
    public async Task GetProduct_WithInvalidId_ReturnsNotFound()
    {
        // ARRANGE
        var client = _factory.CreateClient();

        // ACT
        var response = await client.GetAsync("/products/999");

        // ASSERT
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}

```

### **Summary of Phase 5**

- Use **`MapGroup`** to structure your endpoints, apply common prefixes, and share configuration.
- Use **`IEndpointFilter`** as the lightweight, modern equivalent of MVC action filters for validation and other cross-cutting concerns at the endpoint level.
- Secure your endpoints fluently with **`.RequireAuthorization()`**.
- Document your API with methods like **`.WithTags()`**, **`.WithSummary()`**, and **`.Produces()`** for rich Swagger/OpenAPI integration.
- Write robust integration tests using **`WebApplicationFactory`** to test your entire pipeline in memory.

You have now completed the entire journey, from understanding the core middleware pipeline to building, structuring, and testing production-ready minimal APIs in [ASP.NET](http://asp.net/) Core.