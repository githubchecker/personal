# Observer Pattern

### 1. What is it?

The Observer is a behavioral design pattern that defines a subscription mechanism to notify multiple objects about any events that happen to the object they are observing. The object that has the interesting state is called the **Publisher** (or Subject), and the objects that want to track its changes are called **Subscribers** (or Observers).

The pattern establishes a one-to-many relationship where, when the Publisher's state changes, all of its dependent Subscribers are notified and updated automatically.

The book uses the analogy of a magazine subscription: you (a Subscriber) subscribe to a magazine (the Publisher). When a new issue is released, the publisher automatically sends it to you. The publisher doesn't need to know who you are personally, it just maintains a list of subscribers. You can subscribe or unsubscribe at any time.

### 2. Why it is required?

The Observer pattern is required to solve the problem of tight coupling between related objects. Imagine an object whose state is important to other objects. Without this pattern, you face two bad options:

1. **Polling (The Client Wastes Time):** Other objects constantly have to poll the main object to check if its state has changed. This is inefficient and leads to a lot of pointless checks, as illustrated by the book's `Customer` repeatedly visiting the `Store`.
2. **Tight Coupling (The Publisher is Fragile):** The main object has explicit references to all the objects it needs to notify. This makes the publisher's code complex and hard to maintain. To add a new subscriber type, you must modify the publisher's source code, which violates the Open/Closed Principle.

The Observer pattern solves this by creating a dynamic relationship. The publisher is only coupled to a simple subscriber interface, not to any concrete subscriber classes.

### 3. Details and key points and examples in the reference Book

- **Core Concept:**
    - The pattern suggests adding a subscription mechanism to the **Publisher** class. This mechanism consists of:
        1. A field to store a list of references to its **Subscribers**.
        2. Public methods to `subscribe()` (add) and `unsubscribe()` (remove) subscribers from that list.
- **The Notification Process:**
    - Whenever an important event happens in the Publisher, it iterates over its list of subscribers and calls a specific notification method (e.g., `update()`) on each of their objects.
- **The Common Interface:**
    - It's crucial that all subscribers implement the same interface. This is the key to decoupling. The Publisher communicates with all subscribers only through this interface.
    - This interface declares the notification method and its parameters, which the publisher uses to pass contextual data about the event.
- **Passing Context:**
    - When the publisher notifies a subscriber, it often needs to pass some data about what happened. A common and flexible way to do this is for the publisher to pass a reference to itself (`this`). The subscriber can then fetch any required data directly from the publisher object.
- **Publisher Hierarchy:**
    - If you have many different types of publishers, you can make them all follow a common publisher interface, which would only contain the subscription methods.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - When changes to the state of one object may require changing other objects, and the actual set of objects is unknown beforehand or changes dynamically.
    - When an object in your application needs to notify other objects without being tightly coupled to them. This is extremely common in event-driven systems and GUIs.
    - When some objects in your app must observe others, but only for a limited time or in specific cases (due to the dynamic nature of subscribing/unsubscribing).
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - **Notification Order:** The book notes that subscribers are notified in whatever order they are stored in the list, which can seem random. If the order of notifications is important, this pattern requires modification or another pattern should be considered.
    - **Overkill for Simple Cases:** If the relationship between objects is simple, stable, and one-to-one, using the full pattern might be an over-complication.
    - **Accidental Complexity:** Be careful not to create overly complex notification chains (an observer of an observer of an observer...), as this can make debugging very difficult.

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Define a Subscriber Interface:** Create an interface (e.g., `IObserver`) with a single notification method, typically named `Update()`. This method should accept the publisher as an argument to allow for data fetching (e.g., `void Update(IPublisher publisher);`).
2. **Define a Publisher Interface:** Create an interface (e.g., `IPublisher`) that defines the subscription management methods: `Subscribe(IObserver observer)`, `Unsubscribe(IObserver observer)`, and a method for triggering notifications, `Notify()`.
3. **Implement the Concrete Publisher:** Create your main business object and make it implement the `IPublisher` interface.
    - Inside this class, add a `private List<IObserver> _observers = new List<IObserver>();`.
    - Implement the `Subscribe` and `Unsubscribe` methods to add/remove observers from this list.
    - Implement the `Notify` method to loop through the list and call `observer.Update(this)` on each one.
    - In your business logic methods, call `Notify()` whenever the state changes.
