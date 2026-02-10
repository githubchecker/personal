# Environments in Azure DevOps for AKS

Of course. Let's do a deep dive into **Environments in Azure DevOps**, specifically focusing on their integration with **Azure Kubernetes Service (AKS)**.

This is a feature that elevates a deployment pipeline from a simple script-runner to a traceable, auditable, and controllable release management system.

---

### **1. What is an Environment in Azure DevOps?**

At its simplest, an **Environment** is a **logical target for deployment**. It's a named collection of resources where you deploy your application. Common names are `Dev`, `QA`, `Staging`, and `Production`.

However, its real power comes from the features it enables:

- **Deployment History & Traceability:** You get a full audit trail of which build, which commit, and which user deployed to that environment.
- **Security & Approvals:** You can place manual approval gates and security checks on an environment.
- **Resource Integration:** You can link the logical environment directly to a physical resource, like a Kubernetes namespace.

---

### **2. Why Use Environments for AKS? (The Problem it Solves)**

Without environments, your deployment is a "fire and forget" operation.

- **The "Dumb" Way:** You use a standard `job` and a `kubectl apply` script. The pipeline tells you "Success," but Azure DevOps has no idea *what* is actually running inside your `dev` namespace in AKS. It can't tell you if `Deployment 'my-api'` is healthy or which version is active.

**The "Smart" Way (with Environments):**
By linking your `Dev` environment to the `dev` namespace in your AKS cluster, you tell Azure DevOps:

> "This logical 'Dev' environment is the dev namespace in my AKS cluster. Please track what I deploy there."
> 

This creates a rich, two-way connection.

---

### **3. How to Create and Link an AKS Environment**

Here is the step-by-step process.

**Step 1: Go to the "Environments" Hub**
In your Azure DevOps project, navigate to **Pipelines -> Environments**.

**Step 2: Create a New Environment**

1. Click **"Create environment"**.
2. **Name:** `AKS-Production` (or `AKS-Dev`, `AKS-QA`).
3. **Description:** A clear description, like "Production Kubernetes Cluster (East US)".
4. **Resource:** Select **Kubernetes**.
5. Click **Next**.

**Step 3: Link to the Kubernetes Namespace**
This is the crucial connection step.

1. **Provider:** Select **Azure Kubernetes Service**.
2. **Azure subscription:** Choose the subscription where your AKS cluster lives.
3. **Cluster:** Select your AKS cluster from the dropdown.
4. **Namespace:** Here you link it.
    - Choose **"Use existing"** and select a namespace like `production` from the dropdown.
    - Or, choose **"Create new"** and type `production`. This will also create a `ServiceAccount` and a `RoleBinding` in that namespace, giving Azure DevOps the necessary permissions to deploy.

**Step 4: Review and Create**
Click **"Validate and create"**.

**What just happened in the background?**

- Azure DevOps created the logical `AKS-Production` environment.
- It reached into your AKS cluster and created a `ServiceAccount`.
- It created a `Role` and `RoleBinding` in the `production` namespace that gives that `ServiceAccount` permissions (like `create`, `list`, `patch` on Deployments, Services, etc.).
- It automatically created a **Kubernetes Service Connection** that uses the token from this new `ServiceAccount`.

You now have a secure, namespace-scoped connection without giving your pipeline cluster-admin rights!

---

### **4. Using the Environment in a YAML Deployment Job**

Now, you use the `environment` keyword in a `deployment` job to target this specific linked resource.

```yaml
stages:
- stage: DeployToProd
  jobs:
  # This is a special job type that understands environments
  - deployment: DeployApi
    displayName: 'Deploy API to Production Namespace'
    pool:
      vmImage: 'ubuntu-latest'

    # THIS IS THE KEY
    # It targets the environment you just created.
    environment: 'AKS-Production.production' # Format: {EnvironmentName}.{ResourceName}

    strategy:
      runOnce:
        deploy:
          steps:
          - task: Kubernetes@1
            displayName: 'Deploy Manifests'
            inputs:
              # The service connection was created automatically for you!
              # You can find its name in the Environment's resource details.
              kubernetesServiceConnection: 'MyAKSCluster-production'
              action: 'deploy'
              namespace: 'production'
              manifests: |
                $(Pipeline.Workspace)/manifests/deployment.yaml
                $(Pipeline.Workspace)/manifests/service.yaml

```

---

### **5. The Benefits in the Azure DevOps UI**

Because you used a `deployment` job linked to a Kubernetes `environment`, you unlock a new UI experience.

When you go back to **Pipelines -> Environments -> AKS-Production**, you will now see:

- **Deployments Tab:** A history of every pipeline run that deployed to this environment, linked to the work items and commits.
- **Resources Tab:** Under the Kubernetes resource, you get a live view into the cluster!
    - **Workloads:** See the status of your `Deployments`, `ReplicaSets`, and `Pods`. You can see if they are healthy and how many replicas are running.
    - **Services & Ingresses:** See the IP addresses and ports of your running `Services` and `Ingresses`.

This provides invaluable visibility directly from Azure DevOps, bridging the gap between your pipeline and the live state of your Kubernetes cluster. It's the difference between flying blind and having a full dashboard.