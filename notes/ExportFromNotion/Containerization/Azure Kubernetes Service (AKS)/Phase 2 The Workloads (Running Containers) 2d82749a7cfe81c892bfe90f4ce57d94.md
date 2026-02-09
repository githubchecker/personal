# Phase 2: The Workloads (Running Containers)

In Docker (Phase 4), you used `docker run` to start a container.
In Kubernetes, **we never run containers directly.** We run **Workloads**.

A Workload is an object that *manages* the lifecycle of your containers. The transition from Docker to K8s requires a mindset shift from **Imperative** ("Run this now") to **Declarative** ("Here is the state I want the system to maintain").

---

### **1. The Pod (The Atomic Unit)**

Kubernetes does not know what a "Container" is. It only knows **Pods**.

- **Concept:** A Pod is a wrapper around one (or more) containers. Think of the Container as an *Electron* and the Pod as the *Atom*. You cannot split the atom.
- **Networking:** The Pod gets a single internal IP address. If you run two containers inside one Pod (e.g., Main API + LogForwarder), they share the same IP and can talk via `localhost`.
- **Lifecycle:** Pods are **Mortal**. If a Pod dies, it is not resurrected. It is deleted, and a *new* Pod (with a new IP) is created to replace it.

**Why not create Pods manually?**
If you create a "naked" Pod and the Node it is running on crashes, **the Pod dies and never comes back.** This is bad for production.

---

### **2. The Deployment (The Factory)**

This is the standard workload for **Stateless .NET Core Web APIs**.

A **Deployment** manages a set of identical Pods. You tell the Deployment: "I want 3 copies of `my-api:v1`."
The Deployment creates a **ReplicaSet**, which ensures 3 pods are running.

**Why use a Deployment?**

1. **Self-Healing:** If a Node crashes and 1 Pod dies, the Deployment notices you only have 2/3. It immediately schedules a new Pod on a healthy Node.
2. **Scaling:** You can change "3" to "50" in one command.
3. **Rolling Updates:** When you upgrade from `v1` to `v2`, the Deployment performs a safe rollover:
    - Spin up one `v2` Pod. Wait for it to be ready.
    - Kill one `v1` Pod.
    - Repeat. (Zero Downtime).

---

### **3. Writing the YAML (The Contract)**

In AKS, we define our Workload in a `.yaml` file and send it to the API Server.

**File:** `my-api-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-dotnet-api   # Name of the Deployment logic
  namespace: dev        # Which room does it live in?
spec:
  replicas: 3           # Desired Count (3 instances)
  selector:
    matchLabels:
      app: my-dotnet-app # "I manage any Pod wearing this nametag"
  template:
    metadata:
      labels:
        app: my-dotnet-app # The Nametag
    spec:
      containers:
      - name: main-api
        image: mcr.microsoft.com/dotnet/samples:aspnetapp
        ports:
        - containerPort: 8080 # Informational mainly
        resources: # CRITICAL for AKS Cost/Stability
          requests:
            memory: "128Mi"
            cpu: "250m" # 0.25 Cores
          limits:
            memory: "256Mi"
            cpu: "500m"

```

**How to apply it:**

```bash
kubectl apply -f my-api-deployment.yaml

```

**Labels & Selectors (The Glue):**
Notice `matchLabels` and `labels`. This is how K8s connects things.

1. The Pod is born with a sticker: `app: my-dotnet-app`.
2. The Deployment looks for any pod with that sticker.
3. If it finds 2 pods with that sticker but wants 3, it creates another one.

---

### **4. StatefulSets (The Database Trap)**

A **Deployment** assumes all Pods are interchangeable (Cattle).
A **StatefulSet** assumes Pods have identity (Pets).

- **Behavior:** Pods get sticky names: `db-0`, `db-1`, `db-2`. If `db-0` dies, it is recreated as `db-0` and reattached to its specific Hard Drive (Persistent Volume).
- **Use Case:** Running SQL Server, MongoDB, or Redis *inside* the cluster.
- **Expert Advice:** **Avoid running Databases in AKS.** Managing stateful workloads in K8s is incredibly hard (backups, failover, replication).
    - **The Azure Way:** Use **Azure SQL Database** (PaaS). Connect your AKS pods to Azure SQL via connection strings. Keep the cluster stateless.

---

### **5. Jobs & CronJobs (Task Runners)**

Sometimes you need to run a `.NET Console App` that performs a DB migration or generates a PDF report and then **Exits**.

- **Job:** Runs a container until it exits with Code 0 (Success). Retries if it fails.
- **CronJob:** A Job that runs on a schedule (like Windows Task Scheduler).

**Example Scenario: Database Migrations**
Instead of running `EF Core Migrate` inside your API startup (which is bad), create a **Job** that runs the migration container during the release pipeline.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-v1
spec:
  template:
    spec:
      containers:
      - name: migration-tool
        image: my-registry.io/db-migrator:v1
        command: ["dotnet", "efbundle"]
      restartPolicy: Never

```

---

### **Summary of Phase 2**

1. **Pods** are the smallest unit. They are mortal. Don't manage them manually.
2. **Deployments** manage Pods for your .NET Web APIs. They handle self-healing and zero-downtime updates.
3. **Selectors** are how Deployments find their Pods.
4. **YAML** is the declarative source of truth.
5. **StatefulSets** are for databases, but PaaS (Azure SQL) is usually better.

**The Current State:**
You have applied the YAML. 3 Pods are running.
**The Problem:** You cannot access them. They have internal IPs (e.g., `10.244.0.5`), but no Public IP.

Are you ready for **Phase 3: Networking**? (Where we expose these Pods to the internet via Services and Ingress).