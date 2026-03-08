"""Storage module for managing account data."""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


STORAGE_DIR = Path.home() / ".githubhacker"
ACCOUNTS_FILE = STORAGE_DIR / "accounts.json"


def _ensure_storage_dir() -> None:
    """Ensure the storage directory exists."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def load_accounts() -> Dict[str, dict]:
    """Load all accounts from storage."""
    _ensure_storage_dir()
    if not ACCOUNTS_FILE.exists():
        return {}
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_accounts(accounts: Dict[str, dict]) -> None:
    """Save all accounts to storage."""
    _ensure_storage_dir()
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)


def get_account(name: str) -> Optional[dict]:
    """Get a single account by name."""
    accounts = load_accounts()
    return accounts.get(name)


def add_account(name: str, token: str, username: str) -> None:
    """Add or update an account."""
    accounts = load_accounts()
    accounts[name] = {
        "token": token,
        "username": username,
    }
    save_accounts(accounts)


def remove_account(name: str) -> bool:
    """Remove an account by name. Returns True if removed."""
    accounts = load_accounts()
    if name in accounts:
        del accounts[name]
        save_accounts(accounts)
        return True
    return False


def list_accounts() -> List[dict]:
    """List all accounts."""
    accounts = load_accounts()
    return [
        {"name": name, "username": data.get("username")}
        for name, data in accounts.items()
    ]
