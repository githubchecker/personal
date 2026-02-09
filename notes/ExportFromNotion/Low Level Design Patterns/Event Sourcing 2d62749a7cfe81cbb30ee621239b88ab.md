# Event Sourcing

[Event Sourcing pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)

Instead of storing just the current state of the data in a relational database, store the full series of actions taken on an object in an append-only store. The store acts as the system of record and can be used to materialize the domain objects. This approach can improve performance, scalability, and auditability in complex systems.

**Important**

Event sourcing is a complex pattern that permeates through the entire architecture and introduces trade-offs to achieve increased performance, scalability, and auditability. Once your system becomes an event sourcing system, all future design decisions are constrained by the fact that this is an event sourcing system. There is a high cost to migrate to or from an event sourcing system. This pattern is best suited for systems where performance and scalability are top requirements. The complexity that event sourcing adds to a system isn't justified for most systems.

**Context and problem**

Most applications work with data, and the typical approach is for the application to store the latest state of the data in a relational database, inserting or updating data as required. For example, in the traditional create, read, update, and delete (CRUD) model, a typical data process is to read data from the store, make some modifications to it, and update the current state of the data with the new values—often by using transactions that lock the data.

The CRUD approach is straightforward and fast for most scenarios. However, in high-load systems, this approach has some challenges:

- **Performance**: As the system scales, the performance will degrade due to contention for resources and locking issues.
- **Scalability**: CRUD systems are synchronous and data operations block on updates. This can lead to bottlenecks and higher latency when the system is under load.
- **Auditability**: CRUD systems only store the latest state of the data. Unless there's an auditing mechanism that records the details of each operation in a separate log, history is lost.

**Solution**

The Event Sourcing pattern defines an approach to handling operations on data that's driven by a sequence of events, each of which is recorded in an append-only store. Application code raises events that imperatively describe the action taken on the object. The events are generally sent to a queue where a separate process, an event handler, listens to the queue and persists the events in an event store. Each event represents a logical change to the object, such as `AddedItemToOrder` or `OrderCanceled`.

The events are persisted in an event store that acts as the system of record (the authoritative data source) about the current state of the data. Additional event handlers can listen for events they are interested in and take an appropriate action. Consumers could, for example, initiate tasks that apply the operations in the events to other systems, or perform any other associated action that's required to complete the operation. Notice that the application code that generates the events is decoupled from the systems that subscribe to the events.

At any point, it's possible for applications to read the history of events. You can then use the events to materialize the current state of an entity by playing back and consuming all the events that are related to that entity. This process can occur on demand to materialize a domain object when handling a request.

Because it's relatively expensive to read and replay events, applications typically implement [materialized views](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view), read-only projections of the event store that are optimized for querying. For example, a system can maintain a materialized view of all customer orders that's used to populate the UI. As the application adds new orders, adds or removes items on the order, or adds shipping information, events are raised and a handler updates the materialized view.

The figure shows an overview of the pattern, including some typical implementations with the pattern, including the use of a queue, a read-only store, integrating events with external applications and systems, and replaying events to create projections of the current state of specific entities.

![An overview and example of the Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/_images/event-sourcing-overview.png)

**Workflow**

The following describes a typical workflow for this pattern:

1. The presentation layer calls an object responsible for reading from a read-only store. The data returned is used to populate the UI.
2. The presentation layer calls command handlers to perform actions like create a cart, or add an item to the cart.
3. The command handler calls the event store to get the historical events for the entity. For example, it might retrieve all cart events. Those events are played back in the object to materialize the current state of the entity, prior to any action taking place.
4. The business logic is run and events are raised. In most implementations, the events are pushed to a queue or topic to decouple the event producers and event consumers.
5. Event handlers listen for events they are interested in and perform the appropriate action for that handler. Some typical event handler actions are:
    1. Writing the events to the event store
    2. Updating a read-only store optimized for queries
    3. Integrating with external systems

**Pattern advantages**

The Event Sourcing pattern provides the following advantages:

