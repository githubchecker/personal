# 29. One-to-Many Relationships in Entity Framework Core

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# One-to-Many Relationships in Entity Framework Core

In this article, I will discuss How to Configure One-to-Many Relationships between two Entities in Entity Framework Core with Examples. Please read our previous article discussing [How to Configure One-to-One Relationships between two entities in EF Core](https://dotnettutorials.net/lesson/one-to-one-relationships-in-entity-framework-core/) with Examples.

### What is the One-to-Many Relationship in Entity Framework Core?

A One-to-Many relationship in Entity Framework Core represents a scenario where one entity (the principal) is associated with zero or many instances of another entity (the dependent). This type of relationship is useful when one record in a table is linked to multiple records in another table.

For example, consider an application that manages Orders and their corresponding Order Items. Each Order can have multiple Order Items, but each Order Item belongs to only one Order. This is a classic One-to-Many relationship example in our real-time e-commerce application.

Consider another real-time example: an application that manages departments and employees within a company. Each Department can have multiple Employees, but each Employee belongs to only one Department. This is another example of a One-to-Many relationship.

### Guidelines to Implement One-to-Many Relationships in Entity Framework Core

The following are the key guidelines for implementing One-to-Many relationships in Entity Framework Core:

- **Principal and Dependent Entities:** In a One-to-Many relationship, the principal entity is the “one” side, and the dependent entity is the “many” side, i.e., One Principal Entity can have multiple Dependent Entities. So, first, you need to determine which entity is the principal (e.g., Department, Order) and which is the dependent entity (e.g., Employee, OrderItem).
- **Foreign Key Constraints:** The dependent entity contains the foreign key referencing the principal entity.
- **Optional vs. Required Relationship:** Define whether the relationship is optional or required. The dependent entity can exist without the principal entity if it’s optional. For example, an Employee might be required to belong to a Department, or it might be optional.
- **Navigation Properties:** The Principal Entity will contain a collection navigation property pointing to the Dependent entity. The dependent entity will have one reference navigation property pointing to the Principal entity.
- **Database Schema:** In the database, One-to-Many relationships are represented by placing a foreign key constraint in the dependent table pointing to the principal table.

### Real-Time Example to Understand One-to-Many Relationships in EF Core

Let’s consider an example of Order and OrderItem entities to demonstrate how to implement One-to-Many relationships in Entity Framework Core. I will show you three approaches to implementing One-to-Many Relationships in EF Core. They are as follows:

- Implementing One-to-Many Relationships without Data Annotations or Fluent API
- Implementing One-to-Many Relationships with Data Annotations
- Implementing One-to-Many Relationships with Fluent API

## Implementing One-to-Many Relationships Without Data Annotations or Fluent API

EF Core can sometimes manage relationships automatically without any explicit configuration. However, if we don’t use data annotations or Fluent API, EF Core will attempt to create the default relationships based on naming conventions. Let’s understand how to implement the One-to-Many relationship with default EF Core conventions.

### Creating Entities:

We want to establish a One-to-Many relationship between Order and OrderItem entities.

### Order Entity

Create a class file named Order.cs within the Entities folder with the following code. This will be our principal entity.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Order
    {
        public int Id { get; set; }
        public DateTime OrderDate { get; set; }
        public string OrderNumber { get; set; }
        public List<OrderItem> OrderItems { get; set; } // Navigation property
    }
}

```

### OrderItem Entity

Next, create a class file named OrderItem.cs within the Entities folder. This will be our dependent entity.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class OrderItem
    {
        public int Id { get; set; }
        public string ProductName { get; set; }
        public int OrderId { get; set; } // FK, Required Relationship
        public Order Order { get; set; } // Navigation property
    }
}

```

### With Default Convention:

- EF Core can detect the One-to-Many relationship based on the presence of navigation properties and foreign key properties.
- The OrderItem entity has a foreign key OrderId and a navigation property Order.
- The Order entity has a navigation property, OrderItems, to represent the multiple items associated with an order.

### DbContext Class:

