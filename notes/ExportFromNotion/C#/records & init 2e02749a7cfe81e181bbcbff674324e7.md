# records & init

Of course. **Records** are one of the most significant and useful features added to C# in recent versions (introduced in C# 9 and enhanced in C# 10). They provide a concise, powerful way to create **immutable** data-centric types.

Here is a comprehensive guide to mastering records in C#, from the basics to the expert-level details.

---

### **1. The Problem: The "Boilerplate" of Simple Data Classes**

Before records, if you wanted to create a simple `Person` class to hold data, you had to write a lot of repetitive code to get correct behavior for things like equality, hashing, and string representation.

**The "Old" Way (A Standard Class):**

```csharp
public class Person
{
    public string FirstName { get; init; }
    public string LastName { get; init; }

    // Constructor
    public Person(string firstName, string lastName)
    {
        FirstName = firstName;
        LastName = lastName;
    }

    // To compare two people, you'd have to override Equals... (boilerplate)
    public override bool Equals(object obj)
    {
        if (obj is Person other)
        {
            return FirstName == other.FirstName && LastName == other.LastName;
        }
        return false;
    }

    // And if you override Equals, you MUST override GetHashCode... (more boilerplate)
    public override int GetHashCode()
    {
        return HashCode.Combine(FirstName, LastName);
    }

    // And to print it nicely, you have to override ToString... (even more boilerplate)
    public override string ToString()
    {
        return $"Person {{ FirstName = {FirstName}, LastName = {LastName} }}";
    }

    // Plus operator overloads for == and !=, and IEquatable<T> implementation...
}

```

This is a huge amount of code just for a simple data container.

---

### **2. The Solution: Records (The "New" Way)**

A `record` is a special kind of `class` (or `struct`) where the compiler automatically generates all of that boilerplate for you.

### **Positional Records (The Most Common Form)**

This is the most concise syntax, introduced in C# 9.

```csharp
public record Person(string FirstName, string LastName);

```

**That single line of code is (mostly) equivalent to all the boilerplate from the "Old Way" above!**

Here's what the compiler generates for you behind the scenes:

1. **A primary constructor** (`Person(string firstName, string lastName)`).
2. **Public `init`only properties** (`FirstName` and `LastName`). `init` means you can only set the value during object creation, making the object **immutable**.
3. **Value-based `Equals()` and `GetHashCode()`**: Two records are considered equal if all their property values are equal.
4. **Value-based `ToString()`**: A clean, readable string representation (e.g., `Person { FirstName = John, LastName = Doe }`).
5. Overloads for `==` and `!=` operators.
6. An implementation of `IEquatable<T>`.
7. A "deconstructor" (more on that later).

**Usage:**

```csharp
var person1 = new Person("John", "Doe");
var person2 = new Person("John", "Doe");
var person3 = new Person("Jane", "Doe");

// 1. Immutability
// person1.FirstName = "Jim"; // <-- COMPILE ERROR! Properties are init-only.

// 2. Value-Based Equality
Console.WriteLine(person1 == person2); // True
Console.WriteLine(person1.Equals(person2)); // True
Console.WriteLine(person1 == person3); // False

// 3. Clean ToString()
Console.WriteLine(person1); // Output: Person { FirstName = John, LastName = Doe }

```

---

### **3. Key Features and Syntax Variations**

### **Standard Property Syntax (for more control)**

You don't have to use the positional syntax. You can declare a record with a more traditional class-like syntax if you need a parameterless constructor or more complex logic. The value-based equality is still automatically generated.

```csharp
public record Car
{
    public string Make { get; set; }
    public string Model { get; set; }
    public int Year { get; init; }

    // You can add methods
    public string GetFullName() => $"{Year} {Make} {Model}";
}

```

### **Nondestructive Mutation (The `with` Expression)**

Because records are immutable, how do you create a copy with a small change? You use the `with` keyword. This creates a **new** record by copying the values from the old one and applying the specified changes.

```csharp
var person1 = new Person("John", "Doe");

// Create a new person based on person1, but with a different last name.
var person2 = person1 with { LastName = "Smith" };

Console.WriteLine(person1); // Output: Person { FirstName = John, LastName = Doe }
Console.WriteLine(person2); // Output: Person { FirstName = John, LastName = Smith }

// person1 was NOT modified. person2 is a completely new object.

```

### **Inheritance**

Records can inherit from other records. This allows you to create hierarchies of immutable data types.

```csharp
public record Person(string FirstName, string LastName);

// An Employee IS a Person, but with an additional property.
public record Employee(string FirstName, string LastName, int EmployeeId) : Person(FirstName, LastName);

var emp = new Employee("Jane", "Doe", 123);
Console.WriteLine(emp); // Output: Employee { FirstName = Jane, LastName = Doe, EmployeeId = 123 }

```

### **Deconstruction**

Records automatically generate a `Deconstruct` method, which allows you to easily extract their properties into separate variables.

```csharp
var person = new Person("John", "Doe");

// Deconstruct the person object into two string variables.
var (first, last) = person;

Console.WriteLine($"First name: {first}, Last name: {last}");

```

---

### **4. Record Structs (C# 10)**

In C# 10, you can also declare a `record struct`.

**Syntax:**

```csharp
public readonly record struct Point(int X, int Y);

```

- A `record class` is a **reference type** (stored on the heap).
- A `record struct` is a **value type** (stored on the stack or inline).

