#!/usr/bin/env python3
"""GitHub Hacker CLI - Manage multiple GitHub accounts."""
import sys
import json
import typer
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from . import account_manager, storage
from .account_manager import parse_repo
from . import __version__

console = Console()

# Create config subcommand group
config_app = typer.Typer(help="Manage account configuration")
app = typer.Typer(
    help="GitHub Hacker - Manage multiple GitHub accounts",
)
app.add_typer(config_app, name="config")


def version_callback(value: bool):
    if value:
        console.print(f"github-hacker version [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.command()
def login(
    name: str = typer.Argument(..., help="Alias for this account"),
    token: str = typer.Argument(..., help="GitHub personal access token"),
):
    """Add a GitHub account."""
    try:
        username = account_manager.login(name, token)
        console.print(f"[green]✓[/green] Logged in as [bold]{username}[/bold] (alias: {name})")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def logout(
    name: str = typer.Argument(..., help="Alias of the account to remove"),
):
    """Remove a GitHub account."""
    if account_manager.logout(name):
        console.print(f"[green]✓[/green] Removed account: {name}")
    else:
        console.print(f"[red]Error:[/red] Account not found: {name}")
        raise typer.Exit(1)


@config_app.command("list")
def config_list():
    """List all saved GitHub accounts."""
    accounts = account_manager.list_accounts()

    if not accounts:
        console.print("[yellow]No accounts saved.[/yellow]")
        return

    table = Table(title="Saved GitHub Accounts")
    table.add_column("Alias", style="cyan")
    table.add_column("Username", style="green")

    for acc in accounts:
        table.add_row(acc["name"], acc["username"])

    console.print(table)


@config_app.command("import")
def config_import(
    file: str = typer.Argument(..., help="JSON file to import accounts from"),
    force: bool = typer.Option(False, "-f", "--force", help="Overwrite existing accounts"),
):
    """Import accounts from a JSON file."""
    try:
        with open(file, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid JSON format. Expected a dictionary of accounts.")

        imported_count = 0
        skipped_count = 0

        for name, account_data in data.items():
            if not isinstance(account_data, dict) or "token" not in account_data:
                console.print(f"[yellow]Skipping invalid account:[/yellow] {name}")
                skipped_count += 1
                continue

            existing = storage.get_account(name)
            if existing and not force:
                console.print(f"[yellow]Skipping existing account (use --force to overwrite):[/yellow] {name}")
                skipped_count += 1
                continue

            try:
                username = account_manager.login(name, account_data["token"])
                imported_count += 1
                console.print(f"[green]✓[/green] Imported account: {name} ({username})")
            except ValueError as e:
                console.print(f"[red]Failed to import {name}:[/red] {e}")
                skipped_count += 1

        console.print(f"\n[bold]Summary:[/bold] [green]{imported_count}[/green] imported, [yellow]{skipped_count}[/yellow] skipped")

    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Error:[/red] Invalid JSON file: {file}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("export")
def config_export(
    file: str = typer.Argument(..., help="JSON file to export accounts to"),
):
    """Export accounts to a JSON file."""
    try:
        accounts = storage.load_accounts()

        if not accounts:
            console.print("[yellow]No accounts to export.[/yellow]")
            return

        with open(file, "w") as f:
            json.dump(accounts, f, indent=2)

        console.print(f"[green]✓[/green] Exported {len(accounts)} account(s) to [cyan]{file}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("whoami")
def config_whoami():
    """Show user info for all saved accounts."""
    try:
        accounts = account_manager.list_accounts()
        total = len(accounts)

        console.print(f"\n[bold cyan]Getting account info[/bold cyan] for {total} account(s)...\n")

        if total == 1:
            results = account_manager.whoami()
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Checking accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.whoami(progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Username", style="blue")
        table.add_column("Name", style="green")
        table.add_column("Email", style="yellow")
        table.add_column("Repos", style="dim")
        table.add_column("Followers", style="dim")

        for result in results:
            if "error" in result:
                table.add_row(result["account_name"], "[red]Error[/red]", "-", "-", "-", "-")
            else:
                email = result.get("email") or "-"
                name = result.get("name") or "-"
                table.add_row(result["account_name"], result.get("username", "-"), name, email, str(result.get("public_repos", "-")), str(result.get("followers", "-")))

        console.print(table)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("validate")
def config_validate():
    """Validate all stored tokens."""
    try:
        accounts = account_manager.list_accounts()
        total = len(accounts)

        console.print(f"\n[bold cyan]Validating[/bold cyan] {total} account(s)...\n")

        if total == 1:
            results = account_manager.whoami()
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Validating accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓ Valid[/green]" if success else "[red]✗ Invalid[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.whoami(progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Username", style="blue")
        table.add_column("Status", style="green")

        valid_count = 0
        for result in results:
            if "error" in result:
                table.add_row(result["account_name"], "-", "[red]Invalid[/red]")
            else:
                table.add_row(result["account_name"], result.get("username", "-"), "[green]Valid[/green]")
                valid_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] {valid_count}/{len(results)} accounts valid\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Add version option
@app.callback()
def main_callback(
    version: bool = typer.Option(None, "--version", help="Show version information", is_eager=True, callback=version_callback),
):
    pass


# Register config as a subcommand
app.add_typer(config_app, name="config")


@app.command()
def star(
    repo: str = typer.Argument(..., help="Repository to star (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use (use all accounts if not specified)"),
):
    """Star a repository."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = 1 if account else len(accounts)

        console.print(f"\n[bold cyan]Starring[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        results = []

        if total == 1:
            results = account_manager.star(account, repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.star(account, repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        success_count = 0
        for result in results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            details = result.error if result.error else "Starred successfully"
            table.add_row(result.account_name, status, details)
            if result.success:
                success_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] [green]{success_count}[/green]/{len(results)} accounts succeeded\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def unstar(
    repo: str = typer.Argument(..., help="Repository to unstar (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use (use all accounts if not specified)"),
):
    """Unstar a repository."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = 1 if account else len(accounts)

        console.print(f"\n[bold cyan]Unstarring[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        results = []

        if total == 1:
            results = account_manager.unstar(account, repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.unstar(account, repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        success_count = 0
        for result in results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            details = result.error if result.error else "Unstarred successfully"
            table.add_row(result.account_name, status, details)
            if result.success:
                success_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] [green]{success_count}[/green]/{len(results)} accounts succeeded\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def watch(
    repo: str = typer.Argument(..., help="Repository to watch (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use (use all accounts if not specified)"),
):
    """Watch a repository (subscribe to notifications)."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = 1 if account else len(accounts)

        console.print(f"\n[bold cyan]Watching[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        results = []

        if total == 1:
            results = account_manager.watch(account, repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.watch(account, repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        success_count = 0
        for result in results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            details = result.error if result.error else "Watched successfully"
            table.add_row(result.account_name, status, details)
            if result.success:
                success_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] [green]{success_count}[/green]/{len(results)} accounts succeeded\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def unwatch(
    repo: str = typer.Argument(..., help="Repository to unwatch (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use (use all accounts if not specified)"),
):
    """Unwatch a repository (unsubscribe from notifications)."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = 1 if account else len(accounts)

        console.print(f"\n[bold cyan]Unwatching[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        results = []

        if total == 1:
            results = account_manager.unwatch(account, repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.unwatch(account, repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        success_count = 0
        for result in results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            details = result.error if result.error else "Unwatched successfully"
            table.add_row(result.account_name, status, details)
            if result.success:
                success_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] [green]{success_count}[/green]/{len(results)} accounts succeeded\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    repo: str = typer.Argument(..., help="Repository to check (owner/repo or https://github.com/owner/repo)"),
):
    """Check star and watch status for a repository."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = len(accounts)

        console.print(f"\n[bold cyan]Checking status for[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        if total == 1:
            results = account_manager.status(repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Checking accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status_icon = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status_icon}", completed=current)

                results = account_manager.status(repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Username", style="blue")
        table.add_column("Starred", style="green")
        table.add_column("Watched", style="yellow")

        for result in results:
            starred = "[green]✓[/green]" if result.starred else "[red]✗[/red]"
            watched = "[green]✓[/green]" if result.watched else "[red]✗[/red]"
            table.add_row(result.account_name, result.username, starred, watched)

        console.print(table)

        starred_count = sum(1 for r in results if r.starred)
        watched_count = sum(1 for r in results if r.watched)
        console.print(f"\n[bold]Summary:[/bold] {starred_count}/{len(results)} starred, {watched_count}/{len(results)} watched\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def fork(
    repo: str = typer.Argument(..., help="Repository to fork (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use (use all accounts if not specified)"),
):
    """Fork a repository."""
    try:
        parsed_repo = parse_repo(repo)

        accounts = account_manager.list_accounts()
        total = 1 if account else len(accounts)

        console.print(f"\n[bold cyan]Forking[/bold cyan] [yellow]{parsed_repo}[/yellow] with {total} account(s)...\n")

        results = []

        if total == 1:
            results = account_manager.fork(account, repo) if account else account_manager.fork(repo)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Processing accounts...", total=total)

                def callback(current: int, total: int, account_name: str, success: bool):
                    status = "[green]✓[/green]" if success else "[red]✗[/red]"
                    progress.update(task, description=f"[cyan]{account_name}... {status}", completed=current)

                results = account_manager.fork(account, repo, progress_callback=callback) if account else account_manager.fork(repo, progress_callback=callback)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Account", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Fork", style="blue")

        success_count = 0
        for result in results:
            status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
            fork_name = result.error if result.success else "-"
            table.add_row(result.account_name, status, fork_name)
            if result.success:
                success_count += 1

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] [green]{success_count}[/green]/{len(results)} accounts succeeded\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def info(
    repo: str = typer.Argument(..., help="Repository to check (owner/repo or https://github.com/owner/repo)"),
    account: str | None = typer.Option(None, "-a", "--account", help="Account alias to use"),
):
    """Show repository information."""
    try:
        parsed_repo = parse_repo(repo)

        if not account:
            accounts = account_manager.list_accounts()
            if not accounts:
                raise ValueError("No accounts saved. Use 'login' to add an account first.")
            account = accounts[0]["name"]

        repo_info = account_manager.get_repo_info_account(account, repo)

        console.print(f"\n[bold cyan]Repository:[/bold cyan] [yellow]{repo_info['name']}[/yellow]\n")

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Description", repo_info.get("description") or "-")
        info_table.add_row("Stars", f"[yellow]{repo_info['stars']}[/yellow]")
        info_table.add_row("Forks", f"[yellow]{repo_info['forks']}[/yellow]")
        info_table.add_row("Watchers", f"[yellow]{repo_info['watchers']}[/yellow]")
        info_table.add_row("Language", repo_info.get("language") or "-")
        info_table.add_row("Open Issues", f"[yellow]{repo_info['open_issues']}[/yellow]")
        info_table.add_row("License", repo_info.get("license") or "-")
        info_table.add_row("URL", f"[link]{repo_info['url']}[/link]")

        console.print(info_table)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Run with custom error handling
def main():
    try:
        app(standalone_mode=False)
    except click.exceptions.UsageError as e:
        # No command provided - show help
        if "Missing command" in e.format_message():
            # Call the app with --help to show help
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "githubhacker.cli", "--help"],
                capture_output=True, text=True
            )
            console.print(result.stdout)
            sys.exit(0)
        else:
            console.print(f"[red]Error:[/red] {e.format_message()}")
    except click.exceptions.MissingParameter as e:
        console.print(f"[red]Error:[/red] {e.format_message()}")
        # Show help for the command that was invoked
        if e.ctx:
            console.print()
            with console.capture() as capture:
                console.print(e.ctx.get_help())
            console.print(capture.get())
        console.print("\n[dim]Run with --help for more information.[/dim]")
    except click.exceptions.ClickException as e:
        console.print(f"[red]Error:[/red] {e.format_message()}")
        console.print("\n[bold cyan]Examples:[/bold cyan]")
        console.print("  github-hacker login <name> <token>")
        console.print("  github-hacker logout <name>")
        console.print("  github-hacker config list")
        console.print("  github-hacker config import <file>")
        console.print("  github-hacker config export <file>")
        console.print("  github-hacker config whoami")
        console.print("  github-hacker config validate")
        console.print("  github-hacker star <repo>")
        console.print("  github-hacker star <repo> -a <account>")
        console.print("  github-hacker unstar <repo>")
        console.print("  github-hacker watch <repo>")
        console.print("  github-hacker unwatch <repo>")
        console.print("  github-hacker status <repo>")
        console.print("  github-hacker fork <repo>")
        console.print("  github-hacker info <repo>")
        console.print("\n[dim]Run with --help for more information.[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
