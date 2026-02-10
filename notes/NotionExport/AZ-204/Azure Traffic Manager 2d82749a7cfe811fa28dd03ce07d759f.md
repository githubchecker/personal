# Azure Traffic Manager

**1. What is it?**

- Azure Traffic Manager is a **DNS-based traffic load balancer** that distributes traffic to public-facing applications across different global Azure regions.
    - It does **not** route the actual traffic itself; instead, it intelligently resolves the DNS query from a user and directs the user's client (e.g., their browser) to the most appropriate service endpoint based on a chosen routing method.
    - It operates at the **DNS layer (Layer 7 conceptually, but not in-line)**.

## **2. Why is it used?**

- The core architectural problems Traffic Manager solves are **high availability, disaster recovery, and performance optimization for globally distributed applications.**
    - **Improved Responsiveness:**
        - By directing users to the geographically closest endpoint (**Performance routing**), it reduces latency and improves application performance.
    - **High Availability:**
        - It can automatically detect when an endpoint is unhealthy and redirect traffic to the next closest or next priority endpoint, ensuring your application remains online even if an entire Azure region fails.
    - **Simplified Maintenance:**
        - You can perform maintenance on one regional deployment without impacting users. Simply disable the endpoint in Traffic Manager, and it will route all traffic to the other healthy endpoints. Once maintenance is complete, re-enable it.

## **3. How it works with Quick start details**

- Traffic Manager works by using a custom **DNS CNAME record** to intercept DNS queries for your domain.

### **The User's Journey:**

