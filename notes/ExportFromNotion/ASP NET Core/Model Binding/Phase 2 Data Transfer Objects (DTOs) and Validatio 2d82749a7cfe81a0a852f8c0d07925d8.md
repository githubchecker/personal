# Phase 2: Data Transfer Objects (DTOs) and Validation

Of course. This phase is crucial for building secure and maintainable APIs. It moves beyond just *receiving* data to ensuring the data is **shaped correctly** and is **valid**.

**(Microsoft Docs Main Page:** [*Model Validation in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation))*

---

### **1. Why Use Data Transfer Objects (DTOs)?**

A common mistake for beginners is to accept their EF Core Entity models directly as input.

**The "Bad" Way (Using an Entity Model):**

```csharp
// EF Core Entity
public class User
{
    public int Id { get; set; }
    public string Email { get; set; }
    public string HashedPassword { get; set; }
    public bool IsAdmin { get; set; } // <-- DANGER
    public DateTime CreatedAt { get; set; }
}

[HttpPost]
public IActionResult Register([FromBody] User user)
{
    // ... save user to DB
}

```

This leads to a classic vulnerability called **Over-posting**. A malicious user could send this JSON:

```json
{
  "email": "hacker@evil.com",
  "password": "some_password",
  "isAdmin": true
}

```

The model binder would happily map `isAdmin: true` to your entity, and you might accidentally save an admin user to the database.

**The "Expert" Way (Using a DTO):**
You create a separate class that represents only the data you *expect* to receive.

```csharp
// DTO for user registration
public class RegisterUserDto
{
    public string Email { get; set; }
    public string Password { get; set; }
}

[HttpPost]
public IActionResult Register([FromBody] RegisterUserDto userDto)
{
    // The binder will IGNORE any extra fields like 'isAdmin'.
    // Manually map the DTO to your internal User entity.
    var newUser = new User
    {
        Email = userDto.Email,
        // ... hash password, set defaults
    };
    _db.Users.Add(newUser);
    _db.SaveChanges();
    return Ok();
}

```

**Benefits of DTOs:**

1. **Security:** Prevents over-posting attacks.
2. **Decoupling:** You can change your internal database schema without breaking your public API contract.
3. **Clarity:** The DTO clearly defines the expected input for an endpoint.

---

### **2. Data Annotations (Declarative Validation)**

This is the simplest way to add validation rules to your DTOs. You use attributes from the `System.ComponentModel.DataAnnotations` namespace.

The model binder automatically checks these attributes and adds errors to `ModelState` if they fail.

**Example DTO with Annotations:**

```csharp
using System.ComponentModel.DataAnnotations;

public class CreateProductDto
{
    [Required(ErrorMessage = "Product name is mandatory.")]
    [StringLength(100, MinimumLength = 3, ErrorMessage = "Name must be between 3 and 100 characters.")]
    public string Name { get; set; }

    [Required]
    [Range(0.01, 10000.00, ErrorMessage = "Price must be between 0.01 and 10,000.")]
    public decimal Price { get; set; }

    [EmailAddress(ErrorMessage = "Supplier email is not a valid email address.")]
    public string SupplierEmail { get; set; }
}

```

**Common Data Annotations:**

- `[Required]`: The property cannot be null (or whitespace for strings).
- `[StringLength(max)]`, `[MinLength(min)]`, `[MaxLength(max)]`: For strings.
- `[Range(min, max)]`: For numbers.
- `[RegularExpression("...")]`: Matches a regex pattern.
- `[EmailAddress]`, `[Phone]`, `[Url]`, `[CreditCard]`: Pre-built format validators.
- `[Compare("OtherProperty")]`: Ensures two properties (like `Password` and `ConfirmPassword`) match.

---

### **3. `ModelState.IsValid`**

`ModelState` is a dictionary-like object available in your controller that collects all validation errors found during model binding.

- `ModelState.IsValid` is a boolean property that is `true` if no errors were added.

**How it works with `[ApiController]`:**
If you are using the `[ApiController]` attribute, a built-in action filter automatically checks `!ModelState.IsValid` for you. If it's `false`, the filter short-circuits the request and returns a `400 Bad Request` with a structured list of the errors.

