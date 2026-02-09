# Asp.net Core & SSL

# **Part 1: UseHsts() vs. UseHttpsRedirection() in ASP.NET Core**

These two middleware components in [ASP.NET](http://asp.net/) Core serve distinct but related purposes. They work together to create a secure browsing experience.

### **UseHttpsRedirection() - The "Right Now" Enforcer**

- **What it does:** This middleware inspects every single incoming request. If a request arrives over `http://`, it immediately returns an **HTTP 307 (Temporary Redirect)** or **308 (Permanent Redirect)** response, telling the client to resubmit the same request to the `https://` version of the URL.
- **Analogy:** This is like a security guard standing at the front door. If someone tries to enter through the unsecured side door (HTTP), the guard doesn't let them in; instead, they immediately point them to the main, secure entrance (HTTPS).
- **Who it helps:** It helps all clients, including first-time visitors, browsers, and even naive API clients, by actively forcing them to the secure channel for the current request.
- **Limitation:** It cannot protect against the "first request" vulnerability (SSL stripping attack) because the initial connection is still made over insecure HTTP before the redirect can be issued.

### **UseHsts() - The "Future" Policy Setter**

- **What it does:** HSTS stands for **HTTP Strict Transport Security**. This middleware does nothing to an incoming `http://` request. Instead, when a client connects over a secure `https://` connection, it adds a special response header: `Strict-Transport-Security: max-age=<seconds>`.
- **Analogy:** This is the security guard giving the visitor a signed policy document on their way out. The document says, *"For the next year, you are forbidden from even trying to use the unsecured side door. You must always come directly to the main secure entrance."*
- **Who it helps:** It primarily helps **browsers** that have visited your site at least once before. The browser remembers this policy. On all future visits, if the user types `http://`, the browser itself will change it to `https://` before ever sending a single packet over the network.
- **Benefit:** This completely closes the "first request" vulnerability for repeat visitors.

### **Summary of Differences**

| Feature | UseHttpsRedirection() | UseHsts() |
| --- | --- | --- |
| **Action** | **Active Redirect** (307/308) | **Passive Header** (Strict-Transport-Security) |
| **When it Acts** | On an incoming **HTTP** request | On a response to an **HTTPS** request |
| **Who it Protects** | All clients, for the current request | Primarily browsers, for future requests |
| **Vulnerability Fixed** | Direct access via insecure links | "SSL Stripping" for repeat visitors |

### **How they work together:**

In a typical `Program.cs`, you use both. `UseHttpsRedirection` catches the initial insecure requests, and `UseHsts` ensures that for repeat visits, those insecure requests are never even made.

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    // Use HSTS middleware to send HSTS headers to clients.
    // The default max-age is 30 days. You may want to change this for production scenarios.
    app.UseHsts();
}

// Use HTTPS Redirection middleware to redirect HTTP requests to HTTPS.
app.UseHttpsRedirection();

// ... other middleware
app.MapControllers();

app.Run();

```

*Note: The template puts `UseHsts()` inside the `!IsDevelopment()` check because HSTS can be annoying for local development where you might not have a trusted certificate.*

---

# **Part 2: How It Works for APIs (No Browser)**

This is where the behavior changes significantly.

- **UseHsts() is Mostly Ignored:** As we discussed, most programmatic API clients (like C#'s `HttpClient`, Python's `requests`, Postman) **do not maintain an HSTS policy cache**. They will not automatically "learn" to upgrade future requests. Therefore, `UseHsts()` provides very little value for API-to-API communication.
- **UseHttpsRedirection() Works (But is Inefficient):** If your API client is configured to follow redirects, `UseHttpsRedirection()` will work.

Let's see the code and the network chatter.

### **C# API Client Code (HttpClient)**

```csharp
// By default, HttpClientHandler's AllowAutoRedirect is true.
var httpClient = new HttpClient();

// WRONG: Using an insecure URI in your configuration.
string insecureEndpoint = "<http://my-production-api.azurewebsites.net/api/products/123>";

