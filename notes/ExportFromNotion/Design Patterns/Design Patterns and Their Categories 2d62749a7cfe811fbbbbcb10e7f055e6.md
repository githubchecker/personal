# Design Patterns and Their Categories

### 1. What is it?

A Design Pattern is a general, reusable, and proven solution to a commonly occurring problem within a given context in software design. It is not a finished piece of code or a library that can be plugged in. Instead, it is a **blueprint** or a **general concept** that describes how to structure classes and objects to solve a specific kind of problem.

The book makes an important distinction: an *algorithm* is like a cooking recipe with clear steps to reach a goal, while a *pattern* is more like a blueprint where you can see the final result and its features, but the exact order of implementation is up to you.

### 2. Why it is required?

According to the book, learning and using design patterns is essential for two primary reasons:

1. **Toolkit of Tried-and-Tested Solutions:** Design patterns provide a collection of well-tested solutions to common software design problems. Even if you never encounter the exact problem a pattern solves, studying them teaches you the principles of good object-oriented design and how to build flexible, maintainable, and reusable code.
2. **A Common Language for Developers:** Patterns establish a shared vocabulary. When you say, "Let's use a Facade here," everyone on the team immediately understands the proposed structure and intent without needing a lengthy explanation. This greatly improves the efficiency of communication.

### 3. Details and key points and examples in the reference Book

The book categorizes all design patterns by their **intent**, or purpose. There are three main groups:

- **Creational Patterns**
    - **Purpose:** These patterns provide various object creation mechanisms that increase flexibility and help reuse existing code. They deal with the process of object instantiation.
    - **Key Point:** The main goal is to separate the code that uses an object (the client) from the code that creates the object (the `new` keyword and its associated logic). This means the client code doesn't need to know the specific concrete class it is using.
    - **Patterns in this Category:** Factory Method, Abstract Factory, Builder, Prototype, Singleton.
- **Structural Patterns**
    - **Purpose:** These patterns explain how to assemble objects and classes into larger structures, while keeping those structures flexible and efficient.
    - **Key Point:** They focus on how objects and classes are composed and related to each other. They help ensure that if one part of the structure changes, the entire system doesn't need to change with it.
    - **Patterns in this Category:** Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy.
- **Behavioral Patterns**
    - **Purpose:** These patterns are concerned with algorithms and the assignment of responsibilities between objects.
    - **Key Point:** They focus on patterns of communication between objects. They describe how objects interact and distribute responsibilities to get a job done, making their collaboration more flexible and efficient.
    - **Patterns in this Category:** Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.

### 4. When to Use vs. When to Avoid? (How to Choose a Category)

You don't choose one category "over" another. Instead, you identify the **nature of your design problem**, which will point you to the correct category to look for a solution.

### Choose a Creational Pattern when your problem is about **Object Creation**.

- **Factory Method:** You need subclasses to decide which specific class to create.
    - **Use Case:** An application where `TextDocument` creates `TextPage` objects, and `SpreadsheetDocument` creates `Sheet` objects.
- **Abstract Factory:** You need to create families of related objects that must be used together.
    - **Use Case:** A UI toolkit where a `WindowsFactory` must create `WindowsButton` and `WindowsCheckbox` objects that match.
- **Builder:** You need to construct a complex object with many optional configurations step-by-step.
    - **Use Case:** Building a `Pizza` with a specific size, crust, and multiple optional toppings in a readable way.
- **Prototype:** You need to create a copy of an existing object without knowing its specific class.
    - **Use Case:** Duplicating a pre-configured `Shape` from a palette in a graphics editor.
- **Singleton:** You need to ensure a class has exactly one instance throughout the entire application.
    - **Use Case:** Managing a single, shared database connection pool for the entire application.

### Choose a Structural Pattern when your problem is about **Object Composition and Structure**.

- **Adapter:** You need to make two incompatible interfaces work together.
    - **Use Case:** Making a new analytics library that requires JSON work with your old system that only outputs XML.
- **Decorator:** You need to add extra responsibilities to an object dynamically at runtime.
    - **Use Case:** Wrapping a plain `FileStream` with a `CompressionStream` and then an `EncryptionStream`.
- **Facade:** You need to provide a simple, unified interface to a complex system.
    - **Use Case:** A single `VideoConverter` class that hides the dozen of complex classes in a video conversion library.
