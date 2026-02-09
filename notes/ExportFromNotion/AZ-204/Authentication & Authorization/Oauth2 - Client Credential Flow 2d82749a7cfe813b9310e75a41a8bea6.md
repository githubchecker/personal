# Oauth2 - Client Credential Flow

# **The "Why": The Security Principle**

- The Client Credentials flow is used when an **application needs to access a resource using its own identity**. There is **no user** present. The application itself is the one being authenticated and authorized. The key principle is that the application is a trusted, confidential client with its own credentials (a secret or a certificate).

---

# **The Practical Example: "ReportGen Nightly Service"**

- Let's design a common backend scenario:
    - **ReportGen Nightly Service:** A background worker service (e.g., a Console App, a PowerShell script, an Azure Function on a timer). Its job is to run every night at 2 AM, fetch sales data, and generate a PDF report.
    - **Sales API:** Your custom, protected backend API. It exposes an endpoint like `/api/sales/summary` that contains the data the reporting service needs.

---

# **The Actors in Our Story**

- **1. Client Application (The Confidential Client):** The "ReportGen Nightly Service". This is the actor that needs to authenticate. It is confidential because it runs on a secure server where it can protect its secrets.
- **2. Authorization Server:** Azure Active Directory (AAD).
- **3. Resource Server:** Your custom "Sales API".
- There is **no Resource Owner (User)** in this flow. This is the defining characteristic.

---

# **The Analogy: The Automated Brinks Armored Truck**

- Think of this like an automated, robotic Brinks armored truck that moves money between bank branches overnight.
    - **The Robot Truck (ReportGen Service):** The client application. It operates on a schedule with no driver.
    - **The DMV (Azure AD):** The central authority that issues vehicle registrations and license plates.
    - **The Bank Vault (Sales API):** The secure resource the truck needs to access.
    - **The Truck's Registration & Key (Client ID & Secret):** The truck has its own unique vehicle registration number and a special electronic key that proves it is an authentic Brinks truck.
    - **The Access Code for the Vault (Access Token):** When the truck arrives at the vault, it transmits its credentials and gets a one-time-use code to open the vault door for that specific night. This code is for the *truck itself*, not for a human driver.

---

# **The Step-by-Step Flow in Action**

- This flow is very direct and consists of only one exchange.
    - **Step 1: The Service Requests a Token**
        - At 2 AM, the "ReportGen Nightly Service" wakes up. The very first thing it does is make a direct, server-to-server POST request to Azure AD's token endpoint to get an access token.
        - **ReportGen Service sends a POST Request to Azure AD:**
            
            ```
            POST <https://login.microsoftonline.com/{your-tenant-id}/oauth2/v2.0/token>
            
            Content-Type: application/x-www-form-urlencoded
            
            grant_type=client_credentials
            &client_id={reportgen_service_client_id}
            &client_secret={the_reportgen_service's_secret}
            &scope=api://{sales_api_client_id}/.default
            
            ```
            
            - `grant_type=client_credentials`: "I am an application authenticating with my own credentials."
            - `client_id` & `client_secret`: This is the application's own username and password, proving its identity. (Using a certificate is the even more secure best practice).
            - `scope=api://{sales_api_client_id}/.default`: This is a special scope used **only** for the Client Credentials flow. It means, "Give me an access token for the Sales API with **all** the application permissions that have been pre-consented to me by an administrator."
    - **Step 2: Azure AD Validates and Issues an App-Only Token**
        - Azure AD receives the request.
            1. It validates the `client_id` and `client_secret`.
            2. It checks which application permissions the ReportGen Service has been granted for the Sales API.
            3. It issues a special "app-only" access token.
        - **Azure AD's JSON Response to the Service:**
            
            ```json
            {
              "token_type": "Bearer",
              "expires_in": 3599,
              "access_token": "eyJ0eXAiOiJKV..."
            }
            
            ```
            
            - Notice: **No refresh token** is issued in the Client Credentials flow. When the token expires, the service simply performs the exact same request again to get a new one.
    - **Step 3: The Service Calls Your Custom API**
        - The "ReportGen Service" now has its access token. It uses it to make a secure call to your "Sales API".
        - **ReportGen Service calls the Sales API:**
            
            ```
            GET <https://api.mysales.com/api/sales/summary>
            
            Authorization: Bearer eyJ0eXAiOiJKV...
            
            ```
            
    - **Step 4: The Sales API Validates the App-Only Token**
        - Your "Sales API" must be configured to validate this token.
            1. It validates the signature, issuer, and **audience (aud)** claim, which must be its own Application ID URI.
            2. **CRITICAL:** It inspects the token for a **roles** claim. An app-only token does **not** have a scp (scope) claim. The roles claim will contain a list of the application permissions granted, like `["Reports.Generate"]`.
            3. Your API's authorization logic checks if the roles claim contains the required permission for that specific endpoint. If it does, the request is successful.

---

# **What Needs to be Done in Azure?**

- You need two App Registrations.
    - **1. App Registration for the "Sales API" (The Resource Server):**
        - Go to Azure AD -> App Registrations -> New registration. Name it Sales-API.
        - Go to the **"Expose an API"** blade.
            - Set the Application ID URI (e.g., `api://{sales_api_client_id}`).
            - Scroll down to **"App roles"** and click **"Create app role"**. This is how you define an **Application Permission**.
                - **Display name:** Generate Sales Reports
                - **Allowed member types: Applications** (this is the key difference from a delegated scope!).
                - **Value:** Reports.Generate (This is the name of the role/permission that will appear in the token's roles claim).
                - **Description:** "Allows a service to generate system-wide sales reports."
            - Click Apply.
    - **2. App Registration for the "ReportGen Nightly Service" (The Client):**
        - Create another registration named ReportGen-Nightly-Service.
        - Go to the **"Certificates & secrets"** blade.
            - Click "New client secret". Copy the value. This is the service's "password".
        - Go to the **"API permissions"** blade.
            - Click "Add a permission" -> "My APIs" -> find and select Sales-API.
            - Select **Application permissions**. You will see the Reports.Generate role you just created. Check the box.
            - Click "Add permissions".
            - **CRITICAL FINAL STEP:** An administrator **must** grant consent for this permission. Click the **"Grant admin consent for [Your Tenant]"** button. This is because application permissions are powerful and cannot be granted by regular users.

---

# **Becoming an Expert: Key Concepts**

- **App Roles vs. Scopes:** This is the most important concept to master.
    - **Scopes** (`scp` claim) are for **Delegated** permissions. A user *delegates* authority to an app.
    - **App Roles** (`roles` claim) are for **Application** permissions. An app is granted a *role* like a user would be.
    - Your API's authorization code must check for the roles claim for M2M calls.
- **Admin Consent is Mandatory:** Because application permissions are not tied to a signed-in user's privileges, they are often broad (e.g., "Read all mailboxes"). Therefore, a tenant administrator must always explicitly approve them.
- **Certificates over Secrets:** In production, using a client certificate instead of a client secret is the best practice for security. This avoids having a password-like secret stored in config files. The ReportGen Service would load the certificate from a secure store and use it to sign a request to Azure AD, proving its identity.
- **Use Cases:** Any non-interactive process.
    - Scheduled jobs, background workers, cron jobs.
    - System-to-system integrations in a microservices architecture.
    - Daemon processes that need to monitor or sync data.
    - DevOps scripts that need to manage Azure resources via an API.