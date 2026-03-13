import os
import sys
import subprocess
import pyperclip
import pathspec
import re
import time

# --- CONFIGURATION ---
IGNORE_FILENAME    = ".aicontextignore.txt"
SUGGESTIONS_FILENAME = "new_files_to_consider.txt"
CONTEXT_FILENAME   = f"{os.path.basename(os.getcwd())}.ai_context.txt"
CLIPBOARD_LIMIT    = 500_000

# GAP-4: Always-on token warning threshold (tokens, not chars)
TOKEN_WARN_THRESHOLD  = 200_000   # warn at 200K tokens (~800KB of code)
TOKEN_ERROR_THRESHOLD = 500_000   # hard warning at 500K tokens

# GAP-6: Sentinel files that confirm we are inside a valid project root.
# At least ONE of these must exist in cwd before the agent proceeds.
PROJECT_SENTINEL_FILES = [
    "*.sln",          # .NET solution
    "*.csproj",       # .NET project (single-project repos)
    "package.json",   # Node/JS project
    "requirements.txt",
    "Dockerfile",
    "Dockerfile.webapp",
    "run_agent.bat",  # Our own launcher — always present in valid roots
]

# Regex patterns for file prioritization (Lower index = Higher priority)
# 0. Architecture/Deep Core (Interfaces, Base classes, Entry Points)
# 1. Data Models (DTOs, Models, Types, Schemas)
# 2. Configuration & Infra (Settings, Docker, JSON config)
# 3. Core Business Logic (Services, Managers, Libs)
# 4. Documentation (Architecture, Requirements, Deployment)
PRIORITY_PATTERNS = [
    # --- LEVEL 0: Architecture & Entry Points ---
    r".*[\\\/]I[A-Z][a-zA-Z0-9]+\.cs$",      # C# Interfaces
    r".*[\\\/]Base[a-zA-Z0-9]+\.cs$",         # Base classes
    r".*abstract.*\.cs$",                      # Abstract classes
    r".*Program\.cs$",                         # C# Entry
    r".*Startup\.cs$",                         # C# Startup
    r".*main\.py$",                            # Python Entry
    r".*__init__\.py$",                        # Python Init
    r".*index\.html$",                         # Web Entry
    r".*App\.tsx?$",                           # React/Web Entry

    # --- LEVEL 0 (project-specific): Critical gateway/session files ---
    r".*HybridBffService\.cs$",                # Single API gateway — all backend calls route through here
    r".*SessionManager\.cs$",                  # Central auth & session state
    r".*AppConfig\.cs$",                       # Compile-time config constants
    r".*NavigationService\.cs$",               # Form navigation orchestrator
    r".*StartupGuard\.cs$",                    # Bootstrap error handler

    # --- LEVEL 1: Data Models & Types ---
    r".*[\\\/]Enums?[\\\/].*",
    r".*[\\\/]DTOs?[\\\/].*",
    r".*[\\\/]Models?[\\\/].*",
    r".*[\\\/]Entities?[\\\/].*",
    r".*[\\\/]schemas?[\\\/].*",               # Python Schemas
    r".*\.d\.ts$",                             # TS Types
    r".*[\\\/]types[\\\/].*",                  # JS/TS Types

    # --- LEVEL 2: Configuration ---
    r".*[\\\/]Configuration[\\\/].*",
    r".*appsettings.*\.json$",
    r".*AppConfig\.cs$",
    r".*package\.json$",                       # Node Config
    r".*tsconfig\.json$",                      # TS Config
    r".*requirements\.txt$",                   # Python Config
    r".*Dockerfile[^.]*$",                     # Dockerfiles (any variant)
    r".*\.csproj$",                            # Project files
    r".*\.sln$",                               # Solution files
    r".*nginx\.conf$",                         # Nginx config
    r".*docker-compose.*\.yml$",               # Compose files
    r".*azure-pipelines\.yml$",                # CI/CD pipeline

    # --- LEVEL 3: Core Logic ---
    r".*[\\\/]Services?[\\\/].*",
    r".*[\\\/]Managers?[\\\/].*",
    r".*[\\\/]Repositories?[\\\/].*",
    r".*[\\\/]utils?[\\\/].*",
    r".*[\\\/]lib?[\\\/].*",
    r".*[\\\/]Controllers?[\\\/].*",           # WebApi controllers
    r".*[\\\/]Middleware[\\\/].*",             # WebApi middleware
    r".*[\\\/]Common[\\\/].*",                 # Shared utilities

    # --- LEVEL 4: Documentation (high-value for AI context) ---
    r".*TECHNICAL_ARCHITECTURE\.md$",
    r".*requirements\.md$",
    r".*DEPLOYMENT\.md$",
    r".*README\.md$",
]
# --- END CONFIGURATION ---


