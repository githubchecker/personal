# CD / Release

## **Phase 3: CD - Deploying Your Code & Service Connections**

You have a ZIP file in the Cloud (Phase 2). Now you need to push it to an Azure App Service.

To do this, Azure DevOps needs permission to talk to your Azure Subscription. This handshake is called a **Service Connection**.

---

### **1. Service Connections (The Handshake)**

If you don't get this right, you get the error: *"The subscription X does not exist or you are not authorized."*

### **The Three Ways to Create One**

Go to **Project Settings -> Service Connections -> New -> Azure Resource Manager**.

1. **Automatic (Service Principal):** *The Novice/Quick Way.*
    - **How:** You select "Automatic", log in with your Azure Credentials in a popup, and pick your Subscription from a list.
    - **What happens:** Azure DevOps creates an App Registration (Service Principal) in your Entra ID (Active Directory) automatically with "Contributor" access.
    - **Use case:** You are the admin and just want it to work.
2. **Manual (Service Principal):** *The Strict IT Way.*
    - **How:** Your IT team gives you a `Client ID`, `Tenant ID`, and `Client Secret` (Password). You paste these in.
    - **Use case:** You don't have permission to create Apps in Entra ID, or you want to limit scope to a specific Resource Group only.
3. **Managed Identity:** *The Expert Way (Self-Hosted).*
    - **How:** You select "Managed Identity".
    - **Requirement:** Only works on **Self-Hosted VM Agents**.
    - **Use case:** You assign the VM itself an Identity in Azure. No passwords/secrets exist to be stolen. DevOps just "assumes" the identity of the machine it is running on.

### **Usage in YAML**

Once created, you name it (e.g., `Azure-Prod-Connection`). You use this string in your pipeline:

```yaml
- task: AzureWebApp@1
  inputs:
    azureSubscription: 'Azure-Prod-Connection' # MUST Match exactly!
    appName: 'my-cool-api-v1'

```

---

### **2. The Deployment Job vs. Standard Job**

In CD, we stop using `job:`. We switch to `deployment:` and `environment:`.

- **Standard Job:** Just runs steps.
- **Deployment Job:**
    1. Downloads Artifacts automatically.
    2. Links the build to an **"Environment"** in Azure DevOps (where you can configure "Manual Approvals").
    3. Records deployment history (e.g., "Commit 123 is currently in Prod").

**YAML Syntax:**

```yaml
jobs:
- deployment: DeployWeb
  displayName: 'Deploy to App Service'
  environment: 'Production' # <--- Triggers Manual Approval Checks
  strategy:
    runOnce:
      deploy:
        steps:
          # Steps go here

```

---

### **3. Moving the Artifact (The Handoff)**

In Phase 2, we used `publishLocation: 'Container'`. Now we need to get it back.

- **Standard Job behavior:** You must write `task: DownloadPipelineArtifact@2`.
- **Deployment Job behavior:** It **Auto-Downloads** everything to `$(Pipeline.Workspace)`.

**Visualizing the Disk:**
When the CD stage starts, the agent looks like this:

```
C:\\agent\\_work\\1\\
    ├── my-drop-folder\\   <-- The artifact you downloaded
    │   └── api.zip

```

You refer to this path as: `$(Pipeline.Workspace)/my-drop-folder/api.zip`.

---

### **4. JSON Configuration Substitution**

**Problem:** Your `appsettings.json` inside the zip file has:  `"DbConnection": "Server=localhost"`.
**Goal:** In Production, you need `Server=prod-sql.azure.com`.

**The Solution:** The `AzureWebApp@1` task has a built-in JSON replacement feature.

1. **Define Variable:** In your Pipeline (Library), create a variable named `ConnectionStrings.DefaultConnection` with the value `Server=prod-sql...`.
2. **Enable Replacement:** In the task, set `JSONFiles` to match your settings file.

---

### **5. The Complete Phase 3 YAML**

Here is a full Multi-Stage pipeline. It builds in Stage 1, and Deploys in Stage 2.

```yaml
stages:
# --- STAGE 1: CI (Build) ---
- stage: Build
  jobs:
  - job: Compile
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: DotNetCoreCLI@2
      displayName: 'Publish'
      inputs:
        command: 'publish'
        arguments: '-c Release -o $(Build.ArtifactStagingDirectory)'
        zipAfterPublish: true

    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop' # The Name of the artifact

# --- STAGE 2: CD (Deploy) ---
- stage: Deploy
  dependsOn: Build # Waits for Build to finish
  jobs:
  - deployment: DeployApp
    displayName: 'Deploy to IIS/Azure'
    environment: 'Production' # Requires setup in ADO > Pipelines > Environments
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          # Note: DownloadPipelineArtifact happens automatically here!

          # This deploys the ZIP to Azure App Service
          - task: AzureWebApp@1
            displayName: 'Deploy to App Service'
            inputs:
              azureSubscription: 'My-Azure-Connection' # Service Connection Name
              appType: 'webApp' # or 'webAppLinux'
              appName: 'my-production-site-name'
              package: '$(Pipeline.Workspace)/drop/**/*.zip' # Find zip in download folder

              # Configuration Substitution logic
              enableXmlVariableSubstitution: false
              jsonVariableSubstitution: true # Enable JSON replace

```

