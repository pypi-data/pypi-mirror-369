from sys import argv
from npycli import Command


def main(*nums: int) -> None:
    """
    Sum numbers together.
    :param nums: Numbers to sum.
    """
    print(sum(nums))


if __name__ == '__main__':
    Command.create(function=main, name='main')(argv[1:])
