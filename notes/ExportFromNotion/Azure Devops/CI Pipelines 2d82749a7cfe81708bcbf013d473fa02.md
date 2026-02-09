# CI / Pipelines

![image.png](CI%20Pipelines/image.png)

## **Phase 0: Internal Architecture & Workspace (The Physical Reality)**

Most pipeline failures (errors like "File Not Found", "Path too long", or "Directory does not exist") happen because the developer assumes the pipeline knows where their files are. It does not.

To be an expert, you must visualize the **Hard Drive** of the build agent.

---

### **1. The Agent's Work Folder (`_work`)**

Whether you use a Microsoft-Hosted agent (a fresh VM every time) or a Self-Hosted agent (a persistent server), the logic is the same. The agent creates a working directory, usually named `_work`.

Inside `_work`, it creates a folder number (e.g., `1`, `2`, `3`) for each unique pipeline to prevent file collisions.

**The structure looks like this:**

```
C:\\agent\\_work\\1\\    <-- The Root (Pipeline Workspace)
    │
    ├── s\\           <-- Source Directory
    │   └── MyWebApp\\
    │       ├── MyWebApp.sln
    │       └── appsettings.json
    │
    ├── a\\           <-- Artifact Staging Directory
    │   └── (Empty start, usually zip files go here)
    │
    └── b\\           <-- Binaries (Rarely used in .NET Core)

```

---

### **2. The Critical Directories (Memorize These)**

You will use these Predefined Variables in your YAML constanty.

### **A. The Source Folder: `s`**

- **Variable:** `$(Build.SourcesDirectory)`
- **What is it?** This is your Git Repository.
- **Behavior:** When the pipeline starts, the `checkout` step runs `git clone` (or `git fetch`) and dumps your code here.
- **Usage:** Your `dotnet restore` and `dotnet build` commands run against files inside this folder.

### **B. The Artifact Staging Folder: `a`**

- **Variable:** `$(Build.ArtifactStagingDirectory)`
- **What is it?** Think of this as the **Shipping Dock**. It starts empty.
- **Behavior:** This folder is *not* for compiling code. It is for preparing files to be uploaded to Azure DevOps.
- **Usage:** You command `dotnet publish` to output the final ZIP files here. Then, you tell Azure DevOps to "upload whatever is in folder `a`".

### **C. The Root Workspace**

- **Variable:** `$(Pipeline.Workspace)`
- **What is it?** The parent folder containing `s` and `a`.
- **Usage:** Crucial for **Release Pipelines**. When you download artifacts from a previous build, they often land in this root folder, not inside `s`.

---

### **3. The Data Flow (The "Conveyor Belt")**

This is the most common confusion for beginners. Files do not move themselves. You must move them.

Here is the lifecycle of a .NET Web API release:

1. **Checkout:**
    - Agent downloads git repo into `$(Build.SourcesDirectory)` (folder `s`).
2. **Build:**
    - You run `dotnet build`.
    - The compiled DLLs appear in `s\\MyProject\\bin\\Debug\\net8.0\\`.
    - *Note:* The Staging folder (`a`) is still **empty**.
3. **Publish (Compile & Zip):**
    - You run `dotnet publish --output $(Build.ArtifactStagingDirectory)`.
    - The Agent takes the code from `s`, compiles it, optimizes it, and puts the result (e.g., `api.zip` or the raw DLLs) into `a`.
4. **Upload (PublishArtifact):**
    - You use the YAML task `PublishBuildArtifacts`.
    - You point it to `$(Build.ArtifactStagingDirectory)`.
    - The Agent uploads the zip from `a` to the **Azure DevOps Cloud**.
5. **Clean Up:**
    - The job finishes. If it's a Microsoft-hosted agent, the VM is destroyed.

---

### **4. The `checkout` Step (The Hidden First Step)**

Every YAML pipeline has an invisible first step. Even if you don't write it, Azure executes:

```yaml
steps:
- checkout: self

```

### **How it works:**

1. **Sync:** It checks if `folder s` exists.
2. **Fetch:** It pulls the commit that triggered the build.

