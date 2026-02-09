# Phase 2: Accessing Configuration (Reading the Values)

Of course. Now that we understand how `IConfiguration` is built, let's explore the practical ways your C# code can read those values. This phase will introduce the **Options Pattern**, which is the recommended approach for modern, strongly-typed configuration.

---

### **1. Basic Access with `IConfiguration` (The "Magic String" Method)**

This is the simplest way to read a value. You inject `IConfiguration` and use its indexer, similar to a dictionary.

**The Drawback:** This approach uses "magic strings" (like `"MySettings:ApiKey"`). If you misspell a string or the key in `appsettings.json` changes, your code will fail silently at runtime (returning `null`), and the compiler won't be able to help you.

**Example:**
Assume `appsettings.json` has:

```json
{
  "MySettings": {
    "ApiKey": "ABC-123"
  }
}

```

**The Controller:**

```csharp
public class LegacySettingsController : ControllerBase
{
    private readonly IConfiguration _configuration;

    public LegacySettingsController(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [HttpGet]
    public IActionResult GetApiKey()
    {
        // Direct access using a string key. Prone to typos.
        string apiKey = _configuration["MySettings:ApiKey"];

        // A slightly better way with type conversion.
        int timeout = _configuration.GetValue<int>("MySettings:TimeoutSeconds", 30); // 30 is a default value

        if (string.IsNullOrEmpty(apiKey))
        {
            return Problem("API Key not configured.");
        }

        return Ok(new { ApiKey = apiKey, Timeout = timeout });
    }
}

```

While quick for simple lookups, this pattern becomes unmaintainable in large applications.

---

### **2. The Options Pattern (`IOptions<T>`): The Gold Standard**

*(Microsoft Docs Entry Point: [Options pattern in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options))*

The Options Pattern solves the "magic string" problem by using **strongly-typed C# classes** to represent your configuration sections. This provides compile-time checking and IntelliSense.

### **Step 1: Create the Options Class**

Create a POCO (Plain Old C# Object) class whose property names **exactly match** the keys in your JSON configuration section.

**`appsettings.json`:**

```json
{
  "MyApiSettings": {
    "Url": "<https://api.contoso.com>",
    "TimeoutSeconds": 60,
    "RetryAttempts": 3
  }
}

```

**The C# Class:**

```csharp
public class MyApiSettings
{
    // Property names must match the JSON keys (case-insensitive by default)
    public string Url { get; set; }
    public int TimeoutSeconds { get; set; }
    public int RetryAttempts { get; set; }
}

```

### **Step 2: Register and Bind in `Program.cs`**

You need to tell the DI container two things:

1. Make the `MyApiSettings` class available for injection.
2. Bind it to the `MyApiSettings` section from `IConfiguration`.

```csharp
// In Program.cs
var builder = WebApplication.CreateBuilder(args);

// Find the "MyApiSettings" section and bind it to the MyApiSettings class.
// This also registers IOptions<MyApiSettings> in the DI container.
builder.Services.Configure<MyApiSettings>(
    builder.Configuration.GetSection("MyApiSettings")
);

// ...

```

### **Step 3: Consume via `IOptions<T>`**

Now, instead of injecting `IConfiguration`, you inject `IOptions<MyApiSettings>`. The settings are accessed through the `.Value` property.

```csharp
public class MyService
{
    private readonly MyApiSettings _settings;

    // Inject IOptions<T> and access its Value property.
    public MyService(IOptions<MyApiSettings> apiSettings)
    {
        _settings = apiSettings.Value;
    }

    public void DoWork()
    {
        // Now you have strongly-typed, IntelliSense-enabled access!
        Console.WriteLine($"Connecting to {_settings.Url} with a timeout of {_settings.TimeoutSeconds}s.");
    }
}

```

---

### **3. `IOptionsSnapshot<T>` vs. `IOptions<T>`**

This is a critical distinction related to service lifetimes.

- **`IOptions<T>`**
    - **Lifetime:** Registered as a **Singleton**.
    - **Behavior:** The options object is created **once** when the application starts. It will **never** change, even if the underlying configuration source (like `appsettings.json`) is modified while the application is running.
    - **Use When:** The configuration is static and will not change during the app's lifetime. This is the most common scenario.
- **`IOptionsSnapshot<T>`**
    - **Lifetime:** Registered as **Scoped**.
    - **Behavior:** A new options object is created **once per HTTP request**. This means if the configuration source changes, the *next* request will get the new values.
    - **Use When:** You need to read configuration values that might be updated while the application is running (e.g., changing a feature flag in a file without restarting the server). You should inject this in services that are also Scoped or Transient (like Controllers or Scoped services).

**Example:**
If you change `TimeoutSeconds` in `appsettings.json` and save the file:

- A service injected with `IOptions<MyApiSettings>` will still see the **old** value.
- A controller injected with `IOptionsSnapshot<MyApiSettings>` on the **next** HTTP request will see the **new** value.

---

### **4. `IOptionsMonitor<T>`**

This is a specialized version for long-running services that need to react to changes.

- **Lifetime:** Registered as a **Singleton**.
- **Behavior:** It's a singleton like `IOptions`, but it provides a mechanism to get the current value and, more importantly, to be notified when the configuration changes.
- **Key Feature:** It has an `OnChange` event you can subscribe to.

**Use When:** You have a singleton background service (`IHostedService`) that needs to react to changes in configuration without being restarted.

**Example (Conceptual):**

```csharp
public class MyBackgroundService : IHostedService
{
    private readonly IOptionsMonitor<MyApiSettings> _monitor;
    private MyApiSettings _currentSettings;
    private IDisposable _changeSubscription;

    public MyBackgroundService(IOptionsMonitor<MyApiSettings> monitor)
    {
        _monitor = monitor;
        _currentSettings = _monitor.CurrentValue; // Get initial value
    }

    public Task StartAsync(CancellationToken cancellationToken)
    {
        // Subscribe to changes
        _changeSubscription = _monitor.OnChange(updatedSettings =>
        {
            Console.WriteLine("CONFIGURATION CHANGED! New timeout is: " + updatedSettings.TimeoutSeconds);
            _currentSettings = updatedSettings;
        });
        return Task.CompletedTask;
    }

    // ...
}

```

---

### **Summary of Phase 2**

| Interface | Lifetime | Behavior | When to Use |
| --- | --- | --- | --- |
| `IConfiguration` | Singleton | Raw, string-based access. | Simple, one-off lookups (avoid if possible). |
| `IOptions<T>` | Singleton | **Read once** at startup. Static. | **The Default.** Most application settings. |
| `IOptionsSnapshot<T>` | Scoped | **Re-read per request.** Dynamic. | For controllers/scoped services that need up-to-date values. |
| `IOptionsMonitor<T>` | Singleton | Can **notify** your code of changes. | For singleton services/background tasks that must react to live config updates. |

Are you ready to move to **Phase 3: Advanced Configuration Sources**, where we'll cover User Secrets and Azure Key Vault?