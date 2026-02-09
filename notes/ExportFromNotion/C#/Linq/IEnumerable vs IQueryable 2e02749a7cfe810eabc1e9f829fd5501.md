# IEnumerable vs IQueryable

This is the most critical architectural concept in C# data access. Understanding this distinction is what separates a developer who makes apps that **crash** under load from a developer whose apps **scale** effortlessly.

Here is the deep dive into `IEnumerable<T>` vs. `IQueryable<T>`.

---

### **1. The Hierarchy (The First Surprise)**

Before comparing them, you must understand their relationship.

```csharp
public interface IQueryable<T> : IEnumerable<T>, IQueryable
{
    // ...
}

```

**`IQueryable` inherits from `IEnumerable`.**

- This means anything you can do with an `IEnumerable` (iterate, loop), you can *technically* do with an `IQueryable`.
- However, **how** they work "under the hood" is completely different.

---

### **2. IEnumerable<T>: The In-Memory Iterator**

### **What it is:**

- **Namespace:** `System.Collections.Generic`
- **Target:** Collections stored in **Local Memory** (List, Array, HashSet).
- **Execution Location:** The **Client** (Your Web Server/Application).
- **Underlying Logic:** It uses **Delegates** (`Func<T, bool>`).

### **How it works:**

When you write a LINQ query on an `IEnumerable`, the C# compiler compiles your Lambda Expression into actual executable C# code (a method). When you iterate:

1. The data is loaded into RAM.
2. Your compiled C# function runs against every single item in that list to see if it matches.

### **The Database Scenario (The "Select * Pitfall"):**

If you use `IEnumerable` against a database context (EF Core):

1. EF Core generates a SQL query to select **ALL** rows (`SELECT * FROM Users`).
2. **All** rows are sent over the network to your server.
3. Your server loads **All** rows into RAM.
4. Your server runs the filter to discard the ones you don't need.

---

### **3. IQueryable<T>: The Expression Builder**

### **What it is:**

- **Namespace:** `System.Linq`
- **Target:** Remote Data Sources (SQL Databases, XML APIs, Cloud Services).
- **Execution Location:** The **Server** (The SQL Database Engine).
- **Underlying Logic:** It uses **Expression Trees** (`Expression<Func<T, bool>>`).

### **How it works:**

When you write a LINQ query on an `IQueryable`, the C# compiler **does NOT** compile your Lambda into executable code. Instead, it compiles it into a **Data Structure** (an Abstract Syntax Tree) that *describes* your code.

1. The `QueryProvider` (part of Entity Framework) looks at this tree.
2. It translates that tree into the target language (e.g., T-SQL).
3. It sends the optimized SQL to the database.
4. Only the matching rows are returned over the network.

---

### **4. Deep Dive: Func vs. Expression (The Internals)**

This is the technical differentiator. Look at the signatures of the `.Where()` method for both:

### **IEnumerable uses Delegates:**

```csharp
// Accepts executable code (a function)
public static IEnumerable<T> Where<T>(this IEnumerable<T> source, Func<T, bool> predicate);

```

- `Func<T, bool>`: "Here is a literal block of C# code. Run it."

### **IQueryable uses Expressions:**

```csharp
// Accepts a description of code
public static IQueryable<T> Where<T>(this IQueryable<T> source, Expression<Func<T, bool>> predicate);

```

- `Expression<Func<T, bool>>`: "Here is a tree of objects representing code. Logic: 'Property Id' -> 'GreaterThan' -> 'Constant 5'. Translate this to SQL."

---

### **5. The "Evidence": Comparing SQL Output**

Let's assume we have a table `Users` with 1 million rows. We want users over age 18.

### **Scenario A: Using IEnumerable (Disaster)**

```csharp
// The ToList() forces immediate execution, converting IQueryable to IEnumerable (RAM)
IEnumerable<User> query = dbContext.Users.ToList().Where(u => u.Age > 18);

/*
   SQL GENERATED:
   SELECT * FROM Users;

   PERFORMANCE:
   1. DB reads 1,000,000 rows.
   2. Network transfers 500MB of data.
   3. Server App uses 500MB RAM.
   4. Server CPU loops 1,000,000 times.
*/

```

### **Scenario B: Using IQueryable (Optimized)**

```csharp
// No execution yet. Logic is being built up.
IQueryable<User> query = dbContext.Users.Where(u => u.Age > 18);

// Execution happens here (upon iteration or ToList)
var result = query.ToList();

/*
   SQL GENERATED:
   SELECT [Id], [Name], [Age] FROM Users WHERE [Age] > 18;

   PERFORMANCE:
   1. DB indexes find matching rows (fast).
   2. Network transfers only result data (small).
   3. Server App uses minimal RAM.
*/

```

---

### **6. When does IQueryable become IEnumerable?**

This is known as **Materialization**. It is the moment you switch from "Building a Query" to "Executing the Query".

This happens when you call:

1. `.ToList()`
2. `.ToArray()`
3. `.AsEnumerable()`
4. `foreach (var x in query)`
5. Aggregates like `.Count()`, `.First()`, `.Sum()`

**Warning: "The Client-Side Evaluation Trap"**
Sometimes you *must* switch to `IEnumerable`.
Why? Because SQL doesn't know how to do everything C# can do.

