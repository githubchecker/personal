# Phase 3: Registration Techniques

### **1. Standard Registration (Interface to Implementation)**

This is the bread and butter of DI registration. You map an abstraction (an interface) to a concrete implementation.

**The Syntax:**

```csharp
// In Program.cs
// "When a class asks for IProductService, give it an instance of ProductService."
builder.Services.AddScoped<IProductService, ProductService>();

// "When a class asks for ILogger, the framework knows how to provide a logger instance."
// This is done automatically by builder.Build() and logging providers.

```

You can also register a concrete type without an interface if it will be requested directly.

```csharp
// This is less common but valid. Another class could have `MyConcreteService` in its constructor.
builder.Services.AddScoped<MyConcreteService>();

```

This is equivalent to: `builder.Services.AddScoped<MyConcreteService, MyConcreteService>();`.

---

### **2. Factory-Based Registration**

Sometimes, creating an instance of a service isn't as simple as calling its constructor. You might need to perform some logic, read from configuration, or use other services to construct it. A factory delegate is perfect for this.

**The Use Case:** You have a service that needs a specific API key from your `appsettings.json`.

**`appsettings.json`:**

```json
{
  "ExternalApiService": {
    "ApiKey": "ABC-123-XYZ"
  }
}

```

**The Service and `Program.cs`:**

```csharp
public class ExternalApiService
{
    private readonly HttpClient _httpClient;
    // The constructor needs a simple string, not the whole IConfiguration.
    public ExternalApiService(HttpClient httpClient, string apiKey)
    {
        _httpClient = httpClient;
        _httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
    }
    // ...
}

// In Program.cs
builder.Services.AddHttpClient<ExternalApiService>(); // Registers the HttpClient part

builder.Services.AddScoped<ExternalApiService>(provider =>
{
    // 1. Get the services needed to build our service.
    // The 'provider' is an IServiceProvider that can resolve other dependencies.
    var configuration = provider.GetRequiredService<IConfiguration>();
    var httpClientFactory = provider.GetRequiredService<IHttpClientFactory>();

    // 2. Perform the custom logic.
    var apiKey = configuration["ExternalApiService:ApiKey"];
    var client = httpClientFactory.CreateClient();

    // 3. Manually construct the service and return it.
    return new ExternalApiService(client, apiKey);
});

```

The factory lambda `(provider => ...)` gives you a powerful hook to control exactly how an object is created.

---

### **3. Registering Open Generics**

This is an advanced but incredibly powerful pattern, especially for data access or messaging.

**The Scenario:** You have a generic repository interface to abstract your data access.

```csharp
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task AddAsync(T entity);
    // ...
}

public class EfRepository<T> : IRepository<T> where T : class
{
    private readonly AppDbContext _db;
    public EfRepository(AppDbContext db) { _db = db; }
    // ... implement methods
}

```

**The "Bad" Way (Repetitive):**
You could register each repository one by one. This is tedious and error-prone.

```csharp
builder.Services.AddScoped<IRepository<Product>, EfRepository<Product>>();
builder.Services.AddScoped<IRepository<Order>, EfRepository<Order>>();
builder.Services.AddScoped<IRepository<Customer>, EfRepository<Customer>>();
// ... 50 more lines ...

```

**The "Expert" Way (Open Generic Registration):**
You tell the DI container how to handle *any* request for `IRepository<T>`.

```csharp
// "When someone asks for IRepository<T>, create an EfRepository<T> for them."
builder.Services.AddScoped(typeof(IRepository<>), typeof(EfRepository<>));

```

Now, if a `ProductService` asks for `IRepository<Product>`, the container knows to create an `EfRepository<Product>`. If a `CustomerService` asks for `IRepository<Customer>`, it will create an `EfRepository<Customer>`. You write one line of registration for infinite possibilities.

---

### **4. Assembly Scanning (Automated Registration)**

In very large applications, manually registering dozens or hundreds of services in `Program.cs` becomes cumbersome. You can automate this process.

While [ASP.NET](http://asp.net/) Core's built-in DI container doesn't have a native "scan" feature, the popular and Microsoft-blessed library **Scrutor** provides this functionality.

**Step 1: Install Scrutor**

```bash
dotnet add package Scrutor

```

**Step 2: Use Scrutor in `Program.cs`**
Let's say you have a convention that all your service implementations are in an assembly named `MyProject.Application` and end with the word "Service".

```csharp
// In Program.cs
builder.Services.Scan(scan => scan
    // 1. Tell it which assembly to look in.
    .FromAssemblyOf<ProductService>()

    // 2. Find all public classes that end with "Service".
    .AddClasses(classes => classes.Where(c => c.Name.EndsWith("Service")))

    // 3. Register them against their implemented interface (e.g., ProductService as IProductService).
    .AsImplementedInterfaces()

    // 4. Give them a Scoped lifetime.
    .WithScopedLifetime()
);

```

This single block of code can replace hundreds of `builder.Services.AddScoped...()` lines, making your registration process convention-based and automatic.

---

### **Summary of Registration Techniques**

| Technique | When to Use |
| --- | --- |
| **Standard (`Add...<I, T>`)** | The default for 90% of cases. Simple and explicit. |
| **Factory (`Add...(provider => ...)` )** | When service creation requires logic, configuration values, or is complex. |
| **Open Generics (`typeof(I<>)`)** | When you have a generic abstraction, like a repository or a handler. |
| **Assembly Scanning (`Scrutor`)** | In large, convention-driven projects to automate the registration of many services at once. |

Are you ready to move to **Phase 4: Consumption Patterns**, where we'll look at the different ways services are requested from the container?