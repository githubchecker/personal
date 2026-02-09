# Event Hub

# **Tier 1: The Foundational Pillars (You cannot be an expert without these)**

## **1. Partitions: The Core of Parallelism**

- **What is it?**
    - A partition is a single, ordered log of events within an Event Hub. An Event Hub is simply a collection of these parallel partitions (e.g., an Event Hub with 8 partitions has 8 parallel logs).
- **The "Aha!" Analogy: A Multi-Lane Highway**
    - Think of your Event Hub as a highway and events as cars.
        - **A single partition** is like having a **single-lane road**. All cars travel in a single file, guaranteeing their order, but your throughput is limited.
        - **Multiple partitions** are like a **multi-lane highway**. You can now have many cars (events) flowing in parallel, dramatically increasing throughput. The cars in **Lane 1** are in order relative to each other, but not relative to the cars in **Lane 2**.
- **Why You MUST Master It (The Architectural Implication)**
    - **SCALE.** The number of partitions is the **fundamental upper limit on your consumer's parallelism**. If you have 16 partitions, you can have a maximum of 16 consumer instances (e.g., 16 Docker containers or 16 Azure Function instances) reading from that Event Hub simultaneously. A 17th consumer instance would sit idle, waiting for a partition to become free. Your choice of partition count at creation time defines the maximum scale of your entire downstream system.
- **How It Works (Quick Start Details)**
    - **Configuration:** You set the partition count **when you create the Event Hub**. This number is very difficult to change later, so it's a critical design decision. A good starting point is often between 8 and 32.
    - **Event Distribution:** When a producer sends an event without a partition key, Event Hubs uses a round-robin model to distribute events evenly across all available partitions. This ensures no single partition gets overloaded.
- **Key Rules & Best Practices**
    - **Rule #1: Ordering is ONLY guaranteed within a partition.** This is the most important concept to remember.
    - **Plan for Peak Load:** Choose a partition count that can handle your anticipated peak consumer scale, not your average load.
    - **Don't Confuse Partitions with Throughput Units (TUs):** TUs are about bandwidth (MB/s). Partitions are about the degree of parallelism. They are related but distinct concepts.
    - **It's a One-Way Street:** You can't easily reduce the partition count.

## **2. Consumer Groups**

- **What is it?**
    - A consumer group is a logical "view" or a named "cursor" that tracks the progress of a specific consuming application as it reads through the partitions of an Event Hub.
- **The "Aha!" Analogy: Bookmarks in a Book**
    - Imagine an Event Hub is a book that many people want to read.
        - The **Event Hub stream** is the book's content.
        - Each **Consumer Group** is a **personal bookmark** for a reader.
        - The Real-Time Alerting team can have their bookmark on page 50. The Archival team can have their bookmark on page 20. The Analytics team can be on page 49. Each reader's progress is independent and doesn't affect the others.
- **Why You MUST Master It (The Architectural Implication)**
    - **INDEPENDENCE.** Consumer groups are the feature that enables a true, decoupled, publish-subscribe architecture for event streams. It allows multiple independent downstream systems to consume the exact same stream of data at their own pace, for completely different purposes, without impacting each other. This is how you build a robust data hub.
- **How It Works (Quick Start Details)**
    - **Default Group:** Every Event Hub is created with a default consumer group named `$Default`.
    - **Creating New Groups:** You create new consumer groups in the Azure portal, CLI, or IaC templates for each consuming application.
    - **Specifying in Code:** Your consumer client (like the EventProcessorClient) must specify which consumer group it belongs to.
    
    ```csharp
    // You provide the consumer group name when creating the processor.
    string consumerGroup = "RealtimeAlertsConsumer"; // A dedicated consumer group
    
    var processor = new EventProcessorClient(
        checkpointStore,
        consumerGroup,
        ehubNamespaceConnectionString,
        eventHubName);
    
    ```
    
