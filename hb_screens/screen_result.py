from enum import Enum


class ScreenAction(str, Enum):

    LOAD_PREVIOUS = "previous"
    LOAD_NEXT = "next"
    QUIT_PROGRAM = "quit"

