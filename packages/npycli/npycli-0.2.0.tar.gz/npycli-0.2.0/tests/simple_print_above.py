from sys import argv
from io import StringIO
from threading import Thread
from time import time, sleep
from npycli.ansi import send_ansi, SAVE_CURRENT_CURSOR_POSITION, SCROLL_DOWN, CURSOR_UP, INSERT_NEW_LINE, RESTORE_SAVED_CURRENT_CURSOR_POSITION
from npycli.command import Command


def print_above(*args, **kwargs) -> None:
    buffer: StringIO = StringIO()
    print(*args, **kwargs, flush=True, file=buffer)
    output: str = buffer.getvalue()

    if len(output) > 0 and output[-1] == '\n':
        output = output[:-1]
    line_count: int = output.count('\n') + 1

    send_ansi(SAVE_CURRENT_CURSOR_POSITION)
    send_ansi(SCROLL_DOWN.with_args(line_count))
    send_ansi(CURSOR_UP.with_args(line_count))
    send_ansi(INSERT_NEW_LINE, repeat=line_count)
    print(output, end='', flush=True)
    send_ansi(RESTORE_SAVED_CURRENT_CURSOR_POSITION)


def print_on_interval(total: int, interval: int) -> None:
    sleep(.1)
    start: float = time()
    i: int = 0
    while time() - start < total:
        print_above(f'Printed above:\n\titeration:{i}')
        i += 1
        sleep(interval)


def main(seconds: float, interval: float) -> None:
    if seconds <= 0 or interval <= 0:
        print('seconds and interval must be greater than 0')
        return

    if interval >= seconds:
        print('interval must be less than seconds')
        return

    print(__name__)
    printer: Thread = Thread(target=print_on_interval, args=(seconds, interval))
    printer.start()
    in_str: str = input('>')
    printer.join()
    print(in_str)


if __name__ == '__main__':
    if len(argv) == 1:
        argv.extend(['20', '1'])
    Command.create(function=main, name='main')(argv[1:])
