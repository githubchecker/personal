# Azure Firewall vs Azure AppGateway vs Azure Api Management vs Load Balancer vs Traffic manager vs Azure Frontdoor

Azure Firewall vs Azure AppGateway vs Azure Api Management vs Load Balancer vs Traffic manager vs Azure Frontdoor with there feature which are common and which are not

# **Question X: Azure's Core Traffic Management Services Compared**

- **1. What is it?**
    - This is a collection of Azure services designed to route, secure, manage, and load balance network traffic. Each service operates at a different layer of the network stack and serves a distinct architectural purpose, from simple packet forwarding to sophisticated, global application delivery.
        - **Azure Load Balancer:** A regional Layer 4 load balancer for distributing TCP/UDP traffic.
        - **Azure Application Gateway:** A regional Layer 7 load balancer with a Web Application Firewall (WAF) for HTTP/S traffic.
        - **Azure Firewall:** A stateful, managed network firewall for filtering Layer 3/4 traffic and some Layer 7 traffic for an entire Virtual Network.
        - **Azure Traffic Manager:** A global DNS-based load balancer for directing users to different regional endpoints.
        - **Azure Front Door:** A global Layer 7 load balancer and CDN for high-performance, secure, and resilient global web applications.
        - **Azure API Management:** A comprehensive platform for publishing, securing, and managing APIs, acting as a specialized Layer 7 gateway.
- **2. Why is it used?**
    - As a group, these services are used to build the foundational pillars of any robust cloud application:
        - **Availability:** Distributing traffic across multiple servers or regions to prevent a single point of failure.
        - **Scalability:** Allowing you to add or remove backend instances seamlessly without affecting users.
        - **Security:** Protecting applications from network-level and application-level attacks.
        - **Performance:** Reducing latency by directing users to the closest geographical endpoint and caching content.
        - **Governance:** Controlling access and applying policies to traffic (especially for APIs).

---

# **Comparison of Features: Common vs. Unique**

- This table is the core of the answer, designed for easy comparison.

| Feature / Capability | Load Balancer | App Gateway | Azure Firewall | Traffic Manager | Front Door | API Management |
| --- | --- | --- | --- | --- | --- | --- |
| **Operating Scope** | Regional | Regional | Regional | Global | Global | Regional |
| **Primary OSI Layer** | **Layer 4** | **Layer 7** | L 3/4 (+ L7) | **DNS** | **Layer 7** | **Layer 7** |
| **In Data Path?¹** | Yes | Yes | Yes | **No** | Yes | Yes |
| **--- COMMON FEATURES ---** |  |  |  |  |  |  |
| **Load Balancing** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ (to backends) |
| **Health Probes** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **--- SECURITY FEATURES ---** |  |  |  |  |  |  |
| **Web App Firewall (WAF)** | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Network Traffic Filtering²** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **DDoS Protection³** | Standard | Standard | Standard | Standard | Standard | Standard |
| **SSL/TLS Termination** | ❌ | ✅ | (For Inspection) | ❌ | ✅ | ✅ |
| **--- PERFORMANCE FEATURES ---** |  |  |  |  |  |  |
| **Content Caching (CDN)** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ (Policy-based) |
| **--- ROUTING & GOVERNANCE ---** |  |  |  |  |  |  |
| **URL Path Routing** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ (Operations) |
| **Hostname Routing** | ❌ | ✅ | ✅ (FQDN) | ❌ | ✅ | ✅ (APIs) |
| **API Governance⁴** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
- **Footnotes (CRITICAL distinctions):**
    - **¹ In Data Path?:** This is a key architectural concept. Services in the data path (all except Traffic Manager) actually process the user's traffic. Traffic Manager only answers a DNS query and then gets out of the way.
    - **² Network Traffic Filtering:** This refers to the core job of a traditional firewall: Allow/Deny traffic based on source/destination IP, port, and protocol. Only Azure Firewall specializes in this.
    - **³ DDoS Protection:** All of these services are protected by Azure's basic infrastructure DDoS protection. Application Gateway and Front Door can be enhanced with DDoS Protection Standard for more advanced telemetry and protection.
    - **⁴ API Governance:** This is the unique domain of APIM. It includes features like rate limiting, quotas, transformations, developer portals, subscriptions, and JWT validation. No other service does this.

