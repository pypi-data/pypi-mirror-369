# import os
# import argparse
# import sys
# import subprocess
# import shutil
# import platform
# import json
# import tempfile
# import urllib.request
# from typing import Optional

# # --- Installation Orchestrator and Helpers (Your Code, Integrated) ---

# def check_gh_installed() -> bool:
#     """Check if GitHub CLI is installed with proper verification"""
#     if shutil.which("gh"):
#         try:
#             # Verify gh is actually working
#             subprocess.run(["gh", "--version"], check=True, capture_output=True)
#             return True
#         except (subprocess.CalledProcessError, FileNotFoundError):
#             # Found but not working - might be a PATH issue or broken install
#             return False
#     return False

# def install_gh_cli() -> bool:
#     """Main installation function with comprehensive error handling"""
#     system = platform.system()
#     machine = platform.machine().lower()
    
#     print("\n🔧 Installing GitHub CLI...")
#     print(f"📋 System: {system}, Architecture: {machine}")
    
#     try:
#         if system == "Windows":
#             return install_gh_cli_windows()
#         elif system == "Darwin":
#             return install_gh_cli_mac()
#         elif system == "Linux":
#             return install_gh_cli_linux()
#         else:
#             print(f"❌ Unsupported OS: {system}")
#             return False
#     except Exception as e:
#         print(f"❌ Installation failed: {str(e)}")
#         return False

# def install_gh_cli_windows() -> bool:
#     """Windows installation with multiple fallback methods and PATH management"""
#     methods = [
#         try_winget_install,
#         try_scoop_install,
#         try_choco_install,
#         try_direct_msi_install,
#         try_direct_zip_install
#     ]
    
#     for method in methods:
#         if method():
#             if verify_gh_installation():
#                 return True
#         print("   ⚠️ Trying next installation method...")
    
#     print("❌ All Windows installation methods failed.")
#     return False

# def try_winget_install() -> bool:
#     """Attempt installation via winget"""
#     if not shutil.which("winget"):
#         return False
    
#     print("\n   🔄 Attempting winget installation...")
#     try:
#         subprocess.run(
#             ["winget", "install", "--id", "GitHub.cli", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
#             check=True,
#             capture_output=True
#         )
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"   ⚠️ winget failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
#         return False

# def try_scoop_install() -> bool:
#     """Attempt installation via scoop"""
#     if not shutil.which("scoop"):
#         return False
    
#     print("\n   🔄 Attempting scoop installation...")
#     try:
#         subprocess.run(["scoop", "install", "gh"], check=True, capture_output=True)
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"   ⚠️ scoop failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
#         return False

# def try_choco_install() -> bool:
#     """Attempt installation via chocolatey"""
#     if not shutil.which("choco"):
#         return False
    
#     print("\n   🔄 Attempting chocolatey installation...")
#     try:
#         subprocess.run(["choco", "install", "gh", "-y"], check=True, capture_output=True)
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"   ⚠️ chocolatey failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
#         return False

# def try_direct_msi_install() -> bool:
#     """Direct MSI installation with proper PATH handling"""
#     print("\n   🔄 Attempting direct MSI installation...")
#     temp_dir = ""
#     try:
#         release_info = get_github_release_info()
#         if not release_info: return False
        
#         msi_asset = next((a for a in release_info.get('assets', []) if a['name'].endswith('_windows_amd64.msi')), None)
#         if not msi_asset:
#             print("   ❌ Could not find Windows MSI installer.")
#             return False
            
#         temp_dir = tempfile.mkdtemp()
#         msi_path = os.path.join(temp_dir, msi_asset['name'])
#         print(f"   ⬇️ Downloading {msi_asset['name']}...")
#         if not download_file(msi_asset['browser_download_url'], msi_path): return False
        
#         print("   🛠 Installing (this may require administrator privileges)...")
#         subprocess.run(["msiexec", "/i", msi_path, "/quiet", "/norestart"], check=True)
        
#         shutil.rmtree(temp_dir, ignore_errors=True)
        
#         program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
#         gh_path = os.path.join(program_files, "GitHub CLI", "gh.exe")
#         if os.path.exists(gh_path): add_to_path(os.path.dirname(gh_path))
        
#         return True
#     except Exception as e:
#         print(f"   ❌ MSI installation failed: {str(e)}")
#         if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
#         return False

# def try_direct_zip_install() -> bool:
#     """Fallback ZIP installation for Windows"""
#     print("\n   🔄 Attempting direct ZIP installation...")
#     temp_dir = ""
#     try:
#         release_info = get_github_release_info()
#         if not release_info: return False
        
#         zip_asset = next((a for a in release_info.get('assets', []) if a['name'].endswith('windows_amd64.zip')), None)
#         if not zip_asset:
#             print("   ❌ Could not find Windows ZIP package.")
#             return False
            
#         temp_dir = tempfile.mkdtemp()
#         zip_path = os.path.join(temp_dir, zip_asset['name'])
#         print(f"   ⬇️ Downloading {zip_asset['name']}...")
#         if not download_file(zip_asset['browser_download_url'], zip_path): return False
        
#         print("   📦 Extracting...")
#         shutil.unpack_archive(zip_path, temp_dir)
        
#         bin_dir = next((root for root, _, files in os.walk(temp_dir) if "gh.exe" in files), None)
#         if not bin_dir:
#             print("   ❌ Could not find gh.exe in extracted files.")
#             shutil.rmtree(temp_dir, ignore_errors=True)
#             return False
        
