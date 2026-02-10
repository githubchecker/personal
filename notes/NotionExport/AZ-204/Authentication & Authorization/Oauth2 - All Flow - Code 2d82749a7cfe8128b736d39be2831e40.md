# Oauth2 - All Flow - Code

Here is the comprehensive, minimal code "cheat sheet" to implement these four OAuth 2.0 flows using .NET 8+.

This guide uses the [**Microsoft.Identity.Web**](http://microsoft.identity.web/) library, which drastically simplifies the boilerplate code.

---

# **The Foundation: Our Custom Resource API (`CommentsApi`)**

This is the API we want to protect. All four scenarios will use this same API project as their destination.

### **1. Program.cs - The Core Security Setup**

This setup validates incoming tokens against Azure AD.

```csharp
// Program.cs in your CommentsApi project
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web; // The key Microsoft library

var builder = WebApplication.CreateBuilder(args);

// --- START: AZURE AD SECURITY CONFIGURATION ---
// 1. Adds services to read the "AzureAd" section from appsettings.json
//    and wires up the JWT Bearer authentication handler.
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

// 2. Adds the services for Authorization (checking for scopes/roles)
builder.Services.AddAuthorization();
// --- END: AZURE AD SECURITY CONFIGURATION ---

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// 3. These two middleware components are essential.
//    Authentication must come before Authorization.
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();

```

### **2. appsettings.json - The Configuration**

This file will contain the details of your API's App Registration.

```json
{
  "AzureAd": {
    "Instance": "<https://login.microsoftonline.com/>",
    "TenantId": "YOUR_TENANT_ID", // The directory ID of your tenant
    "ClientId": "YOUR_COMMENTS_API_CLIENT_ID", // The Application (client) ID of the API
    "Audience": "api://YOUR_COMMENTS_API_CLIENT_ID" // The App ID URI you set in "Expose an API"
  },
  //... rest of the file
}

```

### **3. CommentsController.cs - Protecting Endpoints**

Here we define our endpoints and specify the exact permissions required for each.

```csharp
// CommentsController.cs in your CommentsApi project
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Identity.Web.Resource; // Required for the scope/role attributes

[Authorize] // 1. This attribute requires ANY authenticated user.
[ApiController]
[Route("api/[controller]")]
public class CommentsController : ControllerBase
{
    // A list to simulate a database
    private static readonly List<string> _comments = new() { "This is a great comment!" };

    // --- PERMISSION DEFINITIONS ---
    // These constants make our code clean and prevent typos.
    // They MUST match the values you configured in the API's "Expose an API" blade.
    private const string ReadPermissionScope = "Comments.Read";
    private const string WritePermissionScope = "Comments.Write";
    // NOTE: Application Permissions (Roles) usually don't have scope prefixes in the token claim,
    // but in Azure AD "App Roles" UI, the value is just the string.
    private const string DeletePermissionAppRole = "Comments.Delete.All"; // An App Role for M2M

    [HttpGet]
    // 2. This attribute checks if the token contains EITHER the required Delegated Permission (scope)
    //    OR the required Application Permission (app role). The logic is smart enough to check
    //    both the 'scp' and 'roles' claims in the incoming JWT.
    [RequiredScopeOrAppRole(
        RequiredScopesConfigurationKey = "AzureAd:Scopes:Read",
        RequiredAppRolesConfigurationKey = "AzureAd:AppRoles:Read" // We'll add this to appsettings
    )]
    public ActionResult<IEnumerable<string>> ReadComments()
    {
        return Ok(_comments);
    }

    [HttpPost]
    // 3. This checks ONLY for the delegated scope. A M2M call would fail here (by design).
    [RequiredScope(WritePermissionScope)]
    public ActionResult AddComment([FromBody] string comment)
    {
        _comments.Add(comment);
        return Ok($"Comment added. Total comments: {_comments.Count}");
    }

    [HttpDelete("{index}")]
    // 4. This checks ONLY for the Application Permission (App Role). A user call would fail.
    //    Ideal for a privileged, automated system action.
    [Authorize(Roles = DeletePermissionAppRole)] // Standard AspNetCore works for roles too
    public ActionResult DeleteComment(int index)
    {
        if (index >= 0 && index < _comments.Count)
        {
            _comments.RemoveAt(index);
            return Ok("Comment deleted.");
        }
        return NotFound();
    }
}

```

### **4. appsettings.json (Updated for RequiredScopeOrAppRole)**

We map the code keys to the actual string values here to allow changing config without recompiling.

```json
{
  "AzureAd": {
    "Scopes": {
      "Read": "Comments.Read"
    },
    "AppRoles": {
      "Read": "Comments.Read.All" // Let's use a different name for the App Role to be clear
    }
  }
}

```

---

# **Scenario 1: Authorization Code Flow (Web App -> API)**

- **Best Fit Caller:** .NET Core Web App (MVC/Razor Pages). This is a "Confidential Client" because it runs on a server and can keep secrets.

### **Minimal Code for WebApp/Program.cs**

```csharp
// Program.cs in the calling Web App project
using Microsoft.Identity.Web;
using Microsoft.Identity.Web.UI;

var builder = WebApplication.CreateBuilder(args);

// --- START: AZURE AD SECURITY CONFIGURATION ---
// 1. Sets up authentication for users to sign into this web app.
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"))
        // 2. Enables token acquisition to call a downstream API
        .EnableTokenAcquisitionToCallDownstreamApi()
            // 3. Specifies how to call our specific API, reading config from the "CommentsApi" section
            .AddDownstreamApi("CommentsApi", builder.Configuration.GetSection("CommentsApi"))
            // 4. Use an in-memory token cache for simplicity. Use a distributed cache in production.
            .AddInMemoryTokenCaches();

builder.Services.AddRazorPages()
    // 5. Adds the UI for "Sign In / Sign Out" buttons provided by Microsoft.Identity.Web.UI
    .AddMicrosoftIdentityUI();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.MapRazorPages();

app.Run();

```

### **Minimal Code for the calling Page (WebApp/Pages/Index.cshtml.cs)**

```csharp
// Example Razor Page model in the calling Web App
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Identity.Abstractions; // The new, simple way to call APIs

public class IndexModel : PageModel
{
    private readonly IDownstreamApi _downstreamApi;

    public IndexModel(IDownstreamApi downstreamApi)
    {
        _downstreamApi = downstreamApi;
    }

    public IEnumerable<string> Comments { get; set; } = new List<string>();

    public async Task OnGet()
    {
        // The library handles the entire token acquisition process for you.
        // It uses the Authorization Code flow token, and if it's expired,
        // it uses the refresh token to get a new one. All behind the scenes.

        // "CommentsApi" matches the name we gave our API in Program.cs
        // relativeUrl is appended to the BaseUrl in config
        var response = await _downstreamApi.CallApiForUserAsync(
            "CommentsApi",
            options =>
            {
                options.RelativePath = "api/comments";
                options.HttpMethod = HttpMethod.Get;
            });

        if (response.IsSuccessStatusCode)
        {
             Comments = await response.Content.ReadFromJsonAsync<IEnumerable<string>>();
        }
    }
}

```

### **WebApp/appsettings.json**

```json
{
  "AzureAd": {
    // Config for THIS Web App (The Client)
    "Instance": "<https://login.microsoftonline.com/>",
    "TenantId": "YOUR_TENANT_ID",
    "ClientId": "YOUR_WEB_APP_CLIENT_ID",
    "ClientSecret": "YOUR_WEB_APP_CLIENT_SECRET",
    "CallbackPath": "/signin-oidc"
  },
  "CommentsApi": {
    // Config for the API it will call
    "BaseUrl": "<https://localhost:7123>", // The URL of your running CommentsApi
    // The scope THIS WebApp needs for the CommentsApi
    "Scopes": "api://YOUR_COMMENTS_API_CLIENT_ID/Comments.Read"
  }
}

```

---

# **Scenario 2: Authorization Code Flow with PKCE (SPA -> API)**

- **Best Fit Caller:** JavaScript in an HTML file (React, Angular, Vue, or plain JS). This is a "Public Client" because it runs in the browser and cannot keep secrets.

### **Minimal Code for index.html**

```html
<!DOCTYPE html>
<html>
<head>
    <title>SPA PKCE Caller</title>
    <!-- 1. Include the MSAL Browser library from a CDN -->
    <script src="<https://alcdn.msauth.net/browser/2.14.2/js/msal-browser.min.js>"></script>
</head>
<body>
    <h1>SPA Comments</h1>
    <button id="signInButton">Sign In</button>
    <button id="callApiButton">Read Comments</button>
    <pre id="response"></pre>

    <script>
        // --- START: MSAL CONFIGURATION ---
        const msalConfig = {
            auth: {
                clientId: "YOUR_SPA_APP_CLIENT_ID", // Client ID of the SPA's App Registration
                authority: "<https://login.microsoftonline.com/YOUR_TENANT_ID>",
                redirectUri: "<http://localhost:8080>" // Must be configured in the SPA App Reg
            }
        };

        const msalInstance = new msal.PublicClientApplication(msalConfig);

        const apiRequest = {
            // These are the DELEGATED scopes you need for the API call
            scopes: ["api://YOUR_COMMENTS_API_CLIENT_ID/Comments.Read"]
        };
        // --- END: MSAL CONFIGURATION ---

        // Function to acquire a token (MSAL handles PKCE automatically)
        async function getToken() {
            try {
                // First, try to get a token silently (in case user is already logged in)
                const response = await msalInstance.acquireTokenSilent(apiRequest);
                return response.accessToken;
            } catch (error) {
                if (error instanceof msal.InteractionRequiredAuthError) {
                    // If silent fails, pop up a login window
                    const response = await msalInstance.acquireTokenPopup(apiRequest);
                    return response.accessToken;
                }
                console.error(error);
                return null;
            }
        }

        // --- Event Listeners ---
        document.getElementById("signInButton").onclick = () => {
            msalInstance.loginPopup(apiRequest);
        };

        document.getElementById("callApiButton").onclick = async () => {
            const accessToken = await getToken();

            if (!accessToken) {
                document.getElementById("response").innerText = "Could not acquire token.";
                return;
            }

            const headers = new Headers();
            headers.append("Authorization", `Bearer ${accessToken}`);

            const options = { method: "GET", headers: headers };

            try {
                // Call the API directly using fetch
                const response = await fetch("<https://localhost:7123/api/comments>", options);
                const data = await response.json();
                document.getElementById("response").innerText = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById("response").innerText = error;
            }
        };
    </script>
</body>
</html>

```

---

# **Scenario 3: Client Credentials Flow (Backend Service -> API)**

- **Best Fit Caller:** .NET Console App / Background Worker / Azure Function. This is a "Confidential Client" (Service-to-Service). It acts as itself, not a user.

### **Minimal Code for ConsoleApp/Program.cs**

```csharp
// Program.cs in the Console App project
using Microsoft.Identity.Client; // This is the core MSAL.NET library

// --- START: CONFIGURATION ---
var clientId = "YOUR_CONSOLE_APP_CLIENT_ID";
var clientSecret = "YOUR_CONSOLE_APP_CLIENT_SECRET";
var tenantId = "YOUR_TENANT_ID";
// The scope for Client Credentials is usually "api://.../.default"
// This tells Azure AD: "Give me all Application Permissions I have been granted"
var apiScope = new string[] { "api://YOUR_COMMENTS_API_CLIENT_ID/.default" };
var apiUrl = "<https://localhost:7123/api/comments/0>"; // Calling the Delete endpoint
// --- END: CONFIGURATION ---

// 1. Build a confidential client application
IConfidentialClientApplication app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithClientSecret(clientSecret)
    .WithAuthority(new Uri($"<https://login.microsoftonline.com/{tenantId}>"))
    .Build();

Console.WriteLine("Acquiring token for the application...");

try
{
    // 2. Acquire a token FOR THE APP, not a user.
    AuthenticationResult result = await app.AcquireTokenForClient(apiScope)
        .ExecuteAsync();

    Console.WriteLine("Token acquired. Calling API...");

    // 3. Call the protected API with the app-only token
    var httpClient = new HttpClient();
    httpClient.DefaultRequestHeaders.Authorization =
        new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", result.AccessToken);

    // Call the endpoint that requires an App Role (Delete)
    HttpResponseMessage response = await httpClient.DeleteAsync(apiUrl);

    if (response.IsSuccessStatusCode)
    {
        Console.WriteLine("API call successful!");
        Console.WriteLine(await response.Content.ReadAsStringAsync());
    }
    else
    {
        Console.ForegroundColor = ConsoleColor.Red;
        Console.WriteLine($"API call failed with status: {response.StatusCode}");
    }
}
catch (MsalServiceException ex)
{
    Console.WriteLine($"Error acquiring token: {ex.Message}");
}

```

---

# **Scenario 4: On-Behalf-Of Flow (SPA -> Gateway API -> Downstream API)**

- **Best Fit Caller:** A .NET Core Web API acting as a middle-tier (Gateway) between a frontend (SPA) and the final Data API (Comments API).
- **The Flow:** SPA calls Gateway with User Token A -> Gateway exchanges Token A for Token B (via OBO) -> Gateway calls Comments API with Token B.

### **Step 1: The GatewayApi Project (`Program.cs`)**

```csharp
// Program.cs in your GatewayApi project
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// --- START: OBO CONFIGURATION ---
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd")) // 1. Validate incoming token from SPA
        .EnableTokenAcquisitionToCallDownstreamApi() // 2. Enable OBO flow capabilities
            .AddDownstreamApi("CommentsApi", builder.Configuration.GetSection("CommentsApi")) // 3. Define target API
            .AddInMemoryTokenCaches(); // 4. Cache the OBO token
// --- END: OBO CONFIGURATION ---

builder.Services.AddControllers();

// Add CORS so our SPA can call this Gateway
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("<http://localhost:8080>") // The address of our SPA
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();

```

### **Step 2: The GatewayApi Project (`appsettings.json`)**

```json
{
  "AzureAd": {
    "Instance": "<https://login.microsoftonline.com/>",
    "TenantId": "YOUR_TENANT_ID",
    "ClientId": "YOUR_GATEWAY_API_CLIENT_ID",
    "ClientSecret": "YOUR_GATEWAY_API_CLIENT_SECRET", // Needed for OBO exchange
    "Audience": "api://YOUR_GATEWAY_API_CLIENT_ID" // What the SPA calls
  },
  "CommentsApi": {
    "BaseUrl": "<https://localhost:7123>",
    // The Scope THIS GatewayApi needs to ask for on behalf of the user
    "Scopes": "api://YOUR_COMMENTS_API_CLIENT_ID/Comments.Read"
  }
}

```

### **Step 3: The GatewayApi Controller**

```csharp
// GatewayController.cs in your GatewayApi project
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Identity.Abstractions;
using Microsoft.Identity.Web.Resource;

[Authorize]
[ApiController]
[Route("api/[controller]")]
public class GatewayController : ControllerBase
{
    private readonly IDownstreamApi _downstreamApi;
    // The scope the SPA must send to the Gateway
    private const string GatewayReadScope = "Gateway.Read";

    public GatewayController(IDownstreamApi downstreamApi)
    {
        _downstreamApi = downstreamApi;
    }

    [HttpGet("comments")]
    [RequiredScope(GatewayReadScope)]
    public async Task<ActionResult<IEnumerable<string>>> GetComments()
    {
        // --- THE ON-BEHALF-OF FLOW HAPPENS HERE ---
        // 1. Library validates the incoming user token (Token A).
        // 2. Library uses Client Secret + Token A to request Token B from Azure AD.
        // 3. Library adds Token B to the Authorization header of the outgoing request.
        var response = await _downstreamApi.CallApiForUserAsync(
            "CommentsApi",
            options =>
            {
                options.RelativePath = "api/comments";
                options.HttpMethod = HttpMethod.Get;
            });

        if (response.IsSuccessStatusCode)
        {
            var content = await response.Content.ReadAsStringAsync();
            return Ok(content);
        }

        return StatusCode((int)response.StatusCode, "Downstream API failed");
    }
}

```