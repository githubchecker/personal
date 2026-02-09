# Phase 5: Keyed Services (New in .NET 8)

*(Microsoft Docs Entry Point: [Keyed DI container services](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-8.0#keyed-services))*

---

### **1. The Problem: Multiple Implementations of One Interface**

Before .NET 8, Dependency Injection had a major limitation: you could only register **one** implementation per interface. If you tried to register a second, it would overwrite the first.

**The Scenario:**
You're building a notification system. You have a single interface, `IMessageSender`, but multiple ways to send a message.

```csharp
public interface IMessageSender
{
    Task SendMessageAsync(string recipient, string message);
}

public class SmsMessageSender : IMessageSender { /* ... */ }
public class EmailMessageSender : IMessageSender { /* ... */ }
public class PushNotificationSender : IMessageSender { /* ... */ }

```

**The Old Dilemma:**
How do you register all three and then choose which one to use at runtime?

- **The Ugly Workaround:** You would have to create a "factory" service (`MessageSenderFactory`) that would itself inject `IEnumerable<IMessageSender>`. The factory would then contain `if/else` or `switch` logic to find the correct instance from the collection based on some criteria. This was boilerplate code that you had to write yourself.

---

### **2. The Solution: Keyed Services**

.NET 8 introduces the concept of registering a service with a **key** (a string, enum, or any `object`). The DI container can now store multiple implementations of `IMessageSender` as long as each has a unique key.

### **Step 1: Keyed Service Registration (`Program.cs`)**

You use the new `AddKeyed...` methods to register your services. The first parameter is the key.

```csharp
// In Program.cs
public enum NotifierType { Sms, Email, Push }

// Register each implementation with a unique key.
builder.Services.AddKeyedScoped<IMessageSender, SmsMessageSender>(NotifierType.Sms);
builder.Services.AddKeyedScoped<IMessageSender, EmailMessageSender>(NotifierType.Email);
builder.Services.AddKeyedScoped<IMessageSender, PushNotificationSender>(NotifierType.Push);

```

The DI container now holds three different registrations for `IMessageSender`.

---

### **3. Consuming Keyed Services**

Once registered, you need a way to tell the container *which one* you want. You do this with the `[FromKeyedServices]` attribute.

### **Consumption Pattern A: Constructor Injection**

This is the standard way to consume a *specific* keyed service.

```csharp
[ApiController]
[Route("[controller]")]
public class NotificationController : ControllerBase
{
    private readonly IMessageSender _emailSender;

    // Use the attribute to specify which keyed service to inject.
    public NotificationController([FromKeyedServices(NotifierType.Email)] IMessageSender emailSender)
    {
        _emailSender = emailSender;
    }

    [HttpPost("send-email")]
    public async Task<IActionResult> SendEmail(string message)
    {
        await _emailSender.SendMessageAsync("user@example.com", message);
        return Ok("Email sent!");
    }
}

```

### **Consumption Pattern B: Dynamic Resolution with `IServiceProvider`**

What if you need to decide *dynamically* which sender to use based on user input? You can't use constructor injection for that. Instead, you can inject the `IServiceProvider` and use it to resolve the keyed service at runtime.

**The Controller:**

```csharp
[ApiController]
[Route("[controller]")]
public class DynamicNotificationController : ControllerBase
{
    private readonly IServiceProvider _serviceProvider;

    public DynamicNotificationController(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    [HttpPost("send")]
    public async Task<IActionResult> SendNotification(NotifierType type, string message)
    {
        // Use the IServiceProvider to get the correct keyed service dynamically.
        var sender = _serviceProvider.GetRequiredKeyedService<IMessageSender>(type);

        await sender.SendMessageAsync("recipient@example.com", message);

        return Ok($"Notification sent via {type}.");
    }
}

```

When a request comes in for `POST /send?type=Sms`, the code will resolve the `SmsMessageSender` instance. If `type=Email`, it will resolve the `EmailMessageSender`.

---

### **4. When to Use Keyed Services**

Keyed services are a powerful tool, but they are not needed for every situation.

**Use them when:**

1. **Implementing the Strategy Pattern:** You have a common interface (`IFileParser`) and multiple, interchangeable implementations (`CsvParser`, `JsonParser`).
2. **Multiple Configurations:** You need to connect to two different databases of the same type. You could have two keyed `DbContext` registrations, each configured with a different connection string.
3. **A/B Testing or Feature Flags:** You could have an `OldSearchService` and a `NewSearchService` registered. Your controller could dynamically choose which one to use based on a feature flag.

**Don't use them when:**

- You only have one implementation of an interface. The standard `AddScoped<I, T>()` is simpler.
- The services are completely unrelated. Don't use keys to group unrelated services just because you can.

---

### **Summary of Keyed Services**

- **Solves:** The "multiple implementations of one interface" problem.
- **Registration:** Use `AddKeyedScoped`, `AddKeyedTransient`, or `AddKeyedSingleton`, providing a unique key.
- **Consumption (Static):** Use the `[FromKeyedServices]` attribute in constructors or action methods to get a specific implementation.
- **Consumption (Dynamic):** Inject `IServiceProvider` and call `GetRequiredKeyedService<T>(key)` to choose the implementation at runtime.
- **Introduced:** **.NET 8**. This is a modern, forward-looking feature.

Are you ready to move to the final **Phase 6: Disposal and Advanced Scenarios**?