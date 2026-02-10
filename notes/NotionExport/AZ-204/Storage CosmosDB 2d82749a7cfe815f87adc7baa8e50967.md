# Storage CosmosDB

**Question X: Azure Storage Account**

- **1. What is it?**
    - An Azure Storage Account is a foundational, managed cloud storage service that provides a unique namespace in Azure to store and access your data objects. It acts as a container for a suite of highly scalable, durable, and secure data services, including Blobs (object), Files (file shares), Queues (messaging), and Tables (NoSQL). It is the cornerstone of modern data storage in Azure for unstructured and semi-structured data.
- **2. Why is it used?**
    - The core architectural purpose is to provide a **unified, massively scalable, and cost-effective platform for diverse data storage needs.**
        - **Scalability & Durability:** Designed to store exabytes of data with high durability through redundant copies, protecting against hardware failures or regional disasters.
        - **Cost-Effectiveness:** Offers tiered pricing (Hot, Cool, Archive for blobs) and a pay-for-what-you-use model, making it extremely cheap for storing large amounts of data.
        - **Flexibility:** A single account can serve a wide range of workloads, from hosting static website assets and storing big data for analytics (Blobs), to providing cloud file shares for legacy apps (Files), and enabling reliable messaging between application components (Queues).
        - **Unified Security & Management:** Provides a single control plane for managing access, security policies, and lifecycle rules across different data types.
- **3. How it works with Quick start details**
    - You create a storage account in a specific region, which then exposes REST API endpoints for each of its data services. You connect to it using a connection string or other authentication methods.
    - **Portal Steps:**
        1. In the Azure Portal, search for and select **Storage accounts**.
        2. Click **+ Create**.
        3. Select a subscription and resource group.
        4. Provide a **Storage account name**. This must be globally unique, 3-24 characters, and lowercase letters and numbers only.
        5. Choose a **Region**.
        6. Select a **Performance** tier: **Standard** (magnetic disks/HDD, general purpose) or **Premium** (solid-state drives/SSD, for low latency).
        7. Select a **Redundancy** option (e.g., **LRS** - Locally-redundant storage, for the cheapest option; **GZRS** - Geo-zone-redundant storage for the highest availability).
        8. Click **Review + create**, then **Create**.
    - **Azure CLI Example:**
        
        ```bash
        # Create a general-purpose v2 storage account with LRS redundancy
        az storage account create \\
          --name myuniquestorageaccountname \\
          --resource-group my-rg \\
          --location eastus \\
          --sku Standard_LRS \\
          --kind StorageV2
        
        ```
        
- **4. Developer Concepts (AZ-204 Focus)**
    - As a C# developer, you interact with the storage account primarily through the Azure SDKs.
        - **Connection String:** The easiest way to get started. You get this from the "Access keys" blade in the portal. It's stored in `appsettings.json` during development and in Azure App Service Configuration (or Key Vault) in production.
            
            ```json
            // appsettings.json
            "AzureStorage": {
              "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
            }
            
            ```
            
        - **C# SDK Interaction (Blob Example):**
            - You install the appropriate NuGet package (e.g., `Azure.Storage.Blobs`).
            
            ```csharp
            using Azure.Storage.Blobs;
            
            public class BlobService
            {
                private readonly BlobServiceClient _blobServiceClient;
            
                public BlobService(string connectionString)
                {
                    _blobServiceClient = new BlobServiceClient(connectionString);
                }
            
                public async Task UploadFileAsync(string containerName, string filePath)
                {
                    BlobContainerClient containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
                    await containerClient.CreateIfNotExistsAsync();
            
                    string fileName = Path.GetFileName(filePath);
                    BlobClient blobClient = containerClient.GetBlobClient(fileName);
            
                    await blobClient.UploadAsync(filePath, true);
                }
            }
            
            ```
            
        - **Authentication:** The three primary methods are:
            1. **Connection String (Account Key):** Full admin access. Simple but less secure.
            2. **Shared Access Signature (SAS) Token:** A delegated access token with granular permissions (e.g., read-only access to one blob for 1 hour).
            3. **Managed Identity (Azure AD):** The recommended best practice. Your App Service or Function authenticates using its managed identity, eliminating the need for any secrets in your configuration.
