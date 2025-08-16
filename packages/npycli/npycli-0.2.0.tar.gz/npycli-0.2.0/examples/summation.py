from sys import argv
from npycli import Command


def summation(first: float, *others: float) -> None:
    print(f'Sum: {sum((first,) + others)}')


if __name__ == '__main__':
    cmd: Command = Command.create(summation, name='sum', help='Sum a space separated list of numbers.')
    args: list[str] = argv[1:]  # Ignore first argument which is executable
    if len(args) == 0:
        print(cmd)
    else:
        cmd(args)
