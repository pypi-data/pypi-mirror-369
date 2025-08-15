import typer
import questionary
from rich.console import Console
from rich.prompt import Prompt

from gfr.utils.github.api import GitHubAPI, GitHubError
from gfr.utils.git.operations import GitOperations

# Create a Typer app for the 'create' command
app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def main():
    """
    Creates a new GitHub repository in your organization.
    """
    try:
        # Initialize the GitHub API client
        github_api = GitHubAPI()
        git_operations = GitOperations()
        console.print(f"Authenticated as [bold green]{github_api.username}[/bold green] for organization [bold green]{github_api.org_name}[/bold green].")

        # --- Get Repository Name ---
        repo_name = Prompt.ask("[bold cyan]Enter repository name[/bold cyan]")

        # --- Get Repository Description ---
        description = Prompt.ask("\n[bold cyan]Enter repository description[/bold cyan]")

        # --- Get Repository Visibility ---
        is_private = questionary.select(
            "Select repository visibility:",
            choices=[
                {"name": "Public", "value": False},
                {"name": "Private", "value": True},
            ],
            use_indicator=True
        ).ask()        
        
        if is_private is None:
            console.print("[bold red]No selection made. Aborting.[/bold red]")
            raise typer.Exit()

        readmefile = Prompt.ask("Do you want to add a readme file?", choices=['y', 'n'], default='n').lower() == 'y'

        # --- Create Repository ---
        with console.status("[bold yellow]Creating repository...[/bold yellow]", spinner="dots"):
            repo = github_api.repos.create(repo_name, description, is_private, readmefile)
        
        console.print(f"\n[bold green]✔ Repository '{repo.full_name}' created successfully![/bold green]")
        console.print(f"  [link={repo.html_url}]{repo.html_url}[/link]")
        
        
        with console.status("[bold yellow]Cloning repository...[/bold yellow]", spinner="dots"):
            repo_path = git_operations.clone(repo.html_url, repo_name)
            
        console.print(f"\n[bold green]✔ Repository '{repo.full_name}' cloned successfully![/bold green]")

    except GitHubError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()