### **The "Clean" Option (Important for Self-Hosted):**

On a Self-Hosted agent, the files stay there forever. If you deleted a file in Git, it might still exist physically on the Agent's disk from a previous run, potentially breaking your build.

To force a fresh start:

```yaml
steps:
- checkout: self
  clean: true  # This deletes 's', 'a', and 'b' before cloning. Slower, but safer.

```

---

### **5. Practical Exercise: Visualize It**

The best way to learn is to see it. Create a new "Starter Pipeline" in Azure DevOps and paste this code. It works on both Windows and Linux agents.

```yaml
trigger: none

pool:
  vmImage: 'ubuntu-latest' # Or 'windows-latest'

steps:
# 1. Show the mapping of Variables to Real Paths
- script: |
    echo "------------------------------------------------"
    echo "Root Workspace: $(Pipeline.Workspace)"
    echo "Source Code (s): $(Build.SourcesDirectory)"
    echo "Artifact Staging (a): $(Build.ArtifactStagingDirectory)"
    echo "------------------------------------------------"
  displayName: 'Display Directory Variables'

# 2. Show that 's' contains your Git files
- script: |
    echo "listing contents of Source Directory..."
    ls -R $(Build.SourcesDirectory)
  displayName: 'List Source Files'

# 3. Prove that 'a' starts empty
- script: |
    echo "listing contents of Artifact Staging..."
    ls -R $(Build.ArtifactStagingDirectory)
  displayName: 'List Artifact Staging (Empty)'

```

---

### **Summary of Phase 0**

1. Code starts in **`s`** (`$(Build.SourcesDirectory)`).
2. You compile code and send output to **`a`** (`$(Build.ArtifactStagingDirectory)`).
3. The task `PublishBuildArtifacts` uploads **`a`** to the cloud.
4. Never hardcode paths like `C:\\agent`. Always use the `$(Variables)`.

Are you ready to move to **Phase 1: The Core Concepts** (YAML Hierarchy, Pools, and Triggers)?

## Custom Tool Installation in Build Agent

This is a crucial practical question. Managing tool dependencies is the difference between a "flaky" pipeline and a robust one.

Here is the deep dive on installing custom tools (`dotnet ef`, `reportgenerator`, `sonarscanner`, etc.).

---

### **1. The Two Types of Agents (Behavior Recap)**

To understand tool installation, you must remember the hardware reality:

| Agent Type | State | Behavior regarding Tools |
| --- | --- | --- |
| **Microsoft-Hosted** | **Ephemeral (Fresh VM)** | The VM is destroyed after the build. **You must install the tool every single time.** Nothing is saved. |
| **Self-Hosted** | **Persistent (Permanent Server)** | The files stay on the disk. If you install a global tool once, **it stays there forever** (or until you uninstall it). |

---

### **Method A: The "Local Tool" Manifest (Recommended)**

*Best for: `dotnet-ef`, `dotnet-reportgenerator`, `gitversion`*

This is the modern, "clean" way to handle tools in .NET Core. You don't install the tool on the *machine* (globally); you install it for the *repository* (locally).

### **How it works:**

1. **Locally (on your dev machine):** You run this command in your project root:
    
    ```bash
    dotnet new tool-manifest
    dotnet tool install dotnet-reportgenerator-globaltool
    
    ```
    
    This creates a file `.config/dotnet-tools.json` which you push to Git. This file "locks" the exact version of the tool you need.
    
2. **In the Pipeline (YAML):**
You simply tell the agent "Read the json file and download these tools."

### **The YAML:**

```yaml
steps:
- task: PowerShell@2
  displayName: 'Restore .NET Local Tools'
  inputs:
    targetType: 'inline'
    script: |
      # This command reads .config/dotnet-tools.json and installs the tools to a local folder
      dotnet tool restore

```

### **Why is this the Best?**

- **Microsoft-Hosted:** It runs fast. It downloads the specific version you need for this build.
- **Self-Hosted:** It is safe. It doesn't pollute the global machine. If Project A needs v1.0 and Project B needs v2.0, they won't conflict because the tools are scoped to the `_work` folder.

---