def get_file_priority(filepath):
    """Returns a priority score (0-based index) for a file. Lower is better. Default is 999."""
    norm_path = filepath.replace("\\", "/")
    for i, pattern in enumerate(PRIORITY_PATTERNS):
        if re.search(pattern, norm_path, re.IGNORECASE):
            return i
    return 999


def estimate_tokens(text):
    """Approximate token count (roughly 4 chars per token for code/English)."""
    return len(text) // 4


def check_project_root():
    """
    GAP-6: Verify the current working directory is a valid project root.
    Checks for at least one sentinel file/pattern. Warns (does not abort)
    if none are found, so the user can still proceed intentionally.
    """
    import glob
    for sentinel in PROJECT_SENTINEL_FILES:
        if glob.glob(sentinel):
            return True
    print("[WARN] No project sentinel file found in the current directory.")
    print(f"   Current directory: {os.getcwd()}")
    print("   Expected to find one of: " + ", ".join(PROJECT_SENTINEL_FILES))
    print("   Are you running run_agent.bat from the correct project root?")
    print("   Proceeding anyway -- press Ctrl+C to abort.\n")
    return False


def update_ignore_list_suggestions():
    """Intelligently generates a list of new files/folders not yet covered by the ignore file."""
    print("--- Updating Ignore List Suggestions ---")

    existing_patterns = []
    if os.path.exists(IGNORE_FILENAME):
        print(f"INFO: Reading your existing '{IGNORE_FILENAME}'...")
        with open(IGNORE_FILENAME, "r", encoding="utf-8", errors="replace") as f:
            existing_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        print(f"INFO: No '{IGNORE_FILENAME}' file found. Scanning all possible candidates.")

    spec = pathspec.PathSpec.from_lines("gitwildmatch", existing_patterns)

    all_project_items = []
    for root, dirs, files in os.walk(".", topdown=True):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in dirs:
            all_project_items.append(os.path.join(root, name).replace("\\", "/") + "/")
        for name in files:
            all_project_items.append(os.path.join(root, name).replace("\\", "/"))

    unignored_items = [p for p in all_project_items if not spec.match_file(p)]
    operational_files = {os.path.basename(__file__), SUGGESTIONS_FILENAME, CONTEXT_FILENAME, IGNORE_FILENAME}
    final_suggestions = sorted([item for item in unignored_items if os.path.basename(item) not in operational_files])

    if not final_suggestions:
        print(f"\n[OK] Your '{IGNORE_FILENAME}' file is up-to-date. No new items to suggest.")
        return

    with open(SUGGESTIONS_FILENAME, "w", encoding="utf-8") as f:
        f.write(f"# Review this list of items not currently covered by your '{IGNORE_FILENAME}'.\n")
        f.write("# Copy any lines for files/folders you wish to IGNORE into your .aicontextignore.txt file.\n")
        f.write("# You can then delete this suggestions file.\n")
        f.write("-" * 70 + "\n")
        for item in final_suggestions:
            f.write(item + "\n")

    print(f"\n[OK] Found {len(final_suggestions)} new items.")
    print(f"Suggestions have been written to '{SUGGESTIONS_FILENAME}'. Please review it.")


def load_ignore_patterns():
    patterns = [CONTEXT_FILENAME, os.path.basename(__file__), SUGGESTIONS_FILENAME]
    if os.path.exists(IGNORE_FILENAME):
        print(f"INFO: Loading ignore patterns from '{IGNORE_FILENAME}'.")
        with open(IGNORE_FILENAME, "r", encoding="utf-8", errors="replace") as f:
            patterns.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
    else:
        print(f"INFO: No '{IGNORE_FILENAME}' file found. Using minimal default ignores.")
    return patterns


