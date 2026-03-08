"""Account manager for GitHub accounts."""
import re
from dataclasses import dataclass
from typing import List, Callable

from github import Github

from .github_client import get_user, star_repo, unstar_repo, watch_repo, unwatch_repo, check_repo_status, fork_repo, get_repo_info
from . import storage


@dataclass
class StarResult:
    """Result of starring a repository."""
    account_name: str
    success: bool
    error: str | None = None


@dataclass
class StatusResult:
    """Result of checking repository status."""
    account_name: str
    username: str
    starred: bool
    watched: bool
    error: str | None = None


# Callback type for progress updates: (current: int, total: int, account_name: str, success: bool)
ProgressCallback = Callable[[int, int, str, bool], None]


def parse_repo(input_str: str) -> str:
    """
    Parse repository from various input formats.

    Supports:
    - owner/repo
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - http://github.com/owner/repo

    Args:
        input_str: Repository URL or owner/repo

    Returns:
        Owner/repo format

    Raises:
        ValueError: If input format is invalid
    """
    # Already in owner/repo format
    if "/" in input_str and not input_str.startswith("http"):
        # Verify it's owner/repo (no protocol)
        return input_str.strip()

    # Try to parse as URL
    patterns = [
        r"github\.com[/:]([^/]+)/([^/.]+)(?:\.git)?$",
        r"github\.com[/:]([^/]+)/([^/]+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return f"{match.group(1)}/{match.group(2)}"

    raise ValueError(f"Invalid repository format: {input_str}. Use 'owner/repo' or 'https://github.com/owner/repo'")


def login(name: str, token: str) -> str:
    """
    Add a new GitHub account.

    Args:
        name: Alias for the account
        token: GitHub personal access token

    Returns:
        The GitHub username

    Raises:
        ValueError: If token is invalid
    """
    username = get_user(token)
    storage.add_account(name, token, username)
    return username


def logout(name: str) -> bool:
    """
    Remove a GitHub account.

    Args:
        name: Alias for the account

    Returns:
        True if account was removed, False if not found
    """
    return storage.remove_account(name)


def list_accounts() -> List[dict]:
    """
    List all saved accounts.

    Returns:
        List of account info (name, username)
    """
    return storage.list_accounts()


def star(account_name: str | None, repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StarResult]:
    """
    Star a repository using saved account(s).

    Args:
        account_name: Alias of the account to use, or None for all accounts
        repo_input: Repository in any format (owner/repo or URL)
        progress_callback: Optional callback for progress updates (current, total, account_name, success)

    Returns:
        List of StarResult for each account

    Raises:
        ValueError: If no accounts found or star fails
    """
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StarResult] = []
    total = 1 if account_name else len(accounts)
    current = 0

    if account_name:
        account = storage.get_account(account_name)
        if not account:
            raise ValueError(f"Account not found: {account_name}")
        current = 1
        try:
            star_repo(account["token"], repo_full_name)
            results.append(StarResult(account_name=account_name, success=True))
            if progress_callback:
                progress_callback(1, 1, account_name, True)
        except ValueError as e:
            results.append(StarResult(account_name=account_name, success=False, error=str(e)))
            if progress_callback:
                progress_callback(1, 1, account_name, False)
    else:
        # Use all accounts
        for acc in accounts:
            current += 1
            try:
                full_acc = storage.get_account(acc["name"])
                if full_acc:
                    star_repo(full_acc["token"], repo_full_name)
                    results.append(StarResult(account_name=acc["name"], success=True))
                    if progress_callback:
                        progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StarResult(account_name=acc["name"], success=False, error=str(e)))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def unstar(account_name: str | None, repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StarResult]:
    """
    Unstar a repository using saved account(s).

    Args:
        account_name: Alias of the account to use, or None for all accounts
        repo_input: Repository in any format (owner/repo or URL)
        progress_callback: Optional callback for progress updates (current, total, account_name, success)

    Returns:
        List of StarResult for each account

    Raises:
        ValueError: If no accounts found or unstar fails
    """
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StarResult] = []
    total = 1 if account_name else len(accounts)
    current = 0

    if account_name:
        account = storage.get_account(account_name)
        if not account:
            raise ValueError(f"Account not found: {account_name}")
        current = 1
        try:
            unstar_repo(account["token"], repo_full_name)
            results.append(StarResult(account_name=account_name, success=True))
            if progress_callback:
                progress_callback(1, 1, account_name, True)
        except ValueError as e:
            results.append(StarResult(account_name=account_name, success=False, error=str(e)))
            if progress_callback:
                progress_callback(1, 1, account_name, False)
    else:
        # Use all accounts
        for acc in accounts:
            current += 1
            try:
                full_acc = storage.get_account(acc["name"])
                if full_acc:
                    unstar_repo(full_acc["token"], repo_full_name)
                    results.append(StarResult(account_name=acc["name"], success=True))
                    if progress_callback:
                        progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StarResult(account_name=acc["name"], success=False, error=str(e)))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def watch(account_name: str | None, repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StarResult]:
    """Watch a repository using saved account(s)."""
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StarResult] = []
    total = 1 if account_name else len(accounts)
    current = 0

    if account_name:
        account = storage.get_account(account_name)
        if not account:
            raise ValueError(f"Account not found: {account_name}")
        current = 1
        try:
            watch_repo(account["token"], repo_full_name)
            results.append(StarResult(account_name=account_name, success=True))
            if progress_callback:
                progress_callback(1, 1, account_name, True)
        except ValueError as e:
            results.append(StarResult(account_name=account_name, success=False, error=str(e)))
            if progress_callback:
                progress_callback(1, 1, account_name, False)
    else:
        for acc in accounts:
            current += 1
            try:
                full_acc = storage.get_account(acc["name"])
                if full_acc:
                    watch_repo(full_acc["token"], repo_full_name)
                    results.append(StarResult(account_name=acc["name"], success=True))
                    if progress_callback:
                        progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StarResult(account_name=acc["name"], success=False, error=str(e)))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def unwatch(account_name: str | None, repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StarResult]:
    """Unwatch a repository using saved account(s)."""
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StarResult] = []
    total = 1 if account_name else len(accounts)
    current = 0

    if account_name:
        account = storage.get_account(account_name)
        if not account:
            raise ValueError(f"Account not found: {account_name}")
        current = 1
        try:
            unwatch_repo(account["token"], repo_full_name)
            results.append(StarResult(account_name=account_name, success=True))
            if progress_callback:
                progress_callback(1, 1, account_name, True)
        except ValueError as e:
            results.append(StarResult(account_name=account_name, success=False, error=str(e)))
            if progress_callback:
                progress_callback(1, 1, account_name, False)
    else:
        for acc in accounts:
            current += 1
            try:
                full_acc = storage.get_account(acc["name"])
                if full_acc:
                    unwatch_repo(full_acc["token"], repo_full_name)
                    results.append(StarResult(account_name=acc["name"], success=True))
                    if progress_callback:
                        progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StarResult(account_name=acc["name"], success=False, error=str(e)))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def status(repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StatusResult]:
    """
    Check star and watch status for a repository across all accounts.

    Args:
        repo_input: Repository in any format (owner/repo or URL)
        progress_callback: Optional callback for progress updates (current, total, account_name, success)

    Returns:
        List of StatusResult for each account
    """
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StatusResult] = []
    total = len(accounts)
    current = 0

    for acc in accounts:
        current += 1
        full_acc = storage.get_account(acc["name"])
        if full_acc:
            try:
                status_info = check_repo_status(full_acc["token"], repo_full_name)
                results.append(StatusResult(
                    account_name=acc["name"],
                    username=full_acc.get("username", "unknown"),
                    starred=status_info["starred"],
                    watched=status_info["watched"],
                ))
                if progress_callback:
                    progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StatusResult(
                    account_name=acc["name"],
                    username=full_acc.get("username", "unknown"),
                    starred=False,
                    watched=False,
                    error=str(e),
                ))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def fork(repo_input: str, progress_callback: ProgressCallback | None = None) -> List[StarResult]:
    """
    Fork a repository using saved account(s).

    Args:
        repo_input: Repository in any format (owner/repo or URL)
        progress_callback: Optional callback for progress updates

    Returns:
        List of StarResult for each account
    """
    repo_full_name = parse_repo(repo_input)
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[StarResult] = []
    total = len(accounts)
    current = 0

    for acc in accounts:
        current += 1
        full_acc = storage.get_account(acc["name"])
        if full_acc:
            try:
                fork_name = fork_repo(full_acc["token"], repo_full_name)
                results.append(StarResult(account_name=acc["name"], success=True, error=fork_name))
                if progress_callback:
                    progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append(StarResult(account_name=acc["name"], success=False, error=str(e)))
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results


