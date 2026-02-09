# Multiple Output Bindings with Azure Functions in Isolated Worker Process Mode

# **Upgrading Azure Functions to .NET 7: Handling Multiple Output Bindings**

- **Context: Migration from In-Process to Isolated Worker**
    - I’ve been working on changing some Azure Functions from **.NET 6 using the “in-process” mode**, to **.NET 7 using the “isolated worker process” mode**.
- **The Challenge: Managing Multiple Outputs**
    - One of the big changes that I had to make was to the way I handle **multiple output bindings** from my functions.
    - Microsoft has a simple example on their *Guide for running C# Azure Functions in an isolated worker process* of changing to using a **POCO** to return more than one output binding.
        - In my case, I needed to output **two sets of data to a CosmosDB binding**.
- **The Scenario**
    - I’m going to avoid going into the details of what my data is, because it will overcomplicate it.
    - **Focus on this fact:**
        - There are **two separate collections** that we’re reading and writing data from.
        - We also return an object which happens to be a mix of both those collection types.
    - As a result of this simplification, the code looks rather convoluted, but hopefully, it gets the idea across!

---

# **1. The "Before" Approach (.NET 6 In-Process)**

- Here’s what I had before. As you can see, I have **two inputs** (for two different collections), and **two output bindings** (for the same two collections).
    - **Code Example:**
        
        ```csharp
        [FunctionName("GetMyData")]
        public async Task<ActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = "GetMyData/{partitionKey}")] HttpRequest req,
            string partitionKey,
            [CosmosDB(
                databaseName: "MyDatabaseName",
                collectionName: "MyFirstCollection",
                ConnectionStringSetting = "CosmosDBConnection")] IAsyncCollector<MyFirstCollectionType> myFirstCollectionOut,
            [CosmosDB(
                databaseName: "MyDatabaseName",
                collectionName: "MySecondCollection",
                ConnectionStringSetting = "CosmosDBConnection")] IAsyncCollector<MySecondCollectionType> mySecondCollectionOut,
            ILogger logger)
        {
            MyFirstCollectionType newItem = new MyFirstCollectionType(...);
            await myFirstCollectionOut.AddAsync(newItem);
        
            MySecondCollectionType newOtherItem = new MySecondCollectionType(...);
            await mySecondCollectionOut.AddAsync(newOtherItem);
        
            MySpecialType returnData = new MySpecialType(...);
            // returning one object which happens to be a merged version of the two types of data from above
        
            return new JsonResult(returnData);
        }
        
        ```
        

---

# **2. The "After" Approach (.NET 7 Isolated Worker)**

- **The Core Concept Change**
    - To migrate this to an **isolated worker process**, you need to return a **single plain class** that contains all the bindings you need, plus the actual `HttpResponseData` object.
    - **Data Structure Change:**
        - Previously I was able to write to an instance of an `IAsyncCollector<T>`.
        - Now I can just add my data to a `List<T>` and then return that.
- **The New Function Implementation**
    - **Code Example:**
        
        ```csharp
        [FunctionName("GetMyData")]
        public async Task<GetMyDataOutput> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = "GetMyData/{partitionKey}")] HttpRequestData req,
            string partitionKey,
            ILogger logger)
        {
            List<MyFirstCollectionType> myFirstCollectionOut = new List<MyFirstCollectionType>();
            List<MySecondCollectionType> mySecondCollectionOut = new List<MySecondCollectionType>();
        
            MyFirstCollectionType newItem = new MyFirstCollectionType(...);
            myFirstCollectionOut.Add(newItem);
        
            MySecondCollectionType newOtherItem = new MySecondCollectionType(...);
            mySecondCollectionOut.Add(newOtherItem);
        
            MySpecialType returnData = new MySpecialType(...);
            // returning one object which happens to be a merged version of the two types of data from above
        
            var response = req.CreateResponse(System.Net.HttpStatusCode.OK);
            await response.WriteAsJsonAsync(returnData);
        
            return new GetMyDataOutput()
            {
                MyFirstCollectionTypeOut = myFirstCollectionOut,
                MySecondCollectionTypeOut = mySecondCollectionOut,
                HttpResponse = response
            };
        }
        
        ```
        
- **The Output Class Definition (POCO)**
    - This class defines the structure of the return object, mapping properties to specific output bindings.
    - **Code Example:**
        
        ```csharp
        public class GetMyDataOutput
        {
            [CosmosDBOutput(
                databaseName: "MyDatabaseName",
                collectionName: "MyFirstCollection",
                ConnectionStringSetting = "CosmosDBConnection")]
            public IEnumerable<MyFirstCollectionType> MyFirstCollectionTypeOut { get; set; }
        
            [CosmosDBOutput(
                databaseName: "MyDatabaseName",
                collectionName: "MySecondCollection",
                ConnectionStringSetting = "CosmosDBConnection")]
            public IEnumerable<MySecondCollectionType> MySecondCollectionTypeOut { get; set; }
        
            public HttpResponseData HttpResponse { get; set; }
        }
        
        ```
        

---

# **Summary**

- **Conclusion on the Change**
    - Not so scary after all.
    - It actually makes it a lot **clearer** to me, because I can just look at the **returned object** to see all the things that are getting output.