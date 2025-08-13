# GitPush Tool 🚀

[![PyPI version](https://img.shields.io/pypi/v/gitpush-tool.svg)](https://pypi.org/project/gitpush-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A supercharged Git CLI tool that simplifies repository creation and pushing with intelligent defaults.

## Features ✨

- **One-command GitHub repo creation**
- **Automatic Git initialization** for new projects
- **Safe force pushing** (`--force-with-lease`)
- **GitHub CLI integration** for secure authentication
- **Fresh project setup** in one command
- **Comprehensive error handling**

## Installation 📦

```bash
pip install gitpush-tool
```


## Usage 🛠️

### Basic Commands

| Command | Description |
|--------|-------------|
| `gitpush "Commit message"` | Standard push with commit |
| `gitpush` | Push without commit (only staged changes) |
| `gitpush --force` | Safe force push |
| `gitpush --tags` | Push all tags |

### New Repository Workflow

```bash
# Create new public repo
gitpush "Initial commit" --new-repo project-name

# Create private repo with description
gitpush "Initial commit" --new-repo private-project --private --description "My awesome project"
```

### Branch Management

```bash
# Push to specific branch
gitpush "Commit message" feature-branch

# Push to specific remote and branch
gitpush "Commit message" main upstream
```

### Initialization

```bash
# Initialize new repo only
gitpush --init
```

## Workflow Examples 🔥

### Scenario 1: Fresh Project Setup

```bash
mkdir my-app
cd my-app
touch README.md main.py
gitpush "Initial commit" --new-repo my-app
```

### Scenario 2: Existing Project Updates

```bash
# After making changes
gitpush "Fixed authentication bug"

# Force push after rebase
gitpush "Rebased commits" --force
```

### Scenario 3: Create Empty Repository

```bash
mkdir empty-project
cd empty-project
gitpush --init
```

## Configuration ⚙️

The tool uses GitHub CLI (gh) for authentication. On first use:

- It will prompt you to authenticate via browser
- Follow the on-screen instructions
- Authentication persists for future uses

## Troubleshooting 🛑

### Common Issues

**Error: GitHub CLI not found**

```bash
❌ GitHub CLI (gh) is not installed
➡️ Install GitHub CLI using the installation guide
```

**Error: Authentication failed**

```bash
❌ Authentication failed
➡️ Run gh auth login separately to debug
```

**Error: No commits found**

```bash
❌ Failed to create initial commit
➡️ Make sure you have files in your directory before pushing
```

**Error: Repository already exists**

```bash
❌ Repository 'my-repo' already exists
➡️ Choose a different repository name or delete the existing one
```

## Advanced Options 🧠

| Option | Description |
|--------|-------------|
| `--private` | Create private repository |
| `--description "TEXT"` | Set repository description |
| `--force` | Force push with lease |
| `--tags` | Include tags in push |
| `--init` | Initialize Git repo only |

## FAQ ❓

**Q: Can I use this with existing repositories?**  
A: Yes! It works normally with existing repos like regular git push.

**Q: How is this different from regular Git?**  
A: It automates the tedious setup (init, first commit, remote creation) and provides safer defaults.

**Q: Can I customize the .gitignore?**  
A: Yes! The tool creates a basic .gitignore but you can modify it afterward.

## Contributing 🤝

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License 📄

MIT - See LICENSE for details.   

<center>✨ <strong>Happy Coding!</strong> ✨</center>
