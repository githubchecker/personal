# App Service Plan Details

# **1. The Technology Stack Constraint**

- **Question:** If we deploy multiple applications in the same App Service Plan, do they have to have the same tech stack?
- **Answer:** **Yes and No.** This is a nuanced but very important distinction.
    - **For Windows App Service Plans:**
        - You have a lot of flexibility. An App Service Plan running on Windows Server (IIS) is technology-agnostic at its core. You can run **multiple applications with different tech stacks** in the same plan. For example:
            - WebApp 1: .NET 8 (running in-process with IIS)
            - WebApp 2: Node.js 18.x (running in a separate process managed by iisnode)
            - WebApp 3: PHP 8.2 (running via FastCGI)
            - WebApp 4: Java 17 (running a WAR file in a Tomcat/JBoss container)
        - This is possible because the underlying Windows Server is a general-purpose OS, and IIS is designed to host and manage different application runtimes simultaneously.
    - **For Linux App Service Plans:**
        - This is where the constraint applies. A Linux App Service Plan is **container-based**. When you create the plan, you are effectively choosing a single, pre-configured runtime container image (e.g., DOTNET|8.0, NODE|18-lts, PYTHON|3.11). **All Web Apps deployed to this plan MUST use that same runtime and version.**
            - If you create a Linux plan for .NET 8, you can deploy ten different .NET 8 apps, but you **cannot** deploy a Node.js app into that same plan. You would need a separate App Service Plan for your Node.js apps.
- **Why the difference?**
    - The Linux model is designed for simplicity, consistency, and optimized performance by having a single, fine-tuned runtime environment. The Windows model is designed for flexibility and backward compatibility, reflecting the nature of IIS as a multi-purpose web server.

---

# **2. How it Works Internally: Code Deployment & URL Routing**

- **Question:** How is the code deployed separately, and how is the URL routed to two different apps in the same plan?
- **Analogy:** Think of your **App Service Plan** as a single, powerful **web server computer** (a VM instance).
    - **WebApp 1 ([app1.azurewebsites.net](http://app1.azurewebsites.net/))** is like `C:\\inetpub\\wwwroot\\App1` on that server.
    - **WebApp 2 ([app2.azurewebsites.net](http://app2.azurewebsites.net/))** is like `C:\\inetpub\\wwwroot\\App2` on that server.
- **Internal Code Deployment**
    - When you deploy WebApp1 and WebApp2, their code, assets, and web.config/appsettings.json are stored in completely separate, isolated directory structures on the App Service Plan's file system. WebApp1 has no access to the files of WebApp2. On Windows, IIS manages them as separate applications running in their own isolated application pools. On Linux, they are separate processes running within the shared runtime container.
- **The Magic of URL Routing**
    - The routing is handled by a sophisticated, multi-tenant **Front End Role** that sits in front of all App Service Plans in an Azure region. This is a powerful reverse proxy managed by Microsoft. You don't see it, but it's the traffic cop for *.azurewebsites.net.
    1. **Request:** A user's browser makes a request to `app2.azurewebsites.net`.
    2. **DNS:** The DNS resolves `app2.azurewebsites.net` to a shared public IP address of one of these Azure Front End servers.
    3. **Front End Role Inspection:** The Front End server receives the request. It looks at the **Host header** in the incoming HTTP request. The header says `Host: app2.azurewebsites.net`.
    4. **Internal Lookup:** The Front End has a massive, constantly updated routing table for the entire region. It looks up `app2.azurewebsites.net` and finds that it is mapped to **your specific App Service Plan**. It also knows the internal IP address of the VM instance running your plan.
    5. **Forwarding:** The Front End server forwards the request to your App Service Plan instance. The web server (IIS or the Linux equivalent) on your instance receives the request, sees the Host header for `app2.azurewebsites.net`, and knows to route it internally to the App2 codebase.
    - The Host header is the key. It's how this single Front End can serve millions of different web apps.

---

# **3. The "Noisy Neighbor" Problem and Autoscaling**

- **Question:** In case of autoscaling, will it create multiple VM instances and will the non-required app also be autoscaled?
- **Answer:** **Yes, absolutely.** You have described the "Noisy Neighbor" problem perfectly.
    - **Scaling is at the Plan Level:** Autoscale rules are configured on the **App Service Plan**, not the individual Web App. The rules monitor the *total, aggregated* CPU, Memory, or other metrics of the entire VM instance.
    - **Replication is of the Entire Plan:** When an autoscale "scale out" rule is triggered, Azure provisions a brand new, identical VM instance. It then deploys the **ENTIRE App Service Plan configuration** to it. This means it creates full, running copies of **ALL the Web Apps** in the plan.
- **Walkthrough of the Noisy Neighbor Problem:**
    1. **Initial State:** You have one App Service Plan on **1 instance**. It's running `CriticalApiApp` and a low-traffic `MarketingSiteApp`.
    2. **Trigger:** `CriticalApiApp` gets a massive surge in traffic, pushing the total CPU of the App Service Plan to 90%.
    3. **Autoscale Fires:** The autoscale rule says, "If CPU > 70%, scale out by one instance."
    4. **Result:** Azure spins up a **second VM instance**. This new instance gets a full copy of both `CriticalApiApp` **and** `MarketingSiteApp`.
    5. **The Unintended Consequence:** Your `MarketingSiteApp` is now running on two powerful servers, consuming a baseline amount of memory and resources on both, even though its own traffic never increased. You are paying double the cost, but the marketing site didn't need it. `CriticalApiApp` is the "Noisy Neighbor" whose resource needs have forced the entire plan (and your bill) to scale up.
- **Conclusion & Best Practice:**
    - Because of this behavior, the professional best practice is to **isolate applications with different scaling profiles, criticality, or environments into separate App Service Plans.** This gives you granular control over scaling and cost, ensuring that your critical API can scale to 10 instances without affecting the cost or resources allocated to your simple marketing site.