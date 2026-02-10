# 33. Entity Configurations using Entity Framework Core Fluent API

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# Entity Configurations using Entity Framework Core Fluent API

In this article, I will discuss How to Implement Entity Configurations using Entity Framework Core (EF Core) Fluent API with Examples. Please read our previous article discussing [Global Configurations in Entity Framework Core using Fluent API](https://dotnettutorials.net/lesson/global-configurations-in-entity-framework-core-using-fluent-api/) with Examples.

### Entity Configurations in Entity Framework Core using Fluent API

In Entity Framework (EF) Core, Entity Configurations allow us to define settings and rules specific to individual entities. This includes mapping domain entities to database tables, specifying primary keys (including composite keys), configuring relationships between entities, and setting up indexes and constraints. By explicitly configuring entities using the Fluent API, we ensure that the database schema aligns precisely with our application’s requirements, promoting consistency and maintainability.

Entity configurations are particularly useful in the following scenarios:

- When default conventions are insufficient or inappropriate.
- When we need full control over table mapping, relationships, or constraints.
- When working with existing databases and maintaining consistency between domain models and database schema.

Let us proceed and see some real-time examples to understand how and when to apply entity-level configurations using Entity Framework Core Fluent API in a .NET console application. We will cover the following Entity Configurations:

- Configuring Table Names and Schema
- Configuring Primary Keys
- Configuring Composite Primary Keys
- Configuring Indexes
- Configuring Relationships (One-to-One, One-to-Many, Many-to-Many).
- Configuring Cascade Delete Behavior for Specific Relationships
- Ignoring Entities
- Configuring Alternate Keys (Unique Constraints)
- Configuring Owned Entities

### Configuring Table Names and Schema

By default, EF Core maps each entity to a database table with the same name as the entity’s class name or the DbSet property name. However, sometimes, we need to specify a different table name or schema to align with existing database conventions or organizational standards.

This configuration allows for better organization and adherence to naming conventions. For example, to map a Customer entity to a table called tblCustomer in the Admin schema, we configure it as follows. We need to configure the same by overriding the OnModelCreating method of the DbContext class.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .ToTable("tblCustomer", schema: "Admin");
}

```

### Code Explanations:

- **ToTable(“tblCustomer”, schema:** “Admin”): Specifies that the Customer entity should be mapped to a table named tblCustomer within the Admin schema.
- **Schema Organization:** Using different schemas (e.g., Admin, Sales) helps organize tables logically within the database.
- **Provider Support:** Ensure that your database provider supports schemas (e.g., SQL Server does, while some others may not).

### Configuring Primary Key

Every entity requires a primary key to identify each record uniquely. EF Core follows conventions to automatically detect primary keys, typically properties named Id or Id. If your entity uses a different property as the primary key or if you need to configure composite keys, explicit configuration is necessary. For example, we can set CustomerId as the primary key for the Customer entity as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .HasKey(c => c.CustomerId);
}

```

### Code Explanations:

- **HasKey(c => c.CustomerId):** Specifies that CustomerId is the primary key for the Customer entity.
- **Non-Convention Keys:** Useful when the primary key does not follow EF Core’s default naming conventions.
- **Identity Columns:** If needed, you can also configure the primary key to be an identity column (auto-incremented) using ValueGeneratedOnAdd().

### Configuring Composite Primary Keys

In some scenarios, an entity may require a composite primary key composed of multiple properties. Composite keys uniquely identify a record using a combination of two or more properties, common in join tables or when no single property is sufficient for uniqueness. For example, an OrderItem entity may use both OrderId and ProductId as a composite primary key:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<OrderItem>()
        .HasKey(oi => new { oi.OrderId, oi.ProductId });
}

```

### Code Explanation:

- **HasKey(oi => new { oi.OrderId, oi.ProductId }):** Defines a composite primary key using both OrderId and ProductId properties.
- **Use Cases:** Commonly used in many-to-many relationship join tables or scenarios where the combination of properties ensures uniqueness.
- **Order of Properties:** The order of properties in the composite key matters, especially when creating indexes. Ensure consistency across your configurations.
- **EF Core Limitations:** EF Core does not support composite keys with more than 16 properties. Keep composite keys concise.

### Configuring Indexes

Indexes enhance the performance of database queries by allowing faster data retrieval. EF Core allows us to configure indexes on single or multiple properties (composite indexes) at the entity level. You can also enforce uniqueness to ensure data integrity. For example, to create a unique index on the Email property of the Customer entity:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .HasIndex(c => c.Email)
        .IsUnique();
}

```

### Code Explanation:

- **HasIndex(c => c.Email):** Creates an index on the Email property of the Customer entity.
- **IsUnique():** Ensures the Email value is unique across all records, preventing duplicate entries.

### Composite Indexes:

You can also create indexes on multiple properties by passing an anonymous object. For example, we want to create an index on the customer entity’s first and last name columns. EF Core generates index names by default, but you can also specify custom names using HasDatabaseName.

```csharp
modelBuilder.Entity<Customer>()
    .HasIndex(c => new { c.LastName, c.FirstName })
    .HasDatabaseName("IX_Customer_LastName_FirstName");

```

### Filtered Indexes:

EF Core supports filtered indexes (indexes with a WHERE clause) for more advanced scenarios. For example, we can create an Index on the Email where the Where clause [Email] IS NOT NULL as follows. The Email on the WHERE clause will automatically apply the [Email] IS NOT NULL condition to the query.

