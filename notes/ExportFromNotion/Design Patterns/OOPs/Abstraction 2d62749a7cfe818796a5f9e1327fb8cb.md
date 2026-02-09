# Abstraction

Here is the **Detailed Analysis of Abstraction** using your new **CodeZ** template, strictly derived from **"Dive Into Design Patterns"**.

# 🚧 Template: CodeZ | Subject: Abstraction

### 1. What is it?

**Abstraction** is a model of a real-world object or phenomenon, limited to a specific context. It represents all details relevant to this specific context with high accuracy and omits all the rest.

### 2. Why it is required?

Objects in a program usually don't represent the real-world originals with 100% accuracy, and it's rarely required that they do. Trying to model every single aspect of a real object leads to unnecessary complexity. Abstraction is required to filter out "noise" so the program only deals with data and behavior that matters for the specific business logic

### 3. Details and key points and examples in the reference Book?

The book illustrates this concept using an **Airplane** :

- **Real World Object:** An actual Airplane has thousands of parts, physics, distinct engine types, passenger manifests, and fuel chemistry.
- **Context A (Flight Simulator):**
    - *Relevant:* Flight physics, speed, altitude, roll angle, pitch angle, yaw angle.
    - *Irrelevant:* Ticket prices, seat mapping, meal preferences.
- **Context B (Flight Booking App):**
    - *Relevant:* Seat map, available seats, ticket pricing.
    - *Irrelevant:* Engine oil pressure, aerodynamics, roll angle.

**Key Point:** The objects in your code only *model* attributes and behaviors of real objects in a specific context, ignoring the rest.

### 2. When to Use vs. When to Avoid?

- **✅ Use When:**
    - You are modeling real-world entities and need to decide which attributes to include in your class.
    - You want to separate the high-level business logic (What should happen) from the implementation details (How it happens).
- **⚠️ Avoid When:**
    - **Over-engineering:** Creating "God Classes" that try to model every aspect of an object for potential "future use" (YAGNI - You Ain't Gonna Need It).
    - Modeling attributes that the current application logic never accesses.

### 3. Step By Step Detailed Rules to Map the concept to C# code

1. **Analyze the Domain:** Determine strictly what the application does (e.g., "Simulate flying" vs. "Book tickets").
2. **List Attributes:** Write down real-world properties of the entity.
3. **Filter:** Remove any property or behavior that does not directly support the Domain logic.
4. **Define Contract:** Create an `abstract class` or `interface` in C# that defines the essential behavior (public interface) without exposing internal clutter.
5. **Encapsulate:** Ensure state (fields) are hidden (`private`) and only modified via the defined methods (Encapsulation usually pairs with Abstraction).

### 4. C# Code Example which is not in the correct state

This example violates Abstraction by mixing two different contexts (Simulator vs. Booking) into a single confusing entity.

```csharp
// BAD CODE: Mixing abstractions.
// This class tries to be everything: a physics model AND a commercial product.
public class GodAirplane
{
    // Flight Physics context
    public double Altitude { get; set; }
    public double Speed { get; set; }
    public double RollAngle { get; set; }

    // Booking context
    public Dictionary<string, bool> SeatMap { get; set; }
    public decimal TicketPrice { get; set; }

    // Logic mixed together
    public void Fly()
    {
        // Physics calculations...
    }

    public void ReserveSeat(string seatNumber)
    {
        // Booking logic...
    }
}

```

### 5. Applying the rules to make it correct

We apply Abstraction by separating the concerns based on the **Context**. We create focused models that only contain what is necessary for that specific domain.

```csharp
using System;
using System.Collections.Generic;

// Context 1: Flight Simulator Application
// We only care about physics and movement.
public abstract class FlightSimEntity
{
    protected double Speed;
    protected double Altitude;

    public abstract void Fly();
}

public class SimulatorAirplane : FlightSimEntity
{
    // Relevant details for Simulator ONLY
    private double _rollAngle;
    private double _pitchAngle;

    public override void Fly()
    {
        Console.WriteLine("Calculating aerodynamics and engine thrust...");
    }

    public void AdjustPitch(double degrees)
    {
        _pitchAngle += degrees;
    }
}

// Context 2: Airline Booking Application
// We only care about inventory and commerce.
public interface IBookableAsset
{
    bool IsSeatAvailable(string seatId);
    void Reserve(string seatId);
}

public class CommercialAirplane : IBookableAsset
{
    // Relevant details for Booking ONLY
    private Dictionary<string, bool> _seats = new Dictionary<string, bool>();
    public decimal TicketPrice { get; private set; }

    public bool IsSeatAvailable(string seatId)
    {
        return _seats.ContainsKey(seatId) && !_seats[seatId];
    }

    public void Reserve(string seatId)
    {
        if (IsSeatAvailable(seatId))
        {
            _seats[seatId] = true;
            Console.WriteLine($"Seat {seatId} reserved.");
        }
    }
}
```