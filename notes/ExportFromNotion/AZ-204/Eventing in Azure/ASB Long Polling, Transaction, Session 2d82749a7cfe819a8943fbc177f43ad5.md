# ASB Long Polling, Transaction, Session

# **Long Polling vs. Push Mechanism: It's a Hybrid "Streaming" Model**

- You are right to question the mechanism. While you might read about "long polling" in some contexts, and the SDK can provide a "push-style" experience, neither term perfectly describes what happens under the hood.
- The primary protocol for modern Service Bus clients is **AMQP 1.0**, which is an efficient, connection-oriented binary protocol. Here's a more accurate breakdown:
    - **It is NOT traditional long polling:**
        - Your client doesn't simply make an HTTP request and wait for a response. Instead, the Service Bus SDK establishes a persistent TCP connection to the service.
    - **It is NOT a true push from the server:**
        - The Service Bus broker doesn't arbitrarily push messages to a client whenever it feels like it.
    - **It IS a client-controlled streaming pull model:**
        - The best way to describe it is a "streaming pull" or "credit-based flow control" model, which is a core feature of AMQP.
            1. **Persistent Connection:** The client SDK opens a persistent connection and a communication channel (an AMQP "link") to the queue or subscription.
            2. **Client Issues "Credits":** The client receiver tells the broker how many messages it's willing to accept at any given time. This is called issuing "credits."
            3. **Broker Streams Messages:** As long as the client has issued credits, the Service Bus broker will stream messages over the active connection as soon as they become available. These messages are placed into an in-memory buffer on the client side.
            4. **SDK Pulls from Buffer:** Your code, whether using a simple `ReceiveMessageAsync` call or the processor, then "pulls" messages from this local buffer.
- So, while your code *pulls* from the SDK's local buffer, the SDK itself receives messages via a highly efficient *stream* from the broker, which feels like a push. This avoids the overhead of repeated HTTP polling and gives you the performance of a persistent connection.

---

# **How to Achieve Transactions**

- Service Bus provides robust, atomic transactions that allow you to group multiple messaging operations together. If any single operation within the transaction fails, all completed operations in that scope are rolled back. This is critical for maintaining data integrity.
- Transactions are supported on the Standard and Premium tiers.
- **Key Concepts:**
    - **Execution Scope:**
        - All operations must occur within a single messaging entity (e.g., one queue).
    - **Cross-Entity Transactions (Send Via):**
        - A powerful feature where you can receive a message from one queue/subscription and send messages to other queues/topics, all within a single atomic transaction. This is achieved by designating a "transfer queue or topic."
- **Implementing a Transaction in .NET:**
    - Transactions are typically implemented using the `TransactionScope` class.
    
    ```csharp
    // using Azure.Messaging.ServiceBus;
    // using System.Transactions;
    
    await using var client = new ServiceBusClient("YOUR_CONNECTION_STRING");
    ServiceBusSender sender = client.CreateSender("myqueue");
    ServiceBusReceiver receiver = client.CreateReceiver("myqueue");
    
    // 1. Receive a message to process
    ServiceBusReceivedMessage receivedMessage = await receiver.ReceiveMessageAsync();
    
    if (receivedMessage != null)
    {
        try
        {
            // 2. Create a transaction scope
            using (var ts = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
            {
                Console.WriteLine($"Processing message: {receivedMessage.Body}");
    
                // 3. Perform multiple operations within the scope
    
                // Example: Send a related message
                var newMessage = new ServiceBusMessage("This is a related message.");
                await sender.SendMessageAsync(newMessage);
                Console.WriteLine("Sent a new related message.");
    
                // Example: Complete the original message
                await receiver.CompleteMessageAsync(receivedMessage);
                Console.WriteLine("Completed the original message.");
    
                // 4. If all operations succeed, complete the transaction
                ts.Complete();
                Console.WriteLine("Transaction committed.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error during transaction: {ex.Message}. Transaction will be rolled back.");
            // If an exception occurs, the transaction is automatically rolled back
            // and the original message lock will be released, making it available again.
        }
    }
    
    ```
    

---

# **How to Achieve Sessions**

- Message Sessions are a premium feature used to process related messages in a guaranteed **First-In, First-Out (FIFO)** order. All messages with the same SessionId are routed to the same receiver, which holds a lock on that session.
- Sessions are essential for scenarios where order is critical, like processing events for a specific e-commerce order or managing a workflow.
- **Key Concepts:**
    - **Session ID:**
        - The sender must set the `SessionId` property on each `ServiceBusMessage`.
    - **Session-Enabled Queue/Subscription:**
        - You must explicitly enable sessions when creating the queue or subscription in Azure. This cannot be changed later.
    - **Session Lock:**
        - A receiver "accepts" a session, which places an exclusive lock on it. No other receiver can process messages from that session until the first one releases it.
- **Implementing Sessions in .NET:**
    - You send a message with a session ID, and you receive it using a session-aware receiver.
- **Sending Session Messages:**
    
    ```csharp
    // using Azure.Messaging.ServiceBus;
    
    await using var client = new ServiceBusClient("YOUR_CONNECTION_STRING");
    ServiceBusSender sender = client.CreateSender("my-session-queue");
    
    // Group messages by a logical identifier, e.g., an order ID
    string sessionId = "order-123";
    
    // Create messages and assign the SessionId
    var message1 = new ServiceBusMessage("Step 1: Order Placed") { SessionId = sessionId };
    var message2 = new ServiceBusMessage("Step 2: Payment Processed") { SessionId = sessionId };
    var message3 = new ServiceBusMessage("Step 3: Order Shipped") { SessionId = sessionId };
    
    await sender.SendMessageAsync(message1);
    await sender.SendMessageAsync(message2);
    await sender.SendMessageAsync(message3);
    
    Console.WriteLine($"Sent 3 messages for session: {sessionId}");
    
    ```
    
- **Receiving Session Messages:**
    - The recommended way to process sessions is using the `ServiceBusSessionProcessor`. It simplifies the message loop and session management.
    
    ```csharp
    // using Azure.Messaging.ServiceBus;
    
    await using var client = new ServiceBusClient("YOUR_CONNECTION_STRING");
    
    var options = new ServiceBusSessionProcessorOptions
    {
        // The max number of sessions to process concurrently
        MaxConcurrentSessions = 5,
        AutoCompleteMessages = false
    };
    
    // Create a processor that is session-aware
    await using ServiceBusSessionProcessor processor = client.CreateSessionProcessor("my-session-queue", options);
    
    // Configure the message and error handlers
    processor.ProcessMessageAsync += async args =>
    {
        // The SessionId is available in the arguments
        Console.WriteLine($"[Session: {args.SessionId}] Received message: {args.Message.Body}");
    
        // We can complete, abandon, defer, or dead-letter the message
        await args.CompleteMessageAsync(args.Message);
    };
    
    processor.ProcessErrorAsync += args =>
    {
        Console.WriteLine(args.Exception.ToString());
        return Task.CompletedTask;
    };
    
    // Start processing
    await processor.StartProcessingAsync();
    
    Console.WriteLine("Waiting for session messages... Press any key to end.");
    Console.ReadKey();
    
    ```