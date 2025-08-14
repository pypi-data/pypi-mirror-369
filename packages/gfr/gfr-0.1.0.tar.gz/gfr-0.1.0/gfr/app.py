import typer
from gfr.commands import hello

# Create the main Typer application
app = typer.Typer(
    name="ggg",
    help="Git Flow Assistant of Rahmasir (gfr) helps with git and GitHub workflows.",
    add_completion=False,
)

# Add subcommands from the commands module
app.add_typer(hello.app, name="hello")

if __name__ == "__main__":
    app()
