# Inheritance

### 1. What is it?

Inheritance is one of the four core pillars of Object-Oriented Programming (OOP). It is a mechanism that allows a new class (known as a **subclass** or **child class**) to be based on an existing class (the **superclass** or **parent class**). The subclass automatically acquires the fields (state) and methods (behavior) of the superclass, which can then be extended or modified.

### 2. Why it is required?

The primary and most significant benefit of inheritance is **code reuse**. It allows developers to create a new class that is slightly different from an existing one without duplicating code. Instead of writing the same logic in multiple classes, you can define it once in a superclass and have multiple subclasses inherit it. This creates a logical hierarchy and reduces redundancy, making the code easier to maintain and understand.

### 3. Details and key points and examples in the reference Book

- **Core Concept:**
    - Inheritance is defined as the ability to build new classes on top of existing ones.
    - It represents an **"is a"** relationship (e.g., a *Car is a Transport*).
- **Terminology and Structure:**
    - A parent class is called a **superclass**. Its children are called **subclasses**.
    - Subclasses inherit both the state (fields) and behavior (methods) from their parent.
    - A chain of inheritance creates a **class hierarchy**.
        - **Book Example:** An `Animal` class can be a superclass for `Cat` and `Dog` subclasses. Both share common attributes like `name`, `age`, and behaviors like `breathe()` and `sleep()`. The `Animal` class itself could be a subclass of a more general `Organism` class.
- **Key Rules and Consequences:**
    - The subclass has the same public interface as its parent but can add new functionality.
    - A subclass cannot hide or remove a method that was declared in the superclass.
    - If a superclass defines **abstract** methods, the subclass is forced to implement them.
- **Limitations in Most Languages:**
    - A subclass can typically extend only **one** superclass.
    - However, a class can implement **multiple** interfaces.
- **Overriding Behavior:**
    - Subclasses can **override** the behavior of methods inherited from parent classes. This allows a subclass to either completely replace the default behavior or enhance it with additional logic.
- **Inheritance vs. Composition:**
    - The book strongly advises to **"Favor Composition Over Inheritance"** because inheritance introduces several problems:
        - **Breaks Encapsulation:** The internal details of the parent class often become available to the subclass, breaking encapsulation.
        - **Tight Coupling:** Subclasses are tightly coupled to their superclasses. Any change in the superclass can potentially break the functionality of its subclasses.
        - **Rigid Hierarchies:** Trying to reuse code with inheritance can lead to parallel and bloated class hierarchies when multiple dimensions are involved (e.g., Vehicle Type, Engine Type, Control Type), resulting in a "combinatorial explosion" of classes.

### 4. When to Use vs. When to Avoid?

- **✅ When to Use:**
    - When there is a clear **"is a"** relationship between classes that fits a logical hierarchy.
    - When you want to reuse a significant amount of code and the base class logic is stable and unlikely to change frequently.
    - When you need to take advantage of polymorphism, allowing you to treat objects of a subclass as objects of their superclass.
- **⚠️ When to Avoid (Anti-Pattern Warning):**
    - Avoid inheritance just for code reuse if there isn't a logical "is a" relationship. This is a common form of over-engineering.
    - **Warning:** Avoid inheritance when you have multiple, independent dimensions of variation. This leads to a rigid and unmanageable class hierarchy. The book's example shows creating classes for `ElectricCar`, `GasCar`, `ElectricTruck`, etc. This becomes unmanageable when another dimension like `Autopilot` is added. In such cases, **Composition** is a far superior choice.
    - Avoid it if you find yourself needing to reduce or restrict the interface of the superclass, as inheritance does not allow this.

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Declare the Base Class:** Create the parent class (`superclass`). This class should contain the common fields, properties, and methods. Mark methods that subclasses should be able to change as `virtual`.
2. **Declare the Derived Class:** To make a new class inherit from the base class, use the colon (`:`) syntax followed by the base class name.
3. **Override Methods:** In the derived class, use the `override` keyword to provide a new implementation for a `virtual` (or `abstract`) method from the base class.
4. **Use the `base` Keyword:** To call a method or constructor from the base class, use the `base` keyword. This is most common for invoking a parent's constructor (`: base(...)`) or a parent's overridden method (`base.MethodName()`).
5. **Use Abstract Classes for Skeletons:** If a base class is not complete on its own and should not be instantiated, declare it as `abstract`. You can also declare methods within it as `abstract`, which forces all concrete subclasses to provide their own implementation.

