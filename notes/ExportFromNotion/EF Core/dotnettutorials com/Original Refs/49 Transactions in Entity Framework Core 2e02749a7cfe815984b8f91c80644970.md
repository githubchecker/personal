# 49. Transactions in Entity Framework Core

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# Transactions in Entity Framework Core (EF Core)

In this article, I will discuss Transactions in Entity Framework Core (EF Core) with Examples. Please read our previous article discussing [Entity Framework Core Inheritance (TPH, TPT, and TPC)](https://dotnettutorials.net/lesson/entity-framework-core-inheritance/) with Examples.

### What are Transactions in Entity Framework Core?

Entity Framework Core (EF Core) is a modern, open-source, cross-platform Object-Relational Mapper (ORM) for .NET. It allows developers to work with a database using .NET objects, eliminating much of the data-access code that we usually need to write.

Transactions in EF Core ensure that a group of database operations (multiple Data Manipulation Language – DML operations) is treated as a single unit of work. This means that either all operations succeed or none of them are applied, maintaining the integrity and consistency of data in the database. This also means that if one operation in a sequence fails, all previous operations within the same transaction are rolled back. This means the job is never half done; either all of it is done, or nothing is done.

### Different Ways to Implement Transactions in Entity Framework Core

EF Core provides several mechanisms to implement transactions, allowing developers to choose the most suitable approach based on the specific requirements of their application. The primary methods include:

- **Implicit or Automatic Transactions with SaveChanges():** By default, EF Core wraps operations in SaveChanges() within a transaction. If any command fails, it throws an exception, and all changes are rolled back.
- **Manual Transactions with Database.BeginTransaction():** Manually control transaction boundaries for multiple operations. That means we can manually begin, commit, or rollback transactions using the Database property of the DbContext instance.
- **Asynchronous Transactions:** We can also manage transactions asynchronously using asynchronous methods, which is useful in web applications where we want to manage transactions without blocking threads.
- **Distributed Transactions with TransactionScope:** Automatically manage transactions that span multiple contexts or databases.

Let’s proceed and understand each method in detail with real-time examples.

### Real-World Example to Understand Transactions with Entity Framework Core:

Consider an e-commerce application where a customer places an order consisting of multiple items. Placing an order involves multiple operations, such as creating an order record, updating inventory, and processing payment. It’s important to note that all the operations are saved successfully; otherwise, the entire operations should be rolled back to maintain data integrity and consistency.

Let us proceed and implement this example using Transactions in Entity Framework Core with all the approaches. First, let us create the Entities required for our application.

### Order Entity:

Create a class file named Order.cs within the Entities folder and then copy and paste the following code. The following entity represents a customer’s order in the e-commerce application.

```csharp
using System.ComponentModel.DataAnnotations.Schema;
namespace EFCoreCodeFirstDemo.Entities
{
    public class Order
    {
        public int OrderId { get; set; } // Primary Key
        public DateTime OrderDate { get; set; }
        [Column(TypeName = "decimal(18,2)")]
        public decimal TotalAmount { get; set; }
        // Navigation Property - One Order has many OrderItems
        public ICollection<OrderItem> OrderItems { get; set; }
        // Navigation Property - One Order has one Payment
        public Payment Payment { get; set; }
    }
}

```

### OrderItem Entity:

Create a class file named OrderItem.cs within the Entities folder, and then copy and paste the following code. The following entity represents an individual item within an order.

```csharp
using System.ComponentModel.DataAnnotations.Schema;
namespace EFCoreCodeFirstDemo.Entities
{
    public class OrderItem
    {
        public int OrderItemId { get; set; } // Primary Key
        public int ProductId { get; set; } // Foreign Key to Product
        public int Quantity { get; set; }
        [Column(TypeName = "decimal(18,2)")]
        public decimal Price { get; set; }
        public int OrderId { get; set; } // Foreign Key to Order
        // Navigation Properties
        public Order Order { get; set; } 
        public Product Product { get; set; }
    }
}

```

### Product Entity:

Create a class file named Product.cs within the Entities folder and copy and paste the following code. The following entity represents the product inventory in the e-commerce system.

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
namespace EFCoreCodeFirstDemo.Entities
{
    public class Product
    {
        public int ProductId { get; set; } // Primary Key
        [MaxLength(100)]
        public string Name { get; set; }
        [Range(0, double.MaxValue)]
        [Column(TypeName = "decimal(18,2)")]
        public decimal Price { get; set; }
        [Range(0, int.MaxValue)]
        public int Quantity { get; set; }
        public string? Description { get; set; }
        public bool IsInStock { get; set; }
        // Navigation Property - One Product has many OrderItems
        public ICollection<OrderItem> OrderItems { get; set; }
        // Concurrency Token
        [Timestamp]
        public byte[] RowVersion { get; set; }
    }
}

```

### Payment Entity:

Create a class file named Payment.cs within the Entities folder and then copy and paste the following code. The following entity represents a payment transaction for an order.

```csharp
using System.ComponentModel.DataAnnotations.Schema;
namespace EFCoreCodeFirstDemo.Entities
{
    public class Payment
    {
        public int PaymentId { get; set; } // Primary Key
        public int OrderId { get; set; } // Foreign Key
        public DateTime PaymentDate { get; set; }
        [Column(TypeName = "decimal(18,2)")]
        public decimal Amount { get; set; }
        public PaymentStatus Status { get; set; } // Pending, Failed, Completed
        // Navigation Property - One Payment belongs to one Order
        public Order Order { get; set; }
    }
    public enum PaymentStatus
    {
        Pending,
        Failed,
        Completed
    }
}

```

### OrderLog Entity:

Create a class file named OrderLog.cs within the Entities folder, and then copy and paste the following code. The following entity represents a log entry for order-related activities, typically stored in a separate logging database.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class OrderLog
    {
        public int OrderLogId { get; set; } // Primary Key
        public int OrderId { get; set; } // Foreign Key
        public DateTime LogDate { get; set; }
        public string Message { get; set; }
    }
}

```

### DbContext Classes

To manage the entities and their interactions with the database, two separate DbContext classes are uses in our application.

### ECommerceDbContext

Manages the primary e-commerce entities such as Orders, Order Items, Products, and Payments. So, create a class file named ECommerceDbContext.cs within the Entities folder and copy and paste the following code.

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class ECommerceDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            // Configure the connection string to your ECommerceDB SQL Server Database
            optionsBuilder.UseSqlServer(@"Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV;Database=ECommerceDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        // Configures the model and mappings between entities and database
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // Configure enums to be stored as strings
            // For PaymentStatus enum
            modelBuilder.Entity<Payment>()
                .Property(c => c.Status)
                .HasConversion<string>()
                .IsRequired();    // Optional: Specify if the property is required
        }
        // DbSets for primary e-commerce entities
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderItem> OrderItems { get; set; }
        public DbSet<Product> Products { get; set; }
        public DbSet<Payment> Payments { get; set; }
    }
}