def get_files_to_process(ignore_patterns, mode="all"):
    """Determines the list of files to process based on the requested mode."""
    spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)

    # --- GAP-3 + GAP-5: Improved "Changes Only" Mode ---
    if mode == "changes":
        print("INFO: --changes flag detected. Searching for changed files via Git.")
        try:
            # Unstaged changes vs index
            unstaged  = subprocess.check_output(
                ["git", "diff", "--name-only"], stderr=subprocess.DEVNULL
            ).decode("utf-8").strip().splitlines()

            # GAP-3 FIX: Also include staged (cached) changes vs HEAD
            staged    = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"], stderr=subprocess.DEVNULL
            ).decode("utf-8").strip().splitlines()

            # Untracked new files
            untracked = subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard"], stderr=subprocess.DEVNULL
            ).decode("utf-8").strip().splitlines()

            # Deduplicate (a file can appear in both unstaged and staged lists)
            changed_files    = list(dict.fromkeys(unstaged + staged + untracked))
            filtered_changes = [f for f in changed_files if f and not spec.match_file(f.replace("\\", "/"))]

            if filtered_changes:
                print(f"INFO: Found {len(filtered_changes)} changed file(s) "
                      f"({len(unstaged)} unstaged, {len(staged)} staged, {len(untracked)} untracked).")
                return filtered_changes
            else:
                # GAP-5 FIX: Don't silently exit — fall back to full scan with a clear message
                print("INFO: No un-ignored git changes found.")
                print("INFO: Falling back to full project scan (working tree is clean).")
                # Fall through to full scan below

        except Exception as e:
            print(f"WARNING: Git command failed ({e}). Falling back to full scan.")
            # Fall through to full scan below

    # --- Default "All Files" Mode (also fallback from --changes with no results) ---
    if mode != "changes":
        print("INFO: Defaulting to a full scan of all project files.")
    all_files = []
    for root, dirs, files in os.walk(".", topdown=True):
        root_normalized = root.replace("\\", "/")
        dir_paths_to_check = [f"{root_normalized}/{d}/".lstrip("./") for d in dirs]
        ignored_dir_paths  = set(spec.match_files(dir_paths_to_check))
        dirs[:] = [d for d in dirs if f"{root_normalized}/{d}/".lstrip("./") not in ignored_dir_paths]
        for filename in files:
            filepath = os.path.join(root, filename).replace("\\", "/")
            if not spec.match_file(filepath):
                all_files.append(filepath)
    return all_files


