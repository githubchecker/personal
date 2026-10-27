# 01 — How Python Runs & Setup

> Phase 0 · Module 0.1 · Lesson 1 of 16 · [Phase 0.1 — Python Index](README.md) · [Next: 02 Variables, Types & Operators →](02%20Variables%20Types%20and%20Operators.md)

---

## 🗺️ Stage 0 — Concept Map

**The problem:** Without knowing how Python executes and isolates code, you end up with mysterious errors: commands not recognized in your terminal, packages conflicting and breaking across different projects, and scripts running against the wrong interpreter.

**Where it fits:**
- **Builds on:** Nothing — this is the absolute starting point.
- **Unlocks:** Every subsequent module in this road map, from basic syntax to PyTorch, LangChain, and production API servers.

**Why care as an AI Engineer / Architect?**
AI development relies heavily on rapidly evolving open-source libraries (`torch`, `transformers`, `openai`, `pydantic`, `langchain`). These libraries often require specific, conflicting versions of underlying C-extensions and sub-dependencies. If you install everything globally onto your operating system, your development environment will quickly collapse into "dependency hell." Mastering the interpreter, PATH, and **virtual environments (`venv`)** is mandatory survival knowledge.

---

## 🔑 New Terms (plain English)

| Term | One-line meaning |
| :--- | :--- |
| **Interpreter** | The program (`python.exe`) that reads your plain text code and translates it into actions on your computer. |
| **Source code** | The human-readable text you write in a `.py` file. |
| **Bytecode** | The compact, internal machine-friendly instructions Python compiles your code into right before execution. |
| **REPL** | Read-Eval-Print Loop — an interactive scratchpad that runs one line of code at a time in the terminal. |
| **PATH** | An operating system environment variable listing the folders where the terminal searches for runnable programs. |
| **Package / Library** | A reusable collection of code written by others that you download to add capabilities to your project. |
| **`pip`** | The standard package installer program bundled with Python. |
| **Virtual Environment (`venv`)** | An isolated folder containing a dedicated copy of Python and its own independent set of installed libraries. |
| **`site-packages`** | The specific folder inside Python (or inside a `venv`) where downloaded third-party libraries live. |

---

## 🎈 Stage 1 — The Simple Idea

### Analogy 1: The Live Interpreter
A computer processor only understands raw machine switches (binary machine code) — not English, not Python. **Python is a live human translator standing between you and the computer.** You speak readable Python; the translator reads it sentence by sentence and tells the machine what to do as it goes.

Because translation happens on the fly, Python is called an **interpreted language**. You do not need to run a separate manual compile command to produce an executable file before testing your code; you hand your script to the interpreter and it executes immediately.

> **The "Aha!":** "Python" refers to two things: the **language** (the syntax and grammar rules) and the **interpreter** (the program named `python.exe` that executes those rules).

### Analogy 2: Virtual Environments (`venv`) as Dedicated Toolboxes
Imagine you are building two different physical models in your garage:
- Project A is a delicate vintage watch requiring tiny micro-screwdrivers.
- Project B is a heavy-duty lawnmower requiring giant steel wrenches.

If you dump all your tools into one giant central bin, tools collide, parts get lost, and using the wrong wrench on the watch strips the screws.

A **virtual environment** is a dedicated, self-contained toolbox for each project. Project A gets its own small box with only its micro-screwdrivers; Project B gets its own box with its wrenches. Neither knows the other exists. If you destroy Project B's toolbox, Project A is completely untouched.

---

## ⚙️ Stage 2 — How It Actually Works

### 1.1 What happens when you run a program

```text
your_script.py  ──►  Python Interpreter  ──►  Bytecode (.pyc)  ──►  Python Virtual Machine (PVM)  ──►  Output
 (Source code)        (Checks syntax &        (Internal compact      (Executes instructions on
                      parses tokens)          instructions)          your CPU & memory)
```

1. You write plain-text **source code** in a `.py` file.
2. The **interpreter** reads your file, validates syntax, and quietly compiles it into **bytecode** (stored in memory or cached in a `__pycache__` folder).
3. The **Python Virtual Machine (PVM)** executes the bytecode against your machine's CPU and operating system.
4. You see the printed output or results.