---

### **Summary of Phase 3**

1. **Service Connections:** Are the keys to the castle.
2. **Deployments:** Use `deployment` jobs with `environment` to get "Manual Approval" features (e.g., Email Manager before Prod).
3. **Paths:** The artifact lives at `$(Pipeline.Workspace)/{ArtifactName}`.
4. **Config:** Map pipeline variables to `appsettings.json` keys to swap connection strings automatically.

You are right. The specific mechanics of **Variable Substitution** and **Artifact Download** are often glossed over, but they are where deployment bugs usually happen.

Here is the detailed breakdown for an [**ASP.NET](http://asp.net/) Core Web API** deployed to an **Azure App Service**, focusing on *exactly* how the JSON gets updated and how to handle artifacts manually.

---

### **1. Explicit Artifact Download (`DownloadPipelineArtifact@2`)**

While "Deployment Jobs" download files automatically, standard jobs do not. Even in Deployment jobs, expert architects often disable the auto-download (`download: none`) to have full control over *which* artifact is downloaded to *where*.

### **The Syntax**

This task grabs the ZIP file created in the Build Stage.

```yaml
- task: DownloadPipelineArtifact@2
  displayName: 'Download Build Artifacts'
  inputs:
    buildType: 'current' # Download from the run that triggered this
    artifactName: 'drop' # MUST match the name used in PublishBuildArtifacts
    targetPath: '$(Pipeline.Workspace)' # Downloads to C:\\agent\\_work\\1\\

```

### **Visualizing the Result**

After this task runs, your agent's disk looks like this:

```
$(Pipeline.Workspace)/  <-- C:\\agent\\_work\\1\\
    └── drop/           <-- The folder name (ArtifactName)
          └── api.zip   <-- The file you published

```

**Critical Path usage:**
When you configure the App Service Deploy task later, you **must** refer to this path:
`package: '$(Pipeline.Workspace)/drop/**/*.zip'`

---

### **2. Variable Replacement (The "Magic" Link)**

This is how you change `localhost` to `production-db.com` without unzipping the file or writing PowerShell scripts.

### **Step A: Your `appsettings.json` (The Source)**

Imagine your [ASP.NET](http://asp.net/) Core Web API has this configuration file committed to Git.

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=DevDB;User Id=sa;Password=..."
  },
  "AuthSettings": {
    "Issuer": "<https://localhost:5000>",
    "Audience": "MyApi"
  }
}

```

### **Step B: The Pipeline Variables (The Values)**

In Azure DevOps, go to **Pipelines -> Library** (or the "Variables" button in the pipeline editor). You define variables using dot notation to match the JSON hierarchy.

| Name | Value | Secret? |
| --- | --- | --- |
| **ConnectionStrings.DefaultConnection** | `Server=prod-sql.azure.com;Database=ProdDB...` | 🔒 Yes |
| **AuthSettings.Issuer** | `https://my-prod-api.com` | No |

### **Step C: The Task Configuration**

You use the `AzureWebApp@1` task.

- **Trigger:** You must set `jsonVariableSubstitution: true`.
- **Behavior:** The task looks inside the `.zip` file. It finds `appsettings.json`. It looks for matching keys from your Pipeline Variables. If it finds a match (e.g., `AuthSettings.Issuer`), it replaces the value inside the JSON.

---

### **3. Putting it together: The "Expert" Deployment YAML**

Here is a complete Deployment Stage that uses a **Standard Job** (forcing us to use the manual Download task) and demonstrates the substitution.

