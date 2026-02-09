# Strategy Pattern

### 1. What is it?

The Strategy pattern is a behavioral design pattern that allows you to define a **family of algorithms**, encapsulate each one in a separate class, and make them interchangeable. This lets an object (the *context*) change its behavior at runtime by switching the algorithm it uses.

The book uses the analogy of getting to the airport. You have several transportation strategies: catching a bus, ordering a cab, or riding your bicycle. You can choose one of these strategies at runtime based on external factors like your budget or time constraints.

### 2. Why it is required?

It is required to solve the problem of a class that has a single responsibility but can perform that task in many different ways. Without the Strategy pattern, this often leads to a single, monolithic class with a large conditional statement (`if-else` or `switch`) that selects the appropriate behavior.

This approach has major drawbacks:

- **Violates the Open/Closed Principle:** To add a new algorithm, you must modify the existing class, which is risky.
- **Hard to Maintain:** The class becomes bloated and difficult to read, understand, and debug.
- **Team Collaboration Issues:** Multiple developers trying to add or modify different algorithms in the same large class leads to frequent and painful code merge conflicts.

The Strategy pattern refactors this by extracting each branch of the conditional into its own "strategy" class.

### 3. Details and key points and examples in the reference Book

- **Core Concept:**
    - Take a class that does something specific in a lot of different ways and extract all of these algorithms into separate classes called **strategies**.
