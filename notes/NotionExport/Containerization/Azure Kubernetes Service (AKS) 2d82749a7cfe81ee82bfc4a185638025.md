# Azure Kubernetes Service (AKS)

This roadmap is tailored for a **.NET Core Developer** moving to **Azure Kubernetes Service (AKS)**. Kubernetes (K8s) is complex because it solves problems you might not know you had (Service Discovery, Bin Packing, Self-Healing).

Here is the path to mastery, specifically mapping generic K8s concepts to their Azure implementations.

---

### **Phase 1: The Architecture & The "Managed" Promise**

*Understanding what Azure manages vs. what YOU manage.*

1. **Control Plane (The Brain):**
    - **Generic:** The API Server, Scheduler, and ETCD database.
    - **AKS:** Azure manages this for you (Free Tier or Standard). You do *not* see these VMs. They have a 99.95% SLA.
2. **Worker Nodes (The Muscle):**
    - **Generic:** The actual Linux/Windows servers running containers.
    - **AKS:** These are **Virtual Machine Scale Sets (VMSS)** running in your Azure Resource Group. You pay for these.
3. **The "Kubelet":**
    - The agent running on the node that talks to the Control Plane ("The Captain's instructions").
4. **Kubectl:**
    - The CLI tool. How to connect it to AKS (`az aks get-credentials`).

### **Phase 2: The Workloads (Running Containers)**

*Stopping `docker run` and starting `kubectl apply`.*

1. **Pods (The Atomic Unit):**
    - Why K8s runs "Pods", not "Containers".
    - **Sidecar Pattern:** Running two containers in one Pod (e.g., your .NET API + a Logging Agent).
2. **Deployments (Stateless Apps):**
    - **ReplicaSets:** Guaranteeing 3 copies of your API are always alive.
    - **Rolling Updates:** Updating from v1 to v2 with zero downtime.
3. **StatefulSets (Databases):**
    - Why Running SQL Server in K8s is hard (Ordering, Persistence, Network Identity).
4. **Jobs / CronJobs:**
    - Running background tasks (Database migration scripts) that start, finish, and die.

### **Phase 3: Networking (The Hardest Part)**

*Connecting Pods to each other and the Internet.*

1. **ClusterIP (Internal):**
    - Internal load balancing. How Microservice A calls Microservice B using DNS (`http://service-b`).
2. **LoadBalancer (External - Layer 4):**
    - **AKS:** Automatically creates a real **Azure Load Balancer (Public IP)** when you request this.
3. **Ingress (External - Layer 7):**
    - Routing `api.com/cart` -> CartService and `api.com/user` -> UserService.
    - **AKS:** **Application Gateway Ingress Controller (AGIC)** vs. **Nginx Ingress**. SSL Termination and WAF (Web Application Firewall).
4. **CNI Plugins:**
    - **Kubenet** vs. **Azure CNI**. (Does the Pod get a real Azure VNet IP address or a virtual overlay IP? This impacts connecting to on-premise VPNs).

### **Phase 4: Configuration & Secrets (Enterprise Security)**

*Handling `appsettings.json` and Passwords.*

1. **ConfigMaps:**
    - Injecting non-sensitive settings (Feature Flags) as Environment Variables or Files.
2. **Secrets (Native):**
    - Base64 encoded (Not really secure).
3. **AKS Security (The Expert Way):**
    - **Secret Store CSI Driver:** Syncing **Azure Key Vault** secrets directly into the Pod.
    - **Workload Identity:** How a Pod logs into Azure SQL without a password (using Entra ID / Managed Identity).

### **Phase 5: Storage (Persistence)**

*Making sure data survives a Pod crash.*

1. **Persistent Volumes (PV) & Claims (PVC):**
    - The abstraction layer. "I need 10GB disk."
2. **Storage Classes:**
    - **AKS Implementations:**
        - `default`: Azure Managed Disk (Standard HDD).
        - `managed-premium`: Azure SSD.
        - `azurefile`: Azure Files (SMB Share) - Essential for "ReadWriteMany" (Shared folder between pods).

### **Phase 6: Scaling & Scheduling**

*Handling 1 user vs. 1 million.*

1. **Requests & Limits:**
    - Defining how much RAM/CPU a .NET app needs. (Preventing "Noisy Neighbor" problems).
2. **Horizontal Pod Autoscaler (HPA):**
    - "If CPU > 70%, add more Pods."
3. **Cluster Autoscaler (CA):**
    - "If no Nodes have space for new Pods, buy another Azure VM."
4. **KEDA (Kubernetes Event-Driven Autoscaling):**
    - **Critical for .NET:** Scaling based on **Azure Service Bus Queue Length**, not just CPU.

### **Phase 7: Monitoring & Troubleshooting**

*Why is my Pod crashing?*

1. **Probes (Liveness & Readiness):**
    - Mapping .NET Health Checks (`/health`) to K8s so it knows when to restart a hung container.
2. **Container Insights:**
    - Integration with **Azure Monitor** / **Log Analytics** to see `stdout` logs and RAM usage graphs.
3. **Debugging:**
    - `kubectl logs`, `kubectl exec` (remote into container), `kubectl describe`.

---

[**Phase 1: The Architecture & The "Managed" Promise**](Azure%20Kubernetes%20Service%20(AKS)/Phase%201%20The%20Architecture%20&%20The%20Managed%20Promise%202d82749a7cfe817e81e1fb873ddf7d4a.md)

[**Phase 2: The Workloads (Running Containers)**](Azure%20Kubernetes%20Service%20(AKS)/Phase%202%20The%20Workloads%20(Running%20Containers)%202d82749a7cfe81c892bfe90f4ce57d94.md)

[**Phase 3: Networking**](Azure%20Kubernetes%20Service%20(AKS)/Phase%203%20Networking%202d82749a7cfe81debc8ef83f12f45d42.md)

[**Phase 4: Configuration & Secrets (Enterprise Security)**](Azure%20Kubernetes%20Service%20(AKS)/Phase%204%20Configuration%20&%20Secrets%20(Enterprise%20Securi%202d82749a7cfe81ff8293effe9e0f96d6.md)

[**Phase 5: Storage (Persistence)**](Azure%20Kubernetes%20Service%20(AKS)/Phase%205%20Storage%20(Persistence)%202d82749a7cfe8184b573c943e5000b24.md)

[**Phase 6: Scaling & Scheduling**](Azure%20Kubernetes%20Service%20(AKS)/Phase%206%20Scaling%20&%20Scheduling%202d82749a7cfe81f08c29e7277b8e907d.md)

[**Phase 7: Monitoring & Troubleshooting**](Azure%20Kubernetes%20Service%20(AKS)/Phase%207%20Monitoring%20&%20Troubleshooting%202d82749a7cfe8169b417d6eb46beec17.md)