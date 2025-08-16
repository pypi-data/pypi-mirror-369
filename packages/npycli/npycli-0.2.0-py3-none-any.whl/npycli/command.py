from __future__ import annotations
from typing import Callable, Optional, Any
from dataclasses import dataclass, field
from inspect import signature, Signature, Parameter, getdoc
from .errors import ParsingError, CommandArgumentError
from .parsing import type_from_annotation, extract_positionals_keywords, parse_args_as


@dataclass
class Command:
    __CMD_ATTR__ = '__cmd__'
    __FUTURE_CMD_ATTR__ = '__future_cmd__'

    function: Callable
    names: tuple[str, ...]
    help: Optional[str] = field(default=None)
    kwarg_prefix: str = field(default_factory=lambda: '--')

    @staticmethod
    def create(function: Callable, name: Optional[str] = None, names: Optional[tuple[str, ...]] = None,
               help: Optional[str] = None, kwarg_prefix: Optional[str] = None) -> Command:
        """
        Create a Command, wrapper for using either `name` or `names`
        :param function: Function to execute `Command` with.
        :param name: Name of `Command`
        :param names: Name and aliases of `Command`. *Cannot be used with `name`*
        :param help: Help string
        :param kwarg_prefix: Prefix of argument to represent next argument is the value of this argument's keyword
        :return: Created `Command`
        """

        if names is None:
            if name:
                names = name,
            else:
                names = function.__name__,

        return Command(function=function, names=names, help=help,
                       kwarg_prefix=kwarg_prefix or "--")

    @property
    def name(self) -> str:
        """
        Primary name of this `Command`
        :return: Name
        """

        return self.names[0]

    @property
    def aliases(self) -> tuple[str, ...]:
        """
        Aliases of this `Command`
        :return: Aliases
        """

        return self.names[1:]

    @property
    def details(self) -> str:
        """
        Details of this command, which include but are not limited to:
        * Name
        * Aliases
        * Arguments
        * Help string
        :return: Details
        """

        return self._details

    def add_detail(self, detail: str) -> None:
        """
        Add details to this `Command`
        :param detail: Specific detail
        :return: `None`
        """

        if not self._details[-1] == '\t':
            self._details += '\t'
        self._details += detail

    def exec_with(self, args: list[str], parsers: Optional[dict[type, Callable[[str], Any]]] = None) -> Any:
        """
        Execute this `Command` with specified arguments and parsers
        :param args: Arguments
        :param parsers: Custom parsers to parse arguments with.
        :return:
        """

        positionals, keywords = extract_positionals_keywords(args, self.kwarg_prefix)
        args, kwargs = parse_args_as(positionals, keywords, self._positional_types, self._keyword_types,
                                     self._var_args_index, self._var_args_parser, parsers)
        try:
            return self.function(*args, **kwargs)
        except TypeError as type_error:
            if self._is_argument_error(type_error):
                raise CommandArgumentError(*type_error.args)
            raise type_error
        except ParsingError as parsing_error:
            raise CommandArgumentError(*parsing_error.args)

    def _validate_data(self) -> None:
        if not callable(self.function):
            raise TypeError(f'{Command._validate_data} -> {self.function} is not callable.')
        if not isinstance(self.names, tuple) or not all(isinstance(name, str) for name in self.names):
            raise TypeError(f'{Command} names must be a {tuple} of {str}.')
        if not self.names:
            raise ValueError(f'{Command} names must not be empty.')
        for name in self.names:
            for c in name:
                if c.isspace():
                    raise ValueError(f'Name for {self.function} cannot contain whitespace: {name}')
        if getattr(self.function, Command.__CMD_ATTR__, None) is not None:
            raise TypeError(f'Function {self.function} is already a {Command}.')
        if self.help is not None and not isinstance(self.help, str):
            raise TypeError(f'{Command} help must be a {str}.')

    def _attach_self(self) -> None:
        setattr(self.function, Command.__CMD_ATTR__, self)

    def _extract_signature(self) -> None:
        self._signature: Signature = signature(self.function)
        self._required_parameters: list[Parameter] = []
        self._optional_parameters: list[Parameter] = []
        self._positional_types: list[type] = []
        self._keyword_types: dict[str, type] = {}
        self._has_var_args: bool = False
        self._var_args_index: Optional[int] = None
        self._has_var_kwargs: bool = False
        self._var_args_parser: Optional[type] = None

        for index, parameter in enumerate(self._signature.parameters.values()):
            if parameter.default == parameter.empty:
                self._required_parameters.append(parameter)
            else:
                self._optional_parameters.append(parameter)

            if parameter.kind == Parameter.VAR_POSITIONAL:
                self._var_args_parser = str if parameter.annotation == parameter.empty \
                    else type_from_annotation(parameter.annotation)
                self._has_var_args = True
                self._var_args_index = index
                continue
            if parameter.kind == Parameter.VAR_KEYWORD:
                self._has_var_kwargs = True
                continue

            parameter_type: type= str if parameter.annotation == parameter.empty \
                else type_from_annotation(parameter.annotation)
            self._positional_types.append(parameter_type)
            self._keyword_types[parameter.name] = parameter_type

    def _generate_details(self) -> None:
        self._details: str = ''
        last = len(self.names) - 1
        for index, name in enumerate(self.names):
            self._details += name
            if index != last:
                self._details += ' '

        parameters = self._signature.parameters.values()

        if len(parameters) == 0:
            return

        self._details += '\t'
        last = len(parameters) - 1
        for index, parameter in enumerate(self._signature.parameters.values()):
            arg_type = str if parameter.annotation == parameter.empty else type_from_annotation(parameter.annotation)
            if parameter.kind == Parameter.VAR_POSITIONAL:
                self._details += '<*'
            elif parameter.kind == Parameter.VAR_KEYWORD:
                self._details += '<**'
            else:
                self._details += '<'
            self._details += parameter.name

            if parameter.default != parameter.empty:
                self._details += '?'
            if arg_type == str:
                self._details += '>'
            else:
                self._details += f': {arg_type.__name__}>'

            if index != last:
                self._details += ' '

        if self.help is None or self.help.strip() == '':
            self.help = getdoc(self.function)
        else:
            self._details += f'\t{self.help}'

    def _callback_futures(self) -> None:
        if not hasattr(self.function, Command.__FUTURE_CMD_ATTR__):
            return
        for callback in getattr(self.function, Command.__FUTURE_CMD_ATTR__):
            callback(self)

    def __post_init__(self) -> None:
        self._validate_data()
        self._attach_self()
        self._extract_signature()
        self._generate_details()
        self._callback_futures()

    def _is_argument_error(self, type_error: TypeError) -> bool:
        return type_error.args[0].startswith(f'{self.function.__name__}(')

    def __call__(self, args: list[str], parsers: Optional[dict[type, Callable[[str], Any]]] = None) -> Any:
        return self.exec_with(args, parsers)

    def __str__(self) -> str:
        return self.details


def is_cmd(function: Callable) -> bool:
    return hasattr(function, Command.__CMD_ATTR__)


def cmd(function: Callable) -> Command:
    if is_cmd(function):
        return getattr(function, Command.__CMD_ATTR__)
    raise ValueError(f"{function} is not a command. Use {is_cmd}.")


def future_cmd(function: Callable, callback: Callable[[Command], None]) -> None:
    if is_cmd(function):
        raise \
            TypeError(f'function {function} is already not a future command, it is already a command: {cmd(function)}')
    if not hasattr(function, Command.__FUTURE_CMD_ATTR__):
        setattr(function, Command.__FUTURE_CMD_ATTR__, [])
    getattr(function, Command.__FUTURE_CMD_ATTR__).append(callback)
