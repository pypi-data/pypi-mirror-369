# gfr/commands/push.py
import typer
from rich.console import Console

from gfr.utils.git.operations import GitOperations, GitError

app = typer.Typer(name="push", help="Push all branches for the parent repo and all microservices.")
console = Console()

@app.callback(invoke_without_command=True)
def push():
    """
    Pushes all branches (--all) for the main project and every submodule.
    """
    try:
        git_ops = GitOperations()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # --- Get all repositories (parent + submodules) ---
        submodules = git_ops.get_submodules()
        all_repos = ["."] + submodules  # "." represents the parent repo

        console.print(f"Found [bold yellow]{len(submodules)}[/bold yellow] submodule(s).")
        
        # --- Push all branches for each repository ---
        for repo_path in all_repos:
            repo_name = "parent project" if repo_path == "." else repo_path
            console.print(f"\nPushing all branches for [bold cyan]{repo_name}[/bold cyan]...")
            git_ops.push_all(path=repo_path)
            console.print(f"✔ Successfully pushed all branches for [bold cyan]{repo_name}[/bold cyan].")

        console.print("\n[bold green]✔ All repositories have been pushed successfully![/bold green]")

    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