#         install_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHubCLI")
#         os.makedirs(install_dir, exist_ok=True)
        
#         shutil.copytree(bin_dir, install_dir, dirs_exist_ok=True)
#         add_to_path(install_dir)
        
#         shutil.rmtree(temp_dir, ignore_errors=True)
#         return True
#     except Exception as e:
#         print(f"   ❌ ZIP installation failed: {str(e)}")
#         if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
#         return False

# def install_gh_cli_mac() -> bool:
#     """macOS installation with multiple methods"""
#     if shutil.which("brew"):
#         print("\n   🔄 Attempting Homebrew installation...")
#         try:
#             subprocess.run(["brew", "install", "gh"], check=True, capture_output=True)
#             if verify_gh_installation(): return True
#         except subprocess.CalledProcessError as e:
#             print(f"   ⚠️ Homebrew failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
    
#     print("❌ All macOS installation methods failed.")
#     return False

# def install_gh_cli_linux() -> bool:
#     """Linux installation with distro detection and multiple methods"""
#     package_managers = [
#         ("apt-get", "sudo apt-get update && sudo apt-get install -y gh"),
#         ("apt", "sudo apt update && sudo apt install -y gh"),
#         ("dnf", "sudo dnf install -y gh"),
#         ("yum", "sudo yum install -y gh"),
#         ("pacman", "sudo pacman -S --noconfirm github-cli"),
#         ("zypper", "sudo zypper install -y gh"),
#     ]
#     for pm, command in package_managers:
#         if shutil.which(pm):
#             print(f"\n   🔄 Attempting installation via {pm}...")
#             try:
#                 subprocess.run(command, shell=True, check=True, capture_output=True)
#                 if verify_gh_installation(): return True
#             except subprocess.CalledProcessError as e:
#                 print(f"   ⚠️ {pm} failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")

#     print("❌ All Linux package manager installations failed.")
#     return False

# def get_github_release_info() -> Optional[dict]:
#     """Get latest release info from GitHub API"""
#     try:
#         with urllib.request.urlopen("https://api.github.com/repos/cli/cli/releases/latest") as response:
#             return json.loads(response.read().decode())
#     except Exception as e:
#         print(f"   ❌ Failed to get release info from GitHub API: {str(e)}")
#         return None

# def download_file(url: str, path: str) -> bool:
#     """Download a file with progress reporting"""
#     try:
#         def reporthook(count, block_size, total_size):
#             if total_size > 0:
#                 percent = int(count * block_size * 100 / total_size)
#                 sys.stdout.write(f"\r      Downloading... {percent}%")
#                 sys.stdout.flush()
            
#         urllib.request.urlretrieve(url, path, reporthook=reporthook)
#         sys.stdout.write("\r      Downloading... 100%\n")
#         sys.stdout.flush()
#         return True
#     except Exception as e:
#         print(f"\n   ❌ Download failed: {str(e)}")
#         return False

# def add_to_path(directory: str):
#     """Add directory to PATH for the current session and try to make it permanent."""
#     print(f"   ✅ Adding {directory} to PATH...")
#     os.environ["PATH"] = f"{directory}{os.pathsep}{os.environ['PATH']}"
    
#     if platform.system() == "Windows":
#         try:
#             # This makes the PATH change permanent for the current user
#             subprocess.run(
#                 f'setx PATH "%PATH%;{directory}"',
#                 shell=True, check=True, capture_output=True
#             )
#         except Exception as e:
#             print(f"   ⚠️ Could not make PATH change permanent: {e}")
#             print("      You may need to add it manually.")
#     else: # macOS and Linux
#         # Suggest adding to shell profile
#         profile_file = ""
#         shell = os.environ.get("SHELL", "")
#         if "bash" in shell: profile_file = "~/.bashrc"
#         elif "zsh" in shell: profile_file = "~/.zshrc"
#         else: profile_file = "~/.profile"
#         print(f"   To make this change permanent, add the following to your {profile_file}:")
#         print(f'   export PATH="{directory}:$PATH"')

# def verify_gh_installation() -> bool:
#     """Verify gh is properly installed and in PATH"""
#     if not shutil.which("gh"):
#         return False
#     try:
#         result = subprocess.run(["gh", "--version"], check=True, capture_output=True, text=True)
#         print(f"✅ GitHub CLI successfully installed: {result.stdout.splitlines()[0]}")
#         return True
#     except (subprocess.CalledProcessError, FileNotFoundError):
#         return False

# def check_and_install_gh() -> bool:
#     """Main function to check and install GitHub CLI, WITH USER PROMPT."""
#     if check_gh_installed():
#         return True
    
#     # --- ADDED USER PROMPT ---
#     print("\n❓ GitHub CLI (gh) is required for this feature but is not installed.", file=sys.stderr)
#     try:
#         answer = input("   Would you like this tool to attempt an automatic installation? (y/n): ").lower().strip()
#         if answer != 'y':
#             print("\n❌ Installation cancelled by user. Please install gh manually from https://cli.github.com/")
#             return False
#     except (EOFError, KeyboardInterrupt):
#         print("\n❌ Installation cancelled by user.")
#         return False
    
#     if not install_gh_cli():
#         print("\n❌ Failed to install GitHub CLI automatically. Please try manual installation:")
#         print("   Visit https://github.com/cli/cli#installation for instructions.")
#         return False
    