```

### LoggingDbContext

This context class manages logging entities such as OrderLog and typically connects to a separate logging database. So, create a class file named LoggingDbContext.cs within the Entities folder and then copy and paste the following code.

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class LoggingDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            // Configure the connection string to your Logging SQL Server Database
            optionsBuilder.UseSqlServer(@"Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV;Database=LoggingDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        // DbSet for logging entities
        public DbSet<OrderLog> OrderLogs { get; set; }
    }
}

```

### Generate Migration and Update the Databases:

Open the Package Manager Console and execute the Add-Migration and Update-Database commands as follows, but you should get one error.

EF Core uses DbContext classes to interact with the database. When multiple DbContext classes are present in a project, EF Core commands (like Add-Migration or Update-Database) need to know which context to target. Without specifying, EF Core cannot determine the correct context, leading to the error: More than one DbContext was found. Specify which one to use. Use the ‘-Context’ parameter for PowerShell commands and the ‘–context’ parameter for dotnet commands.

### How to Solve the above Error?

To solve the above error, we need to specify the DbContext to target using parameters in the commands. For example, when using the Package Manager Console in Visual Studio, you can specify the context with the -Context parameter. The syntax is given below:

- Add-Migration MigrationName -Context YourDbContextName
- Update-Database -Context YourDbContextName

So, let us proceed with Generating and Applying the migration for both of our DbContext classes. For ECommerceDbContext, please use Add-Migration InitialCreate -Context ECommerceDbContext and Update-Database -Context ECommerceDbContext commands in the Package Manager Console as shown in the below image:

For LoggingDbContext, please use Add-Migration InitialLogging -Context LoggingDbContext and Update-Database -Context LoggingDbContext commands in the Package Manager Console as shown in the below image:

Now, if you verify the database, then we should have the ECommerceDB database with the following tables:

Similarly, we should have the LoggingDB database created with the following tables:

### Insert Statements for the Products Table of the ECommerceDB database

To facilitate testing and demonstrate the functionality, please execute the following SQL INSERT statements to populate the Products table in the ECommerceDB database.

```csharp
-- Insert dummy products into the Products table
INSERT INTO Products (Name, Price, Quantity, Description, IsInStock)
VALUES 
('Laptop', 1500.00, 10, 'High-performance laptop suitable for all purposes.', 1),
('Smartphone', 800.00, 20, 'Latest model smartphone with advanced features.', 1),
('Tablet', 600.00, 15, 'Lightweight tablet with high-resolution display.', 1),
('Headphones', 200.00, 50, 'Noise-cancelling over-ear headphones.', 1),
('Monitor', 300.00, 25, '24-inch full HD monitor with vibrant colors.', 1);

```

### Implicit Transactions with SaveChanges() in EF Core

By default, EF Core wraps all changes made in SaveChanges() within a transaction. If any operation within SaveChanges() fails, EF Core automatically rolls back the entire transaction, ensuring no partial changes persist. Let us place an Order Using EF Core Implicit Transaction. So, modify the Program class as follows:

```csharp
using EFCoreCodeFirstDemo.Entities;
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo
{
    public class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Initialize the DbContext for interacting with the ECommerce database
                using var context = new ECommerceDbContext();
                Console.WriteLine("Creating an Order");
                // 1. Create a new order with multiple order items and an initial payment
                var order = new Order
                {
                    // Set the order date to the current UTC time
                    OrderDate = DateTime.UtcNow,
                    // Set the total amount for the order
                    TotalAmount = 250.00m,
                    // Define the order items associated with this order
                    OrderItems = new List<OrderItem>
                    {
                        // First item in the order
                        new OrderItem
                        {
                            ProductId = 1, // Refers to the product with ID 1
                            Quantity = 2,  // 2 units ordered
                            Price = 100.00m // Price per unit
                        },
                        // Second item in the order
                        new OrderItem
                        {
                            ProductId = 2, // Refers to the product with ID 2
                            Quantity = 1,  // 1 unit ordered
                            Price = 50.00m // Price per unit
                        }
                    },
                    // Define the payment details associated with the order
                    Payment = new Payment
                    {
                        PaymentDate = DateTime.UtcNow, // Set the payment date as the current UTC time
                        Amount = 250.00m, // Payment amount matches the total order amount
                        S
```

### Explanation:

When SaveChanges() is called, EF Core starts a transaction. It inserts the Order and associated OrderItem records. EF Core automatically rolls back the transaction if any operation fails (e.g., a constraint violation), ensuring that no partial data is saved. This approach is simple, straightforward, and suitable for simple scenarios where all operations are within a single SaveChanges() call. When you run the above code, you will get the following output:

### Manual Transactions using Database.BeginTransaction() in EF Core

For scenarios requiring more control over the transaction boundaries, such as multiple SaveChanges() calls within a single transaction, EF Core allows manual transaction management using the Database.BeginTransaction() method.

Let us understand this with an example. Let us place an Order, with Product Quantity Update and Payment Processing. So, we will do the following:

- Creating an order and order items.
- Updating Product Quantity for the ordered products.
- Processing the payment.

Each of these operations involves separate SaveChanges() calls but needs to be part of a single transaction. For a better understanding, please modify the Program class as follows:

```csharp
using EFCoreCodeFirstDemo.Entities;
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo
{
    public class Program
    {
        static async Task Main(string[] args)
        {
            // Initialize the DbContext for interacting with the ECommerce database
            using var context = new ECommerceDbContext();
            // Begin a manual transaction using the context
            using var transaction = await context.Database.BeginTransactionAsync();
            Console.WriteLine("Transaction started...");
            try
            {
                // 1. Create a new order with order items and initial payment status (Pending)
                var order = new Order
                {
                    OrderDate = DateTime.UtcNow, // Set the current UTC time for the order date
                    TotalAmount = 150.00m, // Set the total amount of the order
                    // Define the items in the order (in this case, one item)
                    OrderItems = new List<OrderItem>
                    {
                        new OrderItem
                        {
                            ProductId = 1, // The ProductId of the item being ordered
                            Quantity = 1, // Number of units ordered
                            Price = 150.00m // Price per unit
                        }
                    },
                    // Define the payment details associated with the order
                    Payment = new Payment
                    {
                        PaymentDate = DateTime.UtcNow, // Set the payment date as the current UTC time
                        Amount = 150.00m, // Set the payment amount to match the order total
                        Status = PaymentStatus.Pending // Set the initial payment status to 'Pending'
                    }
                };
                // Add the new order to the Orders DbSet in the context
                context.Orders.Add(order);
                Console.WriteLi
```