```csharp
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.Email)
    .HasFilter("[Email] IS NOT NULL");

```

### Include Columns:

EF Core allows non-key columns in indexes to be included to cover specific queries. You can consider this a Covering Query. For example, we will create an Index on the Email column, but it will also include the FirstName and LastName columns. This is useful when we want to retrieve the First Name, Last Name, and Email based on the Email condition. In this case, it will directly return the data from the Index table without referring to the actual database table.

```csharp
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.Email)
    .IncludeProperties(c => new { c.FirstName, c.LastName });

```

### Configuring Cascade Delete Behavior for Specific Relationships

EF Core allows us to define how deletions in one entity affect related entities. By configuring cascade delete behavior at the relationship level, we can control whether related entities are automatically deleted (Cascade), set to NULL (SetNull), restricted (Restrict), or have no action (NoAction). We can set this delete behavior using the OnDelete() method. For example, to set up a cascade delete for the Order and OrderItem relationship, we need to configure the settings as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<OrderItem>()
        .HasOne(oi => oi.Order)
        .WithMany(o => o.OrderItems)
        .HasForeignKey(oi => oi.OrderId)
        .OnDelete(DeleteBehavior.Cascade);
}

```

### Code Explanations:

- **OnDelete(DeleteBehavior.Cascade):** Configures the relationship so that deleting an Order automatically deletes all related Order Items.

### Alternative Delete Behaviors:

- **DeleteBehavior.Restrict:** Prevents deletion of the principal entity if dependent entities exist.
- **DeleteBehavior.SetNull:** Sets the foreign key properties in dependent entities to NULL when the principal is deleted.
- **DeleteBehavior.NoAction:** No action is taken; referential integrity must be handled manually.

### Ignoring Entities

There might be scenarios where certain classes in your application represent domain concepts but should not be mapped to database tables. EF Core allows us to exclude these entities from the model, ensuring they do not persist in the database. For example, we have an entity AuditLog that we don’t want to map to the database.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Ignore<AuditLog>();
}

```

### Code Explanation:

- **Ignore():** Excludes the AuditLog entity from the EF Core model, preventing the creation of a corresponding table.

### Use Cases:

- **DTOs (Data Transfer Objects):** Classes used for transferring data between layers but not intended for persistence.
- **Base Classes:** Abstract base classes that provide common properties or methods but should not be instantiated.
- **Temporary or Computed Classes:** Classes used for specific operations that do not require storage.

### Configuring Alternate Keys (Unique Constraints)

Beyond primary keys, entities can have alternate keys that enforce uniqueness on other properties. Alternate keys act as unique constraints, ensuring that certain properties remain unique across all records. EF Core enforces uniqueness at the database level, preventing duplicate entries that violate alternate key constraints. For example, to enforce a unique constraint on the Email property of the Customer entity, we can configure as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .HasAlternateKey(c => c.Email)
        .HasName("AK_Customer_Email");
}

```

### Code Explanation:

- **HasAlternateKey(c => c.Email):** Defines Email as an alternate key for the Customer entity.
- **HasName(“AK_Customer_Email”):** Assigns a custom name to the alternate key constraint in the database.
- **Use Cases:** Ensuring unique fields like Email, Username, or other business-critical identifiers.
- **Primary vs. Alternate Keys:** An entity can have multiple alternate keys but only one primary key.

### Composite Alternate Keys:

We can also define alternate keys using multiple properties as follows. Here, the combination of FirstName, LastName, and DateOfBirth cannot be duplicated.

```csharp
modelBuilder.Entity<Customer>()
    .HasAlternateKey(c => new { c.FirstName, c.LastName, c.DateOfBirth })
    .HasName("AK_Customer_FullNameDOB");

```

### Difference Between Alternate Keys and Indexes:

- **Alternate Keys:** Enforce uniqueness, which can be used as foreign keys in other entities.
- **Indexes:** Improve query performance but do not inherently enforce uniqueness unless explicitly specified with IsUnique().

### Configuring Owned Entities

Owned entities are types that do not have their own identity and are owned by another entity. The properties of an owned entity are mapped to columns in the owner’s table. This configuration is useful for modeling value objects or complex types that logically belong to a single entity. Suppose, Customer has an owned type Address.

```csharp
[Owned]
public class Address
{
    public string Street { get; set; }
    public string City { get; set; }
}
public class Customer
{
    public int CustomerId { get; set; }
    public string Name { get; set; }
    public Address Address { get; set; }
}
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .OwnsOne(c => c.Address);
}

```

### Code Explanation:

- **OwnsOne(c => c.Address):** Indicates that Address is an owned entity of Customer.
- **Property Mapping:** The properties of Address will be mapped to columns in the Customer table, reflecting a one-to-one relationship where Address is tightly bound to Customer
- **No Separate Table:** Owned entities do not have their own tables; their properties are included in the owner’s table.

### Complete Example with Models, DbContext, and Program Class

Let’s implement a complete example to understand how these Entity Configurations work together in a .NET console application using Entity Framework Core Fluent API. We will define a few models, apply entity configurations, and show the output.

### Creating Models

We will create four entities: Customer, Product, Order, and OrderItem. We will also create an enum OrderStatus and an owned entity Address.