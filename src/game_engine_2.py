import sys
import pygame
from pathlib import Path
from typing import List, Dict, Any, Tuple
from .loader import Loader
from .enums_class import PlayingState, GameState, Directions


class GameEngine:
    WIDTH = 800
    HEIGHT = 800
    BLACK = (0, 0, 0)
    GRAY = (155, 155, 155)
    PACMAN_YELLOW = (255, 255, 0)
    NEON_BLUE = (33, 33, 255)
    NEON_PINK = (255, 20, 147)

    def _init_game(self) -> None:
        self.state = GameState.MENU
        self.img: Dict[str, pygame.Surface] = {}
        self.sound: Dict[str, Any] = {}
        self.score = 0

        loader = Loader()
        self.config = loader.load_config(sys.argv)

        self.lives = self.config.lives

        assets_dir = Path("assets")

        for img in assets_dir.rglob("*.png"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()

        for sound in assets_dir.rglob("*.wav"):
            sound_name = sound.name.split(".")[0]
            self.sound[sound_name] = pygame.mixer.Sound(sound)

        self.home_page: Dict[Any, Any] = {
            "counter": 0,
            "anim_counter": 0,
            "pos_x": 0,
            1: {
                "ghosts": [
                    self.img["blinky_right"],
                    self.img["clyde_right"],
                    self.img["inky_right"],
                    self.img["pinky_right"],
                ],
                "pac_man": [
                    pac_img
                    for key, pac_img in self.img.items()
                    if key.startswith("pac_")
                    if "gum" not in key
                ],
            },
            2: {
                "pac_man": [
                    pac_img
                    for key, pac_img in self.img.items()
                    if "pac_" in key
                ],
                "scared": [self.img["scared_basic"], self.img["scared_white"]],
            },
            "text": {
                "Start Game": [(0, 0), (0, 0), False],
                "View Highscores": [(0, 0), (0, 0), False],
                "Instructions": [(0, 0), (0, 0), False],
                "Exit": [(0, 0), (0, 0), False],
            },
            "Back": [(0, 0), (0, 0), False],
        }

        self.home_page["pos_x"] = -(
            self.home_page[1]["ghosts"][0].get_width() * 5
        ) - (60)
        self.home_page["start_x"] = -self.home_page["pos_x"]

        font_size = 40
        self.font_back = pygame.font.Font("assets/font/back.otf", font_size)
        self.font_front = pygame.font.Font("assets/font/front.otf", font_size)

        self.font_back_countdown = pygame.font.Font(
            "assets/font/back.otf", font_size * 3
        )
        self.font_front_countdown = pygame.font.Font(
            "assets/font/front.otf", font_size * 3
        )

        self.font_basic = pygame.font.Font("assets/font/basic.ttf", 14)
