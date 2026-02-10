# Builder Pattern : Example 2

Of course. The reference book "Dive Into Design Patterns" uses a very specific and powerful example for the Builder pattern: constructing a **Car** and its corresponding **Car Manual**.

The key insight from the book is that the *process* of construction (the sequence of steps) can be reused for different end products. A Director can instruct a `CarBuilder` to make a sports car, and then instruct a `CarManualBuilder` with the *exact same steps* to create the manual for that sports car.

Here is that exact example represented in C#.

---

### 1. The Products

These are the complex objects being built. As the book notes, they **do not** need to share a common interface.

```csharp
// The first product is the Car itself.
public class Car
{
    private readonly List<string> _parts = new List<string>();

    public void Add(string part)
    {
        _parts.Add(part);
    }

    public string ListParts()
    {
        return "Car parts: " + string.Join(", ", _parts) + "\\n";
    }
}

// The second, completely different product is the Car Manual.
public class Manual
{
    private readonly List<string> _documentedParts = new List<string>();

    public void Add(string documentation)
    {
        _documentedParts.Add(documentation);
    }

    public string ListDocumentation()
    {
        return "Car Manual: \\n" + string.Join("\\n", _documentedParts) + "\\n";
    }
}

// A helper class representing a car engine.
public class Engine
{
    public string Type { get; set; }
}

```

### 2. The Builder Interface

This interface defines the common construction steps required to build *any* representation of the product.

```csharp
// The Builder interface specifies methods for creating the different parts of the product objects.
public interface IBuilder
{
    // A fresh builder instance should contain a blank product object
    // which it uses in further assembly.
    void Reset();

    // All production steps work with the same product instance.
    void SetSeats(int number);
    void SetEngine(Engine engine);
    void SetTripComputer();
    void SetGPS();
}

```

### 3. The Concrete Builders

These classes implement the `IBuilder` interface to construct and assemble parts in their own specific way. One builds a car, the other builds a manual.

```csharp
// The Concrete Builder for creating Car objects.
public class CarBuilder : IBuilder
{
    private Car _car;

    public CarBuilder()
    {
        this.Reset();
    }

    public void Reset()
    {
        _car = new Car();
    }

    public void SetSeats(int number) => _car.Add($"- {number} seats");
    public void SetEngine(Engine engine) => _car.Add($"- {engine.Type}");
    public void SetTripComputer() => _car.Add("- Trip Computer");
    public void SetGPS() => _car.Add("- GPS Navigator");

    // Concrete builders provide their own methods for retrieving results
    // because various builders may create entirely different products that
    // don't all follow the same interface.
    public Car GetProduct()
    {
        Car result = _car;
        this.Reset(); // Get ready for the next build.
        return result;
    }
}

// The Concrete Builder for creating Manual objects.
// It follows the same building steps but produces a different product.
public class CarManualBuilder : IBuilder
{
    private Manual _manual;

    public CarManualBuilder()
    {
        this.Reset();
    }

    public void Reset()
    {
        _manual = new Manual();
    }

    public void SetSeats(int number) => _manual.Add($"Document car seat features: Describes how to use the {number} seats.");
    public void SetEngine(Engine engine) => _manual.Add($"Document engine specs: Details for the {engine.Type}.");
    public void SetTripComputer() => _manual.Add("Document trip computer: Instructions for the onboard computer.");
    public void SetGPS() => _manual.Add("Document GPS: User manual for the navigation system.");

    public Manual GetProduct()
    {
        Manual result = _manual;
        this.Reset();
        return result;
    }
}

```

### 4. The Director (Optional)

The Director class defines the order of building steps. It encapsulates common construction logic to create popular product variations.

```csharp
// The Director is only responsible for executing the building steps in a
// particular sequence. It is helpful when producing products according to a
// specific order or configuration.
public class Director
{
    // The director can construct several product variations using the same building steps.
    public void ConstructSportsCar(IBuilder builder)
    {
        builder.Reset();
        builder.SetSeats(2);
        builder.SetEngine(new Engine { Type = "SportEngine" });
        builder.SetTripComputer();
        builder.SetGPS();
    }

    public void ConstructSUV(IBuilder builder)
    {
        builder.Reset();
        builder.SetSeats(4);
        builder.SetEngine(new Engine { Type = "SUVEngine" });
        builder.SetGPS();
    }
}

```

### 5. Client Code (Demonstration)

The client decides which concrete builder to use and, optionally, which director routine to run. The final product is always retrieved from the builder.

```csharp
public class Application
{
    public static void Main()
    {
        // The client code creates a director, and two types of builders.
        var director = new Director();
        var carBuilder = new CarBuilder();
        var manualBuilder = new CarManualBuilder();

        // --- Use Case 1: Build a sports car using the Director ---
        Console.WriteLine("Director is building a sports car...");
        director.ConstructSportsCar(carBuilder);

        // The final product is retrieved from the car builder object. The director
        // isn't aware of and not dependent on concrete builders and products.
        Car sportsCar = carBuilder.GetProduct();
        Console.WriteLine($"Car built: {sportsCar.ListParts()}");

        // --- Use Case 2: Build a manual for the sports car using the SAME director logic ---
        Console.WriteLine("Director is now building the manual for the sports car...");
        // The Director runs the exact same sequence of steps, but this time on the manual builder.
        director.ConstructSportsCar(manualBuilder);
        Manual sportsCarManual = manualBuilder.GetProduct();
        Console.WriteLine($"Manual built:\\n{sportsCarManual.ListDocumentation()}");

        // --- Use Case 3: Build a custom car without a Director ---
        Console.WriteLine("Client is building a custom car without a director...");
        carBuilder.Reset();
        carBuilder.SetSeats(5);
        carBuilder.SetGPS();
        Car customCar = carBuilder.GetProduct();
        Console.WriteLine($"Custom car built: {customCar.ListParts()}");
    }
}

```