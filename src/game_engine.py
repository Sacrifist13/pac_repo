import os
import pygame
import sys
from pygame.event import Event
from typing import List, Dict, Any, Tuple
from pathlib import Path
from .loader import Loader
from .map_generator import MapGenerator
from .entities import PacMan, Blinky, Clyde, Inky, Pinky
from .enums_class import PlayingState, GameState, Directions


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
        self.map_elements: Dict[str, Any] = {}
        self.countdown_play = False
        self.playing_state = PlayingState.RETREATE
        self.music_load = False

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

    def _init_game_img(self) -> None:
        self.map_elements["pac_man"] = {
            key: pygame.transform.scale(
                img,
                (
                    self.map_elements["cell_size"] // 1.5,
                    self.map_elements["cell_size"] // 1.5,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("pac_")
            if "gum" not in key
        }

        self.map_elements["blinky"] = {
            key: pygame.transform.scale(
                img,
                (
                    self.map_elements["cell_size"] // 2,
                    self.map_elements["cell_size"] // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("blinky")
        }

        self.map_elements["clyde"] = {
            key: pygame.transform.scale(
                img,
                (
                    self.map_elements["cell_size"] // 2,
                    self.map_elements["cell_size"] // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("clyde")
        }

        self.map_elements["inky"] = {
            key: pygame.transform.scale(
                img,
                (
                    self.map_elements["cell_size"] // 2,
                    self.map_elements["cell_size"] // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("inky")
        }

        self.map_elements["pinky"] = {
            key: pygame.transform.scale(
                img,
                (
                    self.map_elements["cell_size"] // 2,
                    self.map_elements["cell_size"] // 2,
                ),
            )
            for key, img in self.img.items()
            if key.startswith("pinky")
        }

        self.map_elements["pac_gum"] = pygame.transform.scale(
            self.img["pac_gum"],
            (
                self.map_elements["cell_size"] // 6,
                self.map_elements["cell_size"] // 6,
            ),
        )

        self.map_elements["super_pac_gum"] = pygame.transform.scale(
            self.img["pac_gum"],
            (
                self.map_elements["cell_size"] // 3,
                self.map_elements["cell_size"] // 3,
            ),
        )

        self.map_elements["pinky"]["scared_1"] = pygame.transform.scale(
            self.img["scared_basic"],
            (
                self.map_elements["cell_size"] // 2,
                self.map_elements["cell_size"] // 2,
            ),
        )

        self.map_elements["pinky"]["scared_2"] = pygame.transform.scale(
            self.img["scared_white"],
            (
                self.map_elements["cell_size"] // 2,
                self.map_elements["cell_size"] // 2,
            ),
        )

    def _pre_render_map(self, logo: List[Tuple[int]]) -> None:
        self.map_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        self.map_surface.fill((0, 0, 0, 0))

        map_rows = len(self.map)
        map_col = len(self.map[0])

        margin = 80
        available_w = self.WIDTH - (margin * 2)
        available_h = self.HEIGHT - (margin * 2)

        self.map_elements["cell_size"] = min(
            available_w // map_col, available_h // map_rows
        )

        self.map_elements["offset_x"] = (
            self.WIDTH - (map_col * self.map_elements["cell_size"])
        ) // 2
        self.map_elements["offset_y"] = (
            self.HEIGHT - (map_rows * self.map_elements["cell_size"])
        ) // 2

        self._init_game_img()

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

        self.map_elements["pac_coord"] = (mid_y, mid_x)
        self.map_elements["blinky_coord"] = (0, 0)
        self.map_elements["clyde_coord"] = (0, map_col - 1)
        self.map_elements["inky_coord"] = (map_rows - 1, 0)
        self.map_elements["pinky_coord"] = (map_rows - 1, map_col - 1)

        coord_filled = [
            self.map_elements["pac_coord"],
            self.map_elements["blinky_coord"],
            self.map_elements["clyde_coord"],
            self.map_elements["inky_coord"],
            self.map_elements["pinky_coord"],
        ]

        self.pac_gums_coord = []
        self.super_pac_gums_coord = []

        i = 0

        for y in range(map_rows):
            for x in range(map_col):

                block_type = self.map[y][x][0]

                px = (
                    self.map_elements["offset_x"]
                    + x * self.map_elements["cell_size"]
                )
                py = (
                    self.map_elements["offset_y"]
                    + y * self.map_elements["cell_size"]
                )

                if block_type == 15:
                    pygame.draw.rect(
                        self.map_surface,
                        self.PACMAN_YELLOW,
                        pygame.Rect(
                            px,
                            py,
                            self.map_elements["cell_size"],
                            self.map_elements["cell_size"],
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
                        (px + self.map_elements["cell_size"], py),
                        wall_width,
                    )

                if block_type & 2:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px + self.map_elements["cell_size"], py),
                        (
                            px + self.map_elements["cell_size"],
                            py + self.map_elements["cell_size"],
                        ),
                        wall_width,
                    )

                if block_type & 4:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px, py + self.map_elements["cell_size"]),
                        (
                            px + self.map_elements["cell_size"],
                            py + self.map_elements["cell_size"],
                        ),
                        wall_width,
                    )

                if block_type & 8:
                    pygame.draw.line(
                        self.map_surface,
                        wall_color,
                        (px, py),
                        (px, py + self.map_elements["cell_size"]),
                        wall_width,
                    )

    def _generate_map(self) -> bool:
        if self.current_level <= 10:
            map, logo = self.map_generator.create_map(self.current_level)

            self.map = map

            self._pre_render_map(logo)
            pac_x, pac_y = self.map_elements["pac_coord"]
            blinky_x, blinky_y = self.map_elements["blinky_coord"]
            clyde_x, clyde_y = self.map_elements["clyde_coord"]
            inky_x, inky_y = self.map_elements["inky_coord"]
            pinky_x, pinky_y = self.map_elements["pinky_coord"]

            self.player = PacMan(
                x=pac_x,
                y=pac_y,
                img=self.map_elements["pac_man"],
                speed=0,
                cell_size=self.map_elements["cell_size"],
                sound=self.sound,
            )
            self.blinky = Blinky(
                x=blinky_x,
                y=blinky_y,
                img=self.map_elements["blinky"],
                speed=0,
                cell_size=self.map_elements["cell_size"],
            )
            self.clyde = Clyde(
                x=clyde_x,
                y=clyde_y,
                img=self.map_elements["clyde"],
                speed=0,
                cell_size=self.map_elements["cell_size"],
            )
            self.inky = Inky(
                x=inky_x,
                y=inky_y,
                img=self.map_elements["inky"],
                speed=0,
                cell_size=self.map_elements["cell_size"],
            )
            self.pinky = Pinky(
                x=pinky_x,
                y=pinky_y,
                img=self.map_elements["pinky"],
                speed=0,
                cell_size=self.map_elements["cell_size"],
            )

            self.countdown_start_time = pygame.time.get_ticks()
            self.countdown_duration = 5000

            return True
        else:
            return False

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
                self.blinky.speed = 2
                self.clyde.speed = 2
                self.inky.speed = 2
                self.pinky.speed = 2
                self.state = GameState.PLAYING
                self.player.set_direction(Directions.UP)
        return True

    def get_hitbox(self, pixel_x, pixel_y, cell_size: int, ratio=0.5):
        hitbox_size = int(cell_size * ratio)
        offset = (cell_size - hitbox_size) // 2
        return pygame.Rect(
            pixel_x + offset, pixel_y + offset, hitbox_size, hitbox_size
        )

    def _draw_pac_gums(self) -> None:
        c_size = self.map_elements["cell_size"]

        pac_gum_w, pac_gum_h = self.map_elements["pac_gum"].get_size()
        super_pac_gum_w, super_pac_gum_h = self.map_elements[
            "super_pac_gum"
        ].get_size()

        for y, x in self.super_pac_gums_coord:

            px = (
                self.map_elements["offset_x"]
                + x * c_size
                + ((c_size - super_pac_gum_w) // 2)
            )
            py = (
                self.map_elements["offset_y"]
                + y * c_size
                + ((c_size - super_pac_gum_h) // 2)
            )

            self.virtual_screen.blit(
                self.map_elements["super_pac_gum"], (px, py)
            )

        self.nb_pac_gums = len(self.pac_gums_coord)
        self.super_pac_gums = len(self.super_pac_gums_coord)

        for y, x in self.pac_gums_coord:

            px = (
                self.map_elements["offset_x"]
                + x * c_size
                + ((c_size - pac_gum_w) // 2)
            )
            py = (
                self.map_elements["offset_y"]
                + y * c_size
                + ((c_size - pac_gum_h) // 2)
            )

            self.virtual_screen.blit(self.map_elements["pac_gum"], (px, py))

    def _draw_entities(self) -> None:
        if self.playing_state != PlayingState.DEATH:
            self.player.draw(
                self.virtual_screen,
                self.map_elements["offset_x"],
                self.map_elements["offset_y"],
                self.map_elements["cell_size"],
            )

        self.blinky.draw(
            self.virtual_screen,
            self.map_elements["offset_x"],
            self.map_elements["offset_y"],
            self.map_elements["cell_size"],
        )

        self.clyde.draw(
            self.virtual_screen,
            self.map_elements["offset_x"],
            self.map_elements["offset_y"],
            self.map_elements["cell_size"],
        )

        self.inky.draw(
            self.virtual_screen,
            self.map_elements["offset_x"],
            self.map_elements["offset_y"],
            self.map_elements["cell_size"],
        )

        self.pinky.draw(
            self.virtual_screen,
            self.map_elements["offset_x"],
            self.map_elements["offset_y"],
            self.map_elements["cell_size"],
            self.playing_state,
        )

    def _render_game_elements(self) -> None:
        level_text_1 = self.font_back.render(
            "Level " + str(self.current_level), True, self.NEON_BLUE
        )
        level_text_2 = self.font_front.render(
            "Level " + str(self.current_level), True, self.PACMAN_YELLOW
        )

        level_text_w, level_text_h = level_text_1.get_size()
        level_text_x = (self.WIDTH - level_text_w) // 2
        level_text_y = (80 - level_text_h) // 2

        self.virtual_screen.blit(level_text_1, (level_text_x, level_text_y))
        self.virtual_screen.blit(level_text_2, (level_text_x, level_text_y))

        score_text_1 = self.font_basic.render("Score ", True, self.GRAY)
        score_text_2 = self.font_basic.render(
            str(self.score), True, self.NEON_PINK
        )

        score_text_h = score_text_1.get_height()

        self.virtual_screen.blit(
            score_text_1, (80, level_text_y + level_text_h - score_text_h)
        )
        self.virtual_screen.blit(
            score_text_2,
            (
                80 + score_text_1.get_width(),
                level_text_y + level_text_h - score_text_h,
            ),
        )

        pac_img_life = pygame.transform.scale(self.img["pac_2"], (20, 20))
        pac_img_x = self.WIDTH - 80 - pac_img_life.get_width()
        pac_img_y = level_text_y + level_text_h - pac_img_life.get_height()

        for i in range(3):
            self.virtual_screen.blit(pac_img_life, (pac_img_x, pac_img_y))
            pac_img_x -= 5 + pac_img_life.get_width()

        pac_img_x += 5 + pac_img_life.get_width()

        for i in range(self.config.lives - self.lives):
            overlay = pygame.Surface((20, 20), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.virtual_screen.blit(overlay, (pac_img_x, pac_img_y))
            pac_img_x += 5 + pac_img_life.get_width()

        self.virtual_screen.blit(self.map_surface, (0, 0))
        self._draw_pac_gums()
        self._draw_entities()

    def _render_dead(self) -> bool:
        x, y = self.player.pixel_x, self.player.pixel_y

        current_time = pygame.time.get_ticks()

        if self.death_time + 1200 <= current_time:
            pac_x, pac_y = self.map_elements["pac_coord"]
            self.player._set_grid_x(pac_x, self.map_elements["cell_size"])
            self.player._set_grid_y(pac_y, self.map_elements["cell_size"])
            self.playing_state = PlayingState.RETREATE
            self.player.speed = 2
            return True

        elapsed = current_time - self.death_time
        frame_index = min(elapsed * 12 // 1200, 11)

        death_frame = pygame.transform.scale(
            self.img[str(frame_index + 1)],
            (
                self.map_elements["cell_size"] // 1.5,
                self.map_elements["cell_size"] // 1.5,
            ),
        )

        px = (
            self.map_elements["offset_x"]
            + x
            + ((self.map_elements["cell_size"] - death_frame.get_width()) // 2)
        )
        py = (
            self.map_elements["offset_y"]
            + y
            + (
                (self.map_elements["cell_size"] - death_frame.get_height())
                // 2
            )
        )

        self.virtual_screen.blit(death_frame, (px, py))

        return False

    def _render_hud(self) -> None:

        self._render_game_elements()

        if self.state == GameState.STARTING_LEVEL:
            pygame.mixer.music.stop()
            if not self.countdown_play:
                self.countdown_play = True
                self.sound["start"].set_volume(0.2)
                self.sound["start"].play()

            blur_surface = pygame.Surface(
                (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
            )
            blur_surface.fill((0, 0, 0, 160))
            self.virtual_screen.blit(blur_surface, (0, 0))

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.countdown_start_time

            count_down = max(1, 4 - (elapsed_time // 1000))

            if count_down == 1:
                text = "GO"
            else:
                text = str(count_down - 1)

            text_1 = self.font_back_countdown.render(text, True, self.GRAY)
            text_2 = self.font_front_countdown.render(
                text, True, self.NEON_BLUE
            )

            text_x = (self.WIDTH - text_1.get_width()) // 2
            text_y = (self.HEIGHT - text_1.get_height()) // 2

            self.virtual_screen.blit(text_1, (text_x, text_y))
            self.virtual_screen.blit(text_2, (text_x, text_y))

        elif self.state == GameState.PLAYING:

            if self.playing_state == PlayingState.DEATH:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    self.sound["pacman_death"].play()
                    self.music_load = True
                if self._render_dead():
                    self.music_load = False
                    if self.lives <= 0:
                        self.state = GameState.MENU

            elif (
                self.playing_state == PlayingState.RETREATE
                or self.playing_state == PlayingState.POWER
            ):
                if self.playing_state == PlayingState.POWER:
                    if not self.music_load:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(
                            "assets/media/power_pellet.wav"
                        )
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        self.music_load = True
                    current_time = pygame.time.get_ticks()
                    if current_time > self.power_time + 6000:
                        self.music_load = False
                        self.playing_state = PlayingState.RETREATE
                else:
                    pygame.mixer.music.stop()

                self.player.move(
                    self.map,
                    self.map_elements["cell_size"],
                    self.pac_gums_coord,
                    self.super_pac_gums_coord,
                )
                self.blinky.move(self.map, self.map_elements["cell_size"])
                self.clyde.move(self.map, self.map_elements["cell_size"])
                self.inky.move(self.map, self.map_elements["cell_size"])
                self.pinky.move(self.map, self.map_elements["cell_size"])

                if len(self.pac_gums_coord) != self.nb_pac_gums:
                    self.score += self.config.points_per_pacgum

                if len(self.super_pac_gums_coord) != self.super_pac_gums:
                    self.score += self.config.points_per_super_pacgum
                    self.playing_state = PlayingState.POWER
                    self.music_load = False
                    self.power_time = pygame.time.get_ticks()

                pac_rect = self.get_hitbox(
                    self.player.pixel_x,
                    self.player.pixel_y,
                    self.map_elements["cell_size"],
                )
                blinky_rect = self.get_hitbox(
                    self.blinky.pixel_x,
                    self.blinky.pixel_y,
                    self.map_elements["cell_size"],
                )

                if pac_rect.colliderect(blinky_rect):
                    self.playing_state = PlayingState.DEATH
                    self.player.speed = 0
                    self.music_load = False
                    self.death_time = pygame.time.get_ticks()
                    self.lives -= 1

    def _render_home(self, mouse_x: int, mouse_y: int) -> None:
        title_img = self.img["title"]

        w, h = title_img.get_size()
        x, y = (self.WIDTH - w) // 2, -40

        offset_y = 0

        hover = False

        for key in self.home_page["text"].keys():
            coord = (40, h + 120 + offset_y)

            text_1 = self.font_back.render(key, True, self.GRAY)
            text_2 = self.font_front.render(key, True, self.PACMAN_YELLOW)

            text_width, text_height = (
                text_1.get_width(),
                text_1.get_height(),
            )

            self.home_page["text"][key][0], self.home_page["text"][key][1] = (
                coord[0],
                coord[0] + text_width,
            ), (coord[1], coord[1] + text_height)

            if (coord[0] <= mouse_x <= coord[0] + text_width) and (
                coord[1] <= mouse_y <= coord[1] + text_height
            ):
                text_1 = self.font_back.render(key, True, self.NEON_BLUE)
                if key == "Exit" and not self.home_page["text"][key][2]:
                    self.sound["munch_2"].play()
                    self.home_page["text"][key][2] = True
                else:
                    if not self.home_page["text"][key][2]:
                        self.sound["munch_1"].play()
                        self.home_page["text"][key][2] = True
                hover = True

            self.virtual_screen.blit(text_1, coord)
            self.virtual_screen.blit(text_2, coord)

            offset_y += 80

        self.virtual_screen.blit(title_img, (x, y))

        if not hover:
            for value in self.home_page["text"].values():
                value[2] = False

        offset_x = 0

        if not self.home_page["counter"] % 2:
            width, height = self.home_page[1]["ghosts"][0].get_size()

            for ghost in self.home_page[1]["ghosts"]:
                if isinstance(ghost, pygame.Surface):
                    x, y = self.home_page["pos_x"] + offset_x, h - height
                    self.virtual_screen.blit(ghost, (x, y))

                    offset_x += width + 10

            self.home_page["anim_counter"] += 1
            anim_frame = self.home_page["anim_counter"]
            pac_man_img = self.home_page[1]["pac_man"][(anim_frame // 4) % 4]

            pac_man = pygame.transform.scale(pac_man_img, (width, height))

            self.virtual_screen.blit(
                pac_man,
                (self.home_page["pos_x"] + offset_x + 20, h - height),
            )
            self.home_page["pos_x"] += 2

            if self.home_page["pos_x"] == self.virtual_screen.get_width():
                self.home_page["counter"] += 1
                self.home_page["pos_x"] = -self.home_page["start_x"]
        else:
            width, height = self.home_page[1]["ghosts"][0].get_size()

            self.home_page["anim_counter"] += 1
            anim_frame = self.home_page["anim_counter"]
            pac_man_img = self.home_page[1]["pac_man"][(anim_frame // 4) % 4]

            pac_man = pygame.transform.scale(pac_man_img, (width, height))

            self.virtual_screen.blit(
                pac_man,
                (self.home_page["pos_x"], h - height),
            )

            offset_x = width + 20

            for i in range(4):
                ghost_scared = pygame.transform.scale(
                    self.home_page[2]["scared"][(anim_frame // 8) % 2],
                    (width, height),
                )
                self.virtual_screen.blit(
                    ghost_scared,
                    (self.home_page["pos_x"] + offset_x, h - height),
                )

                offset_x += width + 10

            self.home_page["pos_x"] += 2

            if self.home_page["pos_x"] == self.virtual_screen.get_width():
                self.home_page["counter"] += 1
                self.home_page["pos_x"] = -self.home_page["start_x"]

    def _render_instructions(self, mouse_x: int, mouse_y: int) -> None:
        w, h = self.virtual_screen.get_size()

        text_1 = self.font_back.render("Instructions", True, self.NEON_BLUE)
        text_2 = self.font_front.render(
            "Instructions", True, self.PACMAN_YELLOW
        )

        coord = ((w - text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(text_1, coord)
        self.virtual_screen.blit(text_2, coord)

        text_1 = self.font_back.render("Back", True, self.GRAY)
        text_2 = self.font_front.render("Back", True, self.PACMAN_YELLOW)
        text_width, text_height = text_1.get_size()

        coord = ((w - text_1.get_width()) // 2, h - text_1.get_height() - 20)

        (
            self.home_page["Back"][0],
            self.home_page["Back"][1],
        ) = (
            coord[0],
            coord[0] + text_width,
        ), (
            coord[1],
            coord[1] + text_height,
        )

        if (coord[0] <= mouse_x <= coord[0] + text_width) and (
            coord[1] <= mouse_y <= coord[1] + text_height
        ):
            text_1 = self.font_back.render("Back", True, self.NEON_BLUE)
            if not self.home_page["Back"][2]:
                self.sound["munch_2"].play()
                self.home_page["Back"][2] = True

        else:
            self.home_page["Back"][2] = False

        self.virtual_screen.blit(text_1, coord)
        self.virtual_screen.blit(text_2, coord)

        info_text = ["right", "up", "left", "down"]
        img = pygame.transform.scale(
            self.img["arrow"], self.home_page[1]["ghosts"][0].get_size()
        )
        angle = 90
        pos_x = None
        offset_y = 0

        for t in info_text:
            text_1 = self.font_back.render(t, True, self.GRAY)
            text_2 = self.font_front.render(t, True, self.PACMAN_YELLOW)

            img = pygame.transform.scale(self.img["arrow"], (40, 40))
            arrow_img = pygame.transform.rotate(img, angle)

            width = arrow_img.get_width() + text_1.get_width() + 60

            x, y = (self.virtual_screen.get_width() - width) // 2, 250

            if not pos_x:
                pos_x = x
            else:
                x = pos_x

            self.virtual_screen.blit(arrow_img, (x, y + offset_y))
            self.virtual_screen.blit(
                text_1, (x + arrow_img.get_width() + 60, y + offset_y)
            )
            self.virtual_screen.blit(
                text_2, (x + arrow_img.get_width() + 60, y + offset_y)
            )

            offset_y += arrow_img.get_height() + 40
            angle += 90

    def _render(self, mouse_x: int, mouse_y: int) -> None:
        self.virtual_screen.fill(self.BLACK)

        if self.state == GameState.MENU:
            self._render_home(mouse_x, mouse_y)
        elif self.state == GameState.INFO:
            self._render_instructions(mouse_x, mouse_y)
        elif (
            self.state == GameState.PLAYING
            or self.state == GameState.STARTING_LEVEL
        ):
            self._render_hud()

    def _get_scale(self) -> Any:
        win_w, win_h = self.real_screen.get_size()
        virt_w, virt_h = self.virtual_screen.get_size()

        scale_x = win_w / virt_w
        scale_y = win_h / virt_h
        scale = min(scale_x, scale_y)

        new_w = int(virt_w * scale)
        new_h = int(virt_h * scale)

        offset_x = (win_w - new_w) // 2
        offset_y = (win_h - new_h) // 2

        raw_x, raw_y = pygame.mouse.get_pos()
        virtual_mouse_x = (raw_x - offset_x) / scale
        virtual_mouse_y = (raw_y - offset_y) / scale

        return (
            new_w,
            new_h,
            offset_x,
            offset_y,
            virtual_mouse_x,
            virtual_mouse_y,
        )

    def run(self) -> None:
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        print("CHEMIN DE PYGAME :", pygame.__file__)

        pygame.init()
        pygame.mixer.init()

        self.real_screen = pygame.display.set_mode(
            (800, 800), pygame.RESIZABLE
        )

        self.virtual_screen = pygame.Surface((800, 800))

        self._init_game()

        clock = pygame.time.Clock()
        running = True

        pygame.mixer.music.load("assets/media/game_start.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(1)

        while running:
            clock.tick(60)

            new_w, new_h, offset_x, offset_y, v_mouse_x, v_mouse_y = (
                self._get_scale()
            )
            running = self._manage_events(
                pygame.event.get(), v_mouse_x, v_mouse_y
            )

            self._render(v_mouse_x, v_mouse_y)

            scaled_surface = pygame.transform.scale(
                self.virtual_screen, (new_w, new_h)
            )

            self.real_screen.fill((0, 0, 0))
            self.real_screen.blit(scaled_surface, (offset_x, offset_y))

            pygame.draw.rect(
                self.real_screen,
                self.PACMAN_YELLOW,
                pygame.Rect(
                    offset_x,
                    offset_y + 2,
                    new_w,
                    new_h - 4,
                ),
                3,
            )

            pygame.display.flip()
