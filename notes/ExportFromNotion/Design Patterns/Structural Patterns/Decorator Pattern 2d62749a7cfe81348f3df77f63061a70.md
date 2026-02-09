# Decorator Pattern

### 1. What is it?

The Decorator is a structural design pattern that lets you attach new behaviors to objects dynamically by placing them inside special **wrapper** objects that contain the new behaviors. It provides a flexible alternative to subclassing for extending functionality.

The book uses the analogy of wearing clothes: you start with a person (the core object). If you're cold, you "wrap" yourself in a sweater (a decorator). If it's raining, you add another wrapper: a raincoat. Each layer adds new functionality (warmth, water-proofing) without changing the person object itself. You can add or remove these layers at runtime.

### 2. Why it is required?

The Decorator pattern is required to solve the problem of adding responsibilities to objects in a flexible and dynamic way. The most common alternative, inheritance (subclassing), has two major drawbacks that Decorator overcomes:

1. **Inheritance is Static:** You cannot alter the behavior of an existing object at runtime. An object is an instance of a specific class, and that cannot be changed.
2. **Combinatorial Explosion:** If you need to support multiple independent extensions, using inheritance forces you to create a subclass for every possible combination. The book's example involves a `Notifier` that sends emails. Adding SMS, Facebook, and Slack notifications would require creating classes like `SmsNotifier`, `FacebookNotifier`, `SmsAndFacebookNotifier`, `SmsAndFacebookAndSlackNotifier`, etc., which is completely unmanageable.

Decorator solves this by using composition, allowing you to wrap an object with any number of "decorators" at runtime.

### 3. Details and key points and examples in the reference Book

- **Core Concept:**
    - The pattern relies on **composition** instead of inheritance to extend behavior.
    - It uses a "wrapper" (the Decorator) that can be linked with a "target" (the Component).
- **The Common Interface:**
    - This is the most critical rule of the pattern. Both the wrapper and the wrapped object must implement the same interface.
    - This ensures that from the client's perspective, the decorated object is identical to the original object. The client can use it in the exact same way.
- **Recursive Composition (Stacking):**
    - Because a decorator implements the same interface as the object it wraps, a decorator can wrap *another decorator*.
    - This allows you to create a stack of decorators, with each one adding its own behavior. The book illustrates this by showing how a notification request passes through a chain of decorators (e.g., Slack -> Facebook -> Email).
- **Key Roles and Structure:**
    - **Component:** The common interface for both the core object and the decorators.
    - **Concrete Component:** The original, base object that we want to add behavior to.
    - **Base Decorator:** An `abstract` class that also implements the Component interface. It holds a reference to a wrapped Component object and its primary job is to delegate all calls to that wrapped object. This class contains the boilerplate wrapping logic.
    - **Concrete Decorators:** These classes inherit from the Base Decorator and add the new behavior. They execute their logic either *before* or *after* calling the parent method (which in turn calls the wrapped object).
