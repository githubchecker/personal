# ASB Retry

As an architect, it is critical to distinguish between **Configuration Options** (static settings defined when creating the Queue) and **Runtime Actions** (dynamic choices made by your code).

Here is the deep dive into the behaviors, specifically addressing your doubt about **Abandonment vs. Prefetch**.

---

### Part 1: The "Static" Configuration Knobs

These are set when you provision the infrastructure (Terraform/Bicep/Portal).

### 1. Time To Live (TTL) - `DefaultMessageTimeToLive`

- **Concept:** The "Expiration Date" of a message.
- **Behavior:** If a message sits in the Queue for longer than this time (e.g., 5 minutes) without being picked up (locked) by a consumer, it expires.
- **Fate:**
    - If `EnableDeadLetteringOnMessageExpiration` is **True**: The message moves to the Dead Letter Queue (DLQ) with reason `TTLExpiredException`.
    - If **False**: The message is permanently deleted and lost.
- **Architectural Use:** High-volume IoT telemetry. If you haven't processed "Vehicle Speed" within 5 minutes, it's irrelevant. Drop it.

### 2. Lock Duration - `LockDuration`

- **Concept:** The "Invisibility Clock."
- **Range:** Max 5 minutes (in basic setup).
- **Behavior:** When your client says `Receive()`, the message isn't removed. It is **Locked** (Hidden from other consumers) for this duration.
- **Risk:** If your code takes 2 minutes to process, but `LockDuration` is 30 seconds, the lock will expire *while you are still processing*. The message becomes visible again, and a **Second Consumer** picks it up. You now have duplicates processing in parallel.

### 3. Max Delivery Count - `MaxDeliveryCount`

- **Concept:** The "Retry Threshold."
- **Behavior:** ASB maintains a counter (`DeliveryCount`) on the message. Every time a lock is acquired (prefetch or receive) or the message is Abandoned (or the lock expires), this counter increments.
- **Fate:** When `DeliveryCount > MaxDeliveryCount`, ASB automatically moves the message to the DLQ.

### 4. Auto Delete on Idle - `AutoDeleteOnIdle`

- **Concept:** "Garbage Collection" for the Queue itself.
- **Behavior:** If no one sends messages to OR reads messages from the Queue for this specific duration, the **entire Queue (and its contents) is deleted.**
- **Architectural Use:** Temporary reply queues used in "Request-Response" patterns. Do **not** use this for persistent production queues.

---

### Part 2: Runtime Actions (The Code Choices)

When you receive a message in `PeekLock` mode, you hold the "Token". You must resolve it with one of these four actions:

1. **Complete (`CompleteMessageAsync`)**: "Success". Tells ASB to delete it from the server.
2. **DeadLetter (`DeadLetterMessageAsync`)**: "Poison". Explicitly moves it to DLQ (skips the Delivery Count logic).
3. **Defer (`DeferMessageAsync`)**: "Later". Keep it in the queue, but hide it. It can only be retrieved again by its specific Sequence Number (Sequence ID). Used for Workflow ordering.
4. **Abandon (`AbandonMessageAsync`)**: "Retry".

---

### Part 3: The Deep Dive - Abandon, Unlocking, and Prefetching

This is where your doubt lies. Let's break down the mechanics of `Abandon` explicitly.

### The Scenario

- **Configuration:** Queue has `PrefetchCount = 100`.
- **State:** Your Consumer has connected. It asks ASB for messages.
- **The Network:** ASB sends 100 messages down the wire to your Client's **Local Memory Buffer (RAM)**.
    - All 100 messages are now **LOCKED** on the Server.
    - No other consumer can see them.
    - Wait/Lock timers are ticking for all 100 messages simultaneously.

### You process Message #1 and call `AbandonAsync()`

Here is exactly what happens, step-by-step:

1. **The Signal:** Your code sends a command to ASB Server: "Release the lock on Message #1."
2. **Server Action:**
    - ASB increments `DeliveryCount` for Message #1.
    - ASB removes the Lock token.
    - The message becomes **Visible** again in the Main Queue (on the Server).
    - **Crucial:** It is placed back based on priority/timestamp. It effectively goes "back on the shelf."
