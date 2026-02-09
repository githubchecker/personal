# Oauth2 - Auth Code with PKCe  Flow

# **The "Why": What Problem Does PKCE Solve?**

- First, you must understand *why* this flow exists.
    - In the old days, simple browser-based apps (SPAs) used a flow called the "Implicit Grant". It was simple, but had a major security flaw: the access token was returned directly in the URL from the authentication server. This meant the token could be leaked through browser history, server logs, or referrer headers.
    - The regular "Authorization Code" flow was more secure because it returned a temporary code first, which was then exchanged for a token. However, that exchange required a `client_secret` to prove the app's identity. But where would you store a `client_secret` in a public client like a JavaScript app? You can't! It would be visible to everyone.
    - **PKCE (Proof Key for Code Exchange)** was invented to solve this exact problem. It's an extension to the Authorization Code flow that allows public clients to prove they are the legitimate initiator of the flow **without needing a pre-configured secret.**

---

# **The Practical Example: "NoteTaker Pro" SPA**

- Let's imagine you are building a **JavaScript Single-Page Application (SPA)** called "NoteTaker Pro". This app runs entirely in the user's browser and needs to call the Microsoft Graph API to save the user's notes to their OneDrive.

## **The Actors in Our Story**

1. **Resource Owner (The User):** Jane, who wants to use your app to write notes.
2. **Client Application (The Public Client):** Your "NoteTaker Pro" SPA running in Jane's browser. It is considered "public" because its source code is visible and it cannot keep a secret.
3. **Authorization Server:** Azure Active Directory (AAD). The ultimate authority on identity. It issues the tokens.
4. **Resource Server:** The Microsoft Graph API. It protects the user's files and requires a valid access token to grant access.

## **The Core Concept: The Secret Handshake**

