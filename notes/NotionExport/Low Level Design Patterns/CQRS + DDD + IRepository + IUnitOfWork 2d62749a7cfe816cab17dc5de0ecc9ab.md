# CQRS + DDD + IRepository + IUnitOfWork

This is a comprehensive reference guide. It transitions from standard layering to **Domain-Driven Design (DDD)** combined with **CQRS, Repository Pattern**, and **Unit of Work**.

---

# **The Big Shift: Where does the code go?**

- Before seeing the code, it is vital to understand the **Movement of Logic**.

| Concept | Standard Approach (Transaction Script) | DDD Approach |
| --- | --- | --- |
| **Data properties** | Public Get/Set (Open for modification) | **Private Setters** (Protected state) |
| **Validation** | In the Controller or Service | **In the Entity** (Self-validating) |
| **Business Logic** | In the Service (e.g., service.CalculateInterest()) | **In the Entity** (e.g., account.CalculateInterest()) |
| **Object Creation** | new Account() { ... } | **Static Factory** (Account.Open(...)) |
| **Data Loading** | ORM loads data directly | **Static Loader / Factory** (Reconstitution) |
| **Orchestration** | Service calls Repository & Logic | **Command Handler** loads Aggregate -> calls Domain Logic -> Saves |

---

# **The Complete Implementation**

- We will build a **Banking System**.

## **1. The Domain Layer (The Heart)**

- *No Database references allowed here.*
- **Key DDD Concepts applied:**
    1. **Private Setters:** Prevent outside classes from corrupting data.
    2. **Rich Behavior:** The class contains the logic (Deposit), not just data.
    3. **Static Factory (Open):** For creating new data.
    4. **Static Loader (Load):** Used by the Repository to convert raw DB data into a Domain Object (if strictly separating Data Models from Domain Models). *Note: EF Core can map directly to private fields, but I will show the explicit Loader pattern as requested.*
    
    ```csharp
    using System;
    using System.Collections.Generic;
    
    namespace Domain
    {
        public class BankAccount
        {
            // 1. Private Setters (Encapsulation)
            public Guid Id { get; private set; }
            public string Email { get; private set; }
            public decimal Balance { get; private set; }
    
            // Domain Event collection (Optional but common in DDD)
            public List<string> DomainEvents { get; private set; } = new List<string>();
    
            // EF Core needs a constructor, usually private or protected
            protected BankAccount() { }
    
            // 2. Static Factory (For Creating NEW entities)
            public static BankAccount Open(string email, decimal initialBalance)
            {
                if (initialBalance < 100)
                    throw new Exception("Minimum opening balance is 100");
    
                return new BankAccount
                {
                    Id = Guid.NewGuid(),
                    Email = email,
                    Balance = initialBalance
                };
            }
    
            // 3. Static Loader (For Reconstituting EXISTING entities from DB)
            // This allows us to separate the DB Data Model from the Domain Model if needed.
            public static BankAccount Load(Guid id, string email, decimal balance)
            {
                return new BankAccount
                {
                    Id = id,
                    Email = email,
                    Balance = balance
                };
            }
    
            // 4. Domain Logic (Behavior)
            public void Deposit(decimal amount)
            {
                if (amount <= 0) throw new Exception("Deposit must be positive");
                Balance += amount;
                DomainEvents.Add($"Deposited {amount} at {DateTime.Now}");
            }
    
            public void Withdraw(decimal amount)
            {
                if (Balance - amount < 0) throw new Exception("Insufficient funds");
                Balance -= amount;
            }
        }
    
        // Domain Interfaces
        public interface IGenericRepository<T> where T : class
        {
            T GetById(Guid id);
            void Add(T entity);
            void Update(T entity);
        }
    
        public interface IAccountRepository : IGenericRepository<BankAccount>
        {
            // Specific Domain Query
            BankAccount GetByEmail(string email);
        }
    
        public interface IUnitOfWork : IDisposable
        {
            IAccountRepository Accounts { get; }
            int Commit();
        }
    }
    
    ```
    

## **2. The Infrastructure Layer (The Plumbing)**

