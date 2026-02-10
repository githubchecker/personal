# Linq

[let](Linq/let%202e02749a7cfe81799b00ca1c77783392.md)

[into](Linq/into%202e02749a7cfe814f9f6bfbb87889d430.md)

[SelectMany](Linq/SelectMany%202e02749a7cfe817888cfe2cd763c656e.md)

[GroupJoin](Linq/GroupJoin%202e02749a7cfe811aaf9cf84831ce979d.md)

[GroupBy](Linq/GroupBy%202e02749a7cfe81b69488e464fd3a422e.md)

[Example of All Joins](Linq/Example%20of%20All%20Joins%202e02749a7cfe816989dcd78b80afe5ab.md)

[IEnumerable vs IQueryable](Linq/IEnumerable%20vs%20IQueryable%202e02749a7cfe810eabc1e9f829fd5501.md)

## Joins Example

Here is a complete, compilable C# guide demonstrating all the requested LINQ Joins using **Query Syntax** and **Method Syntax (Extension Methods)**.

To demonstrate this effectively, we will use two classes: `Department` and `Employee`.

### 1. Data Setup

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class Department
{
    public int Id { get; set; }
    public string Name { get; set; }
    // List used specifically for SelectMany demonstration
    public List<string> FocusAreas { get; set; } = new List<string>();
}

public class Employee
{
    public int Id { get; set; }
    public string Name { get; set; }
    public int DeptId { get; set; }
    public int? ManagerId { get; set; } // Nullable for Self Join
}

public class Program
{
    public static void Main()
    {
        // SEED DATA
        var departments = new List<Department>
        {
            new Department { Id = 1, Name = "HR", FocusAreas = { "Hiring", "Benefits" } },
            new Department { Id = 2, Name = "IT", FocusAreas = { "Support", "Development" } },
            new Department { Id = 3, Name = "Marketing" } // No matching employees
        };

        var employees = new List<Employee>
        {
            new Employee { Id = 1, Name = "Alice", DeptId = 1, ManagerId = null },
            new Employee { Id = 2, Name = "Bob", DeptId = 2, ManagerId = 1 }, // Reports to Alice
            new Employee { Id = 3, Name = "Charlie", DeptId = 2, ManagerId = 1 }, // Reports to Alice
            new Employee { Id = 4, Name = "David", DeptId = 99, ManagerId = 2 } // Dept 99 does not exist (Orphan)
        };

        // ... (Join Examples Below) ...
    }
}

```

---

### 2. Inner Join (Standard Join)

Fetches only records that have matching keys in both lists.

**Query Syntax**

```csharp
// "join" keyword matches DeptId in employees to Id in departments
var innerJoinQuery = from e in employees
                     join d in departments on e.DeptId equals d.Id
                     select new { Employee = e.Name, Dept = d.Name };

```

**Method Syntax**

```csharp
// .Join(innerSource, outerKeySelector, innerKeySelector, resultSelector)
var innerJoinMethod = employees.Join(
    departments,
    e => e.DeptId,      // Key from outer list (employees)
    d => d.Id,          // Key from inner list (departments)
    (e, d) => new { Employee = e.Name, Dept = d.Name } // Result
);

```

---

### 3. GroupJoin

Produces hierarchical data. Takes an outer element and finds *all* matching inner elements as a collection. (e.g., Department -> List of Employees).

**Query Syntax**

```csharp
// "into" keyword groups the matching results into variable 'empGroup'
var groupJoinQuery = from d in departments
                     join e in employees on d.Id equals e.DeptId into empGroup
                     select new {
                         DeptName = d.Name,
                         Employees = empGroup
                     };

```

**Method Syntax**

```csharp
// .GroupJoin(innerSource, outerKey, innerKey, resultSelector)
// The resultSelector receives the Department 'd' and a collection of Employees 'empGroup'
var groupJoinMethod = departments.GroupJoin(
    employees,
    d => d.Id,
    e => e.DeptId,
    (d, empGroup) => new {
        DeptName = d.Name,
        Employees = empGroup
    }
);

```

---

### 4. SelectMany (2 Arguments)

Used to flatten lists or perform Cross Joins. The 2-argument overload allows you to project data from both the "Parent" and the "Child/Sub" item.

**Query Syntax**

```csharp
// Using two "from" clauses.
// Useful for flattening: Department -> FocusAreas
var selectManyQuery = from d in departments
                      from f in d.FocusAreas
                      select new { Dept = d.Name, Area = f };

```

**Method Syntax**

```csharp
// .SelectMany(collectionSelector, resultSelector)
// 1. collectionSelector: returns the list of FocusAreas for a department
// 2. resultSelector: takes the Dept 'd' and the individual FocusArea 'f' to create result
var selectManyMethod = departments.SelectMany(
    d => d.FocusAreas,
    (d, f) => new { Dept = d.Name, Area = f }
);

