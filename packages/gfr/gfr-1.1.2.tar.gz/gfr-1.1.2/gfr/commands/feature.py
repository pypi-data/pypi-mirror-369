# gfr/commands/feature.py
import typer
from gfr.utils.command_helpers import start_new_task, finish_task
from typing_extensions import Annotated

app = typer.Typer(name="feature", help="Start or finish a new feature.", no_args_is_help=True)

@app.callback(invoke_without_command=True)
def feature(
    microservice_name: Annotated[str, typer.Argument(help="The target service (use '.' for parent, '-' for last used).")],
action: Annotated[str, typer.Argument(help="The action to perform: 'start' or 'finish'.")],
    feature_name: Annotated[str, typer.Argument(help="The name of the feature (e.g., 'Login Page'). Required for 'start'.")] = ""
):
    """
    Manages the feature workflow: start a new feature or finish the current one.
    """
    if action.lower() == "start":
        if not feature_name:
            print("Error: The 'feature_name' argument is required when starting a feature.")
            raise typer.Exit(code=1)
        start_new_task("feature", microservice_name, feature_name)
    elif action.lower() == "finish":
        finish_task("feature", microservice_name)
    else:
        print(f"Error: Invalid action '{action}'. Please use 'start' or 'finish'.")
        raise typer.Exit(code=1)
