from enum import Enum, auto


class Directions(Enum):
    """
    Defines the four cardinal directions for entity movement.

    This enumeration is used by Pac-Man and the ghosts to determine their
    next heading on the grid. It facilitates collision detection and
    sprite orientation logic.
    """

    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class GameState(Enum):
    """
    Represents the high-level operational states of the application.

    This enum controls the top-level logic and rendering switches,
    determining whether the user is in a menu, actively playing,
    viewing high scores, or navigating through game-over and win screens.
    """

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SCORE = auto()
    INFO = auto()
    STARTING_LEVEL = auto()
    WIN = auto()


class PlayingState(Enum):
    """
    Represents specific sub-states during active gameplay.

    These states manage the flow within the PLAYING GameState, such as
    handling the transition when a level is passed, managing the power-up
    duration, or processing the sequence when Pac-Man dies.
    """

    RETREATE = auto()
    POWER = auto()
    DEATH = auto()
    LEVEL_PASS = auto()


class Mode(Enum):
    """
    Defines the behavioral and physical modes of game entities.

    This enum dictates how entities interact with one another. For ghosts,
    it determines if they are hunting (NORMAL), frightened (SCARED), or
    returning to base (EAT). For Pac-Man, it manages states like
    INVINCIBLE after a respawn.
    """

    NORMAL = auto()
    EAT = auto()
    INVINCIBLE = auto()
    SCARED = auto()
