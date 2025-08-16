from io import StringIO
from npycli.ansi import (
    send_ansi,
    SAVE_CURRENT_CURSOR_POSITION,
    CURSOR_DOWN,
    CURSOR_UP,
    INSERT_NEW_LINE,
    RESTORE_SAVED_CURRENT_CURSOR_POSITION,
    SELECT_CHARACTER_RENDITION,
    FOREGROND_RED,
    BACKGROND_WHITE,
    SET_BOLD_MODE,
    SCR_RESET
)

def print_above(*args, **kwargs) -> None:
    '''
    Print above the current line.
    '''

    # Use print with file=buffer so this function can be used just like regular print
    buffer: StringIO = StringIO()
    current_is_empty = kwargs.pop('current_is_empty') if 'current_is_empty' in kwargs else False
    print(*args, **kwargs, flush=True, file=buffer)
    output: str = buffer.getvalue()

    if len(output) > 0 and output[-1] == '\n': # Remove trailing \n, if empty newline wanted, supply 2
        output = output[:-1]
    line_count: int = output.count('\n') + 1

    send_ansi(SAVE_CURRENT_CURSOR_POSITION)
    if current_is_empty:
        print()
        send_ansi(CURSOR_UP.with_args(2))

    # These ansi control commands may be supplied with arguments
    print()
    send_ansi(CURSOR_UP.with_args(line_count))
    # This one doesn't have argument, so we just repeat the command
    send_ansi(INSERT_NEW_LINE, repeat=line_count)

    # Flush, just in case current cursor position gets moved after output
    print(output, end='', flush=True)
    send_ansi(RESTORE_SAVED_CURRENT_CURSOR_POSITION)
    send_ansi(CURSOR_DOWN.with_args(line_count))


# Prints in order
print(1)
print(2)
print(4)
print_above(3, current_is_empty=True) #This line will be an empty line, so current_is_empty = True


SELECT_CHARACTER_RENDITION(SET_BOLD_MODE, FOREGROND_RED, BACKGROND_WHITE)
# Or
print(1)
print(2)
print(4, end='')
print_above(3)
SELECT_CHARACTER_RENDITION(SCR_RESET)