def generate_tree_view(file_list, file_tokens=None):
    """
    Renders an ASCII tree of the included files.
    file_tokens: optional dict of {filepath_normalized: token_count}.
                 When provided, each leaf node shows [~NNNt] beside the filename.
    """
    file_tokens = file_tokens or {}

    tree = {}
    for path in sorted(file_list):
        parts = path.replace("\\", "/").split("/")
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    def format_size(size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def build_tree_lines(d, prefix="", parent=""):
        lines, entries = [], sorted(d.keys())
        for i, entry in enumerate(entries):
            connector   = "+-- " if i < len(entries) - 1 else "\\-- "
            full_path   = os.path.join(parent, entry) if parent else entry
            norm_path   = full_path.replace("\\", "/").lstrip("./")
            display_text = entry

            # Leaf node (file)
            if not d[entry] and os.path.isfile(full_path):
                annotations = []
                try:
                    size = os.path.getsize(full_path)
                    annotations.append(format_size(size))
                except Exception:
                    pass

                # Token count — try both with and without leading './' prefix
                tok = file_tokens.get(norm_path) or file_tokens.get(full_path.replace("\\", "/"))
                if tok is not None:
                    annotations.append(f"~{tok:,}t")

                if annotations:
                    display_text += " [" + ", ".join(annotations) + "]"

            lines.append(prefix + connector + display_text)
            if d[entry]:
                extension = "|   " if i < len(entries) - 1 else "    "
                lines.extend(build_tree_lines(d[entry], prefix + extension, full_path))
        return lines

    return "\n".join(build_tree_lines(tree))


def print_token_report(text):
    """
    GAP-4: Always-on token estimate. Prints a clear report with warnings
    so the user knows before pasting into an AI whether the context is safe.
    """
    tokens  = estimate_tokens(text)
    size_kb = len(text) / 1024

    print(f"\n[INFO] Context Size Report:")
    print(f"   Characters : {len(text):>10,}")
    print(f"   Size       : {size_kb:>10.1f} KB")
    print(f"   Est. Tokens: {tokens:>10,}  (approx 4 chars/token)")

    if tokens > TOKEN_ERROR_THRESHOLD:
        print(f"   [CRITICAL] Context exceeds {TOKEN_ERROR_THRESHOLD:,} tokens!")
        print("              Most models will truncate or refuse this input.")
        print("              Action: Tighten .aicontextignore.txt or use --changes mode.")
    elif tokens > TOKEN_WARN_THRESHOLD:
        print(f"   [WARNING]  Context exceeds {TOKEN_WARN_THRESHOLD:,} tokens.")
        print("              Consider using --changes for targeted updates.")
    else:
        print(f"   [OK]       Context is within safe limits.")


def main():
    if "--generate-list" in sys.argv:
        update_ignore_list_suggestions()
        return

    print("Agent starting...")

    # GAP-6: Validate we are in a project root before doing anything
    check_project_root()

    mode = "changes" if "--changes" in sys.argv else "all"

    ignore_patterns  = load_ignore_patterns()
    files_to_process = get_files_to_process(ignore_patterns, mode=mode)

    if not files_to_process:
        print("No relevant files found to process. Exiting.")
        return

    # Sort by Priority
    files_to_process.sort(key=lambda f: (get_file_priority(f), f))

    # Context Header with Unique ID
    gen_id = int(time.time())
    mode_label = "DELTA (changed files only)" if mode == "changes" else "FULL SCAN"
    full_context_str  = f"=== CONTEXT FILE: {os.path.basename(os.getcwd())} ===\n"
    full_context_str += f"=== GENERATION ID: {gen_id} ===\n"
    full_context_str += f"=== MODE: {mode_label} ===\n"
    full_context_str += f"=== GENERATED: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n"

    # Prioritized TOC
    full_context_str += "--- TABLE OF CONTENTS (Prioritized) ---\n"
    for f in files_to_process:
        p   = get_file_priority(f)
        tag = "[ARCH]" if p < 15 else "[CODE]" if p < 900 else "[MISC]"
        full_context_str += f"{tag} {f}\n"
    full_context_str += "==================================================\n\n"

    # Build context string and track per-file token counts simultaneously
    file_tokens = {}   # {normalized_path: token_count}
    for filepath in files_to_process:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content         = f.read()
                normalized_path = filepath.replace("\\", "/").lstrip("./")
                file_tokens[normalized_path] = estimate_tokens(content)
                full_context_str += f"--- FILE: {normalized_path} ---\n{content}\n--- END FILE ---\n\n"
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")

    # GAP-4: Always print token report (not opt-in)
    print_token_report(full_context_str)

    with open(CONTEXT_FILENAME, "w", encoding="utf-8") as f:
        f.write(full_context_str)
    print(f"\n[OK] Context written to '{CONTEXT_FILENAME}'.")

    # Copy to clipboard if small enough
    if len(full_context_str) < CLIPBOARD_LIMIT:
        try:
            pyperclip.copy(full_context_str)
            print("[OK] Copied to clipboard.")
        except Exception:
            print("[INFO] Could not copy to clipboard. Use the generated file.")
    else:
        print(f"[INFO] Context too large for clipboard (>{CLIPBOARD_LIMIT:,} chars). Use the file.")

    print("\n--- Context File Structure (size, ~tokens) ---")
    print(generate_tree_view(files_to_process, file_tokens=file_tokens))
    print("----------------------------------------------")
    total_file_tokens = sum(file_tokens.values())
    print(f"Total files   : {len(files_to_process)}")
    print(f"Total tokens  : ~{total_file_tokens:,}t  (file content only, excl. headers/TOC)")

    # Top token offenders — helps identify what to add to .aicontextignore.txt
    if file_tokens:
        print("\n--- All Files by Token Count (descending) ---")
        sorted_by_tokens = sorted(file_tokens.items(), key=lambda x: x[1], reverse=True)
        max_tok = sorted_by_tokens[0][1] if sorted_by_tokens[0][1] > 0 else 1
        for rank, (path, tok) in enumerate(sorted_by_tokens, start=1):
            bar_width = 20
            bar_fill  = int((tok / max_tok) * bar_width)
            bar       = "#" * bar_fill + "-" * (bar_width - bar_fill)
            print(f"  {rank:>3}. [{bar}] ~{tok:>6,}t  {path}")
        print("---------------------------------------------")


if __name__ == "__main__":
    main()