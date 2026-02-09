# 12. Default Conventions in Entity Framework Core

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# Default Conventions in Entity Framework Core

In this article, I will discuss Default Conventions in Entity Framework Core (EF Core) with Examples. Please read our previous article discussing [Explicit Loading in Entity Framework (EF) Core](https://dotnettutorials.net/lesson/explicit-loading-in-entity-framework-core/) with Examples.

### What are Default Conventions in EF Core?

In Entity Framework Core (EF Core), default conventions are predefined rules that EF Core uses to determine how entity classes map to database tables and columns. These conventions enable EF Core to automatically generate database schemas without requiring explicit configuration. This “Convention over Configuration” approach simplifies development by automating tasks like:

- Automatically detect Primary Key and Foreign Key properties based on naming conventions.
- Setting up one-to-one, one-to-many, and many-to-many Relationships Between Tables based on the navigation properties defined in the entities.
- Determining Column Data Types based on the .NET data types.
- Determining the Table and Column Names based on default naming conventions.
- Configure columns as nullable or non-nullable based on the .NET type’s nullability.
- Automatically generate indexes and constraints for keys and foreign keys. For primary key clustered index and for foreign key non-clustered index.
- Automatically Set up the default cascade delete behaviors based on the relationship types.

While Default Conventions offer a solid starting point, they can be overridden using Data Annotations or the Fluent API for custom configurations, which we will discuss in our upcoming sessions. In this session, let’s focus on understanding the default conventions in detail.

### Example to UnderstandDefault Conventions in Entity Framework Core:

To illustrate EF Core’s Default Conventions, let’s build a real-world example using a student management system in a .NET console application. We will define the following entities:

- Student
- Teacher
- Course
- Address
- Gender (Enumeration)

Then, we will see how EF Core automatically configures database schema such as table names, column names, primary keys (PK), foreign keys (FK), indexes, column data types, column attributes (e.g., nullable, not nullable, identity), relationships between tables, and cascade behaviors.

### Create Model Classes

Let’s start by creating the following model classes. Create a folder called Entities, and inside that folder, please create the following models.

### Student

Create a class file named Student.cs within the Entities folder and then copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Student
    {
        public int StudentId { get; set; }  // SQL Type: INT (NOT NULL, Primary Key)
        public string FirstName { get; set; }  // SQL Type: NVARCHAR(MAX) (NOT NULL)
        public string? LastName { get; set; }  // SQL Type: NVARCHAR(MAX) (NULL)
        public DateTime? DateOfBirth { get; set; }  // SQL Type: DATETIME2 (NULL)
        public decimal GPA { get; set; }  // SQL Type: DECIMAL(18, 2) (NOT NULL)
        public bool IsActive { get; set; }  // SQL Type: BIT (NOT NULL)
        public byte[] ProfilePicture { get; set; }  // SQL Type: VARBINARY(MAX) (NOT NULL)
        public virtual Gender Gender { get; set; }  // SQL Type: INT (NOT NULL, because enums are stored as INT)
        public virtual Address Address { get; set; }  // SQL Type: This would create a foreign key with default INT (if Address is required, it would be NOT NULL)
        public virtual ICollection<Course> Courses { get; set; }  // SQL Type: This would create a join table for many-to-many relationships
    }
}

```

### Key Points:

- **Primary Key:** EF Core recognizes the StudentId property as the primary key due to its naming convention.
- **Nullable Properties:** LastName and DateOfBirth are nullable, allowing NULL values in the database.
- **Enum Mapping:** The Gender property is an enumeration stored as an INT in the database.
- **Navigation Properties:** Address and Courses establish relationships with other entities.

### Teacher

Create a class file named Teacher.cs within the Entities folder and then copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Teacher
    {
        public int TeacherId { get; set; }  // PK (INT, Identity)
        public string FullName { get; set; }  // NVARCHAR(MAX), NOT NULL
        public DateTime HireDate { get; set; }  // DateTime, NOT NULL
        public TimeSpan WorkHours { get; set; }  // TIME, NOT NULL
        public decimal Salary { get; set; }  // DECIMAL(18,2), NOT NULL
        public bool IsTenured { get; set; }  // BIT, NOT NULL
        public virtual ICollection<Course> Courses { get; set; }  // One-to-Many relationship
    }
}

```

### Key Points:

- **Primary Key:** TeacherId is automatically identified as the primary key.
- **Navigation Property:** Courses establish a one-to-many relationship with the Course entity.

### Course

Create a class file named Course.cs within the Entities folder, and then copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Course
    {
        public int CourseId { get; set; }  // PK (INT, Identity)
        public string Title { get; set; }  // NVARCHAR(MAX), NOT NULL
        public double Credits { get; set; }  // FLOAT, NOT NULL
        public int TeacherId { get; set; }  // FK to Teacher (INT, NOT NULL)
        public virtual Teacher Teacher { get; set; }  // Navigation property
        public virtual ICollection<Student> Students { get; set; }  // Many-to-Many relationship
    }
}

```

### Key Points:

- **Primary Key:** CourseId is automatically identified as the primary key.
- **Foreign Key:** TeacherId links the Course to a Teacher.
- **Navigation Properties:** Teacher and Students define relationships with Teacher and Student entities, respectively.

### Address

Create a class file named Address.cs within the Entities folder and then copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Address
    {
        public string Street { get; set; }  
        public string City { get; set; }  
        public string PostalCode { get; set; }
        public int AddressId { get; set; }
        public string? State { get; set; }  
        public string Country { get; set; }  
        public int? StudentId { get; set; }  
        public virtual Student Student { get; set; }  
        public int? TeacherId { get; set; }  
        public virtual Teacher Teacher { get; set; }  
    }
}

```

