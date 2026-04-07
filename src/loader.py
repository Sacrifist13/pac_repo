import sys
import json
from pathlib import Path
from typing import List, Any
from .models import GameConfig


class Loader:
    """
    A utility class for managing configuration loading and terminal output.

    This class provides constants for ANSI escape sequences to format terminal
    output with colors and styles. Its primary responsibility is to handle
    the retrieval, validation, and parsing of external JSON configuration
    files required to initialize the game settings. It includes robust error
    handling to provide clear feedback during the application launch phase.
    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def load_config(self, argv: List[Any]) -> GameConfig:
        """
        Loads and validates the game configuration from a JSON file.

        This method parses command-line arguments to locate a configuration
        file. It performs several validation checks, ensuring the file
        exists, is a valid file type, and possesses a .json extension. It
        supports custom comment stripping (lines starting with '#') before
        deserializing the JSON content into a GameConfig object. If any
        validation or parsing error occurs, it prints a formatted critical
        error message to the console and returns a default configuration.

        Args:
            argv (List[Any]): The list of command-line arguments.

        Returns:
            GameConfig: An object containing the parsed settings or a
                default configuration if loading fails.
        """
        argv = sys.argv
        argc = len(sys.argv)

        if argc != 2:
            padded_key = f"{'Arguments':<25}"
            print(
                f"\n{self.RED}{self.BOLD}[=== CRITICAL LAUNCH ERROR ===]"
                f"{self.RESET}"
            )
            print(
                f"{self.RED}{self.BOLD}  * {self.RESET}"
                f"{self.YELLOW}{self.BOLD}{padded_key}{self.RESET} : "
                "You must provide exactly one configuration file."
            )
            print(
                f"\n{self.BOLD}Usage:{self.RESET} python3 pac-man.py config."
                "json\n"
            )
            return GameConfig()

        config_file = argv[1]

        config_file_path = Path(config_file)

        if (
            not config_file_path.is_file()
            or config_file_path.suffix != ".json"
        ):
            print(
                f"\n{self.RED}{self.BOLD}[=== CRITICAL LAUNCH ERROR ===]"
                f"{self.RESET}"
            )

            if not config_file_path.exists():
                reason = "File does not exist."
            elif not config_file_path.is_file():
                reason = "Target is not a file."
            else:
                reason = "File must have a .json extension."

            padded_key = f"{'config_file':<25}"
            print(
                f"{self.RED}{self.BOLD}  * {self.RESET}"
                f"{self.YELLOW}{self.BOLD}{padded_key}{self.RESET} : {reason}"
            )
            print(
                f"\n{self.BOLD}Usage:{self.RESET} python3 pac-man.py "
                f"config.json\n"
            )

            return GameConfig()

        try:
            with open(config_file_path, "r") as f:
                config_lines = [
                    line.strip()
                    for line in f.readlines()
                    if not line.strip().startswith("#")
                    if line.strip()
                ]
                config_raw = json.loads("".join(config_lines))

                game_config = GameConfig(**config_raw)

                return game_config

        except Exception as e:
            print(
                f"\n{self.RED}{self.BOLD}❌ [ERROR] {e}{self.RESET}\n",
                file=sys.stderr,
            )
            return GameConfig()
