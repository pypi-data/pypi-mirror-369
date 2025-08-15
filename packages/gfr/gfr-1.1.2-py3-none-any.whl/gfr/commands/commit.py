# gfr/commands/commit.py
import typer
import re
from rich.console import Console

from gfr.utils.git.operations import GitOperations, GitError
from gfr.utils.config import GFRConfig

app = typer.Typer(name="commit", help="Commit staged changes for the root repo or a microservice.", no_args_is_help=True)
console = Console()

def _extract_issue_number(branch_name: str) -> str | None:
    """Extracts an issue number from a branch name like 'feature/6-login-page'."""
    match = re.search(r'/(?P<num>\d+)-', branch_name)
    return match.group("num") if match else None

@app.callback(invoke_without_command=True)
def commit(
    microservice_name: str = typer.Argument(..., help="The target service (use '.' for root, '-' for last used)."),
    message: str = typer.Argument(..., help="The commit message.")
):
    """
    Commits staged changes with an optional issue number prefixed to the message.
    """
    try:
        git_ops = GitOperations()
        config = GFRConfig()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # Determine the target repository path
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

        # --- Format the commit message ---
        branch_name = git_ops.get_current_branch(path=target_path)
        issue_number = _extract_issue_number(branch_name)
        
        if issue_number:
            console.print(f"Found issue number [bold yellow]{issue_number}[/bold yellow] from branch '{branch_name}'.")
            microservice_message = f"{message} (#{issue_number})"
            parent_message = f"update {target_name} with issue number {issue_number}: [{message}]"
        else:
            microservice_message = message
            parent_message = f"update {target_name}: [{message}]"

        # --- Execute the commit operation ---
        console.print(f"Committing in [bold cyan]{target_name}[/bold cyan]...")
        git_ops.commit(microservice_message, path=target_path)
        console.print(f"✔ Successfully committed in [bold cyan]{target_name}[/bold cyan].")

        # If we committed in a submodule, we must also stage and commit that change in the root repo
        if target_path != ".":
            console.print(f"Staging and committing updated [bold cyan]{target_name}[/bold cyan] submodule in root project...")
            git_ops.add([target_path], path=".")
            # The root commit message does not get the issue number prefix
            git_ops.commit(parent_message, path=".")
            console.print(f"✔ Successfully committed submodule update in root project.")

        config.set_last_used_microservice(target_path)

    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
