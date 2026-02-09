# Phase 2: Service Lifetimes (The "When")

*(Microsoft Docs Entry Point: [Service lifetimes](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection#service-lifetimes))*

The service lifetime tells the Dependency Injection (DI) container **how long an instance of a service should live**. When a new request for a service comes in, the container decides whether to create a brand new instance or reuse an existing one based on its registered lifetime.

---

### **1. `Transient` (`AddTransient`)**

- **Lifetime:** A new instance is created **every single time** it is requested.
- **Analogy:** A disposable paper cup. You get a new one for every drink, and you throw it away immediately after.

**Behavior:**

```csharp
// In Program.cs
builder.Services.AddTransient<MyService>();

// In a Controller
public class MyController(MyService service1) { ... }

// In another service
public class AnotherService(MyService service2) { ... }

```

Even within the same HTTP request, `service1` and `service2` will be **different instances** of `MyService`. If `MyService` is injected into five different places, five separate objects will be created.

**When to Use `Transient`:**

- For **lightweight, stateless services** where there is no cost to creation.
- For services that are **not thread-safe** and must not be shared across different parts of a request.
- Example: A service that performs a simple calculation, like a `VatCalculator`.

---

### **2. `Scoped` (`AddScoped`)**

- **Lifetime:** A new instance is created **once per client request (scope)**. The same instance is then reused for the duration of that single request.
- **Analogy:** A ceramic mug at a coffee shop. You get one mug for your entire visit. You can get refills (request the service again), but you'll get the same mug. When you leave (the request ends), the mug is washed (disposed of).

**Behavior:**

```csharp
// In Program.cs
builder.Services.AddScoped<MyService>();
```

Within the same HTTP request, `service1` (in the controller) and `service2` (in another service) will be the **exact same instance** of `MyService`. A different HTTP request will get its own, separate instance.

**When to Use `Scoped`:**

- This is the **default lifetime for most services in a web application**.
- For services that need to maintain state or share data **within a single request**.
- **Entity Framework Core `DbContext` is a prime example.** You want all repositories and services within a single request to share the same `DbContext` instance to participate in a single "Unit of Work" or transaction. This is why it's registered as `AddDbContext`, which is `Scoped` by default.

---

### **3. `Singleton` (`AddSingleton`)**

- **Lifetime:** A single instance is created **the first time it is requested**, and that same instance is reused for **every subsequent request for the entire lifetime of the application**.
- **Analogy:** The coffee machine itself. Everyone in the coffee shop uses the same machine, all day long. It's shared by everyone.

**Behavior:**

```csharp
// In Program.cs
builder.Services.AddSingleton<MyService>();
```

Every single HTTP request, from every user, will receive the **exact same instance** of `MyService` until the application is shut down.

**When to Use `Singleton`:**

- For services that are **thread-safe** and expensive to create.
- For services that hold application-wide state or configuration.
- Examples: `ILoggerFactory`, `IConfiguration`, a client for a distributed cache like Redis (`IConnectionMultiplexer`), or a simple in-memory cache service.

---

### **4. "Captive Dependency" (The Expert Trap)**

This is the most dangerous lifetime mismatch. It's a logical error that the DI container helps you catch.

**The Rule:** A service with a longer lifetime cannot depend on a service with a shorter lifetime.

- **CANNOT:** A `Singleton` (lives forever) cannot depend on a `Scoped` (lives for one request).
- **CAN:** A `Scoped` (lives for one request) can depend on a `Singleton` (lives forever).

**The Problem:**
Imagine this incorrect registration:

```csharp
builder.Services.AddSingleton<MySingletonService>();
builder.Services.AddScoped<MyScopedService>(); // Like a DbContext

// MySingletonService's constructor
public MySingletonService(MyScopedService scopedService) { ... }
```

1. **First Request:** The container creates `MySingletonService`. To do so, it also creates an instance of `MyScopedService` and injects it.
2. **`MySingletonService` is now stored forever.** The `MyScopedService` instance is now "captive" inside it.
3. **Second Request:** Another user makes a request. The container reuses the `MySingletonService`. That service is still holding on to the `MyScopedService` from the *first request*.
4. **Result:** You are now accidentally sharing a `DbContext` (or other scoped data) between different users and different requests, which will lead to data corruption and concurrency bugs.

**The Safeguard:**
By default, [ASP.NET](http://asp.net/) Core's DI container will throw an exception at startup (or on the first request) if it detects this invalid dependency graph, saving you from a production disaster.

---

### **Summary of Lifetimes**

| Lifetime | When is it Created? | Who Shares the Instance? | Common Use Case |
| --- | --- | --- | --- |
| **`Transient`** | Every time it's injected. | No one. It's always new. | Lightweight, stateless helpers. |
| **`Scoped`** | Once per HTTP request. | All services within that same request. | **The Default.** `DbContext`, business services. |
| **`Singleton`** | Once for the application's life. | **Everyone.** All requests, all users. | Caching, configuration, expensive clients. |

Are you ready to move to **Phase 3: Registration Techniques**, where we'll explore more advanced ways to register these services?