#     # After installation, a PATH refresh might be needed
#     if not check_gh_installed():
#         print("\n‼️ IMPORTANT: Installation completed, but GitHub CLI is not yet available in this terminal session.")
#         print("   Please open a NEW terminal and run your command again.")
#         return False
    
#     return True


# # --- Core Tool Functions ---

# def gh_authenticated():
#     """Check if user is authenticated with GitHub CLI"""
#     try:
#         result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=True)
#         return "Logged in to github.com" in result.stderr
#     except (subprocess.CalledProcessError, FileNotFoundError):
#         return False


# def is_local_ahead() -> bool:
#     try:
#         result = subprocess.run(
#             ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
#             capture_output=True, text=True, check=True
#         )
#         behind_ahead = result.stdout.strip().split()
#         if len(behind_ahead) == 2:
#             behind, ahead = map(int, behind_ahead)
#             return ahead > 0
#         return False
#     except subprocess.CalledProcessError:
#         return False


# def authenticate_with_gh():
#     """Authenticate user with GitHub CLI"""
#     print("\n🔑 GitHub authentication required.")
#     print("The tool will use the GitHub CLI (gh) to open a browser for secure login.")
    
#     try:
#         subprocess.run(["gh", "auth", "login", "--web", "-h", "github.com"], check=True)
#         return True
#     except subprocess.CalledProcessError:
#         print("❌ Authentication failed. Please try running 'gh auth login' manually.", file=sys.stderr)
#         return False

# def initialize_git_repository():
#     """Initialize git repository if not already initialized"""
#     if os.path.exists(".git"):
#         return False
        
#     print("🛠 Initializing git repository")
#     try:
#         subprocess.run(["git", "init"], check=True, capture_output=True)
#         subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        
#         if not os.path.exists(".gitignore"):
#             with open(".gitignore", "w") as f:
#                 f.write("""# Python
# __pycache__/
# *.py[cod]
# *.so
# .Python
# env/
# venv/
# .env

# # IDE
# .vscode/
# .idea/
# *.swp
# *.swo

# # System
# .DS_Store
# Thumbs.db

# # Project specific
# *.log
# *.tmp
# *.bak
# """)
#             print("📁 Created .gitignore file")
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Failed to initialize Git repository: {e.stderr.decode(errors='ignore').strip()}", file=sys.stderr)
#         return False

# def create_initial_commit(commit_message="Initial commit"):
#     """Create initial commit if no commits exist"""
#     try:
#         result = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True)
#         commit_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
#         if commit_count == 0:
#             print("📦 Creating initial commit")
#             subprocess.run(["git", "add", "."], check=True)
#             subprocess.run(["git", "commit", "-m", commit_message], check=True)
#             return True
#         return False
#     except subprocess.CalledProcessError as e:
#         error_output = e.stderr.decode(errors='ignore').strip()
#         if "nothing to commit" in error_output:
#              print(f"❌ Failed to create initial commit: No files found to commit.", file=sys.stderr)
#              print("➡️  Add some files to your project directory before creating a repository.", file=sys.stderr)
#         else:
#              print(f"❌ Failed to create initial commit: {error_output}", file=sys.stderr)
#         return False

# def create_with_gh_cli(repo_name, private=False, description="", commit_message="Initial commit"):
#     """Create and push to new repository using GitHub CLI"""
#     try:
#         if not os.path.exists(".git"):
#             if not initialize_git_repository():
#                 return False
        
#         if not create_initial_commit(commit_message):
#             if subprocess.run(["git", "status"], capture_output=True).returncode != 0:
#                  return False
#             print("ℹ️ Using existing commits")

#         private_flag = "--private" if private else "--public"
#         cmd = ["gh", "repo", "create", repo_name, private_flag, "--source=.", "--remote=origin", "--push"]
#         if description: cmd.extend(["--description", description])
        
#         print("🚀 Creating repository and pushing code...")
#         process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
#         repo_url = process.stderr.strip()
#         print(f"✅ Successfully created repository: {repo_url}")
#         return True
#     except subprocess.CalledProcessError as e:
#         error_message = e.stderr.strip()
#         if "already exists" in error_message:
#             print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
#             print("➡️  Please choose a different repository name.", file=sys.stderr)
#         else:
#             print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
#         return False
#     except Exception as e:
#         print(f"❌ An unexpected error occurred: {str(e)}", file=sys.stderr)
#         return False

# def standard_git_push(commit_message, branch, remote, force=False, tags=False):
#     """Handle standard git push operations"""
#     try:
#         subprocess.run(["git", "add", "."], check=True)
        
#         if commit_message:
#             print(f"📦 Committing with message: '{commit_message}'")
#             subprocess.run(["git", "commit", "-m", commit_message, "--allow-empty-message"], check=True)
#         else:
#             print("ℹ️ No commit message provided. Pushing only staged changes.")
        
#         if is_local_ahead():
#             push_cmd = ["git", "push"]
#         else:
#             push_cmd = ["git", "push", "origin", "main"]

#         if force:
#             push_cmd.append("--force-with-lease")
#             print("⚠️ Using safe force push (--force-with-lease).")
#         if tags:
#             push_cmd.append("--tags")
#         if remote and branch:
#             push_cmd.extend([remote, branch])
        
#         print(f"🚀 Executing: {' '.join(push_cmd)}")
#         subprocess.run(push_cmd, check=True)
#         print("✅ Successfully pushed changes.")
#         return True

#     except subprocess.CalledProcessError as e:
#         error_output = e.stderr.decode(errors='ignore').strip() if e.stderr else str(e)

