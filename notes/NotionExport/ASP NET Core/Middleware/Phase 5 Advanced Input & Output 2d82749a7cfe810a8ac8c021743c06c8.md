# Phase 5: Advanced Input & Output

This phase focuses on how to cleanly bind incoming request data to your C# models and how to return strongly typed, well-documented responses.

---

### **1. Model Binding in Minimal APIs**

Minimal APIs use the same underlying model binding engine as MVC, but with a more streamlined inference model. The `[From...]` attributes work here too.

**Binding Source Inference:**
The rules are simple and predictable:

1. **`[FromBody]`:** A parameter is bound from the body if it's a complex type (a `class` or `record`), or if it's explicitly marked with `[FromBody]`. You can still only have one.
2. **`[FromRoute]`:** A parameter is bound from the route if its name matches a route parameter (e.g., `{id}`).
3. **`[FromServices]`:** The parameter is resolved from the DI container.
4. **Special Types:** `HttpContext`, `HttpRequest`, `HttpResponse`, `ClaimsPrincipal` are injected by the framework.
5. **Everything Else:** Any other parameter is assumed to be **`[FromQuery]`**.

**Example Combining Sources:**

```csharp
app.MapPut("/products/{id}", (
    int id,                               // Inferred [FromRoute]
    [FromBody] ProductUpdateDto product,  // Explicitly [FromBody]
    [FromHeader(Name = "X-User-Id")] string userId, // Explicitly [FromHeader]
    IProductService service,              // Inferred [FromServices]
    bool preview = false                  // Inferred [FromQuery] (from ?preview=true)
) =>
{
    // ... logic ...
});

```

### **The Power of `[AsParameters]`**

As your endpoints get more complex, the parameter list can become unwieldy. The `[AsParameters]` attribute (introduced in .NET 7) allows you to consolidate your input parameters into a single class or struct.

**The "Cluttered" Way:**

```csharp
app.MapGet("/products", (
    [FromQuery] string? filter,
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 10,
    [FromServices] IProductService service) => { /* ... */ });

```

**The "Clean" Way with `[AsParameters]`:Step 1: Define the Parameter Object**

```csharp
public class ProductQuery
{
    [FromQuery] public string? Filter { get; set; }
    [FromQuery] public int Page { get; set; } = 1;
    [FromQuery] public int PageSize { get; set; } = 10;

    // You can even inject services into the parameter object itself!
    [FromServices] public IProductService Service { get; set; }
}

```

**Step 2: Use in the Endpoint Handler**

```csharp
app.MapGet("/products", ([AsParameters] ProductQuery query) =>
{
    // Access parameters and services through the query object
    var products = query.Service.Search(query.Filter, query.Page, query.PageSize);
    return Results.Ok(products);
});

```

---

### **2. Typed Results (`IResult`)**

Returning `object` or `Results.Ok(myObject)` works, but it's not ideal for compile-time safety or documentation. `IResult` is the interface that all helpers in the `Results` class implement.

**The Problem with `Results.Ok()`:**
The compiler sees the return type as `IResult`. It doesn't know *what kind* of `Ok` result it is, so it doesn't know the type of the object being returned. This makes tooling (like Swagger/OpenAPI) have to work harder to infer the response.

**The Solution: Strongly Typed Results**
By being explicit about all possible return types, you improve documentation, testability, and get better compile-time checks.

The generic `Results<T1, T2, ...>` type is used for this.

**Before (Ambiguous Return Type):**

```csharp
app.MapGet("/products/{id}", (int id, IProductService service) =>
{
    var product = service.GetById(id);
    if (product == null)
    {
        return Results.NotFound(); // IResult
    }
    return Results.Ok(product); // Also IResult
});

```

**After (Strongly Typed Return Type):**

```csharp
// The compiler now knows this endpoint can return either a 200 OK with a Product, or a 404 NotFound.
app.MapGet("/products/{id}", async (int id, IProductService service) =>
{
    var product = await service.GetByIdAsync(id);
    if (product == null)
    {
        // Results.NotFound() returns a concrete 'NotFound' type
        return TypedResults.NotFound();
    }
    // TypedResults.Ok(product) returns a concrete 'Ok<Product>' type
    return TypedResults.Ok(product);
})
.Produces<Product>(StatusCodes.Status200OK) // Explicitly document the success case
.Produces(StatusCodes.Status404NotFound);    // Explicitly document the failure case

```

*Note: We use `TypedResults` for the strongly typed helpers.*

**Benefits:**

1. **OpenAPI Documentation:** The `.Produces()` extension methods provide explicit metadata for Swagger/OpenAPI, generating a much more accurate API spec.
2. **Testability:** In an integration test, you can now assert the specific `IResult` type.
    
    ```csharp
    var result = await client.GetAsync("/products/999");
    Assert.IsAssignableFrom<NotFound>(result);
    
    ```
    

---

### **3. File Uploads and Downloads**

Minimal APIs provide first-class support for handling files.

### **File Uploads with `IFormFile` and `IFormFileCollection`**

This works almost identically to MVC. The endpoint expects a `multipart/form-data` request.

```csharp
app.MapPost("/uploads", (IFormFileCollection files) =>
{
    foreach (var file in files)
    {
        // Process each file (save to disk, stream to blob storage, etc.)
        Console.WriteLine($"Received file: {file.FileName} ({file.Length} bytes)");
    }
    return Results.Ok(new { FileCount = files.Count });
});

```

### **File Downloads with `Results.File()`**

The `Results.File()` helper provides several overloads for returning file content.

**Example: Streaming a file from Azure Blob Storage**

```csharp
app.MapGet("/downloads/{fileName}", async (string fileName, IBlobStorageService blobService) =>
{
    // Get a stream to the blob
    var fileStream = await blobService.GetFileStreamAsync(fileName);
    if (fileStream == null)
    {
        return Results.NotFound();
    }

    // Return the stream directly. The framework handles streaming it to the client.
    // This is memory-efficient as it doesn't load the whole file into RAM.
    return Results.File(fileStream, contentType: "application/octet-stream", fileDownloadName: fileName);
});

```

---

### **Summary of Phase 5**

- Minimal API model binding is **predictable** (Body -> Route -> Services -> Query).
- Use **`[AsParameters]`** to group multiple inputs and clean up your endpoint signatures.
- Return **strongly typed results** (e.g., `Results<Ok<Product>, NotFound>`) to enable better tooling and testing.
- Use `IFormFile` for uploads and `Results.File()` for downloads to handle binary data efficiently.

Are you ready to proceed to the final **Phase 5: Structuring and Productionizing**, where we'll cover endpoint grouping, filters, and security?