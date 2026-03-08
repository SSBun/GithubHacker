# GitHub Hacker

A CLI tool to manage multiple GitHub accounts for batch operations like starring, watching, and forking repositories.

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

```bash
# Clone the repository
git clone https://github.com/yourusername/GithubHacker.git
cd GithubHacker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Login with GitHub Account

```bash
python main.py login myaccount YOUR_GITHUB_TOKEN
```

### List Accounts

```bash
python main.py config list
```

### Star a Repository (All Accounts)

```bash
python main.py star owner/repo
# Or use full URL
python main.py star https://github.com/owner/repo
```

### Star with Specific Account

```bash
python main.py star owner/repo -a myaccount
```

## Commands

### Account Management

```bash
# Add account
python main.py login <name> <token>

# Remove account
python main.py logout <name>

# List accounts
python main.py config list

# Export accounts to JSON
python main.py config export accounts.json

# Import accounts from JSON
python main.py config import accounts.json

# Validate all tokens
python main.py config validate

# Show account info
python main.py config whoami
```

### Repository Operations

```bash
# Star a repository
python main.py star <repo>
python main.py star <repo> -a <account>

# Unstar a repository
python main.py unstar <repo>

# Watch a repository (notifications)
python main.py watch <repo>

# Unwatch a repository
python main.py unwatch <repo>

# Fork a repository
python main.py fork <repo>

# Check status (starred/watched)
python main.py status <repo>

# Show repository info
python main.py info <repo>
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