Next, modify the EFCoreDbContext class as follows. Here, we add both Order and OrderItem as DbSet properties so that EF Core can generate the required database tables with a One-to-Many relationship.

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class EFCoreDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseSqlServer(@"Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV;Database=OrderDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderItem> OrderItems { get; set; }
    }
}

```

### Generating the Migration:

After the changes, run the following commands in the Package Manager Console:

- Add-Migration CreateOrderTables
- Update-Database

Once you execute the above commands, the database should be created with the required Orders and OrderItems tables with a One-to-Many relationship. In the OrderItems table, the OrderId column is created as a foreign key pointing to the Orders table’s primary key column, as shown in the image below.

As you can see, it creates a Non-Unique and Non-Clustered Index in the Foreign Key OrderId column. That means this column can hold duplicate values, i.e., we can have the same OrderId for multiple OrderItems, i.e., One OrderId can have multiple OrderItems. This is how it implements One-to-Many Relationships between Order and OrderItem entities.

### Limitations:

- Without explicit configuration, EF Core relies on conventions that might not always align with your intended schema.
- It’s recommended to use Data Annotations or Fluent API for clarity and to ensure the relationship is correctly established.

## Implementing One-to-Many Relationships Using Data Annotation Attributes in EF Core

We can use Data Annotation Attributes to define One-to-Many relationships explicitly between two entities in Entity Framework Core.

### Entities with Data Annotations:

First, modify the Order.cs file as follows:

```csharp
using System.ComponentModel.DataAnnotations;
namespace EFCoreCodeFirstDemo.Entities
{
    public class Order
    {
        [Key]
        public int Id { get; set; } // Primary Key
        public DateTime OrderDate { get; set; }
        public string OrderNumber { get; set; }
        public List<OrderItem> OrderItems { get; set; } // Navigation property
    }
}

```

Next, modify the OrderItem.cs file as follows:

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
namespace EFCoreCodeFirstDemo.Entities
{
    public class OrderItem
    {
        [Key]
        public int Id { get; set; }
        public string ProductName { get; set; }
        [ForeignKey("OrderId")]
        public int OrderId { get; set; } // FK, Required Relationship
        public Order Order { get; set; } // Navigation property
    }
}

```

### Explanation:

- The [Key] attribute marks the primary key for each entity.
- The [ForeignKey(“OrderId”)] attribute in the OrderItem entity explicitly declares OrderId as a foreign key.

This configuration ensures that each OrderItem is linked to exactly one Order, and one Order can have many OrderItems, enforcing a One-to-Many relationship between them.

### Generating Migration:

With the above changes, open the Package Manager Console and execute the Add-Migration and Update-Database commands. Once the commands are executed, please verify the database. The Orders and OrderItems tables with the correct One-to-Many relationship, as shown in the image below.

Note: The [ForeignKey] attribute can be applied either to the foreign key property (OrderId) or to the navigation property (Order). Applying it to the foreign key property is more explicit.

## Implementing One-to-Many Relationships in EF Core Using Fluent API

The Fluent API provides a more expressive way to configure the model within the OnModelCreating method of the DbContext class. This is the recommended approach for complex configurations. First, modify the entities by removing the [Key] and [ForeignKey] attributes from the model properties:

### Order.cs

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Order
    {
        public int Id { get; set; } // Primary Key
        public DateTime OrderDate { get; set; }
        public string OrderNumber { get; set; }
        public List<OrderItem> OrderItems { get; set; } // Navigation property
    }
}

```

### OrderItem.cs

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class OrderItem
    {
        public int Id { get; set; }
        public string ProductName { get; set; }
        public int OrderId { get; set; } // FK, Required Relationship
        public Order Order { get; set; } // Navigation property
    }
}

```

### DbContext Configuration:

We need to configure the One-to-Many relationship between Order and OrderItem using Fluent API by overriding the OnModelCreating method of the DbContext class. So, please modify the EFCoreDbContext class as follows:

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class EFCoreDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseSqlServer(@"Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV;Database=OrderDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Order>() //Refers to the Order entity.
                .HasMany(o => o.OrderItems) // Order has many OrderItems
                .WithOne(oi => oi.Order)    // Each OrderItem has one Order
                .HasForeignKey(oi => oi.OrderId); // OrderId is the FK in OrderItem
        }
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderItem> OrderItems { get; set; }
    }
}

