# GitHub Hacker

A CLI tool to manage multiple GitHub accounts for batch operations like starring, watching, and forking repositories.

**Official Website**: https://ssbun.github.io/GithubHacker

## Features

- **Multi-account Management**: Login, logout, and manage multiple GitHub accounts
- **Batch Operations**: Perform operations with all accounts at once
- **Repository Operations**:
  - Star/Unstar repositories
  - Watch/Unwatch repositories (subscribe to notifications)
  - Fork repositories
  - Check status (starred/watched)
  - View repository information
- **Config Management**: Import/export account data in JSON format

## Installation

### Option 1: Install with pip (recommended)

```bash
pip install github-hacker
```

### Option 2: Install from source (for development)

```bash
# Clone the repository
git clone https://github.com/SSBun/GithubHacker.git
cd GithubHacker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .
```

After installation, use the `github-hacker` command:

```bash
github-hacker --help
```

## Quick Start

### Login with GitHub Account

```bash
github-hacker login myaccount YOUR_GITHUB_TOKEN
```

### List Accounts

```bash
github-hacker config list
```

### Star a Repository (All Accounts)

```bash
github-hacker star owner/repo
# Or use full URL
github-hacker star https://github.com/owner/repo
```

### Star with Specific Account

```bash
github-hacker star owner/repo -a myaccount
```

## Commands

### Account Management

```bash
# Add account
github-hacker login <name> <token>

# Remove account
github-hacker logout <name>

# List accounts
github-hacker config list

# Export accounts to JSON
github-hacker config export accounts.json

# Import accounts from JSON
github-hacker config import accounts.json

# Validate all tokens
github-hacker config validate

# Show account info
github-hacker config whoami
```

### Repository Operations

```bash
# Star a repository
github-hacker star <repo>
github-hacker star <repo> -a <account>

# Unstar a repository
github-hacker unstar <repo>

# Watch a repository (notifications)
github-hacker watch <repo>

# Unwatch a repository
github-hacker unwatch <repo>

# Fork a repository
github-hacker fork <repo>

# Check status (starred/watched)
github-hacker status <repo>

# Show repository info
github-hacker info <repo>
```

## Supported Repository Formats

Both formats are supported:
- Short format: `owner/repo`
- Full URL: `https://github.com/owner/repo`

## JSON Account Format

When importing/exporting accounts, use this format:

```json
{
  "myaccount": {
    "token": "ghp_xxxxxxxxxxxx",
    "username": "githubuser"
  }
}
```

## Getting a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the `repo` scope for full access
4. Copy the generated token

## License

MIT
