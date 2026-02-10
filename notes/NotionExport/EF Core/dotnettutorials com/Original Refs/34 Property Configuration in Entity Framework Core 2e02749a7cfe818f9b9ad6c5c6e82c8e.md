# 34. Property Configuration in Entity Framework Core using Fluent API

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# Property Configuration in Entity Framework Core using Fluent API

In this article, I will discuss Property Configuration in Entity Framework Core using Fluent API with Examples. Please read our previous article discussing [Entity Configurations in Entity Framework Core using Fluent API](https://dotnettutorials.net/lesson/entity-configurations-using-entity-framework-core-fluent-api/) with Examples.

## Property Configurations in Entity Framework Core using Fluent API

In Entity Framework (EF) Core, Property Configurations allow us to define settings and rules specific to individual properties of an entity. This includes specifying column names, data types, default values, nullability, maximum length, precision and scale, computed columns, value conversions, concurrency tokens, and more. By explicitly configuring properties using the Fluent API, we ensure that database schema accurately reflects application requirements, thereby improving data integrity, consistency, and performance.

Let us proceed and understand how and when to apply property-level configurations using Entity Framework Core Fluent API in a .NET console application. We will cover the following property configurations:

- Configuring Column Names
- Configuring Data Types
- Configuring Default Values
- Configuring Required and Nullable Properties
- Configuring Maximum Length
- Configuring Precision and Scale
- Configuring Computed Columns
- Configuring Value Conversions
- Configuring Concurrency Tokens
- Configuring Shadow Properties
- Configuring Value Generation (Identity)
- Ignoring Properties

### Configuring Column Names

By default, EF Core maps each property of an entity to a database column with the same name as the property name. However, there are scenarios where we might need to specify a different column name to align with existing database conventions, legacy databases, or specific organizational standards.

Suppose we have an entity called Customer with a property called FirstName, but we want it to be mapped to a column called First_Name in the database. Then we need to configure the same using EF Core Fluent API as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .Property(c => c.FirstName)
        .HasColumnName("First_Name");
}

```

### Code Explanation:

- The HasColumnName(“First_Name”) method specifies that the FirstName property should be mapped to a column named First_Name in the database. This allows for consistency with existing database naming conventions or requirements.

### Configuring Data Types

By default, EF Core automatically selects the appropriate database data type based on the .NET type of the property. However, there are cases where we need to specify a particular data type to match existing database schemas, optimize storage, or meet specific application requirements. For example, if we have a decimal property Price in the Product entity and we want to ensure it is mapped to a SQL Server column of type decimal(10,2), then we need to do the following Fluent API configuration:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Property(p => p.Price)
        .HasColumnType("decimal(10, 2)");
}

```

### Code Explanation:

- **HasColumnType(“decimal(10, 2)”):** Explicitly sets the SQL data type of the Price property to decimal with a precision of 10 and a scale of 2.
- **Precision and Scale:** Precision (10) defines the total number of digits, while scale (2) defines the number of digits to the right of the decimal point.

### Configuring Default Values

Setting default values for properties ensures that when a new record is inserted without explicitly setting a value for a property, the database assigns the predefined default value. This is useful for properties like status indicators, timestamps, or flags. For example, to set a default order status of Pending for the Order entity, we can configure the following:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>()
        .Property(o => o.Status)
        .HasDefaultValue(OrderStatus.Pending);
}

```

### Code Explanation:

- **HasDefaultValue(OrderStatus.Pending):** Specifies that the default value for the Status property is Pending. If OrderStatus is an enum, EF Core will store its underlying integer value unless a value converter is specified.

### Setting Default Values Using SQL Functions:

We can also set default values using SQL functions. For example, setting a default date:

```csharp
modelBuilder.Entity<Order>()
    .Property(o => o.OrderDate)
    .HasDefaultValueSql("GETUTCDATE()");

```

### Configuring Required Properties

By default, EF Core determines whether a property is required (non-nullable) or optional (nullable) based on the CLR type of the property. For example, non-nullable types, such as int, decimal, bool, etc., are treated as required. Nullable types such as int?, decimal?, or reference types like string? are optional. However, if we want to explicitly enforce a property to be required, we can use the IsRequired() method. For example, to make the Email property of the Customer entity required, we need to do the following Fluent API Configuration:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .Property(c => c.Email)
        .IsRequired();
}

```

### Code Explanations:

- The IsRequired() method specifies that the Email property cannot be null in the database.

### Configuring Nullable Properties

By default, nullable types are considered optional (nullable). However, we can explicitly configure a property to allow null values using the IsRequired(false) method. For example, to make the Description property in the Product entity optional, we need to do the following Fluent API Configuration:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Property(p => p.Description)
        .IsRequired(false);
}

```

### Code Explanations:

- The IsRequired(false) method allows the Description property to have null values.

### Configuring Maximum Length:

When dealing with string properties, it is often necessary to define the maximum length, which will translate into the appropriate column size in the database and prevent users from exceeding the allowed limit, enforcing data integrity and optimizing storage. For example, we can set a maximum length of 100 characters for the FirstName property in the Customer entity as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .Property(c => c.FirstName)
        .HasMaxLength(100);
}

```

### Code Explanation:

- **HasMaxLength(100):** Ensures that the FirstName property cannot exceed 100 characters.
- **Database Translation:** Depending on the database provider, this might translate to VARCHAR(100), NVARCHAR(100), etc.

### Configuring Precision and Scale

For decimal properties, we can configure the precision (total number of digits) and scale (number of decimal places) to ensure that numeric data is stored accurately, which is critical for financial calculations, measurements, and other precise data types. For example, for a Price property in the Product entity, we can configure the precision and scale as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Property(p => p.Price)
        .HasPrecision(10, 2);
}

```

### Code Explanation:

- **HasPrecision(10, 2):** Sets the Price property to have a precision of 10 digits and a scale of 2 decimal places, corresponding to a SQL Server column of type decimal(10,2). Higher precision and scale consume more storage space, so, balance based on application requirements.

### Configuring Computed Columns

Computed columns are database columns whose values are automatically calculated based on other columns. This ensures data consistency and reduces the need for manual calculations in the application layer. For example, if we want to calculate the TotalPrice in the OrderItem entity based on the Quantity and UnitPrice, then we need to configure the same as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<OrderItem>()
        .Property(oi => oi.TotalPrice)
        .HasComputedColumnSql("[Quantity] * [UnitPrice]");
}

```

### Code Explanation:

- **HasComputedColumnSql(“[Quantity] * [UnitPrice]”):** Defines the TotalPrice column as computed by multiplying the Quantity and UnitPrice columns.
- **Database Responsibility:** The database automatically updates the TotalPrice whenever Quantity or UnitPrice changes.

### Configuring Value Conversions

Sometimes, we need to store a property in the database differently from how it is represented in the application. This can be done using Value Conversions. This is useful for transforming data types, encrypting data, or storing enums as strings. For example, if we want to store the OrderStatus enum as a string in the database, then we need to do the following configuration using EF Fluent API:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>()
        .Property(o => o.Status)
        .HasConversion<string>();
}

```

### Code Explanations:

- **HasConversion():** Converts the OrderStatus enum to its string representation when storing it in the database and converts it back when reading.

### Configuring Concurrency Tokens:

Concurrency tokens help detect and handle conflicts when multiple users attempt to update the same record simultaneously. EF Core uses these tokens to implement optimistic concurrency control, preventing data overwrites. EF Core uses a Timestamp property to handle this. For example, to configure the RowVersion property as a concurrency token:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>()
        .Property(o => o.RowVersion)
        .IsRowVersion();
}

```

### Code Explanation:

- **IsRowVersion():** Marks the RowVersion property as a concurrency token. EF Core uses this property to detect concurrent updates.
- **Underlying Type:** Typically, RowVersion is a byte[] that the database automatically updates on each modification.

### Alternative Concurrency Tokens:

Besides row versions, you can use other properties (e.g., LastModified) as concurrency tokens. In this case, we need to use the IsConcurrencyToken method as follows:

```csharp
modelBuilder.Entity<Order>()
    .Property(o => o.LastModified)
    .IsConcurrencyToken();

```

### Configuring Shadow Properties

Shadow properties are properties that are not defined in the entity class but are part of the EF Core model and mapped to database columns. They are useful for tracking metadata, audit information, or any additional data that should be stored in the database without being part of the domain model. For example, we might want to track CreatedDate and ModifiedDate for entities but not define them in the entity class. We can configure shadow properties like this:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Property<DateTime>("CreatedDate")
        .HasDefaultValueSql("GETDATE()");
}

```

### Code Explanation:

- **Property(“CreatedDate”):** Defines a shadow property named CreatedDate of type DateTime.
- **HasDefaultValueSql(“GETDATE()”):** Sets the default value of CreatedDate to the current date and time when a new record is inserted.

### Configuring Value Generation (Identity)

Value generation strategies define how the database generates values for certain properties. Common strategies include identity columns (auto-incremented values). Configuring these ensures that primary keys or other unique identifiers are generated appropriately. For example, to configure the ID as an identity column in the Customer entity, we need to configure the same as follows:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>()
        .Property(c => c.Id)
        .ValueGeneratedOnAdd();
}

```

### Code Explanation:

- **ValueGeneratedOnAdd():** Configures the Id property to generate its value automatically when a new record is inserted. This is typically used for identity columns.
- **Database Behavior:** For SQL Server, this translates to the IDENTITY property, which auto-increments the value.

### Ignoring Properties

There are instances where certain properties of an entity should not be mapped to the database. This could be because they are used only for business logic, are computed in the application, or should remain private. EF Core allows us to exclude these properties from the model. Suppose the Product entity has a property called FullDescription that we don’t want to persist in the database:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .Ignore(p => p.FullDescription);
}

```

### Code Explanation:

- **Ignore(p => p.FullDescription):** Excludes the FullDescription property from the EF Core model, ensuring it is not persisted to the database.
- **Use Cases:** Temporary fields, properties used solely in the application layer, or redundant data that is derived from other properties.

### Complete Example with Models, DbContext, and Program Class

Let’s implement a complete example to understand how these Property Configurations work together in a .NET console application using Entity Framework Core Fluent API. We will define a few models, apply property configurations, and show the output.

### Creating Models