# PLINQ

Of course. Let's do a deep dive into Parallel LINQ (PLINQ).

PLINQ is not just "LINQ but faster." It's a sophisticated query engine with its own set of behaviors, optimizations, and trade-offs. Understanding its options is key to using it effectively.

### 1. The Core Concept: From `IEnumerable` to `ParallelQuery`

The entire PLINQ system is activated by a single extension method: `.AsParallel()`.

- **`IEnumerable<T>` (Standard LINQ):** This represents a *sequence* that can be pulled one item at a time. It's a single-file line.
- **`ParallelQuery<T>` (PLINQ):** When you call `.AsParallel()`, you convert the sequence into a `ParallelQuery<T>`. This object understands how to **partition** the data source and process those partitions on multiple threads. It's like opening up multiple checkout lanes.

```csharp
IEnumerable<int> sequence = Enumerable.Range(1, 100);

// This is now a ParallelQuery<int>, and all subsequent operators
// will be the PLINQ versions (e.g., a parallel Where).
ParallelQuery<int> parallelSequence = sequence.AsParallel();

```

---

### 2. Deep Dive into the PLINQ Options (Query Operators)

These are methods you can chain into your PLINQ query to control its execution behavior.

### A) `.WithDegreeOfParallelism(int dop)`

- **Meaning:** "Manually set the maximum number of threads that this query is allowed to use."
- **Default Behavior:** By default, PLINQ will try to use all available CPU cores.
- **Use Case:** Throttling. If you have a 16-core server but know your query is memory-intensive or you need to leave resources for other processes, you can constrain it.
- **Example:**
    
    ```csharp
    var results = numbers
        .AsParallel()
        .WithDegreeOfParallelism(4) // Only use a maximum of 4 CPU cores for this query.
        .Where(n => IsPrime(n))
        .ToList();
    
    ```
    

### B) `.AsOrdered()`

- **Meaning:** "The final output sequence must be in the same order as the input source."
- **Default Behavior:** **PLINQ is unordered by default for performance.** It will return results as soon as they are processed, regardless of their original position. A `Where` might return element `[80]` before element `[5]`.
- **Use Case:** Essential when the order of the results matters (e.g., you are processing time-series data or the index has meaning).
- **Performance Cost:** Ordering introduces a performance hit. Each thread processes its items, but then PLINQ must collect all the results and re-sort them before handing them to you.
- **Example:**
    
    ```csharp
    // Without AsOrdered(), this might print 8, 2, 4, 6...
    // With AsOrdered(), this will guarantee printing 2, 4, 6, 8...
    var orderedEvens = Enumerable.Range(1, 10)
        .AsParallel()
        .AsOrdered()
        .Where(n => n % 2 == 0)
        .ToList();
    
    ```
    
- **Counterpart:** You can call `.AsUnordered()` later in a query to "release" the ordering constraint for subsequent operations if it's no longer needed, which can improve performance.

### C) `.WithExecutionMode(ParallelExecutionMode mode)`

- **Meaning:** A hint to the PLINQ engine about whether parallelism is required.
- **Modes:**
    - `Default`: The engine decides. If it thinks the overhead of going parallel is greater than the benefit (e.g., the source collection is tiny), it might run the query sequentially.
    - `ForceParallelism`: "Go parallel no matter what." This forces PLINQ to use multiple threads, even if it might be slower. Useful for testing or when you know more about the query's cost than the engine does.
- **Use Case:** Mostly for benchmarking or forcing a specific behavior when you know the `Default` heuristic is making the wrong choice.
- **Example:**
    
    ```csharp
    var results = smallCollection
        .AsParallel()
        .WithExecutionMode(ParallelExecutionMode.ForceParallelism) // Ensure it runs on multiple threads for this benchmark.
        .Select(x => HeavyCpuWork(x))
        .ToList();
    
    ```
    

### D) `.WithMergeOptions(ParallelMergeOptions options)`

- **Meaning:** Controls how the results from different threads are "merged" back into a single sequence for the consumer (e.g., your `ToList()` or `foreach` loop).
- **Default Behavior:** `AutoBuffered`. PLINQ will process a chunk of items, put them in a buffer, and hand the buffer to the consumer thread. This balances latency and throughput.
- **Options:**
    - `AutoBuffered`: The default. Good for most scenarios.
    - `NotBuffered`: "Streaming mode." As soon as a single item is processed on any thread, immediately hand it to the consumer thread. This provides the lowest latency to get the *first* item, but the high synchronization cost can hurt overall throughput.
    - `FullyBuffered`: Process *all* items on all threads first. Store *all* results in a giant buffer. Only when everything is done, hand the entire result set to the consumer. This has the highest latency but can have the best overall throughput because the consumer thread isn't a bottleneck.
