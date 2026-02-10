# Example of All Joins

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class Linq
{
    public static void Demo()
    {
        // ==========================================
        // 1. DATA SETUP
        // ==========================================
        var departments = DataSeeder.GetDepartments();
        var employees = DataSeeder.GetEmployees();

        Console.WriteLine("--- DATA LOADED ---\n");

        // ==========================================
        // 2. EXERCISES
        // ==========================================

        // ---------------------------------------------------------------------
        // TOPIC: INNER JOIN
        // Goal: List Employee Name and their Department Name.
        //       (Exclude employees with no department and departments with no employees).
        // ---------------------------------------------------------------------
        Console.WriteLine("--- 1. Inner Join Results ---");

        // A. Query Syntax
        // TODO: Write a query using 'from', 'join', 'select'
        var innerJoinQuery = from e in employees
                             join d in departments
                             // Complete the code here...
                             on e.DeptId equals d.Id
                             select new { Employee = e.Name, Dept = d.Name };

        // B. Method Syntax
        // TODO: Write the same using .Join()
        // params: outerSource, innerKey, outerKey, resultSelector
        var innerJoinMethod = employees.Join(
            departments,
            e => e.DeptId,
            d => d.Id,
            (e, d) => new { Employee = e.Name, Dept = d.Name }
        ); // <-- MODIFY THIS

        Print(innerJoinQuery, "Inner Join (Query)");

        // ---------------------------------------------------------------------
        // TOPIC: GROUP JOIN
        // Goal: List every Department and a collection of their employees.
        //       (Must include Departments that have 0 employees).
        // ---------------------------------------------------------------------
        Console.WriteLine("\n--- 2. Group Join Results ---");

        // A. Query Syntax
        // TODO: Use 'join ... into ...'
        var groupJoinQuery = from d in departments
                                 // Complete code here
                             join e in employees on d.Id equals e.DeptId into empGroup
                             select new { Dept = d.Name, Employees = empGroup };

        // B. Method Syntax
        // TODO: Use .GroupJoin()
        var groupJoinMethod = departments.GroupJoin(
            employees,
            d => d.Id,
            e => e.DeptId,
            (d, emps) => new { Dept = d.Name, Employees = emps }
        ); // <-- MODIFY THIS

        foreach (var item in groupJoinQuery)
        {
            Console.WriteLine($"Dept: {item.Dept} has {item.Employees.Count()} employees.");
        }

        // ---------------------------------------------------------------------
        // TOPIC: LEFT OUTER JOIN
        // Goal: List ALL Employees and their Department Name.
        //       If the employee has no department, display "No Department".
        // ---------------------------------------------------------------------
        Console.WriteLine("\n--- 3. Left Outer Join Results ---");

        // A. Query Syntax
        // TODO: Use 'join ... into ...' combined with 'from ... in ...DefaultIfEmpty()'
        var leftJoinQuery = from e in employees
                            join d in departments on e.DeptId equals d.Id into empDepts
                            from d in empDepts.DefaultIfEmpty()
                            select new { e.Name, DeptName = d == null ? "No Department" : d.Name };

        // B. Method Syntax
        // TODO: This usually requires GroupJoin().SelectMany(DefaultIfEmpty)
        // Try to implement the Method Syntax version (This is tricky for beginners!)
        var leftJoinMethod = employees
            .GroupJoin(
                departments,
                e => e.DeptId,
                d => d.Id,
                (e, dList) => new { e, dList }
            )
            .SelectMany(
                x => x.dList.DefaultIfEmpty(),
                (x, d) => new { x.e.Name, DeptName = d?.Name ?? "No Department" }
            );

        Print(leftJoinQuery, "Left Outer Join");

        // ---------------------------------------------------------------------
        // TOPIC: SELECT MANY (with 2 Parameters)
        // Goal: Flatten the relationship. We want a simple list strings saying:
        //       "{DepartmentName} has employee {EmployeeName}"
        // ---------------------------------------------------------------------
        Console.WriteLine("\n--- 4. SelectMany (One-to-Many Flattening) ---");

        // We start with the Departments list.
        // TODO: Use SelectMany that takes the Collection, then the Result Selector
        var selectManyResult = departments.SelectMany(
             d => employees.Where(e => e.DeptId == d.Id), // 1. Collection Selector
             (d, e) => $"{d.Name} has employee {e.Name}"  // 2. Result Selector
        );

        foreach (var str in selectManyResult) Console.WriteLine(str);

        // ---------------------------------------------------------------------
        // TOPIC: SELF JOIN
        // Goal: List Employees and the Name of their Manager.
        //       (Match ManagerId to the Employee Id inside the same list)
        // ---------------------------------------------------------------------
        Console.WriteLine("\n--- 5. Self Join Results ---");

        // A. Query Syntax
        // TODO: Join 'employees' with 'employees'
        var selfJoinQuery = from e in employees
                            join m in employees on e.ManagerId equals m.Id
                            select new { Employee = e.Name, Manager = m.Name };

        Print(selfJoinQuery, "Self Join");

        Console.ReadKey();
    }

    // Helper to print basic list results
    static void Print(IEnumerable<dynamic> list, string header)
    {
        Console.WriteLine($"> {header}:");
        foreach (var item in list)
        {
            Console.WriteLine(item.ToString());
        }
    }
}

// ==========================================
// DATA MODELS AND SEEDER
// ==========================================

public class Department
{
    public int Id { get; set; }
    public string Name { get; set; }
}

public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; }
    public int? DeptId { get; set; }    // Nullable for "No Department" scenario
    public int? ManagerId { get; set; } // Nullable for "Top Boss" scenario
}

public static class DataSeeder
{
    public static List<Department> GetDepartments()
    {
        return new List<Department>
        {
            new Department { Id = 1, Name = "Human Resources" },
            new Department { Id = 2, Name = "IT" },
            new Department { Id = 3, Name = "Marketing" } // Case: Dept with employees
        };
    }

    public static List<Employee> GetEmployees()
    {
        return new List<Employee>
        {
            // Case: Normal Employee in IT
            new Employee { Id = 1, Name = "Alice", DeptId = 2, ManagerId = null }, // CEO (No manager)
            
            // Case: Employee in HR, Managed by Alice
            new Employee { Id = 2, Name = "Bob", DeptId = 1, ManagerId = 1 }, 
            
            // Case: Employee in IT, Managed by Alice
            new Employee { Id = 3, Name = "Charlie", DeptId = 2, ManagerId = 1 },

            // Case: Employee with NO Department (Edge case for Outer Joins)
            new Employee { Id = 4, Name = "David", DeptId = null, ManagerId = 2 },

            // Case: Employee in Marketing (Marketing exists, but let's say Marketing is Id 3)
            new Employee { Id = 5, Name = "Eve", DeptId = 3, ManagerId = 2 }
        };
    }
}
```