4. **Implement Concrete Subscribers:** Create classes that will react to notifications and make them implement the `IObserver` interface. Place the reaction logic inside the `Update()` method.
5. **Wire them up in the Client:** The client code is responsible for creating the publisher and subscriber objects and then registering the subscribers with the publisher by calling `publisher.Subscribe(subscriber)`.

### 6. C# code Example which is not in the correct state

This "Bad Code" shows a `WeatherStation` that is tightly coupled to the specific UI panels it needs to update.

```csharp
// BAD CODE: Tightly coupled and violates Open/Closed Principle.

// These are concrete UI panels.
public class CurrentConditionsDisplay
{
    public void Update(float temp, float humidity)
    {
        Console.WriteLine($"Current Conditions: {temp}F degrees and {humidity}% humidity.");
    }
}

public class ForecastDisplay
{
    public void Update(float pressure)
    {
        Console.WriteLine($"Forecast: Expect improving weather if pressure is rising ({pressure}).");
    }
}

public class WeatherStation
{
    // The WeatherStation has direct references to the concrete displays.
    private readonly CurrentConditionsDisplay _currentDisplay;
    private readonly ForecastDisplay _forecastDisplay;

    private float _temperature;
    private float _humidity;
    private float _pressure;

    // It must know about all displays at construction time.
    public WeatherStation()
    {
        _currentDisplay = new CurrentConditionsDisplay();
        _forecastDisplay = new ForecastDisplay();
    }

    // When the state changes, it must call each display's specific method.
    // What if we want to add a third display? We must modify this method!
    public void MeasurementsChanged()
    {
        _currentDisplay.Update(_temperature, _humidity);
        _forecastDisplay.Update(_pressure);
    }

    // A method to simulate new weather data
    public void SetMeasurements(float temp, float humidity, float pressure)
    {
        _temperature = temp;
        _humidity = humidity;
        _pressure = pressure;
        MeasurementsChanged();
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" refactors the `WeatherStation` using the Observer pattern, decoupling it from the concrete display panels.

```csharp
// GOOD CODE: Applying the Observer Pattern

// Rule 1: Define the Subscriber (Observer) Interface
public interface IObserver
{
    // The Update method takes the publisher as context.
    void Update(WeatherStation station);
}

// Rule 3: Implement the Concrete Publisher
public class WeatherStation
{
    // It manages a list of observers, not concrete classes.
    private readonly List<IObserver> _observers = new List<IObserver>();

    public float Temperature { get; private set; }
    public float Humidity { get; private set; }
    public float Pressure { get; private set; }

    public void Subscribe(IObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IObserver observer) => _observers.Remove(observer);

    public void Notify()
    {
        // It notifies all subscribed observers via the common interface.
        foreach (var observer in _observers)
        {
            observer.Update(this);
        }
    }

    // When measurements change, it just calls Notify. It doesn't know who is listening.
    public void SetMeasurements(float temp, float humidity, float pressure)
    {
        Temperature = temp;
        Humidity = humidity;
        Pressure = pressure;
        Notify();
    }
}

// Rule 4: Implement Concrete Subscribers
public class CurrentConditionsDisplay : IObserver
{
    public void Update(WeatherStation station)
    {
        // It pulls the data it needs from the publisher.
        Console.WriteLine($"Current Conditions: {station.Temperature}F degrees and {station.Humidity}% humidity.");
    }
}

public class ForecastDisplay : IObserver
{
    public void Update(WeatherStation station)
    {
        Console.WriteLine($"Forecast: Expect improving weather if pressure is rising ({station.Pressure}).");
    }
}

// Now we can easily add new displays without changing the WeatherStation class!
public class StatisticsDisplay : IObserver
{
    public void Update(WeatherStation station)
    {
        Console.WriteLine($"Statistics: Temp range is... (logic for stats).");
    }
}

