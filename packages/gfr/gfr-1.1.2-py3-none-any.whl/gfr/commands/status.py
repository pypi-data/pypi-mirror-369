# gfr/commands/status.py
import typer
from rich.console import Console
from rich.panel import Panel

from gfr.utils.git.operations import GitOperations, GitError

app = typer.Typer(name="status", help="Show the working tree status for all repositories.")
console = Console()

@app.callback(invoke_without_command=True)
def status():
    """
    Displays the detailed status of the main project and all its submodules.
    """
    try:
        git_ops = GitOperations()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # Get all repositories (parent + submodules)
        all_repos = ["."] + git_ops.get_submodules()

        console.print("\n[bold]Project Status Overview[/bold]")

        for i, repo_path in enumerate(all_repos):
            repo_name = "root" if repo_path == "." else repo_path
            
            try:
                repo_status = git_ops.get_status(path=repo_path)
            except GitError as e:
                console.print(Panel(f"[bold red]Error checking status:[/bold red] {e}", title=f"[bold cyan]{repo_name}", border_style="red"))
                continue

            console.print(f'[bold blue]{repo_name}[/bold blue]: [yellow]{repo_status.branch}[/yellow]')
            if repo_status.staged:
                console.print("  Staged changes:")
                for file in repo_status.staged:
                    console.print(f"  - [bold green]{file}[/bold green]")
            if repo_status.unstaged:
                console.print("  Unstaged changes:")
                for file in repo_status.unstaged:
                    console.print(f"  - [bold red]{file}[/bold red]")
            if repo_status.untracked:
                console.print("  Untracked changes:")
                for file in repo_status.untracked:
                    console.print(f"  - [red]{file}[/red]")
                    
    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
