import pygame
from pathlib import Path
from typing import Dict, Any


class AssetsManager:
    def __init__(self) -> None:
        self.img: Dict[str, pygame.Surface | pygame.surface.Surface] = {}
        self.sound: Dict[str, Any] = {}
        self.game_img: Dict[str, Any] = {}
        self.countdown_play = False
        self.music_load = False
        self.music_on = True

    def play_sound(
        self, media: str | None, sound: Any, loop: bool, volume: float
    ) -> None:
        if not self.music_on:
            self.music_load = False
            return

        if volume < 0.1 or volume > 1:
            volume = 0.5

        if media:
            if loop:
                pygame.mixer.music.load(media)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.load(media)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(1)
        else:
            sound.set_volume(volume)
            sound.play()

    def init_game(self) -> None:
        assets_dir = Path("assets")

        for img in assets_dir.rglob("*.png"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()

        for img in assets_dir.rglob("*.jpeg"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()

        for sound in assets_dir.rglob("*.wav"):
            sound_name = sound.name.split(".")[0]
            self.sound[sound_name] = pygame.mixer.Sound(sound)

        font_size = 40
        self.f_back = pygame.font.Font("assets/font/back.otf", font_size)
        self.f_front = pygame.font.Font("assets/font/front.otf", font_size)

        self.f_back_over = pygame.font.Font(
            "assets/font/back.otf", int(font_size / 1.5)
        )
        self.f_front_over = pygame.font.Font(
            "assets/font/front.otf", int(font_size / 1.5)
        )

        self.f_back_countdown = pygame.font.Font(
            "assets/font/back.otf", font_size * 3
        )
        self.f_front_countdown = pygame.font.Font(
            "assets/font/front.otf", font_size * 3
        )

        self.f_basic = pygame.font.Font("assets/font/basic.ttf", 14)
        self.f_basic_s = pygame.font.Font("assets/font/basic.ttf", 11)

    def load_game_img(self, cell_size: int) -> None:
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
