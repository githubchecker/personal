# System-Design-Applied

# Applied System Design: The Comprehensive Decision Guide

This guide covers **every** concept in the System Design roadmap. It is structured to help you make decisions by providing a strict **“Choose this IF…”** framework for every option.

---

## 1. System Design Fundamentals

**Goal**: Understand the constraints before building.

### 1.1 Fundamentals & Estimation

- **Back-of-the-envelope Calculations**
    - **Choose this IF**: You need to prove your design is feasible *before* writing code.
    - **Action**: Memorize 2 ≈ 1*KB*, 2 ≈ 1*GB*. Latency: RAM=100ns, Disk=10ms.
        
        10
        
        30
        
- **Trade-offs (The Golden Rule)**
    - **Choose this IF**: You are making *any* architectural decision.
    - **Rule**: There is no “perfect” design. If you optimize for X, you likely hurt Y. (e.g., SQL = Good Consistency, Bad Write Scaling).

### 1.2 Performance vs Scalability

- **Performance (Speed)**
    - **Choose this IF**: Your single user experience is slow (e.g., page load takes 3s).
    - **Action**: Optimize code (*O*(*N*) → *O*(*N*)), add Caching (Redis), use faster hardware.
        
        2
        
    - **Micro-Decision: Amdahl’s Law**:
        - **Choose this IF**: You are optimizing a system with serial bottlenecks (locks).
        - **Rule**: Max speedup is limited by the serial part. If 10% is serial, max speedup is 10x, even with infinite CPUs.
- **Scalability (Volume)**
    - **Choose this IF**: Your site crashes when 10,000 users visit at once, even though it’s fast for 1 user.
    - **Action**: Add more servers (Horizontal Scaling), Shard the database.
    - **Micro-Decision: USL (Universal Scalability Law)**:
        - **Choose this IF**: You are adding servers but performance is *getting worse*.
        - **Reason**: Coherence penalty (nodes talking to each other) is outweighing the benefit of more hardware.

### 1.3 Latency vs Throughput

- **Latency (Time)**
    - **Choose this IF**: You are building Real-time Gaming, High-Frequency Trading, or Voice Chat.
    - **Action**: Use UDP, optimize network path, remove batching.
    - **Micro-Decision: Head-of-Line (HOL) Blocking**:
        - **Choose HTTP/2 or HTTP/3 IF**: One slow request is blocking all other requests on the same connection.
    - **Micro-Decision: Percentiles (p99)**:
        - **Choose this IF**: You want to optimize for the *worst* user experience, not the average. (p99 = 99% of requests are faster than X).
- **Throughput (Quantity)**
    - **Choose this IF**: You are building a File Uploader, Video Streaming, or Analytics Ingestion.
    - **Action**: Use **Batching** (group 100 writes into 1), use Parallelism (Kafka Partitions).
    - **Micro-Decision: Backpressure**:
        - **Choose this IF**: Consumers are slower than Producers. Tell producers to “Slow Down” to prevent OOM crashes.

### 1.3 CAP Theorem (Availability vs Consistency)

- **CP (Consistency + Partition Tolerance)**
    - **Choose this IF**: You are building a **Banking System**, Inventory Management, or Booking System.
    - **Why**: You cannot afford to show incorrect data (e.g., double spending). You accept that the system might return “Error” if the network is down.
- **AP (Availability + Partition Tolerance)**
    - **Choose this IF**: You are building **Social Media**, Comments, or Likes.
    - **Why**: It’s better to show a stale “Like count” than to show an error page. You accept **Eventual Consistency**.
    - **Micro-Decision: PACELC Theorem**:
        - **Choose Latency (L) IF**: The network is healthy (no partition) and you want speed.
        - **Choose Consistency (C) IF**: The network is healthy but you need perfect data sync.
    - **Micro-Decision: Split Brain**:
        - **Choose Quorums (>50% vote) IF**: You need to prevent two servers from both thinking they are the Master during a network cut.

---

## 2. Traffic Entry Layer

**Goal**: Route traffic efficiently and reliably.

### 2.1 DNS (Domain Name System)

- **A Record**
    - **Choose this IF**: You are mapping a name (`google.com`) to a static IPv4 address.
- **CNAME Record**
    - **Choose this IF**: You are mapping a name to another name (e.g., `blog.mysite.com` -> `mysite.github.io`).