- Events are immutable and can be stored using an append-only operation. The user interface, workflow, or process that initiated an event can continue, and tasks that handle the events can run in the background. This process, combined with the fact that there's no contention during the processing of transactions, can vastly improve performance and scalability for applications, especially for the presentation layer.
- Events are simple objects that describe some action that occurred, together with any associated data that's required to describe the action represented by the event. Events don't directly update a data store. They're simply recorded for handling at the appropriate time. Using events can simplify implementation and management.
- Events typically have meaning for a domain expert, whereas object-relational impedance mismatch can make complex database tables hard to understand. Tables are artificial constructs that represent the current state of the system, not the events that occurred.
- Event sourcing can help prevent concurrent updates from causing conflicts because it avoids the requirement to directly update objects in the data store. However, the domain model must still be designed to protect itself from requests that might result in an inconsistent state.
- The append-only storage of events provides an audit trail that can be used to monitor actions taken against a data store. It can regenerate the current state as materialized views or projections by replaying the events at any time, and it can assist in testing and debugging the system. In addition, the requirement to use compensating events to cancel changes can provide a history of changes that were reversed. This capability wouldn't be the case if the model stored the current state. The list of events can also be used to analyze application performance and to detect user behavior trends. Or, it can be used to obtain other useful business information.
- The command handlers raise events, and tasks perform operations in response to those events. This decoupling of the tasks from the events provides flexibility and extensibility. Tasks know about the type of event and the event data, but not about the operation that triggered the event. In addition, multiple tasks can handle each event. This enables easy integration with other services and systems that only listen for new events raised by the event store. However, the event sourcing events tend to be very low level, and it might be necessary to generate specific integration events instead.

> Event sourcing is commonly combined with the CQRS pattern by performing the data management tasks in response to the events, and by materializing views from the stored events.
> 

**Issues and considerations**

Consider the following points when deciding how to implement this pattern:

- **Eventual consistency** - The system will only be eventually consistent when creating materialized views or generating projections of data by replaying events. There's some delay between an application adding events to the event store as the result of handling a request, the events being published, and the consumers of the events handling them. During this period, new events that describe further changes to entities might have arrived at the event store. Your customers must be okay with the fact that data is eventually consistent and the system should be designed to account for eventual consistency in these scenarios.
    
    **Note**
    
    For more information about eventual consistency, see the [**Data Consistency Primer**](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/dn589800(v=pandp.10)).
    
- **Versioning events** - The event store is the permanent source of information, and so the event data should never be updated. The only way to update an entity or undo a change is to add a compensating event to the event store. If the schema (rather than the data) of the persisted events needs to change, perhaps during a migration, it can be difficult to combine existing events in the store with the new version. Your application will need to support changes to events structures. This can be done in several ways.
    - Ensure your event handlers support all versions of events. This can be a challenge to maintain and test. This requires implementing a version stamp on each version of the event schema to maintain both the old and the new event formats.
    - Implement an event handler to handle specific event versions. This can be a maintenance challenge in that bug fix changes might have to be made across multiple handlers. This requires implementing a version stamp on each version of the event schema to maintain both the old and the new event formats.
    - Update historical events to the new schema when a new schema is implemented. This breaks the immutability of events.
- **Event ordering** - Multi-threaded applications and multiple instances of applications might be storing events in the event store. The consistency of events in the event store is vital, as is the order of events that affect a specific entity (the order that changes occur to an entity affects its current state). Adding a timestamp to every event can help to avoid issues. Another common practice is to annotate each event resulting from a request with an incremental identifier. If two actions attempt to add events for the same entity at the same time, the event store can reject an event that matches an existing entity identifier and event identifier.
- **Querying events** - There's no standard approach, or existing mechanisms such as SQL queries, for reading the events to obtain information. The only data that can be extracted is a stream of events using an event identifier as the criteria. The event ID typically maps to individual entities. The current state of an entity can be determined only by replaying all of the events that relate to it against the original state of that entity.
- **Cost of recreating state for entities** - The length of each event stream affects managing and updating the system. If the streams are large, consider creating snapshots at specific intervals such as a specified number of events. The current state of the entity can be obtained from the snapshot and by replaying any events that occurred after that point in time. For more information about creating snapshots of data, see [Primary-Subordinate Snapshot Replication](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/ff650012(v=pandp.10)).
- **Conflicts** - Even though event sourcing minimizes the chance of conflicting updates to the data, the application must still be able to deal with inconsistencies that result from eventual consistency and the lack of transactions. For example, an event that indicates a reduction in stock inventory might arrive in the data store while an order for that item is being placed. This situation results in a requirement to reconcile the two operations, either by advising the customer or by creating a back order.
- **Need for idempotency** - Event publication might be *at least once*, and so consumers of the events must be idempotent. They must not reapply the update described in an event if the event is handled more than once. Multiple instances of a consumer can maintain and aggregate an entity's property, such as the total number of orders placed. Only one must succeed in incrementing the aggregate, when an order-placed event occurs. While this result isn't a key characteristic of event sourcing, it's the usual implementation decision.
- **Circular logic** - Be mindful of scenarios where the processing of one event involves the creation of one or more new events since this can cause an infinite loop.