- **Analogy: The Buffet**
    - `NotBuffered`: The chef brings you each piece of food one at a time as it's cooked.
    - `AutoBuffered` (Default): The chef brings out a full tray of food as it's ready.
    - `FullyBuffered`: The chef waits until the entire 5-course meal is cooked before bringing anything to the table.
- **Example:**
    
    ```csharp
    // I need the first result as fast as possible to update my UI, even if the total time is longer.
    var query = numbers
        .AsParallel()
        .WithMergeOptions(ParallelMergeOptions.NotBuffered)
        .Where(n => IsPrime(n));
    
    // This foreach loop will start receiving items almost instantly.
    foreach (var prime in query) { /* ... */ }
    
    ```
    

---

### 3. Aggregations, Cancellation, and Exceptions

- **Thread-Safe Aggregations:** PLINQ automatically handles aggregations like `.Sum()`, `.Count()`, and `.Average()` in a thread-safe way. It uses the same "thread-local storage" pattern we discussed for `Parallel.ForEach` internally. You do not need to use `lock`.
    
    ```csharp
    long sum = hugeArray.AsParallel().Sum(); // This is safe and highly optimized.
    
    ```
    
- **Cancellation:** PLINQ respects C# cancellation tokens. You use the `.WithCancellation(token)` method.
    
    ```csharp
    var cts = new CancellationTokenSource();
    var query = numbers.AsParallel().WithCancellation(cts.Token).Select(n => HeavyWork(n));
    // ...
    // Later, call cts.Cancel() to stop the query.
    // The query will throw an OperationCanceledException.
    
    ```
    
- **Exception Handling:** If one or more threads throw an exception, PLINQ will wrap all of them into a single `AggregateException`. You must be prepared to catch this type and inspect its `.InnerExceptions` collection.
    
    ```csharp
    try
    {
        var result = data.AsParallel().Select(d => RiskyOperation(d)).ToList();
    }
    catch (AggregateException ae)
    {
        foreach (var ex in ae.InnerExceptions)
        {
            Console.WriteLine($"An exception occurred: {ex.Message}");
        }
    }
    
    ```
    

# Use Case

Excellent question. This scenario perfectly highlights the difference between handling CPU-bound work and I/O-bound work within a parallel query, and it demonstrates the need for concurrent collections.

Let's break it down into three parts:

1. Calling a **Synchronous** method (CPU-Bound).
2. The **Anti-Pattern**: Calling an **Asynchronous** method incorrectly.
3. The **Correct Pattern**: Collecting results into **Concurrent Data Structures**.

### The Scenario

We have a sequence of numbers from 1 to 20,000. We want to use PLINQ to find all the numbers that match a specific criteria and classify them as Odd or Even.

- **Synchronous Criteria (CPU-Bound):** The number is prime. This is a heavy calculation.
- **Asynchronous Criteria (I/O-Bound Simulation):** The number is "approved" by a slow external service.

---

### 1. Calling a Synchronous (CPU-Bound) Method

This is the ideal use case for PLINQ. The synchronous method is executed in parallel across multiple threads.

```csharp
// --- The CPU-Bound Logic ---
// A slow, inefficient primality test to simulate heavy CPU work.
public static bool IsPrime(int n)
{
    if (n <= 1) return false;
    for (int i = 2; i * i <= n; i++)
    {
        if (n % i == 0) return false;
    }
    return true;
}

// --- The PLINQ Query ---
public void FindPrimeNumbers()
{
    var numbers = Enumerable.Range(1, 20_000);

    // This is the correct, simple way to call a synchronous method.
    var primeNumbers = numbers
        .AsParallel() // Distribute the work across CPU cores.
        .Where(n => IsPrime(n)) // The IsPrime function runs on multiple threads.
        .ToList(); // Materialize the results.

    Console.WriteLine($"Found {primeNumbers.Count} prime numbers.");
}

```

**How it works:** PLINQ's partitioner splits the 20,000 numbers into chunks. Each thread gets a chunk and runs a simple loop, calling `IsPrime()` for each number in its chunk. This is highly efficient.

---

### 2. Calling an Asynchronous Method (The Anti-Pattern and The Problem)

Now, let's try to call an async method. PLINQ's `Where` operator expects a `Func<T, bool>`, not a `Func<T, Task<bool>>`. You cannot use `await` inside it.

The only way to make it fit is to block the thread, which leads to the **thread starvation** problem we discussed earlier.