- **TTL (Time To Live)**
    - **Choose High TTL (24h) IF**: Your infrastructure rarely changes. (Pros: Fast lookups).
    - **Choose Low TTL (60s) IF**: You are about to migrate servers. (Pros: Fast failover).
    - **Micro-Decision: Anycast Routing**:
        - **Choose this IF**: You need the absolute lowest latency globally. Users are routed to the *physically nearest* DNS server.

### 2.2 CDN (Content Delivery Network)

- **Pull CDN**
    - **Choose this IF**: You have a standard website. You want the CDN to automatically fetch content when a user asks for it.
- **Push CDN**
    - **Choose this IF**: You are distributing software patches or large files (10GB+). You want to upload them once and ensure they are available everywhere immediately.
    - **Micro-Decision: Cache Invalidation**:
        - **Choose Versioning (style.v2.css) IF**: You update a file. It forces the CDN to fetch the new one immediately (Free).
        - **Choose Purge IF**: You made a mistake (uploaded wrong image) and need to wipe it everywhere (Expensive/Slow).
    - **Micro-Decision: Edge Computing**:
        - **Choose this IF**: You want to run logic (A/B testing, Auth) at the CDN edge to reduce latency.

### 2.3 Load Balancers

- **L4 (Transport Layer)**
    - **Choose this IF**: You need extreme performance (millions of packets/sec) and don’t care about the content (e.g., TCP/UDP gaming traffic).
- **L7 (Application Layer)**
    - **Choose this IF**: You need **Smart Routing**. (e.g., Route `/api/video` to VideoService, `/api/chat` to ChatService).
- **Algorithms**:
    - **Round Robin**: **Choose this IF** all your requests are roughly the same size.
    - **Least Connections**: **Choose this IF** some requests take 10ms and others take 5 minutes (prevents overloading one server).
    - **Consistent Hashing**: **Choose this IF** you need “Sticky Sessions” (User A always goes to Server A).
    - **Micro-Decision: SSL Termination**:
        - **Choose this IF**: You want to save CPU on your application servers. The LB handles the heavy encryption/decryption work.

---

## 3. Availability Patterns

**Goal**: Keep the system alive when servers die.

### 3.1 Fail-over

- **Active-Passive**
    - **Choose this IF**: You want simplicity. One server handles traffic; the other sleeps until the first one dies.
- **Active-Active**
    - **Choose this IF**: You need scale. Both servers handle traffic. (Requires complex bi-directional replication).
    - **Micro-Decision: Fencing (STONITH)**:
        - **Choose this IF**: You are using Active-Passive. If the “Dead” Master wakes up, you must kill it (cut power) to prevent it from corrupting data.
    - **Micro-Decision: VIP (Virtual IP)**:
        - **Choose this IF**: You want fast failover. The IP address “floats” to the active server, so clients don’t need to update their config.

### 3.2 Replication

- **Master-Slave**
    - **Choose this IF**: Your application is **Read-Heavy** (80% reads). All writes go to Master; all reads go to Slaves.
- **Master-Master**
    - **Choose this IF**: You need high write availability across regions (e.g., User writes to US-East and EU-West simultaneously). *Warning: Conflict resolution is hard.*
    - **Micro-Decision: Quorums (R + W > N)**:
        - **Choose this IF**: You need Strong Consistency in a distributed cluster.
        - **Formula**: If you have 3 replicas, Write to 2, Read from 2. You are guaranteed to see the latest data.
    - **Micro-Decision: Replication Lag**:
        - **Choose Sticky Sessions IF**: Users complain about “Read Your Own Write” issues (posting a comment and not seeing it).

---

## 4. Application Layer

**Goal**: Structure your code and communication.

### 4.1 Communication Protocols

- **REST (HTTP/JSON)**
    - **Choose this IF**: You are building a **Public API** for 3rd party developers or Mobile Apps. It’s universal and easy to debug.
    - **Micro-Decision: HATEOAS**:
        - **Choose this IF**: You want the API to be self-discoverable (links to next actions).
- **gRPC (Protobuf)**
    - **Choose this IF**: You are building **Internal Microservices**. You need low latency and strict type safety.
    - **Micro-Decision: Schema Evolution**:
        - **Choose this IF**: You need to add fields without breaking old clients. Protobuf handles this natively (ignore unknown fields).