**When to use this pattern**

Use this pattern in the following scenarios:

- When you want to capture intent, purpose, or reason in the data. For example, changes to a customer entity can be captured as a series of specific event types, such as *Moved home*, *Closed account*, or *Deceased*.
- When it's vital to minimize or completely avoid the occurrence of conflicting updates to data.
- When you want to record events that occur, to replay them to restore the state of a system, to roll back changes, or to keep a history and audit log. For example, when a task involves multiple steps, you might need to execute actions to revert updates and then replay some steps to bring the data back into a consistent state.
- When you use events. It's a natural feature of the operation of the application, and it requires little extra development or implementation effort.
- When you need to decouple the process of inputting, or updating data from the tasks required to apply these actions. This change might be to improve UI performance, or to distribute events to other listeners that take action when the events occur. For example, you can integrate a payroll system with an expense submission website. The events that are raised by the event store in response to data updates made in the website would be consumed by both the website and the payroll system.
- When you want flexibility to be able to change the format of materialized models and entity data if requirements change, or—when used with CQRS—you need to adapt a read model or the views that expose the data.
- When used with CQRS, and eventual consistency is acceptable while a read model is updated, or the performance impact of rehydrating entities and data from an event stream is acceptable.

This pattern might not be useful in the following situations:

- Applications that do not require hyper-scale or performance.
- Small or simple domains, systems that have little or no business logic, or nondomain systems that naturally work well with traditional CRUD data management mechanisms.
- Systems where consistency and real-time updates to the views of the data are required.
- Systems where there's only a low occurrence of conflicting updates to the underlying data. For example, systems that predominantly add data rather than updating it.

# **Example:**

In a production Event Sourcing + CQRS architecture, we split the storage physically or logically:

1. **Write DB (Event Store):** An append-only list of events. (Optimized for writing).
2. **Read DB (Projections):** A standard SQL/NoSQL database optimized for querying (filtering, sorting).

Here is the **Complete Architecture** connecting the dots.

### The "Why" - The Architecture Flow

1. **Command** comes in $\to$ **Command Handler** loads Aggregate from **Event Store**.
2. Aggregate logic runs $\to$ New Events are saved to **Event Store**.
3. **Background Process (Projector)** picks up new events $\to$ Updates the **Read DB**.
4. **Query** comes in $\to$ **Query Handler** reads *only* from **Read DB**.

---

### 1. Infrastructure: The Two Separated Databases

We will simulate two completely different storage mechanisms.

```csharp
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;

// --- DATABASE 1: THE WRITE SIDE (Event Store) ---
// In real life, this could be "EventStoreDB" or a CosmosDB collection.
public class EventStoreRecord
{
    public Guid Id { get; set; }
    public Guid AggregateId { get; set; }
    public string EventType { get; set; }
    public string EventDataJson { get; set; } // Serialized Event
    public DateTime Timestamp { get; set; }
}

public class WriteDbContext : DbContext
{
    public DbSet<EventStoreRecord> Events { get; set; }
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseInMemoryDatabase("Write_EventStore_Db");
}

// --- DATABASE 2: THE READ SIDE (Projections) ---
// This is a standard SQL DB optimized for user screens.
public class AccountReadModel
{
    public Guid Id { get; set; }
    public string Email { get; set; }
    public decimal CurrentBalance { get; set; } // Calculated already!
    public int TransactionCount { get; set; }
}

public class ReadDbContext : DbContext
{
    public DbSet<AccountReadModel> Accounts { get; set; }
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseInMemoryDatabase("Read_Reporting_Db");
}

```