```csharp
public bool ValidateKey(string key) { ... complex c# logic ... }

// ❌ CRASH (in modern EF Core) or BAD PERFORMANCE
// SQL Server doesn't know what "ValidateKey" means. It cannot translate this.
var q = dbContext.Users.Where(u => ValidateKey(u.SecretKey));

```

**The Fix:**
You fetch the data you *can* filter via SQL first, bring it into memory, and *then* run the complex C# logic.

```csharp
var q = dbContext.Users
    .Where(u => u.CreatedYear > 2020) // Runs in SQL (IQueryable)
    .AsEnumerable()                   // Switches context to RAM (Materializes)
    .Where(u => ValidateKey(u.SecretKey)); // Runs in C# (IEnumerable)

```

### **Summary Table**

| Feature | **IEnumerable<T>** | **IQueryable<T>** |
| --- | --- | --- |
| **Executes On** | Client (App Server / Memory) | Server (Database Engine) |
| **Logic** | Executes a `Delegate` (Func) | Parses an `Expression Tree` |
| **Usage** | Lists, Arrays, Parsed Data | Entity Framework, SQL, Linq-to-XML |
| **Filtering** | Fetches all, filters locally | Filters at source, fetches matches |
| **Extensibility** | Supports valid C# methods | Only supports logic SQL understands |
| **Performance** | Good for in-memory lists | Critical for Databases |

**Which one do I choose?**

- If working with **Database/Remote Data**: ALWAYS keep it `IQueryable` as long as possible (until the very last moment).
- If working with **Lists/Arrays** already in memory: Use `IEnumerable`.

# Query Extension

### **1. Immediate Operators (Materialization)**

These are the methods that say: *"Stop planning, start doing."* They force the query to execute and return a result (not a query).

**Common Examples:**

- `.ToList()`, `.ToArray()`, `.ToDictionary()`
- `.Count()`, `.Any()`, `.All()`
- `.First()`, `.Single()`, `.Max()`

### **Is it part of `IEnumerable` vs `IQueryable`?**

Yes, but the implementation is totally different:

**A. On IEnumerable (The Memory Loop)**

- **What happens:** When you call `.Count()`, C# immediately grabs the iterator, runs a `foreach` loop over the objects in RAM, increments a counter integer, and returns it.
- **Cost:** Linear Scan (O(n)).

**B. On IQueryable (The SQL Executor)**

- **What happens:** When you call `.Count()`, EF Core looks at the Expression Tree, translates it to `SELECT COUNT(*) FROM Table`, sends it to the DB, and waits for the single integer result.
- **Cost:** Database Index Lookup (very fast).

### **The "Trap": You cannot extend after execution**

Once you use an immediate operator, you leave the "Query World" and enter the "Result World".

```csharp
// Step 1: Query (IQueryable)
var query = context.Users.Where(u => u.Age > 18);

// Step 2: Immediate Operator (Triggers SQL)
// 'list' is now List<User> (InMemory collection)
var list = query.ToList();

// Step 3: Extending?
// This runs in MEMORY, not SQL. The DB work is already done.
var filteredAgain = list.Where(u => u.Name == "Bob");
```

---

### **2. Extending Queries (Deferred Execution)**

This is the ability to build a query step-by-step. Because LINQ uses **Deferred Execution**, writing a query does not run it. This allows you to stack filters dynamically.

### **How it works**

You can modify an `IQueryable` or `IEnumerable` variable as many times as you want. You are essentially modifying the "Question" before you ask it.

```csharp
// 1. Base Query
IQueryable<User> query = context.Users;

// 2. Condition: User filters by Active
if (shouldFilterActive)
{
    query = query.Where(u => u.IsActive); // Extends the Expression Tree
}

// 3. Condition: User searches by Name
if (!string.IsNullOrEmpty(searchText))
{
    query = query.Where(u => u.Name.Contains(searchText)); // Adds "AND Name LIKE..."
}

// 4. Execution
// The final SQL will contain ALL the Where clauses added above.
var results = query.ToList();

```

### **The difference in implementation**

**A. Extending `IEnumerable` (The Onion)**
Think of this like wrapping an onion.

- Original List -> Wrapped in `Where` Iterator -> Wrapped in `Select` Iterator.
- When you finally loop, the outer iterator calls the inner one, which calls the list. It’s a **chain of delegates**.

**B. Extending `IQueryable` (The Puzzle)**
Think of this like building a sentence.

- Start with "SELECT *".
- `.Where(...)` adds "WHERE ...".
- `.OrderBy(...)` adds "ORDER BY ...".
- Every time you extend the query, you are just appending nodes to the **Expression Tree** (the AST). The SQL isn't generated until the very end.

---

### **Technical Note: "Where do these methods live?"**

You asked if they are "part of" the interfaces. Technically, **No**.

If you look at the C# source code for `IQueryable<T>`, it is actually empty!

```csharp
public interface IQueryable<T> : IEnumerable<T>, IQueryable { }

```

**Where are `.Where` and `.Select`?**
They are **Extension Methods** located in static classes:

1. **For IEnumerable:** `System.Linq.Enumerable` class.
    - Takes `Func` (code) as parameters.
2. **For IQueryable:** `System.Linq.Queryable` class.
    - Takes `Expression` (data) as parameters.

**Why does this matter?**
This is why you need `using System.Linq;` at the top of your file. Without that namespace, the compiler doesn't know these extension methods exist, and your interfaces look empty.