### **Method B: Global Tools (The "Check First" Strategy)**

*Best for: Tools that don't support local manifests or legacy setups.*

If you *must* install a tool globally (`--global`), you have to handle the difference between Microsoft-Hosted and Self-Hosted agents to avoid errors.

### **Microsoft-Hosted (The Simple Way)**

Since the VM is fresh, just install it.

```yaml
- script: dotnet tool install --global dotnet-ef
  displayName: 'Install EF Core (Cloud)'
  condition: eq(variables['Agent.JobName'], 'Azure Pipelines') # Only run on cloud

```

### **Self-Hosted (The Safe Way)**

If you run `dotnet tool install -g dotnet-ef` on a self-hosted agent that *already* has it, the build will **Fail** with: *"Tool 'dotnet-ef' is already installed."*

You need an **Idempotent Script** (Check if exists, if not, install).

**The Universal YAML (Works on Both):**

```yaml
steps:
- task: PowerShell@2
  displayName: 'Install Global Tool Safely'
  inputs:
    targetType: 'inline'
    script: |
      # 1. Define the tool name
      $toolName = "dotnet-reportgenerator-globaltool"

      # 2. Check if it is already installed
      $installed = dotnet tool list -g | Select-String $toolName

      if ($installed) {
          Write-Host "Tool $toolName is already installed. Skipping."
      }
      else {
          Write-Host "Installing $toolName..."
          dotnet tool install --global $toolName
      }

```

---

### **Method C: OS Level Tools (apt-get / choco)**

*Best for: Non-.NET utilities (e.g., a specific version of NodeJS, FFmpeg, Curl).*

Sometimes you need a binary that isn't a .NET tool.

### **On Linux (Ubuntu Agents):**

You use `apt-get`.

- **Microsoft-Hosted:** You verify it isn't already there (Microsoft pre-installs a LOT of stuff), then install.
- **Self-Hosted:** Be very careful. You need `sudo` (admin) rights. It's usually better to have your sysadmin install these once manually rather than doing it inside the pipeline.

**Example (Installing a JSON parser called `jq` on Linux):**

```yaml
steps:
- script: |
    # Update package list and install jq
    sudo apt-get update
    sudo apt-get install -y jq
  displayName: 'Install JQ (Linux)'

```

### **On Windows Agents:**

You use **Chocolatey** (`choco`), which is pre-installed on Microsoft agents.

**Example (Installing a file utility):**

```yaml
steps:
- script: |
    choco install jq -y
  displayName: 'Install JQ (Windows)'

```

---

### **Summary: The "Expert" Workflow**