---

### 1.2 Installing Python on Windows

1. Download the latest stable Python 3 release from the official website: **[python.org/downloads](https://www.python.org/downloads/)**.
2. Run the installer.
3. ⚠️ **Critical Step:** On the very first screen of the installer, check the box:
   `☑ Add python.exe to PATH`
4. Click **Install Now**.
5. Verify the installation by opening a new PowerShell window:

```powershell
# Check interpreter version
python --version
# Expected output: Python 3.12.x (or newer)

# On Windows, you can also use the Python launcher:
py --version
```

> [!NOTE]
> **What does PATH do?** When you type `python` in a terminal, Windows searches every directory listed in your `PATH` environment variable until it finds `python.exe`. If Python is not on `PATH`, Windows returns: `'python' is not recognized as an internal or external command`.

---

### 1.3 Running Python: REPL vs. Script

#### (a) The REPL (Interactive Scratchpad)
Type `python` with no arguments to enter the REPL:

```powershell
python
```
```python
# The '>>>' indicates Python is waiting for your input
>>> 2 + 3
5
>>> text = "AI Engineer"
>>> text.lower()
'ai engineer'
>>> exit()   # or press Ctrl+Z then Enter to return to PowerShell
```

#### (b) Script Files (Production Workflow)
Save your code in a file named `main.py`:

```python
# main.py
# print() sends text to the terminal standard output
print("System initialized.")

model_name = "gpt-4o"
tokens = 1500

# An f-string lets you interpolate variables directly into text
print(f"Model: {model_name} | Tokens used: {tokens}")
```

Run it from your terminal:

```powershell
python main.py
# Output:
# System initialized.
# Model: gpt-4o | Tokens used: 1500
```

---

### 1.4 Virtual Environments (`venv`): Isolation & Setup

#### The Problem: Global Package Pollution
When you install a library globally using `pip install package_name`, Python deposits the files into your machine's global `Lib/site-packages` directory.

Consider this common AI development conflict:
- **Project Alpha (Legacy Bot):** Requires `pydantic==1.10.13` (used by older LangChain).
- **Project Beta (Modern Agent):** Requires `pydantic==2.8.2` (Pydantic V2 has breaking syntax changes).

If you install globally, Project Beta's install will overwrite Project Alpha's files. Project Alpha will immediately crash with `ImportError` or `ValidationError`.

```text
❌ GLOBAL INSTALL (Fragile):
Global Python 3.12 ──► site-packages ──► pydantic 2.8.2 (OVERWRITES v1.10!)
                             ▲
              Both projects share this folder

✅ VIRTUAL ENVIRONMENTS (Isolated):
Project-Alpha/ ──► .venv/ ──► site-packages ──► pydantic 1.10.13  (Safe!)
Project-Beta/  ──► .venv/ ──► site-packages ──► pydantic 2.8.2    (Safe!)
```

---

#### Step 1: Create the Virtual Environment
Navigate to your project root folder in PowerShell and tell Python to run its built-in `venv` module:

```powershell
# Syntax: python -m venv <folder_name>
# Standard convention is to name the folder '.venv' or 'venv'
python -m venv .venv
```

> [!NOTE]
> **What does `-m` mean?** The `-m` flag tells the Python interpreter: "Search your standard library for the module named `venv`, and run it as a script."

What Python creates inside your project directory:
```text
my-project/
├── .venv/                     # The virtual environment directory
│   ├── Include/               # C headers for compiling native extensions
│   ├── Lib/
│   │   └── site-packages/     # Isolated folder where third-party packages will go
│   ├── Scripts/               # Executables & activation scripts on Windows
│   │   ├── python.exe         # Dedicated redirector binary
│   │   ├── pip.exe            # Dedicated package installer
│   │   ├── Activate.ps1       # Activation script for PowerShell
│   │   └── activate.bat       # Activation script for CMD
│   └── pyvenv.cfg             # Configuration file pointing to base Python install
├── main.py
└── .gitignore
```

#### Under the Hood: What `venv` Actually Does
A virtual environment does **not** make a heavy, full copy of the entire Python runtime. Instead:
1. It creates lightweight stub executables (`python.exe`, `pip.exe`) inside `.venv/Scripts/`.
2. It writes a file called `pyvenv.cfg` storing the path to your base system Python:
   ```ini
   home = C:\Users\Username\AppData\Local\Programs\Python\Python312
   include-system-site-packages = false
   version = 3.12.2
   ```
3. When activated, it temporarily prepends `.venv\Scripts` to the front of your system `PATH`. When you type `python` or `pip`, Windows picks up the `.venv` executables first!

---

#### Step 2: Activate the Virtual Environment

##### On Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Once activated, your terminal prompt changes to show the prefix `(.venv)`:
```powershell
(.venv) PS C:\Code\my-project>
```

##### On Windows Command Prompt (CMD):
```cmd
.\.venv\Scripts\activate.bat
```

##### On macOS / Linux (or Git Bash on Windows):
```bash
source .venv/bin/activate
```

---

> ⚠️ **THE POWERSHELL EXECUTION POLICY TRAP:**  
> On fresh Windows machines, running `.\.venv\Scripts\Activate.ps1` often fails with this error:
> ```text
> File ... .venv\Scripts\Activate.ps1 cannot be loaded because running scripts 
> is disabled on this system. (PSSecurityException)
> ```
> **The Fix:** Windows blocks downloaded scripts by default. Allow local scripts for your user account by running this once in PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then run `.\.venv\Scripts\Activate.ps1` again. It will now activate cleanly.

---

#### Step 3: Installing Packages Inside the Environment
With `(.venv)` displayed in your prompt, any package you install is placed strictly inside `.venv/Lib/site-packages`:

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install a third-party package (e.g. requests for HTTP APIs)
pip install requests

# Verify where it is installed:
pip show requests
# Location will show: C:\Code\my-project\.venv\Lib\site-packages
```

#### Step 4: Saving and Restoring Dependencies (`requirements.txt`)

```powershell
# Freeze current dependencies into a standard manifest file
pip freeze > requirements.txt

# Inspect the file contents
Get-Content requirements.txt
# requests==2.32.3
# urllib3==2.2.2
# ...

# When sharing code or cloning on a new machine, install all dependencies in one command:
pip install -r requirements.txt
```

#### Step 5: Deactivating the Environment
When you are finished working on the project, leave the environment:

```powershell
deactivate
# The '(.venv)' prefix disappears from your prompt.
```

---

### 1.5 Version Control: Never Commit `.venv`

The `.venv` folder contains machine-specific paths and binaries. **Never commit `.venv` to Git.**

Create a `.gitignore` file in your project root:
```gitignore
# Python Virtual Environments
.venv/
venv/
ENV/

# Python Cache & Bytecode
__pycache__/
*.pyc
```

Anyone cloning your project will simply run:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 1.6 Configuring VS Code for `venv`

To ensure VS Code provides autocomplete, linting, and runs your code using the virtual environment:

1. Open your project folder in VS Code (`File` → `Open Folder...`).
2. Press `Ctrl + Shift + P` to open the Command Palette.
3. Type: `Python: Select Interpreter`
4. Pick the interpreter located inside your virtual environment:  
   `Python 3.12.x ('.venv': venv) .\.venv\Scripts\python.exe`
5. VS Code will remember this selection in `.vscode/settings.json` and will automatically activate `.venv` every time you open an integrated terminal (`Ctrl + ~`).

---

### 1.7 Comments and Indentation Rules

```python
# 1. COMMENTS:
# Any text following '#' is ignored by Python.
# Use comments to explain the "why" and trade-offs, not obvious syntax.

# 2. INDENTATION:
# Python does NOT use curly braces {} to define code blocks.
# Python uses 4 SPACES of indentation to define code structure.

def check_status(is_active: bool):
    # 4 spaces indentation marks this line as inside the function body
    if is_active:
        # 8 spaces indentation marks this line as inside the if-block
        print("System is operational.")
    else:
        print("System is offline.")

check_status(True)
```

---

## 🚀 Stage 3 — In Practice / Why It Matters

In production AI development, virtual environment hygiene is the difference between reliable systems and untraceable bugs:

1. **CUDA & PyTorch Matching:** PyTorch builds must match your specific CUDA GPU driver versions. Keeping projects in isolated venvs prevents driver/binary mismatches.
2. **Reproducible Docker Containers:** Docker images for deploying FastAPI inference endpoints copy `requirements.txt` into the container and run `pip install` in a clean environment, mirroring your local venv.
3. **Multi-Model Pipelines:** A data preparation script might use older scientific packages (`scipy`), while your LLM agent uses bleeding-edge orchestration libraries (`langchain`, `llamaindex`). Isolating them prevents version lock.

---

## ⚖️ Variations & When to Use

| Tool | What it is | When to use it | When to avoid it |
| :--- | :--- | :--- | :--- |
| **`venv`** | Python built-in standard library tool | **Default for 95% of projects.** Zero installation required, standard in all tutorials and production pipelines. | When you need to manage multiple different Python engine versions (e.g., Python 3.10 vs 3.12). |
| **`uv`** | Modern ultra-fast package manager written in Rust | Large projects with complex dependencies where `pip install` is slow. Installs packages in milliseconds. | When keeping your environment minimal with zero external tool dependencies. |
| **`conda`** | Multi-language environment & package manager | Heavy data science projects requiring complex non-Python C/Fortran/CUDA system libraries outside Python. | Standard web APIs, microservices, and general Python development (it is heavy and slow). |

---

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| :--- | :--- | :--- |
| `'python' is not recognized...` | Python was installed without checking "Add to PATH" | Re-run installer, click "Modify", check "Add to PATH"; or use `py`. |
| `File ... Activate.ps1 cannot be loaded... PSSecurityException` | PowerShell blocks unsigned script execution by default | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell. |
| `ModuleNotFoundError: No module named 'requests'` | Package was installed in another environment, or venv is not activated | Look for `(.venv)` in prompt. Run `.\.venv\Scripts\Activate.ps1`, then check `pip list`. |
| Script runs against wrong Python in VS Code | VS Code selected the global interpreter instead of `.venv` | Press `Ctrl+Shift+P` → `Python: Select Interpreter` → Select `./.venv/Scripts/python.exe`. |
| `python: can't open file 'main.py': No such file or directory` | Your terminal current working directory is not the project folder | Run `pwd` or `dir` to verify directory; `cd` to the directory containing `main.py`. |

---

## 📌 Quick Reference

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Verify activation (prompt shows (.venv))
python -c "import sys; print(sys.prefix)"  # Outputs your .venv path

# 4. Install dependencies
pip install <package_name>
pip freeze > requirements.txt

# 5. Reinstall from requirements manifest
pip install -r requirements.txt

# 6. Deactivate environment
deactivate
```

---

## 🛑 STOP — Self-Check

You open a new PowerShell terminal, navigate to your AI project, and immediately run:
```powershell
pip install openai
```
However, when your teammate clones your repository on their machine and tries to run the project, it fails with:
```text
ModuleNotFoundError: No module named 'openai'
```
**What two mistakes happened on your machine, and what is the proper sequence to prevent this?**

<details><summary>Answer</summary>

### The Mistakes:
1. **No Virtual Environment Activation:** You ran `pip install openai` globally against your machine's base Python because the prompt did not show `(.venv)`.
2. **Missing Dependency Manifest:** You did not record the dependency into a version-controlled `requirements.txt` file.

### The Proper Sequence:
```powershell
# 1. Create and activate the virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install inside the isolated environment
pip install openai

# 3. Record the dependency into source control
pip freeze > requirements.txt

# 4. Commit requirements.txt (and ensure .venv is in .gitignore!)
```

🎉 **Setup Complete!** Continue to the next lesson: [02 Variables, Types & Operators →](02%20Variables%20Types%20and%20Operators.md)

</details>
