# Phase 1: The Architecture & The "Managed" Promise

## **Phase 1: The Architecture & The "Managed" Promise**

Before running containers, you must understand the machine you are operating. Kubernetes is not a single server; it is a **cluster** of servers acting as one.

In **AKS (Azure Kubernetes Service)**, the most critical concept is the distinction between what **Microsoft manages** (The Brain) and what **You manage** (The Muscle).

---

### **1. The Control Plane ("The Brain" - Managed by Azure)**

In standard (vanilla) Kubernetes, installing the Control Plane is a nightmare. You have to install an ETCD database, an API Server, a Scheduler, and certificates.

In AKS, **Azure manages this for you.**

- **API Server:** The entry point (REST API). Every tool (Kubectl, Visual Studio, Azure Portal) talks to this.
- **Etcd:** The database storing the state of the cluster (secrets, configs).
- **Scheduler:** Decides which server runs which container based on free RAM/CPU.

**Key Takeaways for AKS:**

- **Visibility:** You **cannot** SSH into these servers. They don't appear in your Portal.
- **Cost:** **Free** by default. You only pay if you enable the "Uptime SLA" (Standard tier) which guarantees 99.95% availability of the API.
- **Updates:** Azure patches this automatically (if configured).

---

### **2. Worker Nodes ("The Muscle" - Managed by You)**

These are the actual machines executing your .NET applications.

- **Generic K8s:** Physical servers or generic VMs.
- **Azure Reality:** AKS creates an **Azure Virtual Machine Scale Set (VMSS)** under the hood.

**The "Node Pool" Concept:**
You group identical VMs into a pool.

- **System Node Pool:** Runs core K8s services (DNS, Networking). Usually Linux.
- **User Node Pool:** Runs *your* apps.
    - *Linux Pool:* For .NET Core apps (cheaper, faster).
    - *Windows Pool:* For legacy .NET Framework 4.8 apps (heavier).

**The "MC_" Resource Group:**
When you create an AKS cluster named `MyCluster` in resource group `My-RG`, Azure silently creates a **second** resource group named `MC_My-RG_MyCluster_Region`.

- **What's inside?** The actual VMs, Load Balancers, Virtual Networks, and Disks.
- **Warning:** **Never touch** the resources inside the `MC_` group manually. AKS automation owns them. If you delete a VM there, AKS might panic.

---

### **3. Interacting: `kubectl` and the `kubeconfig`**

How do you control the cluster? You don't usually use the Azure Portal for commands. You use the CLI: **`kubectl`** (pronounced *cube-cuttle* or *cube-control*).

**The Authentication Handshake (`az aks get-credentials`):**
Kubectl needs a file (~/.kube/config) with certificates to talk to the Control Plane.

**The Command:**

```bash
# This downloads the credentials from Azure and merges them into your local config
az aks get-credentials --resource-group MyResourceGroup --name MyAKSCluster

```

**Verification:**

```bash
kubectl get nodes

```

- **Success:** You see a list of VMs (e.g., `aks-agentpool-12345...`) with status `Ready`.
- **C# Analogy:** Think of `kubectl` as an `HttpClient`. The `kubeconfig` file is the `Authorization Header` containing the Bearer Token.

---

### **4. Namespaces (Virtual Isolation)**

Your cluster is a big empty building. If you dump all your Microservices (Auth, Order, Cart) for Dev, QA, and Prod into the main room, it becomes a mess.

**Namespaces** are virtual rooms.

- **`default`**: Where things go if you specify nothing.
- **`kube-system`**: Where K8s internal tools live (DNS, Metrics). **Don't touch.**
- **Your Strategy:**
    - Create namespaces for environments: `dev`, `qa`.
    - Or per domain: `orders`, `users`.

**Command:**

```bash
kubectl create namespace dev

```

---

### **5. The "Managed" Upgrade Promise**

Kubernetes releases a new minor version (e.g., 1.29 -> 1.30) every 4 months. Old versions are deprecated quickly.

**The Azure Process:**

1. **Upgrade Control Plane:** You click "Upgrade" in the Portal. Azure updates the API server (Zero downtime for your running apps).
2. **Upgrade Nodes (The Rolling Update):**
    - AKS creates a new VM with the new OS/Version.
    - It moves your containers to the new VM.
    - It deletes the old VM.
    - It repeats this one by one until the pool is updated.

---

### **Summary of Phase 1**

1. **AKS** = Managed Control Plane (Free) + Your VMs (Paid).
2. **Resource Groups:** You see your Cluster resource, but the actual VMs live in a hidden `MC_` resource group.
3. **Authentication:** Run `az aks get-credentials` to wire up your local terminal to the cloud.
4. **Nodes:** We use Linux nodes for .NET Core to save money and increase speed.

**Ready for Phase 2: The Workloads?** (Where we actually run a .NET container inside this architecture using Pods and Deployments).