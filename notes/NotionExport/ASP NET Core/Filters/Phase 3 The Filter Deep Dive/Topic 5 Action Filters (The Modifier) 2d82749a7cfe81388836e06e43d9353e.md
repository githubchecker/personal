# Topic 5: Action Filters (The Modifier)

The **Action Filter** is the most commonly used custom filter because it has the most intimate access to the `Action Method` itself.

**Its Position:**

- Runs **after** Model Binding. (So you have a fully populated C# object to inspect).
- Runs **just before** the action method is invoked.
- Runs **just after** the action method completes, giving you access to its `Result`.

This "inside the sandwich" position makes it the perfect place to **modify**, **validate**, or **log** data directly related to a controller action.

---

### **1. The Interfaces: `IActionFilter` and `IAsyncActionFilter`**

As always, the async version is preferred and uses the `next()` delegate model, which is ideal for wrapping logic.

- `IActionFilter`
    - `OnActionExecuting(ActionExecutingContext context)`
    - `OnActionExecuted(ActionExecutedContext context)`
- `IAsyncActionFilter` (Recommended)
    - `OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)`

The `ActionExecutingContext` is rich with information:

- `context.ActionArguments`: A dictionary of the parameters about to be passed to your action method.
- `context.ModelState`: The result of the model validation.
- `context.Controller`: A castable instance of the controller class itself.
- `context.Result`: Can be set to short-circuit the action.

---

### **2. Production Use Case 1: Advanced Input Manipulation**

Model Binding is great, but sometimes you need to perform custom logic on the input before your action method sees it.

**The Goal:** Automatically trim all leading/trailing whitespace from string properties in any incoming DTO (Data Transfer Object). This prevents users from submitting `" John "` instead of `"John"`.

**The Filter Code:**

```csharp
public class TrimStringsActionFilter : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context)
    {
        // Loop through all the arguments that will be passed to the action method.
        foreach (var argument in context.ActionArguments)
        {
            // If the argument is a simple string, trim it.
            if (argument.Value is string str)
            {
                context.ActionArguments[argument.Key] = str?.Trim();
            }
            // If it's a complex object (like a DTO), we can use reflection to find
            // and trim all its string properties.
            else if (argument.Value is object obj)
            {
                // Find all string properties that can be written to.
                var stringProperties = obj.GetType().GetProperties()
                    .Where(p => p.PropertyType == typeof(string) && p.CanWrite);

                foreach (var prop in stringProperties)
                {
                    var value = (string)prop.GetValue(obj);
                    prop.SetValue(obj, value?.Trim());
                }
            }
        }
    }

    public void OnActionExecuted(ActionExecutedContext context) { }
}

```

**Usage:** You can register this globally in `Program.cs` to automatically sanitize string inputs for your entire API.

---

### **3. Production Use Case 2: Custom Validation & `ModelState`**

While `[ApiController]` handles `ModelState` validation automatically, an Action Filter gives you more control.

**The Goal:** Your API has a business rule that `StartDate` must always be before `EndDate`. This is cross-property validation that standard data attributes can't easily handle.

**The Filter Code:**

```csharp
public class DateRangeValidationFilter : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context)
    {
        // Find the DTO argument from the action parameters.
        if (context.ActionArguments.TryGetValue("request", out var value) && value is DateRangeRequestDto dto)
        {
            if (dto.StartDate > dto.EndDate)
            {
                // Manually add an error to ModelState.
                context.ModelState.AddModelError(nameof(dto.EndDate), "End Date cannot be before Start Date.");
            }
        }

        // Now, check the ModelState and short-circuit if it's invalid.
        if (!context.ModelState.IsValid)
        {
            context.Result = new BadRequestObjectResult(context.ModelState);
        }
    }

    public void OnActionExecuted(ActionExecutedContext context) { }
}

```

**Usage (as an attribute on a specific action):**

```csharp
[HttpPost]
[ServiceFilter(typeof(DateRangeValidationFilter))] // Apply the custom check
public IActionResult ProcessDateRange([FromBody] DateRangeRequestDto request)
{
    // If code reaches here, you are guaranteed the dates are in the correct order.
    return Ok();
}

```

---

### **4. Production Use Case 3: Accessing Controller Properties**

Sometimes a filter needs information from the controller it's attached to.

**The Goal:** A filter that only runs if a specific public property on the controller is set to `true`.

**The Controller:**

```csharp
[ApiController]
public class AdvancedController : ControllerBase
{
    // This property can be used to control filter behavior.
    public bool EnableAdvancedLogging { get; set; } = true;

    // ... actions
}

```

**The Filter Code:**

```csharp
public class ConditionalLoggingFilter : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context)
    {
        // Safely cast the controller instance.
        if (context.Controller is AdvancedController controller)
        {
            if (controller.EnableAdvancedLogging)
            {
                // Do some advanced logging...
                Console.WriteLine("Advanced logging is enabled for this action.");
            }
        }
    }

    public void OnActionExecuted(ActionExecutedContext context) { }
}

```

This pattern allows for highly dynamic and context-aware filter logic.

---

### **Summary of Action Filters**

| Feature | Description |
| --- | --- |
| **Position** | Just before and just after the action method runs. |
| **Key Context** | `context.ActionArguments` (the inputs), `context.ModelState`, `context.Controller`. |
| **Best Use Cases** | **Input manipulation** (sanitization), **complex validation**, performance logging for specific actions, conditional logic based on controller state. |
| **Short-Circuiting?** | Yes. It's the standard place to check `ModelState` and return a `400 Bad Request`. |

The Action Filter is the most precise tool for interacting with the data and logic of a specific controller endpoint.

Are you ready for the final filter, **Topic 6: Result Filters (The Formatter)**, where we'll learn how to globally shape your API's output?