- Before the flow starts, your SPA performs a "secret handshake" preparation in the background. This is the heart of PKCE.
    1. `code_verifier`: Your SPA generates a long, random, unpredictable string. This is the **secret key**. Think of it like a password you invent on the spot.
        - *Example code_verifier: aB7dF9gHJ3k5lM7nO9pQ1rS3tV5wX7yZ (in reality, it's much longer)*
    2. `code_challenge`: Your SPA then takes the `code_verifier`, hashes it using a SHA-256 algorithm, and encodes it. This is the **publicly visible lock**. You can show the lock to anyone, but only the person with the original secret key (`code_verifier`) can prove they created it.
        - *Example code_challenge: sha256_and_base64_encode("aB7dF9gHJ3k5lM7nO9pQ1rS3tV5wX7yZ") -> E832...aFd7*

---

# **The Step-by-Step Flow in Action**

Here is exactly what happens when Jane clicks "Log In".

### **Step 1: The App Initiates the Login**

- Jane clicks the login button. Your "NoteTaker Pro" SPA (the client) creates the `code_verifier` and `code_challenge`. It then redirects Jane's browser to Azure AD with a special URL.
    - **Browser Redirects to Azure AD:**
        
        ```
        GET <https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize>
          ?client_id={your_spa_client_id}
          &response_type=code
          &redirect_uri=http://localhost:3000/callback
          &scope=openid profile offline_access Files.ReadWrite
          &code_challenge={the_generated_code_challenge}
          &code_challenge_method=S256
        
        ```
        
        - `response_type=code`: "I want to do the Authorization Code flow."
        - `scope`: **The Delegated Permissions** your app is requesting. "I need permission to read the user's profile (profile) and read/write files (Files.ReadWrite)."
        - `code_challenge`: The SPA sends the **public lock** to Azure AD.
        - `code_challenge_method=S256`: "This lock was created using SHA-256."

### **Step 2: User Authenticates and Consents**

- Azure AD receives the request.
    1. It prompts Jane to enter her username and password (and MFA).
    2. If it's her first time, it shows her a consent screen: *"NoteTaker Pro would like to: Sign you in and read your profile, Read and write your files."*
    3. Jane accepts.
    4. **Crucially, Azure AD saves the `code_challenge`** and associates it with the temporary authorization code it's about to generate.

### **Step 3: Azure AD Returns the Authorization Code**

- Azure AD redirects Jane's browser back to your application's `redirect_uri` with the temporary code.
    - **Browser is Redirected Back to the SPA:**`http://localhost:3000/callback?code=0.AXA...8aQc`
    - This code is useless by itself. An attacker who steals it still can't get a token.

### **Step 4: The SPA Securely Exchanges the Code for a Token**

- Your SPA's JavaScript code, running in the browser, receives the code. It now makes a direct, behind-the-scenes POST request to Azure AD's `/token` endpoint.
    - **SPA sends a POST Request to Azure AD:**
        
        ```
        POST <https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token>
        
        Content-Type: application/x-www-form-urlencoded
        
        grant_type=authorization_code
        &client_id={your_spa_client_id}
        &code={the_code_from_step_3}
        &redirect_uri=http://localhost:3000/callback
        &code_verifier={the_original_secret_key}
        
        ```
        
        - `grant_type=authorization_code`: "I'm here to exchange an authorization code."
        - `code_verifier`: **This is the moment of truth!** The SPA sends the **original secret key** that was never sent before.

### **Step 5: Azure AD Validates and Issues Tokens**

- Azure AD receives the request and performs the final security check:
    1. It finds the `code_challenge` it saved in Step 2 for the given code.
    2. It takes the incoming `code_verifier` from the request, hashes it using SHA-256.
    3. **It compares the two hashes.** If they match, it proves the client making the request now is the same one that started the process in Step 1.
    4. If they match, Azure AD returns the precious tokens.
    - **Azure AD's JSON Response to the SPA:**
        
        ```json
        {
          "token_type": "Bearer",
          "scope": "openid profile offline_access Files.ReadWrite",
          "expires_in": 3599,
          "access_token": "eyJ0eXAiOiJKV...",
          "refresh_token": "0.AXA..."
        }
        
        ```
        

### **Step 6: The SPA Calls the API**

- Your "NoteTaker Pro" SPA now has an `access_token`. It can use this token in an "Authorization" header to make secure calls to the Microsoft Graph API to save Jane's notes.

---

# **What Needs to be Done in Azure?**

The configuration in Azure is surprisingly simple because the portal is optimized for this flow.

1. Go to **Azure AD -> App Registrations -> New registration**.
2. Give your app a name (e.g., "NoteTaker Pro SPA").
3. For "Supported account types," choose who can use your app.
4. **CRITICAL STEP:** For the "Redirect URI", select **Single-page application (SPA)** from the dropdown and enter your callback URL (e.g., `http://localhost:3000/callback`).
    - **By selecting "SPA", you are telling Azure AD to enforce the PKCE flow for your application. This is the magic button.**
5. Go to the **"API permissions"** blade for your new registration.
    - Click "Add a permission" -> "Microsoft Graph".
    - Select **Delegated permissions**.
    - Search for and add `Files.ReadWrite`. Add `openid` and `profile` if they aren't there.

That's it. Your application is now configured to use this secure flow.

---

# **Becoming an Expert: Key Concepts**

- **Why is it secure?** An attacker might steal the `authorization_code` from the URL in Step 3, but they can't complete the flow because they don't have the `secret code_verifier` which only exists in the legitimate user's browser session.
- **Use Cases:** This is the **ONLY recommended flow** for all modern public clients:
    - JavaScript Single-Page Apps (React, Angular, Vue).
    - Native Mobile Apps (iOS, Android).
    - Desktop Applications (WPF, .NET MAUI, Electron).
- **The Role of Scopes:** Scopes are always **Delegated** in this flow. They represent the permissions the *user* is granting the *application* to act on their behalf. The final `access_token` will contain a `scp` claim listing the granted scopes.
- **Use a Library (MSAL):** You should **never** implement this flow by hand in a real application. Use a library like `MSAL.js` (Microsoft Authentication Library for JavaScript). It will automatically handle:
    - Generating and storing the `code_verifier`.
    - Constructing the `code_challenge`.
    - Managing the redirects.
    - Handling the token exchange.
    - Securely storing and caching tokens.
    - Using the `refresh_token` to silently get new access tokens when they expire.

---

---

# **How Pkce can save if Attacker gets the codeverifier itself after the first request is sent to token endpoint. Once MIMT atacker get the first time sent codeverifier they can now replicate the call right?**

That is a brilliant, expert-level question. You have correctly identified the potential weak point in the chain and are forcing a deeper look at the security model. The short answer is: **you are absolutely right, but this specific attack is prevented by another, fundamental layer of web security: TLS (HTTPS).**

Let's break this down very clearly. Security is always about layers. PKCE was designed to solve one specific problem, while relying on another layer to solve a different one.

## **The Threat PKCE is Designed to Stop: Authorization Code Interception**

This is the primary threat. It assumes the attacker is on the **same device** as the user, not in the middle of the network.

**The Attacker:** A malicious mobile application or a malicious browser extension.

**The Attack Scenario:**

1. **Legitimate App (NoteTaker Pro)** starts the login flow and generates its `code_verifier` and `code_challenge`.
2. The user authenticates with Azure AD.
3. Azure AD redirects the user back to the browser with the `authorization_code` in the URL: `http://localhost:3000/callback?code=ABCD...`
4. **THE ATTACK:** The malicious browser extension is actively watching the user's browser tabs. It sees the redirect, and because the `authorization_code` is in the URL, it **steals the code ABCD...**.
5. **The Race:** Both the legitimate "NoteTaker Pro" SPA and the malicious extension now have the `authorization_code`.
    - **The Malicious Extension tries to exchange the code:** It sends a request to the `/token` endpoint with the stolen code. But it **does not have** the original `code_verifier` (which is stored securely in the "NoteTaker Pro" SPA's JavaScript memory). **The request fails.**
    - **The Legitimate SPA exchanges the code:** It sends its request with the code *and* the original `code_verifier`. **The request succeeds.**

**Conclusion:** PKCE perfectly defends against an attacker on the same "public" client device who can steal the authorization_code.

---

## **The Threat You Are Describing: Man-in-the-Middle (MitM) Attack**

This is a different, more powerful attack. It assumes the attacker is controlling the network between the user and the server.

**The Attacker:** A compromised router, a malicious public Wi-Fi hotspot, or sophisticated network-level snooping.

**The Attack Scenario You Proposed:**

1. "NoteTaker Pro" SPA gets the `authorization_code`.
2. It constructs the POST request to the `/token` endpoint. This request contains the `client_id`, the `code`, and the **`code_verifier`**.
3. The request is sent over the network.
4. **THE ATTACK:** The MitM attacker intercepts this traffic. They read the body of the POST request and now have the `client_id`, the `code`, and the `code_verifier`.
5. The attacker can now replicate the call and get the tokens for themselves.

**Why This Attack Fails: The Role of TLS (HTTPS)**

This is where the other critical layer of security comes in. **All modern OAuth 2.0 communication MUST happen over TLS (HTTPS).**

The `S` in HTTPS stands for "Secure". It provides two fundamental guarantees:

1. **Encryption:** When your SPA sends the POST request to `https://login.microsoftonline.com/...`, the entire contents of that request—including the headers and the body containing the `code_verifier`—are encrypted before they leave the browser. The MitM attacker sniffing the network traffic sees only scrambled, meaningless data. They **cannot read the `code_verifier`**.
2. **Authentication:** The browser validates the server's TLS certificate. This proves that you are actually talking to a legitimate server owned by `microsoftonline.com` and not an impostor server set up by the attacker.

So, while you are logically correct that *if an attacker could read the token request, they could compromise the flow*, **they cannot read it because it is encrypted by TLS.**

---

## **The Expert's Summary: Two Threats, Two Defenses**

Think of your security like a medieval castle. You need multiple types of defenses.

| Threat Scenario | The Attacker's Goal | The Primary Defense | How it Works |
| --- | --- | --- | --- |
| **Code Interception** (on the Public Client) | Steal the `authorization_code` from the browser URL or redirect. | **OAuth 2.0 PKCE** | The attacker gets the code but doesn't have the secret `code_verifier`, so the token exchange fails. |
| **Man-in-the-Middle** (on the Network) | Intercept the token exchange request to steal the `code_verifier`. | **Transport Layer Security (TLS/HTTPS)** | The attacker sees only encrypted traffic. They cannot read the contents of the request to steal the `code_verifier`. |

**Conclusion:** You've correctly reasoned that the `code_verifier` is a secret that must be protected. The PKCE flow is designed to protect it from being stolen on the client side, while the universal requirement of HTTPS protects it from being stolen on the network side. The two mechanisms work together to create a secure chain.

---

---

# **In case of Code Interception (on the Public Client) also the malicious extension gets the codeverifer after first request is sent from app right. Then can it not replicate?**

This is the most insightful question you can ask about this flow, and the answer gets to the very heart of how modern browsers are designed for security.

The answer is unequivocally **no**. The malicious extension **cannot** get the `code_verifier`.

You are correct that *if it could*, the entire PKCE flow would be broken. The reason it can't is due to a fundamental principle of browser security: **JavaScript Sandbox and Memory Isolation**.

## **The Technical Reality: Why the "Box" is Sealed**

1. **Isolated JavaScript Worlds:** When a browser extension injects a "content script" into a web page, that script does not run in the same context as the page's own JavaScript. It runs in an isolated world. They have access to the same shared DOM (the web page content), but they do **not** share memory, variables, or call stacks. A variable `mySecret` defined in the SPA's script is completely invisible and inaccessible to the extension's script. The `code_verifier` is just a variable.
2. **Private Network Requests:** When the SPA's JavaScript calls `fetch()` or uses `XMLHttpRequest` to make the POST request, the construction of that request, including its body, happens within the SPA's private memory space. The browser's engine takes this request object and hands it off internally to its networking stack. The extension's code has no hook or API to intercept that handoff and read the POST body. It's a private operation between the originating script and the browser's core networking engine.
3. **The Flow Revisited with Isolation in Mind:**
    - **Step 1:** The "NoteTaker Pro" SPA generates the `code_verifier`. It is now stored in a variable in the SPA's private JavaScript memory. **The extension cannot see this.**
    - **Step 2:** The user logs in, and the browser is redirected. The URL contains the `authorization_code`. **Both the SPA and the malicious extension can read this from the URL bar.** This is the public information.
    - **Step 3:** The SPA's code runs. It takes the public code from the URL and retrieves its private `code_verifier` from its memory. It constructs the POST request body.
    - **Step 4:** The SPA passes the complete request object to the browser's fetch API. At this point, the request and its payload are handled by the browser's internal engine. **The malicious extension cannot inspect the payload of this in-flight, in-memory request.** The next time the data is "in the clear" is on the Azure AD server after TLS decryption.

## **What *Can* a Malicious Extension Do? (The Real Threats)**

This doesn't mean malicious extensions aren't dangerous. They are, but they attack in different ways. A malicious extension could:

- **Log Keystrokes:** Steal the user's password as they type it into the Azure AD login page. This bypasses OAuth entirely.
- **Scrape the DOM:** After the legitimate flow is complete, if the SPA carelessly writes the received `access_token` to the HTML, the extension could read it from there. (This is why you never do that).
- **Steal from Insecure Storage:** If the SPA stores the tokens in `localStorage` or `sessionStorage`, a malicious extension (with the right permissions) can access that storage and steal the tokens after the fact. (This is why MSAL libraries often prefer to keep tokens in memory to mitigate this).

But what it **cannot** do is peer into the memory of the page's main JavaScript thread or inspect the body of its outgoing POST requests. That privacy is a cornerstone of web browser security, and it is precisely this principle that keeps the `code_verifier` safe from other scripts on the same page.