- *This knows about EF Core.*
    
    ```csharp
    using Microsoft.EntityFrameworkCore;
    using System.Linq;
    using Domain;
    
    namespace Infrastructure
    {
        // 1. The EF Core DbContext
        public class BankDbContext : DbContext
        {
            public DbSet<BankAccount> BankAccounts { get; set; }
    
            protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
            {
                optionsBuilder.UseInMemoryDatabase(databaseName: "DDDBankDb");
            }
        }
    
        // 2. Generic Repository Implementation
        public class GenericRepository<T> : IGenericRepository<T> where T : class
        {
            protected readonly BankDbContext _context;
            protected readonly DbSet<T> _dbSet;
    
            public GenericRepository(BankDbContext context)
            {
                _context = context;
                _dbSet = context.Set<T>();
            }
    
            public T GetById(Guid id) => _dbSet.Find(id);
    
            public void Add(T entity) => _dbSet.Add(entity);
    
            public void Update(T entity)
            {
                // In EF Core, if the object is tracked, this isn't strictly necessary,
                // but good for explicit updates.
                _dbSet.Attach(entity);
                _context.Entry(entity).State = EntityState.Modified;
            }
        }
    
        // 3. Specific Repository (Implementation)
        public class AccountRepository : GenericRepository<BankAccount>, IAccountRepository
        {
            public AccountRepository(BankDbContext context) : base(context) { }
    
            public BankAccount GetByEmail(string email)
            {
                // Using EF Core to find by custom logic
                return _dbSet.FirstOrDefault(x => x.Email == email);
            }
        }
    
        // 4. Unit of Work Implementation
        public class UnitOfWork : IUnitOfWork
        {
            private readonly BankDbContext _context;
            public IAccountRepository Accounts { get; private set; }
    
            public UnitOfWork(BankDbContext context)
            {
                _context = context;
                Accounts = new AccountRepository(_context);
            }
    
            public int Commit()
            {
                return _context.SaveChanges();
            }
    
            public void Dispose()
            {
                _context.Dispose();
            }
        }
    }
    
    ```
    

## **3. The Application Layer (CQRS)**

- *This separates Reads (Queries) from Writes (Commands).*
- **CQRS Concepts:**
    - **Command:** An intent to change state (Create, Update, Delete). Returns void or ID.
    - **Query:** An intent to read data. Returns DTOs.
    - **Handlers:** The logic that executes the command or query.
    
    ```csharp
    using Domain;
    namespace Application.CQRS
    {
        // --- DEFINITIONS ---
        // Interface for a Command (Write)
        public interface ICommand { }
    
        // Interface for a Query (Read)
        public interface IQuery<TResult> { }
    
        // Handler Interfaces
        public interface ICommandHandler<TCommand> where TCommand : ICommand
        {
            void Handle(TCommand command);
        }
    
        public interface IQueryHandler<TQuery, TResult> where TQuery : IQuery<TResult>
        {
            TResult Handle(TQuery query);
        }
    
        // --- DTOs (Data Transfer Objects) ---
        public class AccountDto
        {
            public Guid Id { get; set; }
            public decimal Balance { get; set; }
        }
    
        // --- COMMANDS (WRITES) ---
    
        // 1. The Command Object (Data Payload)
        public class CreateAccountCommand : ICommand
        {
            public string Email { get; set; }
            public decimal InitialAmount { get; set; }
        }
    
        // 2. The Command Handler (The Logic)
        public class CreateAccountHandler : ICommandHandler<CreateAccountCommand>
        {
            private readonly IUnitOfWork _uow;
    
            public CreateAccountHandler(IUnitOfWork uow)
            {
                _uow = uow;
            }
    
            public void Handle(CreateAccountCommand command)
            {
                // A. Use Domain Factory (Logic is in Domain, not here)
                var account = BankAccount.Open(command.Email, command.InitialAmount);
    
                // B. Use Repository to Add
                _uow.Accounts.Add(account);
    
                // C. Commit Transaction
                _uow.Commit();
    
                Console.WriteLine($"[Command] Account created ID: {account.Id}");
            }
        }
    
        public class DepositCommand : ICommand
        {
            public Guid AccountId { get; set; }
            public decimal Amount { get; set; }
        }
    
        public class DepositHandler : ICommandHandler<DepositCommand>
        {
            private readonly IUnitOfWork _uow;
    
            public DepositHandler(IUnitOfWork uow)
            {
                _uow = uow;
            }
    
            public void Handle(DepositCommand command)
            {
                // A. Load Aggregate Root
                var account = _uow.Accounts.GetById(command.AccountId);
                if (account == null) throw new Exception("Account not found");
    
                // B. Execute Domain Logic (Logic is in Domain, not here)
                account.Deposit(command.Amount);
    
                // C. Commit
                _uow.Commit();
                Console.WriteLine($"[Command] Deposited {command.Amount}. New Balance: {account.Balance}");
            }
        }
    
        // --- QUERIES (READS) ---
    
        // 1. The Query Object
        public class GetAccountBalanceQuery : IQuery<AccountDto>
        {
            public string Email { get; set; }
        }
    
        // 2. The Query Handler
        public class GetAccountBalanceHandler : IQueryHandler<GetAccountBalanceQuery, AccountDto>
        {
            // In pure CQRS, we often bypass the Domain Repository for queries
            // and use a "Read Repository" or direct DB access (Dapper/EF).
            // Here we use the Repo for simplicity.
            private readonly IAccountRepository _repo;
    
            public GetAccountBalanceHandler(IAccountRepository repo)
            {
                _repo = repo;
            }
    
            public AccountDto Handle(GetAccountBalanceQuery query)
            {
                // Use the Specific Repository Method
                var account = _repo.GetByEmail(query.Email);
    
                if (account == null) return null;
    
                // Map to DTO (Never return Domain Entity in a Query)
                return new AccountDto
                {
                    Id = account.Id,
                    Balance = account.Balance
                };
            }
        }
    }
    
    ```
    

