# Tenant vs Multi Tenant

Of course. This is one of the most important foundational concepts to master. If you understand this deeply, all the authentication flows will suddenly click into place.

Let's use and expand our real-world analogy of the secure office building to make you an expert.

# **Part 1: The Single Tenant (Your Own Company's Building)**

Imagine your company, "Innovate Corp," has its headquarters in a secure, standalone office building.

- **The Building is the Tenant:** This entire building is your Azure AD **Tenant**. It's a completely isolated, self-contained environment. It has its own security system, its own employee directory, and its own rules.
- **The Tenant ID is the Building's Address:** The unique street address (e.g., 123 Innovation Drive) is the **Tenant ID**. It's the unambiguous identifier for your specific building.
- **The Employees are the Users:** Everyone who works for Innovate Corp is a **User** in your tenant.
- **The Front Desk is Azure AD:** The security desk in the lobby is the Azure AD authentication service. When an employee arrives, they must present their company ID badge (their credentials) to the security guard. The guard checks their photo and name against the official employee directory.

Now, let's introduce an Application.
Innovate Corp wants to install a new, modern coffee machine. This isn't just any coffee machine; it needs to know who you are to charge your department for the coffee.

- **The Coffee Machine is the Application:** It's a service that needs to interact with your employees.
- **Registering the App:** Before the machine can be installed, you must register it with building management (Azure AD). This is **App Registration**. You tell management:
    - "This is the 'Innovate Coffee Machine'."
    - "Its purpose is to serve coffee."
    - "To work, it only needs permission to read an employee's name and department from their ID badge." (This is requesting a **permission** or **scope** like User.Read).
- **Client ID:** Building management gives the machine a unique serial number sticker. This is the **Client ID**. It identifies this specific coffee machine.
- **Admin Consent:** The building manager (an Azure AD Admin) reviews the request. "Okay, it only reads the name and department. That's safe." The manager then grants **Admin Consent**, putting out a memo: "The new coffee machine is approved for everyone." Now, any employee can use it without needing special approval.

This entire setup is **Single-Tenant**. The coffee machine is wired *only* into the Innovate Corp employee directory. If an employee from the company next door tries to use their ID badge, the machine will say, "Error: Badge not recognized," because the Innovate Corp security desk has no record of them.

**Key Takeaway:** A single-tenant application is custom-built for and exclusively trusts the users from **one specific tenant**.

# **Part 2: The Multi-Tenant World (A Universal SaaS Application)**

The company that makes the coffee machine, "Global Coffee Services," has a brilliant idea. Their machine is great, and they want to sell it to *any company in the world*. They want to build one universal model that works in any compatible office building.

This is a **Multi-Tenant Application**.

- **The Universal Blueprint is the App Registration:** Global Coffee Services creates a *single* App Registration in their *own* Azure AD tenant. But during registration, they check a critical box: **"Accounts in any organizational directory (Any Azure AD directory - Multitenant)"**. This is like creating a universal blueprint for their coffee machine, not a machine for a specific building. This blueprint has one universal Client ID.

**The First Customer: "Dynamic Data Inc."**
Dynamic Data wants to install one of these coffee machines in their building (their own separate tenant).

1. **The "Installation" is Admin Consent:** The IT Admin at Dynamic Data (the building manager) must approve the installation. They go through a consent process. Azure AD shows them a prompt based on the universal blueprint: "The 'Global Coffee Machine' wants to be installed in your organization and requires permission to read your users' names and departments."
2. **The Admin Clicks "Accept":** This is the magic moment. By consenting, the admin is essentially creating a **local record** of the global application inside their own tenant. This local record is called a **Service Principal**. Think of it as Dynamic Data's official registration and approval of the universal coffee machine, allowing it to connect to their security desk.
3. **The Machine is Installed:** The machine is now physically in the Dynamic Data building.

**How it Works in Practice**

- **An Innovate Corp Employee:** Walks up to the machine in the Innovate Corp building. They tap their badge. The machine is smart enough to say, "Ah, this is an Innovate Corp badge. I'll talk to the Innovate Corp security desk ([login.microsoftonline.com/innovatecorp.com](http://login.microsoftonline.com/innovatecorp.com))." The user is authenticated.
- **A Dynamic Data Employee:** Walks up to the machine in the Dynamic Data building. They tap their badge. The machine says, "This is a Dynamic Data badge. I need to talk to the Dynamic Data security desk ([login.microsoftonline.com/dynamicdata.com](http://login.microsoftonline.com/dynamicdata.com))." The user is authenticated.

The application code is **exactly the same**. The Client ID is the same. The only difference is that the application now accepts users from *any tenant* that has installed (consented to) it.

# **Summary Table: Expert-Level Understanding**

| Concept | Single-Tenant (The Custom Building App) | Multi-Tenant (The Universal SaaS App) |
| --- | --- | --- |
| **App Registration** | Configured for "Accounts in this organizational directory only". | Configured for "Accounts in any organizational directory". |
| **Purpose** | A Line-of-Business (LOB) app for your own organization. | A Software-as-a-Service (SaaS) product for any customer. |
| **User Sign-in** | Only users from your specific tenant can sign in. The login URL often includes your Tenant ID. | Users from ANY tenant can sign in (if their admin has consented). The login URL uses a generic `/common` or `/organizations` endpoint. |
| **Consent** | An admin in your tenant grants consent once. | The admin of **each customer tenant** must grant consent to "install" the app in their organization. |
| **Service Principal** | One App Registration has **one** Service Principal in your home tenant. | The one App Registration has **many** Service Principals—one in your home tenant, and one in every customer tenant that uses the app. |
| **Analogy** | A custom coffee machine built exclusively for the Innovate Corp building. | A universal coffee machine model sold by a global company, installable in any office building. |

# **Why This is CRUCIAL for Understanding Authentication Flows**

When you see an authentication flow like the On-Behalf-Of flow for a multi-tenant app:

1. The Web App (Service A) will redirect the user to a `/common` endpoint to allow anyone to sign in.
2. After the user signs in, the token issued will contain a **Tenant ID claim (tid)**.
3. Your Backend API (Service B) receives this token. It looks at the `tid` claim to know *which customer's tenant* the user is from.
4. When it performs the OBO flow, it uses that specific `tid` in the request to Azure AD, ensuring it gets a Graph token that is valid for that specific user within their own tenant's data.

By internalizing this building analogy, you've moved from just knowing the definition to understanding the architecture and security boundaries, which is the key to mastering any authentication flow you'll encounter in AZ-204.