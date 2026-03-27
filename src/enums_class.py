from enum import Enum, auto


class Directions(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SCORE = auto()
    INFO = auto()
    STARTING_LEVEL = auto()


class PlayingState(Enum):
    RETREATE = auto()
    POWER = auto()
    DEATH = auto()