1. **Prefer Method A (Local Manifest):** Always use `.config/dotnet-tools.json` and `dotnet tool restore`. It handles versioning and isolation automatically. It works perfectly on both agent types without custom "check if exists" scripts.
2. **Avoid Method B (Global)** on Self-Hosted agents unless absolutely necessary. It leads to version conflicts between different pipelines sharing the same server.
3. **For Method C (OS Tools):** Check the [**Microsoft Hosted Agent Image Software List**](https://github.com/actions/runner-images) first! 90% of the time, the tool you want (Node, Java, Python, Azure CLI) is already installed, and you don't need to do anything.

Are you clear on the Tooling strategy? Ready to move to **Phase 2: CI - Building Your Code** (Where we actually compile the application)?

## **Phase 2: CI - Building Your Code (Continuous Integration)**

Phase 0 and 1 were setup. This is the **Meat**. This is where we turn C# text files into deployable binaries (`.zip` or `.dll`).

For a .NET Core developer, this phase relies heavily on one major task: `DotNetCoreCLI@2`. However, knowing *how* to use it distinguishes a novice from an expert.

---

### **1. Setting the Stage: `UseDotNet@2`**

Before you build, you must define the rules. Microsoft-Hosted agents come with *many* SDKs installed, but they change often. If your app works on .NET 6 today, and Microsoft updates the "Default" to .NET 8 tomorrow, your build might break or produce compatible binaries.

**The Expert Move:** Lock the version using `UseDotNet@2` or `global.json`.

```yaml
steps:
- task: UseDotNet@2
  displayName: 'Install .NET Core SDK'
  inputs:
    packageType: 'sdk'
    version: '8.x' # Use 8.0.x latest. Or be specific '8.0.101'
    includePreviewVersions: false

```

*Why?* This ensures your build environment is deterministic. It downloads the exact SDK version into the agent's cache if it's missing.

---

### **2. The Workhorse: `DotNetCoreCLI@2`**

While you *can* write scripts like `dotnet build`, the official `DotNetCoreCLI@2` task provides massive benefits:

1. **Auth Injection:** It automatically authenticates against Azure Artifacts (Private NuGet Feeds).
2. **Path Handling:** It handles wildcards (`*/*.csproj`) easily.

A standard CI Pipeline consists of 4 discrete commands, usually run sequentially.

### **Step A: Restore**

Downloads NuGet packages.

- **Novice:** Skips this and relies on Build to restore.
- **Expert:** Explicitly runs restore so they can inject custom NuGet Feed credentials.

```yaml
- task: DotNetCoreCLI@2
  displayName: 'Restore NuGet Packages'
  inputs:
    command: 'restore'
    projects: '**/*.csproj' # or specific .sln
    feedsToUse: 'select' # Uses default public NuGet.org
    # vstsFeed: 'MyPrivateFeed' # <--- This is why we use the Task! Easy Auth.

```

### **Step B: Build**

Compiles the code.

- **Expert Tip:** Use `-no-restore` to save time (since we just restored in Step A).

```yaml
- task: DotNetCoreCLI@2
  displayName: 'Build Project'
  inputs:
    command: 'build'
    projects: '**/*.csproj'
    arguments: '--configuration Release --no-restore'

```

### **Step C: Test (Optional but Critical)**

Runs your Unit Tests (`NUnit`, `xUnit`).

- **Expert Tip:** This task automatically publishes the test results (Pass/Fail) to the Azure DevOps "Tests" tab. You don't need a separate "Publish Test Results" task if you use this.

```yaml
- task: DotNetCoreCLI@2
  displayName: 'Run Unit Tests'
  inputs:
    command: 'test'
    projects: '**/*Tests.csproj' # Only target Test projects
    arguments: '--configuration Release --no-build --collect "Code coverage"'

```

- `-no-build`: Saves time, we just built in Step B.
- `-collect "Code coverage"`: Enables coverage XML generation.

### **Step D: Publish**

Packs the compiled code into a format ready for hosting (e.g., a `.zip` file for Web Apps).

```yaml
- task: DotNetCoreCLI@2
  displayName: 'Publish to Staging'
  inputs:
    command: 'publish'
    publishWebProjects: true # Helpful shortcut for ASP.NET Core
    arguments: '--configuration Release --output $(Build.ArtifactStagingDirectory)'
    zipAfterPublish: true # Zips the folder. Azure App Service prefers ZIPs.

```

- **Critical Observation:** Notice where we send the output? `$(Build.ArtifactStagingDirectory)`. This is **Folder `a`** from Phase 0!

---

### **3. The Handoff: `PublishBuildArtifacts`**

At the end of Step D, your Agent has a zip file in `_work/1/a/api.zip`.
But... **if the build finishes now, that file is deleted.** The Agent is wiped.

You must move the file from the Agent to the Azure Cloud (Server) so your Release Pipeline can find it later.

```yaml
- task: PublishBuildArtifacts@1
  displayName: 'Upload Artifacts'
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)'
    ArtifactName: 'drop' # The classic name for the final package
    publishLocation: 'Container' # 'Container' means Azure DevOps Cloud Storage

```

---

### **4. .sln vs .csproj (The Scope)**

- **Question:** Should I point `projects` to the Solution (`.sln`) or the Project (`.csproj`)?
- **Answer:**
    - **For Restore/Build:** Point to the **Solution (`.sln`)**. This ensures Project References (A referencing B) are resolved correctly.
    - **For Publish:** Point to the **specific WebAPI Project (`.csproj`)**. If you publish a `.sln`, it might try to "Publish" your Unit Test library, which makes no sense and wastes time/space.

---

### **Summary of Phase 2 (The Perfect Build YAML)**

If you combine this with Phase 1, you have a production-grade build pipeline.

```yaml
stages:
- stage: Build
  jobs:
  - job: Compile
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    # 1. SDK
    - task: UseDotNet@2
      inputs: { version: '8.x' }

    # 2. Restore (with private feed support if needed)
    - task: DotNetCoreCLI@2
      inputs:
        command: 'restore'
        projects: '**/*.sln'

    # 3. Build (Release mode)
    - task: DotNetCoreCLI@2
      inputs:
        command: 'build'
        projects: '**/*.sln'
        arguments: '--configuration Release --no-restore'

    # 4. Test (Run Tests)
    - task: DotNetCoreCLI@2
      inputs:
        command: 'test'
        projects: '**/*Tests.csproj'
        arguments: '--configuration Release --no-build'

    # 5. Publish (Create the Zip in Folder 'a')
    - task: DotNetCoreCLI@2
      inputs:
        command: 'publish'
        publishWebProjects: false # Set false to target specific csproj manually
        projects: '**/MyWebApi.csproj'
        arguments: '--configuration Release --output $(Build.ArtifactStagingDirectory) --no-build'

    # 6. Upload (Send 'a' to Cloud)
    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'

```

That's a very precise and important question about the execution flow.

**Jobs inside a stage run in parallel.**

Let's break it down with a clear example and explanation.

### **The Hierarchy of Execution**

Think of the YAML structure as a set of nested containers that define execution logic:

1. **Pipeline:** The top-level container for the entire process.
2. **Stages:** A collection of stages. **Stages run sequentially, one after another, by default.**
3. **Jobs:** A collection of jobs within a stage. **Jobs run in parallel, on different agents, by default.**
4. **Steps:** A list of tasks within a job. **Steps run sequentially, one after another, on the same agent.**

### **Visualizing the Execution Flow**

Consider this common YAML structure:

```yaml
stages:
- stage: A  # Stage A starts first
  jobs:
  - job: A1
    steps:
    - script: echo "Job A1, Step 1"
    - script: echo "Job A1, Step 2"
  - job: A2
    steps:
    - script: echo "Job A2, Step 1"
    - script: echo "Job A2, Step 2"

- stage: B  # Stage B can ONLY start after ALL jobs in Stage A are complete
  dependsOn: A
  jobs:
  - job: B1
    steps:
    - script: echo "Job B1"

```

Here is how Azure DevOps will execute this:

1. **Start Pipeline:**
2. **Start Stage A:**
    - It sees two jobs, `A1` and `A2`, that do not depend on each other.
    - It requests **two separate build agents** from the agent pool.
    - **Agent 1** is assigned **Job A1**. It starts running "Job A1, Step 1", then "Job A1, Step 2".
    - **Agent 2** is assigned **Job A2**. It starts running "Job A2, Step 1", then "Job A2, Step 2" **at the same time as Agent 1**.
    - Stage A is considered "complete" only when **both `A1` and `A2` have finished**.
3. **Start Stage B:**
    - The `dependsOn: A` condition is now met.
    - It requests **one build agent**.
    - The agent is assigned **Job B1** and runs its steps.
4. **End Pipeline.**

### **How to Force Sequential Jobs**

If you need jobs *within the same stage* to run one after another, you must explicitly define their dependencies using `dependsOn`.

```yaml
stages:
- stage: A
  jobs:
  - job: A1 # This job runs first
    steps:
    - script: echo "Job A1"

  - job: A2 # This job WAITS for A1 to finish
    dependsOn: A1
    steps:
    - script: echo "Job A2"

```

In this case, only one agent will be used at a time for Stage A. Job `A2` will not start until `A1` is complete.

### **Final Answer**

To be perfectly clear:

- **Stages run sequentially** (unless you define complex `dependsOn` logic to make them parallel, which is an advanced use case).
- **Jobs (within a stage) run in parallel** (unless you use `dependsOn` to make them sequential).
- **Steps (within a job) always run sequentially.**

So, the parallelism happens at the **Job** level.