```

This configuration clearly defines how an Order can have multiple Order Items, each associated with one Order.

### Migration and Database Update:

After setting up the entities and DbContext, open the Package Manager Console and execute the Add-Migration and Update-Database commands. Once the commands are executed, verify the database to ensure the schema reflects the One-to-Many relationship between Order and OrderItem.

### How Do We Configure Cascade Delete using EF Core for One-to-Many Relationships?

In Entity Framework Core (EF Core), the OnDelete method configures the delete behavior for related entities when the principal entity is deleted. This behavior is commonly referred to as cascading actions. When defining relationships between entities, particularly foreign key relationships, it’s important to determine what should happen when a referenced entity (the principal) is deleted. The OnDelete method allows you to specify this behavior.

### Modify the EFCoreDbContext:

For example, if an Order is deleted from the Orders table, then automatically, we need to delete all the related OrderItems belonging to that Order from the OrderItems table. To implement this, we need to use the OnDelete Fluent API method and set the DeleteBehavior to Cascade. So, please modify the EFCoreDbContext class as follows. Here, you can see we are using the OnDelete method; to this method, we are passing the DeleteBehavior.Cascade enum named constant.

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class EFCoreDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            // Configuring the Connection String
            optionsBuilder.UseSqlServer(@"Server=LAPTOP-6P5NK25R\SQLSERVER2022DEV;Database=OrderDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // Fluent API Configuration
            // Configure One to Many Relationships Between Order and OrderItem
            modelBuilder.Entity<Order>()
            .HasMany(o => o.OrderItems) // Order has many OrderItems, specifies the 'many' side of the relationship
            .WithOne(oi => oi.Order)    // OrderItem is associated with one Order, specifies the 'one' side of the relationship
            .HasForeignKey(oi => oi.OrderId) // OrderId is the Foreign key in OrderItem table, specifies the foreign key
            .OnDelete(DeleteBehavior.Cascade); // This will delete the child record(s) when parent record is deleted
        }
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderItem> OrderItems { get; set; }
    }
}

```

### Understanding the DeleteBehavior

The OnDelete method uses the DeleteBehavior parameter, which determines how a delete operation affects dependent entities when the principal is deleted. If you go to the definition of DeleteBehavior, you will see it is an enum with the following values.

The DeleteBehavior enum has the following values:

### Cascade:

- When the principal entity (Order) is deleted, all related dependent entities (e.g., related OrderItems) will also be deleted.
- This behavior is enforced at both the database and EF Core levels. It ensures that child records cannot exist without the parent record.
- The database applies a cascading delete constraint, so when a parent is deleted, all dependents are also removed automatically.

### ClientSetNull:

- When the principal entity is deleted, the foreign key value in the dependent entities (e.g., OrderId in OrderItem) is set to null, but this change happens only in EF Core’s in-memory context before saving to the database.
- If the foreign key property in the dependent entity is non-nullable, an exception will be thrown during SaveChanges() because EF Core cannot set the foreign key to null.

### Restrict:

- This prevents the principal entity from being deleted if any related dependent entities exist.
- It helps prevent accidental data loss by ensuring that parent entities cannot be deleted when dependents are present.
- This behavior is enforced both in EF Core and the database. If you try to delete a parent entity with existing dependents, EF Core will throw an exception.

### SetNull:

- When the principal entity is deleted, the foreign key value in the dependent entities (e.g., OrderId in OrderItem) is set to null.
- This behavior is enforced both at the database level and in EF Core. When deleting the parent, the foreign key columns in the dependent entities are updated to null, and this occurs directly in the database.
- Unlike ClientSetNull, which only affects in-memory entities, SetNull operates on persisted data in the database.

### ClientCascade:

- This is similar to Cascade, but the cascading delete happens only on the client side (EF Core context), meaning that the dependent entities are deleted in memory when the principal entity is deleted.