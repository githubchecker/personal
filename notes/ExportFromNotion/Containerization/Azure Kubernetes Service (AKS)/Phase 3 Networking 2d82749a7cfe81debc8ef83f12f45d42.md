# Phase 3: Networking

This is the Phase where "It works on my machine" usually breaks in the Cloud.

Kubernetes networking is essentially a massive software-defined router. In **AKS**, this abstraction connects directly to physical Azure networking hardware (Virtual Networks, Load Balancers, Application Gateways).

To master this, we will move from **Inside** (Pod-to-Pod) to **Outside** (Internet-to-Pod).

---

### **1. The Service (The Internal Static IP)**

**The Problem:**
Pod IPs are volatile. If you update your Deployment, old Pods die (IP `10.1.0.5`) and new Pods are born (IP `10.1.0.9`).
If Microservice A calls Microservice B by IP `10.1.0.5`, the application breaks immediately after an update.

**The Solution:** The **Service** object.
A Service acts as an **Internal Load Balancer** with a **Static IP** and a **Static DNS Name**.

### **Type A: ClusterIP (Default)**

This allows communication *only* inside the cluster.

- **Scenario:** Your API talks to a Redis Cache running in the cluster. Redis does not need to be on the public internet.
- **The YAML:**
    
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: redis-service # This becomes the DNS name
      namespace: default
    spec:
      type: ClusterIP     # Internal Only
      selector:
        app: redis-pod    # Routes traffic to pods with this label
      ports:
      - port: 6379        # The Service's port
        targetPort: 6379  # The Pod's container port
    
    ```
    
- **The "Expert" DNS behavior:**
Any other Pod in the cluster can now connect to `redis://redis-service:6379`. You do **not** need IPs anymore. Kubernetes runs its own internal DNS server (CoreDNS) that resolves service names to IPs.

---

### **2. Getting Traffic IN (Layer 4 - TCP)**

Now, you want to expose your .NET API to the public internet.

### **Type B: LoadBalancer**

When you request a Service of type `LoadBalancer` in AKS, a specialized "Cloud Controller" wakes up and talks to Azure.

- **Action:** It provisions a **real Azure Public Load Balancer** (Standard SKU) in the `MC_` resource group.
- **Action:** It allocates a **real Public IP address** from Azure.
- **Cost:** You pay for the Public IP and the Load Balancer rules.

**The YAML:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: public-api-service
spec:
  type: LoadBalancer  # Request a Public IP
  selector:
    app: my-dotnet-app
  ports:
  - port: 80         # Exposed to internet
    targetPort: 8080 # Container port (ASP.NET Core default)

```

**Why Experts Don't Use This (Scalability Trap):**
If you have 50 microservices, using `Type: LoadBalancer` creates **50 Public IPs** and **50 Azure Load Balancer rules**.

- **Expensive.**
- **No SSL Management:** You cannot easily handle HTTPS certificates here.
- **Hard to Manage:** You have 50 different DNS A-Records to manage.

---

### **3. Getting Traffic IN (Layer 7 - HTTP/HTTPS - Ingress)**

**The "Ingress" (The Smart Router):**
Instead of giving every service a Public IP, we expose **One Single Public IP**. We use an "Ingress Controller" to route traffic based on the URL.

- `api.com/cart` -> Cart Service
- `api.com/users` -> User Service

In AKS, you have two primary choices for the "Ingress Controller" implementation.

### **Option A: NGINX Ingress Controller (The Standard)**

- **How it works:** You run Nginx **inside** your cluster as just another set of Pods. An **Ingress** has a completely different job. Its purpose is to manage **EXTERNAL** traffic coming **INTO** the cluster from the public internet.
    - An Ingress is the "front door" for your entire application.
    - It listens on a public IP address.
    - It routes external HTTP/HTTPS requests (e.g., https://api.myapp.com/users) to the correct **internal ClusterIP Service** (e.g., users-api-service).
- **Pros:** Extremely fast, rich community support, free (open source).
- **Cons:** You manage it (updates, scaling).
- **Workflow:**
    1. Install Nginx via Helm.
    2. Nginx Service gets `Type: LoadBalancer` (One Azure Public IP).
    3. All traffic hits Nginx. Nginx looks at your Ingress Rules and forwards traffic to your internal ClusterIP services.

### **Option B: Application Gateway Ingress Controller (AGIC)**

- **How it works:** This is the "Azure Native" way. AKS configures an **Azure Application Gateway** (PaaS) outside the cluster.
- **Pros:** Native Azure integration, Built-in WAF (Web Application Firewall) to block SQL Injection attacks.
- **Cons:** More expensive, slower to apply configuration updates (approx 30-45 seconds lag).

### **The Ingress YAML (The Rules):**

This is what connects the "Outside" to your "Service".

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-api-ingress
  annotations:
    # Tell K8s which controller handles this (Nginx vs Azure)
    kubernetes.io/ingress.class: nginx
    # Limit max body size (e.g. for file uploads)
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  rules:
  - host: my-app.com
    http:
      paths:
      - path: /api/v1
        pathType: Prefix
        backend:
          service:
            name: my-dotnet-api-service # Points to ClusterIP Service
            port:
              number: 80

```

