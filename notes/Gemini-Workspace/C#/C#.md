Got it. Let's scrap the massive curriculum. You are prepping for a Senior/Lead interview and you need to move *fast*. 

We will go through Chapter 3 ("Creating Types in C#") sequentially, concept by concept. For each block, I will give you the **precise, most important lines**, **interview gold**, and **commented code examples**.

When you are done reading a block, just reply **NEXT** and we will instantly move to the next page/topic.

Let's begin right at the start of Chapter 3.

***

### 1. Classes: Fields and Constants

**The Core Concept:**
A class is the most common reference type. It contains data members (fields) and function members (methods, properties, etc.).

**Key Important Lines:**
*   **`readonly` fields:** Can *only* be assigned in their declaration or within the enclosing type's constructor. This prevents modification after construction.
*   **Field initialization order:** Field initializers run *before* constructors.
*   **`const` (Constants):** Evaluated statically at **compile time**. The compiler literally substitutes its value wherever used (like a C++ macro).

🔥 **Senior Interview Gold: `const` vs `static readonly`**
If Assembly A exposes a `const` field, and Assembly B uses it, the value is baked into Assembly B at compile time. If Assembly A later updates the value, Assembly B will *still have the old value* until B is recompiled. 
**Fix:** Use `static readonly` for any value that might change in a future version, because it is evaluated at *runtime*.

**Code Example:**
```csharp
public class Octopus 
{
    // 1. Field: private by default
    string name; 
    
    // 2. Readonly Field: Can only be set here or in the constructor
    public readonly int Legs = 8; 
    
    // 3. Constant: Baked in at compile-time. Only primitive types/strings/enums allowed.
    public const string Species = "Cephalopod"; 
    
    // 4. Static Readonly: Evaluated at runtime. Safe for cross-assembly versioning.
    public static readonly DateTime StartupTime = DateTime.Now; 
}
```

---

### 2. Classes: Methods

**The Core Concept:**
Methods perform actions. A method's signature comprises its name and parameter types in order (but **not** the return type, nor the `params` modifier).