#         if "nothing to commit" in error_output:
#             print("ℹ️ No changes to commit. Nothing to do.")
#             return True

#         if "non-fast-forward" in error_output.lower():
#             print("\n❗ Detected non-fast-forward issue. Attempting rebase...")
#             if attempt_rebase(remote, branch):
#                 print("🔁 Retrying push after rebase...")
#                 return standard_git_push(commit_message, branch, remote, force, tags)
#             else:
#                 print("❌ Rebase failed. Please resolve conflicts manually and re-run the push.")
#                 return False

#         print(f"❌ Push failed: {error_output}", file=sys.stderr)
#         return False



# def has_incoming_changes(remote: str = "origin", branch: str = "main") -> bool:
#     try:
#         subprocess.run(["git", "fetch", remote], check=True, capture_output=True)

#         result = subprocess.run(
#             ["git", "rev-list", "--left-right", "--count", f"{remote}/{branch}...{branch}"],
#             check=True, capture_output=True, text=True
#         )
#         behind_ahead = result.stdout.strip().split()
#         if len(behind_ahead) == 2:
#             behind, ahead = map(int, behind_ahead)
#             return behind > 0
#         return False
#     except subprocess.CalledProcessError:
#         return False


# def pull_and_check_conflicts(remote: str = "origin", branch: str = "main") -> bool:
#     print("🔄 Pulling latest changes before pushing...")

#     try:
#         result = subprocess.run(["git", "pull", remote, branch], capture_output=True, text=True)

#         if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
#             print("❗ Merge conflicts detected.")
#             return True
#         else:
#             print("✅ Pulled successfully. No conflicts.")
#             return False
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Pull failed: {e.stderr or str(e)}", file=sys.stderr)
#         return True



# def show_merge_conflict_details():
#     print("\n🔍 Merge Conflict Report:\n")

#     try:
#         result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True, check=True)
#         conflicted_files = result.stdout.strip().splitlines()

#         if not conflicted_files:
#             print("✅ No merge conflicts found.")
#             return

#         for file in conflicted_files:
#             print(f"📄 File: {file}")
#             try:
#                 with open(file, 'r', encoding='utf-8') as f:
#                     lines = f.readlines()
#                     for i, line in enumerate(lines):
#                         if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
#                             marker = line.strip()
#                             print(f"   ⚠️  Conflict Marker ({marker}) at line {i + 1}")
#             except Exception as e:
#                 print(f"   ❌ Could not read file {file}: {str(e)}")

#     except subprocess.CalledProcessError as e:
#         print(f"❌ Could not retrieve conflicted files: {str(e)}")


# def attempt_rebase(remote: str, branch: str) -> bool:
#     print("🔁 Attempting: git pull --rebase")
#     try:
#         subprocess.run(["git", "pull", "--rebase", remote, branch], check=True)
#         print("✅ Rebase completed successfully.")
#         return True
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Rebase failed: {e.stderr.decode(errors='ignore') if e.stderr else str(e)}")
#         show_merge_conflict_details()
#         return False


# def get_git_sync_status(remote: str = "origin", branch: str = "main") -> tuple[str, int, int]:
#     """
#     Returns a tuple (status, behind, ahead) where status is one of:
#     'ahead', 'behind', 'diverged', 'synced'
#     """
#     try:
#         subprocess.run(["git", "fetch", remote], check=True, capture_output=True)
#         result = subprocess.run(
#             ["git", "rev-list", "--left-right", "--count", f"{remote}/{branch}...{branch}"],
#             capture_output=True, text=True, check=True
#         )
#         behind_str, ahead_str = result.stdout.strip().split()
#         behind, ahead = int(behind_str), int(ahead_str)

#         if behind > 0 and ahead > 0:
#             return "diverged", behind, ahead
#         elif ahead > 0:
#             return "ahead", behind, ahead
#         elif behind > 0:
#             return "behind", behind, ahead
#         else:
#             return "synced", behind, ahead
#     except subprocess.CalledProcessError:
#         return "unknown", 0, 0


# # --- Main Entry Point ---

# def run():
#     parser = argparse.ArgumentParser(
#         description="🚀 Supercharged Git push tool with GitHub repo creation",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""Examples:
#   Standard push:         gitpush "My new feature"
#   Create new repo:       gitpush "Initial commit" --new-repo my-awesome-project
#   Private repository:    gitpush "Initial commit" --new-repo my-secret-project --private
#   Force push (safe):     gitpush "Rebased feature" --force
#   Initialize only:       gitpush --init
# """
#     )
#     parser.add_argument("commit", nargs="?", help="Commit message (optional if just pushing staged changes).")
#     parser.add_argument("branch", nargs="?", default=None, help="Branch name (defaults to current branch).")
#     parser.add_argument("remote", nargs="?", default="origin", help="Remote name (default: origin).")
#     parser.add_argument("--force", action="store_true", help="Force push with --force-with-lease.")
#     parser.add_argument("--tags", action="store_true", help="Push all tags.")
#     parser.add_argument("--init", action="store_true", help="Initialize a new Git repository and exit.")
#     parser.add_argument("--new-repo", metavar="REPO_NAME", help="Create a new GitHub repository with the given name.")
#     parser.add_argument("--private", action="store_true", help="Make the new repository private.")
#     parser.add_argument("--description", help="Description for the new repository.")

#     args = parser.parse_args()
    
