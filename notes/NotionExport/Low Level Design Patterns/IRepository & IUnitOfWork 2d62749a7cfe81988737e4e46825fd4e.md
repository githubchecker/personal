# IRepository & IUnitOfWork

- As a beginner, these two patterns often seem intimidating, but they are actually about **organizing your code** to make it cleaner and safer.
- Here is the high-level concept before we dig into code:
    1. **Repository Pattern:** Think of this as a **Librarian**. Instead of you going into the messy storage room (Database) to find a book, you ask the Librarian (Repository) for it. You don't care *how* they find it, you just want the result.
    2. **Unit of Work:** Think of this as a **Shopping Cart Transaction**. You might pick up 5 items (operations), but the "purchase" (saving to the database) only happens once at the checkout. If your credit card fails, *none* of the items are bought.

---

# **1. The Repository Pattern**

- **The Problem:** Without this pattern, your C# code (Controllers or Logic) is often cluttered with SQL commands or Entity Framework logic. If you change your database later, you have to rewrite your whole app.
- **The Solution:** We create an Interface (IRepository) that acts as a contract.
- **The Model**
    - First, let's imagine a simple class we want to save.
    
    ```csharp
    public class Employee
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Department { get; set; }
    }
    
    ```
    
- **The Interface (IRepository)**
    - This is the "Contract." It lists what operations are available without saying *how* they work.
    
    ```csharp
    using System.Collections.Generic;
    
    public interface IEmployeeRepository
    {
        Employee GetById(int id);
        IEnumerable<Employee> GetAll();
        void Add(Employee employee);
        void Remove(int id);
    }
    
    ```
    
- **The Implementation**
    - Now we write the actual code. In a real app, this would use Entity Framework or SQL. For this simple example, I will use a List to pretend it's a database.
    
    ```csharp
    using System.Linq;
    
    public class EmployeeRepository : IEmployeeRepository
    {
        // This List acts as our "Fake Database" for this example
        private readonly List<Employee> _fakeDatabase;
    
        public EmployeeRepository(List<Employee> database)
        {
            _fakeDatabase = database;
        }
    
        public void Add(Employee employee)
        {
            _fakeDatabase.Add(employee);
            // Notice: We are NOT saving to a physical DB here yet.
            // We are just adding it to the memory collection.
        }
    
        public Employee GetById(int id)
        {
            return _fakeDatabase.FirstOrDefault(e => e.Id == id);
        }
    
        public IEnumerable<Employee> GetAll()
        {
            return _fakeDatabase;
        }
    
        public void Remove(int id)
        {
            var emp = GetById(id);
            if (emp != null) _fakeDatabase.Remove(emp);
        }
    }
    
    ```
    

---

# **2. The Unit of Work Pattern**

- **The Problem:** If you have an EmployeeRepository and an OfficeRepository, and you try to save a new Employee and a new Office, what happens if the Employee saves successfully but the Office fails? You have corrupted data.
- **The Solution:** The **Unit of Work** acts as a wrapper. It tracks all changes requested by the Repositories and saves them all at once.
- **The Interface (IUnitOfWork)**
    
    ```csharp
    public interface IUnitOfWork : IDisposable
    {
        // The Unit of Work needs to expose your Repositories
        IEmployeeRepository Employees { get; }
    
        // The famous "Save" button
        int Complete();
    }
    
    ```
    
- **The Implementation**
    - In a real scenario (using Entity Framework), the DbContext is actually the Unit of Work. Here is how we wrap it manually:
    
    ```csharp
    public class UnitOfWork : IUnitOfWork
    {
        // We hold the data source here
        private readonly List<Employee> _fakeDatabase;
    
        public UnitOfWork()
        {
            _fakeDatabase = new List<Employee>();
            // We initialize the repository with our shared data context
            Employees = new EmployeeRepository(_fakeDatabase);
        }
    
        public IEmployeeRepository Employees { get; private set; }
    
        public int Complete()
        {
            // In a real app using Entity Framework, this would be:
            // return _context.SaveChanges();
    
            Console.WriteLine("TRANSACTION COMMITTED: Changes saved to database.");
            return 1;
        }
    
        public void Dispose()
        {
            // Used to clean up memory
            _fakeDatabase.Clear();
        }
    }
    
    ```
    

---

# **3. Putting it all together (Usage)**

- Here is how you would use these in your Program.cs.
    
    ```csharp
    class Program
    {
        static void Main(string[] args)
        {
            // 1. Initialize the Unit of Work
            using (var unitOfWork = new UnitOfWork())
            {
                // 2. Do some work (Add employees)
                // Notice we use unitOfWork.Employees, not the repository directly
                unitOfWork.Employees.Add(new Employee { Id = 1, Name = "John", Department = "IT" });
                unitOfWork.Employees.Add(new Employee { Id = 2, Name = "Sarah", Department = "HR" });
    
                // At this exact moment, nothing is permanently "Saved" or "Committed".
                // It's just sitting in memory waiting.
    
                // 3. Commit the changes
                // If this line fails, nothing gets saved. This ensures data integrity.
                unitOfWork.Complete();
            }
    
            // Verify
            // var allEmps = unitOfWork.Employees.GetAll();
            // foreach(var emp in allEmps)
            // {
            //     Console.WriteLine($"Saved User: {emp.Name}");
            // }
        }
    }
    
    ```
    

---

# **Summary: Why should you care?**

