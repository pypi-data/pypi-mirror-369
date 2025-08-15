# gfr/commands/ac.py
import typer
from rich.console import Console
import sys

# Import the other command modules to reuse their logic
from . import add as add_command
from . import commit as commit_command

app = typer.Typer(name="ac", help="Add all changes and commit them in one step.", no_args_is_help=True)
console = Console()

@app.callback(invoke_without_command=True)
def ac(
    microservice_name: str = typer.Argument(..., help="The target service (use '.' for parent, '-' for last used)."),
    message: str = typer.Argument(..., help="The commit message.")
):
    """
    Stages all changes and commits them with a formatted message in one step by
    sequentially calling the 'add' and 'commit' commands.
    """
    try:
        # --- Step 1: Execute the 'add' command's logic ---
        # We are effectively running 'ggg add [microservice-name] .'
        console.print(f"[bold blue]>>> Running 'add' step...[/bold blue]")
        add_command.add(microservice_name=microservice_name, files_to_add=['.'])
        console.print(f"[bold blue]<<< 'add' step complete.[/bold blue]\n")

        # --- Step 2: Execute the 'commit' command's logic ---
        # We are effectively running 'ggg commit [microservice-name] [message]'
        console.print(f"[bold blue]>>> Running 'commit' step...[/bold blue]")
        commit_command.commit(microservice_name=microservice_name, message=message)
        console.print(f"[bold blue]<<< 'commit' step complete.[/bold blue]")

    except typer.Exit:
        # This allows the underlying commands to exit gracefully without crashing 'ac'
        # We re-raise it to ensure the process exits correctly.
        raise
    except Exception as e:
        # A general catch-all for any unexpected errors during orchestration
        console.print(f"\n[bold red]An unexpected error occurred in the 'ac' command: {e}[/bold red]")
        raise typer.Exit(code=1)

