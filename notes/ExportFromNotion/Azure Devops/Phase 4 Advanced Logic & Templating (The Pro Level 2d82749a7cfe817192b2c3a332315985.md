# Phase 4: Advanced Logic & Templating (The "Pro" Level)

## **Phase 4: Advanced Logic & Templating (The "Pro" Level)**

Up to this point, your pipeline file (`azure-pipelines.yml`) probably looks like a long, messy scroll of code. If you have 10 Microservices, you are likely copy-pasting that file 10 times.

**This is the Novice trap.**

In this phase, we treat YAML like C#. We refactor code into **Templates** (Functions) and use **Parameters** (Arguments) to make them reusable.

---

### **1. Templates: The "DLLs" of YAML**

There are two main ways to include templates.

### **A. Step Templates (Snippets)**

Used to group a sequence of steps (e.g., "Build, Test, and Publish").

**The Template File (`templates/build-steps.yml`):**

```yaml
parameters:
- name: buildConfiguration
  type: string
  default: 'Release'
- name: projectPath
  type: string
  default: '**/*.csproj'

steps:
- task: DotNetCoreCLI@2
  displayName: 'Build'
  inputs:
    command: 'build'
    projects: ${{ parameters.projectPath }}
    arguments: '--configuration ${{ parameters.buildConfiguration }}'

- task: DotNetCoreCLI@2
  displayName: 'Test'
  inputs:
    command: 'test'
    projects: '**/*Tests.csproj'

```

**The Main Pipeline (`azure-pipelines.yml`):**

```yaml
steps:
- script: echo "Starting Build..."

# Reusing the logic!
- template: templates/build-steps.yml
  parameters:
    buildConfiguration: 'Debug'
    projectPath: 'MyApi/MyApi.csproj'

```

### **B. Job/Stage Templates (Workflows)**

Used to define an entire standard process (e.g., "Deploy to any Environment").

**The Template File (`templates/deploy-job.yml`):**

```yaml
parameters:
- name: envName
  type: string

jobs:
- deployment: DeployWeb
  environment: ${{ parameters.envName }}
  strategy:
    runOnce:
      deploy:
        steps:
        - task: AzureWebApp@1
          # ... deployment logic using ${{ parameters.envName }}

```

**The Main Pipeline:**

```yaml
stages:
- stage: Dev
  jobs:
  - template: templates/deploy-job.yml
    parameters:
      envName: 'Development'

- stage: Prod
  jobs:
  - template: templates/deploy-job.yml
    parameters:
      envName: 'Production'

```

---

### **2. Conditions (If / Else Logic)**

By default, a step only runs if the previous one succeeded. You can change this using the `condition` property.

### **A. The "Rollback" or "On Failure" Check**

Run a cleanup script only if the deployment crashes.

```yaml
- task: AzureWebApp@1
  displayName: 'Deploy'

- script: echo "Running Rollback Scripts..."
  displayName: 'Rollback'
  condition: failed() # Runs only if the previous step failed

```

### **B. Branch Logic (Prod vs Dev)**

Only run specific steps if you are on the `main` branch.

```yaml
- task: PublishBuildArtifacts@1
  displayName: 'Upload Artifacts'
  # Condition: Succeeded AND is 'main' branch
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))

```

### **C. Custom Variable Logic**

Using `${{ }}` syntax for compile-time generation vs `condition` for runtime.

```yaml
- script: echo "This is a feature branch build"
  condition: contains(variables['Build.SourceBranch'], 'feature/')

```

---

### **3. The Matrix Strategy (Parallelism)**

Imagine you need to test your library on `.NET 6`, `.NET 8`, Windows, and Linux. That is 4 combinations. Do not write 4 jobs. Use a **Matrix**.

Azure DevOps will automatically spawn **4 separate agents** running in parallel.

```yaml
jobs:
- job: TestLib
  strategy:
    maxParallel: 4
    matrix:
      Win_Net6:
        imageName: 'windows-latest'
        dotnetVersion: '6.x'
      Win_Net8:
        imageName: 'windows-latest'
        dotnetVersion: '8.x'
      Linux_Net8:
        imageName: 'ubuntu-latest'
        dotnetVersion: '8.x'

  pool:
    vmImage: $(imageName) # Dynamically picks pool based on matrix

  steps:
  - task: UseDotNet@2
    inputs:
      version: $(dotnetVersion) # Dynamically picks version

  - script: echo "Running on $(imageName) with .NET $(dotnetVersion)"

```

---

### **4. Real World Scenario: The Governance Repo**

**The "Architect" Pattern:**
You have 50 microservices. You don't want 50 copies of `azure-pipelines.yml`.

1. Create a git repo named `devops-templates`.
2. Put `standard-build.yml` in it.
3. Reference it in your Microservices.

**Microservice A `azure-pipelines.yml`:**

```yaml
resources:
  repositories:
    - repository: templatesRepo
      type: git
      name: MyProject/devops-templates # Points to the other repo

stages:
# Extends syntax is the most powerful way to inherit a pipeline
- template: standard-build.yml@templatesRepo
  parameters:
    solutionName: 'OrderService.sln'

```

**Why is this Expert Level?**
If you need to add SonarQube scanning to **all 50 microservices**, you edit `standard-build.yml` in the `devops-templates` repo **once**. The next time any microservice builds, they automatically get the security scan.

---

### **Summary of Phase 4**

1. **Templates:** Extract repetitive `steps` or `jobs` into `.yml` files.
2. **Parameters:** Typed inputs (`string`, `boolean`, `object`) for templates.
3. **Conditions:** Control flow (`failed()`, `eq()`).
4. **Matrix:** Run one job definition across multiple configs simultaneously.

Are you ready to move to **Phase 5: Security & Secrets**? (We will learn why you should never commit passwords to Git, and how to use KeyVault).