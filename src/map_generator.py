import os
from typing import Any, Dict
from mazegen import MazeGenerator


class MapGenerator:
    def __init__(self, width: int = 14, height: int = 14) -> None:
        entry = "0,0"
        exit_coords = f"{width-1},{height-1}"

        self.level_config: Dict[int, str] = {
            1: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_1.txt\n"
                "PERFECT=False\nSEED=42\n"
            ),
            2: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_2.txt\n"
                "PERFECT=False\n"
            ),
            3: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_3.txt\n"
                "PERFECT=False\n"
            ),
            4: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_4.txt\n"
                "PERFECT=False\n"
            ),
            5: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_5.txt\n"
                "PERFECT=False\n"
            ),
            6: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_6.txt\n"
                "PERFECT=False\n"
            ),
            7: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_7.txt\n"
                "PERFECT=False\n"
            ),
            8: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_8.txt\n"
                "PERFECT=False\n"
            ),
            9: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_9.txt\n"
                "PERFECT=False\n"
            ),
            10: (
                f"WIDTH={width}\nHEIGHT={height}\nENTRY={entry}\n"
                f"EXIT={exit_coords}\nOUTPUT_FILE=map_level_10.txt\n"
                "PERFECT=False\n"
            ),
        }

    def create_map(self, level: int) -> Any:
        width = 21
        height = 21

        config = (
            f"WIDTH={width}\nHEIGHT={height}\nENTRY={(0, 0)}\n"
            f"EXIT={(width - 1, height - 1)}\nOUTPUT_FILE=map_level_10.txt\n"
            "PERFECT=False\n"
        )

        if level in self.level_config:
            config = self.level_config[level]

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
