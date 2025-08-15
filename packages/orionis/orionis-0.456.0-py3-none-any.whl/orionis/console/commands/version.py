from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from rich.console import Console
from rich.panel import Panel
from orionis.metadata import framework

class VersionCommand(BaseCommand):
    """
    Command class to display the current version of the Orionis framework.

    This command prints the version number of the framework in use.
    """
    timestamps: bool = False

    signature: str = "version"

    description: str = "Prints the version of the framework in use."

    def handle(self) -> None:
        """
        Executes the version command to display the current Orionis framework version.

        This method retrieves the version number from the framework metadata and prints it
        in a formatted, bold, and successful style to the console. If an unexpected error occurs
        during execution, it raises a CLIOrionisRuntimeError with the original exception message.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It outputs the version information to the console.

        Raises
        ------
        CLIOrionisRuntimeError
            If an unexpected error occurs during execution, a CLIOrionisRuntimeError is raised
            with the original exception message.
        """

        # Print the Orionis framework version in a bold, success style
        try:

            # Initialize the console for rich output
            console = Console()

            # Compose the main info
            title = f"[bold yellow]{framework.NAME.capitalize()} Framework[/bold yellow] [white]v{framework.VERSION}[/white]"
            author = f"[bold]Author:[/bold] {framework.AUTHOR}  |  [bold]Email:[/bold] {framework.AUTHOR_EMAIL}"
            desc = f"[italic]{framework.DESCRIPTION}[/italic]"
            python_req = f"[bold]Python Requires:[/bold] {framework.PYTHON_REQUIRES}"
            docs = f"[bold]Docs:[/bold] [underline blue]{framework.DOCS}[/underline blue]"
            repo = f"[bold]Repo:[/bold] [underline blue]{framework.FRAMEWORK}[/underline blue]"

            body = "\n".join([desc, "", author, python_req, docs, repo, ""])

            panel = Panel(
                body,
                title=title,
                border_style="bold yellow",
                padding=(1, 6),
                expand=False,
                subtitle="[bold yellow]Orionis CLI[/bold yellow]",
                subtitle_align="right"
            )
            console.line()
            console.print(panel)
            console.line()

        # Raise a custom runtime error if any exception occurs
        except Exception as e:
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}") from e
