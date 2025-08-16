from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ANSIControl:
    CSI = '\u001B['

    name: str
    sequence: str
    no_of_arguments: int = field(default=0)
    no_of_default_arguments: int = field(default=0)

    @staticmethod
    def send(ansi_control: ANSIControl | str, repeat: int = 1) -> None:
        if isinstance(ansi_control, ANSIControl):
            for _ in range(repeat):
                print(str(ansi_control), end='', flush=True)
        else:
            if not ansi_control.startswith(ANSIControl.CSI):
                raise ValueError(f'Sequence {ansi_control} does not start with ANSI CSI')
            for _ in range(repeat):
                print(ansi_control, end='', flush=True)

    def __post_init__(self) -> None:
        self._with_no_args: Optional[ANSIControl] = None

    @property
    def has_args(self) -> bool:
        return self._with_no_args is not None

    @property
    def with_no_args(self) -> ANSIControl:
        if self._with_no_args is None:
            return self
        return self._with_no_args

    def with_args(self, *args) -> ANSIControl:
        if self.has_args:
            return self

        if len(args) > self.no_of_arguments:
            raise ValueError(f'{ANSIControl.with_args}({self.name}) Too many arguments supplied')

        if len(args) < self.no_of_arguments - self.no_of_default_arguments:
            raise ValueError(f'{ANSIControl.with_args}({self.name}) Not enough arguments supplied')

        with_args: ANSIControl = ANSIControl(**asdict(self))
        with_args.sequence = ''

        last: int = len(args) - 1
        for position, arg in enumerate(args):
            with_args.sequence += str(arg)
            if position != last:
                with_args.sequence += ';'
        with_args.sequence += self.sequence

        with_args._with_no_args = self
        return with_args

    def __call__(self, *args, repeat: int = 1) -> ANSIControl:
        if self.has_args:
            assert self._with_no_args is not None
            replaced_args: ANSIControl = self._with_no_args.with_args(*args)
            ANSIControl.send(replaced_args, repeat)
            return replaced_args
        else:
            ANSIControl.send(self.with_args(*args), repeat)
            return self

    def __str__(self) -> str:
        if not self.has_args:
            return str(self.with_args())
        return f'{ANSIControl.CSI}{self.sequence}'


def send_ansi(ansi_control: ANSIControl | str, repeat: int = 1) -> None:
    ANSIControl.send(ansi_control, repeat)


CURSOR_UP: ANSIControl = ANSIControl('CURSOR_UP', 'A', 1, 1)
CURSOR_DOWN: ANSIControl = ANSIControl('CURSOR_DOWN', 'B', 1, 1)
CURSOR_FORWARD: ANSIControl = ANSIControl('CURSOR_FORWARD', 'C', 1, 1)
CURSOR_BACK: ANSIControl = ANSIControl('CURSOR_BACK', 'D', 1, 1)
CURSOR_NEXT_LINE: ANSIControl = ANSIControl('CURSOR_NEXT_LINE', 'E', 1, 1)
CURSOR_PREVIOUS_LINE: ANSIControl = ANSIControl('CURSOR_PREVIOUS_LINE', 'F', 1, 1)
CURSOR_HORIZONTAL_ABSOLUTE: ANSIControl = ANSIControl('CURSOR_HORIZONTAL_ABSOLUTE', 'G', 1, 1)
CURSOR_POSITION: ANSIControl = ANSIControl('CURSOR_POSITION', 'H', 2)
ERASE_IN_DISPLAY: ANSIControl = ANSIControl('ERASE_IN_DISPLAY', 'J', 1, 1)
ERASE_IN_DISPLAY_TO_END: int = 0
ERASE_IN_DISPLAY_TO_BEGINNING: int = 1
ERASE_IN_DISPLAY_ALL: int = 2
ERASE_IN_LINE: ANSIControl = ANSIControl('ERASE_IN_LINE', 'K', 1, 1)
ERASE_IN_LINE_END: int = 0
ERASE_IN_LINE_BEGINNING: int = 1
ERASE_IN_LINE_ALL: int = 2
SCROLL_UP: ANSIControl = ANSIControl('SCROLL_UP', 'T', 1, 1)
SCROLL_DOWN: ANSIControl = ANSIControl('SCROLL_DOWN', 'S', 1, 1)
HORIZONTAL_VERTICAL_POSITION: ANSIControl = ANSIControl('HORIZONTAL_VERTICAL_POSITION', 'f', 2)
SELECT_CHARACTER_RENDITION: ANSIControl = ANSIControl('SELECT_CHARACTER_RENDITION', 'm', 3, 3)
AUX_PORT_ON: ANSIControl = ANSIControl('AUX_PORT_ON', '5i')
AUX_PORT_OFF: ANSIControl = ANSIControl('AUX_PORT_OFF', '4i')
DEVICE_STATUS_REPORT: ANSIControl = ANSIControl('DEVICE_STATUS_REPORT', '6n')

INSERT_NEW_LINE: ANSIControl = ANSIControl('INSERT_NEW_LINE', 'L')

SAVE_CURRENT_CURSOR_POSITION: ANSIControl = ANSIControl('SAVE_CURRENT_CURSOR_POSITION', 's')
RESTORE_SAVED_CURRENT_CURSOR_POSITION: ANSIControl = ANSIControl('RESTORE_SAVED_CURRENT_CURSOR_POSITION', 'u')
SHOW_CURSOR: ANSIControl = ANSIControl('SHOW_CURSOR', '?25h')
HIDE_CURSOR: ANSIControl = ANSIControl('HIDE_CURSOR', '?25l')

REMOVE_LINE: ANSIControl = ANSIControl('REMOVE_LINE', 'M')
REMOVE_CHARACTER: ANSIControl = ANSIControl('REMOVE_CHARACTER', 'P')


SCR_RESET: int = 0


FOREGROND_BLACK: int = 30
FOREGROND_RED: int = 31
FOREGROND_GREEN: int = 32
FOREGROND_YELLOW: int = 33
FOREGROND_BLUE: int = 34
FOREGROND_MAGENTA: int = 35
FOREGROND_CYAN: int = 36
FOREGROND_WHITE: int = 37
FOREGROND_DEFAULT: int = 38


BACKGROND_BLACK: int = FOREGROND_BLACK + 10
BACKGROND_RED: int = FOREGROND_RED + 10
BACKGROND_GREEN: int = FOREGROND_GREEN + 10
BACKGROND_YELLOW: int = FOREGROND_YELLOW + 10
BACKGROND_BLUE: int = FOREGROND_BLUE + 10
BACKGROND_MAGENTA: int = FOREGROND_MAGENTA + 10
BACKGROND_CYAN: int = FOREGROND_CYAN + 10
BACKGROND_WHITE: int = FOREGROND_WHITE + 10
BACKGROND_DEFAULT: int = FOREGROND_DEFAULT + 10


SET_BOLD_MODE: int = 1
SET_DIM_MODE: int = 2
SET_ITALIC_MODE: int = 3
SET_UNDERLINE_MODE: int = 4
SET_BLINKING_MODE: int = 5
SET_INVERSE_MODE: int = 7
SET_INVISIBLE_MODE: int = 8
SET_STRIKETHROUGH_MODE: int = 9
