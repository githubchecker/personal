# Phase 6: Scaling & Scheduling

You now have a running application. But one of the main reasons to use Kubernetes is its ability to handle **elastic traffic**.

If you get featured on Hacker News or it's Black Friday, you need to handle 10x traffic. When the traffic stops, you want to stop paying for those servers.

To master this, you must understand the "Tetris" game of Scheduling, followed by the two layers of Autoscaling.

---

### **1. Requests & Limits (The Contract)**

Before K8s can scale anything, it needs to know how big your container is.

- **Requests (The Scheduler's View):**
    - "I need *at least* this much CPU/RAM to start."
    - K8s uses this to decide **which Node** to place the Pod on. If no Node has enough free space to satisfy the Request, the Pod stays in `Pending` state.
- **Limits (The Linux Kernel's View):**
    - "I promise not to use more than this."
    - **RAM:** If your .NET app tries to allocate more RAM than the Limit -> **OOMKilled** (Out of Memory Error). K8s restarts the Pod.
    - **CPU:** If you try to use more CPU -> **Throttling**. Your app slows down, but doesn't crash.

**The "Novice" Mistake:** Not defining these.
**Result:** "Noisy Neighbor." One runaway .NET app with a memory leak eats 100% of the Node's RAM, crashing other critical services (like DNS) running on the same node.

**The "Expert" YAML:**

```yaml
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"  # 100 millicores (0.1 CPU)
      limits:
        memory: "512Mi" # Hard limit
        cpu: "500m"

```

- **Pro Tip for .NET:** Explicitly configuring these helps the CLR (Common Language Runtime) calculate how much Garbage Collection overhead it needs.

---

### **2. Horizontal Pod Autoscaler - HPA (Scaling the Workload)**

This scales the **Number of Pods**.

- **Logic:** K8s checks metrics every 15 seconds.
    - *Current CPU is 80%. Target is 50%. Formula says: Double the Pods.*
- **Prerequisite:** You **MUST** have Resources (Requests/Limits) defined, or HPA cannot calculate percentage usage.

**The Declarative YAML:**
Don't use `kubectl autoscale`. Write it down.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-dotnet-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70 # Scale if Avg CPU > 70%

```

---

### **3. Cluster Autoscaler - CA (Scaling the Infrastructure)**

This scales the **Number of Nodes (VMs)**.

**The Workflow:**

1. Traffic spikes. HPA increases Pod count from 2 to 10.
2. The Scheduler tries to place the new Pods, but your current Nodes (VMs) are full (based on Requests).
3. Pods go into **`Pending`** state.
4. **Cluster Autoscaler** sees `Pending` pods.
5. It talks to the Azure API (VMSS) and orders a new VM.
6. 5 minutes later, the Node is ready, and the Pods start.

**Cost Saving:**
When traffic drops, HPA deletes pods. Nodes become empty. Cluster Autoscaler detects an under-utilized Node, moves the remaining pods elsewhere ("Draining"), and **deletes the VM** to stop your Azure bill.

---

### **4. KEDA: Event-Driven Scaling (The Master Skill)**

HPA is great for HTTP APIs (CPU scales with traffic).
**HPA is terrible for Background Workers.**

**The Scenario:**
You have a .NET Console App processing an **Azure Service Bus Queue**.

- Queue has 10,000 messages.
- CPU is low (10%) because the app is just waiting on I/O.
- **Result:** HPA sees low CPU and *scales down*, even though you have a massive backlog!

**The Solution: KEDA (Kubernetes Event-driven Autoscaling)**
KEDA is an installed component (addon) in AKS. It lets you scale based on **External Metrics**.

**The KEDA YAML (`ScaledObject`):**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sb-worker-scaler
spec:
  scaleTargetRef:
    name: my-background-worker # Target Deployment
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
  - type: azure-servicebus
    metadata:
      queueName: orders
      connectionFromEnv: SERVICEBUS_CONNECTION_STRING
      messageCount: '5' # Target 5 messages per Pod

```

- **Logic:** "If there are 100 messages in the queue, give me 20 pods (100/5)."

---

### **5. Node Selectors, Affinity, and Taints (Advanced Scheduling)**

Sometimes, not all Nodes are equal.

- **Scenario:** You have a "GPU Node Pool" (Expensive) for ML and a "Standard Node Pool" for Web APIs. You don't want the Web API wasting space on the GPU node.

### **Mechanism A: Node Selectors**

"Only run this Pod on Linux nodes."

```yaml
spec:
  nodeSelector:
    kubernetes.io/os: linux

```

### **Mechanism B: Taints & Tolerations (The VIP Section)**

1. **Taint the Node:** You spray "Repellent" on the GPU nodes using `kubectl taint`.
    - *Effect:* Normal pods cannot land there.
2. **Toleration on Pod:** You give your ML Pod a "Gas Mask" (Toleration).
    - *Effect:* Only the ML Pods can land on the GPU node.

### **1. The Core Concept: The "Bug Spray" Analogy**

To understand Taints, you have to invert your thinking.

- **Node Selectors/Affinity** are about **Attraction** ("Please put me on the Blue Node").
- **Taints** are about **Repulsion** ("Get away from me!").

**The Analogy:**

1. **The Taint (On the Node):** Imagine you spray "Bug Spray" on a specific server (Node).
2. **The Result:** Normal Pods (Mosquitoes) cannot land on that Node. The Scheduler will refuse to place them there.
3. **The Toleration (On the Pod):** You give a specific Pod a "Gas Mask". This Pod creates a special exception. It allows the Pod to land on the Tainted Node (though it doesn't force it to).

---

### **2. Why use Taints in AKS? (Real World Use Cases)**

You don't use Taints for fun. You use them for **Money** and **Stability**.

### **Case A: The GPU / High-Performance Node**

You bought a Node Pool with NVidia A100 GPUs (very expensive).

- **Without Taint:** Kubernetes is dumb. It sees free CPU on the GPU Node and schedules your tiny "Hello World" API there. You are paying $10/hour for a Hello World app to sit on a GPU.
- **With Taint:** You Taint the GPU node. Regular apps are blocked. Only your AI/ML .NET Worker (with the Toleration) can land there.

### **Case B: Spot Instances (Cost Savings)**

You create a Node Pool using **Azure Spot Instances** (90% cheaper, but can be deleted by Azure at any time).

- **The Taint:** Azure automatically taints these nodes.
- **The Workflow:** Your critical "Payment API" won't go there (good!). Your background "Report Generator" (which can restart safely) has a Toleration, so it utilizes the cheap nodes.

### **Case C: System Node Isolation**

In AKS, the "System Node Pool" (where CoreDNS and Metrics Server run) runs critical infrastructure.

- **Best Practice:** You taint the System Node Pool (`CriticalAddonsOnly=true:NoSchedule`). This ensures your buggy memory-leaking application doesn't accidentally crash the DNS server by eating all the RAM.

---

### **3. The Anatomy of a Taint**

A Taint consists of three parts: `Key=Value:Effect`

**The 3 Effects:**

1. **`NoSchedule` (Most Common):** New Pods will not be placed here unless they tolerate it. Existing Pods (if any) stay running.
2. **`PreferNoSchedule`:** "Soft" Taint. The Scheduler tries to avoid this node, but if there is literally nowhere else to go, it will place the Pod here.
3. **`NoExecute` (Nuclear Option):** New Pods are blocked. **AND** any existing Pods running on the Node that do *not* have the toleration are immediately Evicted (Killed).
    - *Use Case:* Hardware maintenance. You taint a node `NoExecute`, and it automatically scrubs itself clean of workloads.

---

### **4. How to Implement it (Step-by-Step)**

### **Step 1: Taint the Node (Infrastructure Layer)**

In AKS, you usually do this when creating the **Node Pool**.

**Via CLI:**

```bash
# Syntax: az aks nodepool add ... --node-taints key=value:Effect
az aks nodepool add \\
    --resource-group MyRG \\
    --cluster-name MyCluster \\
    --name gpupool \\
    --node-vm-size Standard_NC6s_v3 \\
    --node-taints sku=gpu:NoSchedule

```

**Manual (via Kubectl):**

```bash
kubectl taint nodes aks-gpupool-1234 sku=gpu:NoSchedule

```

**Result:** At this point, **NO** pods can run on this node. It sits empty.

### **Step 2: Add Toleration to the Pod (Application Layer)**

Now, we allow our special .NET AI Worker to land there.

**YAML:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-processor
spec:
  template:
    spec:
      containers:
      - image: my-ai-app:v1
        name: main

      # THE GAS MASK
      tolerations:
      - key: "sku"          # Must match the Taint Key
        operator: "Equal"
        value: "gpu"        # Must match the Taint Value
        effect: "NoSchedule" # Must match the Effect

```

---

### **5. The "Combo Move": Taints + Affinity (Expert Level)**

This is a subtle interview question.

**Question:** "I added a Toleration to my Pod. Why is it scheduling on my standard nodes?"

**Answer:**

- **Taint/Toleration** says: "This Pod is **Allowed** to enter the VIP Room." (It does NOT say "You MUST enter the VIP Room").
- The Pod interprets this as: "I can go to the Standard Node OR the GPU Node." The Scheduler might still put it on the Standard node because it's cheaper/emptier.

**To force the Pod to the GPU Node:**
You need **Both**:

1. **Toleration:** To get past the Bouncer (Taint) of the GPU Node.
2. **Node Affinity:** To force the Scheduler to *choose* the GPU Node.

**The Complete Expert YAML:**

```yaml
spec:
  # 1. Permission to land (The Shield)
  tolerations:
  - key: "sku"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"

  # 2. Requirement to land (The Magnet)
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: sku
            operator: In
            values:
            - gpu

```

### **Summary of Taints**

| Feature | Role | Direction |
| --- | --- | --- |
| **Taint** | Applied to **Node** | Repels Pods (Bug Spray) |
| **Toleration** | Applied to **Pod** | Ignores Repulsion (Gas Mask) |
| **NoSchedule** | Effect | "Don't put new stuff here" |
| **NoExecute** | Effect | "Kick everyone out immediately" |

Use Taints when you have specialized hardware or critical system nodes in your AKS cluster that must be protected from generic workloads.

---

### **Summary of Phase 6**

1. **Requests & Limits:** Mandatory. Without them, scaling logic is impossible.
2. **HPA:** Scales **Pods** based on CPU/RAM. (Fast: seconds).
3. **Cluster Autoscaler:** Scales **Nodes** when HPA pushes too many pods. (Slow: minutes).
4. **KEDA:** The industry standard for scaling .NET Background Workers based on Queue/Topic depth.
5. **Taints:** Use these to keep expensive hardware reserved for specific workloads.

**Current State:**
Your app scales up and down automatically. It uses Azure Disks securely. It connects via Ingress.
**The Missing Piece:** How do we update it without breaking it? How do we manage 100 YAML files?

Are you ready for **Phase 7: The "GitOps" Workflow**? (Helm and ArgoCD).