- **GraphQL**
    - **Choose this IF**: You have a complex Frontend (e.g., Facebook) that needs to fetch nested data (User -> Friends -> Photos) in a single request to save bandwidth.

### 4.2 Asynchronism (Queues)

- **Message Queues (RabbitMQ/Kafka)**
    - **Choose this IF**: You need to decouple services. (e.g., “Order Service” sends a message; “Email Service” picks it up later).
    - **Micro-Decision: Dead Letter Queue (DLQ)**:
        - **Choose this IF**: A “Poison Pill” message is crashing your worker. Move it to a DLQ after 3 retries so you can inspect it later.
    - **Micro-Decision: Consumer Groups**:
        - **Choose this IF**: You need to parallelize processing. Group members share the load (each reads 1 partition).
- **Task Queues (Celery/BullMQ)**
    - **Choose this IF**: You need to run background jobs (e.g., Resize Image, Generate PDF) without blocking the user’s HTTP request.
    - **Micro-Decision: Idempotency**:
        - **Choose this IF**: You want to prevent double-charging a user. Ensure `ChargeCard()` can be called 10 times safely.
- **Back Pressure**
    - **Choose this IF**: Your consumers are slower than your producers. You need to tell the producer to “Slow Down” or drop messages to prevent a crash.
    - **Micro-Decision: Load Shedding**:
        - **Choose this IF**: Your CPU is >90%. Immediately return HTTP 503 to new users to save the system.

---

## 5. Data Layer

**Goal**: Store data correctly based on access patterns.

### 5.1 Consistency Patterns

- **Strong Consistency**
    - **Choose this IF**: Financial Transactions. (Use 2PC or Consensus Algorithms like Raft).
    - **Micro-Decision: 2PC (Two-Phase Commit)**:
        - **Choose this IF**: You need atomic transactions across two different databases. *Warning: It blocks if the coordinator dies.*
    - **Micro-Decision: Linearizability vs Serializability**:
        - **Choose Linearizability IF**: You need “Real-time” guarantees (single object).
        - **Choose Serializability IF**: You need “Transaction” guarantees (multiple objects).
- **Eventual Consistency**
    - **Choose this IF**: Social Feeds, Analytics. (Use Gossip Protocols).
    - **Micro-Decision: BASE Model**:
        - **Choose this IF**: You value Availability over Consistency (Soft State).
    - **Micro-Decision: Conflict Resolution**:
        - **Choose LWW (Last Write Wins) IF**: You want simplicity and can tolerate some data loss.
        - **Choose Vector Clocks IF**: You need to detect *causality* (A happened before B) and merge data intelligently.
- **Weak Consistency**
    - **Choose this IF**: VoIP, Video Chat, Real-time Multiplayer positions. (Dropping a packet is better than waiting for it).
    - **Micro-Decision: Monotonic Reads**:
        - **Choose this IF**: You want to prevent “Time Travel” (User sees a comment, refreshes, and it disappears). Ensure user always reads from the same replica.

### 5.2 Database Selection

- **Relational (SQL)**
    - **Choose this IF**: You have structured data with relationships (Users, Orders, Products). You need ACID compliance.
- **NoSQL: Key-Value (Redis)**
    - **Choose this IF**: You need ultra-fast lookup (*O*(1)) for simple data (Caching, Sessions, Leaderboards).
    - **Micro-Decision: Persistence (RDB vs AOF)**:
        - **Choose RDB (Snapshot) IF**: You want fast backups and can tolerate 5 mins of data loss.
        - **Choose AOF (Log) IF**: You need zero data loss (slower recovery).
- **NoSQL: Document (MongoDB)**
    - **Choose this IF**: Your data schema changes frequently (Product Catalogs) or you want to store complex objects (JSON) without joining tables.
- **NoSQL: Wide Column (Cassandra)**
    - **Choose this IF**: You have massive **Write Volume** (IoT Sensors, Logs) and need linear scalability.
    - **Micro-Decision: Tunable Consistency**:
        - **Choose ONE IF**: You want max speed (write to 1 node).
        - **Choose QUORUM IF**: You want balance (write to majority).
