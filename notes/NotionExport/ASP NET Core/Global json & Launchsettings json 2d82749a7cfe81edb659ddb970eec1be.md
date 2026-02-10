# Global.json & Launchsettings.json

Of course. These two files, `global.json` and `launchSettings.json`, are crucial parts of the .NET development ecosystem, but they serve very different purposes and often confuse newcomers. Neither of them directly affects your deployed production application, but they are vital for controlling your **local development environment**.

---

### **1. `global.json`**

### **What is its Primary Job?**

The `global.json` file has one main purpose: **to declare which version of the .NET SDK should be used** when you run `dotnet` CLI commands.

This is essential for ensuring consistency across a team of developers and on your build server.

**The Scenario:**

- Your machine has .NET 6, .NET 7, and .NET 8 SDKs installed.
- Your project is built on .NET 7, and you want to ensure that it is always built and tested with a .NET 7 SDK, not the newer .NET 8 SDK.
- If you don't have a `global.json`, the `dotnet` CLI will **always use the latest SDK installed** on the machine by default. This could lead to unexpected behavior or compilation errors if the project isn't compatible with the latest SDK.

### **Structure and Key Properties**

The file is placed in the root of your solution directory (or any parent directory). The `dotnet` command searches upwards from the current directory to find it.

```json
{
  "sdk": {
    "version": "7.0.400",
    "rollForward": "latestFeature"
  }
}

```

- **`sdk.version`:** This is the specific version of the .NET SDK to use. The CLI will try to find this exact version.
- **`sdk.rollForward`:** This defines the fallback behavior if the exact `version` isn't found. This is a crucial setting.
    - **`patch`:** (Default) Will roll forward to the latest patch version of the same minor release. If `7.0.400` isn't found, it might use `7.0.401`, but it will **not** use `7.1.100`.
    - **`latestPatch`:** Identical to `patch`.
    - **`feature`:** Will roll forward to a newer feature band of the same major version. If `7.0.400` isn't found, it might use `7.1.100`.
    - **`minor`:** Will roll forward to a newer minor version of the same major version. If `7.0.400` isn't found, it might use `7.1.100` or `7.2.100`.
    - **`latestFeature`:** Will roll forward to the highest feature band of the same major version available.
    - **`major`:** Will roll forward to the latest major version. If `7.0.400` isn't found, it might use `8.0.100`. (Use with caution).
    - **`latestMajor`:** Identical to `major`.
    - **`disable`:** Will not roll forward at all. If the exact version is not found, the CLI will fail. This provides the strictest level of version control.

**Is it committed to Git?YES.** You should always commit `global.json` to your repository to ensure every developer and the CI/CD build agent uses the exact same SDK version.

---

### **2. `launchSettings.json`**

### **What is its Primary Job?**

The `launchSettings.json` file configures the **profiles for how to run your application locally** from Visual Studio or with the `dotnet run` command.

This file lives inside the `Properties` folder of your project and has **zero effect on your published application**. It is a development-time tool only. When you deploy to Azure, IIS, or a container, this file is completely ignored.

### **Structure and Key Properties**

