# Prallel.ForEach

Of course. This is one of the most important and nuanced topics in the TPL (Task Parallel Library). Let's do a comprehensive deep dive into `Parallel.For` and `Parallel.ForEach`, focusing on their parameters and the critical challenge of using them with asynchronous operations.

---

### Part 1: The Core Purpose (CPU-Bound Work)

`Parallel.For` and `Parallel.ForEach` are high-performance tools designed for one primary purpose: **CPU-bound parallelism**. They excel at taking a collection of items and processing them across all your available CPU cores simultaneously.

- **Key Behavior:** They are **blocking** methods. The thread that calls `Parallel.ForEach` will stop and wait until every single item in the collection has been processed before moving on to the next line of code.

**Basic Syntax Example (CPU-Bound):**

```csharp
// Scenario: A list of file paths for images we need to apply a heavy filter to.
List<string> imagePaths = GetPaths();

// This line will not complete until ALL images have been filtered.
Parallel.ForEach(imagePaths, path =>
{
    // This is a synchronous, CPU-heavy operation.
    Bitmap image = LoadImage(path);
    ApplySepiaFilter(image); // This function maxes out a CPU core.
    SaveImage(image);
    Console.WriteLine($"Processed {path} on thread {Thread.CurrentThread.ManagedThreadId}.");
});

Console.WriteLine("All filtering complete."); // This line runs only after the loop is done.

```

---

### Part 2: Deep Dive into the Overloads and Parameters

The simple syntax is just the beginning. The real power comes from the advanced overloads.

### 1. `ParallelOptions`: Controlling the Loop's Behavior

You can pass a `ParallelOptions` object to control the execution.

```csharp
var options = new ParallelOptions
{
    // A. The most important option: Limit how many threads can work at once.
    // Useful for not overwhelming a system with 128 cores, or for throttling.
    MaxDegreeOfParallelism = 4,

    // B. Link the loop to a cancellation token.
    CancellationToken = cts.Token
};

try
{
    Parallel.ForEach(items, options, item =>
    {
        // If cancellation is requested, this will throw an OperationCanceledException.
        options.CancellationToken.ThrowIfCancellationRequested();

        DoWork(item);
    });
}
catch (OperationCanceledException)
{
    Console.WriteLine("Loop was cancelled!");
}

```

### 2. `ParallelLoopState`: Interacting with the Loop from Inside

The body of the loop can accept a second parameter, a `ParallelLoopState` object. This allows an iteration to communicate with the overall loop.

- **`state.Break()`**: "I have found a valid result. All iterations that are *currently running* should finish, but no *new* iterations should start for indices higher than mine." This is an optimization.
- **`state.Stop()`**: "Shut everything down *now*. No new iterations should start, and the loop should terminate as soon as possible."

```csharp
// Scenario: Find the first file in a huge list that contains a specific keyword.
string firstFileWithKeyword = null;

Parallel.ForEach(allFilePaths, (path, state) =>
{
    string content = File.ReadAllText(path);
    if (content.Contains("SecretKeyword"))
    {
        firstFileWithKeyword = path;

        // We found it! Tell the loop to stop launching new file reads.
        state.Stop();
    }
});

```

### 3. Thread-Local Variables: The Ultimate Performance Boost

This is the most complex but most powerful overload. It's used to avoid the high cost of **locking**. If multiple threads need to update a shared variable (like a sum or a list), they would normally have to use `lock`, which causes them to wait for each other.

This overload lets each thread have its own **private, local copy** of a variable. They work on their private copy, and only at the very end is the private result merged back into the shared result.

- **Analogy:** Instead of 8 workers sharing one toolbox and waiting for the hammer (`lock`), each worker gets their own private toolbox. They only come together at the end to put their finished parts on the main assembly line.

The overload has three main parts:

1. **`localInit`**: A function to create the thread's private variable (`() => 0` to start a sum).
2. **`body`**: The main loop body. It receives the item, the loop state, and the private variable. It returns the *updated* private variable.
3. **`localFinally`**: A function that is called once per thread when it's done. This is where you merge the private result into the final, shared variable.

```csharp
long totalSize = 0;
var filePaths = Directory.GetFiles(@"C:\\Windows\\System32");

Parallel.ForEach(
    filePaths,
    () => 0L, // 1. localInit: Each thread gets its own private subtotal, initialized to 0.
    (path, state, subtotal) => // 2. body: 'subtotal' is the private variable for THIS thread.
    {
        long fileSize = new FileInfo(path).Length;
        return subtotal + fileSize; // Return the updated private subtotal.
    },
    (finalSubtotal) => Interlocked.Add(ref totalSize, finalSubtotal) // 3. localFinally: Safely add the thread's final subtotal to the shared total.
);

Console.WriteLine($"Total size: {totalSize / 1_000_000.0:N2} MB");

```

