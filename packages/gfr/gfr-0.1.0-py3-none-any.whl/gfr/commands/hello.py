import typer

# Create a new Typer app for the 'hello' command
app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    """
    Prints a simple hello message.
    This is the entry point for the 'ggg hello' command.
    """
    print("Hello from Git Flow assistant of Rahmasir!")