- **5. What are the Limitations and "Gotchas"?**
    - **Naming is Strict:** The globally unique, lowercase-only naming rule often trips up beginners.
    - **Performance Tier is Permanent:** You cannot change a storage account from Standard to Premium (or vice versa) after it has been created. You must create a new account and migrate the data.
    - **Redundancy Choice has Cost Implications:** GRS/GZRS are more expensive than LRS/ZRS. Choose the option that matches your application's availability requirements.
    - **Not a File System:** While Azure Files provides an SMB share, the underlying storage (especially Blob) is an object store. It doesn't have the same hierarchical directory performance as a true file system.
- **6. Practical Use Cases & Scenarios**
    - **Web Application:** Store user-uploaded images, videos, and static assets (CSS/JS) in **Blob Storage**.
    - **Decoupled Microservices:** One service writes a message to a **Queue Storage**, and another service reads from the queue to process the job asynchronously.
    - **Lift-and-Shift Legacy App:** An old on-premises application that writes to a network share can be moved to Azure by using **Azure Files** as its cloud-based SMB file share.
    - **Big Data & Analytics:** Store massive datasets from IoT devices or logs in **Azure Data Lake Storage Gen2** (which is built on top of Blob Storage) for analysis with services like Azure Synapse or Databricks.
- **7. Comparison with other similar services or features**
    - **Azure Storage Account vs. Azure SQL Database:**
        - Storage Account is for **unstructured/semi-structured** data (files, images, messages, NoSQL key-value). SQL is for **fully structured, relational** data with complex querying, transactions, and integrity constraints.
    - **Azure Storage Account vs. Cosmos DB:**
        - A Storage Account provides foundational, simple, and very cheap storage services. Its Table Storage is a basic NoSQL offering.
        - Cosmos DB is a premium, standalone, globally-distributed NoSQL database service with guaranteed low latency, multiple consistency models, and rich indexing. It is much more powerful and expensive than Table Storage.
- **8. Subtopics to master**
    - **Azure Blob Storage Tiers:** Understand Hot, Cool, and Archive tiers and how lifecycle management policies can automatically move data between them to save costs.
    - **Shared Access Signatures (SAS):** Master how to create and use SAS tokens for secure, delegated client access.
    - **Managed Identity for Storage:** Learn the best practice for authenticating from Azure services to storage without secrets.
    - **Storage Redundancy Options (LRS/ZRS/GRS/GZRS):** Understand the availability and durability guarantees of each.
    - **Network Security:** VNet Service Endpoints and Private Endpoints to lock down access to your storage account.
- **9. Pricing Tiers & Feature Availability**
    - The pricing model is based on usage, not on fixed tiers for the account itself. The main factors are:
        - **Performance (Standard vs. Premium):** Premium is significantly more expensive.
        - **Redundancy (LRS vs. GRS, etc.):** More redundancy costs more.
        - **Data Stored (per GB/month):** The cost varies dramatically by Blob access tier (Archive is extremely cheap to store, Hot is cheapest to access).
        - **Operations (per 10,000 transactions):** Every read, write, and list operation has a small cost.
        - **Data Egress (per GB):** Data transferred *out* of an Azure region incurs bandwidth costs.
- **10. Security Considerations**
    - **Authentication:** Always prefer **Managed Identity** over connection strings for services running in Azure. Use SAS tokens for client-side uploads.
    - **Network Isolation:** By default, a storage account is open to the internet. Use the **Storage Firewall** and **Private Endpoints** to restrict access to only your Virtual Network, locking it down completely.
    - **Encryption:** Data is **encrypted at rest by default** by Microsoft-managed keys. You can also use customer-managed keys (CMK) for more control.
    - **Principle of Least Privilege:** Use RBAC roles (like "Storage Blob Data Contributor") to give users and services only the permissions they need.