---

### **4. SSL/TLS Management (cert-manager)**

In Phase 2 (Docker), you likely ignored HTTPS. In AKS, HTTPS is mandatory.

**The "Novice" Way:**
Buy a certificate, download the `.pfx`, upload it to K8s as a Secret, and attach it to the Ingress. Repeat every year when it expires.

**The "Master" Way:**
Use **cert-manager**.
This is a plugin you install in AKS. It talks to **Let's Encrypt**.

1. You define an `Issuer` (Let's Encrypt).
2. You add one line to your Ingress YAML: `cert-manager.io/cluster-issuer: letsencrypt-prod`.
3. **Magic:** cert-manager detects you need SSL, talks to Let's Encrypt, proves you own the domain, downloads the cert, creates the K8s Secret, and auto-renews it 30 days before expiry. Zero human interaction.

---

### **5. The Plumbing: Network Models (CNI vs. Kubenet)**

This is an **Architecture** decision made when creating the cluster. You usually cannot change this later.

### **Option A: Kubenet (Default / Simple)**

- **Mechanism:** Pods get an IP address that creates a "Virtual Network Overlay". The physical Azure Network doesn't strictly know about these IPs. Traffic performs NAT (Network Address Translation) to get out.
- **Pros:** Conserves IP addresses. Great for simple setups.
- **Cons:** Slightly slower. Complex if you need Pods to talk directly to an on-premise server over VPN.

### **Option B: Azure CNI (Advanced / Performance)**

- **Mechanism:** **Every Single Pod gets a REAL IP address** from your Azure VNet subnet.
- **Pros:** High performance (No NAT). Direct visibility. A Pod is a first-class citizen on the network.
- **Cons:** **IP Exhaustion.** If you run 50 nodes with 30 pods each, you need a Subnet with 1,500+ free IPs. You can run out of IPs in your VNet very fast.
    - *New Feature:* **Azure CNI Overlay** fixes the exhaustion issue by combining CNI performance with an overlay approach. **Use this for new clusters.**

---

### **Summary of Phase 3**

1. **ClusterIP Service:** Use for internal Pod-to-Pod talk (e.g., API to Redis). It gives you a stable DNS name.
2. **Ingress:** Use this for external access. It allows 1 Public IP to serve 100 microservices (Routing based on host/path).
3. **Nginx Controller:** The standard, robust choice for handling Ingress traffic.
4. **cert-manager:** Automates SSL so you never touch a certificate file again.
5. **Azure CNI Overlay:** The recommended networking mode for .NET Enterprise clusters.

**Current State:**
We have Apps (Pods). We have traffic hitting them via Ingress (Networking).
**The Missing Piece:** How do we configure them? Where does `appsettings.json` go? Where do database passwords go?

Are you ready for **Phase 4: Configuration & Secrets (Enterprise Security)**?

# **PORTs in Services**

That's a fantastic and very common point of confusion. Getting the port mapping right is essential for traffic to flow correctly in Kubernetes.

Let's break down the roles of `port` and `targetPort` and then map your specific scenario.

---

### **1. The Two "Doors": A Simple Analogy**

Think of a Kubernetes **Service** as a **house**, and a **Pod** as a **room** inside that house.

- **`targetPort`:** This is the door **on the room**. It's the port that your actual application container is listening on. In your case, this is `1025`. This is the internal door that the Service needs to knock on.
- **`port`:** This is the **front door of the house**. It's the port that the *Service itself* exposes to the *rest of the cluster*. Other pods in your cluster will talk to the Service on this port.

**The Service's job is to act as a stable front door and forward traffic from its `port` to the `targetPort` of one of its healthy backend Pods.**

```
        Cluster Internal Network
              |
              | Request to Service at 'port' 9090
              V
+---------------------------+
|      My-Service           | (The "House")
|   (IP: 10.0.10.5)         |
|                           |
|      port: 9090           | <--- Front Door (What other pods see)
+---------------------------+
              |
              | Forwarding traffic...
              V
+---------------------------+
|      My-Pod               | (A "Room" inside the house)
|   (IP: 10.244.0.8)        |
|                           |
|   targetPort: 1025        | <--- Room Door (What your app is listening on)
+---------------------------+
              |
              V
        [Your .NET App in Docker Container]

```

---

### **2. Why Are There Two Different Ports?**

Separating `port` from `targetPort` provides crucial flexibility and follows the principle of abstraction.

1. **Stable Service Contract:** Your services can agree on a standard port. For example, all your internal APIs might be exposed on port `80` through their `Service`.
    - One team's API might be a .NET app running on port `8080` (`targetPort: 8080`).
    - Another team's API might be a Python app running on port `5000` (`targetPort: 5000`).
    - But to any *other pod* in the cluster, they both just appear as services available on the standard `port: 80`. This decouples the "public" service port from the "private" implementation detail of the container's port.
2. **Flexibility in Deployment:** You can change the port your container listens on (by changing the Docker image) and you only need to update the `targetPort` in your Service YAML. All the consumers that were calling the Service on its `port` are completely unaffected.

---

### **3. Your Specific Scenario: The Solution**

- **Your Docker Image Exposes:** `1025`
- **You Want to Call the Service at:** `9090`

**Here is the correct Kubernetes `Service` YAML manifest to achieve this:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-api-service
spec:
  # 'selector' is how the Service finds which Pods to send traffic to.
  # The Pods must have a label matching this (e.g., app: my-api).
  selector:
    app: my-api

  # 'ports' is where we define the mapping.
  ports:
    - name: http-main  # A descriptive name for the port (optional but good practice)
      protocol: TCP

      # The port that THIS SERVICE will listen on.
      # Other pods will call: <http://my-api-service:9090>
      port: 9090

      # The port on the POD that the traffic will be forwarded to.
      # This MUST match the port your container is listening on.
      targetPort: 1025

```

**How it works in practice:**

1. A different pod (e.g., a frontend gateway) makes a request to `http://my-api-service:9090`.
2. Kubernetes DNS resolves `my-api-service` to the Service's stable internal IP address.
3. The request arrives at the Service on port `9090`.
4. The Service looks at its list of healthy backend Pods (found via the `selector`). It picks one (e.g., a Pod with IP `10.244.0.15`).
5. The Service forwards the request to the Pod's IP at port **`1025`**.
6. Your .NET application running in the container receives the request on port `1025` and processes it.

### **Bonus: `nodePort` (The Third Port)**

If your `Service` is of type `NodePort` or `LoadBalancer`, you might see a third port:

- **`nodePort`:** Exposes the Service on a static port on the **IP address of every Node (VM) in the cluster**. This port is usually in a high range (e.g., 30000-32767). It's mainly used for external access or debugging and is less common for internal service-to-service communication.

In your case, you would stick to a `ClusterIP` service (the default type if none is specified), which only requires `port` and `targetPort`.