```csharp
// --- The I/O-Bound Logic (Simulation) ---
// Simulates calling a slow web service to validate a number.
public static async Task<bool> IsApprovedByServiceAsync(int n)
{
    await Task.Delay(10); // Simulate network latency.
    return n % 2 == 0; // The service approves even numbers.
}

// --- The PLINQ ANTI-PATTERN (Incorrect Usage) ---
public void FindApprovedNumbersTheWrongWay()
{
    var numbers = Enumerable.Range(1, 20_000);

    try
    {
        // DANGER: You are forced to block with .Result or .Wait()
        var approvedNumbers = numbers
            .AsParallel()
            .Where(n => IsApprovedByServiceAsync(n).Result) // This BLOCKS the parallel thread!
            .ToList();

        // The result will be correct, but the performance will be AWFUL.
        // The ThreadPool will become starved and will slowly inject new threads.
    }
    catch (AggregateException ae)
    {
        // This will likely wrap a TaskCanceledException if the service times out.
        Console.WriteLine(ae.InnerException.Message);
    }
}

```

**Conclusion:** You should **not** use PLINQ for I/O-bound operations. PLINQ is for parallel CPU work. For I/O concurrency, `Task.WhenAll` with a `SemaphoreSlim` is the right tool.

---

### 3. Using Concurrent Data Structures to Collect Results

Now, let's solve the original problem: "Find all 4-digit numbers and classify them as odd or even."

If we try to add to a regular `List<T>` from multiple threads, our program will crash or lose data.

**The Mistake (Unsafe Code):**

```csharp
var odds = new List<int>();
var evens = new List<int>();
numbers.AsParallel().ForAll(n => {
    if (n % 2 == 0) evens.Add(n); // CRASH! Two threads might call Add() at the same time.
    else odds.Add(n);
});

```

**The Solution:** Use collections from the `System.Collections.Concurrent` namespace. `ConcurrentBag<T>` is often the easiest choice for unordered collections.

### The Correct Implementation with Concurrent Collections

Here is the full, correct solution combining PLINQ with concurrent data structures.

```csharp
using System.Collections.Concurrent;

public void ClassifyNumbers()
{
    var numbers = Enumerable.Range(1, 20_000);

    // 1. Create thread-safe collections to store the results.
    var fourDigitOdds = new ConcurrentBag<int>();
    var fourDigitEvens = new ConcurrentBag<int>();

    // 2. The PLINQ query finds the 4-digit numbers.
    var fourDigitNumbersQuery = numbers
        .AsParallel()
        .Where(n => n >= 1000 && n <= 9999);

    // 3. Use ForAll to process the results and add to the concurrent collections.
    // ForAll is a terminal operator that executes the query.
    fourDigitNumbersQuery.ForAll(n =>
    {
        // This block runs in parallel on multiple threads.
        if (n % 2 == 0)
        {
            // ConcurrentBag.Add() is thread-safe. No lock needed.
            fourDigitEvens.Add(n);
        }
        else
        {
            fourDigitOdds.Add(n);
        }
    });

    Console.WriteLine("Classification complete.");
    Console.WriteLine($"Found {fourDigitEvens.Count} even 4-digit numbers.");
    Console.WriteLine($"Found {fourDigitOdds.Count} odd 4-digit numbers.");

    // Note: The contents of a ConcurrentBag are unordered.
    // If you need to display them in order, you must sort them first.
    var orderedEvens = fourDigitEvens.OrderBy(x => x).Take(5);
    Console.WriteLine($"First 5 evens (sorted): {string.Join(", ", orderedEvens)}");
}

```

### Why `.ForAll()`?

- `.ForAll(action)` is a special PLINQ operator designed for executing an action for each item in the parallel query. It's more efficient than materializing the list with `.ToList()` and then using `Parallel.ForEach`, because it can perform the action as the results are produced without an intermediate list. It's perfect for populating concurrent collections.

### Summary of Rules

1. **Use PLINQ for CPU-Bound logic.** Call synchronous methods directly in operators like `Where` and `Select`.
2. **NEVER call `.Result` or `.Wait()` on an async method inside a PLINQ query.** This will block the thread pool and destroy performance.
3. **Use Concurrent Collections (`ConcurrentBag`, `ConcurrentDictionary`, etc.)** when your PLINQ query needs to add results to a shared collection from multiple threads.
4. **Use `.ForAll()`** as a convenient and efficient way to execute a side-effect (like adding to a collection) for each element of a parallel query.

# Notes

### Part 1: The Direct Answer - Is PLINQ Blocking?

The answer is nuanced but can be summarized like this:

**PLINQ itself is based on *deferred execution* (non-blocking), but the moment you ask for the results, it becomes a *blocking* call.**

Let's break that down into its two distinct phases.

### Phase 1: Query Definition (Non-Blocking)

When you write the PLINQ query, you are **not executing anything**. You are simply building a "query plan" or a "recipe" for execution. This phase is instantaneous and non-blocking.