### 6. C# code Example which is not in the correct state

This "Bad Code" demonstrates two classes with significant code duplication because they do not use inheritance.

```csharp
// BAD CODE: HIGHLY REPETITIVE
using System;

public class Truck
{
    public string LicensePlate { get; set; }
    public int WeightCapacity { get; set; }
    public int CurrentFuel { get; private set; }

    public Truck(string licensePlate)
    {
        LicensePlate = licensePlate;
        CurrentFuel = 100; // Start with a full tank
    }

    // Common logic
    public void StartEngine()
    {
        Console.WriteLine("Truck engine started. Vroom vroom!");
    }

    // Common logic
    public void Refuel()
    {
        CurrentFuel = 100;
        Console.WriteLine("Truck has been refueled.");
    }

    // Specific logic
    public void LoadCargo()
    {
        Console.WriteLine("Loading heavy cargo onto the truck.");
    }
}

public class Sedan
{
    public string LicensePlate { get; set; }
    public int PassengerCapacity { get; set; }
    public int CurrentFuel { get; private set; }

    public Sedan(string licensePlate)
    {
        LicensePlate = licensePlate;
        CurrentFuel = 100; // Start with a full tank
    }

    // Common logic (Duplicated)
    public void StartEngine()
    {
        Console.WriteLine("Sedan engine started. Smooth purr.");
    }

    // Common logic (Duplicated)
    public void Refuel()
    {
        CurrentFuel = 100;
        Console.WriteLine("Sedan has been refueled.");
    }

    // Specific logic
    public void OpenTrunk()
    {
        Console.WriteLine("Opening the sedan's trunk for groceries.");
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" refactors the previous example by creating a base `Vehicle` class, eliminating redundant code and establishing a logical hierarchy.

```csharp
// GOOD CODE: USING INHERITANCE TO REUSE CODE
using System;

// Rule 1 & 5: Create an abstract base class with common logic.
public abstract class Vehicle
{
    // Common Properties are defined once.
    public string LicensePlate { get; set; }
    public int CurrentFuel { get; protected set; }

    // Base constructor handles common initialization.
    public Vehicle(string licensePlate)
    {
        LicensePlate = licensePlate;
        CurrentFuel = 100; // All vehicles start full
    }

    // Common method is defined once.
    public void Refuel()
    {
        CurrentFuel = 100;
        Console.WriteLine($"{this.GetType().Name} with plate {LicensePlate} has been refueled.");
    }

    // A method that can be overridden by subclasses.
    public virtual void StartEngine()
    {
        Console.WriteLine("Vehicle engine started.");
    }
}

// Rule 2: Create derived classes using the ':' syntax.
public class Truck : Vehicle
{
    public int WeightCapacity { get; set; }

    // Rule 4: Call the base constructor to pass the license plate up.
    public Truck(string licensePlate, int weight) : base(licensePlate)
    {
        WeightCapacity = weight;
    }

    // Rule 3: Override the virtual method for specific behavior.
    public override void StartEngine()
    {
        // We could optionally call the base method if needed: base.StartEngine();
        Console.WriteLine("Truck engine started. Vroom vroom!");
    }

    // Specific logic remains only in the Truck class.
    public void LoadCargo()
    {
        Console.WriteLine("Loading heavy cargo onto the truck.");
    }
}

public class Sedan : Vehicle
{
    public int PassengerCapacity { get; set; }

    public Sedan(string licensePlate, int passengers) : base(licensePlate)
    {
        PassengerCapacity = passengers;
    }

    public override void StartEngine()
    {
        Console.WriteLine("Sedan engine started. Smooth purr.");
    }

    // Specific logic remains only in the Sedan class.
    public void OpenTrunk()
    {
        Console.WriteLine("Opening the sedan's trunk for groceries.");
    }
}

```