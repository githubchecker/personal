# Throughput limit on Container vs Database level?

Excellent question. This is one of the most fundamental and financially significant decisions you will make when designing an application with Azure Cosmos DB. Choosing the wrong model can lead to either performance throttling or wasted money.

Let's break down the two throughput provisioning models.

---

# **The Analogy: Office Building Internet**

- Imagine you are the landlord of a new office building (your **Cosmos DB Database**). You need to provide internet for all the companies (your **Containers**) that will rent space. You have two options:
    1. **Database Level (Shared Throughput):** You buy one massive, high-speed internet connection for the whole building (e.g., a 1000 Mbps fiber line). All tenants share this connection. This is your **shared throughput model**.
    2. **Container Level (Dedicated Throughput):** You don't provide a central connection. Instead, each company must order its own dedicated internet line (e.g., Tenant A gets a 100 Mbps line, Tenant B gets a 500 Mbps line). This is your **dedicated throughput model**.
- Now let's apply this to Cosmos DB.

---

# **1. Database Level Throughput (Shared)**

- **What is it?**
    - You provision throughput (RUs) on the database itself. All containers created *within that database* share this single pool of RUs. You pay a single monthly price for the database's throughput, regardless of how many containers are inside it.
- **How it Works**
    - When a request comes in for a container, it "borrows" RUs from the shared database pool to process the request. If multiple containers are busy at the same time, they all compete for RUs from the same pool. Cosmos DB tries to be fair, but if one container is extremely busy, it can consume a disproportionate amount of the shared RUs, starving the others.
- **The "Noisy Neighbor" Problem**
    - This is the single most important concept for shared throughput. If Tenant A (e.g., your Logging container) suddenly starts a massive data import, they might use up 950 of the 1000 Mbps shared internet. When Tenant B (your critical ShoppingCart container) tries to process an order, their connection will be extremely slow or might fail entirely.
    - The Logging container is the **"noisy neighbor,"** negatively impacting the performance of the ShoppingCart container.
- **Pros & Cons**
    - **Pros:**
        - **Cost-Effective for Many Containers:** This is the biggest advantage. If you have many small containers, especially with spiky or infrequent traffic, this model is much cheaper than giving each one its own dedicated (and mostly idle) throughput.
        - **Simplified Management:** You manage one throughput setting for the whole group.
    - **Cons:**
        - **Noisy Neighbor Problem:** Performance is not guaranteed. A busy container can impact a critical one.
        - **No Granular Control:** You cannot give more RUs to one container and less to another. They all share the same pool.
        - **Higher Minimum:** You must provision a minimum of 1000 RU/s (for Autoscale) to use the shared model.
- **Best For:**
    - **Dev/Test Environments.**
    - **Multi-tenant applications** where each tenant gets their own container, and you want to amortize the cost across all tenants.
    - Applications with a large number of small, infrequently used collections.

---

# **2. Container Level Throughput (Dedicated)**

- **What is it?**
    - You provision a specific amount of throughput (RUs) directly on each individual container. This throughput is reserved exclusively for that container and is not shared with any others.
- **How it Works**
    - The ShoppingCart container has its own dedicated 500 RU/s, and the Logging container has its own 200 RU/s. No matter how busy the Logging container gets, it can never affect the performance of the ShoppingCart container. Each container has its own private, guaranteed internet line.
- **Pros & Cons**
    - **Pros:**
        - **Guaranteed, Predictable Performance:** This is the key benefit. You get a strict performance SLA for your critical container.
        - **No Noisy Neighbor Problem:** Complete isolation between container workloads.
        - **Granular Control:** You can precisely allocate RUs based on the needs of each container. You can scale your high-traffic container up without affecting the others.
    - **Cons:**
        - **Potentially Higher Cost:** If you have 20 containers and give each one the minimum dedicated throughput (400 RU/s), you are paying for 20 * 400 = 8000 RU/s in total, which can be much more expensive than a single shared pool of 1000 RU/s. You pay for the provisioned capacity whether you use it or not.
- **Best For:**
    - **Mission-critical, production workloads** that require a predictable performance SLA.
    - Any container with high, sustained traffic.
    - Separating write-heavy workloads from read-heavy workloads to prevent them from interfering with each other.

---

# **The Hybrid Model & The Final Recommendation**

- You are not forced to choose one model for your entire application. **Within a single Cosmos DB account, you can have multiple databases, and you can mix and match provisioning strategies.**
    - You could have a SharedDb with database-level throughput for your low-traffic and dev/test containers.
    - You could have a separate ProductionDb where your most important containers (Users, Orders) each have their own dedicated throughput.
- **Decision Guide - How to Choose:**
    1. **Start with Shared (Database Level):** For a new application with many collections and uncertain traffic patterns, start with database-level throughput. It's more cost-effective and simpler to manage initially.
    2. **Monitor for Noisy Neighbors:** Closely monitor your RU consumption. Use Azure Monitor to see if any single container is consistently consuming a large percentage of the shared RUs.
    3. **"Graduate" to Dedicated (Container Level):** When you identify a container that meets any of these criteria, it's time to move it to its own dedicated throughput:
        - It needs a **strict performance guarantee (SLA)**.
        - It is becoming a **"noisy neighbor"** and negatively impacting other containers in the shared pool.
        - It has a **high, predictable traffic pattern** that justifies paying for reserved capacity.
- By following this "start shared, graduate to dedicated" approach, you can achieve the optimal balance between cost-efficiency and performance.