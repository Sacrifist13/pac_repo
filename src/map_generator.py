import os
from typing import Any
from mazegen import MazeGenerator


class MapGenerator:
    def __init__(self, width: int = 13, height: int = 13) -> None:
        self.width = width
        self.height = height

    def create_map(self, level: int) -> Any:
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
