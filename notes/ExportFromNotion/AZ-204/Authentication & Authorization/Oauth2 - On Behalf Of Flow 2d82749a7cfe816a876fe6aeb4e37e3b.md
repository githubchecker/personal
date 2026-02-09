# Oauth2 - On Behalf Of Flow

# **You're looking to become an expert in the OAuth 2.0 On-Behalf-Of (OBO) flow with Microsoft Graph API**

- Specifically for a web app displaying user mail. This is an advanced and very common scenario for secure, multi-tier applications. Let's break it down step-by-step.

---

# **Understanding the On-Behalf-Of Flow**

- The OBO flow is used when a service (let's call it Service B) needs to call another service (Service C, like Microsoft Graph) on behalf of a user who has already authenticated to an initial service (Service A, your web app).
    - The crucial part is that Service B never sees the user's credentials.
    - Instead, it uses an access token it received from Service A to obtain a new access token for Service C.
- **Why OBO for your scenario?**
    - Imagine your web app (Service A) needs to display user emails. If your web app directly called Microsoft Graph, it would hold the access token for Graph. This is acceptable for simple apps.
    - However, what if your web app has a separate backend API (Service B) that handles business logic and *then* needs to fetch emails?
        - In this case, you don't want your backend API to directly prompt the user for credentials.
        - Instead, you want it to act "on behalf of" the user who already authenticated with your web app.
- **Actors in the OBO Flow:**
    1. **User:** The end-user who wants to see their emails.
    2. **Web App (Client Application - Service A):** Your front-end web application (e.g., React, Angular, [ASP.NET](http://asp.net/) Core MVC). It authenticates the user and calls your backend API.
    3. **Backend API (Confidential Client - Service B):** Your server-side API. This is where the OBO flow primarily occurs. It receives an access token from the web app and exchanges it for a new token to call Microsoft Graph.
    4. **Azure Active Directory (AAD):** Microsoft's identity platform, responsible for issuing tokens.
    5. **Microsoft Graph API (Resource Server - Service C):** The API that provides access to user data.
- Let's trace the requests in order:

---

# **Prerequisites: Azure AD App Registrations**

- Before any requests, you need two application registrations in Azure AD:
    1. **Web App (Client App - Service A):**
        - **Type:** Web application.
        - **Redirect URI:** Where AAD sends the authentication response (e.g., `https://localhost:5001/signin-oidc`).
        - **API Permissions:** No direct Graph permissions here. It will request permission to call your Backend API (Service B). You'll define an "Exposed API" for Service B and grant your Web App permission to it.
    2. **Backend API (Confidential Client - Service B):**
        - **Type:** Web API.
        - **Expose an API:** Define an application-specific scope (e.g., `api://<Backend_API_App_ID>/access_as_user`). This is what your Web App will request permission to.
        - **API Permissions:** Grant **Delegated** permissions to Microsoft Graph. For showing user mail, you'll need Mail.Read. Ensure "Grant admin consent" is done if required.
        - **Client Secret/Certificate:** Generate a client secret or upload a certificate. This is crucial for Service B to authenticate itself to AAD.

---

# **The Flow of Requests**

## **Phase 1: User Authentication & Web App Calling Backend API**

### **1. User Sign-in & Consent (OAuth 2.0 Authorization Code Flow)**

- **Action:** The user visits your web app (Service A). The web app redirects the user's browser to Azure AD for authentication.
- **Request (User's Browser to Azure AD):**
    
    ```bash
    GET <https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize>
    ?client_id=<Web_App_Client_ID>
    &response_type=code
    &redirect_uri=<Web_App_Redirect_URI>
    &response_mode=form_post // or query, fragment
    &scope=openid profile offline_access api://<Backend_API_App_ID>/access_as_user
    &state=12345
    &nonce=67890
    
    ```
    
    - `client_id`: The Application (client) ID of your Web App.
    - `response_type=code`: Indicates the Authorization Code flow.
    - `redirect_uri`: Where AAD will send the authorization code.
    - `scope`:
        - `openid profile offline_access`: Standard OIDC scopes for user identity and refresh tokens.
        - `api://<Backend_API_App_ID>/access_as_user`: This is the custom scope you defined for your Backend API. The Web App is requesting permission to call *your* Backend API.
- **AAD Action:** AAD authenticates the user. If it's the first time, it prompts the user for consent to the requested scopes.
- **Response (AAD to User's Browser - redirects to Web App Redirect URI):**
    
    ```bash
    POST <Web_App_Redirect_URI>
    Form Data:
    code=<authorization_code>
    state=12345
    session_state=<session_state>
    
    ```
    
    - `code`: A short-lived authorization code.

### **2. Web App Exchanging Authorization Code for Access Token (for Service B)**

- **Action:** Your Web App (Service A) receives the `authorization_code`. It then makes a server-side (confidential) request to AAD's token endpoint to exchange this code for an access token.
- **Request (Web App to Azure AD Token Endpoint):**
    
    ```
    POST <https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token>
    Content-Type: application/x-www-form-urlencoded
    
    client_id=<Web_App_Client_ID>
    &scope=openid profile offline_access api://<Backend_API_App_ID>/access_as_user
    &code=<authorization_code>
    &redirect_uri=<Web_App_Redirect_URI>
    &grant_type=authorization_code
    &client_secret=<Web_App_Client_Secret_If_Confidential_Or_PKCE_If_Public>
    // If it's a confidential web app (common for server-side code), it uses a client secret.
    // If it's a public client (e.g., SPA), it would use PKCE (code_verifier).
    
    ```
    
- **AAD Action:** AAD validates the authorization_code, client_id, redirect_uri, and client_secret.
- **Response (Azure AD to Web App):**
    
    ```json
    {
      "token_type": "Bearer",
      "scope": "openid profile offline_access api://<Backend_API_App_ID>/access_as_user",
      "expires_in": 3600,
      "ext_expires_in": 3600,
      "access_token": "eyJ0eXAiOiJKV...", // Access token for Service B
      "refresh_token": "...",    // Refresh token for the web app
      "id_token": "eyJ0eXAiOiJKV..."   // ID token containing user identity
    }
    
    ```
    
    - `access_token`: This token is issued *for your Backend API* (Service B). Its audience (aud claim) will be `api://<Backend_API_App_ID>`. This is the token your Web App will use to call your Backend API.

### **3. Web App Calls Backend API (with Access Token for Service B)**

- **Action:** The Web App (Service A) now has an access token that allows it to call your Backend API (Service B). It makes an authenticated request to your Backend API.
- **Request (Web App to Backend API):**
    
    ```
    GET <https://your-backend-api.com/api/mail>
    Authorization: Bearer eyJ0eXAiOiJKV... // The access_token from step 2
    
    ```
    
    - **Crucial:** Your Backend API must validate this incoming access token. It verifies the signature, issuer, and most importantly, that the aud (audience) claim in the token matches its own Application (client) ID.

---

## **Phase 2: Backend API Calling Microsoft Graph (On-Behalf-Of Flow)**

### **4. Backend API Initiates On-Behalf-Of Flow**

- **Action:** Your Backend API (Service B) receives the `access_token` from the Web App. It now needs an *another* access token, this time for Microsoft Graph, acting on behalf of the original user. It sends a request to AAD's token endpoint using the OBO grant type.
- **Request (Backend API to Azure AD Token Endpoint):**
    
    ```
    POST <https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token>
    Content-Type: application/x-www-form-urlencoded
    
    client_id=<Backend_API_Client_ID>
    &client_secret=<Backend_API_Client_Secret> // Or certificate credential
    &grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
    &assertion=<access_token_from_web_app> // The access_token received in step 3
    &scope=https://graph.microsoft.com/Mail.Read offline_access
    &requested_token_use=on_behalf_of
    
    ```
    
    - `client_id`: The Application (client) ID of your **Backend API**.
    - `client_secret`: The secret for your **Backend API**. This authenticates Service B to AAD.
    - `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`: This is the OBO grant type.
    - `assertion`: This is the incoming `access_token` from the Web App (the token whose aud was your Backend API's ID). AAD will validate this token.
    - `scope`: The permissions your Backend API needs for Microsoft Graph (e.g., Mail.Read). `offline_access` is included if you want a refresh token for Graph.
    - `requested_token_use=on_behalf_of`: Explicitly tells AAD this is an OBO request.
- **AAD Action:** AAD performs several critical checks:
    - Validates the assertion (the token from the web app): Is it valid? Is its audience (aud) the Backend API's client ID? Is it expired?
    - Checks if the Backend API (identified by client_id) has been pre-authorized by the user (via consent during step 1) to access the requested Graph scopes (Mail.Read). This is why your Backend API's app registration must have Mail.Read permissions.
    - If all checks pass, AAD issues a new access token.
- **Response (Azure AD to Backend API):**
    
    ```json
    {
      "token_type": "Bearer",
      "scope": "<https://graph.microsoft.com/Mail.Read> offline_access",
      "expires_in": 3600,
      "ext_expires_in": 3600,
      "access_token": "eyJ0eXAiOiJKV...", // Access token for Microsoft Graph
      "refresh_token": "...",    // Optional refresh token for MS Graph
    }
    
    ```
    
    - `access_token`: This is the token your Backend API will use to call Microsoft Graph. Its audience (aud claim) will be `https://graph.microsoft.com`.

### **5. Backend API Calls Microsoft Graph (with Access Token for Microsoft Graph)**

- **Action:** Your Backend API (Service B) now has the `access_token` for Microsoft Graph. It uses this token to fetch the user's mail.
- **Request (Backend API to Microsoft Graph):**
    
    ```
    GET <https://graph.microsoft.com/v1.0/me/messages?top=10>
    Authorization: Bearer eyJ0eXAiOiJKV... // The access_token from step 4
    ConsistencyLevel: eventual // Often recommended for some Graph queries
    
    ```
    
    - `Authorization`: The access token issued *by AAD for Microsoft Graph*.
- **Microsoft Graph Action:** Microsoft Graph validates the incoming access token. It checks the token's signature, issuer, audience (aud is `https://graph.microsoft.com`), and the scopes (Mail.Read). If valid, it fetches the user's mail.
- **Response (Microsoft Graph to Backend API):**
    
    ```json
    {
      "@odata.context": "<https://graph.microsoft.com/v1.0/$metadata#users('...')/messages>",
      "value": [
        {
          "id": "...",
          "subject": "Hello World!",
          "from": { ... },
          "bodyPreview": "...",
          // ... more mail data
        }
      ]
    }
    
    ```
    

### **6. Backend API Returns Mail Data to Web App**

- **Action:** Your Backend API (Service B) receives the mail data from Microsoft Graph. It then processes this data (if needed) and returns it to the Web App.
- **Response (Backend API to Web App):**
    
    ```json
    [
      { "subject": "Hello World!", ... },
      { "subject": "Meeting Reminder", ... }
    ]
    
    ```
    

### **7. Web App Displays Mail Data to User**

- **Action:** The Web App (Service A) receives the mail data from your Backend API and renders it in the user interface.

---

# **Becoming an Expert: Key Takeaways & Considerations**

- **Token Flow is Everything:** Understand **which** token is being passed at **which** step, and **who** is the intended audience (aud claim) of that token.
    - Token for **Service B:** Issued by AAD to Web App, aud is `api://<Backend_API_App_ID>`.
    - Token for **Service C (Graph):** Issued by AAD to Backend API, aud is `https://graph.microsoft.com`.
- **Security Context:** The OBO flow maintains the security context of the original user throughout the chain. All Graph calls are made *on behalf of* that specific user.
- **Confidential Clients are Key for OBO:** Your Backend API (Service B) **must** be registered as a confidential client in Azure AD (i.e., it must have a client secret or certificate) because it performs server-to-server calls to AAD's token endpoint.
- **Scopes and Permissions:**
    - **Web App scopes:** Requests permission to access your *Backend API's* custom scope.
    - **Backend API scopes (for Graph):** Requests permission to access *Microsoft Graph's* scopes (e.g., Mail.Read). These must be configured in the Backend API's Azure AD app registration.
- **Token Caching and Refresh:**
    - Both your Web App and Backend API will receive `refresh_tokens`.
    - **Web App:** Uses its `refresh_token` to get new access tokens for your Backend API without re-authenticating the user.
    - **Backend API:** Uses its `refresh_token` (if requested with `offline_access` scope in the OBO call) to get new access tokens for Microsoft Graph, again without bothering the user. This is crucial for long-running operations or when tokens expire.
- **Error Handling:** Implement robust error handling for all API calls. Token expiry, invalid scopes, network issues, and permission denied scenarios need to be gracefully managed.
- **Client Libraries:** Microsoft provides excellent client libraries (e.g., [MSAL.NET](http://msal.net/) for .NET, MSAL.js for JavaScript, @azure/msal-node for Node.js) that abstract away much of the low-level OAuth 2.0 protocol details, making implementation much easier and less error-prone. While understanding the raw requests is vital for expertise, use the libraries in production.
- **Never trust the client:** Your Backend API must always validate the incoming access token from the Web App before trusting it and proceeding with the OBO flow. This means checking signature, issuer, audience, and expiry.
- **Multi-tenancy:** If your application supports users from multiple Azure AD tenants, ensure your app registrations are configured as "Multi-tenant."

---

# **Q&A: App Registration & Permissions**

> Your Question: I am confused with App registration and permissions parts of each app. Will each app has single registration and Micorsoft GRaph Api permission is only need to be given to Service 2 but even though user is no represented to include scopes of GRraph Api. So allowing Service 2 to access Graph Api can be configured by suer him self if he is an admin or who does that?
> 
- You are absolutely right:
    - **Each app (Service A and Service B) needs its own, single App Registration in Azure AD.** They have different roles, different credentials, and different permissions.
    - **The Microsoft Graph permission (Mail.Read) is ONLY given to the Backend API (Service B).**
- The core of your question is the "magic" part: **How does the system get the user's permission for Mail.Read if the user is only interacting with the Web App (Service A), which doesn't ask for that permission?**
- The answer lies in how Azure AD constructs the consent screen. Let's break down the App Registrations and permissions in extreme detail.

## **App Registration 1: The Web App (Service A - The Client)**

- This is the user-facing application.
    - **Purpose:** Its only job in this flow is to authenticate the user and get an access token that is valid *only for calling your Backend API (Service B)*.
    - **Key Configurations:**
        - **Authentication:** Configured as a "Web" or "Single-page application (SPA)" with a Redirect URI (e.g., `https://myapp.com/callback`).
    - **API Permissions Blade:** This is the crucial part. On the permissions page for your Web App, you will **NOT** add any Microsoft Graph permissions like Mail.Read. Instead, you will do this:
        1. Click "Add a permission".
        2. Select the "APIs my organization uses" tab.
        3. Search for your Backend API (Service B) by name.
        4. Select it.
        5. Under "Delegated permissions", you will see the custom permission you created (e.g., `access_as_user`). Check this box.
        6. Click "Add permissions".
    - **Result:** The *only* permission this Web App requests is the right to call your Backend API on the user's behalf.
    - Think of it like a keycard. The Web App's keycard only opens the door to the Backend API's office. It doesn't open the filing cabinet (Microsoft Graph) inside that office.

## **App Registration 2: The Backend API (Service B - The Service)**

- This is your confidential, server-side API.
    - **Purpose:** Its job is to (1) expose an API that can be called by trusted clients like your Web App, and (2) have the necessary permissions to call downstream APIs (like Microsoft Graph) on behalf of the user.
    - **Key Configurations:**
        - **Expose an API:** You must define a scope here. This is how you create the custom `access_as_user` permission that the Web App will request. You'll set an "Application ID URI" (e.g., `api://<your-backend-client-id>`) and add a scope like `access_as_user`.
        - **Certificates & Secrets:** You must create a client secret or add a certificate. This is how the Backend API proves its own identity to Azure AD during the OBO flow.
    - **API Permissions Blade:** Here is where you define the permissions your API needs for Microsoft Graph.
        1. Click "Add a permission".
        2. Select "Microsoft Graph".
        3. Select "Delegated permissions". This is critical. It means your API will access Graph *as the signed-in user*, not as itself.
        4. Find and check the box for `Mail.Read`.
        5. Click "Add permissions".
    - **Result:** The Backend API now has the *potential* to read user mail, but it can only do so when it receives a valid user token from the Web App and successfully exchanges it.

## **Solving the Puzzle: The Combined Consent Screen**

- **So, who grants the Mail.Read permission and when?**
    - This happens during the very first step of the entire flow: **User Sign-in & Consent.**
- When the user signs into your Web App (Service A) for the first time, Azure AD does something very smart. It looks at the permission chain:
    1. It sees that the Web App is requesting the `api://.../access_as_user` permission.
    2. It then looks up the registration for that API (your Backend API, Service B).
    3. It sees that the Backend API itself has a *downstream dependency* and requires the `Mail.Read` permission for Microsoft Graph.
- Azure AD combines all these requirements into a **single consent screen** that is presented to the user. The user will see a prompt that says something like:
    - **Permissions requested**
    - This app would like to:
        - Sign you in and read your profile
        - **Access [Your Backend API Name] on your behalf** (This is the permission for Service B)
        - **Read your mail** (This is the downstream permission Service B needs for Graph)
- When the user clicks "Accept", they are granting consent for the *entire chain* of operations in a single step. They are allowing the Web App to call the Backend API, and they are allowing the Backend API to then call Microsoft Graph to read their mail.

## **Who Gives the Consent? User vs. Admin**

- Now for the final part of your question: *can a user do this, or does it have to be an admin?*
    - This depends on two things: the permissions being requested and the organization's policies.
    1. **User Consent:** For "low-impact" permissions (like User.Read, Mail.Read, Files.Read), an organization might allow regular users to consent for themselves. If so, any user can sign in and approve that combined consent screen.
    2. **Admin Consent is Required:** For "high-impact" permissions (e.g., Mail.Read.All which reads *all* mailboxes, or Directory.ReadWrite.All), admin consent is always required. Additionally, an organization's administrator can configure their Azure AD tenant to **require admin consent for *all* permissions**, disabling user consent entirely for security reasons.
- **How an Admin Grants Consent:**
    - **Interactive:** An admin can simply sign in to your application. They will see the same combined consent prompt, but with an extra checkbox that says "Consent on behalf of your organization." If they check this, every other user in the organization can then use the app without seeing the consent screen again.
    - **Proactive (Recommended):** The best practice is for an admin to go directly into the Azure Portal. They navigate to the API permissions blade of **both** your App Registrations and click the **"Grant admin consent for [Your Tenant Name]"** button. This pre-approves the application for all users in the organization.

---

# **Other refs**

- [Microsoft identity platform and OAuth2.0 On-Behalf-Of flow - Microsoft identity platform | Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)