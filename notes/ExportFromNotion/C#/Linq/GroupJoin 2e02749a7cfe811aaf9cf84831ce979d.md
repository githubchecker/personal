# GroupJoin

`GroupJoin` is the LINQ equivalent of a **Left Outer Join** that produces a **hierarchical result**.

Unlike a standard `Join` (which produces a flat list of matching pairs), `GroupJoin` preserves every element of the **Outer** sequence and correlates it with a **List (IEnumerable)** of matching elements from the **Inner** sequence.

Here is the in-depth breakdown of Variable Scopes for both syntaxes.

---

### **The Scenario**

We have **Categories** (Outer) and **Products** (Inner).

- **Electronics**: contains Laptop, Mouse.
- **Books**: contains Novel.
- **EmptyCat**: contains nothing.

```csharp
class Category { public int Id; public string Name; }
class Product  { public int Id; public string Name; public int CatId; }

```

---

### **1. Query Syntax (`join ... into ...`)**

This is the most readable way to use GroupJoin. The magic keyword is `into`.

### **The Scope Rules**

1. **Outer Range Variable (`c`)**: Remains in scope for the entire operation. You can access the Category object in the `select`.
2. **Inner Range Variable (`p`)**: exist **ONLY** inside the `on` clause.
3. **The Group Variable (`prodGroup`)**: Once you type `into prodGroup`, the variable `p` **disappears** from scope. `prodGroup` becomes a variable representing `IEnumerable<Product>`.

### **Code Visualization**

```csharp
var query = from c in categories           // 1. Define Outer (c)
            join p in products             // 2. Define Inner (p)
            on c.Id equals p.CatId         // 3. Match keys using (c) and (p)
            into prodGroup                 // 4. SAVE matches into a new variable

            // --- SCOPE LINE ---
            // 'p' is now DEAD. It cannot be used here.
            // 'c' is ALIVE (The single Category).
            // 'prodGroup' is ALIVE (List<Product> containing matches).

            select new
            {
                CategoryName = c.Name,
                // We operate on the LIST of products here
                ProductCount = prodGroup.Count(),
                Products = prodGroup // The collection itself
            };

```

**Scope Takeaway:** You cannot say `select p.Name` because `p` has been consumed and packaged into the list `prodGroup`.

---

### **2. Fluent (Method) Syntax**

Method syntax is more verbose but explicitly shows the types passed into the lambda expressions.

### **Signature Breakdown**

`GroupJoin` takes 4 arguments. The 4th argument (the **Result Selector**) defines the variable scope for the output.

```csharp
outer.GroupJoin(
    inner,
    outerKeySelector,
    innerKeySelector,
    resultSelector   // (outerItem, innerList) => result
)

```

### **The Scope Rules**

1. **Result Selector Parameters**: The lambda requires two parameters:
    - **Param 1 (`cat`)**: The single element from the Outer source.
    - **Param 2 (`prods`)**: The **collection** `IEnumerable<TInner>` of matching items.
2. **No Direct Inner Item Access**: Just like Query syntax, you do not have access to a single Product object here, only the list of products associated with that category.

### **Code Visualization**

```csharp
var methodQuery = categories.GroupJoin(
    products,                      // Inner sequence
    c => c.Id,                     // Outer Key
    p => p.CatId,                  // Inner Key
    (cat, prods) => new            // RESULT SELECTOR (Scope defined here)
    {
        // 'cat' is the Category instance
        CategoryName = cat.Name,

        // 'prods' is IEnumerable<Product>
        // Even if no matches are found, 'prods' is NOT null. It is an empty list.
        TopProducts = prods.OrderBy(p => p.Name).Take(5)
    }
);

```

---

### **3. Advanced Scope: The "SelectMany" Flattening**

*Wait, what if I want to access properties of the inner variable individually, like a SQL Left Join (Flattened)?*

This is where beginners get stuck. Since `GroupJoin` returns a List inside a List, you must use `SelectMany` (or a second `from` in query syntax) to unpack it.

### **Query Syntax Flattening**

To bring the inner variable back into scope effectively, we iterate the group using `from` again.

```csharp
var flatQuery = from c in categories
                join p in products on c.Id equals p.CatId into prodGroup // Grouping

                from item in prodGroup.DefaultIfEmpty() // Unpacking (Left Join logic)

                // --- SCOPE UPDATE ---
                // 'c': Still alive.
                // 'item': Alive! It represents a single Product (or null if empty).

                select new
                {
                    CatName = c.Name,
                    ProdName = item?.Name ?? "No Product" // Handling null
                };

```

### **Summary of Variable Scopes**

| Syntax | Phase | Variable | Type | Scope Status |
| --- | --- | --- | --- | --- |
| **Query** | Before `into` | `c` (Outer) | `Category` | Active |
|  | Before `into` | `p` (Inner) | `Product` | Active (Only for matching) |
|  | After `into` | `c` (Outer) | `Category` | **Active** |
|  | After `into` | `p` (Inner) | -- | **Gone** (Out of Scope) |
|  | After `into` | `prodGroup` | `IEnumerable<Product>` | **Active** |
| **Method** | Result Selector | Arg 1 | `Category` | Active |
|  | Result Selector | Arg 2 | `IEnumerable<Product>` | Active |