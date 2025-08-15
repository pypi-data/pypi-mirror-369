# gfr/commands/addasset.py
import typer
import os
from rich.console import Console

from gfr.utils.git.operations import GitOperations, GitError
from gfr.utils.config import GFRConfig
from gfr.assets import mit

app = typer.Typer(name="addasset", help="Create a new file in a service from a predefined asset template.", no_args_is_help=True)
console = Console()

# A dictionary to map asset names to their content
ASSETS = {
    "mit": mit.MIT_LICENCE,
    # Add other assets here, e.g., "gitignore": gitignore.GITIGNORE_CONTENT
}

@app.callback(invoke_without_command=True)
def addasset(
    microservice_name: str = typer.Argument(..., help="The target service (use '.' for parent, '-' for last used)."),
    src_file_name: str = typer.Argument(..., help=f"The asset to create. Available: {', '.join(ASSETS.keys())}"),
    destination_file_name: str = typer.Argument(..., help="The name of the file to be created in the service.")
):
    """
    Creates a new file within a specified service using a predefined asset template.
    """
    try:
        git_ops = GitOperations()
        config = GFRConfig()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # --- Validate the requested asset ---
        if src_file_name.lower() not in ASSETS:
            console.print(f"[bold red]Error:[/bold red] Asset '{src_file_name}' not found.")
            console.print(f"Available assets are: {', '.join(ASSETS.keys())}")
            raise typer.Exit(code=1)

        asset_content = ASSETS[src_file_name.lower()]

        # --- Determine the target directory ---
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

        # --- Create the asset file ---
        final_destination_path = os.path.join(target_path, destination_file_name)
        
        if os.path.exists(final_destination_path):
            console.print(f"[bold red]Error:[/bold red] File '{final_destination_path}' already exists.")
            raise typer.Exit(code=1)

        console.print(f"Creating file [bold yellow]{destination_file_name}[/bold yellow] in [bold cyan]{target_name}[/bold cyan]...")
        with open(final_destination_path, "w") as f:
            f.write(asset_content.strip())

        console.print(f"\n[bold green]✔ Success![/bold green] Asset '{destination_file_name}' created.")
        console.print(f"Remember to stage and commit the new file using 'ggg add' and 'ggg commit'.")

        config.set_last_used_microservice(target_name)

    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
