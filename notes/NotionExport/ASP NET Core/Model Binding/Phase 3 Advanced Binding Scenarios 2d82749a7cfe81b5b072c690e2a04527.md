# Phase 3: Advanced Binding Scenarios

Of course. This phase moves beyond the standard `[FromBody]` and `[FromQuery]`. We'll explore how to handle more complex and less structured data, such as file uploads and custom formats.

**(Microsoft Docs Main Page:** [*Custom Model Binding in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/mvc/advanced/custom-model-binding))*

---

### **1. Binding to Collections**

[ASP.NET](http://asp.net/) Core's model binder is smart enough to handle collections from various sources.

### **A. Collections from Query String**

This is common for endpoints that allow filtering by multiple IDs or tags.

**The URL:**`GET /api/products?ids=1&ids=2&ids=3`

**The Controller Action:**
The model binder automatically collects all query parameters with the key `ids` into a collection.

```csharp
[HttpGet]
public IActionResult GetProductsByIds([FromQuery] int[] ids)
{
    // The 'ids' parameter will be an array: [1, 2, 3]
    var products = _repository.GetByIds(ids);
    return Ok(products);
}

```

This also works for `List<int>` and `IEnumerable<string>`.

### **B. Collections from JSON Body**

This is the standard way to handle arrays of complex objects.

**The Request Body (`POST /api/orders/batch`):**

```json
[
  { "productId": 101, "quantity": 2 },
  { "productId": 205, "quantity": 1 }
]

```

**The Controller Action:**

```csharp
[HttpPost("batch")]
public IActionResult CreateBatchOrder([FromBody] List<CreateOrderDto> orders)
{
    // 'orders' will be a list containing two CreateOrderDto objects.
    _orderService.CreateBatch(orders);
    return Ok();
}

```

---

### **2. File Uploads with `IFormFile`**

Handling files requires a different content type: `multipart/form-data`. The model binder uses `[FromForm]` for this.

### **`IFormFile`**

This is the [ASP.NET](http://asp.net/) Core interface representing an uploaded file. It gives you access to:

- `FileName`: The original name of the file on the user's machine.
- `Length`: The file size in bytes.
- `ContentType`: The MIME type of the file (e.g., `image/jpeg`).
- `OpenReadStream()`: A method to get a `Stream` to read the file's contents.

### **Example: Uploading a Single File with Metadata**

**The Controller Action:**

```csharp
[HttpPost("upload-avatar")]
public async Task<IActionResult> UploadAvatar([FromForm] int userId, [FromForm] IFormFile avatar)
{
    if (avatar == null || avatar.Length == 0)
    {
        return BadRequest("No file uploaded.");
    }

    // Security check: Never trust the client's file name. Generate a unique one.
    var uniqueFileName = $"{Guid.NewGuid()}_{Path.GetFileName(avatar.FileName)}";
    var filePath = Path.Combine("wwwroot/avatars", uniqueFileName);

    // Best Practice: Always stream the file to disk, don't load it all into memory.
    await using (var stream = new FileStream(filePath, FileMode.Create))
    {
        await avatar.CopyToAsync(stream);
    }

    // Save the file path to the user's profile in the database...

    return Ok(new { FilePath = $"/avatars/{uniqueFileName}" });
}

```

**To Test:** In a tool like Postman, you must change the Body type to `form-data`. You will then have key-value fields where the "value" for `avatar` can be a file from your disk.

---

### **3. Custom Model Binders (`IModelBinder`)**

Sometimes, the built-in binders aren't flexible enough. You might need to handle a custom data format.

**The Scenario:**
Your frontend team sends a list of IDs as a single, comma-separated string in the query, not as repeated parameters.
**The URL:** `GET /api/products?ids=1,5,12`

**The Goal:** Bind this string directly to a `List<int>`.

### **Step 1: Create the Custom Model Binder**

```csharp
using Microsoft.AspNetCore.Mvc.ModelBinding;

public class CommaSeparatedListBinder : IModelBinder
{
    public Task BindModelAsync(ModelBindingContext bindingContext)
    {
        // 1. Get the raw value from the request (e.g., "1,5,12")
        var valueProviderResult = bindingContext.ValueProvider.GetValue(bindingContext.ModelName);
        var value = valueProviderResult.FirstValue;

        if (string.IsNullOrEmpty(value))
        {
            // If the query parameter is missing, return an empty list.
            bindingContext.Result = ModelBindingResult.Success(new List<int>());
            return Task.CompletedTask;
        }

        try
        {
            // 2. Parse the string into a list of integers
            var intList = value.Split(',')
                               .Select(int.Parse)
                               .ToList();

            // 3. Set the result
            bindingContext.Result = ModelBindingResult.Success(intList);
        }
        catch (FormatException)
        {
            // If parsing fails (e.g., "?ids=1,abc,3"), add a model state error.
            bindingContext.ModelState.TryAddModelError(bindingContext.ModelName, "Invalid integer format in list.");
        }

        return Task.CompletedTask;
    }
}

```

### **Step 2: Apply the Binder**

You apply the binder using an attribute on the action method parameter.

```csharp
[HttpGet]
public IActionResult GetProductsByIds(
    [FromQuery]
    [ModelBinder(BinderType = typeof(CommaSeparatedListBinder))]
    List<int> ids)
{
    // Thanks to the custom binder, 'ids' is now a populated List<int>.
    var products = _repository.GetByIds(ids);
    return Ok(products);
}

```

---

### **4. Custom Value Providers (`IValueProvider`)**

This is the deepest level of customization. A **Value Provider** is the component that tells the model binder *where to look for data*. [ASP.NET](http://asp.net/) Core has built-in value providers for Route, Query, Header, etc.

You would write your own `IValueProvider` if your data comes from a non-standard source.

**The Scenario:**
Your API needs to read a user's language preference from a custom, encrypted cookie named `user-prefs`.

1. **Create a `CookieValueProvider`:** This class would be responsible for finding the `user-prefs` cookie, decrypting it, and exposing its values to the model binding system.
2. **Create a `CookieValueProviderFactory`:** This factory class tells the pipeline how to create your value provider.
3. **Register the Factory in `Program.cs`:**
    
    ```csharp
    builder.Services.AddControllers(options =>
    {
        options.ValueProviderFactories.Insert(0, new CookieValueProviderFactory());
    });
    
    ```
    

This is a very advanced and rare scenario, typically only needed when integrating with legacy systems or implementing complex security protocols.

### **Summary of Phase 3**

- **Collections:** The model binder handles simple collections from query strings and complex object arrays from JSON bodies seamlessly.
- **File Uploads:** Use `[FromForm]` and the `IFormFile` interface to process `multipart/form-data` requests.
- **Custom Model Binders:** Implement `IModelBinder` to handle non-standard data formats or complex parsing logic, like converting a comma-separated string into a list.
- **Custom Value Providers:** The deepest level of customization, used for reading data from entirely new sources.

Are you ready to proceed to **Phase 4: Input Formatters and Body Handling**, where we'll look at how the request body is processed?