#     target_branch = args.branch
#     if not target_branch:
#         try:
#             branch_result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
#             target_branch = branch_result.stdout.strip()
#         except subprocess.CalledProcessError:
#             target_branch = "main"

#     if args.new_repo:
#         # *** THIS IS THE MAIN FIX: Calling your orchestrator function ***
#         if not check_and_install_gh():
#             sys.exit(1)
        
#         if not gh_authenticated():
#             if not authenticate_with_gh():
#                 sys.exit(1)
        
#         if not create_with_gh_cli(
#             args.new_repo,
#             private=args.private,
#             description=args.description or "",
#             commit_message=args.commit or "Initial commit"
#         ):
#             sys.exit(1)

#     elif args.init:
#         if initialize_git_repository():
#              print("✅ Git repository initialized successfully.")
    
#     else:
#         sync_status, behind, ahead = get_git_sync_status(args.remote, target_branch)
#         print(f"\n📊 Git status: {sync_status.upper()} (Behind: {behind}, Ahead: {ahead})")

#         if sync_status == "behind":
#             print("🔄 Your branch is behind remote. Pulling latest changes...")
#             if pull_and_check_conflicts(args.remote, target_branch):
#                 show_merge_conflict_details()
#                 print("\n❌ Resolve conflicts before pushing.")
#                 sys.exit(1)

#         elif sync_status == "diverged":
#             print("⚠️ Your branch has diverged from remote. Rebase recommended.")
#             if attempt_rebase(args.remote, target_branch):
#                 print("✅ Rebase done. Proceeding to push...")
#             else:
#                 print("❌ Rebase failed. Please resolve manually.")
#                 sys.exit(1)



#         if not standard_git_push(
#             args.commit,
#             target_branch,
#             args.remote,
#             args.force,
#             args.tags
#         ):
#             sys.exit(1)

# if __name__ == "__main__":
#     run()
    
    
    
    
# New code

import os
import argparse
import sys
import subprocess
import shutil
import platform
import json
import tempfile
import urllib.request
from typing import Optional

# --- Installation Orchestrator and Helpers (Your Code, Integrated) ---

def check_gh_installed() -> bool:
    """Check if GitHub CLI is installed with proper verification"""
    if shutil.which("gh"):
        try:
            # Verify gh is actually working
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Found but not working - might be a PATH issue or broken install
            return False
    return False

def install_gh_cli() -> bool:
    """Main installation function with comprehensive error handling"""
    system = platform.system()
    machine = platform.machine().lower()
    
    print("\n🔧 Installing GitHub CLI...")
    print(f"📋 System: {system}, Architecture: {machine}")
    
    try:
        if system == "Windows":
            return install_gh_cli_windows()
        elif system == "Darwin":
            return install_gh_cli_mac()
        elif system == "Linux":
            return install_gh_cli_linux()
        else:
            print(f"❌ Unsupported OS: {system}")
            return False
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        return False

def install_gh_cli_windows() -> bool:
    """Windows installation with multiple fallback methods and PATH management"""
    methods = [
        try_winget_install,
        try_scoop_install,
        try_choco_install,
        try_direct_msi_install,
        try_direct_zip_install
    ]
    
    for method in methods:
        if method():
            if verify_gh_installation():
                return True
        print("   ⚠️ Trying next installation method...")
    
    print("❌ All Windows installation methods failed.")
    return False

