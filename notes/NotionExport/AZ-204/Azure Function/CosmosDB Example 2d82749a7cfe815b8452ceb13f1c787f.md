# CosmosDB Example

# **Azure Cosmos DB Bindings in Azure Functions (Runtime 4.x, C#, Out-of-Process Worker)**

This comprehensive guide will make you an expert in using Azure Cosmos DB Triggers, Input, and Output Bindings with Azure Functions. We'll focus on the latest best practices for Runtime 4.x, C#, and the Out-of-Process worker model.

---

# **1. Understanding Azure Cosmos DB Bindings**

Azure Cosmos DB bindings allow your Azure Function to react to changes in a Cosmos DB container (Trigger), read data from a container (Input), and write data to a container (Output) without writing the boilerplate code for the Cosmos DB SDK.

### **Key Advantages:**

- **Reduced Boilerplate:** No need to manually create `CosmosClient` or handle connection strings.
- **Scalability:** Azure Functions runtime handles scaling based on your Cosmos DB activity.
- **Reliability:** Built-in retry mechanisms and error handling.
- **Cost-Effective:** Pay only for the compute used when your function runs.

### **Out-of-Process (Isolated Process) Model:**

In this model, your function app runs in a separate worker process from the Functions host. This offers several benefits:

- **Flexibility:** Use different .NET versions than the Functions host.
- **Reduced Conflicts:** Avoids dependency conflicts with the Functions host.
- **Improved Performance:** Can offer better startup times and memory usage.

---

# **2. Setup and Prerequisites**

Before you start, ensure you have:

- **Azure Subscription:** Required to create Cosmos DB and Azure Function resources.
- **Azure Cosmos DB Account:** A provisioned Cosmos DB account (SQL API recommended for this guide).
- **Visual Studio 2022:** With the "Azure development" workload installed.
- **Azure Functions Core Tools (v4.x):** For local development and testing.
- **Required NuGet Packages:**
    - `Microsoft.Azure.Functions.Worker`
    - `Microsoft.Azure.Functions.Worker.Sdk`
    - `Microsoft.Azure.Functions.Worker.Extensions.CosmosDB`
    - Add these to your `.csproj` file:
    
    ```xml
    <ItemGroup>
        <PackageReference Include="Microsoft.Azure.Functions.Worker" Version="1.21.0" />
        <PackageReference Include="Microsoft.Azure.Functions.Worker.Sdk" Version="1.16.4" />
        <PackageReference Include="Microsoft.Azure.Functions.Worker.Extensions.CosmosDB" Version="4.5.0" />
        <PackageReference Include="Microsoft.ApplicationInsights.WorkerService" Version="2.21.0" />
        <PackageReference Include="Microsoft.Azure.Functions.Worker.ApplicationInsights" Version="1.2.0" />
    </ItemGroup>
    
    ```
    

---

# **3. Azure Cosmos DB Trigger Binding**

The Cosmos DB Trigger allows your function to react to changes in a Cosmos DB container, acting as a change feed processor.

**Scenario:** Process new customer orders as they are added to a `SalesOrders` container.

### **Key Concepts:**

- **Lease Collection:** A separate collection used by the Functions runtime to maintain state and coordinate across instances, ensuring each change feed item is processed exactly once.
- **Connection String:** The connection string for your Cosmos DB account. Store it securely (e.g., in `local.settings.json` or Application Settings).

### **Function Code Example:**

```csharp
// Program.cs -- For Isolated Process
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;

var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureServices(s =>
    {
        s.AddApplicationInsightsTelemetryWorkerService();
        s.ConfigureFunctionsApplicationInsights();
    })
    .Build();

host.Run();

```

