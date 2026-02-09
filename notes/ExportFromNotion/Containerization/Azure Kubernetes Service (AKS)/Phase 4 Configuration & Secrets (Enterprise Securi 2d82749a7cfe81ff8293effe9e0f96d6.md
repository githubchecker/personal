# Phase 4: Configuration & Secrets (Enterprise Security)

In Phase 2, we hardcoded connection strings in the YAML. In Phase 3, we fixed networking. Now, we must fix the Security and Configuration.

In the old VM world, you relied on **File Transformations** (replacing JSON in the Zip file).
In Kubernetes, we decouple the **Image** (Binary) from the **Configuration**. The Image is immutable; the Configuration is injected at runtime.

---

### **1. ConfigMaps (Non-Sensitive Data)**

**The Concept:**
A **ConfigMap** is a K8s object that stores non-confidential data in key-value pairs. Think of it as a dictionary floating in the cluster.

**The .NET Strategy:**
We can "Mount" a ConfigMap into the container so it appears as a physical file on the disk (e.g., `appsettings.Production.json`).

### **Step A: The YAML definition**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-api-config
  namespace: dev
data:
  # The Key becomes the Filename, the Value becomes the Content
  appsettings.Production.json: |
    {
      "Logging": { "LogLevel": { "Default": "Warning" } },
      "FeatureManagement": { "NewCheckout": true }
    }

```

### **Step B: Mounting it in the Deployment**

We update our Deployment YAML to create a "Volume" from this ConfigMap and "Mount" it to the .NET app folder.

```yaml
spec:
  containers:
  - name: my-api
    image: myrepo.azurecr.io/api:v1
    volumeMounts:
    # "Take the volume 'config-vol' and place it at /app/config"
    - name: config-vol
      mountPath: /app/appsettings.Production.json
      subPath: appsettings.Production.json # Only mount this specific file, don't overwrite the whole folder
  volumes:
  - name: config-vol
    configMap:
      name: my-api-config

```

**Result:** When .NET starts, it automatically loads `appsettings.json` (baked in image), and then overlays `appsettings.Production.json` (from K8s), merging the settings.

---

### **2. Secrets (The Native K8s Way - Novice/Intermediate)**

**The Concept:**
Just like ConfigMaps, but meant for passwords.

- **The Flaw:** By default, K8s Secrets are stored in **Base64 encoding**, not encryption. If you have access to the cluster, you can decode them easily (`echo "..." | base64 --decode`).

**Implementation:**
Usually, we inject these as **Environment Variables**, not files.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-db-secret
type: Opaque
data:
  # Values MUST be base64 encoded strings
  # echo -n "Password123!" | base64
  db-password: UGFzc3dvcmQxMjMh

```

**Injection in Deployment:**

```yaml
env:
- name: ConnectionStrings__DefaultConnection
  valueFrom:
    secretKeyRef:
      name: my-db-secret
      key: db-password

```

---

### **3. Azure Key Vault Provider (The Expert Way)**

**The Problem:**
Security teams hate K8s Secrets because they sprawl across clusters. They want centralized control (Audit logs, Rotation policies) in **Azure Key Vault (AKV)**.

**The Solution:**
Use the **Secrets Store CSI Driver**. This is an add-on for AKS that allows the cluster to reach into AKV, grab secrets, and mount them as files.

### **Step A: Enable the Add-on**

```bash
az aks enable-addons --addons azure-keyvault-secrets-provider --name MyCluster --resource-group MyRG

```

### **Step B: define the `SecretProviderClass`**

This tells AKS *which* Key Vault to talk to.

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-kv-sync # We reference this name later
spec:
  provider: azure
  parameters:
    usePodIdentity: "false" # We use Workload Identity now
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "<CLIENT_ID_OF_NODE_IDENTITY>"
    keyvaultName: "my-company-kv"
    objects: |
      array:
        - |
          objectName: ProductionDbSecret
          objectType: secret
    tenantId: "<YOUR_TENANT_ID>"

```

### **Step C: Mount in Pod**

```yaml
volumes:
- name: secrets-store-inline
  csi:
    driver: secrets-store.csi.k8s.io
    readOnly: true
    volumeAttributes:
      secretProviderClass: "azure-kv-sync" # Matches the class above

```

**Result:** The file `/mnt/secrets-store/ProductionDbSecret` appears inside your container containing the password.

---

### **4. Workload Identity (The Master Level - No Secrets)**

**The Philosophy:**
Storing a password (even in Key Vault) is a risk. Rotating passwords requires restarting apps.
**The Master Solution:** Eliminate the password entirely using **Microsoft Entra Workload ID** (formerly Pod Identity).

Your Pod "Logs In" to Azure SQL using a Federation Token.

### **Step A: Setup Identity**

1. Create a **Managed Identity** in Azure (`MyAksIdentity`).
2. Grant this Identity permission to access Azure SQL (`CREATE USER [MyAksIdentity] FROM EXTERNAL PROVIDER`).
3. Federate this identity with a Kubernetes Service Account.

### **Step B: Annotate Service Account**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: "<CLIENT_ID_OF_MANAGED_IDENTITY>"
  name: my-service-account

```

### **Step C: Deployment Configuration**

Tell the Pod to use that Service Account.

```yaml
spec:
  serviceAccountName: my-service-account
  containers:
  - image: my-api
    # No ENV Vars for Password needed!

```

### **Step D: C# Code Change (`DefaultAzureCredential`)**

Update your .NET code to stop looking for passwords in the connection string.

```csharp
using Azure.Identity; // Install Azure.Identity NuGet

// The New Connection String has NO Password:
// "Server=tcp:prod.database.windows.net;Database=Master;Authentication=Active Directory Default;"

// Or if using EF Core directly:
var conn = new SqlConnection("Server=tcp:...");
// This line magically grabs the token from the K8s environment
var credential = new DefaultAzureCredential();
var token = await credential.GetTokenAsync(new TokenRequestContext(new[] { "<https://database.windows.net/.default>" }));
conn.AccessToken = token.Token;

```

**Why this is the Master Level:**

1. **Zero Secrets:** There is no password in YAML, Key Vault, or Git.
2. **Audit:** Azure SQL logs show "MyAksIdentity accessed DB", not just "User SA".
3. **Rotation:** Not needed. Tokens expire automatically.

---

### **Summary of Phase 4**

1. **ConfigMaps:** Use these for `appsettings.json` overlays. Mount them as files (`subPath` is key).
2. **K8s Secrets:** Okay for small/non-critical projects. Base64 is not encryption.
3. **CSI Driver:** Syncs Azure Key Vault to the Pod. Standard for enterprise.
4. **Workload Identity:** The goal. Removes passwords entirely by using Entra ID (Azure AD) tokens directly in C#.

**Current State:**
We have secure Apps running, networking is set, and configs are injected safely.
**The Missing Piece:** Data. What if the Pod crashes? Where does the file upload go?

Are you ready for **Phase 5: Storage (Persistence)**?