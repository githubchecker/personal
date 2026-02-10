# ImagePullSecrets

You've hit on one of the most common stumbling blocks when moving from public Docker images to a private, secure workflow. Let's do a deep dive into `imagePullSecrets`, covering the "why," the different solutions, and exactly how you would integrate this into an Azure DevOps pipeline.

---

### **1. The Problem: "Who Are You?"**

By default, an Azure Kubernetes Service (AKS) cluster knows how to pull public images from Docker Hub. It does **not** know who your private **Azure Container Registry (ACR)** is, and it certainly doesn't have the password.

**The Symptom:**

1. Your CI pipeline successfully builds your Docker image (`my-api:v1.2`) and pushes it to your private ACR (`mycompany.azurecr.io`).
2. Your CD pipeline runs `kubectl apply -f deployment.yaml`.
3. You run `kubectl get pods`. The pod is stuck in `ImagePullBackOff` or `ErrImagePull`.
4. You run `kubectl describe pod <pod-name>` and see the error: **`Failed to pull image "mycompany.azurecr.io/my-api:v1.2": rpc error: code = Unknown desc = failed to pull and unpack image ... authentication required`**.

The Kubernetes node tried to download the image from ACR, and ACR correctly responded with "401 Unauthorized."

---

### **2. The Solutions: Granting AKS Access to ACR**

There are two primary methods to solve this.

### **Method A: The Cluster-Wide ACR Attachment (The "Easy" Way)**

This is the most common and simplest solution for most scenarios where the AKS cluster and the ACR are in the same Azure subscription and managed by the same team.

- **Concept:** You create an identity link at the Azure level. You tell your AKS cluster, "You are permanently authorized to pull images from this specific ACR."
- **How it Works:** In the background, this command grants the **Managed Identity** used by your AKS nodes (the Kubelet identity) the `AcrPull` role on your ACR. This role allows it to read/download images.
- **The Command (One-time setup):**
    
    ```bash
    # Get the ID of your ACR
    ACR_ID=$(az acr show --name MyCompanyRegistry --resource-group MyResourceGroup --query "id" --output tsv)
    
    # Attach the ACR to your AKS cluster
    az aks update \\
      --name MyAKSCluster \\
      --resource-group MyResourceGroup \\
      --attach-acr $ACR_ID
    
    ```
    
- **Pros:**
    - **Simple:** One-time setup.
    - **No YAML Changes:** You do **not** need to add `imagePullSecrets` to any of your Kubernetes `deployment.yaml` files. It "just works" for every pod in the cluster.
- **Cons:**
    - **Less Granular:** It grants every pod in the entire cluster access to the registry. You can't easily restrict Namespace A from pulling images that are meant only for Namespace B.

### **Method B: `imagePullSecrets` (The "Granular" Kubernetes Way)**

This is the native Kubernetes way to handle private registry authentication. It gives you namespace-level control.

- **Concept:** You create a special type of Kubernetes `Secret` that holds the credentials for your ACR. Then, you explicitly tell each `Deployment` (or `ServiceAccount`) to use that secret when pulling its image.

---

### **3. Implementing `imagePullSecrets` in Azure DevOps**

Here is the full workflow, including the Azure DevOps pipeline tasks required to make this work.

### **Step 1: Create the Kubernetes Secret in your Cluster**

This secret is of type `kubernetes.io/dockerconfigjson`. You need to create it once per namespace where you will be deploying.

- **Credentials:** You need an identity to log in to ACR. The best practice is to create an Azure **Service Principal** with the `AcrPull` role scoped *only* to your ACR.
    - `CLIENT_ID`: The Service Principal's App ID.
    - `CLIENT_SECRET`: The Service Principal's password.
- **The `kubectl` command:**
You run this command from your local machine (or in a pipeline script) once to set up the secret in the `dev` namespace.
    
    ```bash
    kubectl create secret docker-registry acr-credentials \\
      --namespace dev \\
      --docker-server=mycompany.azurecr.io \\
      --docker-username=<CLIENT_ID> \\
      --docker-password=<CLIENT_SECRET>
    
    ```
    
    This creates a secret named `acr-credentials` inside the `dev` namespace.
    

### **Step 2: Modify your Kubernetes `deployment.yaml`**

Now, you must tell your `Deployment` to use this secret. This is done by adding the `imagePullSecrets` section to your pod's template spec.

**`deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api-deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: my-api
        image: mycompany.azurecr.io/my-api:__ImageTag__ # Note the replacement token

      # THE MAGIC LINE
      # Tells K8s: "When you pull the image above, use the credentials
      # stored in the 'acr-credentials' secret."
      imagePullSecrets:
      - name: acr-credentials

```

### **Step 3: The Azure DevOps Pipeline Definition**

Your pipeline now needs to do several things:

1. Build and Push the Docker image to ACR.
2. Replace the `__ImageTag__` placeholder in `deployment.yaml` with the current build ID.
3. Apply the modified manifest to the cluster.

Here's what a task for handling `imagePullSecrets` within a larger deployment pipeline might look like. In this example, we'll use a `Kubernetes@1` task that can also create the secret for you.

**The `azure-pipelines.yml` (CD Stage):**

```yaml
- stage: DeployToDev
  displayName: 'Deploy to Dev Namespace'
  jobs:
  - deployment: Deploy
    environment: 'AKS-Dev.dev' # Targeting the linked environment
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          # This assumes your Docker build/push happened in a previous stage
          # and the manifests were published as an artifact.
          - task: DownloadPipelineArtifact@2
            inputs:
              artifactName: 'manifests'
              targetPath: '$(Pipeline.Workspace)/manifests'

          # This is an alternative to running `kubectl create secret` manually.
          # The Kubernetes@1 task can do it for you.
          - task: Kubernetes@1
            displayName: 'Create or Update ImagePullSecret'
            inputs:
              command: 'create'
              secretType: 'dockerRegistry'
              secretName: 'acr-credentials'
              namespace: 'dev'
              dockerRegistryEndpoint: 'MyACRServiceConnection' # A DevOps Service Connection of type "Docker Registry"
              kubernetesServiceConnection: 'MyAKS-Dev-Connection' # The connection to AKS

          - task: Kubernetes@1
            displayName: 'Deploy to AKS'
            inputs:
              kubernetesServiceConnection: 'MyAKS-Dev-Connection'
              action: 'deploy'
              namespace: 'dev'
              manifests: '$(Pipeline.Workspace)/manifests/deployment.yaml'
              # The task can also substitute variables if needed
              # Or you can use a dedicated token replacement task first.
              containers: 'mycompany.azurecr.io/my-api:$(Build.BuildId)'

```

### **Summary: ACR Attachment vs. `imagePullSecrets`**

| Method | Granularity | Setup | YAML Changes Required | When to Use |
| --- | --- | --- | --- | --- |
| **ACR Attachment** | **Cluster-wide** | One-time `az aks update` command. | **None.** | Simple scenarios. When you trust all namespaces in your cluster to access your single ACR. **This is the easiest option.** |
| **`imagePullSecrets`** | **Namespace-level** | Create a `secret` in each namespace. | Add `imagePullSecrets` to **every Deployment YAML**. | Multi-tenant clusters. High-security environments. When you need to pull from multiple different private registries. |

For most new projects where you control both the ACR and AKS, starting with the **ACR Attachment** method is the fastest and simplest path. If your security requirements become more complex, you can then switch to the more granular `imagePullSecrets` approach.