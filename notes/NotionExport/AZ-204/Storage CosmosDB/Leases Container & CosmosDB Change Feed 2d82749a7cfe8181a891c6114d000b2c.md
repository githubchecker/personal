# Leases Container & CosmosDB Change Feed

---

### **1. NOVICE: The Concepts & When to Use**

### **What is the Change Feed?**

Think of the Cosmos DB Change Feed as a **Tape Recorder** attached to your database container.

- Every time you Insert or Update a document, the Change Feed records that item.
- It is sorted by time (mostly).
- **Limitation:** By default, it captures the *latest* version of the document. It does not show intermediate updates (if you update a doc 5 times in 1 second, you might only get the final state) and it does not capture *Deletes* (unless you use Soft Deletes or the new "Full Fidelity" preview mode).

### **What is the Lease Container?**

Think of the Lease Container as a **collection of Bookmarks**.

- The Change Feed is the book.
- Your Azure Function is the reader.
- If your Function crashes or restarts, it needs to know where it stopped reading. It looks at the **Lease Container** (Bookmark) to resume exactly where it left off.

### **When to use this pattern?**

1. **Event Sourcing/Triggering:** A user is created in Cosmos DB $\to$ Trigger Function $\to$ Send Welcome Email.
2. **Materialized Views (CQRS):** Data is saved in a "Write-Optimized" heavy JSON format $\to$ Trigger Function $\to$ flattens it and saves it to SQL for reporting.
3. **Search Sync:** Data saved in Cosmos $\to$ Trigger Function $\to$ Pushes data to Azure AI Search.
4. **Real-time Stream Processing:** Moving data from Cosmos to Event Hubs.

### Where the Lease is Stored & What It Looks Like

**Where is it stored?**
The lease is stored in a **Standard Cosmos DB Container**.
There is nothing "magical" about it. It is just a JSON document sitting in a container (usually named `leases`) that you create alongside your actual data container.

**What does it look like? (The Anatomy)**
If you open the `leases` container in Azure Portal > Data Explorer, you will see documents that look like this.

Each document represents **ONE Physical Partition** of your source data.

```json
{
    "id": "1",                    // The ID of the Partition this lease tracks
    "Owner": "Host-Instance-A",   // Which Azure Function Instance is currently locking this?
    "ContinuationToken": "\\\\"95\\\\"", // THE BOOKMARK. The Logical Sequence Number (LSN).
    "LeaseToken": "1",            // Links to Partition Range 1
    "timestamp": "2024-02-02T10:00:00.0000000Z", // Last time the Bookmark moved
    "_etag": "\\\\"00000000-0000-0000...\\\\"",        // Concurrency control (prevents race conditions)

    // Expert Field: Prefix ensures multiple apps share the container safely
    "id": "email-worker-1"
}

```

**Key Fields Explained:**

1. **`Owner`**: This is how scaling works. If you have 2 Function Instances ("Host A" and "Host B"), some docs will say "Owner: Host A" and others "Owner: Host B".
2. **`ContinuationToken`**: This is the most critical field. It tells Cosmos: *"I have successfully processed everything up to Checkpoint #95. Next time, give me change #96."*
3. **`timestamp`**: This is the heartbeat. The Owner updates this every few seconds (usually 5s) even if there is no data. This proves the Owner is "Alive". If this timestamp gets old, another instance steals the lease.

---

### **2. INTERMEDIATE: The Architecture**

To use this, you need **two** containers:

1. **Monitored Container:** Where your data lives (e.g., `Users`).
2. **Lease Container:** Where the bookmarks live (e.g., `leases`).

**Crucial Concept:** The Leases container is not just one bookmark. It creates **one document per Physical Partition** of your monitored container.

If your `Users` container grows huge and Cosmos DB splits it into **5 Physical Partitions**, your `leases` container will automatically have **5 documents** inside it. Each document tracks the "Continuation Token" (checkpoint) for that specific partition.

---

### **3. ADVANCED: Azure Functions & Scaling (The Magic)**

This answers your specific question: *"How does Azure Function work with it if multiple copies are running?"*

The **Change Feed Processor (CFP)** is the engine running inside the Azure Function Trigger. It acts like a load balancer.

### **Scenario A: 1 Partition, 1 Function Instance**

- **Cosmos:** Has 1 Physical Partition.
- **Leases:** Has 1 Document.
- **Function:** Instance #1 wakes up. It grabs the lease (locks it). It writes "Owned by Instance #1" in the lease document.
- **Result:** Instance #1 processes all events.

### **Scenario B: 10 Partitions, 2 Function Instances (Scaling Out)**

- **Cosmos:** Has 10 Physical Partitions.
- **Leases:** Has 10 Documents (Lease Tokens 1 to 10).
- **Function:** Azure scales out to Instance #1 and Instance #2.
- **The Logic:**
    1. The Instances talk to the Lease Container.
    2. They negotiate.
    3. **Instance #1** locks Leases 1, 2, 3, 4, 5.
    4. **Instance #2** locks Leases 6, 7, 8, 9, 10.
- **Result:** They process in parallel. Instance #1 is unaware of Instance #2's data.

### **Scenario C: 10 Partitions, 20 Function Instances (Over-Scaling)**

- **Cosmos:** 10 Partitions.
- **Function:** You spun up 20 Servers.
- **The Logic:**
    1. Instances #1 through #10 grab one lease each.
    2. Instances #11 through #20 check the lease container, see that all 10 leases are locked by healthy instances.
    3. **Result:** Instances #11–20 sit idle (do nothing).
- **Expert Rule:** You cannot have more active Function Instances than you have Physical Partitions in Cosmos DB.

