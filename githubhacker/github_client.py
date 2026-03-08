"""GitHub client wrapper using PyGithub."""
from github import Github
from github.GithubException import BadCredentialsException, GithubException


def get_user(token: str) -> str:
    """
    Validate token and get username.

    Args:
        token: GitHub personal access token

    Returns:
        GitHub username

    Raises:
        ValueError: If token is invalid
    """
    g = Github(token)
    try:
        user = g.get_user()
        return user.login
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except Exception as e:
        raise ValueError(f"Failed to authenticate: {e}")


def star_repo(token: str, repo_full_name: str) -> None:
    """
    Star a repository.

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Raises:
        ValueError: If token is invalid or repo not found
    """
    g = Github(token)
    try:
        repo = g.get_repo(repo_full_name)
        user = g.get_user()
        # Check if already starred
        if repo.id in [s.id for s in user.get_starred()]:
            raise ValueError(f"Already starred: {repo_full_name}")
        user.add_to_starred(repo)
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        raise ValueError(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise ValueError(f"Failed to star repo: {e}")


def unstar_repo(token: str, repo_full_name: str) -> None:
    """
    Unstar a repository.

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Raises:
        ValueError: If token is invalid or repo not found
    """
    g = Github(token)
    try:
        repo = g.get_repo(repo_full_name)
        user = g.get_user()
        # Check if not starred
        if repo.id not in [s.id for s in user.get_starred()]:
            raise ValueError(f"Not starred: {repo_full_name}")
        user.remove_from_starred(repo)
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        raise ValueError(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise ValueError(f"Failed to unstar repo: {e}")


def watch_repo(token: str, repo_full_name: str) -> None:
    """
    Watch a repository (subscribe to notifications).

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Raises:
        ValueError: If token is invalid or repo not found
    """
    import requests

    url = f"https://api.github.com/repos/{repo_full_name}/subscription"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {"subscribed": True, "ignored": False}

    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 401:
            raise ValueError("Invalid GitHub token")
        if response.status_code == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        if response.status_code == 422:
            error_msg = response.json().get("message", "")
            if "already" in error_msg.lower():
                raise ValueError(f"Already watching: {repo_full_name}")
            raise ValueError(f"GitHub error: {error_msg}")
        if response.status_code not in (200, 201):
            raise ValueError(f"GitHub error: {response.json().get('message', 'Unknown error')}")
    except requests.RequestException as e:
        raise ValueError(f"Failed to watch repo: {e}")


def unwatch_repo(token: str, repo_full_name: str) -> None:
    """
    Unwatch a repository (unsubscribe from notifications).

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Raises:
        ValueError: If token is invalid or repo not found
    """
    import requests

    url = f"https://api.github.com/repos/{repo_full_name}/subscription"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 401:
            raise ValueError("Invalid GitHub token")
        if response.status_code == 404:
            # Check if it's "not found" for subscription (meaning not watching)
            # or "not found" for repo
            raise ValueError(f"Not watching: {repo_full_name}")
        if response.status_code == 204:
            # Success, no content
            return
        if response.status_code not in (200, 201, 204):
            raise ValueError(f"GitHub error: {response.json().get('message', 'Unknown error')}")
    except requests.RequestException as e:
        raise ValueError(f"Failed to unwatch repo: {e}")


def check_repo_status(token: str, repo_full_name: str) -> dict:
    """
    Check if a repository is starred and/or watched.

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Returns:
        Dictionary with 'starred' and 'watched' boolean values

    Raises:
        ValueError: If token is invalid or repo not found
    """
    import requests

    g = Github(token)
    try:
        # Check starred
        repo = g.get_repo(repo_full_name)
        user = g.get_user()
        starred = repo.id in [s.id for s in user.get_starred()]

        # Check watched (subscription)
        url = f"https://api.github.com/repos/{repo_full_name}/subscription"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            raise ValueError("Invalid GitHub token")
        if response.status_code == 404:
            watched = False
        elif response.status_code == 200:
            data = response.json()
            watched = data.get("subscribed", False)
        else:
            watched = False

        return {"starred": starred, "watched": watched}
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        raise ValueError(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise ValueError(f"Failed to check repo status: {e}")


def fork_repo(token: str, repo_full_name: str) -> str:
    """
    Fork a repository.

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Returns:
        Fork full name (e.g., "username/repo")

    Raises:
        ValueError: If token is invalid or repo not found
    """
    g = Github(token)
    try:
        repo = g.get_repo(repo_full_name)
        forked_repo = repo.create_fork()
        return forked_repo.full_name
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        if e.status == 422:
            # Already forked or rate limit
            error_msg = e.data.get("message", "")
            if "fork" in error_msg.lower():
                # Fork already exists, get it
                try:
                    user = g.get_user()
                    fork_name = repo_full_name.split("/")[-1]
                    existing_fork = user.get_repo(fork_name)
                    return existing_fork.full_name
                except:
                    pass
            raise ValueError(f"GitHub error: {error_msg}")
        raise ValueError(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise ValueError(f"Failed to fork repo: {e}")


def get_repo_info(token: str, repo_full_name: str) -> dict:
    """
    Get repository information.

    Args:
        token: GitHub personal access token
        repo_full_name: Repository full name (e.g., "owner/repo")

    Returns:
        Dictionary with repo info (stars, forks, watchers, description, etc.)

    Raises:
        ValueError: If token is invalid or repo not found
    """
    g = Github(token)
    try:
        repo = g.get_repo(repo_full_name)
        return {
            "name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.watchers_count,
            "language": repo.language,
            "open_issues": repo.open_issues_count,
            "license": repo.license.name if repo.license else None,
            "created_at": str(repo.created_at),
            "updated_at": str(repo.updated_at),
            "url": repo.html_url,
        }
    except BadCredentialsException:
        raise ValueError("Invalid GitHub token")
    except GithubException as e:
        if e.status == 404:
            raise ValueError(f"Repository not found: {repo_full_name}")
        raise ValueError(f"GitHub error: {e.data.get('message', str(e))}")
    except Exception as e:
        raise ValueError(f"Failed to get repo info: {e}")