### 2. Infrastructure: The Event Repository (Write Side)

This repository *only* talks to the Write DB.

```csharp
// Using Newtonsoft.Json for simulation
using Newtonsoft.Json;

public interface IEventStoreRepository
{
    void Save(Guid aggregateId, IEnumerable<object> events);
    List<object> GetEvents(Guid aggregateId);
}

public class EventStoreRepository : IEventStoreRepository
{
    private readonly WriteDbContext _context;

    public EventStoreRepository(WriteDbContext context)
    {
        _context = context;
    }

    public void Save(Guid aggregateId, IEnumerable<object> events)
    {
        foreach (var e in events)
        {
            _context.Events.Add(new EventStoreRecord
            {
                Id = Guid.NewGuid(),
                AggregateId = aggregateId,
                EventType = e.GetType().Name,
                EventDataJson = JsonConvert.SerializeObject(e),
                Timestamp = DateTime.UtcNow
            });
        }
        _context.SaveChanges();
    }

    public List<object> GetEvents(Guid aggregateId)
    {
        var records = _context.Events
            .Where(x => x.AggregateId == aggregateId)
            .OrderBy(x => x.Timestamp)
            .ToList();

        var events = new List<object>();
        foreach (var r in records)
        {
            // In real app, use a Type Mapper to get the Class from the String Name
            if (r.EventType == "AccountCreated")
                events.Add(JsonConvert.DeserializeObject<AccountCreated>(r.EventDataJson));
            if (r.EventType == "MoneyDeposited")
                events.Add(JsonConvert.DeserializeObject<MoneyDeposited>(r.EventDataJson));
        }
        return events;
    }
}

```

### 3. The Glue: The Projector (Syncing Write -> Read)

In a real system, this runs on a Service Bus (RabbitMQ/Azure Service Bus). Here, we call it manually for the example.

This class **translates** Events into SQL Table updates.

```csharp
public class AccountProjector
{
    private readonly ReadDbContext _readContext;

    public AccountProjector(ReadDbContext readContext)
    {
        _readContext = readContext;
    }

    // This function is called whenever an event is saved
    public void Project(object @event)
    {
        switch (@event)
        {
            case AccountCreated e:
                _readContext.Accounts.Add(new AccountReadModel
                {
                    Id = e.AccountId,
                    Email = e.Email,
                    CurrentBalance = e.InitialBalance,
                    TransactionCount = 1
                });
                break;

            case MoneyDeposited e:
                var acc = _readContext.Accounts.Find(e.AccountId);
                if (acc != null)
                {
                    acc.CurrentBalance += e.Amount;
                    acc.TransactionCount++;
                }
                break;
        }
        _readContext.SaveChanges();
    }
}

```

### 4. The Application Layer: CQRS Handlers

Now we implement the Interfaces (`ICommandHandler`, `IQueryHandler`) properly.

### The WRITE Side (Command Handler)

This works with the Domain Aggregate and saves to the **Event Store**.

```csharp
public class DepositCommandHandler : ICommandHandler<DepositCommand>
{
    private readonly IEventStoreRepository _repository;
    private readonly AccountProjector _projector; // Simulating the Event Bus

    public DepositCommandHandler(IEventStoreRepository repository, AccountProjector projector)
    {
        _repository = repository;
        _projector = projector;
    }

    public void Handle(DepositCommand command)
    {
        // 1. Load History from Write DB
        var events = _repository.GetEvents(command.AccountId);

        // 2. Reconstitute Aggregate (The "Old" Way)
        var account = new BankAccount(); // Assuming internal/private constructor
        account.LoadFromHistory(events);

        // 3. Execute Logic (Generates new Event)
        account.Deposit(command.Amount);

        // 4. Save New Events to Write DB
        var newEvents = account.GetUncommittedChanges();
        _repository.Save(command.AccountId, newEvents);

        // 5. DISPATCH TO READ DB (Critical Step for CQRS)
        // In production, you publish to RabbitMQ here.
        // The "Projector" is the listener.
        foreach(var e in newEvents)
        {
            _projector.Project(e);
        }
    }
}

```

