# Iterator Pattern

### 1. What is it?

The Iterator is a behavioral design pattern that lets you traverse elements of a collection (like a list, stack, or tree) without exposing its underlying representation. It extracts the traversal logic from the collection into a separate object called an **iterator**.

This pattern is so fundamental that it is built into the core of most modern programming languages, including C# with its `IEnumerable` and `IEnumerator` interfaces and the `foreach` loop.

### 2. Why it is required?

The Iterator pattern is required to solve two main problems:

1. **Hiding Complexity and Decoupling:** Different collections store data in different ways. A `List` is a simple sequence, but a `Tree` has a complex structure. Without a common traversal mechanism, the client code would need to know the specific internal structure of every collection it wants to loop through, leading to tight coupling. If a collection's implementation changes (e.g., from `List` to `Dictionary`), all client code that loops over it would have to be rewritten. The Iterator provides a uniform, abstract way to access elements, decoupling the client from the collection's internal details.
2. **Separating Responsibilities:** A collection's primary responsibility is to store and manage elements efficiently. Adding more and more traversal algorithms (e.g., depth-first, breadth-first for a tree) into the collection class itself would bloat it and violate the Single Responsibility Principle. By extracting traversal algorithms into separate iterator classes, the code becomes cleaner and more maintainable.

### 3. Details and key points and examples in the reference Book

- **Core Idea:**
    - Extract the traversal behavior of a collection into a separate iterator object.
- **Encapsulation of Traversal State:**
    - The iterator object is responsible for tracking the traversal's state, such as the current position and how many elements are left.
    - This allows multiple iterators to traverse the same collection independently and concurrently without interfering with each other.
- **Common Iterator Interface:**
    - All iterators must implement a common interface, which typically provides methods for:
        1. Fetching the next element (e.g., `GetNext()` or `MoveNext()`).
        2. Checking if there are more elements (e.g., `hasMore()` or a boolean return from `MoveNext()`).
        3. Retrieving the current element (e.g., `Current`).
- **The Collection's Role:**
    - The collection itself should have a method that returns a new iterator object (e.g., `createIterator()`).
- **Book Example:**
    - The book uses an example of a social network (`Facebook`) which acts as a collection of user profiles.
    - The system needs to support different ways of traversing the social graph, such as iterating over a user's `friends` versus their `coworkers`.
    - Instead of adding this complex logic to the `Facebook` class, it provides factory methods like `createFriendsIterator()` and `createCoworkersIterator()`.
    - Both of these methods return an object that implements a common `ProfileIterator` interface. A client class like `SocialSpammer` can then work with any iterator through this interface, completely decoupled from the details of Facebook's API or graph structure.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - When your collection has a complex internal structure (like a tree or graph) and you want to hide that complexity from clients.
    - When you need to support multiple traversal algorithms over the same collection and you don't want to bloat the collection class with this logic.
    - When you want a uniform interface for traversing various collection types.
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - **Overkill for Simple Collections:** The book states that applying the pattern can be an overkill if your application only works with simple collections where direct access or a basic loop is sufficient.
    - **Performance:** Using an iterator may be slightly less efficient than direct traversal of some specialized collections (like a plain array). In high-performance computing, this overhead might be a consideration.

### 5. Step By Step Detailed Rules to Map the concept to C# code

In C#, the Iterator pattern is implemented through the `IEnumerable` and `IEnumerator` interfaces. The `foreach` loop is syntactic sugar for using these interfaces. The modern and most common way to implement this is with the `yield return` keyword.

1. **Implement `IEnumerable<T>`:** Make your custom collection class implement the `IEnumerable<T>` interface, where `T` is the type of the objects in your collection.
2. **Implement `GetEnumerator()`:** You must provide an implementation for the `GetEnumerator()` method from the interface.
3. **Use `yield return`:** Inside the `GetEnumerator()` method, create a loop (e.g., a `foreach` or `for` loop) that goes through your collection's internal items. Instead of returning the whole collection, use the `yield return` statement to return one element at a time. The C# compiler will automatically generate a state machine (a private iterator class) behind the scenes for you.
4. **Client Usage:** The client can now use a standard `foreach` loop to traverse your custom collection, just as it would with a `List` or an array.

### 6. C# code Example which is not in the correct state

This "Bad Code" shows a custom `RadioStation` playlist class. The client has to know about its internal `List<Song>` implementation to loop through it, creating tight coupling.

```csharp
// BAD CODE: Client is coupled to the collection's internal implementation.
public class Song
{
    public string Artist { get; }
    public string Title { get; }

    public Song(string artist, string title)
    {
        Artist = artist;
        Title = title;
    }

    public override string ToString() => $"{Artist} - {Title}";
}

// This collection does not have a standard way to be traversed.
public class RadioStation
{
    // The client has to know that the songs are stored in a public List.
    // If we change this to a Dictionary or array, all client code breaks.
    public List<Song> Playlist { get; }

    public RadioStation()
    {
        Playlist = new List<Song>
        {
            new Song("Queen", "Bohemian Rhapsody"),
            new Song("Daft Punk", "Get Lucky"),
            new Song("The Beatles", "Hey Jude")
        };
    }
}

// The Client code is tightly coupled.
public class Client
{
    public static void Main()
    {
        var radio = new RadioStation();

        // The client must access the internal 'Playlist' property directly.
        Console.WriteLine("--- Now Playing on Radio Station ---");
        foreach (var song in radio.Playlist)
        {
            Console.WriteLine(song);
        }
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" refactors the `RadioStation` to correctly implement the Iterator pattern using `IEnumerable<T>` and `yield return`, completely decoupling the client.

```csharp
// GOOD CODE: Applying the Iterator Pattern

public class Song
{
    public string Artist { get; }
    public string Title { get; }

    public Song(string artist, string title)
    {
        Artist = artist;
        Title = title;
    }

    public override string ToString() => $"{Artist} - {Title}";
}

// Rule 1: The collection now implements IEnumerable<Song>.
public class RadioStation : IEnumerable<Song>
{
    // The internal storage is now private, hiding the implementation details.
    private readonly List<Song> _playlist;

    public RadioStation()
    {
        _playlist = new List<Song>
        {
            new Song("Queen", "Bohemian Rhapsody"),
            new Song("Daft Punk", "Get Lucky"),
            new Song("The Beatles", "Hey Jude")
        };
    }

    // Rule 2 & 3: Implement GetEnumerator using 'yield return'.
    // The C# compiler will generate the iterator state machine for us.
    public IEnumerator<Song> GetEnumerator()
    {
        foreach (var song in _playlist)
        {
            // 'yield return' pauses the method and returns one item at a time.
            yield return song;
        }
    }

    // Explicit implementation for the non-generic IEnumerable.
    System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator()
    {
        return this.GetEnumerator();
    }
}

// The Client code is now completely decoupled from the internal implementation.
public class Client
{
    public static void Main()
    {
        var radio = new RadioStation();

        // Rule 4: The client can use a standard foreach loop.
        // It has no idea how the RadioStation stores its songs internally.
        Console.WriteLine("--- Now Playing on Radio Station ---");
        foreach (var song in radio)
        {
            Console.WriteLine(song);
        }
    }
}
```