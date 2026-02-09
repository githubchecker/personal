# Binding Expressions and Patterns | Microsoft Learn

Of course. Let's start from a clean slate and build a complete, definitive guide on Azure Functions Binding Expressions from first principles. I will clearly explain what they are, how they work, and most importantly, specify what is supported in the modern **.NET Isolated Worker model**, which is the recommended standard for all new C#/.NET function apps.

This will be the final, correct answer to resolve any previous confusion.

---

### Part 1: What is a Binding Expression? The Core Concept

A **binding expression** is a special text pattern that you place inside your binding configuration (in attributes for C# or in `function.json`). It acts as a **placeholder**. The Azure Functions Host runtime sees this placeholder and replaces it with a real value *before* the binding is used.

**The best analogy is a "mail merge" template:**

- You write a letter template: `Hello {FirstName}, your order number is {OrderNumber}.`
- The system takes data (e.g., from a spreadsheet).
- It merges the data into the template to produce the final text: `Hello John, your order number is 12345.`

Binding expressions work exactly like this. You define a template in your binding path (e.g., `invoices/{OrderNumber}`), and the Functions Host merges in the actual data at runtime to figure out the final path (e.g., `invoices/12345`).

### Part 2: Who Processes These Expressions? The Host vs. The Worker

This is the most critical concept for understanding the differences between the old **In-Process** model and the modern **Isolated Worker** model.

- **In-Process Model (Legacy):** Your C# code and the Azure Functions Host run in the **same process**. They are tightly coupled and share memory. This allows the Host to perform complex "magic" where it can read trigger data, resolve other bindings based on that data, and then hand everything, fully prepared, to your function code.
- **Isolated Worker Model (Modern):** Your C# code runs in a **separate process** from the Host. They are decoupled and communicate over a defined gRPC channel. The Host's job is simpler: it gathers the trigger data, packages it into a message, and sends it to your worker process. **This decoupling means the Host cannot perform the same complex, multi-step magic.** The responsibility for dynamic logic shifts more to your code.

Now, let's go through each type of binding expression and clarify its support in the **.NET Isolated Worker model**.

---

### Part 3: A Detailed Guide to Binding Expressions in the .NET Isolated Worker

### 1. App Settings

This expression uses **percent signs (`%...%`)** to pull a value from your application settings (from `local.settings.json` locally, or Configuration on Azure).

- **Isolated Worker Support:** ✅ **Fully Supported.**
- **Why it Works:** This is resolved by the Host *before* any trigger is processed. The Host reads its own configuration to determine which queue to listen on or which container path to use. This is independent of your worker code.

**C# Isolated Worker Example:**

```csharp
// local.settings.json
{
  "Values": {
    "ORDERS_QUEUE_NAME": "production-orders"
  }
}

// Function code
[Function("ProcessOrders")]
public void Run([QueueTrigger("%ORDERS_QUEUE_NAME%")] string myQueueItem, FunctionContext context)
{
    var logger = context.GetLogger("ProcessOrders");
    logger.LogInformation("Processing order: {order}", myQueueItem);
}

```

### 2. Blob Trigger Path Patterns

This creates a binding expression from part of a Blob Trigger's file path using **curly braces (`{...}`)**.

- **Isolated Worker Support:** ✅ **Fully Supported.**
- **Why it Works:** The triggering event *is* the blob itself. The Host knows the full path of the blob that triggered the function. It can parse this path (e.g., `samples-workitems/MyFile.csv`), extract the value for `{name}`, and pass that value along with the blob's content to your worker function.

**C# Isolated Worker Example:**

```csharp
[Function("ResizeImage")]
public void Run(
    [BlobTrigger("images-raw/{fileName}")] byte[] inputBlob,
    string fileName, // The value for {fileName} is passed here
    FunctionContext context)
{
    var logger = context.GetLogger("ResizeImage");
    logger.LogInformation("Resizing image named: {name}", fileName);
}

```

### 3. Trigger Metadata

This refers to binding to trigger-specific properties that aren't the primary data payload (e.g., a queue message's `DequeueCount`).

- **Isolated Worker Support:** ⚠️ **Supported, but the implementation is different.**
- **How it Works:** In the Isolated model, you **cannot** bind metadata to separate method parameters. Instead, the entire trigger payload, *including its metadata*, is delivered as a single, strongly-typed object.

**C# Isolated Worker Example:**

