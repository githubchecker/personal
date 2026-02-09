# Phase 6: Infrastructure & Performance

In a professional environment, a pipeline that takes 15 minutes to run is a failure. It slows down development and frustrates teams. **Experts focus on speed, stability, and scale.**

This phase is about optimizing the build and managing the engines (Agents) that run them.

---

### **1. Pipeline Caching (Speed Up Builds)**

The slowest part of a .NET build is usually `dotnet restore`. It downloads hundreds of megabytes of NuGet packages.

**The Problem:** On Microsoft-hosted agents, every build starts with a blank slate. You download the same packages 100 times a day.
**The Solution:** The `Cache@2` task.

```yaml
variables:
  # Define where NuGet packages are stored on this OS
  NUGET_PACKAGES: $(Pipeline.Workspace)/.nuget/packages

steps:
- task: Cache@2
  displayName: 'Cache NuGet Packages'
  inputs:
    # 'key' is a fingerprint. If the file changes, the cache is busted.
    key: 'nuget | "$(Agent.OS)" | **/packages.lock.json'
    # Or use: key: 'nuget | "$(Agent.OS)" | **/*.csproj'
    restoreKeys: |
       nuget | "$(Agent.OS)"
    path: $(NUGET_PACKAGES)
    cacheHitVar: 'CACHE_RESTORED'

- task: DotNetCoreCLI@2
  displayName: 'Restore'
  condition: ne(variables.CACHE_RESTORED, 'true')
  inputs:
    command: 'restore'

```

- **Result:** The second time this pipeline runs, it downloads the zip from Azure cache (very fast) instead of [NuGet.org](http://nuget.org/) (slow). This can save 2–5 minutes per build.

---

### **2. Self-Hosted Agents (Scale and Networking)**

You use a Self-Hosted agent when:

1. **Networking:** You need to deploy to a server behind a private firewall.
2. **Resources:** You need 32GB of RAM or 16 CPUs for massive compilations.
3. **Persistence:** You want to keep large files on disk between builds.

### **Expert Strategy: VM Scale Set (VMSS) Agents**

Managing 10 permanent VMs is a nightmare. Azure DevOps allows you to link an **Azure VM Scale Set** to a Pool.

- **Demand Spike:** 10 people push code. Azure DevOps tells Azure "Spin up 10 VMs."
- **Cooldown:** No builds are running. Azure DevOps deletes the VMs to save you money.

---

### **3. Infrastructure as Code (IaC) in the Pipeline**

Expert developers don't click around the Azure Portal to create the Web App. They use the pipeline to create the infrastructure *before* the code lands.

### **Example: Running Bicep/Terraform**

```yaml
- stage: Provision
  jobs:
  - job: Infrastructure
    steps:
    - task: AzureResourceManagerTemplateDeployment@3
      inputs:
        deploymentScope: 'Resource Group'
        azureResourceManagerConnection: 'MyConnection'
        action: 'Create Or Update Resource Group'
        resourceGroupName: 'my-prod-rg'
        location: 'East US'
        templateLocation: 'Linked artifact'
        csmFile: '$(Build.SourcesDirectory)/infra/main.bicep'
        overrideParameters: '-appName "my-app-prod"'

```

- **Why?** If you need a QA environment tomorrow, you just update a parameter. The infrastructure is version-controlled exactly like the C# code.

---

### **4. Parallelism and "MaxParallel"**

If you have a massive test suite (2,000+ tests), don't run them one by one.

```yaml
jobs:
- job: Test
  strategy:
    # Run the same job on 3 different agents at the same time
    parallel: 3
  steps:
  - script: dotnet test --filter "Priority=High" # Or use slicing logic

```

---

## **Phase 7: Expert / Architect (The Final Frontier)**

This is where you move beyond YAML and start extending Azure DevOps itself.

### **1. The Azure DevOps REST API**

Sometimes, YAML cannot do what you want. You might need to:

- Trigger Pipeline B after Pipeline A finishes only if a specific variable is set.
- Automatically create a "Release Note" in a Wiki after a deploy.

**Expert Skill:** Use `HttpClient` in C# or PowerShell to call:
`PATCH <https://dev.azure.com/{org}/{project}/_apis/build/builds/{buildId}`>

### **2. Custom Tasks**

Tired of copy-pasting a complex PowerShell script into every YAML? You can build your own **Task Extension**.

1. Write a `task.json` (defines inputs like a UI).
2. Write the logic in **TypeScript** or **PowerShell**.
3. Pack it as a `.vsix` and install it in your Organization.
4. Usage in YAML: `task: MyCoolCustomTask@1`.

### **3. Pipeline Decorators**

This is the "Enterprise Architect" level.
**Scenario:** Corporate policy says *every* build in the company (500 projects) must run a virus scan.
**The "Decorator" Solution:** You write a Decorator. It **force-injects** a step at the beginning or end of every pipeline in the organization. Developers cannot see it in their YAML, but it runs every time.

---

### **The "Expert" Summary: Your Professional Workflow**

To become a top-tier Azure DevOps Engineer:

1. **Templatize everything:** Use a Governance repo for standardized `dotnet` templates.
2. **No Secrets in Git:** Use Key Vault linked to Variable Groups.
3. **IaC is Mandatory:** Use Bicep/Terraform stages.
4. **Optimize for Feedback:** Use Caching and Parallel jobs so devs get "Pass/Fail" in < 5 mins.
5. **Multi-Stage YAML Only:** Forget the "Releases" tab exists.

---

### **Final Q&A**

**Q:** Should I use Windows or Linux agents for .NET Core?
**A:** **Linux.** It starts up faster, it's cheaper per minute, and .NET Core runs natively on it. Use `ubuntu-latest`.

**Q:** How do I handle "Version Increments"?
**A:** Use **GitVersion** in Phase 1.5. It reads your Git Tags and automatically sets the Build Number to `1.2.3`.

**Congratulations!** You have the complete roadmap and the technical foundation. Your next step is to **build it**. Create a free Azure DevOps account, a free Azure App Service, and try to make the "Source-to-Cloud" trip yourself!

**Do you have any specific final doubts before concluding this masterclass?**