| Feature | Without Pattern | With Pattern |
| --- | --- | --- |
| **Testing** | Hard. Your code is glued to the database. | **Easy.** You can swap the database for a Fake list (like we did above) to test logic. |
| **Consistency** | If saving data step 2 fails, step 1 might remain saved (Bad Data). | **Safe.** Everything is saved at the exact same time (Transaction). |
| **Maintenance** | If you switch from SQL to Oracle, you rewrite everything. | **Clean.** You only change the Repository implementation; the rest of the app stays the same. |

---

# **A Note on Entity Framework (EF Core)**

- If you start reading advanced C# tutorials, you might hear people say: *"Don't use Repository/UnitOfWork with EF Core."*
- **Why?**
    - Because Microsoft built EF Core to act as these patterns already!
        - `DbSet<T>` is effectively a **Repository**.
        - `DbContext` is effectively a **Unit of Work**.
- This is a very standard approach called the **Generic Repository Pattern**.
- To solve your requirement:
    1. **Generic Repository:** Handles standard GetById, Add, Remove logic to avoid code repetition.
    2. **Specific Repository:** Inherits from the Generic one but adds custom logic (e.g., GetAccountsByCustomerId).
    3. **Unit of Work:** Groups them so you can access both from one place.
- Here is a minimal **Bank Account** example using EF Core concepts.

## **1. The Entities (Data Models)**

```csharp
public class Customer { public int Id { get; set; } public string Name { get; set; } }
public class Account { public int Id { get; set; } public int CustomerId { get; set; } public decimal Balance { get; set; } }

// The "Combined Model" you want to return later
public class CustomerPortfolioDto
{
    public string CustomerName { get; set; }
    public decimal TotalBalance { get; set; }
}

```

## **2. The Generic Base (The Reusable Part)**

- This answers your question: *"Should we use basic get by etc as base?"* **Yes.**
    
    ```csharp
    // Interface
    public interface IGenericRepository<T> where T : class
    {
        T GetById(int id);
        IEnumerable<T> GetAll();
        void Add(T entity);
    }
    
    // Implementation
    public class GenericRepository<T> : IGenericRepository<T> where T : class
    {
        protected readonly DbContext _context;
        protected readonly DbSet<T> _dbSet;
    
        public GenericRepository(DbContext context)
        {
            _context = context;
            _dbSet = _context.Set<T>();
        }
    
        public T GetById(int id) => _dbSet.Find(id);
        public IEnumerable<T> GetAll() => _dbSet.ToList();
        public void Add(T entity) => _dbSet.Add(entity);
    }
    
    ```
    

## **3. The Specific Repositories**

- Here we inherit the basic stuff, but add custom banking logic.
    
    ```csharp
    // -------------- CUSTOMER REPO --------------
    public interface ICustomerRepository : IGenericRepository<Customer> { }
    public class CustomerRepository : GenericRepository<Customer>, ICustomerRepository
    {
        public CustomerRepository(DbContext context) : base(context) { }
    }
    
    // -------------- ACCOUNT REPO --------------
    public interface IAccountRepository : IGenericRepository<Account>
    {
        // Custom logic specifically for Accounts
        IEnumerable<Account> GetAccountsByCustomerId(int customerId);
    }
    
    public class AccountRepository : GenericRepository<Account>, IAccountRepository
    {
        public AccountRepository(DbContext context) : base(context) { }
    
        public IEnumerable<Account> GetAccountsByCustomerId(int customerId)
        {
            // We can access _dbSet because it is 'protected' in the base class
            return _dbSet.Where(a => a.CustomerId == customerId).ToList();
        }
    }
    
    ```
    

## **4. The Unit of Work**

- This wraps the two specific repositories.
    
    ```csharp
    public interface IUnitOfWork : IDisposable
    {
        ICustomerRepository Customers { get; }
        IAccountRepository Accounts { get; }
        int Save();
    }
    
    public class UnitOfWork : IUnitOfWork
    {
        private readonly BankDbContext _context; // Assuming BankDbContext exists
    
        public UnitOfWork(BankDbContext context)
        {
            _context = context;
            Customers = new CustomerRepository(_context);
            Accounts = new AccountRepository(_context);
        }
    
        public ICustomerRepository Customers { get; private set; }
        public IAccountRepository Accounts { get; private set; }
    
        public int Save() => _context.SaveChanges();
        public void Dispose() => _context.Dispose();
    }
    
    ```
    

## **5. Usage: Combining Data (The Logic)**

- Here is how you fetch data from **multiple repositories** using the Unit of Work and map it to your combined model.
    
    ```csharp
    public class BankService
    {
        private readonly IUnitOfWork _unitOfWork;
    
        public BankService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }
    
        public CustomerPortfolioDto GetCustomerPortfolio(int customerId)
        {
            // 1. Get Customer data (Using Basic/Generic method)
            var customer = _unitOfWork.Customers.GetById(customerId);
    
            // 2. Get Account data (Using Custom Specific method)
            // Notice how we can easily access a different repo using the same UoW
            var accounts = _unitOfWork.Accounts.GetAccountsByCustomerId(customerId);
    
            // 3. Combine logic to return your Custom Model
            var portfolio = new CustomerPortfolioDto
            {
                CustomerName = customer.Name,
                // Business logic: Summing up the balance
                TotalBalance = accounts.Sum(x => x.Balance)
            };
    
            return portfolio;
        }
    }
    
    ```
    

---

# **Summary of Benefits**

1. **Less Code:** You didn't have to write GetById inside AccountRepository. It got it for free from GenericRepository.
2. **Separation:** The AccountRepository handles specific query logic (Where CustomerId == ...).
3. **Consistency:** The UnitOfWork ensures that if you were to modify the customer and the accounts, `_unitOfWork.Save()` would save both or neither.