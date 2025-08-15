# gfr/commands/acp.py
import typer
from rich.console import Console

# Import the other command modules to reuse their logic
from . import add as add_command
from . import commit as commit_command
from . import push as push_command

app = typer.Typer(name="acp", help="Add, commit, and push all changes in one step.", no_args_is_help=True)
console = Console()

@app.callback(invoke_without_command=True)
def acp(
    microservice_name: str = typer.Argument(..., help="The target service (use '.' for parent, '-' for last used)."),
    message: str = typer.Argument(..., help="The commit message.")
):
    """
    Stages all changes, commits them, and pushes all branches in one step by
    sequentially calling the 'add', 'commit', and 'push' commands.
    """
    try:
        # --- Step 1: Execute the 'add' command's logic ---
        console.print(f"[bold blue]>>> Running 'add' step...[/bold blue]")
        add_command.add(microservice_name=microservice_name, files_to_add=['.'])
        console.print(f"[bold blue]<<< 'add' step complete.[/bold blue]\n")

        # --- Step 2: Execute the 'commit' command's logic ---
        console.print(f"[bold blue]>>> Running 'commit' step...[/bold blue]")
        commit_command.commit(microservice_name=microservice_name, message=message)
        console.print(f"[bold blue]<<< 'commit' step complete.[/bold blue]\n")

        # --- Step 3: Execute the 'push' command's logic ---
        console.print(f"[bold blue]>>> Running 'push' step...[/bold blue]")
        push_command.push()
        console.print(f"[bold blue]<<< 'push' step complete.[/bold blue]")
        
        console.print("\n[bold green]✔ Add, commit, and push sequence completed successfully![/bold green]")

    except typer.Exit:
        # This allows the underlying commands to exit gracefully without crashing 'acp'
        raise
    except Exception as e:
        # A general catch-all for any unexpected errors during orchestration
        console.print(f"\n[bold red]An unexpected error occurred in the 'acp' command: {e}[/bold red]")
        raise typer.Exit(code=1)