def try_winget_install() -> bool:
    """Attempt installation via winget"""
    if not shutil.which("winget"):
        return False
    
    print("\n   🔄 Attempting winget installation...")
    try:
        subprocess.run(
            ["winget", "install", "--id", "GitHub.cli", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ winget failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
        return False

def try_scoop_install() -> bool:
    """Attempt installation via scoop"""
    if not shutil.which("scoop"):
        return False
    
    print("\n   🔄 Attempting scoop installation...")
    try:
        subprocess.run(["scoop", "install", "gh"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ scoop failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
        return False

def try_choco_install() -> bool:
    """Attempt installation via chocolatey"""
    if not shutil.which("choco"):
        return False
    
    print("\n   🔄 Attempting chocolatey installation...")
    try:
        subprocess.run(["choco", "install", "gh", "-y"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ chocolatey failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
        return False

def try_direct_msi_install() -> bool:
    """Direct MSI installation with proper PATH handling"""
    print("\n   🔄 Attempting direct MSI installation...")
    temp_dir = ""
    try:
        release_info = get_github_release_info()
        if not release_info: return False
        
        msi_asset = next((a for a in release_info.get('assets', []) if a['name'].endswith('_windows_amd64.msi')), None)
        if not msi_asset:
            print("   ❌ Could not find Windows MSI installer.")
            return False
            
        temp_dir = tempfile.mkdtemp()
        msi_path = os.path.join(temp_dir, msi_asset['name'])
        print(f"   ⬇️ Downloading {msi_asset['name']}...")
        if not download_file(msi_asset['browser_download_url'], msi_path): return False
        
        print("   🛠 Installing (this may require administrator privileges)...")
        subprocess.run(["msiexec", "/i", msi_path, "/quiet", "/norestart"], check=True)
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        gh_path = os.path.join(program_files, "GitHub CLI", "gh.exe")
        if os.path.exists(gh_path): add_to_path(os.path.dirname(gh_path))
        
        return True
    except Exception as e:
        print(f"   ❌ MSI installation failed: {str(e)}")
        if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def try_direct_zip_install() -> bool:
    """Fallback ZIP installation for Windows"""
    print("\n   🔄 Attempting direct ZIP installation...")
    temp_dir = ""
    try:
        release_info = get_github_release_info()
        if not release_info: return False
        
        zip_asset = next((a for a in release_info.get('assets', []) if a['name'].endswith('windows_amd64.zip')), None)
        if not zip_asset:
            print("   ❌ Could not find Windows ZIP package.")
            return False
            
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, zip_asset['name'])
        print(f"   ⬇️ Downloading {zip_asset['name']}...")
        if not download_file(zip_asset['browser_download_url'], zip_path): return False
        
        print("   📦 Extracting...")
        shutil.unpack_archive(zip_path, temp_dir)
        
        bin_dir = next((root for root, _, files in os.walk(temp_dir) if "gh.exe" in files), None)
        if not bin_dir:
            print("   ❌ Could not find gh.exe in extracted files.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        install_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHubCLI")
        os.makedirs(install_dir, exist_ok=True)
        
        shutil.copytree(bin_dir, install_dir, dirs_exist_ok=True)
        add_to_path(install_dir)
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
    except Exception as e:
        print(f"   ❌ ZIP installation failed: {str(e)}")
        if temp_dir: shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def install_gh_cli_mac() -> bool:
    """macOS installation with multiple methods"""
    if shutil.which("brew"):
        print("\n   🔄 Attempting Homebrew installation...")
        try:
            subprocess.run(["brew", "install", "gh"], check=True, capture_output=True)
            if verify_gh_installation(): return True
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Homebrew failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")
    
    print("❌ All macOS installation methods failed.")
    return False

def install_gh_cli_linux() -> bool:
    """Linux installation with distro detection and multiple methods"""
    package_managers = [
        ("apt-get", "sudo apt-get update && sudo apt-get install -y gh"),
        ("apt", "sudo apt update && sudo apt install -y gh"),
        ("dnf", "sudo dnf install -y gh"),
        ("yum", "sudo yum install -y gh"),
        ("pacman", "sudo pacman -S --noconfirm github-cli"),
        ("zypper", "sudo zypper install -y gh"),
    ]
    for pm, command in package_managers:
        if shutil.which(pm):
            print(f"\n   🔄 Attempting installation via {pm}...")
            try:
                subprocess.run(command, shell=True, check=True, capture_output=True)
                if verify_gh_installation(): return True
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ {pm} failed: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'Unknown error'}")

    print("❌ All Linux package manager installations failed.")
    return False

def get_github_release_info() -> Optional[dict]:
    """Get latest release info from GitHub API"""
    try:
        with urllib.request.urlopen("https://api.github.com/repos/cli/cli/releases/latest") as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"   ❌ Failed to get release info from GitHub API: {str(e)}")
        return None

def download_file(url: str, path: str) -> bool:
    """Download a file with progress reporting"""
    try:
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r      Downloading... {percent}%")
                sys.stdout.flush()
            
        urllib.request.urlretrieve(url, path, reporthook=reporthook)
        sys.stdout.write("\r      Downloading... 100%\n")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"\n   ❌ Download failed: {str(e)}")
        return False

def add_to_path(directory: str):
    """Add directory to PATH for the current session and try to make it permanent."""
    print(f"   ✅ Adding {directory} to PATH...")
    os.environ["PATH"] = f"{directory}{os.pathsep}{os.environ['PATH']}"
    
    if platform.system() == "Windows":
        try:
            # This makes the PATH change permanent for the current user
            subprocess.run(
                f'setx PATH "%PATH%;{directory}"',
                shell=True, check=True, capture_output=True
            )
        except Exception as e:
            print(f"   ⚠️ Could not make PATH change permanent: {e}")
            print("      You may need to add it manually.")
    else: # macOS and Linux
        # Suggest adding to shell profile
        profile_file = ""
        shell = os.environ.get("SHELL", "")
        if "bash" in shell: profile_file = "~/.bashrc"
        elif "zsh" in shell: profile_file = "~/.zshrc"
        else: profile_file = "~/.profile"
        print(f"   To make this change permanent, add the following to your {profile_file}:")
        print(f'   export PATH="{directory}:$PATH"')

def verify_gh_installation() -> bool:
    """Verify gh is properly installed and in PATH"""
    if not shutil.which("gh"):
        return False
    try:
        result = subprocess.run(["gh", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ GitHub CLI successfully installed: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_and_install_gh() -> bool:
    """Main function to check and install GitHub CLI, WITH USER PROMPT."""
    if check_gh_installed():
        return True
    
    # --- ADDED USER PROMPT ---
    print("\n❓ GitHub CLI (gh) is required for this feature but is not installed.", file=sys.stderr)
    try:
        answer = input("   Would you like this tool to attempt an automatic installation? (y/n): ").lower().strip()
        if answer != 'y':
            print("\n❌ Installation cancelled by user. Please install gh manually from https://cli.github.com/")
            return False
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Installation cancelled by user.")
        return False
    
    if not install_gh_cli():
        print("\n❌ Failed to install GitHub CLI automatically. Please try manual installation:")
        print("   Visit https://github.com/cli/cli#installation for instructions.")
        return False
    
    # After installation, a PATH refresh might be needed
    if not check_gh_installed():
        print("\n‼️ IMPORTANT: Installation completed, but GitHub CLI is not yet available in this terminal session.")
        print("   Please open a NEW terminal and run your command again.")
        return False
    
    return True


# --- Core Tool Functions ---

def gh_authenticated() -> bool:
    """
    Check if user is authenticated with github.com using the recommended gh command.
    This is the most reliable way to check, as it uses the exit code, not text parsing.
    """
    # `gh auth status -h github.com` exits with 0 if logged in to that host, 1 otherwise.
    try:
        subprocess.run(
            ["gh", "auth", "status", "-h", "github.com"],
            check=True,
            capture_output=True  # Suppress command output from user's terminal
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # CalledProcessError means exit code != 0 (not logged in).
        # FileNotFoundError means 'gh' is not installed.
        return False


def is_local_ahead() -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
            capture_output=True, text=True, check=True
        )
        behind_ahead = result.stdout.strip().split()
        if len(behind_ahead) == 2:
            behind, ahead = map(int, behind_ahead)
            return ahead > 0
        return False
    except subprocess.CalledProcessError:
        return False


def authenticate_with_gh() -> bool:
    """
    Authenticate user with GitHub CLI, ensuring correct permissions for creating repos.
    """
    print("\n🔑 GitHub authentication required.")
    print("The tool will use the GitHub CLI (gh) to open a browser for secure login.")
    print("You may be asked to grant permissions for this tool to create repositories.")
    
    try:
        # We explicitly request the 'repo' scope to ensure we can create repositories.
        # `gh` is smart and will just verify if the scope already exists on the token.
        subprocess.run(
            ["gh", "auth", "login", "--web", "-h", "github.com", "-s", "repo"], 
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print("❌ Authentication failed. Please try running 'gh auth login -s repo' manually.", file=sys.stderr)
        return False

def initialize_git_repository():
    """Initialize git repository if not already initialized"""
    if os.path.exists(".git"):
        return False
        
    print("🛠 Initializing git repository")
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        
        if not os.path.exists(".gitignore"):
            with open(".gitignore", "w") as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# System
.DS_Store
Thumbs.db

# Project specific
*.log
*.tmp
*.bak
""")
            print("📁 Created .gitignore file")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize Git repository: {e.stderr.decode(errors='ignore').strip()}", file=sys.stderr)
        return False

def create_initial_commit(commit_message="Initial commit"):
    """Create initial commit if no commits exist"""
    try:
        result = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True)
        commit_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
        if commit_count == 0:
            print("📦 Creating initial commit")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            return True
        return False
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode(errors='ignore').strip()
        if "nothing to commit" in error_output:
             print(f"❌ Failed to create initial commit: No files found to commit.", file=sys.stderr)
             print("➡️  Add some files to your project directory before creating a repository.", file=sys.stderr)
        else:
             print(f"❌ Failed to create initial commit: {error_output}", file=sys.stderr)
        return False

def create_with_gh_cli(repo_name, private=False, description="", commit_message="Initial commit"):
    """Create and push to new repository using GitHub CLI"""
    try:
        if not os.path.exists(".git"):
            if not initialize_git_repository():
                return False
        
        if not create_initial_commit(commit_message):
            if subprocess.run(["git", "status"], capture_output=True).returncode != 0:
                 return False
            print("ℹ️ Using existing commits")

        private_flag = "--private" if private else "--public"
        cmd = ["gh", "repo", "create", repo_name, private_flag, "--source=.", "--remote=origin", "--push"]
        if description: cmd.extend(["--description", description])
        
        print("🚀 Creating repository and pushing code...")
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        repo_url = process.stderr.strip()
        print(f"✅ Successfully created repository: {repo_url}")
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "already exists" in error_message:
            print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
            print("➡️  Please choose a different repository name.", file=sys.stderr)
        else:
            print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}", file=sys.stderr)
        return False

def standard_git_push(commit_message, branch, remote, force=False, tags=False):
    """Handle standard git push operations"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        if commit_message:
            print(f"📦 Committing with message: '{commit_message}'")
            subprocess.run(["git", "commit", "-m", commit_message, "--allow-empty-message"], check=True)
        else:
            print("ℹ️ No commit message provided. Pushing only staged changes.")
        
        if is_local_ahead():
            push_cmd = ["git", "push"]
        else:
            push_cmd = ["git", "push", "origin", "main"]

        if force:
            push_cmd.append("--force-with-lease")
            print("⚠️ Using safe force push (--force-with-lease).")
        if tags:
            push_cmd.append("--tags")
        if remote and branch:
            push_cmd.extend([remote, branch])
        
        print(f"🚀 Executing: {' '.join(push_cmd)}")
        subprocess.run(push_cmd, check=True)
        print("✅ Successfully pushed changes.")
        return True

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode(errors='ignore').strip() if e.stderr else str(e)

        if "nothing to commit" in error_output:
            print("ℹ️ No changes to commit. Nothing to do.")
            return True

        if "non-fast-forward" in error_output.lower():
            print("\n❗ Detected non-fast-forward issue. Attempting rebase...")
            if attempt_rebase(remote, branch):
                print("🔁 Retrying push after rebase...")
                return standard_git_push(commit_message, branch, remote, force, tags)
            else:
                print("❌ Rebase failed. Please resolve conflicts manually and re-run the push.")
                return False

        print(f"❌ Push failed: {error_output}", file=sys.stderr)
        return False



def has_incoming_changes(remote: str = "origin", branch: str = "main") -> bool:
    try:
        subprocess.run(["git", "fetch", remote], check=True, capture_output=True)

        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"{remote}/{branch}...{branch}"],
            check=True, capture_output=True, text=True
        )
        behind_ahead = result.stdout.strip().split()
        if len(behind_ahead) == 2:
            behind, ahead = map(int, behind_ahead)
            return behind > 0
        return False
    except subprocess.CalledProcessError:
        return False


def pull_and_check_conflicts(remote: str = "origin", branch: str = "main") -> bool:
    print("🔄 Pulling latest changes before pushing...")

    try:
        result = subprocess.run(["git", "pull", remote, branch], capture_output=True, text=True)

        if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
            print("❗ Merge conflicts detected.")
            return True
        else:
            print("✅ Pulled successfully. No conflicts.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Pull failed: {e.stderr or str(e)}", file=sys.stderr)
        return True



def show_merge_conflict_details():
    print("\n🔍 Merge Conflict Report:\n")

    try:
        result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True, check=True)
        conflicted_files = result.stdout.strip().splitlines()

        if not conflicted_files:
            print("✅ No merge conflicts found.")
            return

        for file in conflicted_files:
            print(f"📄 File: {file}")
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
                            marker = line.strip()
                            print(f"   ⚠️  Conflict Marker ({marker}) at line {i + 1}")
            except Exception as e:
                print(f"   ❌ Could not read file {file}: {str(e)}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Could not retrieve conflicted files: {str(e)}")


def attempt_rebase(remote: str, branch: str) -> bool:
    print("🔁 Attempting: git pull --rebase")
    try:
        subprocess.run(["git", "pull", "--rebase", remote, branch], check=True)
        print("✅ Rebase completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Rebase failed: {e.stderr.decode(errors='ignore') if e.stderr else str(e)}")
        show_merge_conflict_details()
        return False


def get_git_sync_status(remote: str = "origin", branch: str = "main") -> tuple[str, int, int]:
    """
    Returns a tuple (status, behind, ahead) where status is one of:
    'ahead', 'behind', 'diverged', 'synced'
    """
    try:
        subprocess.run(["git", "fetch", remote], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"{remote}/{branch}...{branch}"],
            capture_output=True, text=True, check=True
        )
        behind_str, ahead_str = result.stdout.strip().split()
        behind, ahead = int(behind_str), int(ahead_str)

        if behind > 0 and ahead > 0:
            return "diverged", behind, ahead
        elif ahead > 0:
            return "ahead", behind, ahead
        elif behind > 0:
            return "behind", behind, ahead
        else:
            return "synced", behind, ahead
    except subprocess.CalledProcessError:
        return "unknown", 0, 0


# --- Main Entry Point ---

def run():
    parser = argparse.ArgumentParser(
        description="🚀 Supercharged Git push tool with GitHub repo creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  Standard push:         gitpush "My new feature"
  Create new repo:       gitpush "Initial commit" --new-repo my-awesome-project
  Private repository:    gitpush "Initial commit" --new-repo my-secret-project --private
  Force push (safe):     gitpush "Rebased feature" --force
  Initialize only:       gitpush --init
"""
    )
    parser.add_argument("commit", nargs="?", help="Commit message (optional if just pushing staged changes).")
    parser.add_argument("branch", nargs="?", default=None, help="Branch name (defaults to current branch).")
    parser.add_argument("remote", nargs="?", default="origin", help="Remote name (default: origin).")
    parser.add_argument("--force", action="store_true", help="Force push with --force-with-lease.")
    parser.add_argument("--tags", action="store_true", help="Push all tags.")
    parser.add_argument("--init", action="store_true", help="Initialize a new Git repository and exit.")
    parser.add_argument("--new-repo", metavar="REPO_NAME", help="Create a new GitHub repository with the given name.")
    parser.add_argument("--private", action="store_true", help="Make the new repository private.")
    parser.add_argument("--description", help="Description for the new repository.")

    args = parser.parse_args()
    
    target_branch = args.branch
    if not target_branch:
        try:
            branch_result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
            target_branch = branch_result.stdout.strip()
        except subprocess.CalledProcessError:
            target_branch = "main"

    if args.new_repo:
        # Check for gh CLI and prompt for installation if missing
        if not check_and_install_gh():
            sys.exit(1)
        
        # Check for authentication status reliably.
        if not gh_authenticated():
            # If not authenticated, run the login flow.
            if not authenticate_with_gh():
                sys.exit(1)
        
        if not create_with_gh_cli(
            args.new_repo,
            private=args.private,
            description=args.description or "",
            commit_message=args.commit or "Initial commit"
        ):
            sys.exit(1)

    elif args.init:
        if initialize_git_repository():
             print("✅ Git repository initialized successfully.")
    
    else:
        sync_status, behind, ahead = get_git_sync_status(args.remote, target_branch)
        print(f"\n📊 Git status: {sync_status.upper()} (Behind: {behind}, Ahead: {ahead})")

        if sync_status == "behind":
            print("🔄 Your branch is behind remote. Pulling latest changes...")
            if pull_and_check_conflicts(args.remote, target_branch):
                show_merge_conflict_details()
                print("\n❌ Resolve conflicts before pushing.")
                sys.exit(1)

        elif sync_status == "diverged":
            print("⚠️ Your branch has diverged from remote. Rebase recommended.")
            if attempt_rebase(args.remote, target_branch):
                print("✅ Rebase done. Proceeding to push...")
            else:
                print("❌ Rebase failed. Please resolve manually.")
                sys.exit(1)



        if not standard_git_push(
            args.commit,
            target_branch,
            args.remote,
            args.force,
            args.tags
        ):
            sys.exit(1)

if __name__ == "__main__":
    run()