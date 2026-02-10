# Service Connections for AKS

Of course. Point 2, **Service Connections for AKS**, is the absolute cornerstone of secure Kubernetes deployments in Azure DevOps. If you get this wrong, your pipeline either won't work or, far worse, will have dangerously excessive permissions.

Let's do a deep dive.

### **1. What is the Core Problem? Authentication.**

Your Azure DevOps pipeline is an **external system**. Your AKS cluster is a **secure, internal system**.

How does the pipeline prove to the AKS API server that it is authorized to run commands like `kubectl apply`? It needs a set of credentials. A **Service Connection** is the secure wrapper in Azure DevOps for storing and managing these credentials.

For AKS, you are not storing a simple username/password. You are storing credentials that allow the pipeline to authenticate as a specific **identity** within the Kubernetes security model.

---

### **2. The Wrong Way: The "Cluster Admin" Trap**

A novice might be tempted to do this:

1. Run `kubectl config view --raw` on their own machine (which has cluster-admin rights).
2. Copy the entire `kubeconfig` block, including the super-user token.
3. Create a generic "KubeConfig" Service Connection in Azure DevOps and paste this in.

**Why this is a disaster:**

- You have just given your CI/CD pipeline **god-mode access** to your entire cluster.
- A bug in your deployment script (or a malicious script) could accidentally run `kubectl delete all --all-namespaces` and wipe out your entire production environment.
- The token is likely tied to a human user account, which is a bad practice for automation.

---

### **3. The Right Way: Namespace-Scoped, Role-Based Access Control (RBAC)**

The principle of least privilege dictates that your pipeline should only have the **exact permissions it needs**, and only in the **specific namespace it's supposed to deploy to**.

Here's how to achieve this by creating a dedicated **Service Account** for your pipeline inside Kubernetes.

### **The Workflow:**

1. **In Kubernetes:** Create a `ServiceAccount` that your pipeline will use.
2. **In Kubernetes:** Create a `Role` that defines the allowed actions (e.g., can `create` and `patch` Deployments, but cannot `delete` Nodes).
3. **In Kubernetes:** Create a `RoleBinding` that "binds" the `Role` to the `ServiceAccount`.
4. **In Azure DevOps:** Create a "Kubernetes" Service Connection that uses the token from this `ServiceAccount`.

While this sounds complex, the **Azure DevOps Environment UI** (from Point 1) does most of this for you automatically! Let's review that process with a security lens.

---

### **4. Creating the Service Connection via the Environment UI (The Recommended Way)**

This is the method we discussed in Point 1, but let's focus on the Service Connection aspect.

**When you create a new Environment and add a "Kubernetes" resource:**

1. You select your AKS cluster and a namespace (e.g., `dev`).
2. Azure DevOps automatically runs `kubectl` commands against your cluster (using your current logged-in user's permissions) to create:
    - A `ServiceAccount` named something like `my-project-dev-1234`.
    - A `Role` named `edit` or similar, which has standard permissions to manage workloads within the `dev` namespace.
    - A `RoleBinding` linking the `ServiceAccount` to that `Role`.
3. It then creates a secret for that `ServiceAccount` and extracts its long-lived token.
4. Finally, it creates a **new Service Connection** in your project's settings. The name will be something like `MyAKSCluster-dev`. This connection stores the AKS API Server URL and the secure token for the newly created `ServiceAccount`.

**The result is a perfect, least-privilege setup.** The Service Connection that is created can *only* manage resources inside the `dev` namespace. If a pipeline using this connection tries to deploy to the `default` or `prod` namespace, Kubernetes will correctly deny the request with a `Forbidden` error.