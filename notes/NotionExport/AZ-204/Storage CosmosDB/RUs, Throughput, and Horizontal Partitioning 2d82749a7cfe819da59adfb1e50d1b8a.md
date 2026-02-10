# RUs, Throughput, and Horizontal
Partitioning

Of course. These three concepts—**RUs, Throughput, and Horizontal Partitioning**—are the holy trinity of Azure Cosmos DB. Understanding how they interrelate is the single most important skill for designing a performant and cost-effective Cosmos DB solution. A lack of understanding here is the #1 cause of performance problems and budget overruns.

Let's break them down in a logical order, as each one builds upon the last.

---

# **1. Horizontal Partitioning: The Foundation of Scale**

- **What is it?**
    - Horizontal partitioning (also known as sharding) is the process of breaking up your large dataset into smaller, more manageable chunks called **partitions**. Cosmos DB stores these partitions across many different physical servers under the hood. This is the fundamental mechanism that allows Cosmos DB to offer virtually unlimited storage and throughput.
- **How it Works: The Partition Key**
    - When you create a container in Cosmos DB, you are forced to choose a **Partition Key**. This is a property from your JSON documents (e.g., userID, deviceId, city) that Cosmos DB will use as an address to decide which partition an item belongs to.
        - All documents with the **same partition key value** are guaranteed to be stored together in the same **logical partition**.
        - A logical partition is a group of items with the same partition key. It has a size limit of 20 GB.
        - Cosmos DB automatically and transparently maps these logical partitions to many different physical partitions to distribute the load.
- **Analogy:** Imagine a massive library with millions of books (your data).
    - **Without partitioning:** All books are in one giant, unsorted pile. Finding a book is impossible.
    - **With partitioning:** The library is organized into sections based on the author's last name (the **Partition Key**). If you're looking for a book by "Smith," you know exactly which section to go to, making the search incredibly fast.
- **The Developer's Critical Choice**
    - Your single most important design decision is choosing a **good partition key**.
        - A **GOOD** key has **high cardinality** (many unique values) and **evenly distributes requests**.
            - Examples: userID, productId, deviceId.
        - A **BAD** key has **low cardinality** or creates a "hot spot." Example: Using "country" as a key for a US-based app. 99% of your requests will go to the "USA" partition, overwhelming it, while all other partitions sit idle. This is a "**hot partition**" and it will cause massive throttling and performance issues.

---

# **2. Request Units (RUs): The Currency of Cosmos DB**

- **What is it?**
    - A Request Unit (RU) is an abstract, normalized unit that represents the cost of performing an operation in Cosmos DB. It is a composite measure of the **CPU, memory, and IOPS** required to fulfill a request.
    - Instead of thinking about VMs, cores, and disk speeds, you just think about RUs. This is the currency you use to "pay" for your database operations.
- **How it Works: Everything has a price**
    - Every single action you take against Cosmos DB has a predictable RU cost:
        - **Reading a small item (1KB) by its ID and Partition Key (a "point read"):** ~1 RU (very cheap)
        - **Writing a new item (1KB):** ~5-10 RUs (writes are more expensive)
        - **Querying for data:** The cost varies dramatically.
            - A query that targets a single partition is relatively cheap.
            - A query that has to search across *all partitions* (a "**cross-partition query**") is extremely expensive.
- **Analogy:** Think of RUs like electricity usage (kWh). Every appliance in your house (read, write, query) consumes a certain amount of power. A small lightbulb (point read) uses very little. A big air conditioner (complex query) uses a lot.
- **The Developer's Goal**
    - Your goal as a developer is to write efficient code that consumes the fewest RUs possible. You can see the RU charge for every single operation in the response headers from the Cosmos DB SDK, allowing you to measure and optimize your code. **Efficient queries that use the partition key are the #1 way to reduce RU cost.**

---

# **3. Throughput: Your RU Budget per Second**

- **What is it?**
    - Throughput is the amount of processing power you reserve for your database or container, measured in **Request Units per second (RU/s)**. This is your budget of RUs that replenishes every single second.
    - If your combined operations in a given second consume more RUs than the throughput you've provisioned, Cosmos DB will reject subsequent requests with an **HTTP 429 "Too Many Requests"** error. This is called **throttling**.
- **Analogy:** Your throughput is your **monthly salary** (4,000 RU/s). The RUs are the **money** you spend. You get a new salary deposit every second. If you try to spend 5,000 in one second, your card gets declined (429 error).
- **How to Handle Throttling (Crucial for Developers)**
    - The Cosmos DB SDKs have built-in retry logic, but you should still be prepared to handle these exceptions gracefully in your code.
    
    ```csharp
    try
    {
        await container.CreateItemAsync(myItem);
    }
    catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
    {
        // Log the throttling event
        Console.WriteLine($"Throttled! Waiting for {ex.RetryAfter?.TotalSeconds} seconds before retrying.");
    
        // Optionally, wait for the suggested duration and retry the operation.
        // The SDK often handles this automatically, but you might want custom logic.
        await Task.Delay(ex.RetryAfter ?? TimeSpan.FromSeconds(2));
    
        // retry logic here...
    }
    
    ```
    
- **Provisioning Models (How you buy your throughput)**
    1. **Standard (Manual):** You set a fixed number of RU/s (e.g., 1000 RU/s). The cost is predictable. Best for stable, predictable workloads.
    2. **Autoscale:** You set a *maximum* RU/s, and Cosmos DB automatically scales the throughput between 10% of the max and the max, based on your application's real-time needs. Best for spiky, unpredictable workloads. You pay for the maximum, but at a different rate, so it's often more cost-effective than provisioning for peak manually.
    3. **Serverless:** You don't provision any throughput. You pay a slightly higher price per RU for each operation. Best for dev/test, or applications with very low or infrequent traffic.

---

# **Putting It All Together: A Complete Story**

1. **Design (Partitioning):** You're building an e-commerce site. You create a "ShoppingCart" container and choose `userID` as the **Partition Key**. This ensures that all items for a single user's cart are stored together for fast retrieval.
2. **Provision (Throughput):** You anticipate a moderate amount of traffic, so you provision **1,000 RU/s** of Autoscale throughput on the container.
3. **Execute (RUs):**
    - A user logs in and views their cart. Your code executes a query: `SELECT * FROM c WHERE c.userID = 'user123'`. Because this query includes the partition key, it's very efficient and only targets one partition. The operation costs **3 RUs**.
    - Your RU/s budget for this second is now 997.
    - During a flash sale, 200 users all add an item to their cart at the exact same second. Each write operation costs 7 RUs.
    - Total required throughput: 200 users * 7 RU/write = 1400 RU/s.
    - Your provisioned throughput is only 1000 RU/s. The first ~142 users (1000 / 7) succeed. The remaining ~58 users will get an **HTTP 429 error** and their client-side code will need to retry the operation a moment later. Because you chose Autoscale, Cosmos DB might instantly scale up your capacity to handle the load.