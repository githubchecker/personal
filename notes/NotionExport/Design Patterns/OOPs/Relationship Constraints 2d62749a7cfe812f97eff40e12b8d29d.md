# Relationship Constraints

### 1. What is it?

It is a hierarchy of coupling between classes, ranging from weak to strong. These constraints define how objects interact and, crucially, **who controls the lifecycle** of the objects.

1. **Dependency:** The weakest link. A uses B temporarily.
2. **Association:** A permanent link. A knows about B.
    1. **Aggregation:** "Has-A" (Shared/Weak). A has B, but B can exist without A.
    2. **Composition:** "Whole-Part" (Exclusive/Strong). A owns B; if A dies, B dies.

### 2. Why it is required?

Defining the correct relationship is essential for **memory management**, **flexibility**, and **modeling accuracy**.

- If you use *Composition* when *Aggregation* was needed, you create rigid code where objects cannot be shared.
- If you use *Association* when *Dependency* was sufficient, you pollute your class with unnecessary fields, keeping objects alive in memory longer than needed.

### 3. Details and key points and examples in the reference Book?

- **Dependency (The method argument):** A weaker variant of association. Usually implies an object accepts another as a method parameter or instantiates it locally.
    - *Example:* `Professor` uses `Salary` . The professor needs the salary to calculate tax, but doesn't "own" the salary object permanently.
- **Association (The link):** One object uses or interacts with another. The link is "always there" (a field).
    - *Example:* `Professor` communicates with `Student` .
- **Aggregation (The Shared Component):** A "whole-part" relationship where the component **can exist** without the container.
    - *Example:* `Department` contains `Professors` . If the Department closes, the Professors (hopefully) still exist and move elsewhere.
- **Composition (The Exclusive Component):** A "whole-part" relationship where the component **cannot exist** without the container.
    - *Example:* `University` consists of `Departments` . A "Department of Physics" belongs strictly to that University. If the University closes, the Department ceases to exist.

### 2. When to Use vs. When to Avoid?

- **Use Dependency:** When an object only needs another object for a specific operation (Method Parameter).
- **Use Association:** When an object needs to maintain a reference to another object to call methods on it repeatedly (Field).
- **Use Aggregation:** When creating a collection of child objects that might belong to multiple parents or must survive the parent (passed via Constructor).
- **Use Composition:** When the child object is strictly internal to the parent and shouldn't be accessed or exist independently (instantiated *inside* the parent).

### 3. Step By Step Detailed Rules to Map the concept to C# code

1. **Dependency:** Do **not** create a field. Pass the object as a parameter to a method or create `new` inside the method (Scope: Method).
2. **Association:** Create a `field` to hold the reference.
3. **Aggregation:** Create a `field`. The value **MUST** be passed in from outside (e.g., via Constructor `public Class(Child c)`). The parent does *not* create the child.
4. **Composition:** Create a `field`. The value **MUST** be instantiated **inside** the parent (e.g., `this.child = new Child()` in the constructor). The parent manages the death of the child.

### 4. C# Code Example which is not in the correct state

This code mixes up the lifecycles. It claims to be a "University", but it takes Departments from outside (Aggregation style) while calculating Salary as a permanent field (Association style) instead of a dependency.

```csharp
// BAD CODE: Semantic mismatch of relationships.

public class Salary { }
public class Department { }

public class University
{
    // Bad: Salary is a fleeting calculation,
    // storing it as a permanent state implies the University "is linked to" a specific Salary packet forever.
    public Salary _salary;

    // Bad: University usually OWNS departments (Composition).
    // Taking it from outside implies shared ownership (Aggregation).
    public Department _dept;

    public University(Salary s, Department d)
    {
        _salary = s;
        _dept = d;
    }
}

```

### 5. Applying the rules to make it correct

We restructure the class to strictly reflect the UML definitions from the book.

```csharp
using System.Collections.Generic;

// 1. Dependency Classes
public class Salary
{
    public decimal Amount { get; set; }
}

// 2. Aggregation Class (Exists independently)
public class Professor
{
    public string Name { get; set; }
}

// 3. Composition Class (Owned by University)
public class Department
{
    public string Name { get; set; }
}

public class University
{
    // COMPOSITION: University OWNS the Departments.
    // The Departments are created inside. If University dies, these lists die.
    private List<Department> _departments = new List<Department>();

    // AGGREGATION: University has Professors, but doesn't own their lives.
    // They are passed in from outside (e.g., a hiring pool).
    private List<Professor> _professors = new List<Professor>();

    public University()
    {
        // Composition: We create the part strictly within the whole.
        _departments.Add(new Department { Name = "Physics" });
    }

    public void HireProfessor(Professor p)
    {
        // Aggregation: We just hold a reference to an outsider.
        _professors.Add(p);
    }

    // DEPENDENCY: We use Salary temporarily.
    // It is passed in, used, and discarded after the method returns.
    public void ProcessPayroll(Salary currentRates)
    {
        foreach(var p in _professors)
        {
            // Using the dependency
            System.Console.WriteLine($"Paying {p.Name}: {currentRates.Amount}");
        }
    }
}

```