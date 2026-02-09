# Polymorphism

### 1. What is it?

**Polymorphism** is the ability of a program to detect the real class of an object and call its implementation even when its real type is unknown in the current context. It allows an object to "pretend" to be something else, usually a class it extends or an interface it implements .

### 2. Why it is required?

It is required to write generic, flexible code that can work with various objects uniformly without depending on their concrete classes. It eliminates the need for massive conditional checks (like `if (object is Cat)`) effectively allowing you to treat different objects as the same abstract type while retaining their specific behaviors .

### 3. Details and key points and examples in the reference Book?

- **The Bag of Animals (Analogy):** Imagine you put several cats and dogs into a large bag. You close your eyes and pull the animals out one by one. You treat them all as a generic **Animal**. However, if you try to cuddle them, each will emit a specific sound based on its **concrete class** (Joyful *Meow* vs. *Woof*). The program doesn't need to know the concrete type to get the correct behavior (Page 19-20).
- **Abstract Methods:** A parent class (e.g., `Animal`) can declare a method (e.g., `makeSound`) as `abstract`. This enforces that all subclasses *must* provide their own implementation, allowing the parent to omit a default implementation .
- **Mechanism:**
    1. The client refers to an object via a **Base Class** or **Interface**.
    2. The runtime "traces down" the subclass of the object whose method is being executed.
    3. The appropriate behavior is run .

### 2. When to Use vs. When to Avoid?

- **✅ Use When:**
    - You want client code to work with a set of distinct objects in the same way (e.g., an `Airport` accepting any `FlyingTransport` like Helicopter, Airplane, or Gryphon) .
    - You need to eliminate long `switch` or `if/else` statements that check object types to execute behavior (Page 356 - State pattern relies on this).
    - You want to extend the system with new classes without breaking existing code (Open/Closed Principle).
- **⚠️ Avoid When:**
    - The subclasses share no common logical link (LSP violation). You shouldn't force two unrelated classes to implement the same interface just for the sake of polymorphism if they don't fundamentally share a "Is-A" relationship .

### 3. Step By Step Detailed Rules to Map the concept to C# code

1. **Identify Commonality:** Find methods that look the same in name but behave differently across classes.
2. **Define Contract:** Create an `abstract class` or `interface` containing this method.
    - Use `abstract` in C# if the base has no implementation.
    - Use `virtual` in C# if the base has a default implementation.
3. **Override:** In specific subclasses, implement the method using the `override` keyword.
4. **Generalize Client:** In the client code (the "Bag"), use the Base Type (e.g., `Animal`) as the variable type, not the concrete type (`Cat`).

### 4. C# code Example which is not in the correct state

This example shows a "Procedural" approach where the `Program` has to know exactly what it is dealing with, violating Polymorphism and the Open/Closed Principle.

```csharp
// BAD CODE: No Polymorphism.
// 1. Client must know every concrete type.
// 2. Adding a new animal requires changing the 'MakeSound' logic.

public class Cat { public string Name; }
public class Dog { public string Name; }

public class AnimalManager
{
    public void MakeSound(object animal)
    {
        // Violation: Manual type checking instead of Polymorphism
        if (animal is Cat)
        {
            Console.WriteLine("Meow!");
        }
        else if (animal is Dog)
        {
            Console.WriteLine("Woof!");
        }
        else
        {
            Console.WriteLine("Unknown sound");
        }
    }
}

```

### 5. Applying the rules to make it correct

We apply Polymorphism by allowing the objects to "pretend" to be a generic `Animal` while keeping their specific `MakeSound` behavior.

```csharp
using System;
using System.Collections.Generic;

// 1. Define the Base Contract (Abstraction)
public abstract class Animal
{
    // "Abstract" forces subclasses to provide their own implementation
    public abstract void MakeSound();
}

// 2. Implement Specific Behaviors
public class Cat : Animal
{
    // "Override" provides the concrete behavior for this class
    public override void MakeSound()
    {
        Console.WriteLine("Meow!");
    }
}

public class Dog : Animal
{
    public override void MakeSound()
    {
        Console.WriteLine("Woof!");
    }
}

public class Program
{
    public static void Main()
    {
        // 3. Generalize Client (The Bag of Animals - Page 20)
        // We store concrete objects in a list of the Base Type.
        List<Animal> bag = new List<Animal>
        {
            new Cat(),
            new Dog()
        };

        // 4. Polymorphic execution
        foreach (Animal a in bag)
        {
            // The program detects the real class automatically.
            // We don't check "if (a is Cat)".
            a.MakeSound();
        }
    }
}

```