**Manual Check (if not using `[ApiController]`):**

```csharp
[HttpPost]
public IActionResult Create(CreateProductDto product)
{
    if (!ModelState.IsValid)
    {
        // This is what [ApiController] does for you automatically.
        return BadRequest(ModelState);
    }
    // ... proceed with valid data
}

```

---

### **4. FluentValidation (The Expert's Choice)**

Data Annotations are great for simple rules, but they have limitations:

- They clutter your DTOs with attributes ("Attribute Hell").
- They can't easily handle complex, cross-property logic.
- They are harder to unit test.

**FluentValidation** is a popular third-party library that solves these problems by decoupling validation logic into separate validator classes.

**Step 1: Install the Package**

```bash
dotnet add package FluentValidation.AspNetCore

```

**Step 2: Create a Validator Class**

```csharp
using FluentValidation;

public class CreateProductDtoValidator : AbstractValidator<CreateProductDto>
{
    public CreateProductDtoValidator()
    {
        RuleFor(p => p.Name)
            .NotEmpty().WithMessage("Product name cannot be empty.")
            .Length(3, 100);

        RuleFor(p => p.Price)
            .GreaterThan(0);

        // Complex custom rule
        RuleFor(p => p.SupplierEmail)
            .Must(BeACompanyEmail)
            .When(p => !string.IsNullOrEmpty(p.SupplierEmail))
            .WithMessage("Only official company email addresses are allowed.");
    }

    private bool BeACompanyEmail(string email)
    {
        return !email.EndsWith("@gmail.com") && !email.EndsWith("@yahoo.com");
    }
}

```

**Step 3: Register in `Program.cs`**

```csharp
// 1. Add FluentValidation services
builder.Services.AddFluentValidationAutoValidation();

// 2. Register your validator classes
builder.Services.AddScoped<IValidator<CreateProductDto>, CreateProductDtoValidator>();

```

