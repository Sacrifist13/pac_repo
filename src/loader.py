from pathlib import Path
from .models import GameConfig

class Loader:
    def load_config(self, config_file : str) -> GameConfig:
        config_file_path = Path(config_file)

        if not config_file_path.is_file() or config_file_path.suffix != ".json":
            