### The READ Side (Query Handler)

This is the missing piece you asked about. It **never** touches the Domain Object or the Event Store. It reads straight from the `ReadDbContext`.

```csharp
// The Query Definition
public class GetAccountSummaryQuery : IQuery<AccountReadModel>
{
    public Guid AccountId { get; set; }
}

// The Query Handler
public class GetAccountSummaryHandler : IQueryHandler<GetAccountSummaryQuery, AccountReadModel>
{
    private readonly ReadDbContext _readContext;

    public GetAccountSummaryHandler(ReadDbContext readContext)
    {
        _readContext = readContext;
    }

    public AccountReadModel Handle(GetAccountSummaryQuery query)
    {
        // FAST! No calculating, no replaying events. Just a SELECT * statement.
        return _readContext.Accounts
            .AsNoTracking() // EF Core optimization for reads
            .FirstOrDefault(x => x.Id == query.AccountId);
    }
}

```

---

### 5. Full Working Example (Program.cs)

Here is how the data flows from Command $\to$ WriteDB $\to$ Projector $\to$ ReadDB $\to$ Query.

```csharp
class Program
{
    static void Main(string[] args)
    {
        // --- SETUP (Dependency Injection) ---
        var writeDb = new WriteDbContext();
        var readDb = new ReadDbContext();

        var eventRepo = new EventStoreRepository(writeDb);
        var projector = new AccountProjector(readDb);

        // Handlers
        var depositHandler = new DepositCommandHandler(eventRepo, projector);
        var queryHandler = new GetAccountSummaryHandler(readDb);

        // --- STEP 1: INITIAL DATA ---
        // Let's manually inject an "AccountCreated" event into the system to start
        Guid myId = Guid.NewGuid();
        var createEvent = new AccountCreated(myId, "expert@code.com", 100);

        // Save to Write DB
        eventRepo.Save(myId, new List<object> { createEvent });
        // Project to Read DB
        projector.Project(createEvent);

        Console.WriteLine("Account Created. Initial Balance: 100");

        // --- STEP 2: THE CQRS WRITE OPERATION ---
        var cmd = new DepositCommand { AccountId = myId, Amount = 50 };
        depositHandler.Handle(cmd);

        Console.WriteLine("Command Executed: Deposited 50.");

        // --- STEP 3: THE CQRS READ OPERATION ---
        // notice: we are using a QUERY object, not an ID
        var query = new GetAccountSummaryQuery { AccountId = myId };
        var result = queryHandler.Handle(query);

        Console.WriteLine("------------------------------------------------");
        Console.WriteLine($"[Read DB Result] User: {result.Email}");
        Console.WriteLine($"[Read DB Result] Balance: {result.CurrentBalance}");
        Console.WriteLine($"[Read DB Result] Total Transactions: {result.TransactionCount}");
        Console.WriteLine("------------------------------------------------");
    }
}

```

### Why Separate Databases? (Expert Insight)

1. **Scaling:**
    - Your app has 100 writes per minute, but 1,000,000 reads per minute.
    - With separation, you can run the `ReadDbContext` on 5 cheap servers (Load Balanced) and the `WriteDbContext` on 1 expensive secure server.
2. **Performance:**
    - **Write Side:** needs to be fast at appending (Inserting). No Complex joins.
    - **Read Side:** needs to be fast at selecting. The `Projector` does the heavy math *once* during saving. The `QueryHandler` just reads the final number.
3. **Flexibility:**
    - You can destroy the `ReadDbContext` entirely. Then, verify your code, run a loop over all events in `WriteDbContext` (Replay), and rebuild the `ReadDbContext` from scratch. This allows you to change how screens look without losing data.