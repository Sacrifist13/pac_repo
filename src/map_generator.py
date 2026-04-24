import os
from typing import Any
from mazegen import MazeGenerator


class MapGenerator:
    """
    Generates procedural maze maps for each game level.

    Wraps the MazeGenerator utility to produce level-specific maps of
    increasing size. Each map is encoded as a 3D grid where each cell
    contains a wall bitmask and an additional state value. Special cells
    with value 15 are tracked separately as logo coordinates used to
    position entities on the map.
    """

    def __init__(self, width: int = 13, height: int = 13) -> None:
        """
        Initializes the MapGenerator with base grid dimensions.

        Args:
            width (int): Base number of columns before level scaling.
                Defaults to 13.
            height (int): Base number of rows before level scaling.
                Defaults to 13.
        """
        self.width = width
        self.height = height

    def create_map(self, level: int) -> Any:
        """
        Generates and returns the maze map for a given level.

        Scales the map dimensions by adding the level number to both the
        base width and height. Writes a temporary configuration file,
        runs the maze generator, converts the output to a hex-encoded
        grid, and parses it into a 3D list structure. Cells with value 15
        are collected as logo coordinates. The temporary config file is
        always removed after generation, regardless of success or failure.

        Args:
            level (int): The current game level, used to scale map size
                and optionally fix the random seed for reproducibility.

        Returns:
            Tuple[List[List[List[int]]], List[Tuple[int, int]]]: A tuple
                containing the maze grid and a list of (x, y) grid
                coordinates marking logo cell positions. Returns an empty
                tuple if generation fails.
        """
        width = self.width + level
        height = self.height + level
        entry = "0,0"
        exit_coords = f"{width-1},{height-1}"

        config = (
            f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
            f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_{level}.txt\n"
            "PERFECT=False\n"
        )

        if level == 1:
            config += "SEED=42\n"

        for key in [
            "HEIGHT",
            "WIDTH",
            "ENTRY",
            "EXIT",
            "PERFECT",
            "SEED",
            "OUTPUT_FILE",
        ]:
            os.environ.pop(key, None)

        try:
            with open("level.txt", "w") as f:
                f.write(config)

            generator = MazeGenerator("level.txt")

            if level != 1:
                generator.seed = None

            map = generator.maze_gen()
            map_hex_str = generator.convert_hex_maze(map)

            maze_map = [
                [[int(c, 16), 0] for c in line] for line in map_hex_str
            ]

            logo_coordinate = []

            for x, col in enumerate(maze_map):
                for y, block in enumerate(col):
                    if maze_map[y][x][0] == 15:
                        logo_coordinate.append((x, y))

            return (maze_map, logo_coordinate)

        except Exception as e:
            print(f"Error {e}")
            return ()

        finally:
            if os.path.exists("level.txt"):
                os.remove("level.txt")