- **Composite:** You need to treat a group of objects in the same way as a single object.
    - **Use Case:** A graphics application where a "shape" can be a single circle or a complex group of many shapes.
- **Bridge:** You need to separate a large class or a set of closely related classes into two separate hierarchies—abstraction and implementation—so that they can be developed independently.
    - **Use Case:** Allowing `RemoteControl` hierarchies (e.g., Basic, Advanced) to work with any `Device` hierarchy (e.g., TV, Radio).
- **Flyweight:** You need to manage a huge number of objects efficiently by sharing common state.
    - **Use Case:** Rendering millions of `Tree` objects in a forest by sharing their common texture and color data.
- **Proxy:** You need to control or manage access to another object.
    - **Use Case:** A `DatabaseProxy` that handles lazy connections and caching for a resource-intensive database object.

### Choose a Behavioral Pattern when your problem is about **Object Communication and Responsibility**.

- **State:** An object's entire behavior needs to change when its internal state changes.
    - **Use Case:** A `Document` object behaving differently if its status is `Draft`, `InReview`, or `Published`.
- **Strategy:** You need an object to be able to switch between a family of interchangeable algorithms at runtime.
    - **Use Case:** A `Navigator` class that can switch its route-finding algorithm between `RoadStrategy` and `WalkingStrategy`.
- **Observer:** You need to notify multiple objects when the state of one object changes, without creating tight coupling.
    - **Use Case:** Notifying multiple chart and table UI elements when data in a spreadsheet is updated.
- **Command:** You need to turn a request or an operation into a standalone object.
    - **Use Case:** Implementing Undo/Redo by storing a history of `CopyCommand` and `PasteCommand` objects.
- **Mediator:** You have many objects that communicate in a chaotic "many-to-many" way, and you want to centralize that logic.
    - **Use Case:** A form where all UI controls (buttons, textboxes) notify the main `Dialog` object instead of talking to each other directly.
- **Chain of Responsibility:** You need to pass a request through a series of potential handlers until one can process it.
    - **Use Case:** Processing a web request through a chain of handlers for authentication, then validation, then caching.
- **Iterator:** You need a uniform way to loop through different collections (e.g., list, tree) without exposing their internal structure.
    - **Use Case:** Using `while (iterator.hasNext())` to traverse a collection, regardless of its underlying implementation.
- **Memento:** You need to save and restore the state of an object without revealing its implementation details.
    - **Use Case:** An `Editor` class creating a "snapshot" of its state before a `Command` runs, allowing for an undo operation.
- **Template Method:** You have an algorithm with a fixed set of steps, but you want subclasses to customize some of those steps.
    - **Use Case:** A data-parsing algorithm with a skeleton (`OpenFile -> ParseData -> CloseFile`) where subclasses only override the `ParseData` step.
- **Visitor:** You need to perform a new operation on a set of objects without changing the classes of those objects.
    - **Use Case:** Adding an `XMLExport` function to a group of `Shape` classes without modifying the `Shape` classes themselves.

---

### Most Used Structural Patterns

Structural patterns focus on how to assemble objects and classes into larger structures. These are the workhorses for keeping your application's architecture clean.

### 1. Facade Pattern

- **Why It's So Common:** Almost every application of significant size interacts with a complex external library, framework, or internal subsystem. The Facade pattern is the standard way to create a simplified, clean entry point to that subsystem, hiding its complexity from the rest of the application. It reduces coupling and makes the code easier to understand and maintain.
- **Common Use Case:** You need to integrate a powerful but complex video conversion library that has dozens of classes for codecs, file handling, and bitrates. Instead of having your application's business logic call all these classes directly, you create a single `VideoConverter` class with one simple method: `ConvertVideo(string sourceFile, string format)`. This class becomes the Facade that handles all the complex interactions with the library behind the scenes.
- **In Modern C#:** This pattern is seen everywhere in service classes. For example, you might create a single `IAwsS3Service` facade that simplifies interactions with the AWS SDK's multiple clients and request objects for uploading and downloading files.

### 2. Adapter Pattern

