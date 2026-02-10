# Mateo2 Auth Flows with Apigee

Excellent question. Integrating Apigee with Azure AD is a very common and powerful enterprise pattern. Apigee acts as the sophisticated, highly configurable security checkpoint in front of your APIs, while Azure AD acts as the authoritative source of identity.

There are two primary ways Apigee interacts with Azure AD, and understanding both is key to mastering this topic.

### The Analogy: The Corporate Campus Security Desk

Think of this entire system like a secure corporate campus:

- **Your Backend APIs:** These are the sensitive labs and offices inside the campus buildings.
- **Azure AD:** This is the central, government-run Department of Motor Vehicles (DMV). It is the ultimate authority that issues official, hard-to-forge ID cards (JWTs).
- **Apigee:** This is the main security desk in the lobby of your campus building. It has two distinct jobs that it must perform.

We will explore both of these jobs.

---

### Pattern 1: Apigee as a **Protector** (Validating Inbound Tokens)

This is the most common and fundamental pattern. An external client (a mobile app, a SPA, a partner system) shows up with an ID card, and Apigee's job is to verify it's real before letting them in.

**Use Case:** You want to protect your `CommentsApi` with Apigee. You want to ensure that only clients with a valid JWT issued by your Azure AD tenant can access it.

**OAuth Flow (for the client):** The client obtains a token using a standard flow like **Authorization Code with PKCE** (for a user/SPA) or **Client Credentials** (for a partner system). The important part is that the token's **audience (`aud` claim) must be the API** that Apigee is protecting.

**The Step-by-Step Flow:**

1. **Client -> Azure AD:** A mobile app user signs in. The app gets a JWT from Azure AD. The audience of this JWT is your `CommentsApi`.
2. **Client -> Apigee:** The mobile app makes a call to the Apigee proxy endpoint for your API. It includes the JWT in the `Authorization` header.
    
    ```
    GET <https://my-org.apigee.net/v1/comments>
    Authorization: Bearer eyJ0eXAiOiJKV... (the user's token)
    
    ```
    
3. **Apigee (The Verification):** Apigee executes a policy called **`VerifyJWT`**. This is the most important part. This policy performs several critical checks **without calling Azure AD**.
    - **A) Checks the Signature:** How does Apigee know the token wasn't faked? Azure AD publishes its public signing keys to a well-known URL (a JWKS - JSON Web Key Set - URI). Apigee fetches these keys (and caches them) and uses them to mathematically verify that the token was indeed signed by Azure AD and hasn't been tampered with.
    - **B) Checks the Issuer (`iss`):** It checks that the issuer claim in the token is correct (e.g., `https://sts.windows.net/YOUR_TENANT_ID/`).
    - **C) Checks the Audience (`aud`):** It checks that the token was intended for this API (e.g., `api://YOUR_COMMENTS_API_CLIENT_ID`). This prevents a token for "API A" from being used to access "API B".
    - **D) Checks the Expiry (`exp`):** It ensures the token has not expired.
    - **E) Checks Scopes/Roles:** It can extract the `scp` or `roles` claims and make decisions based on them.
4. **Apigee -> Backend API:** If all checks pass, Apigee forwards the request to your actual `CommentsApi`. Apigee can be configured to either pass the original JWT through or strip it and replace it with a simpler authentication mechanism that the backend understands.

**How to Configure this in Apigee:**

You use a `VerifyJWT` policy in your API Proxy's PreFlow. It's a snippet of XML.

```xml
<VerifyJWT name="Verify-AzureAD-JWT">
    <DisplayName>Verify Azure AD JWT</DisplayName>
    <Algorithm>RS256</Algorithm>
    <!-- The JWKS URI for Azure AD's public keys -->
    <JWKS uri="<https://login.microsoftonline.com/{YOUR_TENANT_ID}/discovery/v2.0/keys>"/>
    <!-- The issuer you expect in the token -->
    <Issuer><https://sts.windows.net/{YOUR_TENANT_ID}/></Issuer>
    <!-- The audience this token must be for -->
    <Audience>api://{YOUR_COMMENTS_API_CLIENT_ID}</Audience>
</VerifyJWT>

```

---

### Pattern 2: Apigee as a **Client** (Calling a Secured Backend)