1. A user tries to access `www.contoso.com`.
2. The user's browser asks their local DNS resolver: *"What's the IP for [www.contoso.com](http://www.contoso.com/)?"*
3. Your `www` record is a **CNAME** pointing to your Traffic Manager profile, e.g., `contoso.trafficmanager.net`.
4. The local DNS resolver then asks the Azure Traffic Manager DNS servers: *"What's the IP for [contoso.trafficmanager.net](http://contoso.trafficmanager.net/)?"*
5. Traffic Manager's DNS server looks at the request source IP, checks its routing policy (e.g., "**Performance**"), and sees that the user is in Germany. It knows your **West Europe** endpoint is the closest.
6. Traffic Manager returns the IP address of your **West Europe App Service**.
7. The user's browser receives this IP address and connects **directly** to the West Europe App Service. The Traffic Manager is now completely out of the picture for this session.

### **Portal Steps:**

1. Search for and create a **Traffic Manager profile**.
2. Provide a unique name (this becomes part of your `.trafficmanager.net` URL).
3. Choose a **Routing method** (e.g., Performance, Priority, Weighted).
4. Once the profile is created, navigate to it and select the **Endpoints** blade.
5. Click **+ Add**.
6. Select the **Type** of endpoint (e.g., Azure endpoint).
7. Choose the **Target resource type** (e.g., App Service) and then select your actual App Service instance.
8. Configure properties like **Priority** or **Weight** if applicable.
9. Repeat for your other regional endpoints (e.g., an App Service in East US).
10. Finally, go to your domain registrar and create a **CNAME** record for your custom domain (e.g., `www`) pointing to your Traffic Manager profile URL (`contoso.trafficmanager.net`).

### **Azure CLI Example:**

```bash
# Create a Traffic Manager profile with Performance routing
az network traffic-manager profile create \\
  --name my-tm-profile --resource-group my-rg \\
  --routing-method Performance --unique-dns-name my-unique-tm-name

# Add an endpoint pointing to a public IP of a West Europe resource
az network traffic-manager endpoint create \\
  --name endpoint-weu --profile-name my-tm-profile --resource-group my-rg \\
  --type externalEndpoints --target some-weu-resource.westeurope.cloudapp.azure.com

```

## **4. Developer Concepts (AZ-204 Focus)**

- **Health Probes:**
    - Traffic Manager constantly checks the health of your endpoints. For web apps, it typically probes an HTTP/HTTPS endpoint on a specific path.
    - If the endpoint doesn't return a **200 OK** status, it's marked as "degraded," and Traffic Manager will stop sending users to it.
    - As a developer, you must provide a reliable health probe path (e.g., `/api/health`).
- **DNS TTL (Time-to-Live):**
    - This is a critical concept. Traffic Manager sets a TTL on the DNS records it returns.
    - A **low TTL** (e.g., 30 seconds) means DNS resolvers will cache the result for a shorter time, allowing for **faster failover**. However, this can also increase the number of DNS queries to Traffic Manager.
- **Client-Side Behavior:**
    - Because it's DNS-based, the failover is not instant. A user's machine will have the old IP cached for the duration of the TTL.
    - If a region fails, users who recently accessed the site might continue trying to connect to the failed IP until their local DNS cache expires.

## **5. What are the Limitations and "Gotchas"?**

- **DNS Caching:**
    - This is the biggest "gotcha." Failover is not instantaneous and depends on clients and DNS resolvers honoring the TTL. Some misbehaving resolvers can cache for much longer, delaying failover for some users.
- **Not a Proxy or Gateway:**
    - Traffic Manager is **not in the data path**. It doesn't see the HTTP traffic. This means it cannot perform WAF, SSL offloading, or URL path-based routing. It just returns an IP address.
- **Public Endpoints Only:**
    - It can only work with endpoints that have a public IP address. It cannot be used to load balance internal, private traffic within a VNet.
- **"Performance" Routing Source IP:**
    - The performance routing decision is based on the IP of the **local DNS resolver** making the query on behalf of the user, not the user's actual IP. In most cases, this is close enough, but for users behind a large corporate or national DNS proxy, it might be inaccurate.

## **6. Practical Use Cases & Scenarios**

- **Global SaaS Application:**
    - An application is deployed to App Services in East US, West Europe, and Southeast Asia. **Performance** routing is used to send users to their nearest region for the lowest latency.
- **Active-Passive Disaster Recovery:**
    - A critical application runs in West Europe (Priority 1) with a cold standby in North Europe (Priority 2). **Priority** routing sends all traffic to West Europe.
    - If the health probes detect that West Europe is down, Traffic Manager automatically starts sending all users to the North Europe deployment.
- **Blue-Green Deployment / Canary Release:**
    - You have deployed a new version of your application in West Europe (v2) alongside the old version in East US (v1).
    - Using **Weighted** routing, you can send 10% of traffic to v2 and 90% to v1 to test the new version with a small subset of users before a full rollout.

## **7. Comparison with other similar services or features**

| Feature | Azure Traffic Manager | Azure Front Door | Azure Load Balancer |
| --- | --- | --- | --- |
| **Routing Layer** | **DNS** | **Layer 7 (HTTP/S Proxy)** | **Layer 4 (TCP/UDP)** |
| **In Data Path?** | **No** (only for DNS lookup) | **Yes** | **Yes** |
| **Failover Time** | **Slow** (depends on DNS TTL) | **Fast** (seconds) | **Fast** (seconds) |
| **Routing Method** | Geo, Perf, Priority, etc. (at DNS level) | URL Path, Hostname, etc. (at HTTP level) + Global Geo-routing | Hash-based distribution |
| **WAF / SSL Offloading** | **No** | **Yes** | **No** |
| **Scope** | **Global** | **Global** | **Regional** |
| **Best For** | DNS-level global routing, DR, non-HTTP global services. Simple, robust geo-failover. | High-performance, secure, global HTTP web applications. | High-performance TCP/UDP traffic within a region. |
- **Traffic Manager vs. Front Door:** This is the most common comparison.
    - Choose **Traffic Manager** when you need simple, DNS-level global routing and failover, especially for **non-HTTP workloads**, or when you don't need the advanced features (and cost) of a global proxy.
    - Choose **Front Door** for any serious, global **HTTP-based web application**. It provides faster failover, caching, a WAF, and SSL offloading, making it a much more feature-rich and powerful solution.

## **8. Subtopics to master**

- **DNS Fundamentals:**
    - Deeply understand CNAMEs, A Records, and TTL.
- **Health Probe Configuration:**
    - Know how to set up and debug health probes effectively.
- **Routing Methods:**
    - Be able to explain the difference between Priority, Weighted, Performance, and Geographic routing and match them to scenarios.
- **Nested Profiles:**
    - Understand how to combine different Traffic Manager profiles to create more sophisticated routing logic (e.g., performance routing between regions, then priority routing within a region).

## **9. Pricing Tiers & Feature Availability**

- **Pricing Model:** Traffic Manager pricing is based primarily on two factors:
    1. The number of DNS queries received (per million).
    2. The number of endpoints being monitored for health.
- **Availability:**
    - All features of Traffic Manager are generally available in a single pricing model. There are no "Basic vs. Standard" tiers like many other Azure services. It is a standalone, globally available service.

## **10. Security Considerations**

- **Health Probe Security:**
    - Your health probe endpoint should be lightweight and not expose sensitive data. It's a **public endpoint** that Traffic Manager will be hitting frequently.
- **Profile Security:**
    - Use Azure RBAC to control who can modify your Traffic Manager profile. An unauthorized change could redirect your entire site's traffic.
- **Not a Security Service:**
    - Remember that Traffic Manager is **not a firewall or a WAF**. It provides no protection against DDoS attacks, SQL injection, etc., because it never sees the actual data traffic. For security, you must layer it with other services like Azure Front Door (which has a WAF) or Application Gateway at each regional endpoint.