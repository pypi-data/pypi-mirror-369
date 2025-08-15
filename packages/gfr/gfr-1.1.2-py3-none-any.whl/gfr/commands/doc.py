# gfr/commands/doc.py
import typer
from gfr.utils.command_helpers import switch_to_branch

app = typer.Typer(name="doc", help="Switch to the 'doc' branch in the current repository.")

@app.callback(invoke_without_command=True)
def doc():
    """
    Switches the current repository to the 'doc' branch.
    """
    switch_to_branch("doc")
