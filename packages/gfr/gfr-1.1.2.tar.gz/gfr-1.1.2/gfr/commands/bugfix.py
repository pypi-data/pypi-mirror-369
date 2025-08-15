# gfr/commands/bugfix.py
import typer
from gfr.utils.command_helpers import start_new_task, finish_task
from typing_extensions import Annotated

app = typer.Typer(name="bugfix", help="Start or finish a new bugfix.", no_args_is_help=True)

@app.callback(invoke_without_command=True)
def bugfix(
    microservice_name: Annotated[str, typer.Argument(help="The target service (use '.' for parent, '-' for last used).")],
    action: Annotated[str, typer.Argument(help="The action to perform: 'start' or 'finish'.")],
    bug_name: Annotated[str, typer.Argument(help="The name of the bug (e.g., 'Logout Button Broken'). Required for 'start'.")] = ""
):
    """
    Manages the bugfix workflow: start a new bugfix or finish the current one.
    """
    if action.lower() == "start":
        if not bug_name:
            print("Error: The 'bug_name' argument is required when starting a bugfix.")
            raise typer.Exit(code=1)
        start_new_task("bugfix", microservice_name, bug_name)
    elif action.lower() == "finish":
        finish_task("bugfix", microservice_name)
    else:
        print(f"Error: Invalid action '{action}'. Please use 'start' or 'finish'.")
        raise typer.Exit(code=1)