---

### Part 3: The Critical Trap - Asynchronous Functions

This is where your core question lies. What happens when you try to call an `async` method?

**THE RULE: `Parallel.For` and `Parallel.ForEach` DO NOT SUPPORT `await` PROPERLY.**

### Why? The `async void` Problem

The delegate (the lambda) that `Parallel.ForEach` expects has a signature of `Action<T>`, meaning it's a method that accepts a `T` and returns `void`.

When the C# compiler sees you write an `async` lambda where a `void` is expected, it compiles it into an **`async void`** method.

**`async void` means "fire-and-forget."**

When `Parallel.ForEach` calls your `async` lambda, the `await` inside it will yield control, but `Parallel.ForEach` **has no `Task` object to wait for**. It thinks the `void`-returning method is complete, and immediately moves to the next item. The loop itself might complete and exit while all your async operations are still running in the background.

```csharp
public void AsyncVoidTrap()
{
    var urls = new[] { "google.com", "microsoft.com", "amazon.com" };

    Console.WriteLine("Starting loop...");
    // This loop will finish and exit in milliseconds, before any downloads complete.
    Parallel.ForEach(urls, async url =>
    {
        Console.WriteLine($"Starting download for {url}");
        // 'await' returns control to Parallel.ForEach, which thinks this iteration is done.
        var data = await new HttpClient().GetStringAsync("http://" + url);
        Console.WriteLine($"Finished download for {url}"); // This appears much later.
    });

    // THIS LINE EXECUTES IMMEDIATELY.
    Console.WriteLine("Parallel.ForEach has completed. (But the downloads have not!)");
}

```

---

### Part 4: The Solution - `Parallel.ForEachAsync` (.NET 6+)

Microsoft recognized this was a major pain point. In .NET 6, they introduced `Parallel.ForEachAsync`, which is **specifically designed for I/O-bound concurrency with throttling**.

**Where to put `async`?** Right on the main method call and on the lambda!

It solves all the problems of the old approach:

- Its delegate signature is `Func<T, CancellationToken, ValueTask>`, which is **awaitable**.
- It is itself an `async` method, so you `await` the entire loop.
- It has built-in throttling via `ParallelOptions.MaxDegreeOfParallelism`.

```csharp
// THE CORRECT WAY FOR I/O CONCURRENCY
public async Task DownloadUrlsCorrectlyAsync()
{
    var urls = new[] { "google.com", "microsoft.com", "amazon.com" };

    Console.WriteLine("Starting async loop...");
    var options = new ParallelOptions
    {
        MaxDegreeOfParallelism = 2 // Throttle to 2 concurrent downloads.
    };

    // 1. You 'await' the entire loop.
    await Parallel.ForEachAsync(urls, options, async (url, token) => // 2. The lambda is async.
    {
        Console.WriteLine($"Starting download for {url}");
        var data = await new HttpClient().GetStringAsync("http://" + url, token);
        Console.WriteLine($"Finished download for {url}");
    });

    // 3. This line now correctly waits until all async operations are done.
    Console.WriteLine("Parallel.ForEachAsync has completed, and all downloads are finished.");
}

```

### Summary Table

| Method | `Parallel.ForEach` | `Parallel.ForEachAsync` |
| --- | --- | --- |
| **Primary Use Case** | **CPU-Bound** Parallelism | **I/O-Bound** Concurrency |
| **`await` Support** | **NO.** (Leads to `async void` fire-and-forget bugs) | **YES.** First-class support for `async`/`await`. |
| **Behavior** | **Synchronously Blocks** calling thread. | **Asynchronously Waits.** Returns a `Task` to be awaited. |
| **Throttling** | `MaxDegreeOfParallelism` limits running threads. | `MaxDegreeOfParallelism` limits concurrent async operations. |
| **.NET Version** | All versions | .NET 6 and newer |

# Thread-Local Variables Example

### The Problem Scenario

Imagine you have a directory with thousands of log files. You need to process them in parallel to find:

1. The **total size** of all `.log` files.
2. The **number of "ERROR" lines** found across all files.
3. A **list of filenames that are corrupted** (cannot be read).

If we used a simple `lock` inside the loop for all three variables, the threads would constantly be waiting on each other, defeating the purpose of parallelism. This is the perfect use case for thread-local state.

---

### Understanding the Parameters and Variables

First, let's address your questions:

- **How to pass multiple variables?**
You cannot pass multiple *independent* variables directly into the lambda's parameters. The `(path, state, subtotal)` signature is fixed. The solution is to have the thread-local variable be a **custom class or a `Tuple`** that holds all the data a thread needs to track.
- **What is the `state` variable (`ParallelLoopState`)?**
It's a "remote control" for the loop. You don't pass data *with* it; you use it to send signals *to* the loop, like `state.Stop()` or `state.Break()`. We won't use it in this example to keep the focus on the data, but it's important to know it's for control, not data.
- **Is it going to capture outer variables?**
Yes, the lambdas can still "see" and capture variables from the outer scope (like `allFilePaths`). This is how the final lambda (`localFinally`) can access the shared totals at the end. However, the goal of this pattern is to **avoid writing to shared outer variables inside the main `body` lambda**.

---

### The Refined Example with a Custom State Class

Here is the complete, documented code.

### Step 1: Create a custom class to hold the thread's private state.

This is the key to tracking multiple values. Each thread gets its own instance of this class.

```csharp
// Each thread will have its own private instance of this class.
public class ThreadLocalState
{
    public long SubtotalSize { get; set; } = 0L;
    public int ErrorCount { get; set; } = 0;
    public List<string> CorruptedFiles { get; set; } = new List<string>();
}

```

### Step 2: Set up the final, shared variables.

These are the variables in the main scope that will hold the final aggregated results.

```csharp
// These are the final, shared results that all threads will merge into at the end.
long finalTotalSize = 0;
int finalErrorCount = 0;
var finalCorruptedFiles = new ConcurrentBag<string>(); // Use a thread-safe collection for the final list.

```

### Step 3: Implement the `Parallel.ForEach` loop with the custom state.

```csharp
// Assume 'allFilePaths' is a List<string> of file paths.
var allFilePaths = Directory.GetFiles(@"C:\\Your\\Log\\Directory", "*.log");

Parallel.ForEach<string, ThreadLocalState>(
    // Argument 1: The data source to iterate over.
    allFilePaths,

    // Argument 2: localInit - This function runs ONCE PER THREAD.
    // It creates and returns a fresh, private state object for that thread.
    () => {
        // Each thread gets its own new toolbox.
        Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} created its local state.");
        return new ThreadLocalState();
    },

    // Argument 3: body - This function runs for every single file path.
    // It receives the current file path, the loop's control state, and THIS thread's private state object.
    (path, loopState, threadState) => {
        try
        {
            // Read the file and update the thread's PRIVATE state.
            // There is NO locking here because no other thread can access 'threadState'.
            var fileInfo = new FileInfo(path);
            threadState.SubtotalSize += fileInfo.Length;

            string[] lines = File.ReadAllLines(path);
            foreach (var line in lines)
            {
                if (line.Contains("ERROR"))
                {
                    threadState.ErrorCount++;
                }
            }
        }
        catch (IOException ex)
        {
            // If a file is corrupted, add it to the thread's PRIVATE list.
            threadState.CorruptedFiles.Add(path);
        }

        // IMPORTANT: You must return the state object so it can be passed to the next iteration for this thread.
        return threadState;
    },

    // Argument 4: localFinally - This function runs ONCE PER THREAD after it has finished all its work.
    // It receives the thread's final, completed private state.
    (finalThreadState) => {
        Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} is merging its final results.");

        // Now we need to safely merge the thread's private results into the shared, final results.
        // Use Interlocked for simple numeric types for thread safety and performance.
        Interlocked.Add(ref finalTotalSize, finalThreadState.SubtotalSize);
        Interlocked.Add(ref finalErrorCount, finalThreadState.ErrorCount);

        // For the list of files, add them to the thread-safe ConcurrentBag.
        foreach (var file in finalThreadState.CorruptedFiles)
        {
            finalCorruptedFiles.Add(file);
        }
    }
);

```

### Step 4: Display the final results.

```csharp
Console.WriteLine("\\n--- Aggregation Complete ---");
Console.WriteLine($"Total size of log files: {finalTotalSize / 1_048_576.0:N2} MB");
Console.WriteLine($"Total 'ERROR' lines found: {finalErrorCount}");
Console.WriteLine($"Corrupted files found: {finalCorruptedFiles.Count}");
foreach (var file in finalCorruptedFiles)
{
    Console.WriteLine($"  - {file}");
}

```

### Summary of the Flow

1. **Initialization (`localInit`)**: Before the loop really starts, `Parallel.ForEach` creates a few tasks. For each task/thread, it calls the `localInit` function. If it uses 4 threads, it creates 4 `ThreadLocalState` objects.
2. **Processing (`body`)**: The Partitioner hands out file paths to the threads. Each thread processes its assigned file path and updates **its own private `ThreadLocalState` object**. This is fast because there's no waiting or locking.
3. **Finalization (`localFinally`)**: Once a thread has no more file paths to process, the `localFinally` action is called. This is the **only time** that thread needs to interact with the shared `final...` variables. It safely adds its private totals to the shared ones.
4. **Completion**: The `Parallel.ForEach` call completes only after all threads have finished their work and merged their results.