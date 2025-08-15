# gfr/commands/dev.py
import typer
from gfr.utils.command_helpers import switch_to_branch

app = typer.Typer(name="dev", help="Switch to the 'develop' branch in the current repository.")

@app.callback(invoke_without_command=True)
def dev():
    """
    Switches the current repository to the 'develop' branch.
    """
    switch_to_branch("develop")