def get_repo_info_account(account_name: str, repo_input: str) -> dict:
    """
    Get repository information using a specific account.

    Args:
        account_name: Alias of the account to use
        repo_input: Repository in any format (owner/repo or URL)

    Returns:
        Dictionary with repo info

    Raises:
        ValueError: If account not found or query fails
    """
    repo_full_name = parse_repo(repo_input)
    account = storage.get_account(account_name)
    if not account:
        raise ValueError(f"Account not found: {account_name}")
    return get_repo_info(account["token"], repo_full_name)


def whoami(progress_callback: ProgressCallback | None = None) -> List[dict]:
    """
    Get user info for all saved accounts.

    Args:
        progress_callback: Optional callback for progress updates

    Returns:
        List of dicts with user info for each account
    """
    accounts = storage.list_accounts()
    if not accounts:
        raise ValueError("No accounts saved. Use 'login' to add an account first.")

    results: List[dict] = []
    total = len(accounts)
    current = 0

    for acc in accounts:
        current += 1
        full_acc = storage.get_account(acc["name"])
        if full_acc:
            try:
                g = Github(full_acc["token"])
                user = g.get_user()
                results.append({
                    "account_name": acc["name"],
                    "username": user.login,
                    "name": user.name,
                    "email": user.email,
                    "bio": user.bio,
                    "public_repos": user.public_repos,
                    "followers": user.followers,
                    "following": user.following,
                })
                if progress_callback:
                    progress_callback(current, total, acc["name"], True)
            except ValueError as e:
                results.append({
                    "account_name": acc["name"],
                    "error": str(e),
                })
                if progress_callback:
                    progress_callback(current, total, acc["name"], False)

    return results
