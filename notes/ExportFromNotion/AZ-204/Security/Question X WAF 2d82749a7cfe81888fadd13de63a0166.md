# Question X: WAF

# **Question X: Web Application Firewall (WAF)**

- **1. What is it?**
    - A Web Application Firewall (WAF) is a specialized security service that sits in front of a web application to inspect incoming and outgoing HTTP/HTTPS traffic. Its primary purpose is to filter and block malicious requests that exploit common web vulnerabilities, such as SQL Injection and Cross-Site Scripting (XSS), before they can ever reach the application code. It acts as a protective shield, focusing specifically on application-layer (Layer 7) attacks.
- **2. Why is it used?**
    - The core architectural problem a WAF solves is providing a centralized, managed defense against the most common web-based attacks, as categorized by organizations like the **OWASP (Open Web Application Security Project) Top 10**.
        - **Proactive Security:** It protects your application from known vulnerabilities without requiring changes to your application code. This is crucial for patching against zero-day exploits or protecting legacy applications that cannot be easily modified.
        - **Centralized Management:** Instead of relying on every developer to write perfectly secure code (which is impossible), you have a single point of control to define and enforce security rules for all your backend applications.
        - **Reduced Attack Surface:** It hardens the network edge, preventing malicious traffic from ever reaching your application servers, which might have unknown vulnerabilities.
        - **Compliance and Auditing:** Using a WAF is often a requirement for meeting regulatory compliance standards like PCI DSS, as it provides a clear, auditable layer of security.
- **3. How it works with Quick start details**
    - A WAF operates by using a set of rules to analyze HTTP traffic. These rules are designed to identify patterns that match known attack techniques. It can operate in two modes:
        - **Detection Mode (Logging Only):** The WAF inspects traffic, identifies potential attacks, and logs them, but it does not block the request. This is useful for testing a new rule set to see if it generates false positives before enforcing it.
        - **Prevention Mode (Blocking):** The WAF inspects traffic and actively blocks any request that matches a malicious pattern, typically by returning an HTTP 403 Forbidden error.
    - **Implementation with Azure Application Gateway:**
        - **Portal Steps:**
            1. Navigate to the Azure Portal and create a new **Application Gateway**.
            2. On the **Basics** tab, choose a tier that supports WAF. You must select **WAF V2**. (The older "WAF" tier is legacy).
            3. On the **WAF** tab during creation (or under the **Web application firewall** blade on an existing WAF V2 gateway):
                - Set the **Firewall status** to **Enabled**.
                - Set the **Firewall mode** to **Prevention** (for production) or **Detection** (for testing).
            4. **Configure Rule Sets:**
                - By default, the WAF is enabled with a **Managed Rule Set**. This is a collection of rules curated and updated by Microsoft to protect against the OWASP Top 10 and other common threats. You select a version, e.g., OWASP_3.2.
            5. **Configure Custom Rules (Optional):**
                - You can create custom rules to block or allow traffic based on specific criteria, such as IP address ranges (geo-blocking), request headers, or URL string patterns. For example, you could block all requests that don't have a specific User-Agent.
            6. Finish configuring the Application Gateway (backends, listeners, etc.) and deploy. All traffic passing through the gateway will now be inspected by the WAF.
        - **Azure CLI Example:**
            
            ```bash
            # Create a public IP and VNet (prerequisites)
            # ...
            
            # Create an Application Gateway with WAF V2 enabled in Prevention mode
            az network application-gateway create \\
              --name myAppGateway \\
              --resource-group my-rg \\
              --sku WAF_v2 \\
              --location eastus \\
              --public-ip-address myPublicIP \\
              --vnet-name myVNet --subnet mySubnet \\
              --waf-policy myWafPolicy # You typically link to a separate WAF Policy resource
            
            # Create a WAF Policy with managed rules
            az network application-gateway waf-policy create \\
              --name myWafPolicy --resource-group my-rg \\
              --location eastus
            
            ```
            
- **4. Developer Concepts (AZ-204 Focus)**
    - As a developer, your primary interaction with a WAF is understanding why it might block legitimate traffic and how to design your application to be "WAF-friendly."
        - **False Positives:** A WAF rule might mistakenly identify a valid user input as an attack.
            - *Example:* A user in a blog comment textarea writes a code snippet like `var x = "select * from users;"`. A naive WAF rule might see `select * from` and incorrectly flag it as a SQL Injection attempt.
        - **Troubleshooting:** When users report getting 403 Forbidden errors, your first step should be to check the WAF logs (**WAF Diagnostics** in Application Gateway). The logs will tell you exactly which request was blocked and which rule ID was triggered.
        - **WAF Tuning:** Based on the logs, you have several options:
            1. **Create a Custom Exclusion:** Exclude a specific request header or argument from being inspected by the WAF. This is a surgical approach.
            2. **Disable a Specific Rule:** If a managed rule is causing too many problems, you can disable it. This is a broader action and should be done with caution.
            3. **Rewrite Application Code:** The best long-term solution is often to change your application's input format to not trigger the rule (e.g., use JSON instead of passing raw SQL-like strings in a query parameter).