```csharp
// CosmosDbTriggerFunction.cs
using System.Collections.Generic;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace CosmosDbFunctionApp
{
    public class SalesOrder
    {
        public string Id { get; set; }
        public string OrderId { get; set; }
        public string CustomerId { get; set; }
        public double Amount { get; set; }
        public string Status { get; set; }
    }

    public class CosmosDbTriggerFunction
    {
        private readonly ILogger<CosmosDbTriggerFunction> _logger;

        public CosmosDbTriggerFunction(ILogger<CosmosDbTriggerFunction> logger)
        {
            _logger = logger;
        }

        [Function("ProcessSalesOrders")]
        public void Run(
            [CosmosDBTrigger(
                databaseName: "MyDatabase",
                containerName: "SalesOrders",
                Connection = "CosmosDbConnection", // Reference to app setting
                LeaseContainerName = "leases",
                CreateLeaseContainerIfNotExists = true)]
            IReadOnlyList<SalesOrder> input)
        {
            if (input != null && input.Count > 0)
            {
                _logger.LogInformation($"Processing {input.Count} new sales orders.");
                foreach (var order in input)
                {
                    _logger.LogInformation($"Order ID: {order.OrderId}, Customer ID: {order.CustomerId}, Amount: {order.Amount}, Status: {order.Status}");
                    // Implement your business logic here, e.g., send notifications, update inventory.
                }
            }
        }
    }
}

```

**local.settings.json (for local development):**

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated",
    "CosmosDbConnection": "AccountEndpoint=https://YOUR_COSMOSDB_ACCOUNT.documents.azure.com:443/;AccountKey=YOUR_COSMOSDB_KEY;"
  }
}

```

### **Explanation of Attributes:**

- `[CosmosDBTrigger(...)]`: Marks the parameter as a Cosmos DB Trigger.
    - `databaseName`: The name of your Cosmos DB database.
    - `containerName`: The name of the container to monitor for changes.
    - `Connection`: **Crucial!** This is the name of an app setting that holds your Cosmos DB connection string. **Never hardcore connection strings!**
    - `LeaseContainerName`: The name of the container to use for managing leases.
    - `CreateLeaseContainerIfNotExists`: If set to true, the lease container will be created automatically if it doesn't exist.
    - `StartFromBeginning`: (Optional) true to process all existing items from the beginning, false (default) to process new items only. Use with caution in production.
    - `FeedPollDelay`: (Optional) The delay in milliseconds between polls for new changes.
    - `MaxItemsPerInvocation`: (Optional) The maximum number of items to process in a single function invocation.

### **Becoming an Expert Tip:**

- **Error Handling:** Always wrap your processing logic in try-catch blocks within the loop to gracefully handle individual item failures without stopping the entire batch processing.
- **Idempotency:** Design your downstream systems to be idempotent. If a function is retried, ensure processing the same change multiple times doesn't cause issues.
- **Monitoring:** Utilize Azure Application Insights to monitor your function's performance, errors, and throughput.
- **Partitioning:** Be mindful of your Cosmos DB container's partitioning strategy. The change feed works best when changes are distributed across partitions.
- **Throughput:** Ensure your lease collection has enough provisioned throughput (RU/s) to handle the change feed processing.
- **Cold Start Optimization:** For very low-traffic triggers, consider using the consumption plan with pre-warmed instances or a premium plan.

---

# **4. Azure Cosmos DB Input Binding**

The Cosmos DB Input Binding allows your function to read one or more documents from a Cosmos DB container.

**Scenario:** Retrieve customer details based on an Id passed to an HTTP triggered function.

### **Key Concepts:**

- **Id Parameter:** For retrieving a single document, you'll often bind to an `id` parameter.
- **SQL Query:** For retrieving multiple documents or filtering, you can use a SQL query.

### **Function Code Example:**

```csharp
// CosmosDbInputFunction.cs
using System.Collections.Generic;
using System.Net;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace CosmosDbFunctionApp
{
    public class Customer
    {
        public string Id { get; set; }
        public string CustomerId { get; set; }
        public string Name { get; set; }
        public string Email { get; set; }
    }

    public class CosmosDbInputFunction
    {
        private readonly ILogger<CosmosDbInputFunction> _logger;

        public CosmosDbInputFunction(ILogger<CosmosDbInputFunction> logger)
        {
            _logger = logger;
        }

        [Function("GetCustomerById")]
        public HttpResponseData GetCustomerById(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "customer/{id}")] HttpRequestData req,
            string id,
            [CosmosDBInput(
                databaseName: "MyDatabase",
                containerName: "Customers",
                Connection = "CosmosDbConnection",
                Id = "{id}", // Binding Expression to get 'id' from route
                PartitionKey = "{id}")] // PartitionKey is often the same as Id for point reads
            Customer customer)
        {
            _logger.LogInformation($"Attempting to retrieve customer with ID: {id}");

            var response = req.CreateResponse(HttpStatusCode.OK);

            if (customer == null)
            {
                response.StatusCode = HttpStatusCode.NotFound;
                response.WriteString($"Customer with ID '{id}' not found.");
            }
            else
            {
                response.Headers.Add("Content-Type", "application/json; charset=utf-8");
                response.WriteString(JsonConvert.SerializeObject(customer));
            }

            return response;
        }

        [Function("SearchCustomers")]
        public HttpResponseData SearchCustomers(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "customers")] HttpRequestData req,
            [CosmosDBInput(
                databaseName: "MyDatabase",
                containerName: "Customers",
                Connection = "CosmosDbConnection",
                SqlQuery = "SELECT * FROM c WHERE c.Name = {Query.name}")] // Binding Expression for SQL Query
            IEnumerable<Customer> customers)
        {
            _logger.LogInformation($"Searching for customers.");

            var response = req.CreateResponse(HttpStatusCode.OK);
            response.Headers.Add("Content-Type", "application/json; charset=utf-8");
            response.WriteString(JsonConvert.SerializeObject(customers));

            return response;
        }
    }
}