// Rule 5: The Client wires everything together.
public static class Client
{
    public static void Main()
    {
        // 1. Create the publisher.
        var weatherStation = new WeatherStation();

        // 2. Create subscribers.
        var currentDisplay = new CurrentConditionsDisplay();
        var forecastDisplay = new ForecastDisplay();
        var statsDisplay = new StatisticsDisplay(); // Adding a new one is easy.

        // 3. Register the subscribers with the publisher.
        weatherStation.Subscribe(currentDisplay);
        weatherStation.Subscribe(forecastDisplay);
        weatherStation.Subscribe(statsDisplay);

        // 4. Simulate a new weather measurement.
        // This will automatically notify all three displays.
        weatherStation.SetMeasurements(80, 65, 30.4f);

        Console.WriteLine("\\n--- One observer unsubscribes ---\\n");
        weatherStation.Unsubscribe(forecastDisplay);

        // 5. Simulate another measurement. Only two displays will be notified.
        weatherStation.SetMeasurements(82, 70, 29.2f);
    }
}

```

The Observer pattern is so fundamental to C# that the language has first-class features to support it directly: `delegate` and `event`. This makes the implementation much cleaner and more idiomatic than the manual list-based approach.

This "Good Code" refactors the `WeatherStation` using C# `event` and `EventHandler<T>`, the idiomatic way to implement the Observer pattern.

```csharp
// GOOD CODE: Applying the Observer Pattern with C# events.
using System;

// Rule 1: Define the event arguments object to carry data.
public class WeatherDataEventArgs : EventArgs
{
    public float Temperature { get; }
    public float Humidity { get; }
    public float Pressure { get; }

    public WeatherDataEventArgs(float temp, float humidity, float pressure)
    {
        Temperature = temp;
        Humidity = humidity;
        Pressure = pressure;
    }
}

// --- The Publisher ---
public class WeatherStation
{
    // Rule 2: Declare the event using the EventHandler<T> delegate.
    public event EventHandler<WeatherDataEventArgs> MeasurementsChanged;

    // Rule 3: Create a protected method to raise the event.
    protected virtual void OnMeasurementsChanged(WeatherDataEventArgs e)
    {
        // Check if there are any subscribers before invoking.
        MeasurementsChanged?.Invoke(this, e);
    }

    // Business logic that triggers the notification.
    public void SetMeasurements(float temp, float humidity, float pressure)
    {
        var eventArgs = new WeatherDataEventArgs(temp, humidity, pressure);
        // Rule 4: Call the notification method.
        OnMeasurementsChanged(eventArgs);
    }
}

// --- The Subscribers ---
public class CurrentConditionsDisplay
{
    // Rule 5: Create a handler method that matches the event's signature.
    public void HandleWeatherChange(object sender, WeatherDataEventArgs e)
    {
        Console.WriteLine($"Current Conditions: {e.Temperature}F degrees and {e.Humidity}% humidity.");
    }
}

public class ForecastDisplay
{
    public void HandleWeatherChange(object sender, WeatherDataEventArgs e)
    {
        Console.WriteLine($"Forecast: Expect improving weather if pressure is rising ({e.Pressure}).");
    }
}

// --- The Client (Composition Root) ---
public static class Client
{
    public static void Main()
    {
        // 1. Create the publisher and subscribers.
        var weatherStation = new WeatherStation();
        var currentDisplay = new CurrentConditionsDisplay();
        var forecastDisplay = new ForecastDisplay();

        // 2. Rule 6: Use += to subscribe the handler methods to the event.
        weatherStation.MeasurementsChanged += currentDisplay.HandleWeatherChange;
        weatherStation.MeasurementsChanged += forecastDisplay.HandleWeatherChange;

        // 3. Simulate new measurements. This will notify both subscribers.
        weatherStation.SetMeasurements(80, 65, 30.4f);

        Console.WriteLine("\\n--- Forecast display unsubscribes ---\\n");

        // 4. Use -= to unsubscribe.
        weatherStation.MeasurementsChanged -= forecastDisplay.HandleWeatherChange;

        // 5. Simulate another measurement. Only the current display will be notified.
        weatherStation.SetMeasurements(82, 70, 29.2f);
    }
}

```