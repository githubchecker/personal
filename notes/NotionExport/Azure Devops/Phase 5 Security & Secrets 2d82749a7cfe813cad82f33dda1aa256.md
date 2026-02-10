# Phase 5: Security & Secrets

The #1 rule of DevOps: **Never, ever commit passwords, API keys, or connection strings to Git.** If you commit a secret to a repo, assume it is compromised.

In this phase, we learn the three places to hide secrets so your pipeline can use them without anyone seeing them.

---

### **1. The Hierarchy of Secrets**

1. **Pipeline Variables (UI):** Simple secrets for a specific pipeline.
2. **Variable Groups (Library):** Shared secrets used by *many* pipelines.
3. **Azure Key Vault (Gold Standard):** Centralized secrets managed by IT/Security teams, synced to DevOps.
4. **Secure Files:** Binary secrets (Certificates like `.pfx`).

---

### **2. Method A: Pipeline Variables (Simple & Fast)**

If you just need a quick API Key for one specific project:

1. **Setup:** Go to your Pipeline Editor -> Click the **"Variables"** button (Top Right).
2. **Add:** Name: `MyApiKey`, Value: `12345`.
3. **Lock It:** Check the **"Keep this value secret"** (Padlock icon).
4. **Result:**
    - The value is stored encrypted in the Azure DevOps database.
    - If you try to `echo $(MyApiKey)`, the logs will show `**`.
    - YAML usage: `$(MyApiKey)`.

---

### **3. Method B: Variable Groups (The Shared Library)**

**Scenario:** You have 5 Microservices. They all need the same SQL Connection String. If you use Method A, you have to update 5 pipelines when the password changes.

1. **Setup:** Go to **Pipelines -> Library**.
2. **Create:** New Variable Group named `Global-Shared-Vars`.
3. **Add:** `SqlConnection` = `Server=...` (Click the Lock icon).
4. **Usage in YAML:**
You must explicitly reference the group at the top of your YAML.

```yaml
variables:
- group: Global-Shared-Vars # Access all variables inside this group
- name: LocalVar
  value: 'SomeValue'

steps:
- script: echo "Connecting to $(SqlConnection)"
  # Log output: "Connecting to ***"

```

---

### **4. Method C: Azure Key Vault Integration (The Enterprise Standard)**

**Scenario:** The Security Team rotates database passwords weekly in Azure Key Vault (AKV). They don't want to log into Azure DevOps to update variables manually.

**Solution:** You link a Variable Group *directly* to Key Vault.

1. **Prerequisite:** Your Azure Service Connection (from Phase 3) must have **"Get" and "List"** permissions in the Key Vault's "Access Policies" (or RBAC).
2. **Setup:**
    - Go to **Pipelines -> Library -> + Variable Group**.
    - Toggle **"Link secrets from an Azure Key Vault as variables"**.
    - Select your Key Vault.
    - Select the specific secrets (e.g., `ProdDbConnectionString`).
3. **Result:**
    - DevOps acts as a "mirror". When the pipeline runs, it downloads the *current* value from Azure.
    - Usage in YAML is identical to Method B: `$(ProdDbConnectionString)`.

---

### **5. The "Mapping" Gotcha (The Expert Trap)**

This is the most common reason secrets fail in scripts.

**Rule:** Azure DevOps **secrets** (locked variables) are **NOT** automatically injected into Environmental Variables for scripts. Normal variables are, secrets are not.

**Scenario:** You run a PowerShell script that checks `$env:MyPassword`. It will be empty, even if `MyPassword` is defined in the Variable Group.

**The Fix:** You must explicitly map it.

```yaml
variables:
- group: Secrets-Group # Contains 'SuperSecretPass'

steps:
- task: PowerShell@2
  inputs:
    targetType: 'inline'
    script: |
      # Write-Host "Pass is $(SuperSecretPass)" <--- UNSAFE & MIGHT FAIL

      # Correct Way: Read from mapped Environment Variable
      Write-Host "The password length is $($env:MY_MAPPED_PASS.Length)"
  env:
    # EXPLICIT MAPPING REQUIRED FOR SECRETS
    MY_MAPPED_PASS: $(SuperSecretPass)

```

---

### **6. Method D: Secure Files (Certificates)**

Sometimes a secret isn't a string. It's a file, like a code signing certificate (`CodeSign.pfx`) or an Android Keystore.

1. **Upload:** Go to **Pipelines -> Library -> Secure Files**. Upload `MyCert.pfx`.
2. **Download in YAML:** Use the `DownloadSecureFile` task.
3. **Access:** The file is downloaded to a temp folder, usually `$(Agent.TempDirectory)`.

```yaml
steps:
- task: DownloadSecureFile@1
  name: MyCertTask # Name this so we can reference it later
  displayName: 'Download PFX'
  inputs:
    secureFile: 'MyCert.pfx'

- script: |
    echo "The file is at: $(MyCertTask.secureFilePath)"
    # Now use it to sign DLLs
    Signtool sign /f "$(MyCertTask.secureFilePath)" /p "MyPassword" ...

```

---

### **Summary of Phase 5**

| Method | Best For | Storage Location |
| --- | --- | --- |
| **Pipeline Variables** | One-off values for a single pipeline. | ADO Database |
| **Variable Groups** | Shared non-secrets (URLs) across projects. | ADO Database |
| **Azure Key Vault** | **High Security Secrets** (DB Passwords). | Azure Cloud |
| **Secure Files** | Binary files (`.pfx`, `.jks`). | ADO Encrypted Storage |

**Expert Tip:** Always map secrets (`env: Pass: $(MySecret)`) if using them in Scripts.

Are you ready to move to **Phase 6: Infrastructure & Performance**? (We learn how to cache NuGet packages to speed up builds and how to manage the agents themselves).