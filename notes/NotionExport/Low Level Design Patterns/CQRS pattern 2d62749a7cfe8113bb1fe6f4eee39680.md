# CQRS pattern

[CQRS Pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)

Command Query Responsibility Segregation (CQRS) is a design pattern that segregates read and write operations for a data store into separate data models. This approach allows each model to be optimized independently and can improve the performance, scalability, and security of an application.

**Context and problem**

In a traditional architecture, a single data model is often used for both read and write operations. This approach is straightforward and is suited for basic create, read, update, and delete (CRUD) operations.

![Diagram that shows a traditional CRUD architecture.](https://learn.microsoft.com/en-us/azure/architecture/patterns/_images/command-and-query-responsibility-segregation-cqrs-tradition-crud.png)

As applications grow, it can become increasingly difficult to optimize read and write operations on a single data model. Read and write operations often have different performance and scaling requirements. A traditional CRUD architecture doesn't take this asymmetry into account, which can result in the following challenges:

- **Data mismatch:** The read and write representations of data often differ. Some fields that are required during updates might be unnecessary during read operations.
- **Lock contention:** Parallel operations on the same data set can cause lock contention.
- **Performance problems:** The traditional approach can have a negative effect on performance because of load on the data store and data access layer, and the complexity of queries required to retrieve information.
- **Security challenges:** It can be difficult to manage security when entities are subject to read and write operations. This overlap can expose data in unintended contexts.

Combining these responsibilities can result in an overly complicated model.

**Solution**

Use the CQRS pattern to separate write operations, or *commands*, from read operations, or *queries*. Commands update data. Queries retrieve data. The CQRS pattern is useful in scenarios that require a clear separation between commands and reads.

- **Understand commands.** Commands should represent specific business tasks instead of low-level data updates. For example, in a hotel-booking app, use the command "Book hotel room" instead of "Set ReservationStatus to Reserved." This approach better captures the intent of the user and aligns commands with business processes. To help ensure that commands are successful, you might need to refine the user interaction flow and server-side logic and consider asynchronous processing.
    
    
    | Area of refinement | Recommendation |
    | --- | --- |
    | Client-side validation | Validate specific conditions before you send the command to prevent obvious failures. For example, if no rooms are available, disable the "Book" button and provide a clear, user-friendly message in the UI that explains why booking isn’t possible. This setup reduces unnecessary server requests and provides immediate feedback to users, which enhances their experience. |
    | Server-side logic | Enhance the business logic to handle edge cases and failures gracefully. For example, to address race conditions such as multiple users attempting to book the last available room, consider adding users to a waiting list or suggesting alternatives. |
    | Asynchronous processing | [Process commands asynchronously](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/asynchronous-message-based-communication) by placing them in a queue, instead of handling them synchronously. |
- **Understand queries.** Queries never alter data. Instead, they return data transfer objects (DTOs) that present the required data in a convenient format, without any domain logic. This distinct separation of responsibilities simplifies the design and implementation of the system.

**Separate read models and write models**

Separating the read model from the write model simplifies system design and implementation by addressing specific concerns for data writes and data reads. This separation improves clarity, scalability, and performance but introduces trade-offs. For example, scaffolding tools like object-relational mapping (O/RM) frameworks can't automatically generate CQRS code from a database schema, so you need custom logic to bridge the gap.

The following sections describe two primary approaches to implement read model and write model separation in CQRS. Each approach has unique benefits and challenges, such as synchronization and consistency management.

**Separate models in a single data store**

This approach represents the foundational level of CQRS, where both the read and write models share a single underlying database but maintain distinct logic for their operations. A basic CQRS architecture allows you to delineate the write model from the read model while relying on a shared data store.

![Diagram that shows a basic CQRS architecture.](https://learn.microsoft.com/en-us/azure/architecture/patterns/_images/command-and-query-responsibility-segregation-cqrs-basic.png)

This approach improves clarity, performance, and scalability by defining distinct models for handling read and write concerns.

- **A write model** is designed to handle commands that update or persist data. It includes validation and domain logic, and helps ensure data consistency by optimizing for transactional integrity and business processes.
- **A read model** is designed to serve queries for retrieving data. It focuses on generating DTOs or projections that are optimized for the presentation layer. It enhances query performance and responsiveness by avoiding domain logic.

**Separate models in different data stores**

A more advanced CQRS implementation uses distinct data stores for the read and write models. Separation of the read and write data stores allows you to scale each model to match the load. It also enables you to use a different storage technology for each data store. You can use a document database for the read data store and a relational database for the write data store.

![Diagram that shows a CQRS architecture with separate read data stores and write data stores.](https://learn.microsoft.com/en-us/azure/architecture/patterns/_images/command-and-query-responsibility-segregation-cqrs-separate-stores.png)

When you use separate data stores, you must ensure that both remain synchronized. A common pattern is to have the write model publish events when it updates the database, which the read model uses to refresh its data. For more information about how to use events, see [Event-driven architecture style](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven). Because you usually can't enlist message brokers and databases into a single distributed transaction, challenges in consistency can occur when you update the database and publishing events. For more information, see [Idempotent message processing](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-mission-critical/mission-critical-data-platform#idempotent-message-processing).

The read data store can use its own data schema that's optimized for queries. For example, it can store a [materialized view](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view) of the data to avoid complex joins or O/RM mappings. The read data store can be a read-only replica of the write store or have a different structure. Deploying multiple read-only replicas can improve performance by reducing latency and increasing availability, especially in distributed scenarios.

**Problems and considerations**

Consider the following points as you decide how to implement this pattern:

- **Increased complexity.** The core concept of CQRS is straightforward, but it can introduce significant complexity into the application design, specifically when combined with the [Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing).
- **Messaging challenges.** Messaging isn't a requirement for CQRS, but you often use it to process commands and publish update events. When messaging is included, the system must account for potential problems such as message failures, duplicates, and retries. For more information about strategies to handle commands that have varying priorities, see [Priority queues](https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue).
- **Eventual consistency.** When the read databases and write databases are separated, the read data might not show the most recent changes immediately. This delay results in stale data. Ensuring that the read model store stays up-to-date with changes in the write model store can be challenging. Also, detecting and handling scenarios where a user acts on stale data requires careful consideration.

**When to use this pattern**

### **1. "You work in collaborative environments." (Reducing Merge Conflicts)**

**The Problem without CQRS:**
You use a standard CRUD (Create, Read, Update, Delete) model.

- Alice loads a "Task" entity. The title is "Initial Task Title."
- Bob loads the *same* Task entity. He also sees "Initial Task Title."
- Alice changes the title to "New Title from Alice" and saves.
- Bob changes the *description* to "New description from Bob" and saves. He sends the entire `Task` object to the API.

What happens? When Bob saves, his `Task` object still has the old title ("Initial Task Title"). If the update logic is a simple "overwrite," **Bob's save will erase Alice's title change.** This is a classic "lost update" problem or merge conflict.

**The Solution with CQRS (Commands with Intent):**
Instead of sending a whole `Task` object, the UI sends specific **Commands** that describe the user's *intent*.

- Alice's UI sends: `new ChangeTaskTitleCommand { TaskId = 123, NewTitle = "New Title from Alice" }`
- Bob's UI sends: `new ChangeTaskDescriptionCommand { TaskId = 123, NewDescription = "New description from Bob" }`

**The Technical Implementation (The "Write Model"):**
The command handlers are now separate and only touch the specific fields they are responsible for.

```csharp
// Alice's command handler
public class ChangeTaskTitleHandler
{
    public async Task Handle(ChangeTaskTitleCommand command)
    {
        var task = await _db.Tasks.FindAsync(command.TaskId);
        task.Title = command.NewTitle; // Only touches the title
        await _db.SaveChangesAsync();
    }
}

// Bob's command handler
public class ChangeTaskDescriptionHandler
{
    public async Task Handle(ChangeTaskDescriptionCommand command)
    {
        var task = await _db.Tasks.FindAsync(command.TaskId);
        task.Description = command.NewDescription; // Only touches the description
        await _db.SaveChangesAsync();
    }
}

```

**Result:** Both commands can be processed in any order. They do not interfere with each other. The system correctly updates both the title and the description. The merge conflict is prevented by design.

---

### **2. "You have task-based user interfaces." (Complex Domain Models)**

### **The Core Problem with a Multi-Step Wizard**

The fundamental question is: **"What is the *source of truth* for the incomplete data between steps?"**

**The "Bad" Way (Standard CRUD thinking):**
In a traditional model, you might be tempted to do one of these things, all of which have problems:

1. **Save an Invalid `Project` to the Main DB:**
    - **Action:** After Step 1 ("Enter Name"), you save a `Project` entity to your main `Projects` table. This `Project` has no members and no budget, so it violates your business rules.
    - **Problem:** Your database is now full of invalid, "draft" data. You need to add a `Status` column (e.g., `Draft`, `Complete`) and write complex logic to clean up abandoned drafts. Your queries (`SELECT * FROM Projects`) now have to include `WHERE Status = 'Complete'`, polluting all your read logic.
2. **Store the Incomplete Data on the Client (Frontend):**
    - **Action:** The React/Angular app holds the `projectName` in its state. When the user moves to Step 2, it keeps that state. It only sends the complete `Project` object to the server at the very end.
    - **Problem:** If the user closes their browser tab at Step 2 and comes back tomorrow, **their work is gone.** The state was ephemeral. This is a terrible user experience for complex wizards.

### **How CQRS Solves This Elegantly**

CQRS provides a clear separation that allows us to treat the "in-progress wizard" as its own distinct model, completely separate from the final, valid `Project` model.

**The Solution:** The incomplete data is stored on the **Write side**, but not as a "Project." It is stored as a **"Wizard Session"** or a **"Draft Project"**—a model designed specifically for this temporary state.

Here is the step-by-step technical workflow:

### **Step 1: The First Command (`StartProjectCreationCommand`)**

- When the user finishes Step 1, the UI sends a command with clear intent.
- **UI sends:** `new StartProjectCreationCommand { ProjectName = "Project Phoenix", UserId = "user-123" }`

### **Step 2: The Command Handler and the "Draft" Model**

- The command handler does **NOT** create a `Project` entity. It creates a `ProjectCreationDraft` entity and saves it to a separate, temporary storage. This could be a different table in your SQL database (`ProjectDrafts`) or even a document in Redis.
- **The Handler:**
    
    ```csharp
    public class StartProjectCreationHandler
    {
        public async Task<Guid> Handle(StartProjectCreationCommand command)
        {
            // This is a simple DTO/Entity for storing the temporary state.
            var draft = new ProjectCreationDraft
            {
                DraftId = Guid.NewGuid(),
                ProjectName = command.ProjectName,
                CreatedByUserId = command.UserId,
                CurrentStep = "InviteMembers"
            };
    
            // Save it to a temporary store (e.g., a 'Drafts' table or Redis)
            await _draftRepository.SaveAsync(draft);
    
            // Return the ID of the DRAFT, not the final project.
            return draft.DraftId;
        }
    }
    
    ```
    
- **Result:** The UI receives a `draftId`. The main `Projects` table is completely untouched and remains clean.

### **Step 3: Subsequent Steps (`AddMembersToDraftCommand`)**

- For the next steps, the UI holds onto the `draftId`. When the user adds members in Step 2, the UI sends a command that references this draft.
- **UI sends:** `new AddMembersToDraftCommand { DraftId = "guid-from-step-2", Members = [...] }`
- **The Handler:**
    
    ```csharp
    public class AddMembersToDraftHandler
    {
        public async Task Handle(AddMembersToDraftCommand command)
        {
            // 1. Load the existing DRAFT from the temporary store.
            var draft = await _draftRepository.GetByIdAsync(command.DraftId);
    
            // 2. Update the DRAFT with the new information.
            draft.InvitedMembers = command.Members;
            draft.CurrentStep = "SetBudget";
    
            // 3. Save the updated DRAFT.
            await _draftRepository.SaveAsync(draft);
        }
    }
    
    ```
    

### **Step 4: The Final Command (`FinalizeProjectCreationCommand`)**

- When the user clicks "Finish" on the last step, the UI sends the final command.
- **UI sends:** `new FinalizeProjectCreationCommand { DraftId = "guid-from-step-2" }`
- **The Handler (The Grand Finale):**
This handler does three critical things:
    1. Loads the complete `ProjectCreationDraft`.
    2. Uses the draft data to create the **real, valid `Project` aggregate**.
    3. Deletes the draft.
    
    ```csharp
    public class FinalizeProjectCreationHandler
    {
        public async Task<Guid> Handle(FinalizeProjectCreationCommand command)
        {
            // 1. Load the completed draft.
            var draft = await _draftRepository.GetByIdAsync(command.DraftId);
    
            // 2. Use the Domain-Driven Design aggregate to create the REAL project.
            // This enforces all business rules (e.g., must have members).
            var project = Project.Create(draft.ProjectName);
            foreach (var member in draft.InvitedMembers)
            {
                project.AddMember(member);
            }
            project.SetBudget(draft.Budget);
            project.FinalizeProject(); // This might change its status to "Active"
    
            // 3. Save the REAL project to the permanent 'Projects' table.
            await _projectRepository.SaveAsync(project);
    
            // 4. (Crucial) Delete the temporary draft.
            await _draftRepository.DeleteAsync(draft.DraftId);
    
            // Return the ID of the newly created, valid project.
            return project.Id;
        }
    }
    
    ```
    

### **Summary: How CQRS Helps**

1. **Separation of Models:** CQRS encourages you to think about different models for different tasks. You have a `ProjectCreationDraft` (Write side, temporary) and a `Project` (Write side, permanent). They are not the same thing.
2. **Keeps the Core Clean:** Your main `Projects` table, which is likely used for many important queries, is never polluted with incomplete, invalid data.
3. **State Persistence:** The user's progress is saved on the server in a durable store. They can close their browser and resume the wizard later by using the `draftId`.
4. **Intentful Commands:** The commands (`Start...`, `AddMembers...`, `Finalize...`) clearly document the user's journey through the wizard, making the business logic easy to understand and follow.

The data for the incomplete wizard is stored **on the server's write side**, but as a **separate, temporary model** designed specifically for that "task-based UI," not as an invalid version of your core domain model.

---

### **3. "You need performance tuning." (Separate Read/Write Scaling)**

**The Problem without CQRS:**
Your application gets featured on a major blog. You now have 1 million users reading product pages, but only 100 users are actually buying products.

- **The Problem:** Your single database and single API are being hammered by read requests. To scale up, you have to add more powerful database replicas and more API servers, which is expensive. The "write" path is also slowed down by all the "read" traffic.

**The Solution with CQRS:**
You can physically separate the read and write databases.

**The Technical Implementation:**

- **Write Model:**
    - Still uses your main transactional SQL Server database.
    - It might only need to run on **1-2 API instances** to handle the low volume of writes.
- **Read Model:**
    - After the Write model saves to SQL, it publishes an event ("ProductUpdated").
    - A background worker listens to this event and updates a separate, highly optimized **Read Database** (like Redis, Elasticsearch, or a denormalized Azure Cosmos DB).
    - The `GetProductDetails` query now reads from this super-fast, read-optimized database.
    - You can scale the "Read API" to **50 instances** to handle the massive read traffic, and it won't affect the write database at all.

**Result:** You get massive, cost-effective scalability. You use the right tool for the right job: a transactional database for writing and a read-optimized database for querying.

---

### **4. "You have separation of development concerns." (Team Autonomy)**

**The Problem without CQRS:**
In a large, monolithic API, every time the "User Profile" team wants to add a field to their database entity, it might break the "Reporting" team's queries. Both teams are working in the same codebase, on the same models, creating friction and merge conflicts.

**The Solution with CQRS:**
The teams work on separate models.

**The Technical Implementation:**

- **Team A (The "Write" Team):**
    - They work on the complex `User` aggregate and the command handlers (`UpdateUserAddressCommand`, etc.).
    - Their "source of truth" is the transactional database.
    - They can refactor their internal models as much as they want.
- **Team B (The "Read" Team):**
    - They work on the `UserProfileViewModel` and the query handlers.
    - They listen for events published by Team A (e.g., `UserAddressUpdated`).
    - They build and manage their own read-optimized database tailored specifically for their UI needs.

**Result:** Team B doesn't care *how* Team A stores the address. They just care that they receive an event when it changes. The teams can deploy their services independently.

---

### **5. "You have evolving systems." (Flexibility)**

**The Problem without CQRS:**
You have a single `Order` model. The Sales team views it one way, the Warehouse team views it another way, and the Finance team views it a third way. If you try to create one giant `Order` entity to satisfy everyone, it becomes a 100-property monster that is impossible to change.

**The Solution with CQRS:**
You have one **Write Model** (`Order` aggregate) but **multiple Read Models**.

**The Technical Implementation:**

- When a `OrderPlaced` event is published by the Write Model, **three different background workers** listen to it.
    1. **Sales Worker:** Updates the `SalesDashboardView` with the customer name and total price.
    2. **Warehouse Worker:** Updates the `ShippingManifestView` with the product SKUs and shipping address.
    3. **Finance Worker:** Updates the `LedgerView` with the tax information and transaction ID.

**Result:** When the Finance team needs a new field, you only have to update their specific worker and their read model. The Sales and Warehouse teams are completely unaffected. You can add new "views" of the data without ever touching the core write logic.

---

### **6. "You need system integration." (Resilience)**

**The Problem without CQRS:**
Your `CreateUserCommand` needs to do three things:

1. Save the user to your local DB.
2. Call a remote "Mailing List API."
3. Call a remote "Analytics API."

What if the Mailing List API is down? In a synchronous system, the entire "Create User" operation fails. The user sees an error, and your local DB might have to roll back the user creation.

**The Solution with CQRS + Event Sourcing:**
CQRS is a natural fit for **Event-Driven Architectures**.

**The Technical Implementation:**

1. The `CreateUserCommand` handler does only **one thing:** validates the command and writes an **event** to a log: `UserCreated { UserId = 123, Email = "..." }`. This is atomic and very fast. It then immediately returns "Success" to the user.
2. Three separate, independent **background workers** (event listeners) subscribe to this event.
    - **Worker 1 (Local DB):** Sees `UserCreated`, saves the user to your local read model database.
    - **Worker 2 (Mailing List):** Sees `UserCreated`, tries to call the Mailing List API. If it's down, it can use a **Retry Policy** and try again in 5 minutes.
    - **Worker 3 (Analytics):** Sees `UserCreated`, calls the Analytics API.

**Result:** The system is **resilient**. The user registration succeeds instantly. If the Mailing List API is down for an hour, it doesn't matter. Worker 2 will just keep retrying. The failure of one subsystem is completely isolated and does not affect the core functionality of your application.

---

### **7. "You need granular security control." (Field-Level Permissions)**

**The Problem without CQRS:**
You have a `User` entity with `Email`, `DisplayName`, and `IsAdmin`.

- **Problem:** If you expose a generic `UpdateUser(User user)` API endpoint, a malicious user might try to send `{ "IsAdmin": true }` along with their payload. You have to write rigid, complex validation logic in your API controller to blindly check every property: "If the current user is not admin, ignore the IsAdmin property." This logic gets scattered everywhere.

**The Solution with CQRS:**
You create specific commands for specific actions, automatically enforcing security by design.

**The Technical Implementation:**

- **Command 1:** `UpdateUserProfileCommand`. This DTO *only* contains `DisplayName` and `Bio`. It strictly *cannot* touch the `IsAdmin` flag because that property doesn't even exist on the command class.
- **Command 2:** `PromoteUserToAdminCommand`. This command *only* exists for the `IsAdmin` change. You can decorate the *handler* for this command with a specific `[Authorize(Roles = "SuperAdmin")]` attribute.

**Result:** Security is not an "if statement" deep inside your code; it is declarative at the class level. You can't accidentally allow a user to escalate privileges because the "Update Profile" command physically lacks the ability to change roles.

This pattern might not be suitable when:

- The domain or the business rules are simple.
- A simple CRUD-style user interface and data access operations are sufficient.

## **Example: Independent Evolution of Models**

This example demonstrates how the **Write Model** and **Read Model** for a Bank Account can evolve completely separately.

### **Phase 1: The Requirement**

- **Write Requirement:** Enforce strict validation (no negative deposits).
- **Read Requirement:** Show the balance to the user in a visually pleasing format (e.g., "$1,230.50").

### **The Write Side (Focus: Integrity)**

The Write Model uses a **Domain Entity** that maps to a 3rd Normal Form SQL table. Its job is to protect data integrity.

```csharp
// 1. The Command (User Intent)
public class DepositCommand : ICommand
{
    public Guid AccountId { get; set; }
    public decimal Amount { get; set; }
}

// 2. The Domain Entity (Business Logic)
// This maps to a strict SQL table: [Accounts] { Id (PK), Balance (decimal) }
public class BankAccount
{
    public Guid Id { get; private set; }
    public decimal Balance { get; private set; }

    public void Deposit(decimal amount)
    {
        // Business Rule: State integrity
        if (amount <= 0) throw new InvalidOperationException("Amount must be positive");
        Balance += amount;
    }
}

// 3. The Handler (Orchestration)
public class DepositCommandHandler
{
    public void Handle(DepositCommand command)
    {
        var account = _repo.Load(command.AccountId);
        account.Deposit(command.Amount); // Enforce rules
        _repo.Save(account); // Persist to normalized SQL
    }
}

```

### **The Read Side (Focus: UX & Performance)**

The Read Model doesn't care about business rules; it cares about speed.

**Evolution Scenario:**
Imagine the "Account Summary" page is the most visited page in the app (10,000 req/sec). Querying the normalized SQL table is too slow.

**The Evolution:** We change the Read Side to read from a **Redis Cache** or a flattened **NoSQL Document**, *without touching the Write Side code at all*.

```csharp
// 1. The View Model (The Contract)
// This is exactly what the UI expects. It hasn't changed.
public class AccountSummaryViewModel
{
    public string AccountId { get; set; }
    public string DisplayBalance { get; set; } // Pre-formatted currency
    public string StatusLabel { get; set; }    // Pre-calculated status
}

// 2. The Query Handler (The Evolution)
// Previously: SELECT * FROM Accounts
// NOW: Reads from a high-speed Redis cache.
public class AccountQueryHandler
{
    private readonly ICache _redisCache;

    public AccountSummaryViewModel GetSummary(Guid id)
    {
        // FAST: Get pre-computed JSON from Redis
        var cachedJson = _redisCache.GetString($"account:{id}");
        if (cachedJson != null)
        {
            return JsonSerializer.Deserialize<AccountSummaryViewModel>(cachedJson);
        }

        // Fallback or other logic...
        return new AccountSummaryViewModel();
    }
}

```

**Key Takeaway:**

- The **Write Side** kept using rigid SQL transactions to ensure money is never lost.
- The **Read Side** evolved to use Redis for extreme speed.
- Neither side broke the other because they share **no code**. They are decoupled.

## **Combine the Event Sourcing and CQRS patterns**

Some implementations of CQRS incorporate the [Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing). This pattern stores the system's state as a chronological series of events. Each event captures the changes made to the data at a specific time. To determine the current state, the system replays these events in order. In this setup:

- The event store is the *write model* and the single source of truth.
- The *read model* generates materialized views from these events, typically in a highly denormalized form. These views optimize data retrieval by tailoring structures to query and display requirements.

**Benefits of combining the Event Sourcing and CQRS patterns**

The same events that update the write model can serve as inputs to the read model. The read model can then build a real-time snapshot of the current state. These snapshots optimize queries by providing efficient and precomputed views of the data.

Instead of directly storing the current state, the system uses a stream of events as the write store. This approach reduces update conflicts on aggregates and enhances performance and scalability. The system can process these events asynchronously to build or update materialized views for the read data store.

Because the event store acts as the single source of truth, you can easily regenerate materialized views or adapt to changes in the read model by replaying historical events. Basically, materialized views function as a durable, read-only cache that's optimized for fast and efficient queries.

**Considerations for how to combine the Event Sourcing and CQRS patterns**

Before you combine the CQRS pattern with the [Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing), evaluate the following considerations:

- **Eventual consistency:** Because the write and read data stores are separate, updates to the read data store might lag behind event generation. This delay results in eventual consistency.
- **Increased complexity:** Combining the CQRS pattern with the Event Sourcing pattern requires a different design approach, which can make a successful implementation more challenging. You must write code to generate, process, and handle events, and assemble or update views for the read model. However, the Event Sourcing pattern simplifies domain modeling and allows you to rebuild or create new views easily by preserving the history and intent of all data changes.
- **Performance of view generation:** Generating materialized views for the read model can consume significant time and resources. The same applies to projecting data by replaying and processing events for specific entities or collections. Complexity increases when calculations involve analyzing or summing values over long periods because all related events must be examined. Implement snapshots of the data at regular intervals. For example, store the current state of an entity or periodic snapshots of aggregated totals, which is the number of times a specific action occurs. Snapshots reduce the need to process the full event history repeatedly, which improves performance.