- **NoSQL: Graph (Neo4j)**
    - **Choose this IF**: Your data is all about relationships (Social Networks, Recommendation Engines).
    - **Micro-Decision: Cypher/Gremlin**:
        - **Choose this IF**: You need to traverse complex relationships (`User -> Friend -> Friend`).
    - **Micro-Decision: Sharding Difficulty**:
        - **Avoid Sharding IF**: You are using Graph DBs. They don’t shard well (cutting edges is expensive). Scale Vertically instead.
    - **Micro-Decision: Bloom Filters (Wide Column)**:
        - **Choose this IF**: You want to avoid reading from disk for data that doesn’t exist. (Fast “No” check).
    - **Micro-Decision: Denormalization (Document)**:
        - **Choose this IF**: You want to avoid Joins. You duplicate `UserAvatar` inside `Comment` to read it in one go.

### 5.3 Caching Strategies

- **Cache-Aside (Lazy)**
    - **Choose this IF**: You want a general-purpose cache. Only requested data is cached.
- **Write-Through**
    - **Choose this IF**: You need strict data consistency. Data is written to Cache and DB simultaneously. (Slower writes).
- **Write-Behind**
    - **Choose this IF**: You need extreme write speed. Data is written to Cache first, then async to DB. (Risk of data loss).
    - **Micro-Decision: Thundering Herd**:
        - **Choose Request Coalescing IF**: 10,000 users ask for the same key at once. Only allow 1 request to hit the DB.

### 5.4 Eviction Policies

- **LRU (Least Recently Used)**
    - **Choose this IF**: Recent data is most likely to be accessed again (e.g., News, Social Feeds).
- **LFU (Least Frequently Used)**
    - **Choose this IF**: Historical popularity matters (e.g., “Most popular songs of all time”).
    - **Micro-Decision: TTL Jitter**:
        - **Choose this IF**: You have many keys expiring at the same time. Add random seconds (±5s) to prevent a spike in DB load.
    - **Micro-Decision: Random Replacement**:
        - **Choose this IF**: You are memory constrained (CPU cache). It’s fast and requires no metadata.

---

## 6. Advanced Patterns & Resiliency

**Goal**: Handle scale and failure.

### 6.1 Cloud Design Patterns

- **Circuit Breaker**
    - **Choose this IF**: You call an unreliable external service. If it fails often, stop calling it to prevent your own system from hanging.
    - **Micro-Decision: Cascading Failure**:
        - **Choose Circuit Breakers IF**: One failing service is taking down your entire system.
    - **Micro-Decision: Bulkhead Pattern**:
        - **Choose this IF**: You want to isolate resources. If “Image Service” threads are full, “User Service” should still work.
- **CQRS (Command Query Responsibility Segregation)**
    - **Choose this IF**: Your Read patterns are very different from your Write patterns. (e.g., Write complex normalized data; Read simple denormalized views).
    - **Micro-Decision: Materialized Views**:
        - **Choose this IF**: Complex JOINs are too slow. Pre-calculate the result into a single table for fast reads.
- **Event Sourcing**
    - **Choose this IF**: You need a perfect audit trail (e.g., Accounting). You store “Events” (Deposit, Withdraw) instead of “State” (Balance).
- **Strangler Fig**
    - **Choose this IF**: You are migrating a Monolith to Microservices. You slowly replace routes one by one.
- **Sharding**
    - **Choose this IF**: Your DB is too big for one server. You split data by a key (e.g., UserID).
- **Pub/Sub**
    - **Choose this IF**: You need one event to trigger multiple independent actions (e.g., “User Signup” -> Email + Analytics + Welcome Notification).
    - **Micro-Decision: Anti-Corruption Layer (ACL)**:
        - **Choose this IF**: You are migrating a Legacy Monolith. Translate “messy” legacy data into “clean” new data before it enters your system.
    - **Micro-Decision: Saga Pattern**:
        - **Choose this IF**: You need a transaction across multiple Microservices. (Service A succeeds -> Trigger Service B. If B fails -> Trigger Undo A).

### 6.2 Performance Antipatterns

- **Synchronous I/O**
    - **Avoid this IF**: You want high concurrency. Blocking a thread for a DB call kills performance. Use **Async I/O**.
- **N+1 Problem**
    - **Avoid this IF**: You are fetching a list of items. Don’t run 1 query for the list + N queries for the details. Use **Batching** or **JOINs**.
    - **Micro-Decision: JOINs vs Subqueries**:
        - **Choose JOINs IF**: You want to avoid network round-trips.
- **Thread Starvation**
    - **Avoid this IF**: You are blocking threads on I/O. Use **Non-Blocking I/O** (Async) to handle thousands of concurrent requests.