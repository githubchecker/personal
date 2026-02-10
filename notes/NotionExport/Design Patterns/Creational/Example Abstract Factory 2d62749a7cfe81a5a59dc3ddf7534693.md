# Example : Abstract Factory

C# Example of Abstract Factory with Comments

Here is a C# implementation of the Abstract Factory pattern, based on the book's furniture example. It demonstrates how to create families of related objects (`Chair`, `Sofa`) in different styles (`Modern`, `Victorian`) without coupling the client to the concrete classes.

```csharp
using System;

// Step 1: Define Abstract Product Interfaces
// Each distinct product of a family should have a base interface.
// All variants of the product must implement this interface.

public interface IChair
{
    bool HasLegs();
    void SitOn();
}

public interface ISofa
{
    int NumberOfSeats();
    void LieOn();
}

// Step 2: Create Concrete Product Classes
// For each product variant, create concrete classes that implement the abstract interfaces.

// Modern Product Family
public class ModernChair : IChair
{
    public bool HasLegs() => false;
    public void SitOn() => Console.WriteLine("Sitting on a sleek modern chair.");
}

public class ModernSofa : ISofa
{
    public int NumberOfSeats() => 3;
    public void LieOn() => Console.WriteLine("Lying on a minimalist modern sofa.");
}

// Victorian Product Family
public class VictorianChair : IChair
{
    public bool HasLegs() => true;
    public void SitOn() => Console.WriteLine("Sitting on an ornate Victorian chair.");
}

public class VictorianSofa : ISofa
{
    public int NumberOfSeats() => 2;
    public void LieOn() => Console.WriteLine("Lying on a plush Victorian sofa.");
}

// Step 3: Define the Abstract Factory Interface
// This interface declares a set of methods for creating each of the abstract products.
// It acts as a contract for creating a family of related items.
public interface IFurnitureFactory
{
    IChair CreateChair();
    ISofa CreateSofa();
}

// Step 4: Create Concrete Factory Classes
// For each product family variant, create a concrete factory class.
// This class implements the abstract factory and is responsible for creating
// a specific family of products.

public class ModernFurnitureFactory : IFurnitureFactory
{
    public IChair CreateChair()
    {
        // Returns the "Modern" variant of a chair.
        return new ModernChair();
    }

    public ISofa CreateSofa()
    {
        // Returns the "Modern" variant of a sofa.
        return new ModernSofa();
    }
}

public class VictorianFurnitureFactory : IFurnitureFactory
{
    public IChair CreateChair()
    {
        // Returns the "Victorian" variant of a chair.
        return new VictorianChair();
    }

    public ISofa CreateSofa()
    {
        // Returns the "Victorian" variant of a sofa.
        return new VictorianSofa();
    }
}

// Step 5: Create the Client
// The client class works with factories and products only through their
// abstract interfaces. This makes the client independent of the concrete variants.
public class FurnitureShop
{
    private readonly IChair _chair;
    private readonly ISofa _sofa;

    // The client accepts any factory that implements the interface.
    public FurnitureShop(IFurnitureFactory factory)
    {
        Console.WriteLine("Assembling furniture using the provided factory...");
        _chair = factory.CreateChair();
        _sofa = factory.CreateSofa();
    }

    public void ShowcaseFurniture()
    {
        Console.WriteLine("\\n--- Showcasing Furniture ---");
        _chair.SitOn();
        Console.WriteLine($"Chair has legs: {_chair.HasLegs()}");

        _sofa.LieOn();
        Console.WriteLine($"Sofa has {_sofa.NumberOfSeats()} seats.");
    }
}

// Step 6: Application Entry Point (Composition Root)
// This is where a specific concrete factory is chosen and passed to the client.
public static class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("Customer wants a 'Modern' furniture set.");
        // Create a Modern factory
        IFurnitureFactory modernFactory = new ModernFurnitureFactory();
        // Pass the factory to the client
        FurnitureShop modernShop = new FurnitureShop(modernFactory);
        modernShop.ShowcaseFurniture();

        Console.WriteLine("\\n" + new string('-', 40) + "\\n");

        Console.WriteLine("Another customer wants a 'Victorian' furniture set.");
        // Create a Victorian factory
        IFurnitureFactory victorianFactory = new VictorianFurnitureFactory();
        // Pass the different factory to the same client class
        FurnitureShop victorianShop = new FurnitureShop(victorianFactory);
        victorianShop.ShowcaseFurniture();
    }
}

```