# Types of Authentication Flows

Let's create a clear guide. The choice of flow depends almost entirely on two questions:

1. **Can my application keep a secret?** (Is it a "confidential client" or a "public client"?)
2. **Is a user actively present and signing in?**

The Single-Tenant vs. Multi-Tenant decision doesn't change *which* flow you use, but it changes *how* you configure the endpoints and handle consent.

---

# **The Definitive Guide to Common Authentication Flows**

- Here is a breakdown of the most common scenarios you will encounter.
    - **SPA (Single-Page App) e.g., React, Angular, Vue**
        - **Key Characteristics:** Runs entirely in the user's browser. **Cannot keep a secret.** Its code is public.
        - **Recommended Flow:** **Authorization Code Flow with PKCE**.
        - **Why This Flow?** This is the modern standard for security. Since the app can't hold a secret, **PKCE (Proof Key for Code Exchange)** acts as a temporary, per-request secret, preventing attacks where an authorization code could be stolen.
        - **Tenant Consideration:** Works perfectly for both. For Multi-Tenant, your app calls the generic `/common` or `/organizations` endpoint to allow users from any organization to sign in.
    - **Traditional Web App e.g., [ASP.NET](http://asp.net/) Core, Java, Django**
        - **Key Characteristics:** Has a backend that runs on your server. **Can keep a secret.** It is a "**confidential client**".
        - **Recommended Flow:** **Authorization Code Flow**.
        - **Why This Flow?** This is the classic, robust flow. The user signs in via the browser, your backend receives an authorization code, and because it has a **client secret**, it can securely exchange that code for an access token on the server side.
        - **Tenant Consideration:** Works perfectly for both. For Multi-Tenant, use the `/common` endpoint. Your server-side code will be able to identify the user's home tenant from the token it receives.
    - **Protected Web API e.g., [ASP.NET](http://asp.net/) Web API, Node/Express**
        - **Key Characteristics:** Has no UI. It's called by another app (like a SPA or Web App) and needs to call another API (like Microsoft Graph) *as the user*.
        - **Recommended Flow:** **On-Behalf-Of (OBO) Flow**.
        - **Why This Flow?** This flow is specifically designed for a service-to-service call chain initiated by a user. The API receives an access token from the calling app and **exchanges it** for a new access token to call the downstream API, all while maintaining the original user's identity.
        - **Tenant Consideration:** This is the cornerstone of multi-tenant SaaS architectures. The API must be able to handle tokens from users in any customer tenant and then use the OBO flow to get Graph tokens for that specific tenant.
    - **Daemon App / Background Service e.g., a nightly job, a background worker, a system service**
        - **Key Characteristics:** Runs with no user present. Needs to access data using its **own application identity**.
        - **Recommended Flow:** **Client Credentials Flow**.
        - **Why This Flow?** There is no user to delegate permission, so the application authenticates using its own credentials (`client_id` + `client_secret` or certificate). The permissions it uses must be of type "**Application**", not "Delegated".
        - **Tenant Consideration:** Works for both. For a Multi-Tenant daemon, an admin from each customer tenant must grant consent to the application's "Application" permissions. The app would then get a token for each specific tenant it needs to operate on.
    - **Mobile / Native Desktop App e.g., iOS, Android, .NET MAUI, WPF**
        - **Key Characteristics:** A native application installed on a device. **Cannot reliably keep a secret.**
        - **Recommended Flow:** **Authorization Code Flow with PKCE**.
        - **Why This Flow?** Same reason as a SPA. It is a "**public client**." The app uses the system browser or a secure web-view to handle the sign-in, and PKCE secures the code exchange process.
        - **Tenant Consideration:** Works perfectly for both. Use the `/common` endpoint to allow any user to sign in, making your native app available to a wide audience.

---

# **Simple Decision Flowchart**

- To make it even simpler, here is a mental flowchart to follow:
    - **Question 1: Is a user interactively signing in right now?**
        - **NO** (It's a background service, a script, a system-to-system process)
            - ➡️ **Use the Client Credentials Flow.**
        - **YES** (A person is clicking a "Log In" button)
            - **Question 2: Does your application have a secure backend server that can store a secret?**
                - **NO** (It's a JavaScript SPA or a Mobile/Desktop app)
                    - ➡️ **Use the Authorization Code Flow with PKCE.**
                - **YES** (It's a traditional server-side web app like [ASP.NET](http://asp.net/) or Django)
                    - ➡️ **Use the Authorization Code Flow.**
    - **Special Case Question 3: Is your application a backend API that, after being called by an authenticated user, needs to call *another API* on that user's behalf?**
        - **YES**
            - ➡️ **Use the On-Behalf-Of (OBO) Flow** inside your API.

---

# **Quick Mapping: Common Names to Formal Names**

- First, let's create a clear mapping table. This will be your cheat sheet.
    - **Common Application Scenario** -> **Formal OAuth 2.0 Grant Type**
        - Traditional Web App (with a backend) -> **Authorization Code Grant**
        - SPA / Mobile App / Desktop App -> **Authorization Code Grant with PKCE** (PKCE is an extension)
        - Daemon App / Background Service -> **Client Credentials Grant**
        - Protected Web API calling another API -> **On-Behalf-Of Flow**
        - Input-constrained devices (CLI, Smart TV) -> **Device Code Flow**
        - Legacy SPA (Not Recommended) -> **Implicit Grant**
        - Legacy / Special Cases (Not Recommended) -> **Resource Owner Password Credentials (ROPC) Grant**

---

# **Detailed Guide to Each OAuth 2.0 Grant Type**

- Here is the detailed breakdown for your AZ-204 preparation.

## **1. OAuth 2.0 Authorization Code Grant**

- **Mapping to Our Previous Discussion:** This is the flow for **Traditional Web Apps** (e.g., [ASP.NET](http://asp.net/) Core, Java Spring, Django).
- **Actors:**
    - **Resource Owner:** The User.
    - **Client:** Your server-side web application (a "**confidential client**" because it can keep a secret).
    - **Authorization Server:** Azure Active Directory (AAD).
    - **Resource Server:** The API you want to access (e.g., Microsoft Graph).
- **When to Use It:** Use this flow whenever you have a web application with a **secure backend**.
- **How It Works (The Core Principle):** This flow is designed to be highly secure by never exposing access tokens to the browser (the user agent).
    1. The user is redirected to Azure AD to sign in.
    2. After signing in, Azure AD redirects the user back to the application with a temporary, one-time-use **Authorization Code**.
    3. The application's **backend server** takes this code, and because it has its own `client_id` and `client_secret`, it makes a secure, direct call to Azure AD.
    4. Azure AD validates the code and the client secret, and returns the **Access Token** and **Refresh Token** directly to the backend. The browser never sees them.
- **Recommendation:** **HIGHLY RECOMMENDED.** This is the gold standard for web applications that have a backend.

## **2. OAuth 2.0 Client Credentials Grant**

- **Mapping to Our Previous Discussion:** This is the flow for **Daemon Apps / Background Services**.
- **Actors:**
    - **Client:** The application itself (e.g., a background service, a script). There is **no user**.
    - **Authorization Server:** Azure AD.
    - **Resource Server:** The API you want to access.
- **When to Use It:** Use this when an application needs to access resources using its **own identity**, not on behalf of a user. Think of a nightly script that syncs data or a service that processes messages from a queue.
- **How It Works (The Core Principle):** It's the simplest flow. The application directly authenticates with the authorization server.
    1. The application sends its `client_id` and `client_secret` (or a certificate) to the Azure AD token endpoint.
    2. Azure AD validates the credentials and returns an access token.
    3. The token represents the application's identity and contains the permissions granted to the application itself (permissions of type "**Application**", not "Delegated").
- **Recommendation:** **HIGHLY RECOMMENDED.** This is the only correct and secure way for applications to authenticate without a user.

## **3. OAuth 2.0 Device Code Flow**

- **Mapping to Our Previous Discussion:** This is a new one, designed for a specific category of apps.
- **Actors:**
    - **Resource Owner:** The User.
    - **Client:** An application on a device with limited input (e.g., a command-line interface (CLI) tool, a Smart TV app, an IoT device).
    - **User's Secondary Device:** The user's phone or computer with a full browser.
    - **Authorization Server:** Azure AD.
- **When to Use It:** Use this when a user needs to sign in on a device that **lacks a browser or has a difficult text-entry mechanism**. The `az login` command in the Azure CLI is a perfect real-world example.
- **How It Works (The Core Principle):** It offloads the authentication experience to a more capable device.
    1. The CLI tool or TV app makes a request to Azure AD.
    2. Azure AD returns a URL (`https://microsoft.com/devicelogin`) and a short, user-friendly **Device Code**.
    3. The app displays a message to the user: "Go to this URL on your phone/PC and enter this code: GZ-123-BCA".
    4. The user goes to the URL on their phone, signs in normally (with MFA, etc.), and enters the code.
    5. Meanwhile, the original device app is polling Azure AD. Once the user completes the sign-in on their phone, Azure AD gives the access token to the device app.
- **Recommendation:** **RECOMMENDED** for its specific and important use case.

## **4. OAuth 2.0 On-Behalf-Of (OBO) Flow**

- **Mapping to Our Previous Discussion:** This is the flow for a **Protected Web API** that needs to call another API.
- **Actors:**
    - **Client:** The initial application the user signed into (e.g., a SPA or Web App).
    - **Middle-Tier Service:** Your Web API that receives the call from the client.
    - **Authorization Server:** Azure AD.
    - **Downstream Resource Server:** The final API your middle-tier service needs to call (e.g., Microsoft Graph).
- **When to Use It:** This is an absolute necessity for **multi-tier or microservice architectures**. Use it whenever a service needs to call another service and preserve the identity and permissions of the original calling user.
- **How It Works (The Core Principle):** It's a token exchange mechanism.
    1. Your API receives an access token from the client application. The "audience" (`aud` claim) of this token is your API.
    2. Your API authenticates itself to Azure AD (using its `client_id` + secret) and presents the user's access token as proof of the user's identity.
    3. It requests a *new* access token, this time with the downstream API (e.g., Microsoft Graph) as the intended audience.
    4. Azure AD validates everything and issues the new token.
- **Recommendation:** **HIGHLY RECOMMENDED.** This is a critical pattern for modern, secure application design.

---

# **The Legacy / Not Recommended Flows**

- These are important to know for the AZ-204 exam, mostly so you know *why not* to use them.

## **5. OAuth 2.0 Implicit Grant Flow**

- **Mapping to Our Previous Discussion:** The **legacy** way of handling authentication for **SPAs**.
- **Actors:** User, SPA (Public Client), Azure AD, Resource Server.
- **When to Use It:** **You shouldn't use it for new applications.** It was created for browser-based apps at a time when browser restrictions prevented them from making cross-domain requests to a token endpoint (a limitation that no longer exists with CORS).
- **How It Worked:** It simplified the flow for JavaScript apps by returning the access token directly to the browser in the URL redirect fragment (e.g., `myapp.com/callback#access_token=...`). This meant no backend was needed to exchange a code.
- **Why It's Not Recommended:**
    - The access token is in the URL and can be exposed in browser history, server logs, or referrer headers.
    - It does not support refresh tokens, meaning the user would need to re-authenticate more often.
    - **The Authorization Code Flow with PKCE is more secure and has replaced it** as the standard for all public clients (SPAs, mobile apps).
- **Recommendation:** **DEPRECATED.** Avoid at all costs.

## **6. OAuth 2.0 Resource Owner Password Credentials (ROPC) Grant**

- **Mapping to Our Previous Discussion:** A special case, not mapped to our common scenarios.
- **Actors:** User, Client Application (must be highly trusted), Azure AD.
- **When to Use It:** **Almost never.** Its use cases are extremely narrow and risky. Maybe for a command-line tool where you can't use device code flow, or to migrate a very old legacy application that only understands username/password.
- **How It Works:** The application collects the user's literal username and password and sends them directly to Azure AD in a POST request.
- **Why It's STRONGLY DISCOURAGED:**
    - **Your app sees the user's credentials!** This is a massive security liability.
    - It completely breaks **Multi-Factor Authentication (MFA)**. You cannot complete an MFA challenge through this flow.
    - It prevents federated sign-on (you can't "Sign in with Google" or another corporate identity system).
    - It prevents Single Sign-On (SSO). The user has to type their password into your app every time.
- **Recommendation:** **AVOID.** Using this flow means you are disabling most of the modern security features that Azure AD provides.