```csharp
// You must define a class to receive the trigger data and metadata.
public class MyQueueMessage
{
    public string MessageText { get; set; } // The actual queue message content
    public int DequeueCount { get; set; }
    public string Id { get; set; }
}

[Function("ProcessQueueWithMetadata")]
public void Run([QueueTrigger("my-queue")] MyQueueMessage myQueueItem, FunctionContext context)
{
    var logger = context.GetLogger("ProcessQueueWithMetadata");
    // Access metadata via the properties of the input object
    logger.LogInformation("Message ID: {id}", myQueueItem.Id);
    logger.LogInformation("Dequeue Count: {count}", myQueueItem.DequeueCount);
    logger.LogInformation("Content: {text}", myQueueItem.MessageText);
}

```

### 4. JSON Payloads & Dot Notation

This refers to creating binding expressions from properties inside a trigger's JSON payload (e.g., `{BlobName}` or `{BlobName.FileName}`).

- **Isolated Worker Support:** ❌ **NOT SUPPORTED.**
- **Why it's Not Supported:** This is the most significant difference. In the Isolated model, the Host sends the trigger payload to your worker but does **not** pre-process the body to resolve other bindings declaratively. This complex, multi-step "read body -> resolve path -> fetch data -> call function" logic is a feature of the tightly-coupled In-Process model only.

**The Correct Isolated Worker Pattern: Imperative Binding**
You must handle this logic inside your function code by injecting an SDK client.

**C# Isolated Worker Example (The Correct Alternative):**

```csharp
public class HttpTriggerPayload
{
    public string ContainerName { get; set; }
    public string BlobName { get; set; }
}

public class ReadBlobFunction
{
    private readonly BlobServiceClient _blobServiceClient;

    // Inject the Blob client via DI in your Program.cs
    public ReadBlobFunction(BlobServiceClient blobServiceClient)
    {
        _blobServiceClient = blobServiceClient;
    }

    [Function("ReadBlob")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post")] HttpTriggerPayload payload)
    {
        // Declarative binding like [Blob("{ContainerName}/{BlobName}")] is NOT possible.
        // You MUST write the code to get the blob yourself.

        try
        {
            var containerClient = _blobServiceClient.GetBlobContainerClient(payload.ContainerName);
            var blobClient = containerClient.GetBlobClient(payload.BlobName);

            var blobContents = await blobClient.DownloadContentAsync();
            return new OkObjectResult(blobContents.Value.Content.ToString());
        }
        catch (RequestFailedException ex) when (ex.Status == 404)
        {
            return new NotFoundObjectResult("Blob not found.");
        }
    }
}
```

### **5. Special Host-Generated Expressions**

These are expressions resolved by the Host that don't depend on trigger data.

- `{rand-guid}`: Creates a new GUID.
- `DateTime`: Resolves to the current UTC time.
- **Isolated Worker Support:** ✅ **Fully Supported.**
- **Why it Works:** The Host can generate these values itself without needing any input from the trigger or your worker code.

**C# Isolated Worker Example:**

```csharp
public class MyOutputType
{
    [BlobOutput("my-output-container/{DateTime}.txt")]
    public string BlobContent { get; set; }

    public HttpResponseData HttpResponse { get; set; }
}

[Function("CreateTimeStampedBlob")]
public MyOutputType Run([HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequestData req)
{
    // The {DateTime} expression is handled by the host.
    // Your code just needs to return a value for the output binding.
    return new MyOutputType
    {
        BlobContent = $"Request received at {DateTime.UtcNow}",
        HttpResponse = req.CreateResponse(HttpStatusCode.OK)
    };
}
```

---

### The Final Summary & The Golden Rule

| Binding Expression / Pattern | In-Process | Isolated (Out-of-Process) | Key Difference / Notes |
| --- | --- | --- | --- |
| **App Settings (`%...%`)** | ✅ | ✅ | Works identically. Host-level feature. |
| **Blob Trigger Patterns (`{name}`)** | ✅ | ✅ | Works identically. Host-level feature. |
| **Trigger Metadata** | ✅ | ⚠️ | **Different implementation.** In-process binds to method parameters. Isolated binds to properties of a trigger model class. |
| **JSON Payload (`{JsonProp}`)** | ✅ | ❌ | **Not supported in Isolated.** This is a major difference. You must use imperative code in the Isolated model. |
| **Dot Notation (`{Prop.Sub}`)** | ✅ | ❌ | Not supported in Isolated for the same reasons. |
| **Special (`{rand-guid}`, `{DateTime}`)** | ✅ | ✅ | Works identically. Host-level feature. |
| **Runtime / Imperative Binding** | ✅ | ✅ | Possible in both, but **required for dynamic logic** in the Isolated model. |

**The Golden Rule for the .NET Isolated Worker Model:**
If your binding logic depends on the *content* of the trigger payload, you must implement that logic **imperatively inside your function code** using the appropriate Azure SDK. Declarative attribute bindings are for simpler, static, or trigger-path-derived scenarios.