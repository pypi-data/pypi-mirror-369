from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from rich.console import Console
from rich.panel import Panel

class HelpCommand(BaseCommand):
    """
    Command class to display usage information for the Orionis CLI.
    """

    timestamps: bool = False
    signature: str = "help"
    description: str = "Prints help information for the Orionis CLI commands."

    def handle(self) -> None:
        """
        Executes the command to display usage information for the Orionis CLI.
        """
        try:
            console = Console()
            usage = (
                "[bold cyan]Usage:[/]\n"
                "  orionis <command> [options]\n\n"
                "[bold cyan]Available Commands:[/]\n"
                "  help        Show this help message\n"
                "  run         Run the application\n"
                "  make        Generate code scaffolding\n"
                "  migrate     Run database migrations\n"
                "  ...         Other available commands\n\n"
                "[bold cyan]Options:[/]\n"
                "  -h, --help  Show this help message and exit\n"
            )
            panel = Panel(usage, title="[bold green]Orionis CLI Help[/]", expand=False, border_style="bright_blue")
            console.print(panel)
        except Exception as e:
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}") from e
