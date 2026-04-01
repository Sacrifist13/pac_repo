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

            generator = MazeGenerator()

            generator.load_config("level.txt")
            generator.generate_logo()
            generator.generate_maze()
            generator.add_solutions()

            return (generator._maze, generator._logo_coordinate)

        except Exception as e:
            print(f"Error {e}")
            return ()

        finally:
            if os.path.exists("level.txt"):
                os.remove("level.txt")
