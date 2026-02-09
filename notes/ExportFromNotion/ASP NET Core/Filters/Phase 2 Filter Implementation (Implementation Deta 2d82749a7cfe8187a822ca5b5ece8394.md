# Phase 2: Filter Implementation (Implementation Details)

Now that we understand the "why," we need to learn the "how." This phase is about the specific code patterns and attributes you'll use daily.

---

### **1. Implementation: Attribute vs. Registration**

**(Microsoft Docs Link:** [*Filter registration](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters#filter-scopes-and-order-of-execution))*

There are three places (scopes) you can apply a filter:

1. **Global Scope:** Affects every controller action in the entire application.
2. **Controller Scope:** Affects every action within a specific controller class.
3. **Action Scope:** Affects only a single action method.

### **The Code (`Program.cs` for Global Registration)**

Global filters are perfect for things you *always* want, like a global exception handler.

```csharp
builder.Services.AddControllers(options =>
{
    // Method 1: Add by Type. This filter CANNOT have constructor dependencies.
    // options.Filters.Add(new MySimpleFilter());

    // Method 2: Add by Type, letting DI create it. This filter CAN have dependencies.
    options.Filters.Add<MyDependencyInjectedFilter>();
});

```

### **The Code (Attributes for Controller/Action)**

Attributes are perfect for things that apply selectively, like a transaction boundary.

```csharp
[ApiController]
[MyControllerLevelFilter] // <-- Controller Scope
public class MyController : ControllerBase
{
    [HttpGet]
    [MyActionLevelFilter] // <-- Action Scope
    public IActionResult Get() { ... }
}

```

---

### **2. The Dependency Injection Problem & Solution**

**The Problem:**
An `[Attribute]` is created by the .NET runtime itself during compilation. **It cannot use constructor injection.**

**Novice Mistake:**

```csharp
public class BadFilterAttribute : Attribute, IActionFilter
{
    private readonly ILogger _logger;

    // THIS WILL CRASH! Attributes cannot have dependencies.
    public BadFilterAttribute(ILogger<BadFilterAttribute> logger)
    {
        _logger = logger;
    }
    // ...
}

```

**The Solutions:** `ServiceFilter` and `TypeFilter`.

### **A. `[ServiceFilter(typeof(MyFilter))]` (The Expert Standard)**

This is the cleanest and most common way to create a stateful filter. It decouples the filter logic from the attribute itself.

1. **Create the Filter Class (Pure C#):**
This class can now have dependencies.
    
    ```csharp
    public class MyAwesomeFilter : IActionFilter
    {
        private readonly ILogger<MyAwesomeFilter> _logger;
    
        public MyAwesomeFilter(ILogger<MyAwesomeFilter> logger) // <-- DI works!
        {
            _logger = logger;
        }
    
        public void OnActionExecuting(ActionExecutingContext context)
        {
            _logger.LogInformation("Executing with my awesome filter!");
        }
    
        public void OnActionExecuted(ActionExecutedContext context) { }
    }
    
    ```
    
2. **Register it in DI (`Program.cs`):**
You must register the filter itself as a service.
    
    ```csharp
    builder.Services.AddScoped<MyAwesomeFilter>();
    
    ```
    
3. **Apply it via the `ServiceFilter` Attribute:**`[ServiceFilter]` is a built-in attribute that acts as a bridge. It asks the DI container to resolve an instance of your filter.
    
    ```csharp
    [ApiController]
    [ServiceFilter(typeof(MyAwesomeFilter))]
    public class ValuesController : ControllerBase { ... }
    
    ```
    

### **B. `[TypeFilter(typeof(MyFilter))]`**

`TypeFilter` is almost identical to `ServiceFilter`.

- **Key Difference:** It resolves the type directly without you having to register it in `Program.cs`. It's less explicit, so `ServiceFilter` is generally preferred as it makes dependencies clearer.

---

### **3. Short-Circuiting the Pipeline**

**(Microsoft Docs Link:** [*Short-circuiting the filter pipeline](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters#cancellation-and-short-circuiting))*

Sometimes, a filter's job is to stop the request dead in its tracks. This is called **short-circuiting**.

**How it works:**
Inside any `...Executing` method (e.g., `OnActionExecuting`), you set the `context.Result`. Once a result is set, [ASP.NET](http://asp.net/) Core **skips all subsequent filters and the action method**. It immediately jumps to the "Result Execution" part of the pipeline.

**Classic Use Case: `ModelState` Validation**
This is so common, [ASP.NET](http://asp.net/) Core does it for you with `[ApiController]`, but here is how you would write it manually.

```csharp
public class ValidateModelAttribute : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context)
    {
        if (!context.ModelState.IsValid)
        {
            // The pipeline stops here. The Get() action below will NOT run.
            context.Result = new BadRequestObjectResult(context.ModelState);
        }
    }

    public void OnActionExecuted(ActionExecutedContext context) { }
}

```

---

### **4. Asynchronous Filters (`IAsyncActionFilter`)**

If your filter needs to `await` anything, you MUST use the async version of the interface.

**The Signature is Different:**
Instead of two separate methods (`Executing`, `Executed`), you get one method with a `next()` delegate.

```csharp
public class MyAsyncFilter : IAsyncActionFilter
{
    public async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        // 1. Code here runs BEFORE the action
        Console.WriteLine("Before the action...");

        // This is the "break" point
        // It calls the next filter in the chain, or the action itself.
        var resultContext = await next();

        // 3. Code here runs AFTER the action and can access the result
        // For example, checking if the result was an error
        if (resultContext.Exception != null)
        {
            Console.WriteLine("Action threw an exception!");
        }

        Console.WriteLine("After the action...");
    }
}

```

This "pass the delegate" pattern is fundamental to modern .NET middleware and filters.

---

### **Summary of Phase 2**

1. **Scope:** Use `options.Filters.Add` for **Global** filters. Use attributes for **Controller/Action** filters.
2. **DI is Key:** If your filter needs a `DbContext` or `ILogger`, you must use `[ServiceFilter]` and register the filter class in `Program.cs`.
3. **Short-Circuit:** Set `context.Result` inside an `...Executing` method to stop the request immediately.
4. **Async is the Default:** When in doubt, implement the `IAsync...Filter` version. It handles both sync and async code gracefully.

Are you ready for **Phase 3: The Specific Filter Types**? (We will build practical examples for each of the five filter types).