# Azure Functions Triggers vs. Input Bindings

- Azure Functions is a serverless compute service that allows you to write event-driven code. Two important concepts in this platform are Triggers and Input Bindings, which often confuse developers because both deal with connecting a function to external resources. However, they serve distinct purposes in the Azure Functions ecosystem.
- **What is an Azure Function Trigger?**
    - A Trigger is the **event that starts the execution** of an Azure Function. In other words, the function runs only when the trigger event occurs. Every Azure Function must have **exactly one trigger**.
    - **Examples include:**
        - An **HTTP request** (HTTP Trigger)
        - A **new message** added to a queue (Queue Trigger)
        - A **timer firing** on a schedule (Timer Trigger)
        - A **blob being created** or updated in Blob Storage (Blob Trigger)
    - The trigger binds your function to the event source and provides data to the function related to that event.
- **What is an Azure Function Input Binding?**
    - An Input Binding **provides data to the function** at the time it is triggered without the function needing to explicitly fetch this data manually. Input bindings let you declaratively connect to other Azure services or external data sources so that the data is automatically available to your function when it runs.
    - **For example, you might:**
        - Bind to a **Cosmos DB document** (to read the document)
        - Bind to a **table storage entity**
        - Bind to a **blob or file** to read additional data
    - Unlike triggers, input bindings **do not start your function**; they only pass data into the function at runtime.
- **Summary of Differences**

| Aspect | Trigger | Input Binding |
| --- | --- | --- |
| **Purpose** | Starts the function execution | Provides additional input data to function |
| **Function Requirement** | **Exactly one** trigger per function | **Zero or more** input bindings allowed |
| **Examples** | HTTP request, Timer, Queue message, Blob event | Cosmos DB document, Table storage, Blob |
| **Action** | **Activates** the function | **Supplies data** used by the function |
- **Why Use Both?**
    - A function could be triggered by an HTTP request (HTTP Trigger) but might also need to read data from other resources like a database or storage blob during its execution. Input bindings let you **declaratively connect** to those data sources seamlessly without writing explicit code to fetch the data.
- **Example**
    
    ```csharp
    public static class FunctionExample
    {
        [FunctionName("BlobTriggeredFunction")]
        public static void Run(
            // Trigger
            [BlobTrigger("samples-workitems/{name}")] Stream myBlob,
    
            // Input Binding
            [CosmosDB(
                databaseName: "TestDb",
                collectionName: "Items",
                Id = "{name}",
                ConnectionStringSetting = "CosmosDBConnection")] Item item,
    
            ILogger log)
        {
            log.LogInformation($"Blob trigger fired for {name}.");
            log.LogInformation($"CosmosDB item loaded: {item?.Id}");
        }
    }
    
    ```
    
    - Here, the function runs when a blob is uploaded or changed (**BlobTrigger**), and it also retrieves a corresponding document from Cosmos DB (**Input Binding**) to use within the function.
- **In conclusion:**
    - **Triggers** start your function based on an event.
    - **Input Bindings** bring data into your function during execution without extra code.
    - They are related but not the same and serve complementary roles in Azure Functions.