import os
import sys
import pygame
from pathlib import Path
from typing import Dict, Any, Union, Optional


def get_resource_path(*paths: str) -> str:
    """
    Resolve absolute path for dev and PyInstaller.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, *paths)


class AssetsManager:
    """
    Central controller for loading, storing, and managing game resources.

    This class handles the discovery and initialization of all external
    multimedia assets, including images (PNG, JPEG), sound effects (WAV),
    and custom fonts. It maintains specialized dictionaries for raw and
    scaled game assets and provides a unified interface for playing audio
    tracks and sound effects with volume control.
    """

    def __init__(self) -> None:
        """
        Initializes the asset containers and default audio state.
        """
        self.img: Dict[str, Union[pygame.surface.Surface, pygame.Surface]] = {}
        self.icon: Union[pygame.surface.Surface, pygame.Surface]
        self.sound: Dict[str, Any] = {}
        self.game_img: Dict[str, Any] = {}
        self.countdown_play = False
        self.music_load = False
        self.music_on = True

    def play_sound(
        self, media: Optional[str], sound: Any, loop: bool, volume: float
    ) -> None:
        """
        Plays a music file or a sound effect based on availability.

        Args:
            media (str | None): Path to a music file. If provided, used with
                pygame.mixer.music.
            sound (Any): A pygame.mixer.Sound object. Used if media is None.
            loop (bool): Whether to loop the music indefinitely.
            volume (float): Audio volume level (clamped between 0.1 and 1.0).
        """
        if not self.music_on:
            self.music_load = False
            return

        if volume < 0.1 or volume > 1:
            volume = 0.5

        if media:
            media_path = get_resource_path(media)

            if loop:
                pygame.mixer.music.load(media_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.load(media_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(1)
        else:
            sound.set_volume(volume)
            sound.play()

    def init_game(self) -> None:
        """
        Scans the assets directory to load images, sounds, and fonts.

        Automatically populates the internal dictionaries by recursively
        searching for supported file formats. It also initializes the
        various font objects used for menus, gameplay HUD, and countdowns.
        """
        assets_dir = Path(get_resource_path("assets"))

        for img in assets_dir.rglob("*.png"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()
            if "icon" in img.parts:
                self.icon = pygame.image.load(img).convert_alpha()

        for img in assets_dir.rglob("*.jpeg"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()

        for sound in assets_dir.rglob("*.wav"):
            sound_name = sound.name.split(".")[0]
            self.sound[sound_name] = pygame.mixer.Sound(sound)

        font_size = 40
        self.f_back = pygame.font.Font(
            get_resource_path("assets", "font", "back.otf"), font_size
        )
        self.f_front = pygame.font.Font(
            get_resource_path("assets", "font", "front.otf"), font_size
        )

        self.f_back_over = pygame.font.Font(
            get_resource_path("assets", "font", "back.otf"),
            int(font_size / 1.5),
        )
        self.f_front_over = pygame.font.Font(
            get_resource_path("assets", "font", "front.otf"),
            int(font_size / 1.5),
        )

        self.f_back_countdown = pygame.font.Font(
            get_resource_path("assets", "font", "back.otf"), font_size * 3
        )
        self.f_front_countdown = pygame.font.Font(
            get_resource_path("assets", "font", "front.otf"),
            font_size * 3,
        )

        self.f_basic = pygame.font.Font(
            get_resource_path("assets", "font", "basic.ttf"), 14
        )
        self.f_basic_s = pygame.font.Font(
            get_resource_path("assets", "font", "basic.ttf"), 11
        )

    def load_game_img(self, cell_size: int) -> None:
        """
        Scales raw image assets to fit the specific game grid dimensions.

        This method processes the previously loaded raw images to create
        game-ready versions of Pac-Man, ghosts (in all states), gums,
        and level keys. Scaling is based on the provided cell_size to
        ensure visual consistency across different display resolutions.

        Args:
            cell_size (int): The pixel size of a single map cell.
        """
        self.game_img["pac_man"] = {
            key: pygame.transform.scale(
                img,
                (
                    int(cell_size / 1.5),
                    int(cell_size / 1.5),
                ),
            )
            for key, img in self.img.items()
            if key.startswith("pac_")
            if "gum" not in key
        }

        self.game_img["blinky"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("blinky")
        }

        self.game_img["clyde"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("clyde")
        }

        self.game_img["inky"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("inky")
        }

        self.game_img["pinky"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("pinky")
        }

        self.game_img["pac_gum"] = pygame.transform.scale(
            self.img["pac_gum"],
            (
                cell_size // 6,
                cell_size // 6,
            ),
        )

        self.game_img["super_pac_gum"] = pygame.transform.scale(
            self.img["pac_gum"],
            (
                cell_size // 3,
                cell_size // 3,
            ),
        )

        self.game_img["scared"] = [
            pygame.transform.scale(
                self.img["scared_basic"],
                (
                    int(cell_size / 1.8),
                    int(cell_size / 1.8),
                ),
            )
        ]

        self.game_img["scared"].append(
            pygame.transform.scale(
                self.img["scared_white"],
                (
                    int(cell_size / 1.8),
                    int(cell_size / 1.8),
                ),
            )
        )

        self.game_img["eaten"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("eaten_")
        }

        self.game_img["key"] = pygame.transform.scale(
            self.img["key"],
            (
                int(cell_size / 1.5),
                int(cell_size / 1.5),
            ),
        )