- **5. What are the Limitations and "Gotchas"?**
    - **Not a Silver Bullet:** A WAF is just one layer of a "Defense in Depth" strategy. It does not absolve developers from writing secure code (e.g., using parameterized queries to prevent SQLi).
    - **HTTPS/TLS Traffic:** A WAF can only inspect traffic it can see. To inspect HTTPS traffic, it must be configured on a service that performs **SSL/TLS termination** (like Application Gateway or Azure Front Door). It cannot inspect end-to-end encrypted traffic.
    - **Complexity of Custom Rules:** Writing effective and secure custom rules is difficult. A poorly written rule can either block legitimate users or create new security holes.
    - **Maintenance Overhead:** WAFs require tuning. You can't just "set it and forget it." You must monitor the logs for false positives and adapt the rules as your application evolves.
- **6. Practical Use Cases & Scenarios**
    - **Protecting a Public E-commerce Site:** An Application Gateway with a WAF is placed in front of an App Service. The WAF's managed rules automatically block attempts to steal customer data via SQL Injection in the search bar or use Cross-Site Scripting to hijack user sessions.
    - **Securing a REST API:** A developer wants to block API access from certain countries. They create a custom rule on the WAF to block requests based on their source IP address's geographical location.
    - **Bot Protection:** A news website is being scraped aggressively by bots, increasing server load and costs. They enable the bot protection rule set on their Azure Front Door WAF to identify and block traffic from known malicious botnets.
- **7. Comparison with other similar services or features**

| Service | WAF | Network Security Group (NSG) | Firewall (Azure Firewall) |
| --- | --- | --- | --- |
| **OSI Layer** | **Layer 7** (Application) | **Layer 3/4** (Network/Transport) | **Layer 3/4/7** (Stateful Firewall) |
| **Inspects** | **HTTP/S request content** (URL, body, headers) | **IP Addresses and Ports** (TCP/UDP packets) | **Packets and some application protocols** (e.g., FQDN filtering) |
| **Core Function** | Block web attacks (SQLi, XSS) | Allow/Deny network traffic between subnets/internet | Central network traffic filtering for an entire VNet |
| **Example Rule** | "If URL contains `<script>`, Block" | "Allow traffic from IP X on Port 443" | "Deny traffic from the Dev subnet to *.github.com" |
| **Analogy** | Inspects the contents of a letter | Checks the address on the envelope | Acts as the central post office security checkpoint |

```
*   A WAF works with these services, not instead of them. A typical setup: NSG -> Azure Firewall -> Application Gateway (with WAF) -> Your App.
```

- **8. Subtopics to master**
    - **OWASP Top 10:** You must be familiar with the most common web vulnerabilities, like SQL Injection, Cross-Site Scripting (XSS), and Broken Authentication.
    - **HTTP Protocol:** Understand HTTP verbs (GET, POST), headers, status codes, and cookies, as these are the elements that WAF rules are built upon.
    - **Azure Monitor and Log Analytics:** Know how to query WAF logs to diagnose issues.
    - **Regular Expressions (RegEx):** Often used for writing advanced custom rules.
- **9. Pricing Tiers & Feature Availability**
    - **Azure Application Gateway:** WAF is only available on the **WAF V2** SKU. The Standard_V2 SKU does not include it. The cost is based on an hourly rate plus a capacity unit processing charge.
    - **Azure Front Door:** WAF is available with the **Standard** and **Premium** SKUs of Azure Front Door. Front Door Premium offers more advanced threat intelligence-based rules managed by Microsoft. The cost is part of the Front Door pricing, often on a per-rule or per-policy basis.
    - **Azure CDN:** WAF is available on Azure CDN Premium from Verizon.
- **10. Security Considerations**
    - **Defense in Depth:** Never rely solely on a WAF. Continue to follow secure coding practices: validate all user input, use parameterized queries (ORM like Entity Framework helps here), and properly encode output to prevent XSS.
    - **Log Monitoring:** Regularly review WAF logs. This helps you identify emerging attack patterns, tune rules to reduce false positives, and discover potential vulnerabilities in your application that are being probed by attackers.
    - **Keep Rules Updated:** If using managed rule sets, ensure they are set to automatically update to the latest version to protect against newly discovered vulnerabilities.
    - **Secure the Backend:** The WAF is your front door. You must still secure the backend. Configure your App Service or VMs to **only accept traffic from the Application Gateway's IP address** to prevent attackers from bypassing the WAF and hitting your application directly. This is typically done with NSGs or App Service network restrictions.