```yaml
stages:
- stage: DeployProd
  displayName: 'Deploy to Production'
  dependsOn: Build
  jobs:
  - job: DeployJob
    pool:
      vmImage: 'ubuntu-latest'
    steps:

    # 1. EXPLICIT DOWNLOAD TASK
    - task: DownloadPipelineArtifact@2
      displayName: 'Download API Package'
      inputs:
        buildType: 'current'
        artifactName: 'drop'
        targetPath: '$(Pipeline.Workspace)'

    # 2. OPTIONAL: Debugging - Verify the file is there
    - script: ls -R $(Pipeline.Workspace)
      displayName: 'Verify Artifact Download'

    # 3. DEPLOY & SUBSTITUTE VARIABLES
    - task: AzureWebApp@1
      displayName: 'Deploy to Azure App Service'
      inputs:
        azureSubscription: 'My-Azure-Service-Connection'
        appType: 'webAppLinux' # Use 'webApp' for Windows
        appName: 'my-production-api-001' # Name of App Service in Azure Portal

        # Path to the zip file we just downloaded
        package: '$(Pipeline.Workspace)/drop/**/*.zip'

        # -------------------------------------------------------
        # VARIABLE SUBSTITUTION MAGIC
        # -------------------------------------------------------
        # 1. Finds 'appsettings.json' inside the zip
        # 2. Looks for Pipeline Variable 'ConnectionStrings.DefaultConnection'
        # 3. Updates the JSON value securely
        jsonVariableSubstitution: true

```

---

### **4. Alternative: The Standalone `FileTransform` Task**

Sometimes you need to change variables *without* deploying (maybe you are creating a zip to send to a third party). You can use the `FileTransform` task separately.

```yaml
- task: FileTransform@1
  displayName: 'Update appsettings.json'
  inputs:
    folderPath: '$(Pipeline.Workspace)/drop' # Unzipped folder
    fileType: 'json'
    targetFiles: '**/appsettings.json'

```

*Note: This requires the artifact to be UNZIPPED. The `AzureWebApp` task is smarter—it can modify the JSON **inside** the Zip file on the fly.*

### **Summary of Mechanics**

1. **Hierarchy:** Use dots (`.`) in your Pipeline Variable names to navigate nested JSON objects (`Parent.Child.Property`).
2. **Case Sensitivity:** JSON replacement is case-sensitive! `connectionstrings.defaultconnection` variable will **not** replace `ConnectionStrings.DefaultConnection` in the file.
3. **Secrets:** If you mark a variable as a Secret (Lock icon), the value is masked in logs (`**`), but the `AzureWebApp` task can still read it and inject it into the `appsettings.json` correctly.

Are you clear on the **Dot Notation** and the **Explicit Download** now? Shall we move to **Phase 4: Advanced Logic & Templating** (Reusable Code)?

# Inject Variable using script

Yes. While the `AzureWebApp@1` task has the convenient `appSettings` input, using a script provides far more power. It allows you to **calculate** values dynamically (e.g., generating a "ReleasedAt" timestamp) and then push them to Azure.

The best tool for this is the **`AzureCLI@2` task**.

### **The "Script Injection" Pattern**

The standard deployment flow becomes:

1. **Run Azure CLI Script:** Calculate values -> `az webapp config appsettings set`
2. **Run Deployment:** Push the code.

---

### **Step-by-Step Example**

Imagine you want to inject two dynamic variables:

1. **`ReleasedAt`:** The current timestamp (calculated via script).
2. **`Deployer`:** The name of the person who clicked the button (`$(Build.RequestedFor)`).

### **The YAML**

```yaml
stages:
- stage: Deploy
  jobs:
  - job: DeployJob
    pool: { vmImage: 'ubuntu-latest' }
    steps:

    # ---------------------------------------------------------
    # STEP 1: Scripted Environment Injection
    # ---------------------------------------------------------
    - task: AzureCLI@2
      displayName: 'Inject Dynamic Env Vars'
      inputs:
        azureSubscription: 'My-Azure-Service-Connection'
        scriptType: 'bash' # or 'pscore' for PowerShell
        scriptLocation: 'inlineScript'
        inlineScript: |
          # 1. Calculate dynamic values (Bash)
          TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
          USER="$(Build.RequestedFor)"

          echo "Injecting Release Time: $TIMESTAMP"

          # 2. Use Azure CLI to push them to the App Service
          # The command is: az webapp config appsettings set
          az webapp config appsettings set \\
            --resource-group "MyResourceGroup" \\
            --name "my-production-api" \\
            --settings ReleasedAt="$TIMESTAMP" Deployer="$USER" CustomLogic="CalculatedInBash"

    # ---------------------------------------------------------
    # STEP 2: Deploy Code
    # ---------------------------------------------------------
    - task: AzureWebApp@1
      displayName: 'Deploy Code'
      inputs:
        azureSubscription: 'My-Azure-Service-Connection'
        appType: 'webAppLinux'
        appName: 'my-production-api'
        package: '$(Pipeline.Workspace)/drop/**/*.zip'
        # No need for 'appSettings' input here since we did it above

```

### **Why use a script instead of the built-in Task Input?**