- **Key Roles and Structure:**
    - **Context:** The original class (e.g., the `Navigator` in the book's example). It holds a reference to a strategy object but is completely unaware of the concrete type of strategy it's using. It communicates with the strategy object only through a common interface.
    - **Strategy Interface:** This is the common interface for all concrete strategies. It declares a single method that the `Context` will call to execute the algorithm.
    - **Concrete Strategies:** These are the classes that implement the different algorithms (e.g., `RoadStrategy`, `WalkingStrategy`). Each one provides its own implementation for the method defined in the Strategy Interface.
    - **Client:** The client is responsible for creating a specific strategy object and passing it to the context, usually during the context's initialization or by calling a setter method.
- **Delegation over Implementation:**
    - The `Context` object does not execute an algorithm itself. It **delegates** the task to its linked strategy object. This is a key principle: "Favor Composition over Inheritance."
- **Book Example:**
    - The book details a `Navigator` app. Initially, all routing logic is inside the `Navigator` class.
    - The Strategy pattern is applied by creating a `RouteStrategy` interface with a `buildRoute()` method.
    - Concrete strategies like `RoadStrategy`, `PublicTransportStrategy`, and `WalkingStrategy` are created.
    - The `Navigator` class (the context) now has a `routeStrategy` field and simply calls `routeStrategy.buildRoute()`. It also has a method to switch the active strategy, allowing the UI buttons to change the routing behavior on the fly.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - When you have an object with a massive conditional statement that switches between different variants of the same algorithm. This is the primary indicator.
    - When you have a lot of similar classes that only differ in how they execute some behavior. Strategy can consolidate them into one class configured with different behaviors.
    - When you need to be able to switch algorithms at runtime.
    - When you want to isolate the implementation details of algorithms from the business logic that uses them.
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - **Overkill for Simple Cases:** If you only have a couple of algorithms and they rarely change, the pattern may introduce unnecessary complexity. A simple conditional might be more straightforward.
    - **Client Awareness:** The client must be aware of the different strategies to be able to select the appropriate one. This can increase complexity on the client's side.
    - **Functional Alternatives:** The book notes that modern languages (like C# with delegates and lambda expressions) allow you to implement different versions of an algorithm using anonymous functions. This can achieve the same goal as the Strategy pattern but with less boilerplate code (fewer classes and interfaces).

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Define the Strategy Interface:** Create a new interface that declares a single method for executing the algorithm. For example, `IPaymentStrategy` with a `Pay(decimal amount)` method.
2. **Implement Concrete Strategy Classes:** For each algorithm, create a separate class that implements the Strategy interface. For example, `CreditCardPaymentStrategy`, `PayPalPaymentStrategy`, etc.
3. **Define the Context Class:** Identify the class that currently contains the complex conditional logic. This is your `Context`.
4. **Add a Strategy Field:** Inside the `Context` class, add a private field to hold a reference to the strategy interface (e.g., `private IPaymentStrategy _paymentStrategy;`).
5. **Provide a Way to Set the Strategy:** Allow the client to inject the strategy. The two common ways are:
    - Through the `Context`'s constructor.
    - With a public setter method (e.g., `SetPaymentStrategy(IPaymentStrategy strategy)`).
6. **Delegate Work to the Strategy:** In the `Context`'s method that previously had the conditional logic, replace the entire block with a single call to the strategy's method (e.g., `_paymentStrategy.Pay(amount);`).

### 6. C# code Example which is not in the correct state

This "Bad Code" shows an `OrderProcessor` class with a rigid `switch` statement for handling different payment methods, making it hard to extend.

```csharp
// BAD CODE: A single class with a rigid switch statement
public enum PaymentMethod
{
    CreditCard,
    PayPal,
    BankTransfer
}

public class Order
{
    public decimal Amount { get; set; }
}

public class OrderProcessor
{
    // This method violates the Open/Closed Principle.
    // To add a new payment method, we must modify this class.
    public void ProcessOrder(Order order, PaymentMethod method)
    {
        Console.WriteLine($"Processing order for amount: ${order.Amount}");

        switch (method)
        {
            case PaymentMethod.CreditCard:
                Console.WriteLine("Initiating credit card payment...");
                // Complex logic for credit card processing...
                break;
            case PaymentMethod.PayPal:
                Console.WriteLine("Redirecting to PayPal for payment...");
                // Complex logic for PayPal integration...
                break;
            case PaymentMethod.BankTransfer:
                Console.WriteLine("Providing bank transfer details...");
                // Complex logic for bank transfers...
                break;
            default:
                throw new ArgumentException("Invalid payment method.");
        }
        Console.WriteLine("Payment successful.");
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" refactors the `OrderProcessor` using the Strategy pattern, making it flexible and open for extension.

```csharp
// GOOD CODE: Applying the Strategy Pattern

// Rule 1: Define the Strategy Interface
public interface IPaymentStrategy
{
    void Pay(decimal amount);
}

// Rule 2: Implement Concrete Strategy Classes
public class CreditCardPaymentStrategy : IPaymentStrategy
{
    public void Pay(decimal amount)
    {
        Console.WriteLine("Initiating credit card payment...");
        // Complex logic for credit card processing...
    }
}

public class PayPalPaymentStrategy : IPaymentStrategy
{
    public void Pay(decimal amount)
    {
        Console.WriteLine("Redirecting to PayPal for payment...");
        // Complex logic for PayPal integration...
    }
}

public class BankTransferPaymentStrategy : IPaymentStrategy
{
    public void Pay(decimal amount)
    {
        Console.WriteLine("Providing bank transfer details...");
        // Complex logic for bank transfers...
    }
}

public class Order
{
    public decimal Amount { get; set; }
}

// Rule 3-6: The Context class now delegates payment processing.
public class OrderProcessor
{
    private IPaymentStrategy _paymentStrategy;

    // Rule 5: Provide a way for the client to set the strategy.
    public void SetPaymentStrategy(IPaymentStrategy paymentStrategy)
    {
        _paymentStrategy = paymentStrategy;
    }

    // Rule 6: The context delegates the work.
    public void ProcessOrder(Order order)
    {
        if (_paymentStrategy == null)
        {
            throw new InvalidOperationException("Payment strategy has not been set.");
        }
        Console.WriteLine($"Processing order for amount: ${order.Amount}");
        _paymentStrategy.Pay(order.Amount);
        Console.WriteLine("Payment successful.");
    }
}

// --- Client Code (Composition Root) ---
public class Client
{
    public static void Main()
    {
        var order = new Order { Amount = 150.75m };
        var processor = new OrderProcessor();

        // Scenario 1: User chooses to pay with Credit Card
        Console.WriteLine("Customer chose Credit Card.");
        processor.SetPaymentStrategy(new CreditCardPaymentStrategy());
        processor.ProcessOrder(order);

        Console.WriteLine("\\n------------------\\n");

        // Scenario 2: User chooses to pay with PayPal
        Console.WriteLine("Customer chose PayPal.");
        processor.SetPaymentStrategy(new PayPalPaymentStrategy());
        processor.ProcessOrder(order);

        // Now, adding a new payment method (e.g., Bitcoin) requires
        // ONLY adding a new strategy class. The OrderProcessor class remains unchanged.
    }
}

```