```

### **Explanation of Attributes:**

- `[CosmosDBInput(...)]`: Marks the parameter as a Cosmos DB Input.
    - `databaseName`: The name of your Cosmos DB database.
    - `containerName`: The name of the container to read from.
    - `Connection`: App setting reference for the connection string.
    - `Id`: **Binding Expression!** Specifies the document id to retrieve. Can come from route data (`{id}`), query strings (`{Query.paramName}`), or other binding sources.
    - `PartitionKey`: **Crucial for performance!** If your container is partitioned, providing the `PartitionKey` for a point read (`Id`) significantly improves performance and reduces RU consumption. It can also be a binding expression.
    - `SqlQuery`: **Binding Expression!** A SQL query to retrieve multiple documents. Parameters in the query can also be binding expressions.
    - `PreferredLocations`: (Optional) A comma-separated list of preferred Cosmos DB regions.

### **Binding Expression Examples:**

- `{id}`: Gets the value from a route parameter named `id`.
- `{Query.name}`: Gets the value from a query string parameter named `name`.
- `{Headers.x-custom-header}`: Gets the value from an HTTP header.
- `{data.someField}`: If your trigger provides a JSON payload, you can extract values from it.

### **Becoming an Expert Tip:**

- **Point Reads vs. Queries:** Always prefer point reads (using `Id` and `PartitionKey`) over SQL queries when you know the exact document ID and partition key, as they are significantly more performant and cheaper.
- **Indexing:** Ensure your Cosmos DB container has appropriate indexing policies for the fields you're querying.
- **Error Handling:** The input binding will return `null` if a single document is not found. For queries, it will return an empty collection. Handle these cases gracefully.
- **Large Result Sets:** If your queries might return a large number of documents, consider implementing pagination or using a Cosmos DB SDK directly for more control.
- **Security:** Be cautious when constructing SQL queries using user-provided input to prevent SQL injection vulnerabilities. Validate and sanitize all input.

---

# **5. Azure Cosmos DB Output Binding**

The Cosmos DB Output Binding allows your function to write new documents or update existing ones in a Cosmos DB container.

**Scenario:** Create a new audit log entry after processing a sales order.

### **Key Concepts:**

- `ICollector<T>` or `T`: You can bind to a collection to write multiple documents or a single object to write one.
- **Idempotency (for updates):** If you're updating documents, ensure your logic can handle potential retries.

### **Function Code Example:**

```csharp
// CosmosDbOutputFunction.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace CosmosDbFunctionApp
{
    public class AuditLogEntry
    {
        public string Id { get; set; } = System.Guid.NewGuid().ToString();
        public string EventType { get; set; }
        public string EntityId { get; set; }
        public string Message { get; set; }
        public System.DateTime Timestamp { get; set; } = System.DateTime.UtcNow;
    }

    public class CosmosDbOutputFunction
    {
        private readonly ILogger<CosmosDbOutputFunction> _logger;

        public CosmosDbOutputFunction(ILogger<CosmosDbOutputFunction> logger)
        {
            _logger = logger;
        }

        [Function("CreateAuditLog")]
        [CosmosDBOutput(
            databaseName: "MyDatabase",
            containerName: "AuditLogs",
            Connection = "CosmosDbConnection",
            CreateIfNotExists = true, // Creates the container if it doesn't exist
            PartitionKey = "/eventType")] // Specifies the partition key path for new documents
        public async Task<AuditLogEntry> CreateAuditLog(
            [HttpTrigger(AuthorizationLevel.Function, "post", Route = "audit")] HttpRequestData req,
            FunctionContext context)
        {
            _logger.LogInformation("C# HTTP trigger function processed an audit request.");

            string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
            dynamic data = JsonConvert.DeserializeObject(requestBody);

            string eventType = data?.eventType;
            string entityId = data?.entityId;
            string message = data?.message;

            if (string.IsNullOrEmpty(eventType) || string.IsNullOrEmpty(entityId))
            {
                // Handle bad request
                // In a real scenario, you'd want to return an HttpResponseData with BadRequest status
                // But for output binding simplicity here, we might just throw or return null
               throw new System.Exception("Invalid Input");
            }

            var newLog = new AuditLogEntry
            {
                EventType = eventType,
                EntityId = entityId,
                Message = message
            };

            _logger.LogInformation($"Creating audit log for EventType: {eventType}");

            // The return value will be written to Cosmos DB
            return newLog;
        }

        // Example combining Trigger and Output binding
        [Function("ProcessOrderAndLog")]
        [CosmosDBOutput(
            databaseName: "MyDatabase",
            containerName: "ProcessedOrders",
            Connection = "CosmosDbConnection",
            CreateIfNotExists = true)]
        public IEnumerable<SalesOrder> ProcessOrderAndLog(
            [CosmosDBTrigger(
                databaseName: "MyDatabase",
                containerName: "SalesOrders",
                Connection = "CosmosDbConnection",
                LeaseContainerName = "leases")]
            IReadOnlyList<SalesOrder> input,
            FunctionContext context)
        {
            _logger.LogInformation($"Processing {input.Count} sales orders for logging.");
            var processedOrders = new List<SalesOrder>();

            foreach (var order in input)
            {
                _logger.LogInformation($"Marking order {order.OrderId} as processed.");
                order.Status = "Processed"; // Update status
                // Add to the list to be written to the 'ProcessedOrders' container
                processedOrders.Add(order);
            }

            // All items in the returned IEnumerable will be written to the output container.
            return processedOrders;
        }
    }
}