try
{
    // 1. First network call: An insecure HTTP GET request is sent.
    HttpResponseMessage response = await httpClient.GetAsync(insecureEndpoint);

    // The server responds with a 307/308 Redirect to the HTTPS endpoint.
    // The HttpClient handler sees this and automatically follows it.

    // 2. Second network call: A secure HTTPS GET request is sent to the new location.
    // 'response' will contain the final result from the HTTPS endpoint.

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    Console.WriteLine(responseBody);
}
catch (HttpRequestException e)
{
    Console.WriteLine($"Error: {e.Message}");
}

```

**The Problem:** You have just made **two network round-trips** where only one was necessary. This adds latency and is inefficient. The first trip was also unencrypted, potentially exposing the path and query parameters of your API call to anyone on the network.

**The API Best Practice:** The responsibility is on the **developer of the client**. Never put `http://` URIs for production endpoints in your configuration. **The client code itself should enforce HTTPS.**

---

# **Part 3: Production-Grade Strategy: Offloading to Azure Infrastructure**

For a robust, secure, and production-grade application, you should **not** rely solely on your application code for this. Enforcing security at the infrastructure edge is more efficient, consistent, and secure.

### **Why offload this?**

- **Efficiency:** Infrastructure services (like Front Door, App Gateway) are highly optimized for this kind of traffic management. They handle the redirect before the request ever hits your application's web server, saving your compute resources.
- **Security (Defense in Depth):** It creates a secure perimeter. You can configure your App Service to only accept traffic from your gateway, meaning no one can bypass your security rules by hitting your app's direct URL.
- **Consistency:** The same HTTPS enforcement policy is applied to every application behind the gateway, whether it's an [ASP.NET](http://asp.net/) app, a Node.js app, or a Java app. You don't have to worry if one developer forgot to add the middleware.

### **Ranking the Azure Services for this Job:**

1. **Azure Front Door / Application Gateway (Best Practice):**
    - **How:** These are the ideal services. They have a simple setting to enforce HTTPS. You can configure a rule that says "If the protocol is HTTP, redirect to HTTPS."
    - **Mechanism:** They will handle the 307/308 redirect at the edge, very efficiently.
    - **Advantage:** This is their core competency. They combine this with WAF, caching, and load balancing, providing a complete security and delivery solution at the network edge. This is the **most professional, production-grade way**.
2. **App Service (Good, but not the best):**
    - **How:** You can enable the "HTTPS Only" toggle in the App Service configuration under "TLS/SSL settings".
    - **Mechanism:** The App Service platform's front-end role (the part that receives traffic before it hits your code) will perform the same redirect that the `UseHttpsRedirection()` middleware does.
    - **Advantage:** It's a simple, one-click solution that is more efficient than doing it in your app code.
    - **Disadvantage:** It lacks the WAF and other advanced features of a true gateway. It also only protects this one App Service, whereas a gateway can protect many backend services.
3. **API Management (Viable for APIs):**
    - **How:** APIM enforces HTTPS by default for all API calls. You cannot call an API through the default gateway URL using HTTP. It will reject the connection.
    - **Advantage:** Built-in and requires no configuration.
    - **Disadvantage:** Similar to App Service, it lacks a WAF and is not meant as a general-purpose security edge for a full web application.
4. **Azure Load Balancer (Not Capable):**
    - **How:** It can't do this. A Standard Load Balancer operates at Layer 4 (TCP/UDP). It does not understand HTTP, so it has no concept of URLs or protocols to perform a redirect. It just forwards packets.

### **The Production-Grade Implementation Strategy:**

1. **At the Edge (Front Door/App Gateway):** Configure a rule to **redirect all HTTP to HTTPS**. This is your primary enforcement point.
2. **In your App Service:** Turn on **"HTTPS Only"** as a second layer of defense. This protects your app if someone finds its direct `.azurewebsites.net` URL and tries to bypass the gateway.
3. **In your [ASP.NET](http://asp.net/) Core App:** Keep `UseHttpsRedirection()` and `UseHsts()`. This is your third layer of defense. It costs very little and ensures the application behaves correctly and securely even during local development or if the infrastructure configuration is ever misconfigured. This follows the principle of "Defense in Depth".
4. **In your Client Code:** Always use `https://` URIs in your configuration files. Never rely on redirection for API calls.