3. **Local RAM (Prefetch Buffer):**
    - The message is **removed** from your local prefetch buffer.
    - **It does NOT stay in your local queue.** It is gone from your memory.
    - Your `ServiceBusProcessor` will grab the next message (Message #2) from the local buffer.

### The "Thundering Herd" Question

**Question:** *"Does it go to the queue to be handled by other or same processor?"*

**Answer:** It goes to the **Queue (Server)**.
Because it is on the Server, **ANY** consumer asking for a message can get it.

1. **Scenario A (You are the only Consumer):**
    - You Abandon Message #1.
    - It goes to Server.
    - Your Local Prefetch buffer still has Messages #2 - #100 waiting.
    - You will process #2... #100.
    - Once your buffer runs low, you ask the Server for more.
    - You *might* download Message #1 again (now with DeliveryCount = 2).
2. **Scenario B (Multiple Consumers):**
    - Consumer A Abandons Message #1.
    - Message #1 becomes visible on Server.
    - Consumer B is currently asking for messages.
    - **Consumer B gets Message #1 immediately.**

### Summary of the Prefetch Trap

There is a dangerous edge case here.
If you prefetch 100 messages, and `LockDuration` is 30 seconds.

- Message #100 sits in your RAM buffer waiting for you to process #1 through #99.
- By the time you get to #100, 2 minutes have passed.
- **The Lock for #100 has expired on the Server.**
- Another Consumer picks up #100 (Copy B).
- Your Consumer tries to process #100 (Copy A) and calls `Complete`.
- **Error:** `LockLostException`. You tried to complete a message lock that no longer exists.

**Architect's Advice:**
Never set `PrefetchCount` higher than what you can realistically process within the `LockDuration`. If you process 1 msg/sec and Lock is 60 sec, do not Prefetch more than 40-50.

# Retry Logic

As a solution architect, you must view "Retry" in Azure Service Bus (ASB) through two completely different lenses. Mixing these up is the most common mistake developers make.

1. **Transient/Operation Retries:** The *client* fails to talk to the *server* (Network blips, throttles).
2. **Message Lifecycle Retries:** The *code* successfully received the message but crashed while processing it (Bug, Database down).

Here is the top-notch breakdown of how to handle both.

---

### Layer 1: Client/Connection Retries (The "Can't Reach ASB" Phase)

This handles the scenario where your application tries to send a message, but the Azure infrastructure blips, or the socket is closed. This is controlled entirely by `ServiceBusRetryOptions`.

**The Architect's Rule:** Use **Exponential Backoff** with Jitter. Do not use Fixed retries in production, or you will create a "Thundering Herd" effect that can take down your system when it tries to recover.

### Registration (`Program.cs`)

You configure this globally when registering the client.

```csharp
using Azure.Messaging.ServiceBus;
using Microsoft.Extensions.Azure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddAzureClients(clients =>
{
    clients.AddServiceBusClient(builder.Configuration.GetConnectionString("ServiceBusConnection"))
           .ConfigureOptions(options =>
           {
               options.RetryOptions = new ServiceBusRetryOptions
               {
                   // MODE: Exponential (Wait 2s, then 4s, then 8s...) to give Azure time to heal.
                   Mode = ServiceBusRetryMode.Exponential,

                   // How many times the SDK attempts the network call before throwing generic Exception
                   MaxRetries = 3,

                   // Sanity check: Don't wait longer than 30s
                   MaxDelay = TimeSpan.FromSeconds(30),

                   // Start fast
                   Delay = TimeSpan.FromSeconds(0.8)
               };
           });
});

```

---

### Layer 2: Message Processing Retries (The "Poison Message" Phase)

This is the critical part. What happens when your consumer code throws an exception (e.g., SQL Database is offline)?

**The Architecture:**
Azure Service Bus uses a mechanism called **Peek-Lock**.

1. App locks message (nobody else can see it).
2. App tries to process.
3. **If Crash:** The lock is released (or explicitly abandoned).
4. **The Retry:** The message immediately becomes visible again on the Queue for the next consumer to pick up.
5. **The Safety Valve:** Each retry increments the `DeliveryCount` header on the message. If `DeliveryCount > MaxDeliveryCount` (defined in Azure Portal, default is 10), the broker moves it to the **Dead Letter Queue (DLQ)**.

### How to Implement Robust Processor Retries

You do not write a `while(true)` loop for retries inside your message handler. You let the architecture do it.

**The Code (Worker Service Pattern):**

```csharp
public class ServiceBusWorker : BackgroundService
{
    private readonly ServiceBusProcessor _processor;
    private readonly ILogger<ServiceBusWorker> _logger;

    public ServiceBusWorker(ServiceBusClient client, ILogger<ServiceBusWorker> logger)
    {
        _logger = logger;

        // Configure the PROCESSOR (The listener)
        var options = new ServiceBusProcessorOptions
        {
            // PRO-TIP: "PeekLock" requires explicit completion.
            // "ReceiveAndDelete" is fire-and-forget (dangerous, don't use).
            ReceiveMode = ServiceBusReceiveMode.PeekLock,

            // If true, the SDK completes the message if your function returns cleanly,
            // or Abandons it if you throw an Exception.
            AutoCompleteMessages = false,

            // Threading power
            MaxConcurrentCalls = 10
        };

        _processor = client.CreateProcessor("my-queue", options);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _processor.ProcessMessageAsync += MessageHandler;
        _processor.ProcessErrorAsync += ErrorHandler;

        await _processor.StartProcessingAsync(stoppingToken);
    }

    private async Task MessageHandler(ProcessMessageEventArgs args)
    {
        string body = args.Message.Body.ToString();
        try
        {
            _logger.LogInformation($"Processing: {body}. Attempt: {args.Message.DeliveryCount}");

            // 1. SIMULATE BUSINESS LOGIC
            // If this throws, we go to catch
            await ProcessBusinessLogic(body);

            // 2. SUCCESS: Tell ASB "I'm done, remove it."
            await args.CompleteMessageAsync(args.Message);
        }
        catch (CustomTransientException ex)
        {
            // SCENARIO A: A known temporary issue (e.g., DB locked).
            // STRATEGY: Retry immediately (increment delivery count).
            // 'Abandon' puts it back in the queue instantly.
            _logger.LogWarning("Transient error. Retrying...");
            await args.AbandonMessageAsync(args.Message);
        }
        catch (JsonException ex)
        {
            // SCENARIO B: The data is corrupt. Retrying 10 times won't fix bad JSON.
            // STRATEGY: Kill it immediately. Move to DLQ manually.
            _logger.LogError("Poison data. Moving to DLQ.");
            await args.DeadLetterMessageAsync(args.Message, "InvalidJson", ex.Message);
        }
        catch (Exception ex)
        {
            // SCENARIO C: Unknown crash.
            // STRATEGY: Let it retry until MaxDeliveryCount (default 10) is hit.
            // DO NOT complete. DO NOT deadletter.
            // Just let the Lock expire or call Abandon.
            _logger.LogError(ex, "Unknown crash. Let auto-retry handle it.");
            await args.AbandonMessageAsync(args.Message);
        }
    }

    private Task ErrorHandler(ProcessErrorEventArgs args)
    {
        // This handles connection drops, authentication errors, etc.
        _logger.LogError(args.Exception, "Service Bus Infrastructure Error");
        return Task.CompletedTask;
    }
}

```

---

### Layer 3: Advanced Architect Patterns

There is a major flaw in the default ASB Retry behavior: **It is immediate.**
If your DB is down, and you have `MaxDeliveryCount = 10`, your app will hammer the queue 10 times in 500ms and then Dead Letter the message.

To fix this, we need **Delayed Retries** (Long Polling). The single biggest architectural pitfall in Azure Service Bus error handling. To be absolutely clear as an architect, here is the confirmation of your statement and the nuance you need to handle it properly.

### Option A: Schedule for later (The "Manual Backoff")

### 1. The Behavior of `AbandonAsync` (The Problem)

When you call `AbandonAsync` (or throw an exception that triggers an abandon):

- **Availability:** IMMEDIATE.
- **Result:** The message goes back to the queue head.
- **Consequence:** If your Database is down, and your code takes 100ms to fail, your application will pick up that **same message** and fail 10 times in **1 second** (assuming `MaxDeliveryCount = 10`).
- **Outcome:** The message goes to Dead Letter Queue (DLQ) in 1 second. Your system never gave the Database time to recover. This is called a **"Tight Loop Retry"**.

### 2. The Solution: `ScheduleMessageAsync` (The Pattern)

Since Azure Service Bus does **not** have a native "Abandon with Delay" feature (unlike AWS SQS, which allows changing visibility timeout), you **must** implement the "Clone & Schedule" pattern.

Here is the implementation strategy you must follow to make this work like a "Top Notch" architect:

### The Catch: The "DeliveryCount" Reset

When you create a **New** Scheduled Message, it is physically a brand new message on the server.

- **Side Effect:** The system `DeliveryCount` on this new message is **reset to 0** (or 1).
- **The Risk:** If you don't track retries manually, this loop can go on forever (Infinite Loop), costing you money and resources.

### The Architectural Fix: "Custom Retry Counter"

You must use `ApplicationProperties` (Headers) to track the *real* number of attempts.

### The "Perfect" Retry Code Block

Here is the snippet that solves the immediate retry problem while preventing infinite loops:

```csharp
public async Task HandleMessage(ProcessMessageEventArgs args)
{
    try
    {
        // Try to process business logic...
        throw new InvalidOperationException("DB is Down!");
    }
    catch (Exception ex)
    {
        ServiceBusMessage incomingMsg = args.Message;

        // 1. READ CUSTOM RETRY COUNTER
        // If the header doesn't exist, it's the 1st attempt.
        int currentRetry = 0;
        if (incomingMsg.ApplicationProperties.ContainsKey("X-Custom-Retry-Count"))
        {
            currentRetry = (int)incomingMsg.ApplicationProperties["X-Custom-Retry-Count"];
        }

        // 2. CHECK THRESHOLD (The Circuit Breaker)
        if (currentRetry >= 5)
        {
            // We tried 5 times with delays. It's truly dead.
            // DeadLetter the ORIGINAL message.
            await args.DeadLetterMessageAsync(incomingMsg, "MaxDelayedRetries", "DB is still down");
            return;
        }

        // 3. CALCULATE DELAY (Exponential Backoff)
        // Attempt 0: 5s, Attempt 1: 10s, Attempt 2: 20s...
        double seconds = 5 * Math.Pow(2, currentRetry);
        var scheduledTime = DateTimeOffset.UtcNow.AddSeconds(seconds);

        // 4. CLONE THE MESSAGE
        // We must manually copy the Body and Properties to the new message
        ServiceBusMessage delayedMsg = new ServiceBusMessage(incomingMsg.Body)
        {
            ContentType = incomingMsg.ContentType,
            Subject = incomingMsg.Subject,
            MessageId = incomingMsg.MessageId // Optional: Keep same ID for tracing
        };

        // Copy all existing user properties (Important!)
        foreach (var prop in incomingMsg.ApplicationProperties)
        {
            delayedMsg.ApplicationProperties.Add(prop.Key, prop.Value);
        }

        // 5. UPDATE THE CUSTOM COUNTER
        delayedMsg.ApplicationProperties["X-Custom-Retry-Count"] = currentRetry + 1;

        // 6. EXECUTE THE SWAP
        // A. Send the "Future" message
        ServiceBusSender sender = _client.CreateSender(args.EntityPath);
        await sender.ScheduleMessageAsync(delayedMsg, scheduledTime);

        // B. Complete (Delete) the "Current" message so it doesn't retry immediately
        await args.CompleteMessageAsync(incomingMsg);

        // C. (Optional) Log it
        _logger.LogWarning($"DB Down. Scheduling retry #{currentRetry + 1} in {seconds} seconds.");
    }
}

```

### Summary Comparison

| Action | Availability | Delivery Count | Best Use Case |
| --- | --- | --- | --- |
| **AbandonAsync()** | **Immediate** (ms) | Increments System `DeliveryCount` | **Network Blips** or extremely transient errors. |
| **Schedule / Complete** | **Delayed** (Seconds/Mins) | **Resets** (Must track manually) | **Infrastructure Failures** (DB Down, 3rd Party API offline). |

You are now managing the queue, rather than letting the queue manage you.

### Option B: Client-side SDK (RetryOptions in Processor)

The Service Bus Processor does have a retry option for the handler itself, but it keeps the connection open and holds the lock. Use this sparingly as it can starve other threads if retries take a long time.

---

### Summary Checklist for Architects

1. **Configure `ServiceBusRetryOptions`**: Set this to `Exponential` to handle network blips gracefully.
2. **Define `MaxDeliveryCount`**: In your Infrastructure (Terraform/Bicep), set this to 5 or 10.
3. **Handle Serialization Errors**: Immediately `DeadLetterAsync`. Do not retry bad data.
4. **Handle Transient Logic Errors**: Use `AbandonAsync` to let the broker retry standard failures.
5. **Handle Long Outages**: Do not rely on `DeliveryCount` if you need to wait 5 minutes between retries. Use `ScheduleMessageAsync`.