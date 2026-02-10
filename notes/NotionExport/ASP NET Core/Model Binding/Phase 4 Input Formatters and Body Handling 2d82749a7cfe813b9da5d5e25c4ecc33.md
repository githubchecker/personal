# Phase 4: Input Formatters and Body Handling

Of course. This phase dives into the mechanics of how the raw request body is interpreted by the framework. Mastering this is key to handling custom data formats and specific security scenarios.

**(Microsoft Docs Entry Point:** [*Format response data in ASP.NET Core Web API*](https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/formatting) - concepts are similar for input)*

---

### **1. Input Formatters (`IInputFormatter`)**

An **Input Formatter** is a component that deserializes the request body into a C# object. The framework selects which formatter to use based on the `Content-Type` header of the incoming request.

### **Built-in Formatters:**

By default, [ASP.NET](http://asp.net/) Core includes formatters for:

- **`application/json`**: `SystemTextJsonInputFormatter` (or `NewtonsoftJsonInputFormatter` if configured).
- **`application/xml`**: `XmlSerializerInputFormatter` or `DataContractSerializerInputFormatter` (if `AddXmlSerializerFormatters()` is called).
- **`multipart/form-data`**: Handles form data for `[FromForm]`.

### **How Selection Works:**

1. **Request:** A client sends a `POST` request with `Content-Type: application/json`.
2. [**ASP.NET](http://asp.net/) Core:** The framework looks at its registered input formatters.
3. **Match:** It finds the `SystemTextJsonInputFormatter`, which states it can handle `application/json`.
4. **Execute:** The framework passes the request body stream to this formatter, which uses `System.Text.Json.JsonSerializer` to deserialize the JSON into your DTO.

### **Creating a Custom Input Formatter**

This is an advanced technique used when you need to support a custom media type.

**The Scenario:**
You need to support a legacy `text/csv` format for creating a batch of users.

**Step 1: Create the Formatter Class**

```csharp
using Microsoft.AspNetCore.Mvc.Formatters;
using System.Text;

public class CsvInputFormatter : TextInputFormatter
{
    public CsvInputFormatter()
    {
        SupportedMediaTypes.Add("text/csv");
        SupportedEncodings.Add(Encoding.UTF8);
        SupportedEncodings.Add(Encoding.Unicode);
    }

    protected override bool CanReadType(Type type)
    {
        // This formatter can only deserialize into a List of a specific DTO
        return type == typeof(List<CreateUserDto>);
    }

    public override async Task<InputFormatterResult> ReadRequestBodyAsync(InputFormatterContext context, Encoding encoding)
    {
        var httpContext = context.HttpContext;
        using var reader = new StreamReader(httpContext.Request.Body, encoding);

        var userList = new List<CreateUserDto>();
        string line;

        // Skip header row
        await reader.ReadLineAsync();

        while ((line = await reader.ReadLineAsync()) != null)
        {
            var parts = line.Split(',');
            if (parts.Length == 2)
            {
                userList.Add(new CreateUserDto { Email = parts[0], Password = parts[1] });
            }
        }

        return await InputFormatterResult.SuccessAsync(userList);
    }
}

```

**Step 2: Register in `Program.cs`**

```csharp
builder.Services.AddControllers(options =>
{
    // Add our custom formatter to the list of available formatters
    options.InputFormatters.Insert(0, new CsvInputFormatter());
});
```

Now, if a client sends a request with `Content-Type: text/csv`, your custom formatter will be invoked automatically.

---

### **2. The `[FromBody]` Limitation**

This is a fundamental rule in [ASP.NET](http://asp.net/) Core that often confuses beginners.

**The Rule:** An action method can have at most **one** parameter decorated with the `[FromBody]` attribute.

**Why?**
The request body is a **forward-only stream**. Once it's read and deserialized into an object, it cannot be "rewound" and read a second time to deserialize into another object. The framework enforces this limitation to prevent unpredictable behavior and promote clear API design.

**The "Bad" Way (This will fail at runtime):**

```csharp
[HttpPost]
public IActionResult CreateProductAndSupplier(
    [FromBody] CreateProductDto product,
    [FromBody] CreateSupplierDto supplier) // <-- ERROR: Can't have two
{
    // ...
}

```

**The "Expert" Way (Create a Composite DTO):**
The correct approach is to create a single DTO that encapsulates all the data you expect in the body.

```csharp
public class ProductAndSupplierRequestDto
{
    public CreateProductDto Product { get; set; }
    public CreateSupplierDto Supplier { get; set; }
}

[HttpPost]
public IActionResult CreateProductAndSupplier([FromBody] ProductAndSupplierRequestDto request)
{
    var product = request.Product;
    var supplier = request.Supplier;
    // ...
}

```

---

### **3. Reading the Raw Body Stream**

Sometimes you need to bypass model binding and formatters entirely.

**The Scenario:**
You are implementing a webhook endpoint for a service like Stripe or GitHub. To verify the request's authenticity, you must compute an HMAC hash of the **raw, unmodified request body** and compare it to a signature provided in a header (`X-Stripe-Signature`).

If you use `[FromBody]`, the JSON formatter reads and buffers the stream, potentially changing its encoding or whitespace, which would invalidate the signature.

**The Solution:** Read `Request.Body` or `Request.BodyReader` directly.

**The Controller Action:**

```csharp
[HttpPost("stripe-webhook")]
public async Task<IActionResult> StripeWebhook()
{
    // 1. Get the signature from the header
    var signature = Request.Headers["Stripe-Signature"];
    string requestBody;

    // 2. Read the raw body into a string
    using (var reader = new StreamReader(Request.Body, Encoding.UTF8))
    {
        requestBody = await reader.ReadToEndAsync();
    }

    // 3. Verify the signature (pseudo-code)
    var webhookSecret = "whsec_...";
    var isValid = StripeSignatureVerifier.Verify(requestBody, signature, webhookSecret);

    if (!isValid)
    {
        return BadRequest("Invalid signature.");
    }

    // 4. Now that it's verified, you can manually deserialize the body string
    var stripeEvent = JsonSerializer.Deserialize<StripeEvent>(requestBody);

    // ... process the event ...

    return Ok();
}

```

To enable this, you must tell the framework not to touch the body. The simplest way is to have no parameters in your action method.

### **Summary of Phase 4**

- **Input Formatters** are the components responsible for deserializing the request body based on the `Content-Type` header.
- You can create **custom formatters** to support non-standard media types like CSV or protobuf.
- You can only have **one `[FromBody]` parameter** per action. Use composite DTOs to combine multiple inputs.
- For security-sensitive operations like webhook signature validation, **bypass model binding** and read the raw request body stream directly to ensure its integrity.

Are you ready to proceed to the final **Phase 5: Production & Security Considerations**, where we'll cover topics like over-posting and parameter binding nuances?

## **`IInputFormatter`  vs `IValueProvider`**

Here is the definitive difference between a custom `IValueProvider` and a custom `IInputFormatter`.

---

### **1. `IInputFormatter` (The Body Deserializer)**

### **Its Single Job**

To take the **entire raw request body stream** and deserialize it into a single C# object.

### **Its Trigger**

It is chosen and executed based on the `Content-Type` header of the request (e.g., `application/json`, `application/xml`, `text/csv`).

### **Does it only work on `[FromBody]`?**

**YES. Absolutely.** An `IInputFormatter` is invoked *only when* the model binding system needs to populate a parameter marked with `[FromBody]` (or a complex type that is inferred to be from the body).

### **Analogy**

The `IInputFormatter` is a specialized **translator**. It knows how to read a specific language (JSON, XML, Protobuf) and translate the entire book (the request body) into a single, structured object (`CreateProductDto`). It does not care about individual words (query parameters) or notes in the margin (headers).

---

### **2. `IValueProvider` (The Data Source)**

### **Its Single Job**

To tell the model binding system **where to find raw, string-based key-value data**. It does not deserialize complex objects. It just provides a way to look up simple values.

### **Its Trigger**

Value Providers are consulted for **almost every parameter** that is *not* `[FromBody]`. The model binder asks each registered `IValueProvider` in order: "Do you have a value for the key `id`?" or "Do you have a value for the key `searchTerm`?"

- `QueryStringValueProvider` looks in the query string.
- `RouteValueProvider` looks in the route data.
- `HeaderValueProvider` looks in the headers.

### **Why would you create a custom one?**

You create a custom `IValueProvider` when your data lives in a place the built-in providers don't know about.

**Scenario:** A client is sending an encrypted value in a custom header, `X-Encrypted-Payload`. The header contains a JWE (JSON Web Encryption) token.

Your custom `JweValueProvider` would:

1. Find the `X-Encrypted-Payload` header.
2. Decrypt the JWE token.
3. The decrypted content is a simple JSON object: `{ "userId": 123, "tenantId": "abc" }`.
4. It would then expose these values. When the model binder asks for `"userId"`, your provider would return `"123"`.

The model binder would then handle the final conversion of the string `"123"` to the `int` parameter of your action.

---

### **The Definitive Difference: `IInputFormatter` vs. `IModelBinder` vs. `IValueProvider`**

| Feature | `IInputFormatter` (The Body Translator) | `IModelBinder` (The Parameter Assembler) | `IValueProvider` (The Data Locator) |
| --- | --- | --- | --- |
| **Primary Job** | To deserialize the **entire HTTP request body** into a single, complete C# object. | To construct the value for a **single C# action method parameter** by orchestrating data from one or more sources. | To teach the model binding system **where to find raw, key-value data** from a new, non-standard source. |
| **Scope of Work** | **Macro-level:** It operates on the entire request body stream as a whole. | **Micro-level:** It is focused on populating one specific parameter at a time. | **Source-level:** It operates before the binder, providing a new location to search for data. |
| **Primary Input Data** | The raw `HttpRequest.Body` (`Stream`). | Any part of the `HttpContext` is available, primarily using `ValueProviders` to get data from the Route, Query, Form, or Headers. | A specific part of the `HttpContext`, like a custom cookie or header format. |
| **Output** | A single, fully deserialized object (e.g., a `ProductDto`). The result is a success or failure for the whole object. | The final, correctly typed value for one parameter (e.g., a `List<int>`). The result can be a successfully bound value or an error added to `ModelState`. | Raw string values for specific keys (e.g., providing the value `"123"` for the key `"userId"`). |
| **How it's Triggered** | Based on the `Content-Type` header of the request, but **only** for a parameter marked with **`[FromBody]`**. | By applying the `[ModelBinder]` attribute to a specific action parameter or by registering it for a specific type. | Registered globally in `Program.cs`. It is consulted by the model binding system for nearly **every parameter** *not* marked `[FromBody]`. |
| **Typical Use Case** | You need to support a new data serialization format for your entire request body, like **Protocol Buffers (`application/x-protobuf`)**, **MessagePack**, or a custom `text/csv` format. | The framework's default binding rules for a specific parameter are not sufficient. Classic example: binding a comma-separated string (`?ids=1,2,3`) from the query into a `List<int>`. | Your data is located in a non-standard place. Example: Reading configuration values from an **encrypted cookie** or a base64-encoded header and making them available to the model binder as if they were query parameters. |
| **Key Limitation** | It is **only for the request body**. It has no knowledge of Route, Query, or Header data. You can only have one `[FromBody]` parameter, so only one formatter runs per request. | While it *can* read the request body, doing so is complex and dangerous, as the body is a forward-only stream. It can conflict with `IInputFormatter`. Its main job is to work with key-value sources. | It only **provides raw strings**. It is not responsible for converting `"123"` into an `int`. The model binder does that final conversion after getting the value from the provider. |
| **When to Choose** | **Choose this when:** You are defining an API contract that uses a specific, non-JSON format for `POST`/`PUT` requests and want it to work seamlessly with `[FromBody]`. | **Choose this when:** You need custom logic to build a *single parameter* from the URL or query string in a way the default binder cannot. It's about custom parsing and construction for one piece of the puzzle. | **Choose this when:** Your input data isn't in the route, query, or form. You need to teach the framework about a **new source** of key-value data. This is the rarest of the three to implement. |

---

### **Practical Scenario: Putting It All Together**

Imagine an incoming request:
`POST /api/products?extra-ids=4,5,6Content-Type: application/x-protobufX-Encrypted-Session: [some_encrypted_base64_string]`
Body: `[Binary Protobuf Data]`

And your action method:

```csharp
public IActionResult Create(
    [FromBody] ProductDto product, // Needs IInputFormatter
    [FromQuery] [ModelBinder(typeof(CommaBinder))] List<int> extraIds, // Needs IModelBinder
    [FromEncryptedSession] int tenantId // Needs a custom IValueProvider
)

```

1. **`IValueProvider` (`FromEncryptedSession`) runs:** It reads the `X-Encrypted-Session` header, decrypts it, finds a `tenantId` key, and provides the raw string value to the model binding system.
2. **`IInputFormatter` (`ProtobufInputFormatter`) runs:** It sees `[FromBody]` and `Content-Type: application/x-protobuf`. It reads the entire request body stream and deserializes it into the `ProductDto` object.
3. **`IModelBinder` (`CommaBinder`) runs:** It is assigned to the `extraIds` parameter. It asks the `QueryStringValueProvider` for the value of `"extra-ids"` (`"4,5,6"`), then splits and parses it into a `List<int>`.

Each component has a distinct, well-defined role in populating the final action method parameters.

---

### **1. Can you have multiple `[ModelBinder]` attributes on the same action method?**

**Yes, absolutely.**

Each `[ModelBinder]` attribute is scoped to a **single parameter**. Since an action method can have multiple parameters, each of those parameters can have its own, completely independent model binder.

This is a very common and powerful pattern.

### **The Scenario**

Imagine an endpoint that needs to process two different, custom-formatted inputs from the query string.

- A comma-separated list of integer IDs (`?ids=1,2,3`).
- A base64-encoded JSON object representing filter criteria (`?filter=eyJuYW1lIjoiV2lkZ2V0In0=`).

**The Action Method:**

```csharp
[HttpGet("search")]
public IActionResult Search(
    // Binder #1: This will be handled by your custom CommaSeparatedListBinder.
    [FromQuery(Name = "ids")]
    [ModelBinder(typeof(CommaSeparatedListBinder))]
    List<int> productIds,

    // Binder #2: This will be handled by a different custom binder.
    [FromQuery(Name = "filter")]
    [ModelBinder(typeof(Base64JsonBinder<ProductFilter>))]
    ProductFilter filterCriteria
)
{
    // By the time this code runs:
    // 'productIds' is a populated List<int>.
    // 'filterCriteria' is a fully deserialized ProductFilter object.

    return Ok(new { Ids = productIds, Criteria = filterCriteria });
}

```

**How it Works:**

1. When the model binding system starts processing the request, it looks at the `Search` method's parameters one by one.
2. For the `productIds` parameter, it sees the `[ModelBinder(typeof(CommaSeparatedListBinder))]` attribute and invokes an instance of that binder to produce the `List<int>`.
3. For the `filterCriteria` parameter, it sees `[ModelBinder(typeof(Base64JsonBinder<ProductFilter>))]` and invokes an instance of *that* binder. This binder's logic would find the `filter` query parameter, decode it from base64, and then deserialize the resulting JSON string into a `ProductFilter` object.

Each model binder works in isolation on its assigned parameter. You can mix and match as many as you need.

---

### **2. Can a Custom `IModelBinder` use a Custom `IValueProvider`?**

**Yes, and this is a perfect example of the pipeline's composability.** This is how you can create very powerful and clean input processing logic.

The `IModelBinder` does not care *where* the raw values come from. It gets them from an abstraction called the `ValueProviderFactory`, which is a collection of all the registered `IValueProvider`s.

If you create and register a custom `IValueProvider`, it automatically becomes available to **all** model binders (both built-in and custom).

### **The Scenario**

Let's combine the concepts. We need to get a `tenantId` from a custom, encrypted cookie. Then, we need to use a custom model binder to take that `tenantId` and a `userId` from the query string and combine them into a single `UserContext` object.

**The Goal:**

- Request URL: `GET /api/documents?userId=5`
- Request Cookie: `my-app-session: [encrypted_string_containing_tenantId_123]`
- Action Parameter: `UserContext context`
- Final Object: `UserContext { TenantId = 123, UserId = 5 }`

**Step 1: Create the Custom `IValueProvider`**
This provider's only job is to decrypt the cookie and expose the `tenantId` value.

```csharp
// This provider knows how to read our specific cookie.
public class EncryptedCookieValueProvider : IValueProvider
{
    // ... logic to decrypt the cookie and expose a 'tenantId' key ...
}

public class EncryptedCookieValueProviderFactory : IValueProviderFactory
{
    public Task CreateValueProviderAsync(ValueProviderFactoryContext context)
    {
        // Adds our provider to the list of available providers.
        context.ValueProviders.Add(new EncryptedCookieValueProvider(context.ActionContext.HttpContext));
        return Task.CompletedTask;
    }
}

```

**Step 2: Register the `IValueProviderFactory` in `Program.cs`**
This makes the new value provider available to the entire application.

```csharp
builder.Services.AddControllers(options =>
{
    // Add our custom factory to the list of places the model binder looks for data.
    options.ValueProviderFactories.Add(new EncryptedCookieValueProviderFactory());
});

```

**Step 3: Create the Custom `IModelBinder`**
This binder is responsible for building the `UserContext` object. It will automatically be able to see the values from our custom value provider.

```csharp
public class UserContextModelBinder : IModelBinder
{
    public Task BindModelAsync(ModelBindingContext bindingContext)
    {
        // The ValueProvider abstracts away the source. We don't care if it came
        // from a query, route, or our custom cookie provider.
        var tenantIdResult = bindingContext.ValueProvider.GetValue("tenantId");
        var userIdResult = bindingContext.ValueProvider.GetValue("userId");

        if (tenantIdResult == ValueProviderResult.None || userIdResult == ValueProviderResult.None)
        {
            return Task.CompletedTask; // Or fail
        }

        // At this point, tenantIdResult came from our custom EncryptedCookieValueProvider!
        // And userIdResult came from the built-in QueryStringValueProvider.

        int.TryParse(tenantIdResult.FirstValue, out var tenantId);
        int.TryParse(userIdResult.FirstValue, out var userId);

        var userContext = new UserContext { TenantId = tenantId, UserId = userId };

        bindingContext.Result = ModelBindingResult.Success(userContext);
        return Task.CompletedTask;
    }
}

```

**Step 4: Use it in the Controller Action**

```csharp
[HttpGet("documents")]
public IActionResult GetDocuments(
    [ModelBinder(typeof(UserContextModelBinder))] UserContext context
)
{
    // Thanks to the combination of the custom provider and custom binder,
    // the 'context' object is now fully populated with data from
    // two completely different sources.

    var documents = _repo.GetDocumentsForUser(context.TenantId, context.UserId);
    return Ok(documents);
}

```

### **Summary**

1. **Multiple Model Binders:** **Yes.** You can apply a different `[ModelBinder]` to each parameter of your action method.
2. **Custom Provider + Binder:** **Yes.** This is a powerful composition pattern. The `IValueProvider`'s job is to **find and provide** raw data from a custom source. The `IModelBinder`'s job is to **consume** that raw data (along with data from other providers) to **build** a complex parameter. They work together perfectly.