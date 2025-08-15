from abc import ABC, abstractmethod
from typing import List, Optional

class IReactor(ABC):

    @abstractmethod
    def call(
        self,
        signature: str,
        args: Optional[List[str]] = None
    ):
        """
        Executes a command by its signature with optional command-line arguments.

        This method retrieves a registered command by its signature, validates any provided
        arguments against the command's argument parser, and executes the command's handle
        method with the parsed arguments and application context.

        Parameters
        ----------
        signature : str
            The unique signature identifier of the command to execute.
        args : Optional[List[str]], default None
            Command-line arguments to pass to the command. If None, no arguments are provided.

        Returns
        -------
        None
            This method does not return any value. The command's handle method is called
            directly for execution.

        Raises
        ------
        ValueError
            If the command with the specified signature is not found in the registry.
        SystemExit
            If argument parsing fails due to invalid arguments provided.
        """
        pass