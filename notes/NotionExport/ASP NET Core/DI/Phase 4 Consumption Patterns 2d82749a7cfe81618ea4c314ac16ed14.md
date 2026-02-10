# Phase 4: Consumption Patterns

While there are several ways to get a dependency, there is one strongly preferred pattern and a few others that are useful in specific scenarios (or should be avoided).

---

### **1. Constructor Injection (The Standard & Preferred Pattern)**

This is the primary, most common, and cleanest way to receive dependencies.

**The Pattern:** A class declares the services it needs as parameters in its public constructor.

```csharp
public class ProductService : IProductService
{
    private readonly IRepository<Product> _productRepository;
    private readonly ILogger<ProductService> _logger;

    // The class states its dependencies upfront.
    public ProductService(IRepository<Product> productRepository, ILogger<ProductService> logger)
    {
        // Guard clauses are a good practice to ensure dependencies are not null.
        _productRepository = productRepository ?? throw new ArgumentNullException(nameof(productRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task CreateProductAsync(Product product)
    {
        // The service can now use its dependencies throughout its lifetime.
        _logger.LogInformation("Creating a new product...");
        await _productRepository.AddAsync(product);
    }
}

```

**Why it's the Best Pattern:**

1. **Explicit Dependencies:** It's immediately clear what a class needs to function just by looking at its constructor signature. There are no hidden dependencies.
2. **Guaranteed Availability:** The object cannot be constructed without its required dependencies. You'll never have a `NullReferenceException` because a dependency wasn't provided (assuming you have guard clauses).
3. **Testability:** In a unit test, you can easily pass in mock implementations of `IRepository<Product>` and `ILogger` to the constructor, giving you full control over the test environment.
4. **Immutability:** Dependencies are typically stored in `readonly` fields, preventing them from being changed after the object is created, which leads to more predictable behavior.

---

### **2. Action Method Injection (`[FromServices]`)**

Sometimes, a dependency is only needed for a single action method and not by the entire controller. Injecting it into the constructor might feel like "polluting" the class, especially if it's a large controller with many actions.

Action Method Injection allows you to request a service directly as a parameter to an action method.

**The Pattern:** You add the service interface as a parameter to your MVC Action or Minimal API handler and decorate it with the `[FromServices]` attribute.

**Example in an MVC Controller:**

```csharp
[ApiController]
[Route("[controller]")]
public class ReportsController : ControllerBase
{
    // Note: The constructor is clean, no IReportGenerator here.
    public ReportsController() { }

    [HttpGet("generate-pdf")]
    public IActionResult GeneratePdfReport([FromServices] IPdfGeneratorService pdfGenerator)
    {
        // The 'pdfGenerator' is resolved by the DI container only for this request.
        // It has a 'Scoped' lifetime, tied to this HTTP request.
        var pdfBytes = pdfGenerator.Generate();
        return File(pdfBytes, "application/pdf", "report.pdf");
    }

    [HttpGet("generate-csv")]
    public IActionResult GenerateCsvReport([FromServices] ICsvGeneratorService csvGenerator)
    {
        var csvContent = csvGenerator.Generate();
        return Content(csvContent);
    }
}

```

**Why use it?**

- It's a good choice when a service is "heavy" and only used in one out of ten actions in a controller. This can make the class's primary dependencies clearer.

**Why avoid it?**

- It can slightly obscure the full dependency graph of a class. Someone reading the constructor might not realize the class has other dependencies. Use it judiciously for non-critical or action-specific helpers.

---

### **3. `HttpContext.RequestServices` (The Service Locator Anti-Pattern)**

This pattern allows you to manually request a service from the DI container at any point where you have access to the `HttpContext`. It's known as the **Service Locator** pattern.

**The Pattern:**

```csharp
// Inside middleware, a filter, or a controller action...
var myService = httpContext.RequestServices.GetRequiredService<IMyService>();

// 'GetRequiredService' throws an exception if the service isn't registered.
// 'GetService' returns null if the service isn't registered.

```

**Why it's an Anti-Pattern and Should Be Avoided:**

1. **Hidden Dependencies:** This code violates the principle of explicit dependencies. A class can now secretly grab any service it wants from the container without declaring it in the constructor. This makes the code harder to reason about and understand.
    
    ```csharp
    public class MyBadService
    {
        private readonly IHttpContextAccessor _httpContextAccessor;
        public MyBadService(IHttpContextAccessor httpContextAccessor)
        {
            _httpContextAccessor = httpContextAccessor;
        }
    
        public void DoWork()
        {
            // SECRET DEPENDENCY! This class needs ILogger, but you'd never
            // know by looking at its constructor.
            var logger = _httpContextAccessor.HttpContext.RequestServices.GetRequiredService<ILogger>();
            logger.LogInformation("Doing work...");
        }
    }
    
    ```
    
2. **Difficult to Test:** To unit test `MyBadService`, you now have to mock the entire `IHttpContextAccessor`, `HttpContext`, `RequestServices`, and finally the `ILogger`. This is far more complex than just passing in a mock logger via the constructor.

**When is it (Rarely) Acceptable?**

- In static helper classes or extension methods where you cannot use constructor injection.
- In the `Program.cs` file during application startup to resolve a service needed for configuration.

In general, if you find yourself reaching for `RequestServices`, stop and ask, "Can I refactor this to use Constructor Injection instead?" The answer is almost always yes.

---

### **Summary of Consumption Patterns**

| Pattern | How it Works | Pros | Cons | Recommendation |
| --- | --- | --- | --- | --- |
| **Constructor Injection** | Dependencies are parameters of the constructor. | Explicit, testable, guarantees availability. | Can lead to large constructors if a class does too much. | **Use this 99% of the time.** |
| **Action Method Injection** | `[FromServices]` on an action parameter. | Good for action-specific, non-critical dependencies. | Hides dependencies from the constructor signature. | Use judiciously for helpers. |
| **Service Locator** | `HttpContext.RequestServices.GetService<T>()` | Works anywhere you have `HttpContext`. | **Anti-Pattern.** Hides dependencies, makes testing difficult. | **Avoid whenever possible.** |

Are you ready to move to the new .NET 8 feature, **Phase 5: Keyed Services**?