---

# **Question X: Table Storage vs Cosmos DB**

- **1. What is it?**
    - **Azure Table Storage:** A simple, schema-less NoSQL key-value/key-attribute store. It is one of the four data services offered within a standard Azure Storage Account, designed for storing massive amounts of semi-structured data at a very low cost.
    - **Azure Cosmos DB:** Azure's premier, globally-distributed, multi-model NoSQL database-as-a-service. It's a standalone, high-performance product engineered for mission-critical applications requiring guaranteed single-digit millisecond latency, tunable consistency, and seamless multi-region write capabilities.
- **2. Why is it used?**
    - **Table Storage:** Solves the problem of needing to store **huge volumes of simple data with simple query patterns as cheaply as possible**. Its primary design goal is massive scale at low cost, sacrificing advanced features like secondary indexes and complex queries.
    - **Cosmos DB:** Solves the problem of building **high-performance, globally-scaled applications**. Its "why" is to provide a turnkey database that delivers guaranteed low latency and high availability anywhere in the world, a feat that is extremely difficult to achieve with traditional databases.
- **3. How it works with Quick start details**
    - **Table Storage:** You interact with tables within an existing storage account. Data is organized by a **PartitionKey** and a **RowKey**, which together form the unique primary key. Queries on this key are extremely fast; all other queries are slow.
        - **Azure CLI:** `az storage table create --name mytable --account-name myaccount`
    - **Cosmos DB:** You create a dedicated Cosmos DB account and choose an API (e.g., Core (SQL), MongoDB, Cassandra, etc.). Data is stored in containers (like tables or collections) as JSON items. It automatically indexes every attribute of your JSON documents.
        - **Azure CLI:** `az cosmosdb create --name my-cosmos-db --resource-group my-rg`
        - Then you create a database and a container: `az cosmosdb sql database create ...`
