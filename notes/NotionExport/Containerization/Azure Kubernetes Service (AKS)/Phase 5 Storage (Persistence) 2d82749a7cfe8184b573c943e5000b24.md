# Phase 5: Storage (Persistence)

We established in Phase 4 (Docker) that containers have amnesia. In Kubernetes, this is even more volatile because Pods actually move between servers (Nodes).

If your .NET app saves a file to `C:\\local\\temp` or `/app/uploads` and that Pod is rescheduled to a new Node, **that file is deleted.**

To become an expert, you must understand the distinction between **Block Storage** (Disks) and **File Storage** (Shares), and how AKS abstracts them via CSI Drivers.

---

### **1. The Abstraction: PVC vs. PV**

In the Cloud, developers shouldn't need to know the Physical Disk ID. Kubernetes solves this with a "Ticket System".

1. **PVC (Persistent Volume Claim):** The **Ticket**.
    - The Developer writes a YAML file saying: "I need 10GB of storage."
2. **PV (Persistent Volume):** The **Resource**.
    - This is the actual pointer to the Azure Managed Disk or Azure File Share.
3. **StorageClass:** The **Menu**.
    - This tells AKS *what kind* of storage to create when it sees a ticket (e.g., fast SSD vs. cheap HDD).

**Dynamic Provisioning (The Magic):**
In AKS, you rarely create a PV manually. You create a PVC, and AKS automatically calls the Azure API, creates a Disk/Share, and binds it to your Pod.

---

### **2. Access Modes: The "One vs. Many" Problem**

This is the #1 reason deployments fail in storage scenarios. You must choose the right mode.

### **Mode A: ReadWriteOnce (RWO)**

- **Analogy:** A physical USB stick. Only one computer can plug it in at a time.
- **Azure Backend:** **Azure Managed Disk**.
- **Use Case:** Databases (SQL, Redis). High performance, exclusive access.
- **Limitation:** If you run `replicas: 3`, **only 1 Pod can start**. The other 2 will fail because the disk is already "plugged in" to the first Pod.

### **Mode B: ReadWriteMany (RWX)**

- **Analogy:** A Shared Network Folder (SMB/NFS). Many computers can read/write simultaneously.
- **Azure Backend:** **Azure Files**.
- **Use Case:** Web Servers saving User Uploads (Avatars, Reports). All 3 replicas can write to the same folder.
- **Performance:** Slower than Disks. Do not run a Database on this.

---

### **3. Implementing Block Storage (Azure Disk - RWO)**

Use this for high-performance needs where only **one** instance runs (e.g., a singleton background processor or a database).

**The YAML (PVC):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-disk-claim
spec:
  accessModes:
    - ReadWriteOnce # <--- Requires Azure Disk
  storageClassName: managed-csi # Premium SSD in AKS
  resources:
    requests:
      storage: 5Gi # Create a 5GB Disk

```

**The YAML (Pod Mount):**

```yaml
spec:
  containers:
  - name: my-app
    image: ...
    volumeMounts:
    - mountPath: "/app/data"
      name: data-volume
  volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: my-disk-claim

```

---

### **4. Implementing File Storage (Azure Files - RWX)**

Use this if you have `replicas: 3` and you need them to share uploaded PDFs or images.

**The YAML (PVC):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-shared-files
spec:
  accessModes:
    - ReadWriteMany # <--- Critical! Allows multiple pods
  storageClassName: azurefile-csi # Uses Azure Files (SMB)
  resources:
    requests:
      storage: 10Gi

```

- **Result:** All 3 pods see the same contents at `/app/uploads`. If Pod A writes `logo.png`, Pod B sees `logo.png` instantly.

---

### **5. The Blob Storage CSI Driver (Expert Level)**

What if you have Petabytes of data? You don't want an Azure Managed Disk (Expensive) or Azure Files (Protocol overhead). You want **Azure Blob Storage**.

AKS has a new **Blob CSI Driver**. It allows you to mount an Azure Blob Container as a folder using **BlobFuse**.

- **Why?** You can treat Blob Storage like a local folder.
- **Code:** `File.ReadAllText("/mnt/blob/data.txt")`
- **Reality:** It is actually streaming from Azure Blobs.

**Expert Advice:**
While cool, mounting Blob Storage as a drive is usually an **Anti-Pattern** for .NET code. It hides the network latency.
**Better Approach:** Use the `Azure.Storage.Blobs` SDK in C# and talk to Blob Storage directly via API. Only use the CSI mount if using legacy software that *must* write to a file path.

---

### **6. StatefulSets & Databases (Master Level)**

We mentioned in Phase 2 that **StatefulSets** are for DBs. Storage is why.

If you deploy a Mongo/SQL cluster, you need 3 Pods (`db-0`, `db-1`, `db-2`), and they each need their **own distinct** disk. You don't want them sharing one disk (Corruption!).

**VolumeClaimTemplates:**
Inside a StatefulSet YAML, you provide a template. K8s generates a unique PVC for each Pod.

- `db-0` gets `disk-0`
- `db-1` gets `disk-1`

**The Master's Rule on Databases:**

> "Just because you can run stateful workloads in AKS, doesn't mean you should."
> 

For a .NET Architecture:

1. **Apps (Stateless):** Run in AKS. Use `azurefile-csi` for simple uploads if needed.
2. **Databases (Stateful):** Use **Azure SQL / CosmosDB**.
3. **Large Files:** Use **Azure Blob Storage SDK**.

**Why?**
If you run SQL in AKS using a PVC (Azure Disk), and the Azure Availability Zone goes down, your DB goes down. AKS doesn't automatically handle cross-zone replication logic for SQL Server—YOU have to configure that. Azure SQL PaaS does it for you.

---

### **Summary of Phase 5**

1. **Dynamic Provisioning:** Create a PVC, and AKS creates the Azure Resource for you.
2. **Storage Classes:**
    - `managed-csi` = Managed Disk (Fast, Single Pod).
    - `azurefile-csi` = Azure Files SMB (Slower, Shared Pods).
3. **Access Modes:** Match the mode to the class. Don't try to attach a Disk to multiple Pods (RWX).
4. **Persistence:** If you delete the PVC, you lose the underlying Azure Disk and the data! Set `reclaimPolicy: Retain` if you are paranoid.

**Current State:**
We have Apps, Networking, Configs, and now Storage.
**The Problem:** We are running 3 pods manually. What if Black Friday hits and we need 50? What if the cluster is full?

Are you ready for **Phase 6: Scaling & Scheduling**? (Horizontal Pod Autoscaling and Cluster Autoscaling).