```

---

### 5. Left Outer Join

Returns all elements from the Left list, and matching elements from the Right. If no match, returns null (or default).

*Logic: Perform a `GroupJoin` and then use `SelectMany` with `DefaultIfEmpty()` on the group.*

**Query Syntax**

```csharp
// 1. Join into 'empGroup'
// 2. Perform a second 'from' (SelectMany) on empGroup.DefaultIfEmpty()
var leftJoinQuery = from d in departments
                    join e in employees on d.Id equals e.DeptId into empGroup
                    from subEmp in empGroup.DefaultIfEmpty() // Use default if list is empty
                    select new {
                        Dept = d.Name,
                        Employee = subEmp != null ? subEmp.Name : "No Employee"
                    };

```

**Method Syntax**

```csharp
// 1. GroupJoin departments with employees
// 2. SelectMany to flatten the group back out
// 3. DefaultIfEmpty() ensures the Left side (Department) stays even if Right side is empty
var leftJoinMethod = departments.GroupJoin(
    employees,
    d => d.Id,
    e => e.DeptId,
    (d, empGroup) => new { d, empGroup }
)
.SelectMany(
    x => x.empGroup.DefaultIfEmpty(),
    (x, subEmp) => new {
        Dept = x.d.Name,
        Employee = subEmp != null ? subEmp.Name : "No Employee"
    }
);

```

---

### 6. Right Outer Join

LINQ does not have a native "Right Join" operator. You simply swap the tables in a Left Join setup.

**Query Syntax**

```csharp
// Exact same syntax as Left Join, just swapped 'employees' to be the primary source
var rightJoinQuery = from e in employees
                     join d in departments on e.DeptId equals d.Id into deptGroup
                     from subDept in deptGroup.DefaultIfEmpty()
                     select new {
                         Employee = e.Name,
                         Dept = subDept != null ? subDept.Name : "No Dept"
                     };

```

**Method Syntax**

```csharp
// Swapped sources: employees.GroupJoin(departments...)
var rightJoinMethod = employees.GroupJoin(
    departments,
    e => e.DeptId,
    d => d.Id,
    (e, deptGroup) => new { e, deptGroup }
)
.SelectMany(
    x => x.deptGroup.DefaultIfEmpty(),
    (x, subDept) => new {
        Employee = x.e.Name,
        Dept = subDept != null ? subDept.Name : "No Dept"
    }
);

```

---

### 7. Full Outer Join

Returns all records when there is a match in either left or right records.
*Logic: `Left Join` UNION `Right Join`.*

**Query Syntax (Mixed)**

```csharp
// 1. Get Left Join Result
var leftSide = from d in departments
               join e in employees on d.Id equals e.DeptId into empGroup
               from subEmp in empGroup.DefaultIfEmpty()
               select new { DeptName = d.Name, EmpName = subEmp?.Name };

// 2. Get Right Join Result (Only the ones missing the left side, to avoid duplicates logic,
//    but Union handles duplicates automatically if the object projection is identical)
var rightSide = from e in employees
                join d in departments on e.DeptId equals d.Id into deptGroup
                from subDept in deptGroup.DefaultIfEmpty()
                select new { DeptName = subDept?.Name, EmpName = e.Name };

// 3. Union
var fullJoinQuery = leftSide.Union(rightSide);

```

**Method Syntax**

```csharp
// Same logic written with extensions
var fullJoinMethod = leftJoinMethod // (Code from Left Join section above)
    .Union(rightJoinMethod);        // (Code from Right Join section above)

```

*(Note: For `.Union` to work perfectly with anonymous types, the property names and types in `new { ... }` must be exactly the same in both queries).*

---

### 8. Self Join

Joining a collection to itself. Common for Parent-Child relationships within one table (e.g., Manager-Employee).

**Query Syntax**

```csharp
// "join" the list 'employees' with itself ('employees')
var selfJoinQuery = from e in employees
                    join m in employees on e.ManagerId equals m.Id
                    select new {
                        Employee = e.Name,
                        Manager = m.Name
                    };

```

**Method Syntax**

```csharp
// Pass 'employees' as both outer and inner source
var selfJoinMethod = employees.Join(
    employees,
    e => e.ManagerId, // Outer Key
    m => m.Id,        // Inner Key
    (e, m) => new {
        Employee = e.Name,
        Manager = m.Name
    }
);

```

---

### 9. Cross Join (Cartesian Product)

Pairs every element of the first sequence with every element of the second sequence.

**Query Syntax**

```csharp
// Multiple "from" clauses without a "where" filter creates a Cross Join
var crossJoinQuery = from d in departments
                     from e in employees
                     select new { d.Name, e.Name };

```

**Method Syntax**

```csharp
// Use SelectMany to project every employee for every department
var crossJoinMethod = departments.SelectMany(
    d => employees,
    (d, e) => new { d.Name, e.Name }
);

```