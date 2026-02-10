# Garbage Collection

---

### Part 1: Managed vs. Unmanaged Resources

This is the most critical distinction. The Garbage Collector (GC) can **only** manage memory that the .NET runtime allocated itself. It has no idea about resources requested directly from the Operating System.

### A) Managed Resources

- **Definition:** Anything whose memory is allocated and managed entirely by the .NET Common Language Runtime (CLR). This includes almost everything you create in C#.
- **How it works:** The GC keeps a graph of all objects. It knows which objects are reachable (still in use) and which are not. It can automatically find and reclaim the memory of unreachable objects.
- **Analogy:** You rent a furnished apartment from a large management company (the CLR). You don't own the furniture (`string`, `int`, `List<T>`). When you move out (the object goes out of scope), the management company automatically takes care of cleaning everything up and re-renting the space.
- **Examples:**
    - **All standard C# objects:** `new Person()`, `new List<string>()`
    - **Strings:** `string s = "hello";`
    - **Arrays:** `int[] numbers = new int[10];`
    - **Delegates, Events, etc.**

**You do not need to do anything to clean up managed resources.** The GC handles it for you.

### B) Unmanaged Resources

- **Definition:** Resources that are acquired directly from the Operating System (OS) and are **not** under the direct control of the .NET GC. These are often "handles"—small integer pointers that the OS gives you to represent a heavyweight kernel object.
- **How it works:** The GC knows about the C# *wrapper object* that holds the handle, but it has no idea what the handle itself represents (e.g., an open file). If the GC just cleans up the wrapper, the handle is lost, and the OS resource is **leaked**. It remains open until the process exits.
- **Analogy:** You buy a car directly from the manufacturer (the OS). The car's title (the handle) is in your name. If you abandon the car on the side of the road (let the C# object go out of scope), the car is still legally yours and will rust away, taking up space (a resource leak). You have a **responsibility to go to the DMV and explicitly release the title** (`Dispose()`).
- **Examples (often wrapped by a `SafeHandle`):**
    - **File Handles:** `FileStream`, `StreamWriter` (they hold a handle to a file opened by the OS).
    - **Network Connections:** `Socket`, `TcpClient` (they hold a handle to a network socket).
    - **Database Connections:** `SqlConnection` (holds a handle to a TCP connection and a session on the SQL server).
    - **Graphics Objects:** GDI+ handles like `System.Drawing.Bitmap` (holds a handle to a device-dependent bitmap in memory).
    - **Direct Memory Allocation:** Pointers allocated via `Marshal.AllocHGlobal`.

**You MUST explicitly release unmanaged resources** using the `IDisposable` pattern (`using` block or `.Dispose()`).

---

### Part 2: How the Runtime Manages Stack and Heap

Memory in a .NET application is divided into two main areas: the **Stack** and the **Heap**. The GC only operates on the Heap.

### A) The Stack (Not Garbage Collected)

- **What it is:** A highly organized, Last-In-First-Out (LIFO) data structure. Each thread gets its own Stack.
- **What goes on it:**
    - **Value Types:** `int`, `double`, `bool`, `struct`, `DateTime`. (Local variables only).
    - **Pointers (References):** A pointer to an object that lives on the Heap. The pointer itself is on the Stack.
    - **Method Parameters & Return Addresses.**
- **Memory Management:** **Extremely fast and simple. There is NO garbage collection on the Stack.**
    1. When a method is called, a "stack frame" containing its local variables is pushed onto the top of the stack.
    2. When the method **exits**, the entire frame is simply popped off. The memory is instantly "reclaimed" because the stack pointer just moves back down.

**Example Code Breakdown:**

```csharp
public void MyMethod() // Method Entry: Stack frame is created for MyMethod.
{
    int x = 10;           // 'x' (value 10) is placed on the Stack.
    Person p = new Person(); // 'p' (a reference/pointer) is placed on the Stack.
                          // The actual Person object is created on the HEAP.
    AnotherMethod();
} // Method Exit: Entire stack frame (x and p) is instantly destroyed.
  // The Person object on the Heap is now "orphaned".

```

### B) The Heap (Garbage Collected)

- **What it is:** A large, unorganized pool of memory for storing objects (reference types). It's more like a messy garage where you find the first available space.
- **What goes on it:**
    - **Reference Types:** Anything created with the `new` keyword (`class` instances, arrays, strings).
    - Static variables.