---

# **Quick Guide: When to Use What**

- **Use Load Balancer IF...** you need to distribute **non-HTTP** traffic (e.g., databases) inside a VNet.
- **Use App Gateway IF...** you need to secure and route **HTTP** traffic for regional applications and need a **WAF**.
- **Use Azure Firewall IF...** you need to control and filter **all egress and ingress network traffic** for an entire Virtual Network, not just for a specific web app.
- **Use Traffic Manager IF...** you need simple, **DNS-level global failover**, especially for non-HTTP workloads.
- **Use Front Door IF...** you are building a **global HTTP application** and need the best performance, fast failover, and a WAF.
- **Use API Management IF...** you are exposing **APIs** and need to apply policies, security, and governance to them.

---

# **The Layered Architecture: How They Work Together**

- In a sophisticated, secure, and globally-scaled application, you don't choose one; you use several together in layers.
- **Example Scenario:** A global e-commerce enterprise application.
    1. **Client Request:** A user in Japan requests `https://shop.contoso.com/api/products`.
    2. **Layer 1 (Global DNS Routing) - Azure Traffic Manager or Azure Front Door:**
        - **Traffic Manager:** A DNS lookup for [shop.contoso.com](http://shop.contoso.com/) resolves to the IP address of the closest healthy **Azure Front Door** instance. (Note: Front Door can also handle this itself with its own Anycast network).
    3. **Layer 2 (Global Edge & Security) - Azure Front Door:**
        - The user connects to the nearest Front Door edge location (e.g., Tokyo).
        - **SSL Termination:** Front Door terminates the HTTPS connection.
        - **WAF:** It inspects the request for SQL injection or other attacks.
        - **Caching:** If this is a frequently requested product list, Front Door might serve the response directly from its cache.
        - **Routing:** If not cached, Front Door's routing rules determine that the request should go to the "Asia Production" backend. It forwards the request to the Application Gateway in the Japan East region.
    4. **Layer 3 (Network Security) - Azure Firewall:**
        - (Optional but high security) All traffic entering the Virtual Network from Front Door could be forced through Azure Firewall. The firewall checks rules to ensure only traffic from known Front Door IP ranges on port 443 is allowed.
    5. **Layer 4 (Regional Application Security) - Application Gateway:**
        - The Application Gateway receives the request from Front Door.
        - It might do a second-level WAF inspection. Its path-based routing sends `/api/*` traffic to the **API Management** service's internal IP address.
    6. **Layer 5 (API Governance) - API Management:**
        - APIM receives the request.
        - It validates the JWT token or API key.
        - It checks if the user has exceeded their rate limit.
        - It transforms the request if needed, and then forwards it to the backend service.
    7. **Layer 6 (Internal Load Balancing) - Azure Load Balancer:**
        - The backend service might be a set of containers in AKS or VMs. An internal Azure Load Balancer distributes the request from APIM to a healthy container/VM instance.
- This layered approach provides "Defense in Depth," where each service performs its specialized role, creating a highly secure, resilient, and performant architecture.

---

# NSG vs Azure Firewall vs App Gateway

### 1. The Architectural Hierarchy (The "3 Lines of Defense")

Think of your cloud infrastructure as a high-security office building.

1. **NSG (Network Security Group):** This is the **Lock on the Office Door**.
    - **Role:** Extremely granular, micro-segmentation.
    - **Layer:** OSI Layer 4 (Transport). It sees IPs, Ports, and Protocols (TCP/UDP).
    - **Intelligence:** Low. It doesn't know *what* data is inside the packet. It just checks the envelope (Source IP: 10.0.0.1, Dest Port: 443).
    - **Scope:** Applied to a Subnet or a specific Network Interface (NIC).
2. **Azure Firewall:** This is the **Security Guard at the Main Lobby**.
    - **Role:** Network-wide protection, central governance.
    - **Layer:** OSI Layers 3–7.
    - **Intelligence:** High. It has "Threat Intelligence" (knows known malicious IPs). It creates a "Hub and Spoke" filter. It handles non-web traffic (RDP, SSH, FTP, SQL) perfectly.
    - **Scope:** Centralized (usually in a Hub VNet).
3. **Application Gateway:** This is the **Concierge for the Executive Suite (Web Apps)**.
    - **Role:** Application Delivery Controller (ADC).
    - **Layer:** OSI Layer 7 (Application). It "speaks" HTTP/HTTPS fluently.
    - **Intelligence:** Application-aware. It opens the package, reads the HTTP Headers, Cookies, and URL path, then makes decisions.
    - **Scope:** Ingress (Incoming traffic) for Web Applications.

---

### 2. Capabilities Exchange (Who does what?)

You asked what App Gateway does (excluding WAF) that Firewall cannot, and vice-versa.

### What App Gateway Does (That Firewall CANNOT efficiently do)

Since App Gateway is a Layer 7 Reverse Proxy, it interacts with the web logic:

1. **URL Path-Based Routing:** Route `/api/*` to Microservice A and `/images/*` to a Storage Account. A Firewall sees only IP addresses; it cannot read the URL path.
2. **Cookie-Based Session Affinity (Sticky Sessions):** App Gateway can ensure a specific user stays connected to "Server-1" for the duration of their shopping session using cookies. A Firewall cannot see cookies.
3. **TLS/SSL Offloading:** It decrypts HTTPS traffic, inspects it, and can send unencrypted HTTP to the backend (saving backend CPU). While Premium Firewalls can do TLS inspection, App Gateway is purpose-built for high-volume certificate management.
4. **HTTP Header Rewriting:** It can modify request/response headers on the fly (e.g., removing `Server: IIS` header for security) before the traffic hits your app.

### What Azure Firewall Does (That App Gateway CANNOT do)

1. **Non-HTTP Protocol Filtering:** App Gateway **only** understands HTTP/S. If you need to filter RDP, SSH, SMB, or direct SQL connectivity (TCP 1433) between VNets, you **must** use a Firewall.
2. **Outbound SNAT (Network Address Translation):** Azure Firewall acts as a single static public IP for all outbound traffic from your backend servers. App Gateway is primarily Ingress (Inbound).
3. **FQDN Tags (Windows Update / Azure Backup):** Firewall can allow traffic to `.windowsupdate.com`. App Gateway expects a specific host header for web traffic, it is not designed to act as a general outbound proxy for servers.

---

### 3. NSG on Private Endpoints (The "Gotcha" Scenario)

You asked: *"How NSG is used in Private endpoint can we not bypass it as there is already firewall?"*

This is a critical architectural nuance.

### The Old World (Pre-2022)

Originally, NSGs **did not work** on Private Endpoints. The Private Endpoint injected a NIC into your VNet, and it bypassed all NSG rules. You were forced to use a Firewall to secure it.

### The Modern Architecture (Network Policies Enabled)

Now, we explicitly enable **"Private Endpoint Network Policies"** on the subnet. This allows NSGs to filter traffic flowing into the Private Endpoint.

### **Can you bypass the Firewall? YES.**

If you do not have an NSG on the Private Endpoint subnet, lateral movement attacks can bypass the Firewall entirely.

**The Bypass Scenario:**

1. **Hub:** Contains Azure Firewall.
2. **Spoke A (Web):** Has a VM. Route Table (UDR) sends traffic to Firewall (0.0.0.0/0 -> Firewall).
3. **Spoke B (Data):** Has a SQL Private Endpoint.

If the Attacker compromises the Web VM in Spoke A:

- They try to reach Spoke B.
- The UDR forces traffic to the Firewall. **Firewall Blocks it.** (Safe).

**BUT**, if the Attacker compromises a VM inside **Spoke B (The same VNet as the Private Endpoint)**:

- Traffic within the same Subnet or VNet typically obeys "System Routes" which prefer "Local VNet" over the UDR pointing to the Firewall.
- **Result:** The attacker connects directly to the Private Endpoint, bypassing the Firewall.

**The Solution:** You apply an **NSG on the Private Endpoint's Subnet**. This is your specific defense-in-depth lock. Even if they are in the same VNet, the NSG on the NIC level says "Deny All except from App-Subnet".

---

### 4. The Master Scenario: "The E-Commerce Platform"

Let's visualize where all three fit in a single request flow to make this concrete.

**Infrastructure:**

- **Web App:** Running in an AKS Cluster (Spoke VNet A).
- **Database:** Azure SQL with Private Endpoint (Spoke VNet B).
- **Security Hub:** Azure Firewall (Hub VNet).

### Use Case 1: Customer buys a product (HTTP Traffic)

*Flow: Internet -> App Gateway -> AKS*

1. User hits `www.shop.com`.
2. **App Gateway** (L7) receives it. It decrypts SSL, checks the URL (`/checkout`), looks for the session cookie, and checks the WAF for SQL Injection.
3. **App Gateway** forwards the clean request to the AKS Internal Load Balancer.
4. **NSG** on the AKS Subnet allows traffic on Port 80 **only** from the App Gateway Subnet IP range. (Layer 4 Lock).

### Use Case 2: The Web App saves the order to DB (East-West Traffic)

*Flow: AKS -> Azure Firewall -> SQL Private Endpoint*

1. The Microservice needs to talk to SQL (Port 1433).
2. **UDR (User Defined Route)** on the AKS Subnet forces all outbound traffic to **Azure Firewall** IP.
3. **Azure Firewall** receives the packet. It checks: "Is Spoke A allowed to talk to Spoke B SQL?" (Network Rule). It logs the connection.
4. Firewall forwards traffic to the SQL Private Endpoint IP.
5. **NSG** on the SQL Subnet receives the packet. It checks: "Is Source IP = Firewall?" Allow.
6. DB transaction happens.

### Use Case 3: Why we need the NSG on Private Endpoint (The Attack)

An intern deploys a Test VM inside **Spoke VNet B** (Database VNet) to debug something.

1. The intern tries to connect directly to the SQL Private Endpoint.
2. Because they are in the same VNet, the traffic does **not** go to the Hub Firewall. It goes direct.
3. **The NSG on the Private Endpoint Subnet kicks in.**
    - Rule: `Allow from Firewall IP`.
    - Rule: `Deny All`.
4. The Test VM is blocked.

### Summary Table

| Feature | NSG | Azure Firewall | App Gateway |
| --- | --- | --- | --- |
| **Primary Job** | Subnet/NIC filtering (Access Control Lists). | Enterprise segmentation, Egress filtering, IDPS. | Web Load Balancing, WAF, SSL Termination. |
| **OSI Layer** | Layer 4 (Transport). | Layer 3-7 (Network/App). | Layer 7 (Application - HTTP/S). |
| **Understand URLs?** | No. | Limited (FQDNs), but not paths. | **Yes** (Paths, Headers, Cookies). |
| **Bypassable?** | No (Hard bound to NIC/Subnet). | Yes (Intra-VNet traffic bypasses it unless UDR is strict). | Yes (If not enforced by NSG/Firewall). |
| **Key Differentiator** | Cheap, Fast, Basic. | Centralized logging, Non-HTTP protocols. | **URL Routing, Cookie Affinity**, Image compression. |