This pattern solves the problem from your previous question. An external system calls Apigee using a simple API key, but Apigee then needs to turn around and call a backend API that is secured by Azure AD.

**Use Case:** A legacy partner system can only send API keys. Your new `SalesApi` is secured with Azure AD. Apigee must act as a mediator, accepting an API key and exchanging it for an Azure AD token.

**OAuth Flow:** Apigee itself uses the **Client Credentials Flow** to get an app-only token from Azure AD.

**The Step-by-Step Flow:**

1. **Legacy Client -> Apigee:** The partner system makes a call to an Apigee proxy endpoint.
    
    ```
    POST <https://my-org.apigee.net/v1/sales-report>
    x-api-key: aBcDeFg... (the partner's API key)
    
    ```
    
2. **Apigee (The Exchange):** Apigee validates the API key. Now, it needs to get its own token.
    - **A) `ServiceCallout` Policy:** Apigee uses a `ServiceCallout` policy to make a direct, backend `POST` request to Azure AD's `/token` endpoint.
    - **B) Build the Request:** This request is a standard Client Credentials flow: `grant_type=client_credentials`, `client_id` (Apigee's own ID), `client_secret` (Apigee's secret), and `scope`.
3. **Azure AD -> Apigee:** Azure AD validates Apigee's credentials and returns an **app-only** access token, which is then stored in a variable within the Apigee flow.
4. **Apigee (The Backend Call):** Apigee uses another policy, `AssignMessage`, to construct the request to the final backend. It adds the newly acquired token to the `Authorization` header.
5. **Apigee -> Backend API:** Apigee calls the backend `SalesApi`, which validates the app-only token and returns the data.

**How to Configure this in Apigee (Simplified Policies):**

1. **Verify API Key:** A standard policy to check the incoming key.
2. **Service Callout to get the token:**
    
    ```xml
    <!-- This policy makes a POST request to Azure AD -->
    <ServiceCallout name="Get-AzureAD-Token">
      <Request variable="azureTokenRequest">
        <Set>
          <Verb>POST</Verb>
          <FormParams>
             <FormParam name="grant_type">client_credentials</FormParam>
             <FormParam name="client_id">{azure.client_id}</FormParam> <!-- Stored securely in Apigee -->
             <FormParam name="client_secret">{azure.client_secret}</FormParam>
             <FormParam name="scope">api://{SALES_API_CLIENT_ID}/.default</FormParam>
          </FormParams>
        </Set>
      </Request>
      <Response>azureTokenResponse</Response> <!-- Store the response -->
      <HTTPTargetConnection>
         <URL><https://login.microsoftonline.com/{YOUR_TENANT_ID}/oauth2/v2.0/token></URL>
      </HTTPTargetConnection>
    </ServiceCallout>
    
    ```
    
3. **Extract the Token from the Response:** Use an `ExtractVariables` policy to get the `access_token` from the JSON response.
4. **Assign Message to call the backend:**
    
    ```xml
    <AssignMessage name="Assign-Backend-Request">
       <!-- Add the Authorization header with the token we just got -->
       <Add>
          <Headers>
             <Header name="Authorization">Bearer {extracted_access_token}</Header>
          </Headers>
       </Add>
       <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    </AssignMessage>
    
    ```
    

### Summary: The Expert's View

| Feature | Pattern 1: Apigee as Protector | Pattern 2: Apigee as Client |
| --- | --- | --- |
| **Analogy** | The security desk **verifying** a government-issued ID card. | The security desk **requesting its own special pass** from the government to open a door. |
| **Core Job** | Validate an inbound JWT from a client. | Obtain a new, outbound JWT for itself. |
| **Key Apigee Policy** | **`VerifyJWT`** | **`ServiceCallout`** |
| **OAuth Flow Used** | The client uses flows like Auth Code/PKCE. Apigee *validates* the token. | Apigee itself uses the **Client Credentials Flow**. |
| **Azure AD Setup** | The API has an App Registration. The *client* has an App Registration with permissions to the API. | **Apigee needs its own App Registration** with a client secret and application permissions to the downstream API. |
| **Performance** | Very high performance. Validation is local using cached public keys. | Lower performance. Involves a network hop to Azure AD to get a token (but this token can be cached in Apigee for its lifetime). |