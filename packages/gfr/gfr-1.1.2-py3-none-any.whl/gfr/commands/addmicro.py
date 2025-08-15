import typer
import questionary
import os
from rich.console import Console
from rich.prompt import Prompt

from gfr.utils.github.api import GitHubAPI
from gfr.utils.github.exceptions import GitHubError
from gfr.utils.git.operations import GitOperations, GitError

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def main(
    micro_service_name: str = typer.Argument(..., help="The name of the microservice directory.")
):
    """
    Creates a new GitHub repository for a microservice, initializes it,
    and adds it as a submodule to the current project.
    """
    try:
        # --- Initialize APIs ---
        git_ops = GitOperations()
        github_api = GitHubAPI()
        
        # --- Pre-flight Checks ---
        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from the root of a Git repository.")
            raise typer.Exit(code=1)
            
        if not os.path.isdir(micro_service_name):
            console.print(f"[bold red]Error:[/bold red] Directory '{micro_service_name}' not found.")
            raise typer.Exit(code=1)

        if git_ops.is_git_repo(path=micro_service_name):
            console.print(f"[bold red]Error:[/bold red] '{micro_service_name}' is already a Git repository.")
            raise typer.Exit(code=1)

        console.print(f"Authenticated as [bold green]{github_api.username}[/bold green] for organization [bold green]{github_api.org_name}[/bold green].")
        
        # --- Get Repository Details ---
        repo_name = Prompt.ask("[bold cyan]Enter repository name[/bold cyan]", default=micro_service_name)
        if not repo_name:
            console.print("[bold red]Repository name cannot be empty. Aborting.[/bold red]")
            raise typer.Exit()

        description = Prompt.ask("[bold cyan]Enter repository description[/bold cyan]")

        is_private = questionary.select(
            "Select repository visibility:",
            choices=[
                {"name": "Private", "value": True},
                {"name": "Public", "value": False}
            ],
            use_indicator=True
        ).ask()

        if is_private is None:
            console.print("[bold red]No selection made. Aborting.[/bold red]")
            raise typer.Exit()

        # --- Workflow Steps ---
        with console.status("[bold yellow]Setting up microservice...[/bold yellow]", spinner="dots") as status:
            # Step 1: Create GitHub Repository
            status.update("[bold yellow]Creating GitHub repository...[/bold yellow]")
            repo = github_api.repos.create(repo_name, description, is_private, False) # should be empty
            console.print(f"✔ Repository '{repo.full_name}' created on GitHub.")

            # Step 2: Initialize Local Repository for the microservice
            status.update(f"[bold yellow]Initializing repository in '{micro_service_name}'...[/bold yellow]")
            git_ops.init(path=micro_service_name)
            git_ops.add_remote(repo.clone_url, path=micro_service_name)
            console.print(f"✔ Local repository initialized in '{micro_service_name}'.")

            # Step 3: Create an initial commit to allow branching
            status.update(f"[bold yellow]Creating initial commit...[/bold yellow]")
            gitkeep_path = os.path.join(micro_service_name, ".gitkeep")
            with open(gitkeep_path, "w") as f:
                pass
            git_ops.add([".gitkeep"], path=micro_service_name)
            git_ops.commit("Initial commit", path=micro_service_name)
            console.print("✔ Created initial commit.")

            # Step 4: Create and Push Branches
            status.update("[bold yellow]Creating and pushing branches...[/bold yellow]")
            git_ops.create_branch("develop", path=micro_service_name)
            git_ops.push_branch("main", set_upstream=True, path=micro_service_name)
            git_ops.push_branch("develop", set_upstream=True, path=micro_service_name)
            console.print("✔ 'main' and 'develop' branches created and pushed.")
            
            status.update("[bold yellow]Setting 'develop' as default branch...[/bold yellow]")
            github_api.repos.edit(repo, default_branch="develop")
            console.print("✔ Default branch set to 'develop' on GitHub.")

            # Step 5: Switch to develop branch
            git_ops.switch_branch("develop", path=micro_service_name)
            console.print("✔ Switched to 'develop' branch.")
            
            # Step 6: Add as Submodule to Parent Repo
            status.update("[bold yellow]Adding as submodule to parent project...[/bold yellow]")
            git_ops.add_submodule(repo.clone_url, micro_service_name)
            console.print("✔ Added as a submodule.")

        console.print(f"\n[bold green]✔ Success![/bold green] Microservice '{repo_name}' is ready.")
        console.print(f"It has been added as a submodule to your current project.")

    except (GitHubError, GitError) as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