### **What happens if Instance #1 crashes? (Lease Stealing)**

1. Instance #1 dies.
2. It fails to update the "Renew Timestamp" on Leases 1-5.
3. Instance #2 (or a new Instance #3) scans the Lease container.
4. It sees Leases 1-5 have expired.
5. It **"Steals"** the lease (changes the Owner to itself) and starts processing from the last checkpoint.
6. **Self-Healing:** Zero data loss, slight delay in processing.

---

### **4. EXPERT: Specific Configurations**

### **1. The `LeaseCollectionPrefix`**

What if you want **two different functions** to listen to the *same* change feed?

- Function A: Sends Emails.
- Function B: Updates Analytics SQL.

You cannot let them fight over the same lease documents.

- **Solution:** You use the **same** `leases` container, but use a **Prefix**.
    - Function A uses prefix: `email-service-`
    - Function B uses prefix: `analytics-service-`
- **Result:** The Lease container will now have double the documents (e.g., `email-service-1`, `analytics-service-1`), tracking independent bookmarks for each function.

### **2. Handling Lag (The Estimator)**

In high-scale systems, data comes in fast. How do you know if your Function is keeping up or falling behind?

- You don't look at CPU.
- You look at **Estimator Lag**. This calculates: `(Latest LSN in Cosmos) - (LSN in Lease Document)`.
- If this number grows, you need more Physical Partitions (to allow more Function Instances to run in parallel).

### **3. StartFromBeginning**

- **Default:** `false`. The function only processes changes that happen *after* the Function starts.
- **True:** When the Lease is created for the *first time*, it starts reading from the very beginning of time (History Replay).
    - *Note:* Once a lease exists, this setting is ignored. To replay again, you must physically delete the documents in the `leases` container.

---

### **Code Snippet: The Top-Notch Setup**

Here is how an Expert configures the Azure Function Trigger.

```csharp
public class UserChangesFunction
{
    [FunctionName("ProcessUserChanges")]
    public async Task Run(
        // TRIGGER
        [CosmosDBTrigger(
            databaseName: "MyStore",
            containerName: "Users", // The Monitored Container
            Connection = "CosmosDBConnection",

            // LEASE CONFIG
            LeaseContainerName = "leases",
            LeaseContainerPrefix = "email-worker-", // Expert Pattern: Isolation
            CreateLeaseContainerIfNotExists = true, // Lazy config

            // BEHAVIOR
            StartFromBeginning = false, // Standard for event-driven
            MaxItemsPerInvocation = 100 // Batch Size control
        )] IReadOnlyList<UserDocument> input,

        ILogger log)
    {
        if (input != null && input.Count > 0)
        {
            log.LogInformation($"Documents modified: {input.Count}");
            foreach (var doc in input)
            {
                // Business Logic Here
            }
        }
    }
}

```

### **Summary Checklist for the Architect**

1. **Scaling Unit:** Change Feed scales by **Physical Partition**, not by logical Request Units.
2. **Concurrency:** Max Parallel Consumers = Number of Physical Partitions.
3. **State:** The `leases` container is the Source of Truth for state. If you delete it, you lose your place.
4. **Reliability:** Always separate `leases` by using `LeaseCollectionPrefix` if you have multiple consumers.

---

### Change Feed Processor (CFP) vs. Azure Function

This is a trick question because **Azure Functions uses the Change Feed Processor internally.**

However, you can choose *how* you implement it.

### Option A: Azure Functions (The "Managed" CFP)

- **What is it?** It is a wrapper around the CFP Library. The Azure Functions Runtime hosts the processor for you.
- **When to use:** 95% of use cases.
    - Simple Event Processing (Email triggers, Audit logs).
    - Low overhead maintenance (Serverless).
    - You don't want to manage Virtual Machines or Console Apps.

### Option B: The "Raw" Change Feed Processor (The "Library")

- **What is it?** You add `Microsoft.Azure.Cosmos` NuGet package to your own `.NET Core Console App`, `Worker Service`, or `AKS Container`.
- **How you write it:** You manually define the delegate logic.
    
    ```csharp
    Container leaseContainer = client.GetContainer("db", "leases");
    Container dataContainer = client.GetContainer("db", "data");
    
    ChangeFeedProcessor processor = dataContainer
        .GetChangeFeedProcessorBuilder<MyItem>("processorName", HandleChangesAsync)
            .WithInstanceName("Host-1")
            .WithLeaseContainer(leaseContainer)
            .Build();
    
    await processor.StartAsync();
    
    ```
    
- **When is this REQUIRED?**
    1. **Long Running Processes:** Azure Functions (Consumption Plan) timeout after 5 or 10 minutes. If processing a batch of changes takes 30 minutes, you **must** use a Background Worker (Raw CFP) hosted on a VM or Kubernetes.
    2. **Strict Resource Control:** You need to strictly control CPU/RAM usage on the host machine.
    3. **Complex State Management:** You are building a complex microservice that needs to hold heavy in-memory state between batches.

### Summary Comparison

| Feature | Azure Functions Trigger | Raw CFP Library (Worker Service) |
| --- | --- | --- |
| **Ease of Use** | ⭐⭐⭐⭐⭐ (Magic) | ⭐⭐⭐ (Code heavy) |
| **Hosting** | Serverless / App Service | AKS / VM / App Service WebJob |
| **Max Duration** | Limited (10 mins on Consumption) | **Unlimited** |
| **Scaling** | Auto-scales by Platform logic | Manual / KEDA Scaling required |
| **State** | Stateless (mostly) | Can be Stateful |
| **Recommendation** | **Default Choice.** Start here. | Use only for "Heavy Lifting" tasks. |