- **Memory Management:** This is where the Garbage Collector does its work.

---

### Part 3: The Garbage Collection Process (Internally)

The .NET GC is a "Mark and Compact" generational garbage collector. This sounds complex, but it's a very clever, multi-stage process.

### Step 1: The "Roots"

The GC needs a starting point to figure out what's still in use. It creates a list of "roots," which are things that are always considered reachable:

- Global/static objects.
- Local variables and parameters on the **current stack** of every active thread.
- CPU registers.

### Step 2: The "Mark" Phase

1. The GC starts at the roots.
2. It recursively follows every single reference from the roots, building a graph of all objects that can be reached.
3. It "marks" every object it finds as "alive."
4. Any object that is not marked at the end of this phase is considered **garbage**.

**In our earlier example:** When `MyMethod` exits, the pointer `p` on the stack is gone. The `Person` object on the heap is no longer reachable from any root, so it will **not be marked** as alive.

### Step 3: The "Sweep" (or "Compact") Phase

1. **Sweep:** The GC goes through the heap and frees the memory occupied by all the unmarked (garbage) objects.
2. **Compact (Key Optimization):** To avoid memory fragmentation (lots of small empty holes), the GC then **shuffles all the "alive" objects down**, moving them next to each other at the start of the heap segment.
3. It then updates all the root pointers on the Stack to point to the new locations of the moved objects.

This compaction step is why managed memory access can be very fast—related objects often end up physically close to each other in RAM.

This entire process is highly optimized using **Generations (Gen 0, 1, 2)**, based on the "Generational Hypothesis": *most objects die young*. The GC runs frequently on the "youngest" objects (Gen 0) and much less frequently on the long-lived objects (Gen 2), making the common case extremely fast.

# How Garbage Collector Works

---

### The Generational Hypothesis: "Most Objects Die Young"

The entire concept of generations is built on a simple observation of how programs behave:

1. **Many objects are short-lived.** A `string` created inside a loop for temporary processing is a classic example.
2. **Few objects are long-lived.** A singleton service, a logger instance, or a global cache are examples.
3. **Compacting the entire heap is slow.** If you have a 16 GB heap, stopping the program to scan and compact all of it would be a major performance killer.

Based on this, the GC divides the managed heap into segments called **Generations**.

### Part 1: Generation 0 (Gen 0) - The Nursery

