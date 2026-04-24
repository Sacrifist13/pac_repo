from enum import Enum


class CELL(Enum):
    """
    Enumeration representing the possible states of a maze cell.

    Each value corresponds to a specific role a cell can play during
    maze generation and pathfinding. These states are used internally
    by the MazeGenerator to track cell types and mark traversal progress.

    Attributes:
        WALL: The cell is a solid wall and cannot be traversed.
        EMPTY: The cell is an open passage with no special designation.
        FIND: The cell has been discovered during pathfinding traversal.
        PATH: The cell is part of a valid route through the maze.
        START: The cell is the designated entry point of the maze.
        EXIT: The cell is the designated exit point of the maze.
    """
    WALL = 0
    EMPTY = 1
    FIND = 3
    PATH = 4
    START = 6
    EXIT = 7