### Explanation:

- **Begin Transaction:** The transaction is started using BeginTransaction().
- **Multiple Operations:** Multiple SaveChanges() calls are made within the transaction.
- Create Order and OrderItem.
- Update Inventory.
- Process Payment.
- **Commit/Rollback:** If all operations succeed, transaction.Commit() is called to commit the transaction. If any operation fails, transaction.Rollback() is invoked to undo all changes.

This approach allows grouping multiple operations into a single transactional unit, ensuring that all operations succeed or fail. So, when you run the above code, you will get the following output:

### Distributed Transactions with TransactionScope in Entity Framework Core

When operations span multiple DbContext instances or different databases, TransactionScope can manage distributed transactions. This ensures that all participating operations across different contexts or resources are committed or rolled back together. Distributed transactions involve more overhead and should be used only when necessary.

Let us understand this with an example. When placing an order, we also need to log the activity in a separate logging database. Both operations need to be part of a single transaction. For a better understanding, please modify the Program class as follows:

```csharp
using EFCoreCodeFirstDemo.Entities;
using Microsoft.EntityFrameworkCore;
using System.Transactions;
namespace EFCoreCodeFirstDemo
{
    public class Program
    {
        static void Main(string[] args)
        {
            // Enable implicit distributed transactions in case operations span multiple databases
            TransactionManager.ImplicitDistributedTransactions = true;
            // Define transaction options: Isolation level (ReadCommitted) and timeout duration (default 1 minute)
            var transactionOptions = new TransactionOptions
            {
                IsolationLevel = IsolationLevel.ReadCommitted, // Ensures data read is committed, avoiding dirty reads
                Timeout = TransactionManager.DefaultTimeout // Default transaction timeout
            };
            // Start a TransactionScope to encompass operations across different DbContexts
            using (var scope = new TransactionScope(
                TransactionScopeOption.Required, // Requires a new transaction or joins an existing one
                transactionOptions,
                TransactionScopeAsyncFlowOption.Enabled)) // Enables async operations within the transaction
            {
                try
                {
                    int generatedOrderId; // Variable to hold the generated OrderId for logging purposes
                    // 1. Perform operations using ECommerceDbContext to handle order-related activities
                    using (var orderContext = new ECommerceDbContext())
                    {
                        // Create a new order with associated OrderItems and Payment details
                        var order = new Order
                        {
                            OrderDate = DateTime.UtcNow, // Set the order date to the current UTC time
                            TotalAmount = 300.00m, // Set the total amount for the order
                            // Create a list of order items for the order
                      
```

### Explanation:

- **TransactionScope:** Encapsulates a block of code in a transaction.
- **Multiple DbContexts:** Operations are performed across two different DbContext instances (ECommerceDbContext and LoggingDbContext) connected to different databases.
- **Atomicity:** If any operation within the TransactionScope fails, all changes across both contexts are rolled back.
- **scope.Complete():** Must be called to commit the transaction. If not called, the transaction is rolled back upon disposal.

Now, run the above code, you should get the following output:

### Points to Remember:

- **TransactionManager.ImplicitDistributedTransactions:** Setting TransactionManager.ImplicitDistributedTransactions to true allows distributed transactions to be automatically managed if the transaction involves multiple resource managers (like different databases).
- **IsolationLevel.ReadCommitted:** Ensures that the transaction does not read data that has been modified but has not yet been committed by other transactions. This prevents scenarios like dirty reads, where uncommitted data is read.
- **Timeout:** Specifies the maximum time the transaction is allowed to run before it is automatically aborted. The default is typically sufficient, but it can be adjusted based on the application’s performance requirements.
- **TransactionScopeOption.Required:** Indicates that the code block should participate in a transaction. If an existing transaction is present, it joins that transaction; otherwise, it creates a new one.
- **TransactionScopeAsyncFlowOption.Enabled:** Allows the transaction to flow correctly across asynchronous method calls, which is crucial for modern applications that rely heavily on async/await patterns.

### Asynchronous Transactions in Entity Framework Core

Asynchronous transactions are essential for applications that require non-blocking operations, such as web applications handling multiple concurrent requests. EF Core supports asynchronous transaction management, handling transactions without blocking the executing thread.