```

### **Explanation of Attributes:**

- `[CosmosDBOutput(...)]`: Marks the return value or an `out` parameter as a Cosmos DB Output.
    - `databaseName`: The name of your Cosmos DB database.
    - `containerName`: The name of the container to write to.
    - `Connection`: App setting reference for the connection string.
    - `CreateIfNotExists`: If true, the container will be created automatically if it doesn't exist. **Use with caution in production environments.**
    - `PartitionKey`: **Crucial!** Specifies the partition key path for new documents. This is a static string, e.g., `"/category"`. If you need a dynamic partition key from the document, you should use the Cosmos DB SDK directly or ensure the PartitionKey is part of the document being written.
    - `Throughput`: (Optional) Specifies the throughput (RU/s) for a newly created container (only effective if `CreateIfNotExists` is true).

### **Becoming an Expert Tip:**

- **Return Value vs. IAsyncCollector:**
    - **Return Value:** Simplest for writing a single document or a collection of documents. The function's return type directly maps to the output.
    - **IAsyncCollector<T>:** For more advanced scenarios where you need to write documents conditionally or asynchronously throughout your function's execution. This offers more control.
    
    ```csharp
    // Example with IAsyncCollector
    [Function("CreateAuditLogCollector")]
    public async Task CreateAuditLogCollector(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = "audit-collector")] HttpRequestData req,
        [CosmosDBOutput(
            databaseName: "MyDatabase",
            containerName: "AuditLogs",
            Connection = "CosmosDbConnection")]
        IAsyncCollector<AuditLogEntry> outputCollector) // Use IAsyncCollector
    {
        // ... (parse request body)
    
        var newLog = new AuditLogEntry { /* populate properties */ };
        await outputCollector.AddAsync(newLog); // Add document to the collector
    
        // You can add multiple documents here
        await req.CreateResponse(System.Net.HttpStatusCode.Created);
    }
    
    ```
    
- **Upsert Behavior:** If a document with the same `id` already exists in the container, the output binding will by default **replace** the existing document. This is an upsert operation.
- **Partition Key Consistency:** Ensure that the `PartitionKey` attribute, if specified, aligns with the actual partition key defined for your Cosmos DB container. If the output document itself contains the partition key, the binding will correctly use it.
- **Throughput Considerations:** Be mindful of the RU/s consumed by your writes. Batching writes (using `IEnumerable<T>`) can sometimes be more efficient than many individual writes.

---

# **6. Binding Expressions in Depth**

Binding expressions are powerful features that allow you to dynamically set property values in your bindings based on information from the function's trigger, environment, or other sources.

**Syntax:** `{Source.Property}` or `{Property}`

**Common Sources:**

- **Trigger Data:**
    - `{id}` (from route parameter `id` in `[HttpTrigger(..., Route = "api/{id}")]`)
    - `{name}` (from HTTP query string `?name=...` or route parameter)
    - `{queueTrigger}` (for Queue Storage Trigger, the message content itself)
    - `{data.field}` (for JSON payloads from triggers like Event Grid, Cosmos DB, Queue)
- **HTTP Request:**
    - `{Query.parameterName}`: Value from the query string (e.g., `{Query.userId}` for `?userId=123`).
    - `{Headers.headerName}`: Value from an HTTP header (e.g., `{Headers.x-api-key}`).
- **Environment Variables / App Settings:**
    - `%AppSettingName%`: The value of an application setting or environment variable. Used directly in the attribute value (e.g., `Connection = "%CosmosDbConnection"`), but `Connection = "CosmosDbConnection"` is generally preferred as it points to the **name** of the app setting.

**Examples from above:**

- **Input Binding Id:** `Id = "{id}"` - Retrieves the `id` from the HTTP route parameter.
- **Input Binding SqlQuery:** `SqlQuery = "SELECT * FROM c WHERE c.Name = {Query.name}"` - Uses the `name` from the HTTP query string in the SQL query.
- **Trigger Connection:** `Connection = "CosmosDbConnection"` - Refers to the app setting named `CosmosDbConnection`.

**Becoming an Expert Tip:**

- **Debugging:** When binding expressions don't work as expected, check your trigger's payload structure and the exact casing of properties.
- **Complex Payloads:** For complex JSON payloads, you might need to deserialize the payload manually within your function to extract specific values before passing them to an output binding.
- **Security:** Be extremely careful when using binding expressions directly from untrusted input (like HTTP query parameters) in sensitive operations like `Id` for lookups or `SqlQuery` values. Always validate and sanitize input if there's any risk.

---

# **7. Deployment to Azure**

1. **Create Azure Resources:**
    - Azure Cosmos DB account (if not already done).
    - Azure Function App.
2. **Configure Application Settings:**
    - Go to your Function App in the Azure Portal.
    - Navigate to "Configuration" -> "Application settings".
    - Add an application setting named `CosmosDbConnection` with the primary connection string from your Cosmos DB account.
    - Add `FUNCTIONS_WORKER_RUNTIME` with value `dotnet-isolated`.
3. **Deploy your Function App:**
    - From Visual Studio, right-click your project and select "Publish".
    - Choose "Azure" -> "Azure Function App (Windows/Linux)" and follow the prompts to publish to your created Function App.

---

# **8. Troubleshooting Common Issues**

- **CosmosDbConnection not found:** Double-check the spelling of the `Connection` attribute and the app setting in Azure Portal/`local.settings.json`.
- **Lease container issues:** Ensure the lease container is correctly named and has enough RU/s. Check the Function App logs for errors related to lease acquisition.
- **Permissions:** Your Function App's managed identity (or whatever identity is used) needs appropriate permissions to Cosmos DB (e.g., Cosmos DB Built-in Data Contributor role).
- **Partition Key Mismatch:** If you're getting errors about partition keys, ensure your `PartitionKey` attribute value in the binding correctly matches the path defined in your Cosmos DB container.
- **CreateIfNotExists in Production:** Be cautious using `CreateIfNotExists = true` in production, as it can inadvertently create containers if names are misspelled. Manage container creation via Infrastructure as Code (IaC) or manual setup.
- **Data Types:** Ensure the data types of your C# model (`SalesOrder`, `Customer`, `AuditLogEntry`) match the structure of your Cosmos DB documents.

---

# **9. When to use Bindings vs. Cosmos DB SDK**

**Use Bindings When:**

- You need simple CRUD operations (create, read single, read collection).
- You want to react to the change feed without managing the change feed processor explicitly.
- You prefer a more declarative approach.
- Performance is good enough for your scenario.

**Use Cosmos DB SDK (with Dependency Injection) When:**

- You need fine-grained control over Cosmos DB operations (e.g., batch operations, transactional batches).
- You need complex queries with aggregations or specific query options not supported by `SqlQuery` binding.
- You need to handle specific error codes or retry policies differently.
- You want to work with different consistency levels dynamically.
- You need to manage connections and client instances more explicitly.
- For very high-performance scenarios where every millisecond and RU matters, as the SDK offers the most control.

**Example of using Cosmos DB SDK (Isolated Process):**

1. **Register CosmosClient in Program.cs:**
    
    ```csharp
    using Microsoft.Azure.Cosmos;
    
    var host = new HostBuilder()
        .ConfigureFunctionsWorkerDefaults()
        .ConfigureServices(s =>
        {
            s.AddSingleton(new CosmosClient(
                Environment.GetEnvironmentVariable("CosmosDbConnection"),
                new CosmosClientOptions() { ApplicationName = "MyFunctionApp" }));
            // Other services...
        })
        .Build();
    
    ```
    
2. **Inject CosmosClient into your function:**
    
    ```csharp
    public class CosmosDbSdkFunction
    {
        private readonly CosmosClient _cosmosClient;
        private readonly ILogger<CosmosDbSdkFunction> _logger;
    
        public CosmosDbSdkFunction(CosmosClient cosmosClient, ILogger<CosmosDbSdkFunction> logger)
        {
            _cosmosClient = cosmosClient;
            _logger = logger;
        }
    
        [Function("CreateItemWithSdk")]
        public async Task<HttpResponseData> Run(
            [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req)
        {
            // ... parse request body for a new item
    
            var database = _cosmosClient.GetDatabase("MyDatabase");
            var container = database.GetContainer("Items");
    
            var newItem = new { id = Guid.NewGuid().ToString(), Name = "SDK Item" };
            await container.CreateItemAsync(newItem, new PartitionKey(newItem.id));
    
            var response = req.CreateResponse(System.Net.HttpStatusCode.Created);
            response.WriteString("Item created using SDK.");
            return response;
        }
    }
    
    ```
    

---

By mastering these concepts, binding expressions, and knowing when to use which approach, you'll be well on your way to becoming an Azure Cosmos DB and Functions expert!

Here's an illustrative image of the concept:
 

![pic.jpg](CosmosDB%20Example/pic.jpg)