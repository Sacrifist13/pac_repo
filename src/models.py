from typing import Any
from pydantic import BaseModel, Field, model_validator


class GameConfig(BaseModel):
    """
    Data model representing the game's configuration settings.

    This class uses Pydantic to define and validate global settings such as
    scoring values, player lives, level time limits, and external file paths.
    It acts as a single source of truth for game balancing and persistent
    data storage locations.
    """

    highscore_filename: str = Field(
        default="highscores.json",
        description="High Score file name",
    )
    lives: int = Field(default=3, ge=0, description="Player lives")
    points_per_pacgum: int = Field(default=10, description="Pacgum points")
    points_per_super_pacgum: int = Field(
        default=50, description="Super Pacgum points"
    )
    points_per_ghost: int = Field(default=200, description="Ghost points")
    seed: int = Field(default=42, description="Maze seed")
    level_max_time: int = Field(default=90, description="Max time per level")

    @model_validator(mode="before")
    @classmethod
    def check_config(cls, data: Any) -> Any:
        """
        Validates and sanitizes raw configuration data before model creation.

        This validator ensures that all input values from the JSON file meet
        specific game requirements (e.g., positive integers, correct file
        extensions). If a value is invalid or missing, it logs a formatted
        error message to the console and "clamps" the field to its default
        hardcoded value to ensure the game remains stable and playable.

        Args:
            data (Any): The raw dictionary parsed from the config file.

        Returns:
            Any: The sanitized dictionary with corrected values.
        """
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        if not isinstance(data, dict):
            return {}

        numeric_fields = [
            ("points_per_pacgum", 10),
            ("points_per_super_pacgum", 50),
            ("points_per_ghost", 200),
            ("seed", 42),
            ("level_max_time", 90),
        ]

        errors = []

        lives = data.get("lives")
        if lives is not None and (not isinstance(lives, int) or lives != 3):
            padded_key = f"{'lives':<25}"
            errors.append(
                f"{RED}{BOLD}  * {RESET}"
                f"{YELLOW}{BOLD}{padded_key}{RESET} : Must be exactly 3. "
                "Clamped to 3."
            )
            data["lives"] = 3

        for key, default_val in numeric_fields:
            val = data.get(key)
            if val is not None and (not isinstance(val, int) or val < 0):
                padded_key = f"{key:<25}"
                errors.append(
                    f"{RED}{BOLD}  * {RESET}"
                    f"{YELLOW}{BOLD}{padded_key}{RESET} : Must be a "
                    f"positive integer. Clamped to {default_val}."
                )
                data[key] = default_val

        filename = data.get("highscore_filename")
        if filename is not None and (
            not isinstance(filename, str) or not filename.endswith(".json")
        ):
            padded_key = f"{'highscore_filename':<25}"
            errors.append(
                f"{RED}{BOLD}  * {RESET}"
                f"{YELLOW}{BOLD}{padded_key}{RESET} : Must be a .json file"
                ". Clamped to 'highscores.json'."
            )
            data["highscore_filename"] = "highscores.json"

        if errors:
            print(f"\n{RED}{BOLD}[=== CONFIGURATION FILE ERROR ===]{RESET}")
            for error in errors:
                print(error)
            print()

        return data