- **Why It's So Common:** Software is rarely built in a vacuum. Developers constantly need to integrate new components with old systems, third-party APIs, or legacy code. These different parts often have incompatible interfaces. The Adapter pattern acts as the "glue" that allows them to work together.
- **Common Use Case:** Your application works with an `IEmployee` interface. You need to integrate with a new third-party HR system, but its employee class is called `Person` and has different method names (e.g., `GetFullName()` instead of `GetName()`). You would create an `PersonToEmployeeAdapter` that wraps the `Person` object and implements your `IEmployee` interface, translating the method calls internally.
- **In Modern C#:** This pattern is implicitly used when mapping between objects, such as converting Data Transfer Objects (DTOs) from an API request into your internal domain models. Libraries like AutoMapper are essentially sophisticated adapter generators.

### 3. Decorator Pattern

- **Why It's So Common:** The Decorator pattern provides a flexible alternative to subclassing for extending functionality. It allows you to add new behaviors to objects dynamically at runtime by wrapping them in special "decorator" objects. This aligns perfectly with the Open/Closed Principle.
- **Common Use Case:** As shown in the book, you have a basic `FileDataSource` object that writes data to a disk. You want to add compression and encryption. Instead of creating complex subclasses, you can wrap the original object: `new EncryptionDecorator(new CompressionDecorator(new FileDataSource()))`. Each decorator adds its specific behavior before passing the call down to the object it wraps.
- **In Modern C#:** This is the core principle behind the [**ASP.NET](http://asp.net/) Core Middleware pipeline**. Each piece of middleware (for authentication, logging, routing, etc.) is a decorator that wraps the next piece of the HTTP request processing pipeline. The `System.IO.Stream` classes (`FileStream`, `GZipStream`, `CryptoStream`) are also a classic example of the Decorator pattern.

---

### Most Used Behavioral Patterns

Behavioral patterns focus on effective communication and the assignment of responsibilities between objects.

### 1. Strategy Pattern

- **Why It's So Common:** It is the classic, clean solution for handling situations where you have a family of interchangeable algorithms for a specific task. Instead of using a large `if-else` or `switch` statement to select a behavior, you encapsulate each algorithm in its own class (a "strategy") and let the client or context object switch between them.
- **Common Use Case:** A navigation app needs to calculate routes. The algorithm can vary: `RoadStrategy` (for cars), `WalkingStrategy` (for pedestrians), or `PublicTransportStrategy`. The main `Navigator` class holds a reference to a `IRouteStrategy` interface and simply calls its `BuildRoute()` method, without needing to know the specifics of the current algorithm.
- **In Modern C#:** This pattern is extremely common and works very well with Dependency Injection. You can easily register multiple implementations of an `IRouteStrategy` and inject the desired one into your `Navigator` class based on user selection or configuration.

### 2. Observer Pattern

- **Why It's So Common:** This pattern is the foundation of event-driven programming. It allows you to create a subscription mechanism where multiple "observer" objects can be notified when something happens to the "publisher" object they are observing, without the publisher needing to know anything about its observers. This creates a very loose coupling.
- **Common Use Case:** A `Customer` object is interested in a `Product` that is out of stock. When the `Product`'s availability changes, it notifies all subscribed `Customer` objects, who can then take action.
- **In Modern C#:** This pattern is a first-class citizen in the C# language through the **`event` keyword**. UI programming in .NET (WinForms, WPF, Blazor) is almost entirely based on this pattern (e.g., `button.Click += OnButtonClicked;`). The `INotifyPropertyChanged` interface used in data binding is another prime example.

### 3. Iterator Pattern

- **Why It's So Common:** The Iterator pattern is so fundamental that it's built directly into most modern programming languages. It provides a standard way to traverse through the elements of a collection without exposing the collection's underlying structure (e.g., array, list, tree).
- **Common Use Case:** You have a custom collection class, and you want clients to be able to loop through it using a standard `foreach` loop.
- **In Modern C#:** This pattern is implemented via the `IEnumerable` and `IEnumerator` interfaces. Every time you use a **`foreach` loop**, you are using the Iterator pattern. The entire LINQ library is built on top of this pattern, allowing you to compose complex queries over any collection that implements `IEnumerable`.

### Special Mentions (Also Highly Used)

- **Template Method:** Extremely common in frameworks. It defines the skeleton of an algorithm in a base class and allows subclasses to override specific steps without changing the overall structure. It's a very natural way to share code in an inheritance-based design.
- **Command:** The go-to pattern for implementing Undo/Redo functionality. It's also used to queue tasks, log operations, and parameterize UI elements with actions.