**When to use a `record struct`?**
Use it for small, simple data structures where you want to avoid heap allocation for performance reasons. A `Point`, an `RgbColor`, or a `Money` struct are great candidates. For larger, more complex objects, stick with `record class`. Adding `readonly` ensures the struct is also immutable.

---

### **5. When Should You Use Records?**

**Records are the perfect choice for:**

1. **Data Transfer Objects (DTOs):** Their primary purpose is to carry data between layers of your application or over a network. Immutability makes them predictable and safe.
2. **API Models:** For request and response models in an [ASP.NET](http://asp.net/) Core Web API.
3. **State in Functional-Style Programming:** When you want to work with immutable state, the `with` expression is a core part of that workflow.
4. **Dictionary Keys:** Because their `GetHashCode` is correctly implemented based on their values, they make excellent, reliable keys in a `Dictionary`.

**When should you NOT use a record?**

- **When you need mutable state:** If you are modeling something that has a distinct identity and whose state is meant to change over time (like an Entity Framework Core entity that needs to be updated), a standard `class` is often more appropriate. For example, `person.Age++` is a natural mutation that doesn't fit the "create a new copy" model of records.
- **When you need reference equality:** If you need to know if two variables point to the exact same object in memory, a standard class's default `Equals` behavior is what you want.

# init

Of course. The `init` keyword is a small but powerful feature that is central to the concept of **immutability** in modern C#. It's the "secret sauce" that makes records and other immutable types work so cleanly.

---

### **1. The Problem: The "All or Nothing" Constructor**

Before C# 9, if you wanted to make a class's properties immutable, you had two main options:

**Option A: Private Setter with Constructor**

```csharp
public class Person
{
    public string FirstName { get; private set; }
    public string LastName { get; private set; }

    public Person(string firstName, string lastName)
    {
        FirstName = firstName;
        LastName = lastName;
    }
}

```

- **The Problem:** What if you have 10 properties? The constructor becomes huge (`new Person("John", "Doe", 30, "USA", ..., ...)`). What if some are optional? You need multiple constructor overloads. It gets messy.

**Option B: No Setter (Readonly Field)**
This is even more restrictive and suffers from the same constructor problem.

---

### **2. The Solution: `init` Accessor (The "Set-Once" Property)**

The `init` keyword creates an **`init`-only property accessor**. It's a special kind of setter that can **only be called during object initialization**.

**"Object Initialization" means:**

1. In the constructor.
2. In an **object initializer** (the `{...}` syntax right after `new()`).

Once the object has been fully constructed, `init`-only properties become effectively `readonly`.

**The Syntax:**
You replace `set;` with `init;`.

```csharp
public class Person
{
    public string FirstName { get; init; }
    public string LastName { get; init; }
}

```

### **How it Solves the Problem: The Flexibility of Object Initializers**

Now you can create an immutable `Person` object using the clean object initializer syntax, which is much more readable for classes with many properties.

```csharp
// You can use the flexible object initializer syntax.
var person = new Person
{
    FirstName = "John", // This is allowed because we are in the initializer.
    LastName = "Doe"    // This is also allowed.
};

// ... a few lines later ...

// NOW the object is fully constructed. Trying to set the property will fail.
// person.FirstName = "Jane"; // <-- COMPILE ERROR!
// Error: Init-only property or indexer 'Person.FirstName' can only be assigned in an object initializer...

```

This gives you the best of both worlds:

- **Immutability:** The object cannot be changed after it's created.
- **Flexibility:** You don't need a massive constructor. You can set the properties you need in a readable way during creation.

---

### **3. How `init` and `record` Work Together**

When you use the concise **positional record** syntax, the compiler automatically generates `init`-only properties for you.

**The Record:**

```csharp
public record Person(string FirstName, string LastName);

```

**What the Compiler Generates (Simplified):**

```csharp
public class Person
{
    public string FirstName { get; init; } // <-- Automatically init-only
    public string LastName { get; init; }  // <-- Automatically init-GPT

    public Person(string firstName, string lastName)
    {
        FirstName = firstName;
        LastName = lastName;
    }
    // ... plus all the other record goodies (Equals, ToString, etc.) ...
}

```

This is why you can't change the properties of a positional record after it has been created.

---

### **4. `init` and the `with` Expression**

The `with` expression is syntactic sugar that works perfectly with `init`-only properties.

When you write this:

```csharp
var person1 = new Person("John", "Doe");
var person2 = person1 with { LastName = "Smith" };

```

The compiler is effectively doing this behind the scenes:

1. Creates a **new** `Person` object.
2. Copies the `FirstName` from `person1` into the initializer of the new object.
3. Sets the `LastName` to the new value ("Smith") in the initializer.
4. Returns the fully constructed new object.

Because this all happens during the object initialization phase of `person2`, the `init`-only properties can be set.

---

### **5. Summary: `set` vs. `init` vs. `readonly`**

| Accessor | Can be set in Constructor? | Can be set in Object Initializer? | Can be changed AFTER construction? | Mutability |
| --- | --- | --- | --- | --- |
| `set;` | Yes | Yes | **Yes** | **Mutable** |
| `init;` | Yes | **Yes** | **No** | **Immutable** |
| (none, on `readonly` field) | **Yes** | **No** | **No** | **Immutable** |

**The Expert Takeaway:**
Use `init` whenever you are creating a **data-centric class or struct (like a DTO)** and you want to ensure that its state cannot be accidentally changed after it's been created. It is the modern C# way of expressing immutability with a clean and flexible initialization syntax.