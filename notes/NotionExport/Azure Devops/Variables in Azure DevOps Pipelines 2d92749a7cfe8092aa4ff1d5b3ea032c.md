# Variables in Azure DevOps Pipelines

Of course. Here is the definitive, consolidated reference guide on Variables in Azure DevOps. This guide covers everything from the basics of pipeline variables to the secure integration of Azure Key Vault, designed to take a developer from novice to expert.

---

## **The Ultimate Guide to Variables in Azure DevOps Pipelines**

### **Part 1: The Three Tiers of Variables**

Think of variables in three levels of scope and security.

### **Tier 1: Pipeline Variables (Local & Simple)**

- **What they are:** Variables defined directly inside your `azure-pipelines.yml` file. They are local to that specific pipeline.
- **When to use them:** For non-sensitive, pipeline-specific configuration that you want to version control with your code. Examples: `buildConfiguration: 'Release'`, `projectPath: '**/MyApi.csproj'`.
- **Security:** **NOT SECURE.** These are plain text in your Git repository. **Never store secrets here.**
- **YAML Syntax:**
    
    ```yaml
    variables:
      - name: myLocalVariable
        value: 'Hello from YAML'
      - name: anotherVariable # shorthand syntax
        value: 'Another value'
    
    ```
    

### **Tier 2: Variable Groups (Shared & Secure)**

- **What they are:** A reusable collection of variables and secrets defined in the Azure DevOps **Library** (`Pipelines -> Library`).
- **When to use them:**
    - For sharing the same configuration value (like an API URL) across **multiple pipelines**.
    - For storing **simple secrets** (like a connection string) that are managed by the DevOps team.
- **Security:** Can store both plain text and **secret** variables. Secrets are encrypted at rest and masked in logs (`**`).
- **How to Create:**
    1. Go to **Pipelines -> Library -> + Variable group**.
    2. Give it a name (e.g., `Shared-Release-Config`).
    3. Add your variables. Click the **lock icon** to make a variable a secret.
    4. Save.
- **YAML Syntax to Use:**
    
    ```yaml
    variables:
      # This "imports" the entire group into your pipeline.
      - group: 'Shared-Release-Config'
    
    ```
    

### **Tier 3: Azure Key Vault (The Gold Standard for Secrets)**

- **What it is:** A dedicated, hardware-secured Azure service for managing secrets, keys, and certificates.
- **When to use it:** The **best practice** for all production secrets. It provides centralized management, audit logs, and rotation policies, often managed by a dedicated security team.
- **Security:** **Highest level.** Secrets are encrypted at rest and in transit. Your pipeline authenticates using a secure Service Principal or Managed Identity, not a password.
- **How it Works:** You link a **Variable Group** to your Azure Key Vault, turning the group into a secure mirror.

---

### **Part 2: Linking a Variable Group to Azure Key Vault (Step-by-Step)**

This is the bridge that connects the ultra-secure world of Key Vault to your pipeline.

1. **Prerequisite in Azure:**
    - Have an **Azure Key Vault** with secrets stored in it (e.g., a secret named `Prod-DB-Password`).
    - Have an **Azure DevOps Service Connection** (`Azure Resource Manager` type). This connection's underlying Service Principal must have **"Get" and "List"** secret permissions on your Key Vault's "Access policies".
2. **Create the Linked Group in Azure DevOps:**
    1. Go to **Pipelines -> Library -> + Variable group**.
    2. Give the group a name, e.g., `Production-KeyVault-Secrets`.
    3. Toggle **ON** the switch for **"Link secrets from an Azure Key Vault as variables"**.
    4. Select your **Azure subscription** (via the service connection).
    5. Select your **Key vault name** from the dropdown.
    6. Click **Authorize**. (This confirms the permissions).
    7. Click the **+ Add** button. A list of secrets from your Key Vault will appear.
    8. Select the secrets you want to make available to your pipeline (e.g., `Prod-DB-Password`).
    9. Click **Save**.
3. **Use it in YAML:**
The usage is identical to a normal variable group.
    
    ```yaml
    variables:
      - group: 'Production-KeyVault-Secrets'
    
    ```
    

When your pipeline runs, it will now authenticate to Key Vault, download the value of `Prod-DB-Password`, and make it available as a secret variable named `Prod-DB-Password`.

---

### **Part 3: Accessing Variables (The Critical Differences)**

This is where the concepts of runtime, compile-time, and environment variables come together.

### **A. In Pipeline Tasks (Macro Syntax: `$(...)`)**

