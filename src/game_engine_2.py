import sys
import pygame
from pathlib import Path
from pygame.event import Event
from typing import List, Dict, Any, Tuple
from .loader import Loader
from .map_generator import MapGenerator
from .enums_class import GameState, Directions, PlayingState
from .entities import PacMan, Ghost, Blinky, Clyde, Inky, Pinky


class GameEngine:
    WIDTH = 800
    HEIGHT = 800
    BLACK = (0, 0, 0)
    GRAY = (155, 155, 155)
    PACMAN_YELLOW = (255, 255, 0)
    NEON_BLUE = (33, 33, 255)
    NEON_PINK = (255, 20, 147)

    def __init__(self) -> None:
        self.map_generator = MapGenerator()
        self.game_img: Dict[str, pygame.Surface | pygame.surface.Surface] = {}

    def _get_hitbox(self, pixel_x, pixel_y, cell_size: int, ratio=0.5):
        hitbox_size = int(cell_size * ratio)
        offset = (cell_size - hitbox_size) // 2
        return pygame.Rect(
            pixel_x + offset, pixel_y + offset, hitbox_size, hitbox_size
        )

    def _init_game(self) -> None:
        self.state = GameState.MENU
        self.img: Dict[str, pygame.Surface] = {}
        self.sound: Dict[str, Any] = {}

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

    def _load_game_img(self, cell_size: int) -> None:
        self.game_img["pac_man"] = {
            key: pygame.transform.scale(
                img,
                (
                    cell_size // 1.5,
                    cell_size // 1.5,
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
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
        ]

        self.game_img["scared"].append(
            pygame.transform.scale(
                self.img["scared_white"],
                (
                    cell_size // 2,
                    cell_size // 2,
                ),
            )
        )

    def _load_map_elements(self, logo: List[Tuple[int]], margin: int) -> None:
        self.map_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        self.map_surface.fill((0, 0, 0, 0))

        map_rows = len(self.map)
        map_cols = len(self.map[0])

        available_w = self.WIDTH - (margin * 2)
        available_h = self.HEIGHT - (margin * 2)

        cell_size = min(available_w // map_cols, available_h // map_rows)

        offset_x = (self.WIDTH - (map_cols * cell_size)) // 2
        offset_y = (self.HEIGHT - (map_rows * cell_size)) // 2

        self._load_game_img(cell_size)

        wall_color = self.NEON_BLUE
        wall_width = 3

        mid_x = (
            min([coord[0] for coord in logo])
            + max([coord[0] for coord in logo])
        ) // 2

        mid_y = (
            min([coord[1] for coord in logo])
            + max([coord[1] for coord in logo])
        ) // 2

        ghosts = {
            Blinky: ("blinky", 0, 0),
            Clyde: ("clyde", 0, map_cols - 1),
            Inky: ("inky", map_rows - 1, 0),
            Pinky: ("pinky", map_rows - 1, map_cols - 1),
        }

        self.pac_man = PacMan(
            "Pac-man", mid_x, mid_y, 0, cell_size, self.game_img["pac_man"]
        )

        self.ghosts: Dict[str, Ghost] = {}

        for key, value in ghosts:
            name, y, x = value
            self.ghosts[name] = key(
                name,
                x,
                y,
                0,
                cell_size,
                self.game_img[name],
                self.game_img["scared"],
            )

        coord_filled = [(coord[1], coord[0]) for coord in ghosts]
        coord_filled.append((mid_y, mid_x))

        self.pac_gums_coord = []
        self.super_pac_gums_coord = []

        i = 0

        for y in range(map_rows):
            for x in range(map_cols):

                block_type = self.map[y][x][0]

                px = offset_x + x * cell_size
                py = offset_y + y * cell_size

                if block_type == 15:
                    pygame.draw.rect(
                        self.map_surface,
                        self.PACMAN_YELLOW,
                        pygame.Rect(
                            px,
                            py,
                            cell_size,
                            cell_size,
                        ),
                    )
                else:
                    if (y, x) not in coord_filled:
                        if i % 2:
                            self.pac_gums_coord.append((y, x))
                        i += 1
                    elif (y, x) in coord_filled[1:]:
                        self.super_pac_gums_coord.append((y, x))

                if block_type & 1:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px, py),
                        (px + cell_size, py),
                        wall_width,
                    )

                if block_type & 2:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px + cell_size, py),
                        (
                            px + cell_size,
                            py + cell_size,
                        ),
                        wall_width,
                    )

                if block_type & 4:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px, py + cell_size),
                        (
                            px + cell_size,
                            py + cell_size,
                        ),
                        wall_width,
                    )

                if block_type & 8:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px, py),
                        (px, py + cell_size),
                        wall_width,
                    )

    def _generate_map(self) -> bool:
        if self.current_level > 10:
            return False

        map, logo = self.map_generator.create_map(self.current_level)
        self.map = map
        self._load_map_elements(logo)
        self.countdown_start_time = pygame.time.get_ticks()
        self.countdown_duration = 5000

    def _manage_events(
        self, events: List[Event], mouse_x: int, mouse_y: int
    ) -> bool:
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for key, value in self.home_page["text"].items():
                            x_min, x_max = value[0]
                            y_min, y_max = value[1]

                            if (x_min <= mouse_x <= x_max) and (
                                y_min <= mouse_y <= y_max
                            ):
                                if key == "Start Game":
                                    self.state = GameState.STARTING_LEVEL
                                    self.current_level = 1
                                    self._generate_map()
                                    self.score = 0

                                elif key == "View Highscores":
                                    self.state = GameState.SCORE
                                elif key == "Instructions":
                                    self.state = GameState.INFO
                                elif key == "Exit":
                                    return False

            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.set_direction(Directions.UP)
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_direction(Directions.RIGHT)
                    elif event.key == pygame.K_LEFT:
                        self.player.set_direction(Directions.LEFT)
                    elif event.key == pygame.K_DOWN:
                        self.player.set_direction(Directions.DOWN)

            elif self.state == GameState.PAUSED:
                pass

            elif self.state == GameState.SCORE:
                pass

            elif self.state == GameState.GAME_OVER:
                pass
            elif self.state == GameState.INFO:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.home_page["Back"][0]
                        y_min, y_max = self.home_page["Back"][1]

                        if (x_min <= mouse_x <= x_max) and (
                            y_min <= mouse_y <= y_max
                        ):
                            self.state = GameState.MENU

        if self.state == GameState.STARTING_LEVEL:
            current_time = pygame.time.get_ticks()
            if (
                current_time - self.countdown_start_time
                >= self.countdown_duration
            ):
                self.player.speed = 2

                for ghost in self.ghosts.values():
                    ghost.speed = 2

                self.state = GameState.PLAYING
                self.player.set_direction(Directions.UP)
        return True