A typical `launchSettings.json` for an [ASP.NET](http://asp.net/) Core Web API looks like this:

```json
{
  "$schema": "<https://json.schemastore.org/launchsettings.json>",
  "profiles": {
    "https": {
      "commandName": "Project",
      "dotnetRunMessages": true,
      "launchBrowser": true,
      "launchUrl": "swagger",
      "applicationUrl": "<https://localhost:7001>;<http://localhost:5000>",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development",
        "MyCustomSetting": "Value from launchSettings"
      }
    },
    "IIS Express": {
      "commandName": "IISExpress",
      "launchBrowser": true,
      "launchUrl": "swagger",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      }
    }
  }
}

```

- **`profiles`:** Contains a list of different ways to launch the app. You can switch between these profiles in Visual Studio's "Debug" dropdown.
    - **`"https"` (or `Project`):** This profile uses Kestrel, the cross-platform web server. The `dotnet run` command will use this profile by default.
    - **`"IIS Express"`:** This profile uses the lightweight version of IIS for local development on Windows.
- **`commandName`:** Specifies the web server to use (`Project` for Kestrel, `IISExpress`).
- **`launchBrowser`:** `true` will automatically open a browser window when you start the application.
- **`launchUrl`:** The relative URL that the browser will be opened to (e.g., "swagger" for the Swagger UI page).
- **`applicationUrl`:** A semicolon-separated list of URLs that Kestrel will listen on.
- **`environmentVariables`:** This is the most important section. This is where you can set **environment variables specifically for your local debugging sessions**.
    - **`"ASPNETCORE_ENVIRONMENT": "Development"`:** This is how the framework knows to load `appsettings.Development.json` and enable User Secrets.
    - You can add any custom variables here. These values will be available through `IConfiguration` just like any other environment variable, but only when you are running the project locally.

**Is it committed to Git?YES.** This file should be committed to your repository so that every developer on the team has the same set of launch profiles and local environment variables, ensuring a consistent local development experience.

### **Summary Table**

| Feature | `global.json` | `launchSettings.json` |
| --- | --- | --- |
| **Purpose** | Pins the **.NET SDK version**. | Configures **local launch profiles** and dev environment variables. |
| **Location** | Solution root (or any parent folder). | `Properties` folder of a project. |
| **Used by** | The `dotnet` CLI command itself. | Visual Studio and the `dotnet run` command. |
| **Affects Production?** | **No.** | **No.** Completely ignored when published. |
| **Commit to Git?** | **Yes.** Ensures build consistency. | **Yes.** Ensures team development consistency. |

---

# Azure App Configuration to the expert-level pattern of referencing Key Vault secrets *through* App Configuration

### **Phase 1: The "Why" - App Configuration vs. `appsettings.json`**

**The Problem with `appsettings.json`:**

- **Static:** If you need to change a value (like a feature flag or a logging level), you have to redeploy your entire application.
- **Decentralized:** If you have 10 microservices, they each have their own `appsettings.json`. To change a shared value, you have to update and redeploy all 10 services.
- **Secrets:** It's not a secure place for secrets.

**The Solution: Azure App Configuration**
Azure App Configuration is a **centralized, managed service** for your application's configuration.

- **Centralized:** All your microservices can read from one place.
- **Dynamic:** You can change values in the Azure Portal, and your running applications can pick up those changes **without restarting**.
- **Integrated:** It has first-class integration for feature flags and, crucially, for secrets stored in Azure Key Vault.

---

### **Phase 2: Basic Integration with Azure App Configuration**

Let's get your [ASP.NET](http://asp.net/) Core API to read its settings from Azure App Configuration.

### **Step 1: Create an App Configuration resource in Azure**

1. Go to the Azure Portal and create a new "App Configuration" resource.
2. Once created, go to **Configuration explorer** -> **Create** -> **Key-value**.
3. Add a few settings. Use the colon (`:`) for hierarchy, just like in `appsettings.json`.
    - **Key:** `MyApi:Settings:Greeting` -> **Value:** `Hello from Azure App Configuration!`
    - **Key:** `FeatureManagement:EnableCoolNewFeature` -> **Value:** `true`

### **Step 2: Install the NuGet Package**

```bash
dotnet add package Microsoft.Extensions.Configuration.AzureAppConfiguration
dotnet add package Azure.Identity # For authentication

```

### **Step 3: Connect to App Configuration in `Program.cs`**

The key is to add the `AddAzureAppConfiguration` provider to your configuration builder.

```csharp
// In Program.cs
var builder = WebApplication.CreateBuilder(args);

// --- Configuration Setup ---
var appConfigEndpoint = builder.Configuration["AppConfigEndpoint"];

if (!string.IsNullOrEmpty(appConfigEndpoint))
{
    // Add the Azure App Configuration provider.
    builder.Configuration.AddAzureAppConfiguration(options =>
    {
        // Connect using the endpoint and Managed Identity.
        // DefaultAzureCredential will automatically use the app's Managed Identity in Azure,
        // or your local VS/Azure CLI credentials during development.
        options.Connect(new Uri(appConfigEndpoint), new DefaultAzureCredential());
    });
}
// ---

// The IConfiguration object now contains a merged view of:
// 1. appsettings.json
// 2. Azure App Configuration (will override appsettings.json)
// 3. Environment variables, etc.

builder.Services.AddControllers();
var app = builder.Build();
//...

```

**How do you tell your app the endpoint?**
You add a single setting to your `appsettings.json` or as an environment variable.
**`appsettings.json`:**

```json
{
  "AppConfigEndpoint": "<https://myappconfig.azconfig.io>"
}

```

Now, your application will load its settings from App Configuration at startup. You can access them through `IConfiguration` or the Options Pattern just like any other setting.

---

### **Phase 3: Dynamic Reloading (Feature Flags)**

This is where App Configuration shines. You can enable a "sentinel" key that tells your application to refresh its configuration when a change is detected.

### **Step 1: Create a Sentinel Key**

In your App Configuration store, create a key that you will update whenever you want to signal a change.

- **Key:** `MyApi:Settings:Sentinel` -> **Value:** `1`

### **Step 2: Update `Program.cs` to Watch for Changes**

```csharp
builder.Configuration.AddAzureAppConfiguration(options =>
{
    options.Connect(new Uri(appConfigEndpoint), new DefaultAzureCredential())
           // Tell the provider which keys to load.
           .Select("MyApi:*")
           // Configure the refresh mechanism.
           .ConfigureRefresh(refreshOptions =>
           {
               // Watch the 'Sentinel' key for any changes.
               refreshOptions.Register("MyApi:Settings:Sentinel", refreshAll: true)
                             // Set how often the app should check for changes.
                             .SetCacheExpiration(TimeSpan.FromSeconds(30));
           });

    // This line enables the built-in feature flag functionality.
    options.UseFeatureFlags();
});

// You also need to add the App Configuration middleware.
builder.Services.AddAzureAppConfiguration();
//...
var app = builder.Build();
app.UseAzureAppConfiguration(); // <-- Middleware that triggers the refresh

```

Now, if you change any value in App Configuration and then update the `MyApi:Settings:Sentinel` key (e.g., change its value to `2`), your running application will detect the change within 30 seconds and reload its entire configuration.

---

### **Phase 4: Integrating Key Vault (The "Key Vault Reference" Pattern)**

This is the **best practice** for managing secrets. You do **not** put secrets directly into App Configuration. Instead, you put a **reference** to a secret that lives in Azure Key Vault.

**The Workflow:**

1. Your application asks App Configuration for the `DatabaseConnectionString`.
2. App Configuration doesn't return the password. It returns a special URI pointing to the secret in Key Vault.
3. The App Configuration client library in your app sees this special URI.
4. It automatically connects to Key Vault (using the same Managed Identity) and fetches the secret value.
5. It replaces the URI with the real secret value before adding it to `IConfiguration`.

This gives you the dynamic refresh capability of App Configuration with the top-tier security of Key Vault.

### **Step 1: Store the Secret in Key Vault**

1. Go to your **Azure Key Vault**.
2. Create a secret named `MyDbPassword` with the actual password as its value.

### **Step 2: Create a Key Vault Reference in App Configuration**

1. Go to your **Azure App Configuration** store -> **Configuration explorer**.
2. Click **Create** -> **Key Vault reference**.
3. **Key:** `ConnectionStrings:DefaultConnection`
4. **Key Vault:** Select your Key Vault.
5. **Secret:** Select the `MyDbPassword` secret you just created.
6. Click **Apply**. You will see the value is a URI.

### **Step 3: Grant Permissions**

The **Managed Identity** of your [ASP.NET](http://asp.net/) Core application needs permission to access **both** services:

1. **App Configuration:** It needs the "App Configuration Data Reader" role.
2. **Key Vault:** It needs "Get" and "List" permissions on secrets.

### **Step 4: Update `Program.cs`**

The code is almost identical to the basic setup, but you must tell the provider to resolve Key Vault references.

```csharp
builder.Configuration.AddAzureAppConfiguration(options =>
{
    var credential = new DefaultAzureCredential();
    options.Connect(new Uri(appConfigEndpoint), credential)
           // This is the magic line that enables the Key Vault lookup.
           .ConfigureKeyVault(kv =>
           {
               kv.SetCredential(credential);
           });
});

```

**That's it!**

Now, when your application starts and asks for `ConnectionStrings:DefaultConnection`, the provider will perform the two-step fetch automatically. From your C# code's perspective, it just looks like a normal configuration value.

### **Summary of Best Practices**

| Type of Setting | Where to Store It | How to Access in Code |
| --- | --- | --- |
| **Non-Sensitive, Static Config** | `appsettings.json` (for local dev) | `IConfiguration` / `IOptions` |
| **Non-Sensitive, Dynamic Config** | **Azure App Configuration** (as a key-value) | `IConfiguration` / `IOptionsSnapshot` |
| **Feature Flags** | **Azure App Configuration** (as a feature flag) | `IFeatureManager` |
| **Sensitive Secrets** | **Azure Key Vault** (as a secret) | **Azure App Configuration** (as a Key Vault Reference) -> `IConfiguration` |

This layered approach gives you the best of all worlds: centralized and dynamic configuration from App Configuration, with the unparalleled security of Azure Key Vault for your secrets.