# Delegate vs Application Permission

Of course. This is arguably the **most important foundational concept** in the entire Azure AD security model. If you master this, every OAuth flow will become clear.

Let's break this down from the ground up to make you an expert.

# **The Core Analogy: The Personal Assistant vs. The Nightly Janitor**

Imagine your API (like Microsoft Graph) is a secure corporate building.

1. **Delegated Permission is like a Personal Assistant.**
    - You hire a personal assistant (the **Application**).
    - You (the **User**) give the assistant a keycard.
    - Crucially, this keycard is a copy of *your* keycard. The assistant can only enter the rooms *you* are allowed to enter. They cannot enter the CEO's office if you don't have access.
    - The assistant always acts "**on behalf of you.**" Their access is *delegated* from you.
2. **Application Permission is like a Nightly Janitor.**
    - The building management hires a janitorial service (the **Application**).
    - There is no single employee present at night.
    - The janitor is given a special master key that only opens specific rooms (e.g., all common areas and standard offices, but not the server room).
    - The janitor acts on its "**own identity.**" Its permission is inherent to its role, not delegated from any user. It can access *multiple* people's offices.

---

# **In-Depth Breakdown: Delegated Permissions**

- **The Core Concept:** The application acts on behalf of a signed-in user. The app can do nothing more than what the signed-in user is allowed to do.
- **The Key Phrase to Remember:** "On behalf of the user."

**Actors**

- **User (Resource Owner):** The person who signs into the application.
- **Client Application:** The app the user is interacting with (e.g., a web app, mobile app).
- **Resource API:** The API the app wants to call (e.g., Microsoft Graph).

**Relevant OAuth 2.0 Flows**
This permission type is used in **every flow where a user is present**:

- Authorization Code Grant (and with PKCE)
- On-Behalf-Of (OBO) Flow
- Device Code Flow
- Implicit Grant (Legacy)

It is **NEVER** used with the Client Credentials Flow, because that flow has no user.

**Practical Example**

- **Use Case:** A custom web app needs to display the currently logged-in user's upcoming meetings.
- **Scenario:**
    1. Jane signs into "[MyMeetingsWebApp.com](http://mymeetingswebapp.com/)".
    2. The web app requests permission to read Jane's calendar.
    3. Jane consents.
    4. The app receives an access token. This token contains claims identifying both Jane (`oid`, `sub`) and the app (`appid`). It also contains the delegated permission scope (`scp: Calendars.Read`).
    5. The app uses this token to call Microsoft Graph: `GET /me/events`.
    6. Microsoft Graph checks the token. It sees that "MyMeetingsWebApp" is calling **on behalf of Jane** with permission to read calendars. It then returns **only Jane's** calendar events.

**How Scopes Look**
They are typically user-centric and use dot-notation, like `User.Read`, `Mail.Read`, `Calendars.ReadWrite`, `Files.ReadAll`.

**Azure AD Configuration**

1. Go to your App Registration in the Azure AD portal.
2. Navigate to **API permissions**.
3. Click **+ Add a permission**.
4. Select the API (e.g., **Microsoft Graph**).
5. Choose **Delegated permissions**.
6. Find and check the boxes for the permissions your app needs (e.g., `Calendars.Read`).
7. Click **Add permissions**.

**The Consent Experience**
A prompt is shown to the user during sign-in, saying, *"MyMeetingsWebApp would like to: Read your calendars."* The user must agree. If the permission is highly privileged (like `Mail.ReadWrite.All`), an administrator may need to grant consent on behalf of all users.

---

# **In-Depth Breakdown: Application Permissions**

- **The Core Concept:** The application acts as itself, using its own identity. It has no signed-in user. This is used for backend services, daemons, and automation.
- **The Key Phrase to Remember:** "As the application itself."

**Actors**

- **Client Application:** The backend service, script, or daemon app.
- **Resource API:** The API the app wants to call (e.g., Microsoft Graph).
- **(No User is present during the API call)**

**Relevant OAuth 2.0 Flows**
This permission type is used **exclusively** with one flow:

- **Client Credentials Grant**

**Practical Example**

- **Use Case:** A nightly background service that needs to scan a specific support mailbox ([support@mycompany.com](mailto:support@mycompany.com)) for new emails and create tickets in a separate system.
- **Scenario:**
    1. At 2 AM, the "TicketCreatorService" wakes up.
    2. It authenticates directly with Azure AD using its own Client ID and a Client Secret (or certificate).
    3. It requests a token for Microsoft Graph with the Application permission `Mail.Read`.
    4. Azure AD returns an access token. This token identifies **only the application** (`appid`). It has no user information. Its permission scope will be in the `roles` claim (e.g., `roles: [Mail.Read]`).
    5. The service uses this token to call Microsoft Graph: `GET /users/support@mycompany.com/messages`.
    6. Microsoft Graph checks the token. It sees that "TicketCreatorService" is calling with the approved application-level permission to read mail for any user (that it has been granted access to). It returns the emails from the support mailbox.

**How Scopes Look**
They are typically broader and often contain `.All`, signifying access to more than one user's data, like `Mail.ReadWrite.All`, `Directory.Read.All`, `User.Read.All`.

**Azure AD Configuration**

1. Go to your App Registration in the Azure AD portal.
2. Navigate to **API permissions**.
3. Click **+ Add a permission**.
4. Select the API (e.g., **Microsoft Graph**).
5. Choose **Application permissions**.
6. Find and check the boxes for the permissions your app needs (e.g., `Mail.Read`).
7. Click **Add permissions**.

**The Consent ExperienceAdmin Consent is ALWAYS required.** There is no user to ask for consent during a sign-in flow. An Azure AD administrator *must* go to the API permissions page and click the "**Grant admin consent for [Your Tenant]**" button. This pre-approves the application to use these powerful permissions.

---

# **Expert Level Key Concept: The "Effective Permissions" Intersection**

This is the most critical rule for **Delegated Permissions**.

The final, **effective permission** of an API call is the **intersection** (the least privileged combination) of the user's own permissions AND the application's delegated permissions.

**Example:**

- **The App:** Your app has been granted the delegated permission `Mail.ReadWrite` (it can read and send mail).
- **The User:** A contractor, "Bob," signs into your app. Bob's user account in your organization has a policy applied that **only allows him to read mail, not send it**.

**The Result:** When the app makes a call to Microsoft Graph on behalf of Bob, it can successfully **read** his mail. If the app tries to use the same token to **send** an email as Bob, Microsoft Graph will **reject the request with a "Permission Denied" error**.

Why? Because the effective permission is the intersection:

*(App can Read/Write) ∩ (Bob can only Read) = **Read-only access**.*

This is a powerful security feature ensuring that a user can never use an app to escalate their own privileges. For Application permissions, this concept doesn't apply because there is no user in the equation. The app's permission is absolute.