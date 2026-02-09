# Adapter Pattern

### 1. What is it?

The Adapter is a structural design pattern that allows objects with incompatible interfaces to collaborate. It acts as a middle-layer translator, or **wrapper**, that converts the interface of one object (the *adaptee*) into an interface that another object (the *client*) expects.

The book uses a perfect real-world analogy: a power plug adapter for traveling. Your US laptop charger plug won't fit into a European wall socket. An adapter has a US-style socket on one end and a European-style plug on the other, allowing the two incompatible interfaces to work together seamlessly.

### 2. Why it is required?

It is required when you need to integrate an existing class into your application, but its interface is different from what your application's code expects. This often happens when working with:

- Third-party libraries.
- Legacy systems.
- External APIs.

You typically cannot (or should not) change the source code of the library or legacy system. The Adapter pattern provides a clean way to make the integration work without modifying the existing code on either side, thus adhering to the Open/Closed Principle.

### 3. Details and key points and examples in the reference Book

- **Core Idea:**
    - An adapter wraps one of the objects to hide the complexity of the data format or method call conversion happening behind the scenes. The wrapped object is completely unaware of the adapter.
- **Key Roles and Structure:**
    - **Client:** The class that contains the application's existing business logic.
    - **Client Interface (Target):** The interface that the client code depends on.
    - **Service (Adaptee):** The class (often from a library or legacy system) with the incompatible interface.
    - **Adapter:** A class that implements the `Client Interface` and wraps an instance of the `Service`.
- **Process Flow:**
    1. The client calls a method on the adapter using the `Client Interface`.
    2. The adapter receives the call.
    3. The adapter translates the request into one or more calls to the wrapped `Service` object, converting data formats and method signatures as needed.
- **Book Implementations:**
    - **Object Adapter (Composition):** This is the most common and flexible approach. The Adapter holds an instance of the Service. This is the standard way to implement the pattern in C#.
    - **Class Adapter (Inheritance):** This approach uses multiple inheritance to inherit from both the client interface and the service class. The book notes this is only possible in languages like C++, not C#.
- **Book Example:** The book provides the classic example of fitting a `SquarePeg` into a `RoundHole`. A `SquarePegAdapter` is created that **inherits** from `RoundPeg`. It pretends to be a round peg by calculating the smallest radius of a circle that can circumscribe the square peg it wraps. This allows the `RoundHole` to check if the `SquarePegAdapter` will "fit" without ever knowing it's dealing with a square peg.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - When you want to use an existing class, but its interface is incompatible with the rest of your code.
    - When you want to reuse several existing subclasses that lack some common functionality that can't be added to the superclass.
    - When you are working with third-party code and you want to isolate your application from changes in that library. If the library gets a major update with breaking changes, you only have to update the adapter, not your entire application.
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - If you have the ability to change the `Service` class directly to match the client's interface, that is often a simpler solution than creating a new adapter class.
    - Be careful not to overcomplicate the system. An adapter adds a new layer of indirection. If the interface mismatch is trivial (e.g., just one method name), it might be simpler to handle it with a small helper function rather than the full pattern.

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Identify Incompatibles:** Identify the `Client` class and the `Adaptee` (the service class) which have incompatible interfaces.
2. **Define Target Interface:** Ensure the client works through an interface (`ITarget`). If the client is directly coupled to a concrete class, first refactor it to depend on an interface that describes its expectations.
3. **Create the Adapter Class:** Create a new class, the `Adapter`, and make it implement the `ITarget` interface.
4. **Wrap the Adaptee:** Add a private field inside the `Adapter` class to hold a reference to the `Adaptee` object. Pass an instance of the `Adaptee` to the `Adapter`'s constructor.
5. **Implement the Translation:** Implement all methods of the `ITarget` interface in the `Adapter`. Inside these methods, call the methods of the wrapped `Adaptee` object. This is where you perform the "translation"—converting data, calling different methods, or handling different sequences.
6. **Refactor the Client's Initialization:** In the application's composition root (where objects are created), create an instance of the `Adaptee`, wrap it in the `Adapter`, and then pass the `Adapter` instance to the `Client`. The client code itself does not need to change, as it still works with the `ITarget` interface.

### 6. C# code Example which is not in the correct state

This "Bad Code" shows an application that needs to use a third-party logging service, but the service's interface is completely different from the application's internal logging interface.

```csharp
// BAD CODE: Client cannot use the new logger without modification.

// --- The Existing Application Code ---
// Rule 2: The client works with a simple, standard interface.
public interface ILogger
{
    void Log(string message);
}

public class AppService
{
    private readonly ILogger _logger;
    public AppService(ILogger logger)
    {
        _logger = logger;
    }
    public void DoWork()
    {
        _logger.Log("Doing important work...");
    }
}

// --- The New, Incompatible Third-Party Library ---
// Rule 1: This is the Adaptee. Its interface is totally different.
public class ThirdPartyLogger
{
    public void LogMessage(string severity, string message)
    {
        Console.WriteLine($"[ThirdParty] {severity}: {message}");
    }
}

// --- The Problem in the Composition Root ---
public class Program
{
    public static void Main()
    {
        // We want to use the new logger, but how?
        var newLogger = new ThirdPartyLogger();

        // This won't compile! ThirdPartyLogger does not implement ILogger.
        // var service = new AppService(newLogger);

        Console.WriteLine("Cannot use the new logger because its interface is incompatible.");
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" introduces an `Adapter` class that allows the `AppService` to use the `ThirdPartyLogger` without any changes to either class.

```csharp
// GOOD CODE: Using the Adapter Pattern

// --- The Existing Application Code (Unchanged) ---
public interface ILogger
{
    void Log(string message);
}

public class AppService
{
    private readonly ILogger _logger;
    public AppService(ILogger logger)
    {
        _logger = logger;
    }
    public void DoWork()
    {
        _logger.Log("Doing important work...");
    }
}

// --- The New, Incompatible Third-Party Library (Unchanged) ---
public class ThirdPartyLogger
{
    public void LogMessage(string severity, string message)
    {
        Console.WriteLine($"[ThirdParty] {severity.ToUpper()}: {message}");
    }
}

// Step 3: Create the Adapter Class that implements the target interface.
public class LoggerAdapter : ILogger
{
    // Step 4: Wrap the Adaptee. It holds a reference to the service.
    private readonly ThirdPartyLogger _adaptee;

    public LoggerAdapter(ThirdPartyLogger adaptee)
    {
        _adaptee = adaptee;
    }

    // Step 5: Implement the translation logic.
    // The adapter's Log method calls the adaptee's LogMessage method.
    public void Log(string message)
    {
        // Here we "translate" the simple call into the more complex one.
        // We can default the severity or perform other logic.
        _adaptee.LogMessage("info", message);
    }
}

// Step 6: The client's initialization is clean and decoupled.
public class Program
{
    public static void Main()
    {
        // 1. Create an instance of the incompatible logger (the adaptee).
        var thirdPartyLogger = new ThirdPartyLogger();

        // 2. Wrap it inside our adapter.
        ILogger logger = new LoggerAdapter(thirdPartyLogger);

        // 3. Pass the adapter to the client. The client thinks it's using
        // a standard ILogger and is unaware of the complex adaptee.
        var service = new AppService(logger);
        service.DoWork(); // This will now correctly log using the third-party service.
    }
}

```