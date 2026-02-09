# 8. How to Design Database using EF Core Code First Approach

Back to: [ASP.NET Core Tutorials For Beginners and Professionals](https://dotnettutorials.net/course/asp-net-core-tutorials/)

# How to Design Database using EF Core Code First Approach:

In this article, I will discuss How to Design a Database using the EF Core Code First Approach. The Code-First approach in Entity Framework Core (EF Core) allows us to design the database starting from the C# domain classes rather than designing the database first and then generating the models. Once we create the model classes and DbContext class, EF Core will take responsibility for translating these model classes into database tables.

Let us develop a comprehensive Student Management System for an educational institution. We will also use this application as the base for the upcoming articles. We will work with the same application we have been using so far. So, let us proceed to create the Model classes. We will create all the Model classes within the Entities folder.

### Student:

The Student model represents students within the institution, including personal details and academic information. So, create a class file named Student.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Student
    {
        public int StudentId { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public string Gender { get; set; }
        public DateTime DateOfBirth { get; set; }
        public int BranchId { get; set; }
        public Branch Branch { get; set; }
        public Address Address { get; set; }
        public ICollection<Course> Courses { get; set; }
    }
}

```

### Properties Description:

- **StudentId:** Primary Key. Unique identifier for each student.
- **FirstName:** First name of the student.
- **LastName:** Last name of the student.
- **Gender:** Gender of the student.
- **DateOfBirth:** Date of birth of the student.
- **BranchId:** Foreign Key. Links the student to a specific branch.
- **Branch:** The Branch navigation property represents the branch the student belongs to.
- **Address:** Navigation property for the student’s address.
- **Courses:** A collection representing the many-to-many relationship between students and courses.

### Relationships:

- **Branch:** A Student belongs to one Branch (one-to-one).
- **Courses:** A Student can enroll in many Courses (one-to-many).
- **Address:** A Student has one Address (one-to-one relationship).

### Branch:

This model represents a branch. That means there are multiple branches of the institutions. It will represent a particular branch. So, create a class file named Branch.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Branch
    {
        public int BranchId { get; set; }
        public string BranchLocation { get; set; }
        public string? BranchPhoneNumber { get; set; }
        public string? BranchEmail { get; set; }
        public ICollection<Student> Students { get; set; }
        public ICollection<Teacher> Teachers { get; set; }
    }
}

```

### Properties Description:

- **BranchId:** Primary Key. Unique identifier for each branch.
- **BranchLocation:** Location or Address of the branch.
- **BranchPhoneNumber:** (Optional) Phone number for the branch.
- **BranchEmail:** (Optional) Email address for the branch.
- **Students:** Collection of students enrolled in this branch.
- **Teachers:** A collection of teachers has been assigned to this branch.

### Relationships:

- **Students:** A Branch can have multiple Students (one-to-many).
- **Teachers:** A Branch can have multiple Teachers (one-to-many).

### Teacher:

This model represents teachers in the system. So, create a class file named Teacher.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Teacher
    {
        public int TeacherId { get; set; }
        public string TeacherName { get; set; }
        public int BranchId { get; set; }
        public Branch Branch { get; set; }
        public Address Address { get; set; }
        public ICollection<Subject> Subjects { get; set; }
    }
}

```

### Properties Description:

- **TeacherId:** Primary Key. Unique identifier for each teacher.
- **TeacherName:** Name of the teacher.
- **BranchId:** Foreign Key. Links the teacher to a specific branch.
- **Branch:** The Branch navigation property represents the branch the teacher works for.
- **Address:** Navigation property for the teacher’s address.
- **Subjects:** Collection of subjects taught by the teacher.

### Relationships:

- **Branch:** A Teacher works in one Branch (one-to-one).
- **Subjects:** A Teacher can teach multiple Subjects (one-to-many).
- **Address:** A Teacher has one Address (one-to-one relationship).

### Subject:

This Model contains information about subjects taught in the institution, including their names and descriptions. So, create a class file named Subject.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Subject
    {
        public int SubjectId { get; set; }
        public string SubjectName { get; set; }
        public string Description { get; set; }
        public ICollection<Teacher> Teachers { get; set; }
        public ICollection<Course> Courses { get; set; }
    }
}

```

### Properties Description:

- **SubjectId:** Primary Key. Unique identifier for each subject.
- **SubjectName:** Name of the subject.
- **Description:** Description of the subject.
- **Teachers:** Collection of teachers who teach the subject.
- **Courses:** Collection of courses that include the subject.

### Relationships:

- **Teachers:** A Subject can have multiple Teachers (one-to-many).
- **Courses:** A Subject can be part of multiple Courses (one-to-many).

### Address:

This model represents the addresses of both students and teachers. So, create a class file named Address.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Address
    {
        public int AddressId { get; set; }
        public string Street { get; set; }
        public string City { get; set; }
        public string State { get; set; }
        public string PostalCode { get; set; }
        public int? StudentId { get; set; }
        public Student Student { get; set; }
        public int? TeacherId { get; set; }
        public Teacher Teacher { get; set; }
    }
}

```

### Properties Description:

- **AddressId:** Primary Key. Unique identifier for each address.
- **Street:** Street of the address.
- **City:** City of the address.
- **State:** State of the address.
- **PostalCode:** Postal code of the address.
- **StudentId:** Foreign Key (nullable). Links the address to a student (if applicable).
- **Student:** Navigation property is for the student who lives at this address.
- **TeacherId:** Foreign Key (nullable). Links the address to a teacher (if applicable).
- **Teacher:** The navigation property is for the teacher at this address.

### Relationships:

- **Student:** An address can be assigned to one Student (one-to-one).
- **Teacher:** An address can be assigned to one Teacher (one-to-one).

### Course:

This model represents courses that students enroll in. So, create a class file named Course.cs within the Entities folder and copy and paste the following code.

```csharp
namespace EFCoreCodeFirstDemo.Entities
{
    public class Course
    {
        public int CourseId { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Fees { get; set; }
        public ICollection<Student> Students { get; set; }
        public ICollection<Subject> Subjects { get; set; }
    }
}

```

### Properties Description:

- **CourseId:** Primary Key. Unique identifier for each course.
- **Name:** Name of the course.
- **Description:** Description of the course.
- **Fees:** Course fees.
- **Students:** Collection of students enrolled in the course.
- **Subjects:** Collection of subjects included in the course.

### Relationships:

- **Students:** A Course can have multiple Students (one-to-many).
- **Subjects:** A Course can have multiple Subjects (one-to-many).

### Modifying the Context Class:

Next, modify the EFCoreDbContext class as follows. Now, we will work with the StudentDB. If the StudentDB database exists, it will use it or create a new StudentDB database if it does not exist. Inside this StudentDB database, it will create the Required database tables, which we specified as DbSet entities.

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
namespace EFCoreCodeFirstDemo.Entities
{
    public class EFCoreDbContext : DbContext
    {
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            // Enable Logging
            optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information);
            //Connection String
            optionsBuilder.UseSqlServer("Server=LAPTOP-6P5NK25R\\SQLSERVER2022DEV;Database=StudentDB;Trusted_Connection=True;TrustServerCertificate=True;");
        }
        // DbSet properties represent the tables in the database. 
        // Each DbSet corresponds to a table, and the type parameter corresponds to the entity class mapped to that table.
        public DbSet<Student> Students { get; set; }
        public DbSet<Teacher> Teachers { get; set; }
        public DbSet<Branch> Branches { get; set; }
        public DbSet<Address> Addresses { get; set; }
        public DbSet<Subject> Subjects { get; set; }
        public DbSet<Course> Courses { get; set; }
    }
}

```

### Generating Migration and Syncing with Database

The most important point is that whenever we add or update domain classes or configurations, we need to sync the database with the model. For every change we make to our Model classes, we must create a Migration File and sync the database using the Add-Migration command and Update-Database commands using the Package Manager Console in Visual Studio.

To do so, open the NuGet Package Manager Console in Visual Studio by selecting Tools => NuGet Package Manager => Package Manager Console from the menu below. Then, execute the Add-Migration CreatingStudentDatabase command, as shown in the image below. Please select the Project where you want to generate the Migration.

### Updating the Database:

After creating the migration file, we need to update the database using the Update-Database command. We can use the –verbose option to view the generated SQL statements executed in the target database. So, open the Package Manager Console and execute the Update-Database -Verbose command, as shown in the image below.

Once the above command is executed successfully, it will generate and execute the required SQL Statements in the defined database. You can also verify the database and database tables using SSMS, as shown in the image below.