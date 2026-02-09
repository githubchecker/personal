# App Service Certificates & TLS/SSL Bindings

# **Question X: App Service Certificates and TLS/SSL Bindings**

- **1. What is it?**
    - Securing an App Service with a certificate involves binding a custom domain to your web app and associating it with an SSL/TLS certificate. This enables HTTPS (https://) traffic, which encrypts data between the client (user's browser) and the server (your App Service). Azure provides three primary methods to obtain and manage these certificates:
        1. **App Service Managed Certificate:** A free, auto-renewing public certificate provided and managed entirely by Microsoft for your custom domain.
        2. **Purchased App Service Certificate:** A public certificate you buy directly through Azure, which is then stored and managed in Azure Key Vault.
        3. **Import from Key Vault:** A public or private certificate you acquire from any Certificate Authority (CA) and upload to Azure Key Vault, which your App Service can then reference.
- **2. Why is it used?**
    - The strategic purpose of using SSL/TLS certificates is to establish **trust and security** for your web application.
        - **Encryption:** It encrypts all data in transit, preventing eavesdropping and man-in-the-middle attacks. This is essential for protecting sensitive user data like login credentials, personal information, and payment details.
        - **Authentication:** It verifies the identity of your server. The browser trusts the Certificate Authority (e.g., DigiCert, Let's Encrypt), and the CA vouches that the certificate belongs to your domain, assuring users they are connected to the legitimate site.
        - **User Trust & SEO:** Modern browsers explicitly flag sites without HTTPS as "Not Secure," which erodes user trust. Search engines like Google also rank HTTPS-enabled sites higher.
- **3. How it works with Quick start details**
    - At a high level, the process is: **1. Add Custom Domain -> 2. Acquire Certificate -> 3. Bind Certificate to Domain**. The certificate's public key is sent to the browser during the TLS handshake. The browser uses it to encrypt a session key, which both parties then use for fast symmetric encryption for the rest of the session.
    - Here's how to implement the three main methods after you've configured your custom domain (`www.contoso.com`) in the App Service:
    - **Method 1: App Service Managed Certificate (Easiest)**
        - **Portal Steps:**
            1. Navigate to your App Service -> **TLS/SSL settings** -> **Private Key Certificates (.pfx)**.
            2. Click **+ Create App Service Managed Certificate**.
            3. Select the custom domain you want to secure from the dropdown.
            4. Click **Create**. Azure will validate domain ownership and issue the certificate. This process can take a few minutes.
            5. Once created, go to the **Bindings** tab, click **+ Add TLS/SSL Binding**, select your domain, choose the new managed certificate, select **SNI SSL** for the type, and click **Add Binding**.
        - **Azure CLI Example:**
            
            ```bash
            # Step 1: Create the certificate
            az webapp config ssl create --resource-group my-rg --name my-webapp --hostname www.contoso.com --name www.contoso.com
            
            # Step 2: Bind it to the webapp (command may differ slightly based on context, binding is often part of creation)
            az webapp config ssl bind --resource-group my-rg --name my-webapp --certificate-name www.contoso.com --ssl-type Sni
            
            ```
            
    - **Method 2: Import from Key Vault (Most Secure & Flexible)**
        - **Prerequisites:** You have a certificate (.pfx file) and have uploaded it as a secret to an Azure Key Vault. Your App Service must have a Managed Identity configured with Get and List secret permissions on the Key Vault.
        - **Portal Steps:**
            1. Navigate to App Service -> **TLS/SSL settings** -> **Private Key Certificates (.pfx)**.
            2. Click **+ Import Key Vault Certificate**.
            3. Select your subscription, the Key Vault containing your certificate, and the specific certificate secret.
            4. Click **Select**. The certificate will now appear in your list.
            5. Go to the **Bindings** tab and bind this imported certificate to your domain as described in Method 1.
        - **Azure CLI Example:**
            
            ```bash
            # Prereq: Grant App Service Managed Identity access to Key Vault
            # az keyvault set-policy ...
            
            # Import the certificate from Key Vault into the App Service
            az webapp config ssl import --resource-group my-rg --name my-webapp --key-vault MyKeyVault --key-vault-certificate-name MyContosoCert
            
            ```
            
            *(Method 3, Purchasing, is less common for developers and is a wizard in the portal under "App Service Certificates".)*
            
- **4. Developer Concepts (AZ-204 Focus)**
    - **Public vs. Private Certificates**
        - **Public Certificate:** Used to secure your website for public users (i.e., TLS/SSL binding). It's issued by a trusted public Certificate Authority (CA) and validates your domain's identity to browsers. **All three methods above deal with public certificates.**
        - **Private Certificate:** Used for internal, machine-to-machine authentication, not for browsers. Examples include client certificate authentication (mTLS) for an API or signing JWTs. A private certificate can be self-signed or issued by a private corporate CA.
    - **Using a Private Certificate in Code (C#):**
        - To use a private certificate in your C# code, you must first import it (usually via Key Vault) and then tell App Service to load it into the app's personal certificate store.
        1. **Configure App Setting:** Add an App Setting named `WEBSITE_LOAD_CERTIFICATES`. The value should be the **thumbprint** of the private certificate you imported. Use  to load all certificates.
        2. **C# Code to Find and Use the Certificate:**
            
            ```csharp
            public X509Certificate2 GetMyPrivateCertificate(string thumbprint)
            {
                // App Service loads the certificate into the current user's personal store.
                using (var store = new X509Store(StoreName.My, StoreLocation.CurrentUser))
                {
                    store.Open(OpenFlags.ReadOnly);
                    var certCollection = store.Certificates.Find(X509FindType.FindByThumbprint, thumbprint, validOnly: false);
                    if (certCollection.Count > 0)
                    {
                        return certCollection[0];
                    }
                }
                return null; // Or throw an exception
            }
            
            ```
            
    - **Automatic HTTPS Redirection:** In [ASP.NET](http://asp.net/) Core (Program.cs), ensure your app redirects HTTP requests to HTTPS: `app.UseHttpsRedirection();`
- **5. What are the Limitations and "Gotchas"?**
    - **App Service Managed Certificate:**
        - **No Wildcard:** Does not support wildcard domains (e.g., `.contoso.com`). You must create one for each subdomain.
        - **Apex Domain Issues:** Cannot be used for an apex/root domain (e.g., `contoso.com`) if that domain uses an A record. It requires a CNAME record, which often conflicts with the MX records needed for email.
    - **General:**
        - **Pricing Tier:** You cannot use custom domains or SSL on the **Free** or **Shared** tiers. **Basic** tier is the minimum.
        - **Certificate Rotation:** Purchased and manually imported certificates do not auto-renew. You are responsible for their lifecycle. Importing from Key Vault and configuring auto-renewal within Key Vault is the best practice for automation. App Service can sync automatically with the latest version in Key Vault.
        - **PFX Passwords:** When importing a .pfx file, it must be password protected. A blank password is not accepted.
- **6. Practical Use Cases & Scenarios**
    - **Simple Public Blog/Portfolio Site:** `www.myblog.com`. An **App Service Managed Certificate** is perfect—it's free, auto-renewing, and simple to set up.
    - **Enterprise E-commerce Site with Wildcard:** `shop.contoso.com`, `account.contoso.com`, etc. Use a **Wildcard Certificate (*.contoso.com)** purchased from a CA and **Import from Key Vault**. This centralizes management and secures all subdomains with one certificate.
    - **Secure B2B API (mTLS):** Your API needs to ensure it's only called by trusted clients. You issue a **private client certificate** to your partner. They use it to call your API, and your C# code (using the `WEBSITE_LOAD_CERTIFICATES` feature) validates their certificate.
- **7. Comparison with other similar services or features**

| Feature | App Service Managed Cert | Purchased App Service Cert | Import from Key Vault |
| --- | --- | --- | --- |
| **Cost** | **Free** | Paid (annual fee) | Cost of certificate from any CA |
| **Management** | Fully automated (auto-renewal) | Managed via Azure, manual renew | You manage lifecycle (can automate in KV) |
| **Wildcard Support** | **No** | **Yes** | **Yes** |
| **Apex Domain** | Limited (CNAME only) | **Yes** (A record compatible) | **Yes** (A record compatible) |
| **Centralization** | Tied to a single App Service | Stored in Key Vault, reusable | Stored in Key Vault, reusable |
| **Best For** | Simple sites, subdomains, non-critical apps | Azure-centric workflows, wildcards | Maximum flexibility, enterprise-grade, existing certs, automation |
- **8. Subtopics to master**
    - **Custom Domains:** The absolute prerequisite. Know how to configure CNAME and A records.
    - **Azure DNS:** For programmatically managing the DNS records needed for domain validation.
    - **Azure Key Vault:** The cornerstone of secure certificate management. Understand access policies, secrets vs. certificates, and rotation.
    - **Managed Identity:** The secure mechanism that allows your App Service to talk to Key Vault without credentials.
    - **Public Key Infrastructure (PKI):** Understand the roles of a Certificate Authority (CA), public/private keys, and the chain of trust.
    - **SNI vs. IP-based SSL:** SNI (Server Name Indication) is the modern standard, allowing multiple SSL certificates on a single IP address. It's cheaper and what you'll use 99% of the time.
- **9. Pricing Tiers & Feature Availability**
    - **Free / Shared Tiers:** **Not supported.** You cannot add custom domains or SSL certificates on these tiers.
    - **Basic Tier:** **Supported.** This is the minimum tier for custom domains and all SSL/TLS binding types (Managed, Imported).
    - **Standard, Premium, Isolated Tiers:** **Fully supported.** Purchasing an App Service Certificate requires a Standard tier or higher App Service Plan, but once purchased, it can be used on other plans (like Basic) within the same subscription.
    - **SNI Bindings:** Included in Basic and higher tiers at no extra cost per binding.
    - **IP-based SSL Binding:** An older type that dedicates an IP address to your certificate. It incurs an additional cost and is generally not needed unless you support very old clients that don't support SNI.
- **10. Security Considerations**
    - **Always Use HTTPS:** Configure HTTP to HTTPS redirection to enforce encryption for all users.
    - **Centralize with Key Vault:** For any production application, **Import from Key Vault** is the most secure best practice. It centralizes control, auditing, and rotation.
    - **Automate Rotation:** A short-lived, automatically rotated certificate is more secure than a long-lived one. Configure Key Vault to auto-renew and have your App Service sync with the latest version.
    - **Protect Private Keys:** The private key of your certificate is a highly sensitive secret. Never store it in source control or application settings. Key Vault is designed to protect it.
    - **Least Privilege Access:** Use a Managed Identity and grant the App Service only get and list permissions for secrets in Key Vault. The App Service does not need delete or set permissions to use a certificate.