- **Book Example:** The book details two examples: the `Notifier` (Email, SMS, Slack, etc.) and a `DataSource` that reads/writes data. The `DataSource` example is very clear: you start with a simple `FileDataSource`. You then wrap it with a `CompressionDecorator` and an `EncryptionDecorator`. When you write data, it first gets compressed, then encrypted, and finally written to the file.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - When you need to add responsibilities to objects dynamically and transparently, without affecting other objects.
    - When subclassing is impractical due to the large number of possible feature combinations.
    - When you want to extend a class that is `sealed` (in C#) or `final` (in Java), as you cannot inherit from it.
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - It's hard to remove a specific wrapper from the middle of the decorators stack.
    - The pattern can create a lot of small, similar-looking objects, which can make the code harder to debug and understand.
    - The initial configuration code for assembling the decorator stack can become quite complex (e.g., `new A(new B(new C(...)))`).

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Define the Component Interface:** Create an interface that defines the common operations for both the core object and the decorators (e.g., `IDataSource` with `Read()` and `Write()` methods).
2. **Create the Concrete Component:** Implement the interface with a base class that has the core functionality (e.g., `FileDataSource`).
3. **Create the Base Decorator:** Create an `abstract` class that also implements the component interface.
    - Add a `protected readonly` field of the component interface type to hold the object it will wrap.
    - In the constructor, accept an object of the component interface type and assign it to this field.
    - Implement the interface methods as `virtual`. In each method, simply delegate the call to the wrapped object (e.g., `public virtual void Write(data) => _wrappee.Write(data);`).
4. **Create Concrete Decorators:** Create concrete classes that inherit from the Base Decorator.
    - Override the methods where you need to add new behavior.
    - In the overridden method, add your custom logic *before* or *after* calling the base method (`base.Write(data);`).
5. **Refactor the Client:** The client code will now compose the object by wrapping the concrete component with one or more decorators. The client will then use the final object through the common component interface.

### 6. C# code Example which is not in the correct state

This "Bad Code" shows a `ReportGenerator` where optional features like adding a header or a timestamp are controlled by complex booleans in the constructor, violating the Single Responsibility Principle.

```csharp
// BAD CODE: A single class with too many responsibilities and complex logic.
public class ReportGenerator
{
    private readonly bool _addHeader;
    private readonly bool _addTimestamp;

    public ReportGenerator(bool addHeader, bool addTimestamp)
    {
        _addHeader = addHeader;
        _addTimestamp = addTimestamp;
    }

    public string Generate(string content)
    {
        string report = content;

        // This logic is messy and inflexible.
        // What if we want to add a footer? Or encryption? This class would keep growing.
        if (_addHeader)
        {
            report = "[Official Company Header]\\n" + report;
        }

        if (_addTimestamp)
        {
            report = report + $"\\nGenerated at: {DateTime.Now}";
        }

        return report;
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" refactors the report generation using the Decorator pattern, making it flexible, clean, and adherent to the Open/Closed Principle.

```csharp
// GOOD CODE: Applying the Decorator Pattern

// Step 1: The Component Interface
public interface IReportGenerator
{
    string Generate(string content);
}

// Step 2: The Concrete Component with the core functionality.
public class BasicReportGenerator : IReportGenerator
{
    public string Generate(string content)
    {
        // The core responsibility is just to return the content.
        return content;
    }
}

// Step 3: The abstract Base Decorator.
public abstract class ReportDecorator : IReportGenerator
{
    // It holds a reference to the wrapped component.
    protected readonly IReportGenerator _wrappee;

    protected ReportDecorator(IReportGenerator wrappee)
    {
        _wrappee = wrappee;
    }

    // It delegates the call to the wrapped component.
    // This is virtual so concrete decorators can override it.
    public virtual string Generate(string content)
    {
        return _wrappee.Generate(content);
    }
}

// Step 4: Concrete Decorators that add new behavior.
public class HeaderDecorator : ReportDecorator
{
    public HeaderDecorator(IReportGenerator wrappee) : base(wrappee) { }

    public override string Generate(string content)
    {
        // Add new behavior BEFORE calling the base (wrapped) method.
        string header = "[Official Company Header]\\n";
        string reportContent = base.Generate(content);
        return header + reportContent;
    }
}

public class TimestampDecorator : ReportDecorator
{
    public TimestampDecorator(IReportGenerator wrappee) : base(wrappee) { }

    public override string Generate(string content)
    {
        // Add new behavior AFTER calling the base (wrapped) method.
        string reportContent = base.Generate(content);
        string timestamp = $"\\nGenerated at: {DateTime.Now}";
        return reportContent + timestamp;
    }
}

// Step 5: The Client composes and uses the objects.
public static class Client
{
    public static void Main()
    {
        // 1. Create the base component.
        IReportGenerator basicReport = new BasicReportGenerator();
        Console.WriteLine("--- Basic Report ---");
        Console.WriteLine(basicReport.Generate("This is the monthly sales data."));

        // 2. Decorate it with a Header.
        IReportGenerator headerReport = new HeaderDecorator(basicReport);
        Console.WriteLine("\\n--- Report with Header ---");
        Console.WriteLine(headerReport.Generate("This is the monthly sales data."));

        // 3. Decorate it with both a Header and a Timestamp.
        // This is where the stacking/composition happens.
        IReportGenerator fullReport = new TimestampDecorator(new HeaderDecorator(new BasicReportGenerator()));
        Console.WriteLine("\\n--- Full Report (Header + Timestamp) ---");
        Console.WriteLine(fullReport.Generate("This is the monthly sales data."));
    }
}

```