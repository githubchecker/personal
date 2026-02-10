# Encapsulation

# 1. What is it?

**Encapsulation** is the ability of an object to hide parts of its state and behaviors from other objects, exposing only a limited interface to the rest of the program. To "encapsulate" something means to make it `private`, thus accessible only from within the methods of its own class.

### 2. Why it is required?

It is required to protect the internal state of an object from being corrupted by unwanted external interference. It ensures that clients use the object only through a defined "contract" (Interface).
Furthermore, applying the principle **"Encapsulate What Varies"**  minimizes the effect caused by changes. If a specific logic (like tax calculation) changes, it shouldn't break unrelated parts of the code.

### 3. Details and key points and examples in the reference Book?

- **Real-World Analogy (The Car):** To start a car engine, you only turn a key or press a button. You don't need to connect wires under the hood, rotate the crankshaft, or control the fuel injectors manually. Those details are hidden; you only interact with the public interface (Start Button) .
- **Encapsulate What Varies (The Ship):** The book compares a program to a ship. If the hull is not divided into compartments (encapsulated modules), a single breach (change/bug) can sink the whole ship. Encapsulating varying parts seals them in compartments .
- **Levels of Encapsulation:**
    1. **Method Level:** Extracting a piece of logic (e.g., tax calculation) into a separate private method .
    2. **Class Level:** Moving that logic into a completely separate class (e.g., `TaxCalculator`) to decouple it from the main class .

### 2. When to Use vs. When to Avoid?

- **✅ Use When:**
    - You need to protect specific fields (invariants) from invalid values.
    - You anticipate a specific chunk of logic will change in the future (e.g., Tax rates in US vs. EU) .
    - You want to decouple components so they interact only via Interfaces, not concrete implementations.
- **⚠️ Avoid When:**
    - You are writing a very simple script or a tiny program (~200 lines) where setting up complex privacy scopes adds unnecessary boilerplate.

### 3. Step By Step Detailed Rules to Map the concept to C# code

1. **Hide State:** Mark all fields representing the internal state as `private` or `protected` .
2. **Define Interface:** Create `public` methods (or C# properties) that act as the "buttons" or "keys" to interact with that state.
3. **Isolate Logic (Method Level):** If a method performs a calculation that might change (like `getTaxRate`), extract it into a separate `private` method .
4. **Delegate (Class Level):** If the logic becomes too complex, extract it into a new class and hold a reference to it using Composition, rather than inheriting or hard-coding it .

### 4. C# code Example which is not in the correct state

This example (based on Page 37) demonstrates **Bad Code** where tax calculation logic is mixed directly into the main order method, and fields are exposed publicly.

```csharp
// BAD CODE: No Encapsulation.
// 1. Fields are public (State is exposed).
// 2. "Varying" logic (Tax) is hardcoded inside the main flow.
public class Order
{
    public List<Item> lineItems; // Public access to internal list
    public string country;

    public double GetOrderTotal()
    {
        double total = 0;
        foreach (var item in lineItems)
        {
            total += item.Price * item.Quantity;
        }

        // Violation: Tax logic is mixed here.
        // If tax laws change, we risk breaking the 'total' calculation.
        if (country == "US")
        {
            total += total * 0.07; // US Tax
        }
        else if (country == "EU")
        {
            total += total * 0.20; // EU VAT
        }

        return total;
    }
}

```

### 5. Applying the rules to make it correct

Here we apply **Method Level Encapsulation**  and **Class Level Encapsulation**  to hide the tax logic and protect the data.

```csharp
using System.Collections.Generic;

// 1. We define a strict interface/contract for tax calculations (Abstraction/Encapsulation)
public interface ITaxCalculator
{
    double GetTaxRate(string country);
}

// 2. We encapsulate the varying logic into its own class
public class TaxCalculator : ITaxCalculator
{
    public double GetTaxRate(string country)
    {
        if (country == "US") return 0.07;
        if (country == "EU") return 0.20;
        return 0;
    }
}

public class Order
{
    // 3. Internal state is hidden (Private/Protected)
    private readonly List<Item> _lineItems;
    private readonly string _country;
    private readonly ITaxCalculator _taxCalculator;

    public Order(string country, ITaxCalculator taxCalculator)
    {
        _country = country;
        _lineItems = new List<Item>();
        _taxCalculator = taxCalculator; // 4. Delegating to an encapsulated object
    }

    // Public Interface to add items (protects the list from being nullified)
    public void AddItem(Item item)
    {
        _lineItems.Add(item);
    }

    public double GetOrderTotal()
    {
        double total = 0;
        foreach (var item in _lineItems)
        {
            total += item.Price * item.Quantity;
        }

        // 5. The "Varying" logic is encapsulated.
        // We just call the method. We don't care HOW tax is found.
        total += total * _taxCalculator.GetTaxRate(_country);

        return total;
    }
}

```