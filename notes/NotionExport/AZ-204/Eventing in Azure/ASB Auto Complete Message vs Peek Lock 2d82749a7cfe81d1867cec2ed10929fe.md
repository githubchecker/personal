# ASB Auto Complete Message vs Peek Lock

# **What is AutoCompleteMessages?**

- **AutoCompleteMessages** is a **convenience feature** provided by the Azure Service Bus SDK's processor clients (`ServiceBusProcessor` and `ServiceBusSessionProcessor`).
- When `AutoCompleteMessages = true` (which is the default setting in older versions of the SDK, but often set explicitly now), the processor essentially wraps your message handler code in a hidden try...catch block.
    - **How it works:**
        1. The processor receives a message and passes it to your handler function (e.g., `ProcessMessageAsync`).
        2. It then waits for your handler to complete.
        3. **If your handler function finishes without throwing an exception**, the processor automatically calls `CompleteMessageAsync()` on the message for you. This tells the Service Bus broker that the message was processed successfully and can be deleted.
        4. **If your handler function throws an exception**, the processor automatically calls `AbandonMessageAsync()` on the message. This releases the lock and makes the message immediately available for another receiver to try processing.
- **Pros of AutoCompleteMessages = true:**
    - **Simplicity:** It reduces boilerplate code. You can focus solely on your business logic without worrying about message completion.
- **Cons of AutoCompleteMessages = true:**
    - **Loss of Control:** You cannot perform more complex settlement actions like dead-lettering or deferring a message.
    - **Risk of Message Loss:** If your process crashes *after* your handler function completes but *before* the processor can call `CompleteMessageAsync`, the message lock might expire, and the message could be delivered again, potentially leading to duplicate processing. This is a subtle but important race condition.

---

# **How to Not Remove the Message Until Confirmation (The Peek-Lock Pattern)**

- Your second question, *"is it possible to not remove the message until the receiver sends confirmation?"*, is the very definition of the **PeekLock receive mode**. This is the default and most common way to interact with Service Bus for reliable messaging.
- When you set `AutoCompleteMessages = false`, you are taking full manual control over this PeekLock pattern. This is the **recommended approach for all production applications**.
- Here is the lifecycle of a message in PeekLock mode:
    1. **Peek and Lock:** The receiver (your processor) asks the queue for a message. The Service Bus broker finds a message, makes it invisible to other receivers by placing a lock on it, and sends it to your processor. **The message is NOT deleted from the queue.**
    2. **Process:** Your message handler code executes its business logic using the message's content.
    3. **Settle:** This is the crucial step where **you, the receiver, send the confirmation**. You must explicitly tell the broker what to do with the message by calling one of the following methods:
        - `CompleteMessageAsync(message)`: **This is the confirmation.** You are telling the broker, "I have successfully processed this message, you can now permanently delete it from the queue."
        - `AbandonMessageAsync(message)`: You are telling the broker, "I failed to process this message, but it's not poison. Release the lock so another receiver (or myself) can try again immediately." The message's delivery count is incremented.
        - `DeadLetterMessageAsync(message, reason)`: You are telling the broker, "This message is unprocessable (e.g., malformed data, invalid ID). Move it to the special Dead-Letter Queue (DLQ) so it doesn't block processing of other messages."
        - `DeferMessageAsync(message)`: A special case where you tell the broker, "I can't process this message right now, but I will need to later. Hold onto it, but hide it from normal receives. I will fetch it later using its unique sequence number."
- If your processor crashes or the lock duration expires before you settle the message, the lock is automatically released, and the message becomes visible again for another receiver to process. This ensures "at-least-once" delivery.

---

# **Code Example: Manual Control (`AutoCompleteMessages = false`)**

- This is the robust, production-ready pattern.
    
    ```csharp
    // using Azure.Messaging.ServiceBus;
    
    await using var client = new ServiceBusClient("YOUR_CONNECTION_STRING");
    
    // Set AutoCompleteMessages to false to take manual control
    var options = new ServiceBusProcessorOptions
    {
        AutoCompleteMessages = false,
        MaxConcurrentCalls = 1 // Process one message at a time
    };
    
    await using ServiceBusProcessor processor = client.CreateProcessor("myqueue", options);
    
    // Configure the message handler
    processor.ProcessMessageAsync += async args =>
    {
        ServiceBusReceivedMessage message = args.Message;
        Console.WriteLine($"Received message: {message.Body}");
    
        try
        {
            // Your business logic here...
            // e.g., save to a database, call another API, etc.
            bool isSuccessful = ProcessMyData(message);
    
            if (isSuccessful)
            {
                // This is the confirmation. The message will be deleted.
                await args.CompleteMessageAsync(message);
                Console.WriteLine("Message completed.");
            }
            else
            {
                // The message is malformed, send it to the DLQ.
                await args.DeadLetterMessageAsync(message, "InvalidData", "The message content was not valid.");
                Console.WriteLine("Message dead-lettered.");
            }
        }
        catch (Exception ex)
        {
            // Something went wrong during processing. Abandon the message to retry.
            Console.WriteLine($"Error processing message: {ex.Message}. Abandoning.");
            await args.AbandonMessageAsync(message);
        }
    };
    
    // Configure the error handler for the processor itself
    processor.ProcessErrorAsync += args =>
    {
        Console.WriteLine(args.Exception.ToString());
        return Task.CompletedTask;
    };
    
    // Start the processor
    await processor.StartProcessingAsync();
    
    Console.WriteLine("Waiting for messages... Press any key to end.");
    Console.ReadKey();
    
    await processor.StopProcessingAsync();
    
    ```
    

---

# **Summary**

| Setting | How it Works | Reliability | Best For |
| --- | --- | --- | --- |
| **AutoCompleteMessages = true** | SDK automatically Completes on success or Abandons on exception. | Good, but less control. Risk of message loss on process crash. | Quick demos, simple fire-and-forget tasks where a rare duplicate is acceptable. |
| **AutoCompleteMessages = false** | You have full manual control to Complete, Abandon, DeadLetter, or Defer. | **Excellent.** Provides "at-least-once" delivery and full control. | **All production applications.** Complex workflows, transactional logic, and any scenario where message loss is unacceptable. |