```csharp
// --- THIS ENTIRE BLOCK IS NON-BLOCKING. IT RUNS INSTANTLY. ---

// We are just building a recipe. No numbers are being checked yet.
var myPlinqQuery = Enumerable.Range(1, 10_000_000)
    .AsParallel()
    .WithDegreeOfParallelism(4)
    .Where(n => n % 3 == 0)
    .Select(n => n.ToString());

// The 'myPlinqQuery' variable holds the execution plan, not the results.
// No threads have been used yet.
Console.WriteLine("Query has been defined.");

```

### Phase 2: Query Execution / Materialization (Blocking)

The moment you try to consume the results of the query, the PLINQ engine kicks in, partitions the data, spins up tasks on the ThreadPool, and **blocks your calling thread** until the entire parallel operation is complete.

This is called "materializing" the query. The most common materialization triggers are:

- `.ToList()`, `.ToArray()`, `.ToDictionary()`
- `.Count()`, `.Sum()`, `.Average()`
- Using the query in a `foreach` loop.

```csharp
// The recipe has been defined above...

Console.WriteLine("Now materializing the query... THIS WILL BLOCK.");

// THIS IS THE BLOCKING CALL. The main thread will pause here until all
// 10 million numbers have been processed in parallel across 4 threads.
List<string> results = myPlinqQuery.ToList();

// This line will only execute AFTER the parallel work is 100% finished.
Console.WriteLine($"Query complete. Found {results.Count} numbers.");

```

**Why is it blocking by design?**
PLINQ's purpose is **CPU-Bound Parallelism**. Its goal is to return a final, computed result (like a list or a sum) to the caller as fast as possible by using all available CPU power. The caller *needs* that result to proceed, so it makes sense for the caller to wait for it.

---

### Part 2: Do We Need `async` and `await`?

**No, you do not use `async` and `await` directly on a PLINQ query.**

`async/await` is a model for **Concurrency**, primarily for non-blocking I/O operations. Its core feature is returning a `Task` or `Task<T>` that represents a "promise" of future completion, allowing the thread to be released.

PLINQ does **not** return a `Task<T>`. It returns a `ParallelQuery<T>`, which is not "awaitable."

The two models solve different problems:

- **PLINQ:** "Use all my CPU cores *right now* to finish this heavy calculation. I will wait for the answer." (Blocking Parallelism)
- **`async/await`:** "Start this network/file operation, and *let me know when it's done*. I have other things to do in the meantime." (Non-Blocking Concurrency)

---

### Part 3: The Solution - How to Make a PLINQ Query Asynchronous

So what if you have a UI application and you need to run a heavy, 10-second PLINQ query without freezing the interface?

You combine the two models: **You wrap the blocking PLINQ call inside a `Task.Run`** to make the *entire operation* asynchronous from the caller's perspective.

This is the standard and correct pattern.

```csharp
// This method is called from a UI button click, for example.
// It returns a Task, so the UI thread is not blocked.
public async Task<List<int>> GetPrimeNumbersAsync()
{
    Console.WriteLine("Offloading the heavy PLINQ query to a background thread...");

    // 1. We await a Task.Run. This makes the GetPrimeNumbersAsync method
    //    asynchronous and non-blocking FOR THE CALLER (the UI).
    List<int> primeNumbers = await Task.Run(() =>
    {
        // 2. INSIDE the Task.Run, we execute our blocking PLINQ query.
        //    This will block the BACKGROUND THREAD it is running on,
        //    which is perfectly fine. That's its job.
        return Enumerable.Range(1, 2_000_000)
            .AsParallel()
            .Where(n => IsPrime(n)) // Heavy CPU work
            .ToList(); // The blocking materialization happens here.
    });

    Console.WriteLine("The background PLINQ operation is complete.");
    return primeNumbers;
}

// Helper for heavy work
private bool IsPrime(int n)
{
    if (n <= 1) return false;
    for (int i = 2; i * i <= n; i++)
    {
        if (n % i == 0) return false;
    }
    return true;
}

```

### Summary Table

| Characteristic | PLINQ (`.AsParallel`) | `async`/`await` |
| --- | --- | --- |
| **Primary Goal** | **CPU-Bound Parallelism** (Speed up calculations) | **I/O-Bound Concurrency** (Release threads while waiting) |
| **Execution Model** | **Blocking** (on materialization) | **Non-Blocking** (yields the thread) |
| **Return Type** | `ParallelQuery<T>` (not awaitable) | `Task<T>` (awaitable) |
| **Typical Use Case** | Heavy math, image processing, data analysis. | Network requests, database calls, file I/O. |
| **How to Combine** | Wrap the blocking PLINQ call in `Task.Run` to make it awaitable. |  |