## **4. Putting it together (Program.cs)**

```csharp
using Application.CQRS;
using Infrastructure;
using Domain;

class Program
{
    static void Main(string[] args)
    {
        // 1. Setup Dependencies (In real app, use Dependency Injection container)
        var dbContext = new BankDbContext();
        var unitOfWork = new UnitOfWork(dbContext);
        var accountRepo = new AccountRepository(dbContext);

        // Setup Handlers
        var createHandler = new CreateAccountHandler(unitOfWork);
        var depositHandler = new DepositHandler(unitOfWork);
        var queryHandler = new GetAccountBalanceHandler(accountRepo);

        // ---------------------------------------------------------
        // SCENARIO 1: Create Account (Command)
        // ---------------------------------------------------------
        var createCmd = new CreateAccountCommand
        {
            Email = "user@example.com",
            InitialAmount = 500
        };

        createHandler.Handle(createCmd);

        // ---------------------------------------------------------
        // SCENARIO 2: Deposit Money (Command)
        // ---------------------------------------------------------
        // We need the ID, usually returned by command or looked up
        var accountData = queryHandler.Handle(new GetAccountBalanceQuery { Email = "user@example.com" });

        var depositCmd = new DepositCommand
        {
            AccountId = accountData.Id,
            Amount = 250
        };

        depositHandler.Handle(depositCmd);

        // ---------------------------------------------------------
        // SCENARIO 3: Read Data (Query)
        // ---------------------------------------------------------
        var query = new GetAccountBalanceQuery { Email = "user@example.com" };
        var result = queryHandler.Handle(query);

        Console.WriteLine($"[Query] Final Balance for {query.Email}: {result.Balance}");

        // Cleanup
        unitOfWork.Dispose();
    }
}

```

---

# **Detailed Breakdown of Concepts Used**

### **1. Why the "Static Loader" (BankAccount.Load)?**

- In DDD, entities are not simple data containers; they are behavior objects.
    - **Problem:** If you use a public constructor, a developer might create an account with Balance = -500 bypassing your validation.
    - **Solution:**
        - We make the constructor protected or private.
        - We use `Open(...)` factory for **Business Creation** (Enforces rules like "Min balance 100").
        - We use `Load(...)` (or EF Core's internal reflection) for **Infrastructure Loading** (Puts data back into the object without triggering business rules validation, because the data is already trusted from the DB).

### **2. Why Generic Repository + Specific Repository?**

- **Generic (IGenericRepository):** Removes boilerplate. You don't want to write FindById for Account, Customer, Transaction, Log manually.
- **Specific (IAccountRepository):** DDD Repositories should speak the Ubiquitous Language. `GetByEmail` is a business requirement, not a generic DB function. This is where you put complex LINQ or SQL queries hidden behind a clean name.

### **3. Why CQRS (Command/Query)?**

- **Segregation:** In large systems, the way you write data (complex validation, transactions, domain events) is very different from how you *read* data (simple filters, paging, joining tables).
- **Performance:** ICommand uses the heavy Domain Model (Repo + UoW + Entity Logic). IQuery can just select a DTO directly from the DB, skipping the overhead of creating a full Domain Entity.

### **4. How IRepository & IUnitOfWork fit in DDD?**

- **Repository:** In DDD, a Repository abstracts the **Aggregate Root** collection. It gives the illusion that all Bank Accounts are just sitting in a list in memory. It protects the Domain from knowing about SQL or Entity Framework.
- **UnitOfWork:** Represents the **Business Transaction**. It ensures that if the Command Handler modifies an Account and creates a Transaction Log, both are saved atomically. In DDD, one Command = One Transaction.