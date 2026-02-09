# Example : Custom Database Configuration Provider

You're right, seeing concrete examples is the best way to understand these advanced concepts.

Here are detailed, practical examples for both creating a **Database Configuration Provider** and loading configuration from an **External JSON File**.

---

### **Example 1: Custom Database Configuration Provider**

This example shows how to load configuration values from a SQL Server table using Entity Framework Core. This allows you to change settings in the database, and the application will pick them up on the next startup (or even live, with a bit more work).

### **Step 1: The Database Model**

First, you need a simple table to store your key-value pairs.

**EF Core Entity:**

```csharp
public class AppSetting
{
    // Key will be in the format "Section:SubSection:Key"
    [Key]
    public string Key { get; set; }

    public string Value { get; set; }
}

```

And your `DbContext` would have: `public DbSet<AppSetting> AppSettings { get; set; }`

### **Step 2: The Custom `ConfigurationProvider`**

This is the core logic. This class is responsible for connecting to the database and loading the data.

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using System.Collections.Generic;
using System.Linq;

// Inherit from ConfigurationProvider. The magic happens in the Load() method.
public class EntityFrameworkConfigurationProvider : ConfigurationProvider
{
    private readonly DbContextOptions<AppDbContext> _options;

    public EntityFrameworkConfigurationProvider(DbContextOptions<AppDbContext> options)
    {
        _options = options;
    }

    // This method is called by the configuration system to load the data.
    public override void Load()
    {
        // We create a new DbContext instance to query the database.
        using (var dbContext = new AppDbContext(_options))
        {
            dbContext.Database.EnsureCreated(); // Ensure the table exists.

            // Read all settings from the database and convert them into a dictionary.
            // The dictionary's keys must match the configuration keys (e.g., "MySettings:ApiKey").
            Data = dbContext.AppSettings.ToDictionary(c => c.Key, c => c.Value, StringComparer.OrdinalIgnoreCase);
        }
    }
}

```

### **Step 3: The `ConfigurationSource` and Extension Method**

These are boilerplate classes that make it easy to wire up your provider in `Program.cs`.

**The Source:**

```csharp
public class EntityFrameworkConfigurationSource : IConfigurationSource
{
    private readonly DbContextOptions<AppDbContext> _options;

    public EntityFrameworkConfigurationSource(DbContextOptions<AppDbContext> options)
    {
        _options = options;
    }

    public IConfigurationProvider Build(IConfigurationBuilder builder)
    {
        return new EntityFrameworkConfigurationProvider(_options);
    }
}

```

**The Extension Method:**

```csharp
public static class EntityFrameworkConfigurationExtensions
{
    public static IConfigurationBuilder AddEntityFramework(this IConfigurationBuilder builder, Action<DbContextOptionsBuilder> optionsAction)
    {
        var optionsBuilder = new DbContextOptionsBuilder<AppDbContext>();
        optionsAction(optionsBuilder.Options);

        return builder.Add(new EntityFrameworkConfigurationSource(optionsBuilder.Options));
    }
}

```

### **Step 4: Using it in `Program.cs`**

Now you can add your custom provider to the configuration pipeline. Remember that the order matters. Here, we add it *after* the JSON files, so values in the database will override `appsettings.json`.

```csharp
var builder = WebApplication.CreateBuilder(args);

// --- Configure the sources ---
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

// Add our custom provider.
builder.Configuration.AddEntityFramework(options =>
    options.UseSqlServer(connectionString)
);

// Now, IConfiguration will contain values from JSON files AND the database.
// The database values will win in case of a conflict.

// ... rest of your Program.cs ...

```

You have successfully built a provider that loads configuration from a SQL database!

---

### **Example 2: Adding an External JSON File as a Provider**

Sometimes you need to load a configuration file that is **not** named `appsettings.json` or is located outside your application's root directory. This is common for shared configuration or optional overrides.

**The Scenario:**
You have a shared configuration file located at `C:\\SharedConfig\\global-settings.json` that multiple applications need to read.

### **The Method: `AddJsonFile()`**

[ASP.NET](http://asp.net/) Core has a built-in method for this. The key is to provide the full path to the file.

- `optional: true`: The application will not throw an error if the file doesn't exist. This is crucial for configuration that might not be present in every environment.
- `reloadOnChange: true`: The application will monitor this file for changes. If you edit and save `global-settings.json` while the app is running, `IOptionsSnapshot` and `IOptionsMonitor` will automatically pick up the new values.

**The `Program.cs` Configuration:**

```csharp
var builder = WebApplication.CreateBuilder(args);

// --- Configure the sources ---

// The standard appsettings.json providers are added by default.
// Now, let's add our external file.
builder.Configuration.AddJsonFile(
    path: "C:\\\\SharedConfig\\\\global-settings.json",
    optional: true, // Don't crash if the file is not there.
    reloadOnChange: true // Reload the config if the file is edited.
);

// You can also use a relative path. This example looks for a file
// one directory level above the application's content root.
builder.Configuration.AddJsonFile(
    path: "../common-settings.json",
    optional: true,
    reloadOnChange: true
);

// At this point, IConfiguration is a merged view of:
// 1. appsettings.json
// 2. appsettings.Development.json
// 3. C:\\SharedConfig\\global-settings.json (will override previous files)
// 4. ../common-settings.json (will override previous files)
// 5. User Secrets, Environment Variables, etc...

// ... rest of your Program.cs ...

```

This simple `AddJsonFile()` method gives you complete control over which files contribute to your application's configuration, allowing for highly flexible and layered configuration strategies.