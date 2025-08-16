from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import CLI
    from .command import Command


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super(ParsingError, self).__init__(*args)


class MissingKeywordArgumentValueError(ParsingError):
    def __init__(self, *args) -> None:
        super(MissingKeywordArgumentValueError, self).__init__(*args)


class TooManyArgumentsError(ParsingError):
    def __init__(self, *args) -> None:
        super(TooManyArgumentsError, self).__init__(*args)


class CLIError(Exception):
    def __init__(self, *args, cli=None, command=None) -> None:
        super(CLIError, self).__init__(*args)
        self.cli: Optional[CLI] = cli
        self.command: Optional[Command] = command


class EmptyEntriesError(CLIError):
    def __init__(self, *args, **kwargs) -> None:
        super(EmptyEntriesError, self).__init__(*args, **kwargs)


class CommandDoesNotExistError(CLIError):
    def __init__(self, *args, **kwargs) -> None:
        super(CommandDoesNotExistError, self).__init__(*args, **kwargs)


class CommandArgumentError(CLIError):
    def __init__(self, *args, **kwargs) -> None:
        super(CommandArgumentError, self).__init__(*args, **kwargs)
