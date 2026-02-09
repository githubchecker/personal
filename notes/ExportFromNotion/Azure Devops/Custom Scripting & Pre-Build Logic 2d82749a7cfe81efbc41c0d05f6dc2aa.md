# Custom Scripting & Pre-Build Logic

**Custom Scripting & Pre-Build Logic**

Built-in tasks (like "DotNetCoreCLI") are great, but they are rigid. To handle real-world scenarios—like parsing a JSON config, calculating a dynamic version number, or handling complex logic—you need to write scripts.

As a .NET developer, **PowerShell** is your weapon of choice, even on Linux agents.

---

### **1. The Big Three Scripting Tasks**

You will see these three tasks used to run custom commands.

### **A. `PowerShell@2` (Recommended)**

- **Why:** It runs **PowerShell Core (pwsh)**. It works on `windows-latest` AND `ubuntu-latest`. It creates an object-oriented scripting environment perfect for .NET logic.
- **Syntax:**

```yaml
- task: PowerShell@2
  inputs:
    targetType: 'inline' # or 'filePath'
    script: |
      $version = "1.0.0"
      Write-Host "Determined version is $version"

```

### **B. `Bash@3`**

- **Why:** Best for raw Linux commands if using `ubuntu-latest`. Faster startup time than PowerShell, but harder for C# devs to maintain if you aren't fluent in Bash.
- **Syntax:**

```yaml
- task: Bash@3
  inputs:
    targetType: 'inline'
    script: echo "Hello Linux"

```

### **C. `CmdLine@2` (Avoid)**

- **Why:** Runs `cmd.exe` on Windows or `sh` on Linux. It is very basic. Only use it for simple one-liners like `dir` or `cat`.

---

### **2. Pre-Build Tasks: Preparing the Kitchen**

Before you cook (Compile), you must clean the counter and check the ingredients.

### **A. Restoring Tools**

Your project might rely on local .NET tools (like EF Core migrations or linters) defined in a `.config/dotnet-tools.json` file. The Build Agent doesn't have these by default.

```yaml
steps:
- task: PowerShell@2
  displayName: 'Restore .NET Tools'
  inputs:
    targetType: 'inline'
    script: dotnet tool restore

```

### **B. Dynamic Versioning (The Expert Way)**

Novices let Azure name builds `#1022`. Experts name builds `1.0.4-beta.2`.
You often run a tool like **GitVersion** before the build starts to calculate the version based on your Git Commit History.

```yaml
# Simplified example of setting a build version
- task: PowerShell@2
  displayName: 'Calculate Version'
  inputs:
    targetType: 'inline'
    script: |
      # In reality, you'd call a tool like 'dotnet-gitversion' here
      $myVersion = "1.2.5"
      Write-Host "Current Semantic Version: $myVersion"

```

---

### **3. Agent Communication (The "Magic" VSO Commands)**

This is the most critical concept in Phase 1.5.

**Problem:** If you calculate a variable `$myVersion = "1.2.5"` inside a PowerShell script, that variable **dies** when the script finishes. The next step in the pipeline (the `.NET Build`) doesn't know about it.

**Solution:** You must use **Logging Commands**.
The Agent monitors the Standard Output (Console logs) of your script. If it sees a specific syntax starting with `##vso`, it executes an internal command.

### **Command A: Set Variable (Pass data to next step)**

**Syntax:** `##vso[task.setvariable variable=NAME]VALUE`

**PowerShell Example:**

```yaml
- task: PowerShell@2
  displayName: 'Set Custom Variable'
  inputs:
    targetType: 'inline'
    script: |
      $calculatedVersion = "1.2.5"
      # This looks like text, but the Agent intercepts it!
      Write-Host "##vso[task.setvariable variable=AppVersion]$calculatedVersion"

```

**Next Step Usage:**
You can now use `$(AppVersion)` in any subsequent YAML step.

### **Command B: Update Build Number (Change the UI)**

**Syntax:** `##vso[build.updatebuildnumber]VALUE`

**PowerShell Example:**

```yaml
- task: PowerShell@2
  inputs:
    targetType: 'inline'
    script: |
      $name = "Release-2025-v1.0"
      Write-Host "##vso[build.updatebuildnumber]$name"

```

*Result:* The Azure DevOps UI will now show "Release-2025-v1.0" instead of "Build #555".

### **Command C: Log Warning/Error (Catch attention)**

**Syntax:** `##vso[task.logissue type=warning]MESSAGE`

```yaml
- task: PowerShell@2
  script: |
    Write-Host "##vso[task.logissue type=warning]Configuration file missing! Using default."

```

*Result:* The pipeline summary page will show a bright orange warning.

---

### **4. Inline vs. File-Path Scripts**

- **Inline:**
    - *Pros:* Great for small logic (under 10 lines). Easy to read in the browser.
    - *Cons:* No Intellisense. Hard to quote strings correctly (YAML formatting hell).
- **FilePath:**
    - *Pros:* Professional. You write `setup.ps1` in your IDE, test it locally, and check it into git. The YAML simply calls the file.
    - *Cons:* Requires checking out the repo.

**Recommendation:** If the script is longer than 5 lines, put it in a file (`/build/scripts/myscript.ps1`) and call it like this:

```yaml
- task: PowerShell@2
  inputs:
    filePath: '$(Build.SourcesDirectory)/build/scripts/myscript.ps1'
    arguments: '-Environment Production' # Passing params to the script

```

---

### **Summary of Phase 1.5**

1. **Use `PowerShell@2`:** It is cross-platform and powerful.
2. **`##vso` is magic:** Use `Write-Host "##vso[task.setvariable...]"` to persist data.
3. **Clean Up:** Use these scripts to run `dotnet tool restore` or version calculations *before* the main build.

Are you ready for **Phase 2: CI - Building Your Code**? (This is where we compile the C# code using the official .NET tasks).