- **Key Rules & Best Practices**
    - **Rule #1: One Consumer Group Per Consuming Application.** This is the golden rule. If you have an alerting system and an archival system, you create two consumer groups.
    - **Don't Use $Default for Production:** While it works, it signals a lack of explicit design. Always create named groups for your applications.
    - **Name Logically:** Name your consumer groups after the application that uses them (e.g., LogAnalyticsIngestion, FraudDetectionEngine). This makes your architecture self-documenting.

## **3. Partition Keys**

- **What is it?**
    - A partition key is a string value you provide when sending an event. The Event Hubs service uses this key to hash and deterministically route your event to a specific partition.
- **The "Aha!" Analogy: Assigned Mailboxes**
    - Imagine a mailroom with 16 mailboxes (partitions).
        - **Without a partition key (round-robin),** the mail clerk puts letters into the mailboxes one by one to keep them all even.
        - **With a partition key (e.g., the recipient's name),** the mail clerk has a rule: "All mail for 'Alice' always goes into Mailbox #7. All mail for 'Bob' always goes into Mailbox #2."
- **Why You MUST Master It (The Architectural Implication)**
    - **ORDER.** This is the **only way to guarantee in-order processing for a sequence of related events**. If you need to process all telemetry from device-123 in the exact order it was sent, you must send all those events with the partition key "device-123". This ensures they all land in the same partition and will therefore be read by a single consumer instance in sequence.
- **How It Works (Quick Start Details)**
    - **Sending:** You specify the key when you create a batch of events to send.
    
    ```csharp
    // using Azure.Messaging.EventHubs.Producer;
    await using (var producerClient = new EventHubProducerClient(connectionString, eventHubName))
    {
        // A logical identifier for related events
        string deviceId = "device-123";
    
        // Create a batch with options to ensure all events in it go to the same partition
        using EventDataBatch eventBatch = await producerClient.CreateBatchAsync(
            new CreateBatchOptions { PartitionKey = deviceId });
    
        eventBatch.TryAdd(new EventData("Reading 1"));
        eventBatch.TryAdd(new EventData("Reading 2")); // Reading 2 is guaranteed to follow Reading 1
    
        await producerClient.SendAsync(eventBatch);
    }
    
    ```
    
- **Key Rules & Best Practices**
    - **Rule #1: Use a partition key IF, and only IF, you need strict ordering for related events.**
    - **Choose a Key with High Cardinality:** A good key is one with many unique values (e.g., deviceId, userId, sessionId). A bad key has few values (e.g., region="US-East"), as this would send a massive amount of traffic to only a few partitions, creating "hot partitions" and a performance bottleneck.
    - **No Key = Better Distribution:** If you don't need ordering, do not provide a partition key. The default round-robin behavior provides the most even distribution of load.

## **4. EventProcessorClient**

- **What is it?**
    - The `EventProcessorClient` is a high-level, intelligent consumer client in the Azure SDK. It is not just a receiver; it is a complete framework for building robust, scalable, and resilient consumer applications.
- **The "Aha!" Analogy: A Fleet Manager**
    - Imagine your consumer application instances are a fleet of taxi drivers.
        - The **EventProcessorClient** is the **fleet manager/dispatcher**.
        - It **assigns routes** (partitions) to each driver.
        - It **monitors progress** by having drivers check in (checkpointing).
        - If a driver gets a flat tire (crashes), the manager sees they've stopped checking in, **takes their route away, and reassigns it** to an available driver, telling them where the last driver left off.
- **Why You MUST Master It (The Architectural Implication)**
    - **RELIABILITY & SIMPLICITY.** It automatically handles the three hardest problems in distributed stream processing:
        1. **Load Balancing:** Automatically distributes partitions across all running instances of your application.
        2. **State Management (Checkpointing):** Persists your processing progress to Azure Blob Storage, so you don't re-process data after a restart.
        3. **Fault Tolerance:** If a consumer instance fails, its partition leases will expire and be picked up by other healthy instances, ensuring the stream continues to be processed. **You should almost never build a consumer without it.**
- **How It Works (Quick Start Details)**
    - You provide it with connection details, a storage container for checkpoints, and two event handlers: one for processing events and one for handling errors.
    
    ```csharp
    // using Azure.Messaging.EventHubs;
    // using Azure.Messaging.EventHubs.Consumer;
    // using Azure.Storage.Blobs;
    
    // 1. You need a BlobContainerClient for checkpointing
    var storageClient = new BlobContainerClient("YOUR_STORAGE_CONNECTION_STRING", "checkpoints");
    
    // 2. Create the processor
    var processor = new EventProcessorClient(
        storageClient,
        EventHubConsumerClient.DefaultConsumerGroupName,
        "YOUR_EVENTHUB_CONNECTION_STRING",
        "YOUR_EVENTHUB_NAME");
    
    // 3. Define what to do with each event
    async Task ProcessEventHandler(ProcessEventArgs eventArgs)
    {
        // Your business logic here
        Console.WriteLine($"Event received from partition {eventArgs.Partition.PartitionId}: {eventArgs.Data.EventBody}");
    
        // Update the checkpoint in blob storage
        await eventArgs.UpdateCheckpointAsync(eventArgs.CancellationToken);
    }
    
    // 4. Define what to do if an error occurs
    Task ProcessErrorHandler(ProcessErrorEventArgs eventArgs)
    {
        Console.WriteLine($"Error on partition {eventArgs.PartitionId}: {eventArgs.Exception.Message}");
        return Task.CompletedTask;
    }
    
    // 5. Wire up the handlers and start processing
    processor.ProcessEventAsync += ProcessEventHandler;
    processor.ProcessErrorAsync += ProcessErrorHandler;
    
    await processor.StartProcessingAsync();
    
    // ... wait for work ...
    await processor.StopProcessingAsync();
    
    ```
    
- **Key Rules & Best Practices**
    - **Rule #1: Always use the EventProcessorClient** for production consumers unless you have a very specialized need (e.g., using Spark).
    - **Make Your Handlers Idempotent:** Because Event Hubs guarantees "at-least-once" delivery, your processing logic should be safe to run on the same event twice without causing issues.
    - **Checkpointing is a Performance Trade-off:** Checkpointing after every message is safest but slowest. Checkpointing every 50 messages is faster but means you might re-process up to 50 messages after a crash.
    - **The ProcessErrorAsync handler is your safety net.** Log aggressively here to diagnose problems with your processor.

---

# **Tier 2: The Scalability & Performance Engine (How to Go Fast)**

## **5. Throughput Units (TUs) & Processing Units (PUs)**

- **What is it?**
    - A Throughput Unit (TU) is a **pre-purchased, reserved unit of capacity** for an Event Hubs Standard namespace. It dictates how much data you can send and receive per second and how many events you can process. Processing Units (PUs) are the equivalent for the Premium and Dedicated tiers, offering isolated resources and higher performance.
- **The "Aha!" Analogy: A Highway Toll Plaza**
    - **Throughput Units (TUs)** are the **number of toll booths** you have open.
    - **1 TU** is like having **one toll booth open**. It can only process a certain number of cars (events) per second. If too many cars arrive, a traffic jam (throttling) occurs.
    - **10 TUs** is like having **ten toll booths open**. Your capacity to handle traffic is much higher.
    - You pay for the number of booths you keep open, regardless of whether there's a constant stream of cars.
- **Why You MUST Master It (The Architectural Implication)**
    - **PERFORMANCE vs. COST.** TUs are the primary lever you control to balance performance and cost.
        - **Under-provisioning (too few TUs):** Your producers and consumers will get **throttling exceptions** (ServerBusyException). Your entire data pipeline will slow down or halt. This is a common cause of production failures.
        - **Over-provisioning (too many TUs):** Your system will run smoothly, but you will be **wasting money** on unused capacity.
        - An expert knows how to monitor utilization to find the sweet spot and uses features like Auto-Inflate to handle the rest.
- **How It Works (Quick Start Details)**
    - **Standard Tier (TUs):**
        - **Capacity per TU:**
            - **Ingress (Sending):** Up to **1 MB/s** OR **1000 events/s**, whichever comes first.
            - **Egress (Receiving):** Up to **2 MB/s** OR **4096 events/s**.
        - **Billing:** Billed per hour, for each provisioned TU.
        - **Scope:** Capacity is shared across all Event Hubs within a single Standard namespace.
    - **Premium/Dedicated Tiers (PUs):**
        - **Capacity per PU:** Much higher and more consistent performance than TUs.
        - **Key Feature: Resource Isolation.** When you buy PUs, you get dedicated CPU and memory. Your workload is not affected by "noisy neighbors" (other Azure customers), providing predictable latency.
        - **When to Use:** For mission-critical, enterprise-grade workloads that require high performance and cannot tolerate any throttling.
- **Key Rules & Best Practices**
    - **Rule #1: Monitor, Monitor, Monitor.** In Azure Monitor, track "Incoming Requests" and "Throttled Requests". If Throttled Requests are greater than zero, you need more TUs.
    - **Understand the "Whichever Comes First" Rule:** If you send lots of very small events, you'll likely hit the 1000 events/sec limit before the 1 MB/s limit.
    - **Provision for the 80%, Inflate for the 20%:** Set your baseline TUs to handle your normal, everyday peak load. Use Auto-Inflate (next topic) to handle unexpected spikes.

## **6. Auto-Inflate**

- **What is it?**
    - Auto-Inflate is a feature of the Standard tier that **automatically scales up your provisioned TUs** when your traffic exceeds their capacity, protecting you from throttling.
- **The "Aha!" Analogy: A Car's Turbocharger**
    - **Your engine** is your baseline number of **provisioned TUs**. It handles normal driving perfectly.
    - **Auto-Inflate** is the **turbocharger**. When you suddenly need to accelerate hard to merge onto the highway (a traffic burst), the turbo kicks in, gives you a massive power boost (more TUs), and prevents the engine from stalling (throttling).
- **Why You MUST Master It (The Architectural Implication)**
    - **RELIABILITY & COST OPTIMIZATION.** This is your safety net. It allows you to provision your TUs for your typical peak load instead of your absolute maximum theoretical peak load. This saves you money on a day-to-day basis while ensuring your application can survive a sudden, massive burst of traffic (like a Black Friday sale or a viral event).
- **How It Works (Quick Start Details)**
    - **Configuration:** You enable it on your Event Hubs Standard namespace.
    - **Settings:**
        1. **Default TUs:** Your baseline number of TUs.
        2. **Maximum TUs:** The ceiling. The system will not inflate beyond this number.
    - **The Catch (One-Way Street):** Auto-Inflate **only scales up**. It **DOES NOT automatically scale back down**. If your traffic burst is over and you've inflated from 2 TUs to 10 TUs, you will continue to be billed for 10 TUs until you manually scale it back down in the portal or via a script.
- **Key Rules & Best Practices**
    - **Rule #1: Almost Always Enable It.** For any production workload with variable traffic, this is a must-have feature.
    - **Set a Sane Maximum:** Set the maximum TUs to a number that can handle your largest imaginable spike but won't cause a catastrophic bill if something goes wrong.
    - **Implement a Scale-Down Strategy:** Since it doesn't scale down, an expert will set up an Azure Monitor Alert. For example: "If average incoming bytes is below the 2-TU limit for 3 hours, send an alert to an Azure Function or Logic App that programmatically resets the TUs back to 2."

## **7. Producer-Side Batching**

- **What is it?**
    - The practice of grouping multiple individual events into a single collection (a batch) and sending that batch to Event Hubs in one network call.
- **The "Aha!" Analogy: A Carpool Lane**
    - **Sending one event at a time** is like **one person driving one car**. If you have 100 people, you have 100 cars on the road, creating massive traffic (network overhead), high fuel costs (resource utilization), and slow travel times.
    - **Batching events** is like creating a **carpool**. You put 4 people (events) in one car (a batch). For 100 people, you now only have 25 cars on the road. It's vastly more efficient, cheaper, and faster.
- **Why You MUST Master It (The Architectural Implication)**
    - **THROUGHPUT.** This is the single most important technique for achieving high performance from your producers. Sending events one-by-one is a performance anti-pattern that will never scale. Every official Azure SDK is heavily optimized for batching. By batching, you:
        - Minimize network latency and round trips.
        - Maximize your use of your provisioned TUs.
        - Drastically improve the overall throughput of your application.
- **How It Works (Quick Start Details)**
    - The SDK makes this easy. The recommended pattern is to create a batch, add events until it's full, send it, and then create a new batch.
    
    ```csharp
    // using Azure.Messaging.EventHubs.Producer;
    // Assume producerClient is already created.
    
    var myEvents = GetEventsToSend(); // A list of many EventData objects
    
    // 1. Create a batch. The SDK will ensure it doesn't exceed the max message size.
    using EventDataBatch eventBatch = await producerClient.CreateBatchAsync();
    
    foreach (var eventData in myEvents)
    {
        // 2. Try to add an event to the batch.
        if (!eventBatch.TryAdd(eventData))
        {
            // If the batch is full:
            // a. Send the full batch.
            await producerClient.SendAsync(eventBatch);
    
            // b. Create a new empty batch.
            eventBatch = await producerClient.CreateBatchAsync();
    
            // c. Don't forget to add the event that didn't fit!
            eventBatch.TryAdd(eventData);
        }
    }
    
    // 3. Send any final, remaining events in the last batch.
    if (eventBatch.Count > 0)
    {
        await producerClient.SendAsync(eventBatch);
    }
    
    ```
    
- **Key Rules & Best Practices**
    - **Rule #1: Always Batch.** Never send events in a one-by-one loop.
    - **Let the SDK Manage Batch Size:** Don't try to manually calculate if you've hit the 1MB message size limit. The `eventBatch.TryAdd()` method does this for you safely.
    - **Partition Keys and Batches:** All events within a single batch **will be sent to the same partition**. If you specified a partition key when creating the batch, they go to that key's partition. If not, they are sent to a round-robin partition *as a single unit*.

---

# **Tier 3: The Integration & Ecosystem Features (The Architect's Toolkit)**

## **8. Event Hubs Capture**

- **What is it?**
    - Event Hubs Capture is a "zero-code" feature that you simply enable with a toggle. It automatically and continuously captures the entire stream of event data passing through your Event Hub and saves it as micro-batches into **Azure Blob Storage** or **Azure Data Lake Storage Gen2**.
- **The "Aha!" Analogy: A Security DVR System**
    - **Your Event Hub** is the **live video feed** from all the security cameras in a building. It's real-time and what you watch for immediate threats.
    - **Event Hubs Capture** is the **DVR system** connected to those cameras. It doesn't interfere with the live feed, but in the background, it reliably records everything to a hard drive (Blob Storage). If you need to review footage from last Tuesday (perform batch analytics), you go to the DVR's recordings, not the live feed.
- **Why You MUST Master It (The Architectural Implication)**
    - It solves the Lambda Architecture problem. This is the foundational pattern for combining real-time ("hot path") and batch ("cold path") analytics.
        - **Hot Path:** Systems that need immediate data (like Stream Analytics or Azure Functions) consume the live Event Hubs stream.
        - **Cold Path:** Capture automatically creates the durable, long-term data archive in your data lake. Batch processing tools like Azure Synapse Analytics, Databricks, or HDInsight can then run large, complex queries over this historical data at their own pace.
    - This is the **most efficient, reliable, and cost-effective way to create a durable archive** of your event stream.
- **How It Works (Quick Start Details)**
    - This is a configuration task, not a coding one.
    1. Navigate to your Event Hub in the Azure portal.
    2. Under "Features," select **"Capture."**
    3. Turn it On.
    4. **Configure the Settings:**
        - **Capture Destination:** Choose either "Azure Storage" or "Azure Data Lake Storage Gen2." Select your account and container/filesystem.
        - **Time Window:** How often to write a new file. (Range: 1-15 minutes). A common choice is 5 minutes.
        - **Size Window:** How large a file should get before a new one is created. (Range: 10-500 MB). A common choice is 100-300 MB.
        - (Whichever threshold is met first triggers a write.)
        - **Capture File Format:** **Avro** (default, recommended) or JSON.
        - **File Naming Convention:** Leave the default. It creates a logical, query-friendly folder structure: `{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}`.
- **Key Rules & Best Practices**
    - **Rule #1: Use this for Archival and Batch Analytics.** It's the default, best-practice pattern.
    - **Choose Avro over JSON.** Avro is a binary, compressed format that includes the data schema. It results in significantly smaller files, which saves storage costs and speeds up downstream queries. JSON is only useful if you need immediate human readability.
    - **Understand it's "Micro-Batch," not Real-Time.** Don't rely on Capture for tasks that need sub-minute latency. That's what the live stream is for.
    - **The Folder Structure is Your Friend.** The default naming convention automatically partitions your data by time, which is critical for efficient queries in big data systems like Synapse or Databricks.

## **9. The Apache Kafka Endpoint**

- **What is it?**
    - It's a feature that makes your Azure Event Hub **look and act like an Apache Kafka broker**. It exposes a protocol-compatible endpoint that allows standard Kafka clients (producers and consumers written in Java, Python, Go, etc.) to connect to Event Hubs without any code changes, typically just by modifying a configuration file.
- **The "Aha!" Analogy: A Universal Power Adapter**
    - **Your Kafka application** is like a **laptop with a US plug**.
    - **Azure** is like the **power grid in Europe**. The plugs don't match.
    - The **Event Hubs Kafka Endpoint** is the **power adapter**. You plug your US laptop into the adapter, and the adapter into the European wall. The laptop works perfectly and doesn't even know it's not plugged into a US socket.
- **Why You MUST Master It (The Architectural Implication)**
    - **MIGRATION & ECOSYSTEM LEVERAGE.** This is a game-changer for two key scenarios:
    1. **Cloud Migration ("Lift-and-Shift"):** A company has a large, existing investment in on-premises Apache Kafka. They want to move to a managed cloud service without rewriting years of application code. With this feature, they can simply point their existing producers and consumers to Event Hubs.
    2. **Hybrid & Tooling:** It allows you to use the vast ecosystem of Kafka-compatible tools (connectors, monitoring tools, etc.) directly with the managed, scalable, and secure backend of Azure Event Hubs.
- **How It Works (Quick Start Details)**
    - You don't "turn it on" for Standard/Premium tiers; it's always available. The work is in the client configuration.
    1. **Get the Connection String:** Go to your Event Hubs Namespace -> "Shared access policies."
    2. **Configure your Kafka Client (e.g., kafka-producer.properties):**
    
    ```
    # Endpoint: your Event Hubs Namespace FQDN with port 9093
    bootstrap.servers=YOUR_NAMESPACE.servicebus.windows.net:9093
    
    # Security Protocol must be SASL_SSL
    security.protocol=SASL_SSL
    sasl.mechanism=PLAIN
    
    # JAAS config using your connection string
    sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="YOUR_EVENTHUB_CONNECTION_STRING";
    
    ```
    
    1. **Run your standard Kafka application.** The code itself doesn't change. A Java producer is still a KafkaProducer, a consumer is still a KafkaConsumer.
- **Key Rules & Best Practices**
    - **Rule #1: Use it for MIGRATION, not for new cloud-native apps.** If you are building a new application from scratch on Azure, you should use the native Event Hubs SDKs. They are more tightly integrated and often more performant.
    - **Know the Limitations:** Event Hubs supports the core Kafka producer/consumer APIs, but not all Kafka features (like Kafka Streams or infinite log compaction). An expert knows what is and isn't supported.
    - **Use with Premium/Dedicated Tiers:** Kafka clients can be quite "chatty." For production workloads, the resource isolation of the Premium or Dedicated tiers provides the most stable performance.

## **10. Integration with Azure Functions & Stream Analytics**

- **What is it?**
    - These are first-class, native bindings that make Event Hubs a seamless **trigger** and **output** for Azure's premier serverless compute and real-time analytics services.
- **The "Aha!" Analogy: Pre-Wired Sockets in a Smart Home**
    - **Your house** is the **Azure ecosystem**.
    - **Event Hubs** is the central **power bus** running through the walls.
    - The **bindings** are specialized **pre-wired sockets**.
    - **Azure Functions** and **Stream Analytics** are smart **appliances**. You don't need to do complex electrical work; you just plug the appliance directly into the correct socket, and it's instantly connected to the power bus, ready to work.
- **Why You MUST Master It (The Architectural Implication)**
    - This is the engine of modern serverless event-driven architecture on Azure. It's how you build powerful, reactive pipelines that scale automatically without managing any infrastructure. An expert combines these services like LEGO bricks to build solutions.
        - **Functions for Code:** When you need to run complex, imperative code in response to an event (e.g., call a REST API, perform complex data enrichment, run a machine learning model).
        - **Stream Analytics for Queries:** When you need to perform filtering, transformations, aggregations over time windows, or anomaly detection on the event stream using a simple, powerful SQL-like query language.
- **How It Works (Quick Start Details)**
    
    **1. Azure Functions (The "Code" Appliance):**
    
    - You use a simple trigger binding in your C# code.
    
    ```csharp
    // using Azure.Messaging.EventHubs;
    // using Microsoft.Azure.Functions.Worker;
    
    public class MyEventHubProcessor
    {
        private readonly ILogger _logger;
    
        public MyEventHubProcessor(ILoggerFactory loggerFactory)
        {
            _logger = loggerFactory.CreateLogger<MyEventHubProcessor>();
        }
    
        // The binding is defined by the attribute
        [Function("MyEventHubProcessor")]
        public async Task Run(
            // Process events in a batch for high performance
            [EventHubTrigger("my-event-hub-name", Connection = "EventHubConnection", ConsumerGroup = "FunctionAppConsumer")] EventData[] events)
        {
            foreach (EventData eventData in events)
            {
                _logger.LogInformation($"Event Body: {eventData.EventBody}");
                _logger.LogInformation($"Partition Key: {eventData.PartitionKey}");
            }
        }
    }
    
    ```
    
    **2. Azure Stream Analytics (The "Query" Appliance):**
    
    - This is a "no-code/low-code" experience in the Azure portal.
    1. Create a Stream Analytics Job.
    2. Define an **INPUT**: Select "Event Hub," point it to your hub, and give it a dedicated consumer group. Name it `logInput`.
    3. Define an **OUTPUT**: Select a destination, like "Azure SQL Database." Name it `errorOutput`.
    4. Write the **QUERY**:
    
    ```sql
    -- Select only error logs and send them to the SQL database
    SELECT
        System.Timestamp AS EventTime,
        GetRecordPropertyValue(log, 'Level') AS LogLevel,
        GetRecordPropertyValue(log, 'Message') AS Message
    INTO
        [errorOutput]
    FROM
        [logInput]
    WHERE
        GetRecordPropertyValue(log, 'Level') = 'Error'
    
    ```
    
    1. Start the job.
- **Key Rules & Best Practices**
    - **Rule #1: Dedicated Consumer Group for every binding.** A Function App gets its own consumer group. A Stream Analytics job gets its own. Never share them.
    - **Process in Batches in Functions.** As shown in the code, triggering on an array `EventData[]` is vastly more efficient than triggering on a single event.
    - **Use Stream Analytics First:** For filtering, routing, and aggregations, try to use Stream Analytics. It is often cheaper, faster, and easier to manage than writing, deploying, and scaling custom Function code. Use Functions when you need the power of a full programming language.