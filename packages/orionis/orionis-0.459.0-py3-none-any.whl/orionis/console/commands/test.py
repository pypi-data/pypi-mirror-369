from orionis.app import Orionis
from orionis.console.base.command import BaseCommand
from orionis.console.exceptions import CLIOrionisRuntimeError
from orionis.test.contracts.kernel import ITestKernel

class TestCommand(BaseCommand):
    """
    Command class to display usage information for the Orionis CLI.

    Attributes
    ----------
    timestamps : bool
        Indicates whether timestamps will be shown in the command output.
    signature : str
        The command signature.
    description : str
        A brief description of the command.
    """

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "test"

    # Command description
    description: str = "Prints help information for the Orionis CLI commands."

    def handle(self) -> None:
        """
        Executes the test command for the Orionis CLI.

        This method initializes the Orionis application, retrieves the test kernel instance,
        and runs the test suite using the kernel's handle method. If any exception occurs during
        execution, it raises a CLIOrionisRuntimeError with the error details.

        Returns
        -------
        None
            This method does not return any value. It performs actions as a side effect,
            such as running the test suite and handling exceptions.

        Raises
        ------
        CLIOrionisRuntimeError
            If an unexpected error occurs during the execution of the test command.
        """
        try:

            # Initialize the Orionis application instance
            app = Orionis()

            # Retrieve the test kernel instance from the application container
            kernel: ITestKernel = app.make(ITestKernel)

            # Run the test suite using the kernel's handle method
            kernel.handle()

        except Exception as e:

            # Raise a CLI-specific runtime error if any exception occurs
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}") from e