- **How it works:** Evaluated at **runtime**, just before the task executes.
- **What it can access:** **ALL** variables: local, group, and Key Vault secrets.
- **Security:** If the variable is a secret, the value will be masked as `**` in logs, but the task receives the real, unencrypted value.
- **When to use:** This is your default method for passing variables to task inputs.

```yaml
variables:
  - group: 'My-KeyVault-Group' # Contains 'MySecret'
  - name: myLocalVar
    value: 'local-value'

steps:
- task: SomeTask@1
  inputs:
    someInput: $(myLocalVar)
    secretInput: $(MySecret) # The task gets the real secret

```

### **B. In Scripts (Environment Variables: `$VAR_NAME` or `$env:VAR_NAME`)**

- **How it works:** Before running a script, the DevOps agent injects variables into the shell's environment. It converts names to `UPPER_CASE`.
- **What it can access:**
    - **AUTOMATICALLY:** Local variables and **non-secret** variables from groups.
    - **MANUALLY:** Secret variables **must** be explicitly mapped using the `env:` block.
- **Security:** This is a "safety on" feature. It prevents accidental leakage of all secrets to every script.

**Example Script:**

```yaml
variables:
  - group: 'My-KeyVault-Group' # Contains secret 'DatabasePassword'
  - name: AppName
    value: 'MyWebApp'

steps:
- task: PowerShell@2
  # This 'env' block creates an environment variable named 'DB_PASS' for this script only.
  env:
    DB_PASS: $(DatabasePassword)

  inputs:
    script: |
      # Non-secret is automatically available
      Write-Host "App Name from environment: $env:APPNAME"

      # Secret is ONLY available because we mapped it.
      # The value will be masked in logs, but tools can use it.
      Write-Host "Database password is: $env:DB_PASS"

      # This would be EMPTY because 'DatabasePassword' was not automatically mapped.
      Write-Host "Direct secret access (will fail): $env:DATABASEPASSWORD"

```

### **C. In Pipeline Structure (Template Expression: `${{...}}`)**

- **How it works:** Evaluated at **compile time**, when the pipeline is first parsed.
- **What it can access:** **Only non-secret variables** defined in the YAML file. It cannot access variable groups or secrets.
- **Security:** This is a strict security boundary to prevent secrets from being accessible during the structural parsing of the pipeline.
- **When to use:** For controlling the "shape" of your pipeline using `if`, `each`, or `parameters`.

```yaml
parameters:
- name: deployProd
  type: boolean
  default: false

# This entire stage will only exist if the parameter is true.
${{ if eq(parameters.deployProd, true) }}:
- stage: DeployProduction
  jobs:
  - job: A
    # ...

```

---

### **Part 4: Putting It All Together (The Placeholder Replacement Example)**

This is the full, novice-to-expert workflow you asked for.

**Goal:** Securely replace a database password placeholder in a Kubernetes manifest (`secret.yaml`) using a secret from Azure Key Vault.

**1. `secret.yaml` (Checked into Git):**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-db-secret
stringData:
  password: "#{DB_PASSWORD}#"

```

**2. `azure-pipelines.yml`:**

```yaml
variables:
  # Import the variable group linked to your Azure Key Vault.
  # This group contains the secret 'Prod-Db-Password'.
  - group: 'Production-KeyVault-Secrets'

stages:
- stage: Deploy
  jobs:
  - deployment: DeployAKS
    environment: 'MyAKS-Prod.production'
    strategy:
      runOnce:
        deploy:
          steps:
            - task: DownloadPipelineArtifact@1
              inputs:
                artifactName: 'manifests' # Assumes 'secret.yaml' is here
                downloadPath: '$(Pipeline.Workspace)/m'

            - task: replacetokens@5
              displayName: 'Replace Secret Placeholders in Manifest'
              inputs:
                rootDirectory: '$(Pipeline.Workspace)/m'
                targetFiles: 'secret.yaml'
                tokenPrefix: '#{'
                tokenSuffix: '}#'
                # IMPORTANT: Map the secret to a name the task can find.
                # The task looks for a variable named 'DB_PASSWORD'. We map our
                # Key Vault variable 'Prod-Db-Password' to it.
                variables: |
                  DB_PASSWORD: $(Prod-Db-Password)

            - task: KubernetesManifest@1
              displayName: 'Apply Secret to AKS'
              inputs:
                action: 'apply'
                manifests: '$(Pipeline.Workspace)/m/secret.yaml'

```

This final example ties all the concepts together: linking a Key Vault group, importing it, and using a task to securely consume the secret variable to modify a file before deployment.