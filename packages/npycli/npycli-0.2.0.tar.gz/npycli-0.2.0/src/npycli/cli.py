from typing import Optional, Callable, Any
from shlex import split
from .command import Command
from .errors import EmptyEntriesError, CommandDoesNotExistError, CLIError


class CLI:
    def __init__(self, title: Optional[str] = None, prompt_marker: Optional[str] = None,
                 kwarg_prefix: Optional[str] = None, parsers: Optional[dict[type, Callable[[str], Any]]] = None,
                 env: Optional[dict] = None, retval_handler: Optional[Callable[[Command, Any], None]] = None,
                 error_handler: Optional[Callable[[Command, Exception], None]] = None) -> None:
        self.title: str = title or 'CLI'
        self.prompt_marker: str = prompt_marker or '>'
        self.kwarg_prefix: str = kwarg_prefix or '--'
        self.parsers: dict[type, Callable[[str], Any]] = parsers or {}
        self.env: dict = env or {}
        self._retval_handler: Optional[Callable[[Command, Any], None]] = retval_handler
        self._error_handler: Optional[Callable[[Command, Exception], None]] = error_handler
        self._commands: list[Command] = []

    @property
    def commands(self) -> list[Command]:
        """
        Get commands current added to this CLI.
        :return: commands
        """

        return self._commands

    @property
    def prompt_entry_marker(self) -> str:
        """
        Get the prompt entry marker for this CLI
        :return: *title* *prompt marker*
        """

        return f'{self.title}{self.prompt_marker}'

    def get_command(self, name: str) -> Optional[Command]:
        """
        Get the command with the specified name. If it does not exist, `None` is returned.
        :param name: Name of command.
        :return: `Command` that matches `name`
        """

        try:
            return next(filter(lambda cmd: name in cmd.names, self.commands))
        except StopIteration:
            return None

    def add_command(self, command: Command) -> None:
        """
        Append a `Command` to the list of commands on this CLI.
        :param command: `Command` to add.
        :return: `None`
        """

        self._commands.append(command)

    def cmd(self, name: Optional[str] = None, names: Optional[tuple[str, ...]] = None, help: Optional[str] = None) \
            -> Callable[[Callable], Callable]:
        """
        Curry function that creates a decorator that creates a `Command` from the function.
        :param name: Name of `Command`
        :param names: Names and aliases of `Command`. *Cannot be used with `name`*
        :param help: Help string
        :return: Decorator
        """

        def decorator(function: Callable) -> Callable:
            self.add_command(
                Command.create(function=function, name=name, names=names, help=help, kwarg_prefix=self.kwarg_prefix))
            return function

        return decorator

    def retvals(self) -> Callable[[Callable[[Command, Any], None]], Callable]:
        """
        Curry function that creates a decorator to specify a return value handler function.
        :return: Decorator
        """

        def decorator(function: Callable[[Command, Any], None]) -> Callable[[Command, Any], None]:
            self._retval_handler = function
            return function

        return decorator

    def errors(self) -> Callable[[Callable[[Command, Exception], None]], Callable]:
        """
        Curry function that creates a decorator to specify an error handler function.
        :return: Decorator
        """

        def decorator(function: Callable[[Command, Exception], None]) \
                -> Callable[[Command, Exception], None]:
            self._error_handler = function
            return function

        return decorator

    def exec(self, entries: list[str]) -> Optional[Any]:
        """
        Execute a command from specified `entries`.
        :param entries: Command name and arguments.
        :return: Command function return value
        """

        if not entries:
            raise EmptyEntriesError('Nothing was entered.')
        name: str = entries.pop(0)
        if (command := self.get_command(name)) is None:
            raise CommandDoesNotExistError(f'Command {name} does not exist.')

        try:
            retval: Any = command(entries, self.parsers)
        except CLIError as cli_error:
            if self._error_handler is None:
                cli_error.cli = self
                raise cli_error
            self._error_handler(command, cli_error)
            return None
        except Exception as error:
            if self._error_handler is None:
                raise CLIError(f'An exception was raised running {command.name}: {error}', cli=self,
                               command=command) from error
            self._error_handler(command, error)
            return None

        if self._retval_handler is not None:
            self._retval_handler(command, retval)
        return retval

    def prompt(self) -> Optional[Any]:
        """
        Prompt the user for entries to `exec` on this CLI.
        :return: Command function return value
        """

        return self.exec(split(input(self.prompt_entry_marker)))
