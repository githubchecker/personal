# 53. Entity Framework Core Database First Approach

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# Entity Framework Core Database First Approach

In this article, I will discuss the Entity Framework Core (EF Core) Database First Approach with Examples. Please read our previous article discussing [Global Query Filters in Entity Framework Core](https://dotnettutorials.net/lesson/global-query-filters-in-entity-framework-core/) with Examples.

### Entity Framework Core Database First Approach

The Database First approach in Entity Framework Core (EF Core) is a methodology where the data access layer (comprising models and a DbContext class) is generated from an existing database. This strategy is particularly useful when integrating EF Core with a pre-existing database or when database schema design is managed by a database administrator or an external team. So, this approach is particularly useful in the following scenarios:

- **Working with an existing database:** When the database already exists and is managed by database administrators or external teams.
- **Database-centric development:** When the database schema design is finalized before the application development begins.

With the Database First approach, EF Core will generate the necessary models, relationships, and DbContext class based on the structure of the database, enabling developers to access the database and perform database CRUD operations. This is often used in scenarios where the database schema has already been defined, and you want to avoid manually creating models and contexts.

### Entity Framework Core Database First Approach with an E-commerce Application

Let us understand how to use the Entity Framework Core (EF Core) Database First approach step by step with an existing E-commerce database. This example will cover:

- **Creating the Database Schema:** Designing the tables and their relationships.
- **Scaffolding the DbContext:** Generating the DbContext and model classes from the database.
- **Performing CRUD Operations:** Creating, reading, updating, and deleting data.
- **Utilizing Views, Stored Procedures, and Functions:** Enhancing data operations with SQL Server features.

### Key Entities in the E-commerce Database

The E-commerce database will manage several key entities essential for an online shopping platform. The key tables and their purposes are:

- **Customers:** Stores personal information of customers.
- **Addresses:** Holds multiple addresses associated with each customer.
- **Categories:** Organizes products into various classifications.
- **Products:** Contains detailed information about each product.
- **Orders:** Records customer orders.
- **OrderItems:** Lists the products included in each order.
- **Payments:** Tracks payment details for orders.

### SQL Scripts for Database Creation

Let’s start by creating the EcommerceDB database and all necessary tables with proper relationships, views, stored procedures, and functions. So, please execute the following SQL script in SQL Server Management Studio (SSMS).

```sql
CREATE DATABASE EcommerceDB;
GO
USE EcommerceDB;
GO
-- Create Customers Table
-- Holds customer details like name, email, phone, and date of birth.
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Phone NVARCHAR(20),
    DateOfBirth DATE,
    CreatedDate DATETIME DEFAULT GETDATE()
);
GO
-- Create Addresses Table
-- Stores multiple addresses per customer, including whether an address is the default.
CREATE TABLE Addresses (
    AddressID INT PRIMARY KEY IDENTITY,
    CustomerID INT NOT NULL,
    AddressLine1 NVARCHAR(100) NOT NULL,
    AddressLine2 NVARCHAR(100),
    City NVARCHAR(50) NOT NULL,
    State NVARCHAR(50) NOT NULL,
    PostalCode NVARCHAR(20) NOT NULL,
    Country NVARCHAR(50) NOT NULL,
    IsDefault BIT DEFAULT 0,
    CreatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
GO
-- Create Categories Table
-- Organizes products into categories, supporting hierarchical relationships with ParentCategoryID.
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY IDENTITY,
    CategoryName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    ParentCategoryID INT NULL,
    CreatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (ParentCategoryID) REFERENCES Categories(CategoryID)
);
GO
-- Create Products Table
-- Contains product information, pricing, stock levels, and category association.
CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY,
    ProductName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    Price DECIMAL(18, 2) NOT NULL,
    CategoryID INT NOT NULL,
    StockQuantity INT NOT NULL,
    CreatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);
GO
-- Create Orders Table
-- Records each order's details, including the customer, shipping address, total amount, and status.
CREATE TABLE Orders (
    
```

Once you execute the above SQL Script, the database with the required database objects is created, as shown in the below image:

### Creating a New Console Application:

We can use the EF Core Database First Approach with any type of Dot Net Core Application, including ASP.NET Core MVC, ASP.NET Core Web API, Console Application, etc. So, let us create a new Console Application named ECommerceApp.

Once you create the Console Application, we need to add the Microsoft.EntityFrameworkCore.SqlServer (EF Core provider for SQL Server) and Microsoft.EntityFrameworkCore.Tools (Tools for EF Core, including the Scaffold-DbContext command) packages. Please execute the following commands in the Package Manager Console to install these two packages.

- Install-Package Microsoft.EntityFrameworkCore.SqlServer
- Install-Package Microsoft.EntityFrameworkCore.Tools

### Implementing EF Core Database First Approach

Now, we will see how to create the Context and Entity classes from our existing EcommerceDB database using the Entity Framework Core Database First Approach. Creating Context and Entity classes for an existing database is called Database-First Approach.

Entity Framework Core does not support Visual Designer for DB model and wizard to create entity and context classes similar to Entity Framework 6. So, we need to use the Scaffold-DbContext command, which is also called Reverse Engineering.

The Scaffold-DbContext command creates entities and context classes based on the schema of the existing database. We need to do this using Package Manager Console (PMC) tools.

### Scaffolding the Database in EF Core

Scaffolding is the process of generating the DbContext and entity classes based on the existing database schema. Let us first understand the syntax of the Scaffold-DbContext

Syntax: Scaffold-DbContext “Connection String” Microsoft.EntityFrameworkCore.SqlServer -o Models -f

### Parameters:

- **Connection String:** Specifies how to connect to the database.
- **Microsoft.EntityFrameworkCore.SqlServer:** Specifies the EF Core provider.
- **-o Models:** Output directory for the generated classes.
- **-f:** Forces scaffolding by overwriting existing files.

### Example: Connecting to SQL Server EcommerceDB database

Scaffold-Dbcontext “Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV; Database=EcommerceDB; Trusted_Connection=True; TrustServerCertificate=True;” Microsoft.EntityFrameworkCore.SqlServer -O Models -f

So, open the Package Manager Console and execute the following command to create the entities and context class based on the EcommerceDB database:

Once you execute the above command, it should create the Models folder. It should have created the DbContext class and the required entities inside that folder, as shown in the image below.

Here, you can see that entities are created for all database tables and views, and the EcommerceDbContext class manages the database operations using these entities.

### Performing CRUD Operations using EF Core DB First Approach

Now, let us Proceed and see how we can perform database CRUD Operations using the Entity Framework Core Database First Approach. Later, I will show how to use Views, Stored Procedures, and Stored Functions.

### Adding Data

Let us see how to add new categories, products, customers, addresses, orders, order items, and payments. To better understand, please modify the Program class as follows. The following example code is self-explained, so please read the comment lines.

```csharp
using ECommerceApp.Models;
using Microsoft.EntityFrameworkCore;
namespace ECommerceApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            using var context = new EcommerceDbContext();
            var dbTransction = context.Database.BeginTransaction();
            try
            {
                // *** Create Operations ***
                // Adding Categories
                Console.WriteLine("Adding new categories...");
                // Create a new 'Electronics' category
                var electronicsCategory = new Category
                {
                    CategoryName = "Electronics",
                    Description = "Electronic devices and gadgets",
                    CreatedDate = DateTime.Now
                };
                context.Categories.Add(electronicsCategory);
                // Create a new 'Clothing' category
                var clothingCategory = new Category
                {
                    CategoryName = "Clothing",
                    Description = "Men's and Women's Clothing",
                    CreatedDate = DateTime.Now
                };
                context.Categories.Add(clothingCategory);
                // Save categories to the database
                context.SaveChanges();
                Console.WriteLine("Categories 'Electronics' and 'Clothing' added successfully.\n");
                // Adding Products
                Console.WriteLine("Adding new products...");
                // Create a new product 'Smartphone' under 'Electronics' category
                var product1 = new Product
                {
                    ProductName = "Smartphone",
                    Description = "Latest model smartphone",
                    Price = 699.99M,
                    StockQuantity = 50,
                    CategoryId = electronicsCategory.CategoryId,
                    CreatedDate = DateTime.Now
                };
                context.Products.Add(product1)
```

### Output:

### Reading Data:

Let us retrieve and display orders with the customer, order item, and payment details. To better understand, please modify the Program class as follows. The following example code is self-explained, so please read the comment lines.

```csharp
using ECommerceApp.Models;
using Microsoft.EntityFrameworkCore;
namespace EcommerceApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            try
            {
                // Create an instance of the DbContext to interact with the database
                using var context = new EcommerceDbContext();
                // *** Retrieve and Display Orders with Details ***
                Console.WriteLine("Fetching and displaying all orders with customer, order items, and payment details...\n");
                // Fetch orders including related data:
                var orders = context.Orders
                    .Include(o => o.Customer) // Include customer information
                    .Include(o => o.OrderItems) // Include order items
                        .ThenInclude(oi => oi.Product) // Include product details for each order item
                    .Include(o => o.Payments) // Include payments associated with the order
                    .Include(o => o.ShippingAddress) // Include shipping address
                    .ToList();
                // Check if any orders exist
                if (orders.Any())
                {
                    // Iterate through each order
                    foreach (var order in orders)
                    {
                        // Display basic order information
                        Console.WriteLine($"Order ID: {order.OrderId}, Date: {order.OrderDate}, Status: {order.Status}, Total Amount: {order.TotalAmount}");
                        // Display customer information
                        Console.WriteLine($"Customer: {order.Customer.FirstName} {order.Customer.LastName}");
                        Console.WriteLine($"Email: {order.Customer.Email}");
                        Console.WriteLine($"Phone: {order.Customer.Phone}");
                        // Display shipping address
                        var address = order.ShippingAddress;
                        Conso
```

### Output:

### Updating Data

Let us update the status of an order and payment and adjust the stock quantities of the products in the order. To better understand, please modify the Program class as follows. The following example code is self-explained, so please read the comment lines.

```csharp
using ECommerceApp.Models;
using Microsoft.EntityFrameworkCore;
namespace EcommerceApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            using var context = new EcommerceDbContext();
            var dbTransaction = context.Database.BeginTransaction();
            try
            {
                // *** Update Order Status, Payment Status, and Adjust Stock Quantities ***
                // Specify the Order ID that you want to update
                int orderIdToUpdate = 1; // Change this to the actual Order ID
                Console.WriteLine($"Updating Order ID: {orderIdToUpdate}\n");
                // Retrieve the order including related entities:
                // - Include Order Items and their associated Products
                // - Include Payments associated with the order
                var order = context.Orders
                    .Include(o => o.OrderItems)
                        .ThenInclude(oi => oi.Product)
                    .Include(o => o.Payments)
                    .FirstOrDefault(o => o.OrderId == orderIdToUpdate);
                // Check if the order exists
                if (order != null)
                {
                    // Update payment status if payment exists
                    //var payment = order.Payments.FirstOrDefault();
                    foreach (var payment in order.Payments)
                    {
                        // Display current payment status
                        Console.WriteLine($"Current Payment Status: {payment.Status}");
                        // Update the payment status to 'Completed'
                        payment.Status = "Completed";
                        // Display updated payment status
                        Console.WriteLine($"Updated Payment Status: {payment.Status}\n");
                    }
                    //Updating Order Status
                    // Display current order status
                    Console.WriteLine($"Cu
```

### Output:

### Deleting Data

Let us delete an order and the associated Order Items and payments. To better understand, please modify the Program class as follows. The following example code is self-explained, so please read the comment lines.

```csharp
using ECommerceApp.Models;
using Microsoft.EntityFrameworkCore;
namespace EcommerceApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            try
            {
                using var context = new EcommerceDbContext();
                // *** Delete an Order and Associated Order Items and Payments ***
                // Specify the Order ID that you want to delete
                int orderIdToDelete = 1; // Change this to the actual Order ID you want to delete
                Console.WriteLine($"Attempting to delete Order ID: {orderIdToDelete}\n");
                // Retrieve the order including related entities:
                // - Include Order Items
                // - Include Payments
                var order = context.Orders
                    .Include(o => o.OrderItems)
                    .Include(o => o.Payments)
                    .FirstOrDefault(o => o.OrderId == orderIdToDelete);
                // Check if the order exists
                if (order != null)
                {
                    // Display order details
                    Console.WriteLine("Order Details:");
                    Console.WriteLine($"Order ID: {order.OrderId}, Date: {order.OrderDate}, Status: {order.Status},Total Amount: {order.TotalAmount}\n");
                    // Display associated order items
                    Console.WriteLine("Associated Order Items:");
                    foreach (var orderItem in order.OrderItems)
                    {
                        Console.WriteLine($"\tOrder Item ID: {orderItem.OrderItemId}, Product ID: {orderItem.ProductId}, Quantity: {orderItem.Quantity}, Total Price: {orderItem.TotalPrice}");
                    }
                    // Display associated payments
                    Console.WriteLine("\nAssociated Payments:");
                    foreach (var payment in order.Payments)
                    {
                        Console.WriteLine($"\tPayment ID: {payment.Pay
```

### Output:

### Stored Function using EF Core:

Even though we are using a Database-First approach, we need to manually define the function in our DbContext class, as EF Core does not automatically import functions through the scaffolding process. So, add the following method in EcommerceDbContext that represents the scalar function. Use the DbFunction attribute to link it to the SQL function.

```csharp
// Define the stored function
[DbFunction("CalculateDiscount", "dbo")]
public static decimal? CalculateDiscount(decimal? totalAmount)
{
    // This method is for EF Core to know how to call the function.
    throw new NotImplementedException();
}

```

Once you have defined the function in the EcommerceDbContext class, you can call it like any other static method in your code.

### Using Views, Stored Procedures, and Functions in EF Core DB First Approach:

Please modify the Program class as follows: Here, I am showing how to use Stored procedures and views with Entity Framework Core Database First Approach using the FromSqlRaw method. At the same time, we can call the CalculateDiscount method, which will execute the CalculateDiscount function. The following code is self-explained, so please read the comment lines for a better understanding.

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Data.SqlClient;
using ECommerceApp.Models;
namespace EcommerceApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            // Create an instance of the DbContext
            using var context = new EcommerceDbContext();
            var dbTransaction = context.Database.BeginTransaction();
            try
            {
                // *** Step 1: Create a New Order with Discount Applied ***
                Console.WriteLine("Creating a new order with discount applied...\n");
                // Define the existing CustomerID and ProductID
                int existingCustomerId = 1; // Replace with actual CustomerID
                int existingProductId = 1;   // Replace with actual ProductID
                // Retrieve the existing customer and product from the database
                var customer = context.Customers.FirstOrDefault(c => c.CustomerId == existingCustomerId);
                var product1 = context.Products.FirstOrDefault(p => p.ProductId == existingProductId);
                var product2 = context.Products.FirstOrDefault(p => p.ProductId == 2);
                if (customer == null || product1 == null || product2 == null)
                {
                    Console.WriteLine("Customer or Product not found. Cannot proceed with order creation.");
                    return;
                }
                // Retrieve the customer's default shipping address
                var shippingAddress = context.Addresses
                    .FirstOrDefault(a => a.CustomerId == customer.CustomerId && a.IsDefault == true);
                if (shippingAddress == null)
                {
                    Console.WriteLine("Shipping address not found for the customer.");
                    return;
                }
                // Create a new order for the customer
                var newOrder = new Order
                {
                    CustomerId = custo
```

We have successfully implemented how to use the EF Core Database First approach with an E-commerce database. We generated the required models by reverse-engineering the existing database and performing CRUD operations. Additionally, we use database views, stored procedures, and functions within our application.

Note: If the database schema changes, the models and DbContext will need to be updated using the scaffold command with the -Force option to regenerate the models, which will overwrite any customizations.