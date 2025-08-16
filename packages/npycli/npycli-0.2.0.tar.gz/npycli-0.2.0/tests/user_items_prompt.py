from typing import Optional
from npycli import CLI, Command, EmptyEntriesError, CommandDoesNotExistError
from npycli.kwarg_alasing import alias_cmd_kwargs

cli = CLI(title='user-items', prompt_marker='->', env={'user-items': {}})


def __log_out__(text: str) -> None:
    with open(f'{__name__}.log', 'a+', encoding='utf-8') as log_file:
        log_file.write(text)


def user_items() -> dict[str, str]:
    return cli.env['user-items']


@cli.cmd(name='add')
@alias_cmd_kwargs({'key': ('k',), 'value': ('v',)})
def add_item(key: str, value: str) -> str:
    if key in user_items():
        return f'Key {key} already exists'
    user_items()[key] = value
    return f'Added {key}: {value}'


@cli.cmd(name='change')
def change_item(key: str, value: str) -> str:
    if key not in user_items():
        return f'Key {key} does not exist'
    old_value: str = user_items()[key]
    user_items()[key] = value
    return f'Swapped value of {key} from {old_value} for {value}'


@cli.cmd(name='show')
def show_item(key: Optional[str] = None) -> str:
    if key is None:
        s = ''
        for k, v in user_items().items():
            s += f'{k}: {v}\n'
        return s
    if key not in user_items():
        return f'Key {key} does not exist'
    return f'{key}: {user_items()[key]}'


@cli.cmd(names=('delete', 'del', 'remove', 'rm', 'pop'))
def delete_item(key: str) -> str:
    if key not in user_items():
        return f'Key {key} does not exist'
    return f'Popped {key}: {user_items().pop(key)}'


@cli.cmd(name='help')
def show_help() -> str:
    help_str = ''
    for command in cli.commands:
        help_str += f'{command}{"" if command.help is None else f"\n\t{command.help}"}\n'
    return help_str


@cli.retvals()
def retvals(command: Command, retval: str) -> None:
    __log_out__(f'{command.name}:\n{retval}\n')
    print(retval)


@cli.errors()
def errors(command: Optional[Command], exception: Exception) -> None:
    print(
        f'Exception {exception.__class__.__name__} thrown: {exception} | {exception.args} - {f" Running command {command.name}" if command is not None else ""}')


def main() -> None:
    while True:
        try:
            cli.prompt()
        except CommandDoesNotExistError as cmd_error:
            print(cmd_error.args[0])
        except EmptyEntriesError:
            ...


if __name__ == '__main__':
    main()
