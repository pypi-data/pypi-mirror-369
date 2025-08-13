"""
GitPush Tool - Supercharged Git CLI (v0.2.0)

A powerful command-line tool that simplifies Git operations with automatic GitHub repository creation.

Key Features:
• One-command GitHub repo creation
• Automatic Git initialization
• Safe force pushing (--force-with-lease)
• GitHub CLI integration
• Fresh project setup in one command

Basic Usage:
  gitpush "Commit message"              # Standard push
  gitpush --new-repo project-name       # Create new repo
  gitpush --force                       # Safe force push

Install GitHub CLI first:
  macOS: brew install gh
  Windows: winget install GitHub.cli
  Linux: sudo apt install gh

Documentation: https://github.com/inevitablegs/gitpush
Issues: https://github.com/inevitablegs/gitpush/issues
"""