### Key Points:

- **Primary Key:** AddressId is the primary key.
- **Foreign Keys:** StudentId and TeacherId link Address to Student and Teacher entities, respectively.
- **Optional Relationships:** Both foreign keys are nullable, indicating that an address may belong to a student, a teacher, or neither.

### Gender

Create a class file named Gender.cs within the Entities folder, and then copy and paste the following code. This is going to be an Enum to hold the Gender-named constants. By default, EF Core stores enums as their underlying integer values in the database.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public enum Gender
    {
        Male = 1,
        Female = 2,
        Other = 3
    }
}

```

### Modifying DbContext Class

The DbContext is the bridge between domain classes and the database. It manages entity configurations, connections, and more. Next, please modify the EFCoreDbContext class as follows. Here, we are adding the Entities as DbSet properties.

```csharp
using Microsoft.EntityFrameworkCore;
namespace EFCoreCodeFirstDemo.Entities
{
    public class EFCoreDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            //Connection String
            optionsBuilder.UseSqlServer("Server=LAPTOP-6P5NK25R\\SQLSERVER2022DEV;Database=MyStudentDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        // DbSet properties represent the tables in the database. 
        // Each DbSet corresponds to a table, and the type parameter corresponds to the entity class mapped to that table.
        public DbSet<Student> Students { get; set; }
        public DbSet<Teacher> Teachers { get; set; }
        public DbSet<Course> Courses { get; set; }
        public DbSet<Address> Addresses { get; set; }
    }
}

```

### Key Points:

- **Connection String:** Specifies the database server and database name. In production applications, it’s best practice to store connection strings securely, such as in configuration files or environment variables.
- **DbSet Properties:** Each DbSet corresponds to a table in the database and allows CRUD operations on the entities.

### Generating and Applying Migrations

Migrations in EF Core allow us to update the database schema to match domain models while preserving existing data. So, after setting up the models and DbContext, we need to create the migration and apply it to sync our models with the database schema.

So, open the Package Manager Console and execute the Add-Migration ExtendingModel command as follows. You can give your migration any name. I am giving the name ExtendingModel.

### Warning for Decimal Property Precision:

By default, EF Core maps decimal properties to the SQL data type DECIMAL (18,2). The database column can store up to 18 digits, with two digits after the decimal point. If the values you want to store in the GPA or Salary property require more precision (e.g., more than 2 decimal places), those values will be silently truncated, causing a loss of precision. That is the reason why we are getting the above warning. In our upcoming session, we will see how to overcome these warnings using Data annotation and Fluent API configurations. For now, ignore the warning.

### Updating the Database:

Again, open the Package Manager Console and execute the Update-Database command as follows:

This command applies the pending migrations to the database, creating the necessary tables and schema based on your models. Upon successful execution, EF Core creates the MyStudentDB database with the configured tables.

### What are the Default Entity Framework Core Conventions?

EF Core’s Default Conventions cover a wide range of configurations. Let us understand these Default Entity Framework Core Conventions one by one.

### Default Schema in EF Core:

EF Core uses the database provider’s default schema. For SQL Server, this is typically dbo. You can also specify a different schema using the Fluent API or Data Annotations if needed, which we will discuss in our coming sessions. For example, if you have a Student entity, EF Core will create the table as dbo.Students.

Now, if you verify the MyStudentDB database tables, you will see that they are created with the dbo schema, as shown in the image below.

### Default Table Name in EF Core:

Tables are named after the DbSet properties in the DbContext. If a DbSet is named Students, the corresponding table will be Students. EF Core does not automatically pluralize table names. It uses the exact name provided in the DbSet or the class name if DbSet is not specified. For example, public DbSet Students results in a table named Students. For a better understanding, please have a look at the following image.

### Default Primary Key Name in EF Core:

EF Core identifies a property as a primary key if it follows the naming conventions:

- A property named Id.
- A property named Id (e.g., StudentId).

The primary key is automatically configured as NOT NULL and set as the table’s primary key constraint. If both Id and Id are present, Id takes precedence. By default, the primary key column is placed first in the table. The absence of a key property results in an exception during migration. For a better understanding, please have a look at the following diagram.

### Default Foreign Key Column Name in EF Core:

In Entity Framework Core (EF Core), the default foreign key column name is determined based on the relationship between the entities.

### Single Foreign Key (One-to-Many or One-to-One):

By default, the FK column is named Id. For example, the Address table has a foreign key named StudentId referencing the Student table. In the Courses table, TeacherId is the foreign key to the Teachers table.

EF Core Automatically configures the foreign key relationships based on navigation properties and matching key properties. For a better understanding, please have a look at the following two entities.

In this case, EF Core will automatically name the foreign key column as StudentId in the Addresses table. For a better understanding, please check the Addresses table, and you should see the following:

### Composite Foreign Key (Many-to-Many Relationship):

For many-to-many relationships, EF Core creates a junction (or join) table with foreign key columns referring to both related entities. The foreign key columns will be named based on the format PrimaryKey and PrimaryKey. For a many-to-many relationship between Student and Course, EF Core will generate a junction table (CourseStudent) with two foreign key columns as shown in the below image:

### Default Constraints in EF Core:

In Entity Framework Core (EF Core), several types of constraints are automatically generated when creating database tables. These include primary key constraints, foreign key constraints, and unique constraints. These constraints can be customized using the Fluent API or Data Annotations if specific naming or behaviors are required.

### Primary Key (PK) Constraint Name:

By default, EF Core names the primary key constraint as PK_. For example, if the table name is Students, the primary key constraint will be named PK_Students. For a better understanding, please look at the below image.