| Feature | `AzureWebApp@1` Input | `AzureCLI@2` Script |
| --- | --- | --- |
| **Simplicity** | High (Just a list) | Low (Needs CLI commands) |
| **Logic** | None (Static values only) | **Full Logic** (If/Else, Math, API calls) |
| **Key Vault** | Limited to pipeline variables | Can fetch secrets dynamically |
| **Timing** | Happens *during* deploy | Can happen *before* or *after* |
| **Restart** | Triggers an App Restart | Triggers an App Restart |

**Important Warning on Restarts:**
Every time you update `appsettings`, the Azure App Service **restarts**.
If you run the CLI script (Step 1) and then the Deploy task (Step 2), you might trigger **two restarts** back-to-back.

- *Optimization:* If possible, do the CLI step *after* the deployment (if the startup doesn't crash without them), or accept the double-restart as the cost of flexibility.

### Yaml [ Multi stage build ] vs Realease Pipeline

This is one of the **most confusing** parts of the Azure DevOps interface for beginners, so do not feel bad asking this.

The short answer is: **It depends on which "Generation" of Azure DevOps you use.**

1. **The Modern Way (Multi-Stage YAML):** **YES**, one single YAML file handles **Both** Build and Release. They are not separate.
2. **The Classic Way (Legacy):** **NO**, they are totally separate. You use YAML for Build, but a "GUI Visual Designer" (The Releases Tab) for deployment.

Here is the breakdown of why this confusion exists and how they differ.

---

### **1. The "Releases" Tab (Classic / Legacy)**

If you look at the left sidebar in Azure DevOps, you see **Pipelines** and **Releases**.

- **The Workflow:**
    1. **Pipelines (Build):** You write a YAML file that just compiles code and creates a Zip (`azure-pipelines.yml`). It ends with `PublishBuildArtifacts`.
    2. **Releases (Deploy):** You click the "Releases" tab. This **Does NOT use YAML**.
    3. **The UI:** You use a Drag-and-Drop editor to say "Take the artifact from the Build Pipeline and push it to Dev."
- **Why it's bad (for Experts):**
    - The deployment logic is **NOT in Git**.
    - If you change a database password or a script in the Release UI, there is no "Git Commit History" to track *who* did it or *why*.
    - If you clone your repo to a new project, you lose the deployment logic because it's locked inside the Azure DevOps database, not your files.

---

### **2. Multi-Stage Pipelines (The Expert Standard)**

This is what we covered in Phase 3. **Everything** lives in the "Pipelines" tab. We ignore the "Releases" tab entirely.

- **The Workflow:**
You have **ONE** `azure-pipelines.yml` file. It has logical sections.
    
    ```yaml
    stages:
    # 1. CI Part (The "Build")
    - stage: Build
      jobs:
      - job: CompileCode
        steps:
        - task: DotNetCoreCLI@2 (Publish)
        - task: PublishBuildArtifacts@1
    
    # 2. CD Part (The "Release")
    - stage: DeployDev
      jobs:
      - deployment: DeployToAzure
        environment: 'Development' # Creates the "Gate"
        strategy:
          runOnce:
            deploy:
              steps:
              - task: AzureWebApp@1
    
    ```
    
- **How do approvals work?**
In the Classic UI, you clicked a circle to add an "Approval".
In YAML, you go to **Pipelines -> Environments**, click "Development", and add a "Check/Approval".
When the YAML pipeline tries to run the `DeployDev` stage, it pauses and waits for you to say "Yes" in the UI.

---

### **Comparison Summary**

| Feature | **Classic (Releases Tab)** | **Multi-Stage YAML (Pipelines Tab)** |
| --- | --- | --- |
| **Location** | Separate "Releases" Tab | Same "Pipelines" Tab |
| **Definition** | Visual Editor (GUI) | YAML Text File |
| **Versioning** | Stored in ADO DB (No Git) | Stored in Git (Version Controlled) |
| **Artifacts** | Explicit linking required | Automatic (Download Pipeline Artifact) |
| **Best For** | Beginners / Non-Technical PMs | Developers / DevOps Engineers |

### **The "Hybrid" Trap (Common Mistake)**

Many companies are in a transition period. You will often see:

- The Build is YAML.
- The Release is Classic UI.

**Why?** Because 5 years ago, YAML Release pipelines didn't exist.
**Expert Advice:** If you are building a *new* project, **use Multi-Stage YAML (One file for everything)**. It makes specific versions of your code tightly coupled to the logic required to deploy them.

### **Final Verdict for your Learning Path**

In our Roadmap (Phase 3), we are strictly learning **Multi-Stage YAML**. We treat the "Releases" tab as deprecated (even though Microsoft hasn't officially killed it yet).

Does that clear up the confusion? Are you ready to move to **Phase 5: Security & Secrets**?