- **What it is:** The "youngest" and smallest generation. **This is where all newly allocated small objects go.**
- **Analogy:** The "triage" or "reception" area of a hospital. Everyone arrives here first.
- **How it works:** Gen 0 is designed to be collected **very frequently and very fast**. Because most objects die young, a collection of Gen 0 is highly effective at reclaiming a lot of memory with minimal work.
- **Process:**
    1. The application runs, and new objects fill up Gen 0.
    2. When Gen 0 becomes full (its budget is exhausted), a **Gen 0 garbage collection is triggered.** This is the cheapest type of GC.
    3. The GC's "Mark" phase starts from the roots and identifies all reachable (alive) objects *within Gen 0*.
    4. **Survival:** Any object in Gen 0 that survives the collection (i.e., it's still alive) is **promoted to Generation 1.**
    5. **Reclamation:** The memory space of Gen 0 is then considered completely free. The surviving objects were moved, not just marked, so there's no need for a complex sweep. The allocation pointer is simply reset to the beginning of the Gen 0 segment.

**Key Point:** A healthy application should have frequent, fast Gen 0 collections. This is a sign of good memory hygiene.

### Part 2: Generation 1 (Gen 1) - The Buffer

- **What it is:** The "middle-aged" generation. It contains objects that survived a Gen 0 collection.
- **Analogy:** The "short-term observation ward" of the hospital. Patients who aren't immediately discharged but aren't critically ill go here.
- **How it works:** Gen 1 acts as a buffer between the volatile short-lived objects in Gen 0 and the long-lived objects in Gen 2. A Gen 1 collection is triggered when Gen 0 collections aren't freeing up enough memory.
- **Process:**
    1. A **Gen 1 garbage collection** is triggered.
    2. This process collects **both Gen 1 and Gen 0**.
    3. The GC marks all reachable objects in Gen 0 and Gen 1.
    4. **Survival:**
        - Surviving objects from Gen 0 are promoted to Gen 1.
        - Surviving objects from Gen 1 are **promoted to Generation 2.**
    5. The memory for Gen 0 and the collected parts of Gen 1 is compacted and reclaimed.

**Key Point:** Gen 1 collections are more expensive than Gen 0 because they involve scanning a larger set of objects.

### Part 3: Generation 2 (Gen 2) - The Long-Term Store

- **What it is:** The "oldest" generation. It contains long-lived objects that have survived collections in both Gen 0 and Gen 1.
- **Analogy:** The "long-term care facility" of the hospital. Patients who will be here for a very long time reside here.
- **How it works:** This is the home for application-level objects like services, static data, and large caches. Gen 2 is collected **infrequently**.
- **Process:**
    1. A **Gen 2 garbage collection (a "full GC")** is triggered. This is the most expensive type of collection and can cause a noticeable pause in the application.
    2. It collects **the entire managed heap: Gen 2, Gen 1, and Gen 0.**
    3. The GC marks reachable objects across all generations.
    4. Any object that survives in Gen 2 stays in Gen 2.
    5. Memory is compacted.

**Key Point:** A high frequency of Gen 2 collections is a **major performance warning sign**. It might indicate you have a memory leak or are creating objects that are being promoted but then dying shortly after, a condition known as "mid-life crisis" objects.

### Part 4: The Large Object Heap (LOH) - The Special Ward

- **What it is:** Not technically a "generation," but a separate logical area of the heap. It's for **very large objects**, specifically those **85,000 bytes or larger**.
- **Why does it exist?** Compacting large objects is extremely expensive. Moving a 10 MB byte array in memory is a slow operation that can stall the application.
- **How it works:**
    1. When you allocate a large object (e.g., `new byte[100_000]`), it goes **directly to the LOH**, bypassing Gen 0 entirely.
    2. The LOH is collected **only during a Gen 2 collection.**
    3. **Crucially (before .NET 4.5.1):** The LOH was **not compacted**. When an object on the LOH died, it left a hole. Over time, the LOH would become fragmented, which could lead to `OutOfMemoryException` even if there was enough total free memory, because no single hole was large enough to fit a new allocation.
    4. **Modern .NET:** The GC can now compact the LOH, but it's still an expensive operation that it tries to avoid.

**Key Point:** Avoid allocating large, short-lived objects. Frequent LOH allocations are a major source of memory fragmentation and performance issues. This is why APIs like `ArrayPool` and `Memory<T>` were created—to reuse large buffers instead of constantly allocating new ones.

### The GC "Finalization Queue" (More accurately, the Freachable Queue)

This isn't for normal GC, but for objects that have a **finalizer** (a `~MyClass()` method). You should almost never write a finalizer. `IDisposable` is the correct pattern.

- **When it's used:** When the GC finds that a finalizable object is garbage, it does **not** immediately reclaim its memory.
- **The Process:**
    1. The object is considered "garbage."
    2. The GC finds a pointer to it and puts that pointer onto a special queue called the **"F-reachable Queue."**
    3. A dedicated, high-priority finalizer thread runs separately. It pulls pointers from this queue and calls the `~MyClass()` finalizer method on each object.
    4. **Only on the *next* GC cycle** will the now-finalized object's memory be reclaimed.

**Why this is bad:**

- **Unpredictable:** You have no idea *when* the finalizer will run. It could be seconds or minutes later.
- **Resurrection:** It makes the object "live" for at least one extra GC cycle, keeping its memory locked.
- **Performance:** It adds significant overhead to the GC process.

**Golden Rule:** Use `IDisposable` and `using` blocks to deterministically clean up unmanaged resources. Do not use finalizers unless you are writing a direct wrapper around an unmanaged resource (a `SafeHandle` is even better).

# IDispose vs Finalizers ~ClassName()

### 1. The Core Purpose: Releasing Unmanaged Resources

Both of these mechanisms exist for one primary reason: to handle the cleanup of **unmanaged resources**. The Garbage Collector is ignorant of these resources, so we need a way to tell our program how to release them.

- **Managed Resources:** `string`, `List<T>`, `int[]`. **GC handles these automatically.**
- **Unmanaged Resources:** File Handles, Database Connections, Network Sockets, GDI handles (`Bitmap`). **We must handle these manually.**

The key difference between the two mechanisms is **when and how** they are called.

- **`IDisposable.Dispose()` (Deterministic):** "Clean up now, on my command."
- **Finalizer (`~ClassName()`) (Non-Deterministic):** "Clean up... eventually... maybe... when the GC gets around to it."

---

### 2. Deep Dive: `IDisposable` and the `Dispose` Pattern

### A) Concept and Interface

`IDisposable` is a simple interface with a single method, `Dispose()`. It's a public contract that says:

> "I am a class that holds onto an expensive or unmanaged resource. I am giving you, the developer who is using me, a way to tell me exactly when you are done with that resource so I can release it immediately."
> 

It provides **deterministic cleanup**.

### B) The Correct Implementation: The `using` statement

The `using` statement is C#'s syntactic sugar for the `try...finally` pattern with `Dispose()`. It guarantees that `.Dispose()` will be called, even if an exception occurs.

```csharp
public void ProcessFile(string path)
{
    // The 'using' block is the PREFERRED way to handle IDisposable objects.
    // It guarantees that fileReader.Dispose() is called at the closing brace '}'.
    using (StreamReader fileReader = new StreamReader(path))
    {
        // 1. A File Handle (unmanaged resource) is opened by the OS.
        string line = fileReader.ReadLine();
        Console.WriteLine(line);

        if (string.IsNullOrEmpty(line))
        {
            throw new InvalidOperationException("File is empty.");
        }
    } // <-- COMPILER TRANSFORMS THIS to a finally block where fileReader.Dispose() is called.

    // At this point, the file handle is guaranteed to be closed and released.
}

```

This is what the compiler actually generates:

```csharp
/*
StreamReader fileReader = new StreamReader(path);
try
{
    // ... work ...
}
finally
{
    if (fileReader != null)
    {
        ((IDisposable)fileReader).Dispose();
    }
}
*/

```

### C) The Full `IDisposable` Pattern (When you have a base class and a finalizer)

When you are authoring a class that directly holds an unmanaged handle, the full pattern is more complex. It's designed to be called correctly by both the user (`.Dispose()`) and the Garbage Collector (finalizer) without doing a double-cleanup.

```csharp
public class MyResourceWrapper : IDisposable
{
    // Represents a handle from the OS (e.g., from an unmanaged C++ DLL).
    private IntPtr _unmanagedHandle;
    private bool _disposed = false; // To prevent redundant calls

    public MyResourceWrapper(string resourceName)
    {
        // P/Invoke call to get the unmanaged resource handle.
        _unmanagedHandle = NativeMethods.CreateResource(resourceName);
    }

    // PUBLIC DISPOSE METHOD: Called by the user.
    public void Dispose()
    {
        // Call the internal dispose method.
        // 'true' means we are disposing from user code, so clean up EVERYTHING (managed and unmanaged).
        Dispose(true);
        // Tell the GC that it doesn't need to call the finalizer, because we've already cleaned up.
        GC.SuppressFinalize(this);
    }

    // PROTECTED VIRTUAL DISPOSE: For subclasses to override.
    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;

        if (disposing)
        {
            // FREE MANAGED RESOURCES HERE (if any).
            // Example: someManagedObject.Dispose();
        }

        // FREE UNMANAGED RESOURCES HERE.
        // Always do this, whether called from Dispose() or the finalizer.
        NativeMethods.ReleaseResource(_unmanagedHandle);
        _unmanagedHandle = IntPtr.Zero;

        _disposed = true;
    }

    // FINALIZER: The backup plan. Called by the GC if the user forgot to call Dispose().
    ~MyResourceWrapper()
    {
        // We are being called from the finalizer thread, not user code.
        // We should ONLY clean up unmanaged resources.
        // We must NOT touch any other managed objects, as they may have already been finalized!
        Dispose(false);
    }
}
```

### 3. Deep Dive: The Finalizer (`~`)

### A) Concept

A finalizer is a special C# class method that is invoked **non-deterministically** by the Garbage Collector *before* the object's memory is reclaimed. It looks like a C++ destructor (`~ClassName()`), but it behaves very differently.

**It is not a destructor! It is a "last-chance cleanup" safety net.**

### B) When to Use It (The Golden Rule)

**Almost never.**

The only valid reason for an application developer to implement a finalizer is if:

1. Your class **directly holds an unmanaged resource handle** (e.g., an `IntPtr` from a `P/Invoke` call).
2. You need a **backup plan** in case a lazy developer using your class forgets to call `Dispose()`.

If your class *only* contains managed objects (even if those objects are themselves `IDisposable`), you should **NOT** implement a finalizer. Just implement `IDisposable`.

**Why not?**
Because creating a finalizer tells the GC this object is special. It makes it survive an extra GC collection cycle and puts it on the "F-reachable" queue, which adds significant performance overhead.

### C) How It Fails You

1. **It's NOT guaranteed to run.** If your application terminates abnormally, the finalizer thread might not have a chance to run.
2. **You have NO control over when it runs.** It could be seconds or minutes after the object becomes garbage. A file handle could be held open for an unacceptably long time.
3. **The order is not guaranteed.** You cannot rely on finalizers for different objects running in any specific order.
4. **You cannot reference other managed objects.** When the finalizer runs, other managed objects it might have known about may have *already been garbage collected*. Trying to access them will lead to undefined behavior or exceptions.

---

### 4. Summary: The Decision Tree

Follow this logic when writing a class:

1. **Does my class use any `IDisposable` members OR directly hold an unmanaged handle?**
    - **NO:** You don't need to do anything. The GC will handle it.
    - **YES:** Go to step 2.
2. **Implement `IDisposable`** by creating a `Dispose()` method. In this method, call `.Dispose()` on all your disposable members. Use the `using` statement everywhere you instantiate your class.
3. **Does my class *directly* hold an unmanaged resource handle (`IntPtr`, `SafeHandle`)?**
    - **NO:** You are done. `IDisposable` is all you need.
    - **YES:** Add a **finalizer (`~`)** as a safety net in case the user forgets to call `Dispose()`. Implement the full `protected virtual Dispose(bool)` pattern shown above.

**Example of a class that needs `IDisposable` but NOT a finalizer:**

```csharp
public class FileManager : IDisposable
{
    // It HOLDS a disposable object, but not a raw handle.
    private readonly StreamWriter _writer;

    public FileManager(string path)
    {
        _writer = new StreamWriter(path);
    }

    public void WriteData(string data)
    {
        _writer.WriteLine(data);
    }

    // It only needs to implement Dispose.
    public void Dispose()
    {
        // Pass the responsibility down the chain.
        _writer.Dispose();
    }
}
```

# IDispose example for SqlConnection

You are absolutely correct. That point is confusing and is one of the most frequently misunderstood aspects of the `IDisposable` pattern.

Let's clarify it with a better, more practical example.

### The Misconception vs. The Reality

- **The Misconception:** "I need to set my managed objects to `null` inside `Dispose` so the GC can collect them."
    - **This is wrong and unnecessary.** Setting a reference to `null` doesn't speed up garbage collection. The GC is smart enough to find unreachable objects on its own.
- **The Reality:** The phrase "free managed resources" doesn't mean manually collecting memory. It means **"recursively call `.Dispose()` on any other `IDisposable` objects that *this* object owns."**

It's about passing the cleanup signal down the chain of ownership.

### The Perfect Real-World Example: A Database Repository

Imagine you are creating a class, `UserRepository`, which is responsible for talking to a database. It needs a `SqlConnection` object to do its job.

A `SqlConnection` is `IDisposable` because it holds an unmanaged network socket and a session handle on the SQL Server.

The `UserRepository` **owns** the `SqlConnection`. When the `UserRepository` is destroyed, the `SqlConnection` must also be properly disposed of.

Here is the correct implementation.

```csharp
using System;
using System.Data.SqlClient;

// A class that OWNS an IDisposable resource (the SqlConnection).
// Therefore, it must ALSO be IDisposable.
public class UserRepository : IDisposable
{
    // ==================
    // 1. MANAGED RESOURCE
    // ==================
    // This is a "managed" object from our perspective, but it WRAPS an
    // unmanaged resource. We are responsible for Disposing it.
    private SqlConnection _connection;

    // A simple managed object that does NOT need special handling.
    private readonly string _tableName = "Users";

    private bool _isDisposed = false;

    public UserRepository(string connectionString)
    {
        // The UserRepository creates and therefore "owns" this connection.
        _connection = new SqlConnection(connectionString);
        _connection.Open();
    }

    public string GetUserName(int id)
    {
        if (_isDisposed)
            throw new ObjectDisposedException(nameof(UserRepository));

        // ... code to get user name from the database ...
        Console.WriteLine($"Getting user {id} from table '{_tableName}'");
        return "John Doe";
    }

    // ==========================================================
    // 2. THE DISPOSE IMPLEMENTATION (THE IMPORTANT PART)
    // ==========================================================

    // The public entry point, called by the user (via `using`).
    public void Dispose()
    {
        // Start the cleanup chain.
        Dispose(true);
        // We've cleaned up, so tell the GC it doesn't need to call the finalizer.
        GC.SuppressFinalize(this);
    }

    // The internal cleanup logic.
    protected virtual void Dispose(bool disposing)
    {
        // Prevent running this more than once.
        if (_isDisposed)
        {
            return;
        }

        // The parameter 'disposing' is KEY.
        if (disposing)
        {
            // ===========================================================
            // === "FREE MANAGED RESOURCES" HAPPENS HERE ===
            // ===========================================================
            // This code block runs ONLY when called from the public Dispose().
            // It is SAFE to access other managed objects here.
            //
            // We are NOT setting them to null. We are calling THEIR Dispose() methods.
            if (_connection != null)
            {
                Console.WriteLine("Disposing the managed SqlConnection object...");
                _connection.Dispose(); // Pass the cleanup signal down the chain.
                _connection = null;    // Optional: help prevent ObjectDisposedException.
            }
        }

        // ==========================================================
        // === "FREE UNMANAGED RESOURCES" WOULD GO HERE ===
        // ==========================================================
        // This class doesn't hold any RAW unmanaged handles (like an IntPtr),
        // so this section is empty. If it did, the cleanup code would be here.
        // This part runs whether called from Dispose() OR the finalizer.

        _isDisposed = true;
    }

    // A finalizer is often overkill if you only have managed IDisposable members,
    // but it's included for demonstrating the pattern. It's the "safety net".
    ~UserRepository()
    {
        // User forgot to call Dispose()!
        // The GC is calling us from the finalizer thread.
        Console.WriteLine("UserRepository's finalizer is running. This indicates a memory leak!");
        Dispose(false);
    }
}

```

### The Logic of the `disposing` Flag

Now we can see the purpose of that boolean flag:

- **Case 1: The Good Developer (User calls `Dispose()`)**
    1. The `using` block ends. `UserRepository.Dispose()` is called.
    2. It calls `Dispose(true)`.
    3. The `if (disposing)` block executes.
    4. It safely calls `_connection.Dispose()`. The connection is closed, and the unmanaged socket is released immediately.
    5. Everything is clean. `GC.SuppressFinalize(this)` prevents the finalizer from running later.
- **Case 2: The Bad Developer (User forgets `using`)**
    1. The `UserRepository` object is abandoned.
    2. Eventually, the GC finds it's unreachable. It sees the object has a finalizer.
    3. It puts the object on the finalization queue.
    4. The finalizer thread later runs `~UserRepository()`.
    5. It calls `Dispose(false)`.
    6. The `if (disposing)` block is **SKIPPED**.
    7. **Why?** Because the GC gives no guarantee about the state of other managed objects. The `_connection` object might have *already been finalized or collected*. It is **unsafe to call methods on it**.
    8. The "free unmanaged resources" section would run, cleaning up any raw handles this class was *directly* responsible for.
    9. In this specific example, since the `UserRepository` doesn't have its *own* raw unmanaged handles, the forgotten `Dispose()` call results in a **resource leak**—the `SqlConnection` is never properly closed. The finalizer only protects the resources the class *directly* owns, not the ones its members own.

### Summary

| `Dispose(true)` (Called from `Dispose()`) | `Dispose(false)` (Called from Finalizer `~`) |
| --- | --- |
| **Who Calls It?** You, the developer. | The Garbage Collector. |
| **When?** Deterministically. Immediately. | Non-deterministically. "Eventually." |
| **Is it safe to touch other managed objects (like `_connection`)?** | **Yes.** |
| **Action** | Dispose managed resources (`_connection.Dispose()`) **AND** unmanaged resources. |

So, "freeing managed resources" is really about being a good citizen in the `IDisposable` ecosystem and **calling `Dispose` on the objects you own.**