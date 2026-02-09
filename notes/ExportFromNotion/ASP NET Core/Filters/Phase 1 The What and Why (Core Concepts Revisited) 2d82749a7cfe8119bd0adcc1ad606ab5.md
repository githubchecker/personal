# Phase 1: The "What" and "Why" (Core Concepts Revisited)

This is the foundation. If you don't understand the "Why", you will use filters incorrectly.

---

### **1. Filters and Cross-Cutting Concerns**

**(Microsoft Docs Link:** [*Introduction to filters*](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters))

The core problem filters solve is **Cross-Cutting Concerns**. These are behaviors required by many parts of your application, but they are not part of the core business logic.

**Imagine you run a restaurant.**

| Business Logic | Cross-Cutting Concerns |
| --- | --- |
| Cook the steak (The Controller Action) | 1. Is the customer over 21? (**Authorization**) |
| Prepare the salad | 2. Is our kitchen currently open? (**Resource Check**) |
| Bill the customer | 3. Did they order from the menu? (**Model Validation**) |
|  | 4. What if a fire starts? (**Exception Handling**) |
|  | 5. Log the order details (**Logging**) |

If you put all the "cross-cutting" logic inside the "cook steak" method, it becomes a mess. A filter allows you to extract these checks into reusable, external components.

**The benefits of this separation are huge:**

1. **DRY (Don't Repeat Yourself):** Write the "Age Check" logic once. Apply it to every alcoholic drink on the menu.
2. **Clean Code:** Your controller actions become incredibly clean. They only contain business logic.
3. **Testability:** You can unit test your `AgeCheckFilter` in isolation without needing to test the entire `CookSteak` process.

---

### **2. The [ASP.NET](http://asp.net/) Core Request Pipeline**

A filter is not middleware. Middleware is lower-level and dumber; it only knows about the raw HTTP request. Filters are higher-level; they know about MVC concepts like which `Action` is about to run.

**The Full Journey of a Request (Simplified):**

```
 [Request Arrives]
      |
      V
 [Middleware #1 (Static Files)] -> serve index.html? (No, next)
      |
      V
 [Middleware #2 (Routing)] -> Ah, this matches /WeatherForecast! (Okay, next)
      |
      V
 [Middleware #3 (Authentication)] -> Token looks good. I'll create User object. (Okay, next)
      |
      V
 ========================= MVC STARTS HERE ============================
      |
      V
 [Authorization Filter] -> Does this User have the "Admin" role?
      |
      V
 [Resource Filter] -> Is this in the Cache? (If so, return and stop)
      |
      V
 [Model Binding] -> Map JSON to C# WeatherForecast object.
      |
      V
 [Action Filter] -> Is ModelState Valid?
      |
      V
 --- [YOUR ACTION METHOD RUNS] --- `public IActionResult Get() { ... }`
      |
      V
 [Action Filter] (On its way OUT) -> Log that the action finished.
      |
      V
 [Result Filter] -> Add a custom header to the HTTP response.
      |
      V
 ========================== MVC ENDS HERE =============================
      |
      V
 [Response goes back through middleware in reverse order...]

```

---

### **3. The Five Filter Types (Taxonomy)**

This is the most critical part of Phase 1. Memorize this table.

| Filter Type | Question it Answers | Typical `[Attribute]` Name | Short-Circuits? (Stops the Request) |
| --- | --- | --- | --- |
| **Authorization** | "Is this user allowed to run this?" | `[Authorize]` | **Yes** (Returns `401 Unauthorized` or `403 Forbidden`) |
| **Resource** | "Can I serve this resource cheaper/faster, or do I need to prepare something?" | Custom (e.g., `[Cache]`) | **Yes** (Returns a cached result) |
| **Action** | "Is the data for this method correct, and can I do anything before it runs?" | Custom (e.g., `[ValidateModel]`) | **Yes** (Returns `400 Bad Request`) |
| **Exception** | "An error happened inside the action. How do I handle it gracefully?" | Custom (e.g., `[GlobalExceptionHandler]`) | **N/A** (Runs *instead* of a normal response) |
| **Result** | "How can I change the final response before it's sent to the client?" | Custom (e.g., `[AddHeader]`) | **No** (It just modifies the result) |

---

### **4. Key Interfaces (The Contracts)**

Each filter type maps to one or more C# interfaces.

- `IAuthorizationFilter`
- `IResourceFilter`, `IAsyncResourceFilter`
- `IActionFilter`, `IAsyncActionFilter`
- `IExceptionFilter`, `IAsyncExceptionFilter`
- `IResultFilter`, `IAsyncResultFilter`

**Async vs. Sync:**

- Use the **Async** version if your filter needs to perform asynchronous work (e.g., making a database call).
- **Best Practice:** Always default to `IAsync...Filter`. It's safer.

---

### **5. Filter Order (A Deeper Look)**

**(Microsoft Docs Link:** [*Filter execution order](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters#filter-execution-order))*

If you apply multiple filters, they run in a specific sequence. This sequence can be controlled using the `IOrderedFilter` interface or the `Order` property on built-in attributes.

**Order goes from Outside -> In, then In -> Out.**

Example:

```csharp
[Order(1)]
public class OuterFilter : IActionFilter { ... }

[Order(2)]
public class InnerFilter : IActionFilter { ... }

```

**Execution flow:**

1. OuterFilter `OnActionExecuting`
2. InnerFilter `OnActionExecuting`
3. **ACTION RUNS**
4. InnerFilter `OnActionExecuted`
5. OuterFilter `OnActionExecuted`

This nesting behavior is crucial for features like database transactions, where you must *start* the transaction in the "outer" filter and *commit* it in the same filter on the way out.

### **Summary of Phase 1**

- Filters solve **Cross-Cutting Concerns**.
- They run **inside** the MVC pipeline, after routing.
- You must choose the correct **Filter Type** for the job (Auth, Resource, Action, etc.).
- Execution flows like an **Onion**, and this order is predictable.

Are you ready to dive into **Phase 2: Implementation Details** (How to actually write and register these filters, and a deep-dive into Dependency Injection)?