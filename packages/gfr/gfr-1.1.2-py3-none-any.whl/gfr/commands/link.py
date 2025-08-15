import typer
from rich.console import Console
from rich.table import Table

from gfr.utils.git.operations import GitOperations, GitError
from gfr.utils.command_helpers import format_git_url_to_http

app = typer.Typer(name="link", help="Display GitHub links for the parent repo and all submodules.")
console = Console()

@app.callback(invoke_without_command=True)
def link():
    """
    Displays the GitHub links for the main project and all its submodules.
    """
    try:
        git_ops = GitOperations()

        if not git_ops.is_git_repo():
            console.print("[bold red]Error:[/bold red] This command must be run from within a Git repository.")
            raise typer.Exit(code=1)

        # Get all repositories (parent + submodules)
        all_repos = ["."] + git_ops.get_submodules()

        table = Table(title="Project GitHub Links", show_header=True, header_style="bold magenta")
        table.add_column("Repository", style="cyan", no_wrap=True)
        table.add_column("GitHub Link", style="green")

        console.print("Fetching remote URLs...")
        for repo_path in all_repos:
            repo_name = "root" if repo_path == "." else repo_path
            try:
                remote_url = git_ops.get_remote_url(path=repo_path)
                http_url = format_git_url_to_http(remote_url)
                table.add_row(repo_name, f"[link={http_url}]{http_url}[/link]")
            except GitError:
                table.add_row(repo_name, "[dim]No remote found[/dim]")

        console.print(table)

    except GitError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        raise typer.Exit()