- **4. Developer Concepts (AZ-204 Focus)**
    - **Table Storage (C#):** Uses the `Azure.Data.Tables` NuGet package. The entity must implement `ITableEntity`. Designing the PartitionKey and RowKey is the most important development task.
        
        ```csharp
        using Azure.Data.Tables;
        
        // Entity must define PartitionKey, RowKey, Timestamp, and ETag
        public class CustomerEntity : ITableEntity
        {
            public string PartitionKey { get; set; } // e.g., "USA"
            public string RowKey { get; set; }     // e.g., "CUSTOMER_1234"
            public DateTimeOffset? Timestamp { get; set; }
            public ETag ETag { get; set; }
            public string Email { get; set; }
        }
        
        // Client code
        var tableClient = new TableClient(connectionString, "customers");
        await tableClient.CreateIfNotExistsAsync();
        var customer = new CustomerEntity { PartitionKey = "USA", RowKey = "C123", Email = "..." };
        await tableClient.AddEntityAsync(customer);
        
        ```
        
    - **Cosmos DB (C# - Core SQL API):** Uses the `Microsoft.Azure.Cosmos` NuGet package. You interact with JSON documents, often represented by POCO classes.
        
        ```csharp
        using Microsoft.Azure.Cosmos;
        
        public class Customer
        {
            public string id { get; set; } // Becomes the unique key
            public string partitionKey { get; set; } // e.g., "USA"
            public string Email { get; set; }
            public Address[] Addresses { get; set; }
        }
        
        // Client code
        var cosmosClient = new CosmosClient(endpoint, key);
        var container = cosmosClient.GetContainer("MyDB", "customers");
        var customer = new Customer { id = "C123", partitionKey = "USA", Email = "..." };
        await container.CreateItemAsync(customer, new PartitionKey(customer.partitionKey));
        
        ```
        
- **5. What are the Limitations and "Gotchas"?**
    - **Table Storage:**
        - **No Secondary Indexes:** This is the biggest limitation. Queries that do not use the PartitionKey will result in a full table scan, which is incredibly slow and inefficient for large datasets.
        - **Limited Query API:** No server-side joins, aggregates, or complex filtering.
        - **Throughput is Capped:** Throughput is limited at the storage account level.
    - **Cosmos DB:**
        - **Cost:** It is significantly more expensive than Table Storage. Costs are based on provisioned throughput (**Request Units - RUs**) and storage. Mismanaging RUs can lead to high bills or throttled requests.
        - **Complexity:** Understanding and optimizing RUs, consistency levels, and partitioning strategies requires learning and effort.
- **6. Practical Use Cases & Scenarios**
    - **Choose Azure Table Storage When:**
        - You need to store terabytes of simple data (e.g., application logs, IoT telemetry, user settings).
        - Your primary query pattern is a simple key lookup (e.g., "get all logs for DeviceId=X").
        - Cost is your primary driver.
    - **Choose Azure Cosmos DB When:**
        - You need **guaranteed low-latency** reads/writes anywhere in the world (e.g., a shopping cart for a global e-commerce site).
        - You need **flexible queries** on any property of your data (e.g., "find all users in Seattle whose first name is John").
        - You need **multi-region write capabilities** for high availability.
        - Performance and availability are your primary drivers.
- **7. Comparison with other similar services or features**

| Feature | Azure Table Storage | Azure Cosmos DB (Core SQL API) |
| --- | --- | --- |
| **Data Model** | Key-Value / Key-Attribute | JSON Documents |
| **Performance** | Good (for key lookups) | **Excellent** (single-digit ms latency) |
| **Indexing** | Only on PartitionKey + RowKey | **Automatically indexes every property** |
| **Global Distribution** | Single-region writes | Turnkey **multi-region writes** |
| **Consistency** | Strong within a region | **5 tunable consistency levels** |
| **Query Language** | Basic OData filter syntax | **Rich SQL-like query language** |
| **Cost** | **Extremely Low** | High (based on RUs + storage) |
| **Best For** | Massive, simple datasets, cost-sensitive workloads. | Mission-critical, global, low-latency applications. |
- **8. Subtopics to master**
    - **Table Storage:** PartitionKey and RowKey design strategies (e.g., avoiding hot partitions). This is 90% of designing for Table Storage.
    - **Cosmos DB:** Request Units (RUs) and provisioning, partitioning strategies, consistency levels (Strong vs. Eventual vs. Session, etc.), the Change Feed feature.
- **9. Pricing Tiers & Feature Availability**
    - **Table Storage:** Part of the standard Azure Storage pricing model. You pay per GB of data stored and per 10,000 transactions. It's incredibly inexpensive.
    - **Cosmos DB:** Has two main pricing models:
        - **Provisioned Throughput:** You reserve a certain number of RUs/second. Best for predictable workloads.
        - **Serverless:** You pay per operation (per RU consumed). Best for spiky, unpredictable workloads.
        - Both models also charge for storage per GB.
- **10. Security Considerations**
    - **Table Storage:** Security is managed at the parent Storage Account level. This includes network security (VNet/Private Endpoints), identity (SAS tokens/Managed Identity), and encryption.
    - **Cosmos DB:** Has the same network security options. In addition, it has its own fine-grained, role-based access control (RBAC) for data plane operations (e.g., granting a user read-only access to a specific container) and supports resource tokens for giving temporary, granular access to end-user clients.

[**RUs, Throughput, and Horizontal
Partitioning**](Storage%20CosmosDB/RUs,%20Throughput,%20and%20Horizontal%20Partitioning%202d82749a7cfe819da59adfb1e50d1b8a.md)

[Throughput limit on Container vs Database level?](Storage%20CosmosDB/Throughput%20limit%20on%20Container%20vs%20Database%20level%202d82749a7cfe819ca043ec8ab42b5bbd.md)

[**Leases Container & CosmosDB Change Feed**](Storage%20CosmosDB/Leases%20Container%20&%20CosmosDB%20Change%20Feed%202d82749a7cfe8181a891c6114d000b2c.md)

[Consistency Levels](Storage%20CosmosDB/Consistency%20Levels%202e92749a7cfe80f3ad17e24e47226779.md)