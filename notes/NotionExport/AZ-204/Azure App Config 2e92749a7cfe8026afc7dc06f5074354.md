# Azure App Config

### **Section 1: The Core Distinction (Data vs. Brains)**

To fix the mental model, you must separate **loading data** from **enabling behavior**.

1. **`builder.Configuration.AddAzureAppConfiguration(...)`**
    - **Role:** **The Data Loader (Provider)**.
    - **Function:** Connects to Azure, authenticates, resolves Key Vault references, and sets up the Sentinel watchers. It downloads the key-values into the application's configuration dictionary.
    - **Key Concept:** This is where you pass the `options` for **Sentinel** and **Key Vault**.
2. **`builder.Services.AddAzureAppConfiguration()`**
    - **Role:** **The Intelligence (Services)**.
    - **Function:** It injects the `IConfigurationRefresherProvider` and Feature Manager into the Dependency Injection (DI) container.
    - **Key Concept:** This takes **NO parameters** (usually) regarding connection strings. It essentially tells the internal framework: *"Hey, be ready to use that configuration provider we added earlier to perform refreshes later."*
3. **`builder.Configuration.AddJsonFile(...)`**
    - **Role:** **Local Overrides**.
    - **Function:** Loads static files. Useful for local development settings that shouldn't be in the cloud.
4. **`builder.Services.Configure<T>(...)`**
    - **Role:** **The Type Binder**.
    - **Function:** Maps a specific section of the configuration dictionary (loaded by step 1 or 3) into a strongly typed C# Class (`IOptions<T>`).

---

### **Section 2: The Corrected Implementation (Modern Syntax)**

This is the standard `Program.cs` pattern for a .NET 8 Web API.

**Prerequisites:**

- `Microsoft.Azure.AppConfiguration.AspNetCore`

```csharp
using Azure.Identity;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// =========================================================
// 1. CONFIGURATION SOURCE (The "Data Loader")
// =========================================================
// Note: We access 'builder.Configuration' directly.
// We DO NOT use 'Host.ConfigureAppConfiguration'.

var appConfigEndpoint = builder.Configuration["AppConfig:Endpoint"];

if (!string.IsNullOrEmpty(appConfigEndpoint))
{
    // A. Connect to Azure App Configuration
    // THIS is where the 'options' parameter goes for Sentinels and Key Vault.
    builder.Configuration.AddAzureAppConfiguration(options =>
    {
        options.Connect(new Uri(appConfigEndpoint), new DefaultAzureCredential())
               // Configure Key Vault linkage
               .ConfigureKeyVault(kv =>
               {
                   kv.SetCredential(new DefaultAzureCredential());
               })
               // Configure the Sentinel for Dynamic Refresh
               // (This registers the Key to watch, but doesn't auto-refresh yet)
               .ConfigureRefresh(refresh =>
               {
                   refresh.Register("MyApi:Sentinel", refreshAll: true)
                          .SetCacheExpiration(TimeSpan.FromSeconds(30));
               });
    });
}

// B. Add Custom JSON (Optional)
// This appends/overwrites keys found in the cloud with local file keys
builder.Configuration.AddJsonFile("custom-settings.json", optional: true, reloadOnChange: true);

// =========================================================
// 2. SERVICES (The "Brains" & Binding)
// =========================================================

// C. Register the App Config Services
// MANDATORY for Dynamic Refresh and Feature Flags to work.
// Note: No connection string options passed here.
builder.Services.AddAzureAppConfiguration();

// D. Configure IOptions (Type Binding)
// Maps the "Database" section from (Azure + JSON) to the DatabaseSettings class.
builder.Services.Configure<DatabaseSettings>(builder.Configuration.GetSection("Database"));

// =========================================================
// 3. MIDDLEWARE (The "Trigger")
// =========================================================

var app = builder.Build();

// E. Add the Middleware
// This checks the Sentinel defined in Step 1 on every request.
app.UseAzureAppConfiguration();

app.MapGet("/", (IOptionsSnapshot<DatabaseSettings> settings) =>
{
    // We use IOptionsSnapshot to get the live value if it changed in Azure
    return Results.Ok(new {
        Message = "Config Value:",
        Value = settings.Value.Timeout
    });
});

app.Run();

// ---------------------------------------------------------
// POCO Class
// ---------------------------------------------------------
public class DatabaseSettings
{
    public int Timeout { get; set; }
    public string ConnectionString { get; set; }
}

```

---

### **Section 3: Mechanics & Rules (The Deep Dive)**

### **Why did your syntax feel wrong previously?**

You correctly identified that passing connection options to `builder.Services.AddAzureAppConfiguration()` is incorrect or deprecated for the standard refresh flow.

- **The Config Builder (`builder.Configuration.AddAzureAppConfiguration`)** holds the *Definition* of the connection (The URL, The Sentinel Key, The Key Vault Credentials). It creates the "Configuration Provider".
- **The Service (`builder.Services.AddAzureAppConfiguration`)** acts as the *Bridge*. It looks at the Configuration Provider created in step 1 and exposes its `Refresher` capabilities to the Middleware.

### **Options vs. OptionsSnapshot**

When using the pattern in Step 2-D (`builder.Services.Configure<T>`):

- If you inject `IOptions<T>`: You get the value calculated at **Startup**. Even if Azure refreshes, this variable will stay the same.
- If you inject `IOptionsSnapshot<T>`: The container re-binds the C# class from the configuration dictionary **on every HTTP Request**. This is required to see the changes triggered by the Sentinel.

### **Section 4: Decision Matrix (Correct Usage)**

| Task | Correct Syntax Location |
| --- | --- |
| **Defining the Sentinel Key** | `builder.Configuration.AddAzureAppConfiguration(options => ...)` |
| **Setting Key Vault Credential** | `builder.Configuration.AddAzureAppConfiguration(options => ...)` |
| **Adding Feature Management** | `builder.Services.AddFeatureManagement()` (Separate package) |
| **Enabling the "Watcher"** | `builder.Services.AddAzureAppConfiguration()` (Empty) |
| **Reading Data** | `builder.Configuration["Key"]` OR `IOptionsSnapshot<T>` |