The `AddFluentValidationAutoValidation()` method automatically plugs FluentValidation into the [ASP.NET](http://asp.net/) Core pipeline, so `ModelState.IsValid` works just like it does with Data Annotations.

### **Summary of Phase 2**

- **Use DTOs:** Always create dedicated input models to separate your API contract from your database schema and enhance security.
- **Data Annotations:** Provide a simple, declarative way to enforce basic validation rules.
- **`[ApiController]`:** Automates the process of checking `ModelState` and returning `400 Bad Request` responses.
- **FluentValidation:** For complex, business-specific, or cross-property validation, FluentValidation provides a much cleaner, more powerful, and testable approach.

Are you ready to proceed to **Phase 3: Advanced Binding Scenarios**, where we'll handle file uploads and custom data formats?

# **Custom Validation Options**

That's an excellent question that goes to the heart of clean architecture and proper validation placement. The best place for cross-property validation like `"EndDate cannot be before StartDate"` depends on the complexity and reusability of your validation logic.

Here is a guide, ordered from the simplest to the most robust and recommended approach, aligned with Microsoft's documentation and best practices.

---

### **Option 1: In the Controller Action (The "Quick and Dirty" Way)**

You can always perform manual validation directly inside your action method.

- **How it works:** You write a simple `if` statement and, if the validation fails, you manually add an error to `ModelState` and return a `BadRequest`.

```csharp
[HttpPost]
public IActionResult CreateEvent([FromBody] EventDto eventDto)
{
    if (eventDto.EndDate < eventDto.StartDate)
    {
        ModelState.AddModelError(nameof(eventDto.EndDate), "End Date cannot be before Start Date.");
    }

    if (!ModelState.IsValid)
    {
        return BadRequest(ModelState);
    }

    // ... proceed with valid data
}

```

- **Pros:**
    - Simple and direct for a one-off check.
- **Cons (Why you shouldn't do this):**
    - **Violates DRY:** If you need this same validation in an `UpdateEvent` action, you have to copy-paste the logic.
    - **Clutters the Controller:** The controller's job is to handle HTTP flow, not complex business validation. This mixes concerns.
- **Documentation Verdict:** This is a valid technique but is not the recommended pattern for anything other than the simplest, non-reusable checks.

---

### **Option 2: Custom Validation Attribute (The "Reusable" Way)**

You can create your own custom `ValidationAttribute` to encapsulate this logic. This is a significant improvement because it makes the validation reusable.

- **How it works:** You create a class that inherits from `ValidationAttribute` and override the `IsValid` method.

**Step 1: Create the Attribute**

```csharp
using System.ComponentModel.DataAnnotations;

public class DateRangeAttribute : ValidationAttribute
{
    private readonly string _startDatePropertyName;

    public DateRangeAttribute(string startDatePropertyName)
    {
        _startDatePropertyName = startDatePropertyName;
    }

    protected override ValidationResult IsValid(object value, ValidationContext validationContext)
    {
        // 'value' is the EndDate.
        var endDate = (DateTime)value;

        // Get the StartDate property from the object being validated.
        var startDateProperty = validationContext.ObjectType.GetProperty(_startDatePropertyName);
        if (startDateProperty == null)
        {
            throw new ArgumentException("Invalid property name for start date.");
        }

        var startDate = (DateTime)startDateProperty.GetValue(validationContext.ObjectInstance);

        if (endDate < startDate)
        {
            return new ValidationResult("End Date cannot be before Start Date.", new[] { validationContext.MemberName });
        }

        return ValidationResult.Success;
    }
}

```

**Step 2: Apply the Attribute to your DTO**

```csharp
public class EventDto
{
    [Required]
    public DateTime StartDate { get; set; }

    [Required]
    [DateRange(nameof(StartDate))] // Apply the custom attribute
    public DateTime EndDate { get; set; }
}

```

- **Pros:**
    - **Reusable:** You can apply the `[DateRange]` attribute to any DTO that needs this validation.
    - **Declarative:** Keeps the validation logic out of the controller and on the model where it belongs.
- **Cons:**
    - Can get complex if your validation needs to access external services (like a database). This is where attributes show their limits, as they are not easily integrated with Dependency Injection.
- **Documentation Verdict:** Microsoft's documentation explicitly covers creating custom validation attributes as a standard pattern for this kind of cross-property validation. It is a highly recommended approach for self-contained validation logic.

---

### **Option 3: `IValidatableObject` Interface (The "Self-Validating Model" Way)**

You can implement the `IValidatableObject` interface directly on your DTO. This allows the model to contain its own complex validation logic.

- **How it works:** You implement the `Validate` method, which is automatically called during the model validation process.

```csharp
public class EventDto : IValidatableObject
{
    [Required]
    public DateTime StartDate { get; set; }

    [Required]
    public DateTime EndDate { get; set; }

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (EndDate < StartDate)
        {
            yield return new ValidationResult(
                "End Date cannot be before Start Date.",
                new[] { nameof(EndDate) }
            );
        }
    }
}

```

- **Pros:**
    - Keeps the validation logic encapsulated within the model itself.
    - Simple to implement for model-specific rules.
- **Cons:**
    - Still suffers from the same DI limitation as custom attributes. It cannot easily access external services.
    - Tightly couples the model to its validation logic, which some architectures try to avoid.
- **Documentation Verdict:** This is a fully supported and documented pattern, often presented as an alternative to custom attributes for self-contained model validation.

---

### **Option 4: FluentValidation (The "Expert" and Recommended Way)**

For any non-trivial application, a dedicated validation library like **FluentValidation** is the best practice and is implicitly endorsed by Microsoft's documentation through its wide community adoption and seamless integration.

- **How it works:** You completely separate your validation rules into a dedicated `Validator` class, which can use Dependency Injection.

### **Final Recommendation**

| Your Situation | Best Place for Validation |
| --- | --- |
| Simple, non-reusable check | **1. Controller Action** (but try to avoid) |
| Reusable, self-contained logic | **2. Custom `ValidationAttribute`** (Good) or **3. `IValidatableObject`** (Also Good) |
| **Complex rules, needs DB access, or you want the cleanest architecture** | **4. FluentValidation** (**The Best Practice**) |