**Key Important Lines:**
*   **Expression-bodied methods:** Methods comprising a single expression can use the fat-arrow `=>` syntax.
*   **Local methods:** You can define a method *inside* another method. It is only visible to the enclosing method.
*   **Static local methods (C# 8):** Adding `static` to a local method prevents it from "capturing" local variables of the enclosing method.

🔥 **Senior Interview Gold: Variable Capturing in Local Methods**
Interviewers love asking about local methods vs lambda expressions. Both can "capture" outer variables, which forces the compiler to generate a hidden class and allocate memory on the heap. By marking a local method as `static`, you guarantee it won't capture state, preventing hidden memory allocations (great for micro-optimizations).

**Code Example:**
```csharp
public class Calculator
{
    // Expression-bodied method
    public int Multiply(int x, int y) => x * y;

    public void WriteCubes()
    {
        int captureMe = 5; // Local variable

        Console.WriteLine(Cube(3));

        // Local Method (can access 'captureMe' if it wasn't marked static)
        // Marked 'static' prevents accidental memory allocation via closures
        static int Cube(int value) => value * value * value; 
    }
}
```

***

**Are you ready?** 
Reply **NEXT** to move to the next page: **Instance Constructors, Deconstructors, and Object Initializers**. 
*(Or ask a question if you want to clarify anything here!)*

### 3. Instance Constructors

**The Core Concept:**
Constructors run initialization code when an object is created. They have no return type and share the name of the class.

**Key Important Lines:**
*   **Implicit parameterless constructor:** The C# compiler generates a parameterless constructor automatically *if and only if* you do not define any constructors yourself. 
*   **Constructor overloading:** One constructor can call another using the `this` keyword to avoid code duplication. The called constructor executes *first*.
*   **Execution Order:** Field initializers run *before* the constructor is executed.
*   **Nonpublic constructors:** You can make constructors `private` or `internal`.

🔥 **Senior Interview Gold: Why use a Private Constructor?**
Interviewers ask this to test design pattern knowledge. A private constructor is typically used to control instantiation. Use cases include:
1.  **Singleton Pattern:** Prevent outside classes from using `new`.
2.  **Factory Methods:** Force creation through a static method (e.g., pulling from a pool or returning cached instances).
3.  **Static Classes:** (Though C# has `static class`, historically private constructors prevented instantiation).

**Code Example:**
```csharp
public class Wine
{
    public decimal Price;
    public int Year;

    // 1. Expression-bodied constructor
    public Wine(decimal price) => Price = price;

    // 2. Constructor chaining: The 'this(price)' runs FIRST.
    public Wine(decimal price, int year) : this(price) 
    {
        Year = year;
    }
}
```

---

### 4. Deconstructors

**The Core Concept:**
The opposite of a constructor: it takes an object and assigns its fields back to a set of variables.

**Key Important Lines:**
*   The method must be named `Deconstruct` and have one or more `out` parameters.
*   **Discards:** You can use the underscore `_` symbol if you are uninterested in one or more variables during deconstruction.

🔥 **Senior Interview Gold: Extension Deconstructors**
You don't need to own the class to deconstruct it! The `Deconstruct` method can be an **Extension Method**. This is a brilliant trick if you want to deconstruct types from a 3rd party library or the .NET BCL.

**Code Example:**
```csharp
class Rectangle
{
    public float Width, Height;

    // Must be called 'Deconstruct' with 'out' parameters
    public void Deconstruct(out float width, out float height)
    {
        width = Width;
        height = Height;
    }
}

// Usage:
var rect = new Rectangle { Width = 3, Height = 4 };

// Deconstruction into new local variables
var (w, h) = rect; 

// Using a discard '_' if we only care about width
var (onlyWidth, _) = rect; 
```

---

### 5. Object Initializers & The `this` Reference

**The Core Concept:**
Object initializers let you set accessible fields or properties directly after calling `new`, without needing a massive constructor with optional parameters.

**Key Important Lines:**
*   **Under the hood:** The compiler creates a *temporary variable* to hold the object, applies the properties to it, and *then* assigns it to your final variable. 
*   **The `this` reference:** Refers to the instance itself. It's valid only within nonstatic members.

🔥 **Senior Interview Gold: Why does the compiler use a temporary variable?**
To prevent you from ending up with a "half-initialized" object. If an exception is thrown while evaluating one of the properties in the object initializer, the assignment to your variable never happens.

**Code Example:**
```csharp
// The C# code you write:
Bunny b = new Bunny { Name = "Bo", LikesCarrots = true };

// What the compiler actually generates behind the scenes:
Bunny temp = new Bunny();
temp.Name = "Bo";
temp.LikesCarrots = true;
Bunny b = temp; // Assignment happens LAST, ensuring safety
```

***

**Ready for the next chunk?** 
Reply **NEXT** to cover **Properties, Init-Only Setters (C# 9), and Primary Constructors (C# 12)**.


### 6. Properties & Encapsulation

**The Core Concept:**
Properties look like fields from the outside but contain logic like methods on the inside. They give you complete control over getting and setting values, enabling encapsulation.

**Key Important Lines:**
*   **Automatic properties:** Instruct the compiler to generate a hidden private backing field automatically (e.g., `public decimal Price { get; set; }`).
*   **Property initializers:** You can assign a default value to an auto-property (e.g., `{ get; set; } = 123;`).
*   **Different access levels:** You can restrict a setter to be `private` or `protected` while keeping the getter `public`.
*   **Expression-bodied properties:** Use `=>` for read-only properties or for concise getters/setters.

🔥 **Senior Interview Gold: How the CLR sees Properties**
Under the hood, the CLR does not "understand" properties the way C# does. The C# compiler translates properties into two methods: `get_PropertyName()` and `set_PropertyName(value)`. 
*Performance note:* Non-virtual property accessors are typically **inlined** by the Just-In-Time (JIT) compiler, meaning there is absolutely zero performance difference between accessing a property and accessing a raw field.

**Code Example:**
```csharp
public class Stock
{
    // 1. Automatic property with an initializer
    public decimal CurrentPrice { get; set; } = 123;

    // 2. Different accessibility (Public read, Private write)
    public decimal MaxPrice { get; private set; }

    // 3. Expression-bodied read-only property (computed)
    decimal sharesOwned = 100;
    public decimal Worth => CurrentPrice * sharesOwned; 
}
```

---

### 7. Init-Only Setters (C# 9)

**The Core Concept:**
`init` accessors act like `set` accessors, but they can **only** be executed during object initialization (via an object initializer or a constructor). After that, the property becomes read-only.

**Key Important Lines:**
*   You declare them using `init` instead of `set`.
*   They are permitted to modify `readonly` fields within their own class.
*   They are the foundation for nondestructive mutation in Records (using the `with` keyword, which we'll cover soon).

🔥 **Senior Interview Gold: `init` Properties vs. Constructor Parameters**
Why use `init` properties instead of just passing everything into a constructor to ensure immutability? **Binary Compatibility.**
If you publish a library and later add an optional parameter to a constructor, you *break binary compatibility* for existing consumers (because the parameter count changes in the IL). However, adding a new `init`-only property is 100% safe and doesn't break existing compiled code.

**Code Example:**
```csharp
public class Note
{
    // Can only be set via object initializer or constructor
    public int Pitch { get; init; } = 20; 
    public int Duration { get; init; } = 100;
}

// Usage:
var note = new Note { Pitch = 50 };
// note.Pitch = 200; // ERROR: Cannot assign after initialization
```

---

### 8. Primary Constructors (C# 12)

**The Core Concept:**
You can place a parameter list directly after a class (or struct) name. The compiler uses these parameters to generate a primary constructor.

**Key Important Lines:**
*   Displaces the default parameterless constructor.
*   If you write any other explicit constructors in the class, they **must** invoke the primary constructor using `: this(...)`.
*   The parameters are magically available in scope for field/property initializers and method bodies throughout the class.

🔥 **Senior Interview Gold: Classes vs. Records Primary Constructors**
Interviewers will try to trick you here. 
If you use a primary constructor on a **Record** (C# 9), the compiler automatically generates `public init` properties for every parameter. 
If you use a primary constructor on a standard **Class or Struct** (C# 12), the compiler does *not* generate public properties. The parameters are simply captured as hidden private fields (if used in methods) or consumed during initialization. You must explicitly declare properties if you want to expose them.

**Code Example:**
```csharp
// C# 12 Primary Constructor
class Person(string firstName, string lastName) 
{
    // The parameters are visible here to initialize properties
    public string FirstName { get; } = firstName;
    
    // The parameters are also visible inside methods!
    // (Compiler creates hidden backing fields to store them)
    public void Print() => Console.WriteLine(firstName + " " + lastName);

    // Any other constructor MUST call the primary one
    public Person(string firstName) : this(firstName, "Unknown") { }
}

var p = new Person("Alice", "Jones");
p.Print(); // Outputs: Alice Jones
```

***

**Ready to keep moving?** 
Reply **NEXT** to dive into **Indexers, Static Classes, and Partial Types**.

### 9. Indexers

**The Core Concept:**
Indexers provide a natural syntax for accessing elements in a class or struct that encapsulate a list or dictionary, allowing you to access them using square brackets like an array (`obj[index]`).

**Key Important Lines:**
*   You declare an indexer by defining a property named `this` with arguments in square brackets.
*   Types can declare *multiple* indexers (overloading) with different parameter types (e.g., an `int` indexer and a `string` key indexer).
*   **Indices and Ranges (C# 8):** You can natively support the `^` (from end) and `..` (range) operators by defining indexers that accept `System.Index` or `System.Range`.

🔥 **Senior Interview Gold: CLR Representation**
How does the CLR handle indexers? It compiles them into methods named `get_Item` and `set_Item`. If you are writing interop code or examining IL, you won't see an "indexer", you will see these methods. 
*Bonus:* You can call null-conditional indexers like this: `string word = sentence?[0];`

**Code Example:**
```csharp
class Sentence
{
    string[] words = "The quick brown fox".Split();

    // Standard Indexer
    public string this[int wordNum] 
    {
        get => words[wordNum];
        set => words[wordNum] = value;
    }

    // C# 8+ Indices and Ranges support
    public string this[Index index] => words[index];
    public string[] this[Range range] => words[range];
}

// Usage:
var s = new Sentence();
Console.WriteLine(s[^1]);    // Outputs: fox (using Index)
var subset = s[1..3];        // Outputs: quick, brown (using Range)
```

---

### 10. Static Classes & Static Constructors

**The Core Concept:**
A class marked `static` cannot be instantiated or subclassed, and must be composed solely of static members. A static constructor executes exactly *once* per type, prior to the type being used.

**Key Important Lines:**
*   **Triggers:** The runtime invokes a static constructor just before either: (a) instantiating the type, or (b) accessing a static member of the type.
*   **Initialization Order:** Static field initializers run *just before* the static constructor is called, in the order they are declared.
*   You cannot add access modifiers (like `public`) or parameters to a static constructor.

🔥 **Senior Interview Gold: The "Poisoned" Type**
What happens if a static constructor throws an unhandled exception? 
The CLR throws a `TypeInitializationException`. Because static constructors only run *once*, if it fails, the CLR will not try again. That type becomes **permanently unusable** for the entire lifetime of the application process. This is a critical failure point in high-uptime services.

**Code Example:**
```csharp
static class DatabaseConfig 
{
    // Runs 1st
    public static readonly string ConnectionString = "Server=..."; 

    // Runs 2nd (Static Constructor)
    static DatabaseConfig() 
    {
        Console.WriteLine("Type Initialized");
        // If this throws, DatabaseConfig is dead for the rest of the app's life.
    }
}
```

---

### 11. Partial Types & Methods

**The Core Concept:**
`partial` types allow a class, struct, or interface definition to be split across multiple files. It is heavily used to separate auto-generated code from hand-authored code.

**Key Important Lines:**
*   **Standard Partial Methods:** Must return `void`, are implicitly `private`, and cannot have `out` parameters. If you define a hook but never implement it, the compiler completely erases the definition and all calls to it (zero performance cost).
*   **Extended Partial Methods (C# 9):** If a partial method starts with an access modifier (e.g., `public`), it becomes an *extended* partial method.

🔥 **Senior Interview Gold: Why did C# 9 add "Extended" Partial Methods?**
**Source Generators.** Roslyn Source Generators write code during compilation. Standard partial methods were too restrictive for this because they couldn't return values or have `out` params. By adding an access modifier, the method *must* be implemented (it won't melt away), allowing developers to define complex method signatures that the Source Generator guarantees it will implement behind the scenes.

**Code Example:**
```csharp
// File 1: Hand-authored by developer
public partial class PaymentForm 
{
    // Standard partial method (melts away if unimplemented)
    partial void ValidatePayment(decimal amount);

    // Extended partial method (C# 9+) - MUST be implemented somewhere
    public partial bool TryParse(string input, out int result);
}

// File 2: Auto-generated by a tool/Source Generator
public partial class PaymentForm 
{
    // The implementation
    public partial bool TryParse(string input, out int result) 
    {
        return int.TryParse(input, out result);
    }
}
```

***

**Making good time!** 
Reply **NEXT** to move into the heart of OOP: **Inheritance, Polymorphism, Casting, and Virtual/Hidden Methods**.

Got it, I will remove those icons so the Read Aloud feature works perfectly for you. 

Here is the next core section covering Inheritance and Polymorphism.

***

### 12. Inheritance & Polymorphism

**The Core Concept:**
A class can inherit from another class to extend or customize it. The subclass gets everything the base class has, plus its own new members. Polymorphism means a variable of a base type can refer to an object of a derived type.

**Key Important Lines:**
*   A class can inherit from only a **single** base class.
*   Polymorphism works because subclasses have all the features of their base class. The reverse is not true.

**[Senior Interview Focus]: The limitation of single inheritance**
Interviewers might ask how C# handles the limitation of single class inheritance. The answer is through Interfaces (which allow multiple inheritance of behavior) and, since C# 8, Default Interface Members, which allow traits to be mixed in without multiple class inheritance.

---

### 13. Casting and the 'as' / 'is' Operators

**The Core Concept:**
Because of polymorphism, you often need to cast object references up and down the inheritance chain.

**Key Important Lines:**
*   **Upcasting:** Creates a base class reference from a subclass reference. It is implicit and always succeeds.
*   **Downcasting:** Creates a subclass reference from a base class reference. Requires an explicit cast because it can fail at runtime (throws `InvalidCastException`).
*   **The `as` operator:** Performs a downcast that evaluates to `null` if it fails, rather than throwing an exception.
*   **The `is` operator:** Tests whether a reference conversion would succeed. In modern C#, it also lets you introduce a pattern variable on the fly.

**[Senior Interview Focus]: 'as' vs 'is' pattern matching**
Historically, developers used the `as` operator followed by a null check. Today, the `is` operator with pattern matching is the industry standard because it tests and casts in a single, safe operation, preventing accidental `NullReferenceExceptions`. Also note that the `as` operator cannot perform custom or numeric conversions, only reference and nullable conversions.

**Code Example:**
```csharp
Asset a = new Stock { Shares = 100 }; // Upcast (implicit)

// The old way (using 'as')
Stock s = a as Stock;
if (s != null) {
    Console.WriteLine(s.Shares);
}

// The modern standard (using 'is' with a pattern variable)
if (a is Stock myStock) {
    Console.WriteLine(myStock.Shares);
}
```

---

### 14. Virtual Methods, Overriding, and Hiding

**The Core Concept:**
A method marked as `virtual` provides a default implementation that subclasses can change using the `override` keyword. 

**Key Important Lines:**
*   **Covariant return types (C# 9):** You can override a method and have it return a *more derived* (subclassed) type than the base method specified.
*   **Hiding (`new` modifier):** If a base class and subclass have identical members without the `override` keyword, the subclass "hides" the base member. You use the `new` modifier to suppress the compiler warning.

**[Senior Interview Focus]: 'override' vs 'new' (Method Hiding)**
This is a guaranteed interview question. 
If you use `override`, the method is resolved at **runtime** based on the actual object type (Late Binding). 
If you use `new`, the method is resolved at **compile-time** based on the variable's reference type (Early Binding).

**Code Example:**
```csharp
class BaseClass { 
    public virtual void Foo() => Console.WriteLine("Base"); 
}

class Overrider : BaseClass { 
    public override void Foo() => Console.WriteLine("Overrider"); 
}

class Hider : BaseClass { 
    public new void Foo() => Console.WriteLine("Hider"); 
}

// Interview Test:
Overrider over = new Overrider();
BaseClass b1 = over;
b1.Foo(); // Outputs "Overrider" (resolved at runtime)

Hider h = new Hider();
BaseClass b2 = h;
b2.Foo(); // Outputs "Base" (resolved at compile-time based on b2's type)
```

---

### 15. Abstract and Sealed Classes

**The Core Concept:**
These keywords enforce strict rules on your class hierarchy. `abstract` forces inheritance; `sealed` prevents it.

**Key Important Lines:**
*   **Abstract Classes:** Cannot be instantiated. Only their concrete subclasses can be instantiated.
*   **Abstract Members:** Like virtual members, but they provide *no default implementation*. The subclass is forced to provide the implementation.
*   **Sealed Classes:** Cannot be subclassed.
*   **Sealed Members:** You can seal an overridden method (`public sealed override void Foo()`) to prevent further subclasses from overriding it again.

**[Senior Interview Focus]: Why seal a class?**
Beyond just "preventing inheritance," sealing a class has a performance benefit. The Just-In-Time (JIT) compiler can make devirtualization optimizations. When calling a method on a sealed class, the JIT knows no subclasses exist, so it can resolve method calls at compile-time instead of doing virtual table lookups at runtime, potentially inlining the method entirely.

***

**Are you ready for the next section?**
Reply **NEXT** to cover **Base Constructors, The Object Type, Boxing, and Structs**.

### 16. Constructors and Inheritance

**The Core Concept:**
A subclass must declare its own constructors. It does not automatically inherit the base class's constructors, but it must call them to ensure the base class is properly initialized.

**Key Important Lines:**
*   **The base Keyword:** Used to call a base-class constructor from a subclass constructor.
*   **Implicit Calling:** If you omit the `base` keyword, the compiler implicitly calls the parameterless constructor of the base class.
*   **Required Members (C# 11):** Adding the `required` modifier to a field or property forces the caller to set it via an object initializer. You can bypass this restriction on a specific constructor by adding the `[SetsRequiredMembers]` attribute.

**[Senior Interview Focus]: Initialization Order**
Interviewers love asking about the exact order of execution when you instantiate a subclass. The order is:
1. Subclass fields are initialized.
2. Base class fields are initialized.
3. Base class constructor executes.
4. Subclass constructor executes.

**Code Example:**
```csharp
public class BaseClass
{
    public int X = 1; // Executes 2nd
    public BaseClass(int x) { ... } // Executes 3rd
}

public class SubClass : BaseClass
{
    int y = 1; // Executes 1st
    
    // Explicitly calling the base constructor
    public SubClass(int x) : base(x) 
    {
        ... // Executes 4th
    }
}
```

---

### 17. The object Type, Boxing, and Unboxing

**The Core Concept:**
`object` (System.Object) is the ultimate base class for all types. Any type can be upcast to `object`.

**Key Important Lines:**
*   **Boxing:** Converting a value type (like `int`) to a reference type (`object` or an interface). This copies the value-type instance into a new object allocated on the managed heap.
*   **Unboxing:** Reversing the operation by casting the `object` back to the original value type. It requires an explicit cast.
*   Unboxing requires an exact type match. You cannot unbox an `int` that was boxed as an `object` directly into a `long` (it will throw an `InvalidCastException`).

**[Senior Interview Focus]: The Performance Cost of Boxing**
Why do we care about boxing? Because allocating objects on the heap triggers garbage collection tracking, and creating the object takes CPU cycles. Before Generics were introduced in C# 2.0, collections like `ArrayList` used `object`, causing massive performance penalties when storing integers or structs. Generics (`List<int>`) solved this by avoiding boxing entirely.

**Code Example:**
```csharp
int x = 9;
object obj = x;           // BOXING: Allocates memory on the heap
int y = (int)obj;         // UNBOXING: Copies value back to stack

// Invalid unboxing example:
object obj2 = 9;          // Boxed as an int
long z = (long)obj2;      // Runtime Error: InvalidCastException

// Correct way to unbox then convert:
long z2 = (long)(int)obj2; 
```

---

### 18. Static vs Runtime Type Checking (GetType vs typeof)

**The Core Concept:**
C# checks types both at compile time (statically) and at runtime. 

**Key Important Lines:**
*   **typeof:** Evaluated statically at compile time. Used when you know the name of the type in your source code.
*   **GetType():** Evaluated at runtime on an instance of an object. 

**[Senior Interview Focus]: When to use which?**
Use `typeof` when you are doing reflection or passing type parameters and you know the type while writing the code. Use `GetType()` when you receive an `object` or a base class parameter and need to know the actual derived type of the instance sitting in memory at runtime.

---

### 19. Structs (Value Types)

**The Core Concept:**
A struct is similar to a class, but it is a Value Type, not a Reference Type. 

**Key Important Lines:**
*   Structs do not support inheritance (they implicitly derive from `System.ValueType`).
*   Variables of a struct type cannot be `null` (unless wrapped in `Nullable<T>` or `?`).
*   Assignment copies the entire value, not a reference.

**[Senior Interview Focus]: Array Memory Layout**
If you create an array of 1000 classes, you allocate 1 array object on the heap containing 1000 null references, and you must instantiate 1000 individual objects on the heap. If you create an array of 1000 structs, you allocate exactly 1 object on the heap, and all 1000 structs sit continuously inline inside that single memory block. This provides massive CPU Cache locality benefits for high-performance code.

---

### 20. Advanced Structs (readonly and ref)

**The Core Concept:**
Modern C# introduces modifiers to struct definitions to give the compiler strict rules about how the struct can be used, enabling extreme performance optimizations.

**Key Important Lines:**
*   **readonly struct:** Enforces that all fields must be `readonly`. This allows the compiler to avoid making defensive copies when passing the struct around.
*   **readonly methods (C# 8):** You can apply `readonly` to a specific method inside a mutable struct to guarantee that method won't modify any fields.
*   **ref struct (C# 7.2):** Ensures the struct can only ever exist on the stack. It can never be boxed, put in an array, or used as a field in a class.

**[Senior Interview Focus]: Why do ref structs exist?**
`ref struct` was created specifically to support `Span<T>` and `ReadOnlySpan<T>`. Because a span can wrap pointers to stack-allocated memory, it would be a catastrophic security vulnerability if a span somehow got boxed and moved to the heap, outliving the stack frame it points to. `ref struct` tells the compiler to strictly block any code that might cause it to move to the heap (like `async` methods or closures).

**Code Example:**
```csharp
// High-performance immutable struct
readonly struct Point
{
    public readonly int X, Y;
    public Point(int x, int y) => (X, Y) = (x, y);
}

// Stack-only struct
ref struct FastBuffer
{
    public Span<int> Data;
    // Cannot be used in async methods, cannot be boxed, cannot implement interfaces
}
```

***

**Are you ready for the next section?**
Reply **NEXT** to cover **Access Modifiers, Interfaces (including default and static abstract members), and Enums.**