# gfr/commands/add.py
import typer
from rich.console import Console
from typing import List

from gfr.utils.git.operations import GitOperations, GitError
from gfr.utils.config import GFRConfig

app = typer.Typer(name="add", help="Add file contents to the index for the root repo or a microservice.", no_args_is_help=True)
console = Console()

@app.callback(invoke_without_command=True)
def add(
    microservice_name: str = typer.Argument(..., help="The target service (use '.' for root, '-' for last used)."),
    files_to_add: List[str] = typer.Argument(..., help="Files to add to the staging area (e.g., '.' for all).")
):
    """
    Adds file changes to the staging area for either the main project or a specific microservice.
    
    Examples:
    - ggg add . .                   (Stage all changes in the root project)
    - ggg add user src/main.py      (Stage a specific file in the 'user' microservice)
    - ggg add - .                   (Stage all changes in the last used microservice)
    """
    try:
        git_ops = GitOperations()
        config = GFRConfig()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # Determine the target repository path based on the microservice_name argument
        if microservice_name == '.':
            target_path = "."
            target_name = "root project"
        elif microservice_name == '-':
            target_path = config.get_last_used_microservice()
            if not target_path:
                console.print("[bold red]Error:[/bold red] No last used microservice found. Please specify a service.")
                raise typer.Exit(code=1)
            target_name = target_path
        else:
            target_path = microservice_name
            target_name = microservice_name

        # Validate the target path for microservices
        if target_path != ".":
            submodules = git_ops.get_submodules()
            if target_path not in submodules:
                console.print(f"[bold red]Error:[/bold red] '{target_name}' is not a valid submodule in this project.")
                raise typer.Exit(code=1)

        # --- Execute the add operation ---
        console.print(f"Staging files in [bold cyan]{target_name}[/bold cyan]...")
        git_ops.add(files_to_add, path=target_path)
        console.print(f"✔ Successfully staged changes in [bold cyan]{target_name}[/bold cyan].")

        config.set_last_used_microservice(target_path)

    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
