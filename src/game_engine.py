import os
import sys
import pygame
from pathlib import Path
from pygame.event import Event
from typing import List, Dict, Any, Tuple
from .loader import Loader
from .map_generator import MapGenerator
from .enums_class import GameState, Directions, PlayingState, Mode
from .entities import PacMan, Ghost, Blinky, Clyde, Inky, Pinky


class GameEngine:
    WIDTH = 800
    HEIGHT = 800
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (155, 155, 155)
    PACMAN_YELLOW = (255, 255, 0)
    NEON_BLUE = (33, 33, 255)
    NEON_PINK = (255, 20, 147)
    NEON_PURPLE = (191, 0, 255)
    NEON_RED = (255, 7, 58)
    NEON_GREEN = (57, 255, 20)

    def __init__(self) -> None:
        self.map_generator = MapGenerator()
        self.game_img: Dict[str, Any] = {}
        self.playing_state = PlayingState.RETREATE
        self.countdown_play = False
        self.music_load = False
        self.death_time: int = 0
        self.power_time: int = 0
        self.time_score_eating: int = 0
        self.score_eating_coord: Tuple[int, int] = (0, 0)
        self.score_eating: int = 0
        self.current_level: int = 1
        self.score: int = 0
        self.lives: int = 0
        self.ghosts_eat: int = 0
        self.pause_info: Dict[Any, Any] = {}
        self.music_on = True
        self.level_pass_animation = False
        self.level_pass_animation_time: int = 0
        self.home_page_sound_play: bool = False
        self.in_typing: bool = False
        self.pseudo = ""
        self.pseudo_valid: bool = False
        self.input_cursor_i: int = 0
        self.speed_cheat: bool = False
        self.freeze_cheat: bool = False

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

    def _get_hitbox(
        self, pixel_x: int, pixel_y: int, cell_size: int, ratio: float = 0.5
    ) -> pygame.Rect:
        hitbox_size = int(cell_size * ratio)
        offset = (cell_size - hitbox_size) // 2
        return pygame.Rect(
            pixel_x + offset, pixel_y + offset, hitbox_size, hitbox_size
        )

    def _play_sound(
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

    def _init_game(self) -> None:
        self.state = GameState.MENU
        self.img: Dict[str, pygame.Surface] = {}
        self.sound: Dict[str, Any] = {}

        loader = Loader()
        self.config = loader.load_config(sys.argv)

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

        self.interface: Dict[Any, Any] = {
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
            "Back_instructions": [(0, 0), (0, 0), False],
            "Back_highscores": [(0, 0), (0, 0), False],
            "Back_game_over": [(0, 0), (0, 0), False],
            "Exit_paused": [(0, 0), (0, 0), False],
        }

        self.interface["pos_x"] = -(
            self.interface[1]["ghosts"][0].get_width() * 5
        ) - (60)
        self.interface["start_x"] = -self.interface["pos_x"]

        font_size = 40
        self.font_back = pygame.font.Font("assets/font/back.otf", font_size)
        self.font_front = pygame.font.Font("assets/font/front.otf", font_size)

        self.font_back_game_over = pygame.font.Font(
            "assets/font/back.otf", int(font_size / 1.5)
        )
        self.font_front_game_over = pygame.font.Font(
            "assets/font/front.otf", int(font_size / 1.5)
        )

        self.font_back_countdown = pygame.font.Font(
            "assets/font/back.otf", font_size * 3
        )
        self.font_front_countdown = pygame.font.Font(
            "assets/font/front.otf", font_size * 3
        )

        self.font_basic = pygame.font.Font("assets/font/basic.ttf", 14)
        self.font_basic_small = pygame.font.Font("assets/font/basic.ttf", 11)

    def _load_game_img(self, cell_size: int) -> None:
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

    def _load_map_elements(
        self, logo: List[Tuple[int, int]], margin: int = 80
    ) -> None:
        self.map_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        self.map_surface.fill((0, 0, 0, 0))

        map_rows = len(self.map)
        map_cols = len(self.map[0])

        available_w = self.WIDTH - (margin * 2)
        available_h = self.HEIGHT - (margin * 2)

        cell_size = min(available_w // map_cols, available_h // map_rows)

        self.game_offset_x = (self.WIDTH - (map_cols * cell_size)) // 2
        self.game_offset_y = (self.HEIGHT - (map_rows * cell_size)) // 2

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

        for ghost_class, value in ghosts.items():
            name, y, x = value
            self.ghosts[name] = ghost_class(
                name,
                x,
                y,
                0,
                cell_size,
                self.game_img[name],
                self.game_img["scared"],
                self.game_img["eaten"],
            )

        coord_filled: List[Tuple[int, int]] = [(mid_y, mid_x)]
        for value in ghosts.values():
            coord_filled.append((int(value[1]), int(value[2])))

        self.pac_gums_coord = []
        self.super_pac_gums_coord = []

        i = 0

        for y in range(map_rows):
            for x in range(map_cols):

                block_type = self.map[y][x][0]

                px = self.game_offset_x + x * cell_size
                py = self.game_offset_y + y * cell_size

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

        return True

    def _draw_time_left(self) -> bool:
        current_time = pygame.time.get_ticks()

        time_left_s = (
            int(
                self.level_starting_time
                + (self.config.level_max_time * 1000)
                - current_time
            )
            // 1000
        )

        if time_left_s <= 0:
            return False

        time_left_text = self.font_basic.render(
            str(time_left_s), True, self.NEON_PINK
        )

        time_left_w, time_left_h = time_left_text.get_size()
        time_x, time_y = (
            self.WIDTH - time_left_w
        ) // 2, self.HEIGHT - time_left_h - 20

        self.virtual_screen.blit(time_left_text, (time_x, time_y))

        return True

    def _draw_pac_gums(self) -> None:
        c_size = self.pac_man.cell_size

        pac_gum_w, pac_gum_h = self.game_img["pac_gum"].get_size()
        super_pac_gum_w, super_pac_gum_h = self.game_img[
            "super_pac_gum"
        ].get_size()

        for y, x in self.super_pac_gums_coord:
            px = (
                self.game_offset_x
                + x * c_size
                + ((c_size - super_pac_gum_w) // 2)
            )
            py = (
                self.game_offset_y
                + y * c_size
                + ((c_size - super_pac_gum_h) // 2)
            )

            self.virtual_screen.blit(self.game_img["super_pac_gum"], (px, py))

        self.nb_pac_gums = len(self.pac_gums_coord)
        self.super_pac_gums = len(self.super_pac_gums_coord)

        for y, x in self.pac_gums_coord:

            px = self.game_offset_x + x * c_size + ((c_size - pac_gum_w) // 2)
            py = self.game_offset_y + y * c_size + ((c_size - pac_gum_h) // 2)

            self.virtual_screen.blit(self.game_img["pac_gum"], (px, py))

    def _draw_game_status(self) -> None:
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

    def _draw_entities(self) -> None:
        if self.playing_state != PlayingState.DEATH:
            self.pac_man.draw_on_surface(
                self.virtual_screen,
                self.game_offset_x,
                self.game_offset_y,
                self.playing_state,
            )
        if self.playing_state != PlayingState.LEVEL_PASS:
            for ghost in self.ghosts.values():
                ghost.draw_on_surface(
                    self.virtual_screen,
                    self.game_offset_x,
                    self.game_offset_y,
                    self.playing_state,
                )

    def _move_entities(self) -> None:

        self.pac_man.move(self.map)

        if self.playing_state == PlayingState.LEVEL_PASS:
            return

        if self.playing_state == PlayingState.POWER:
            for ghost in self.ghosts.values():
                if ghost.mode == Mode.SCARED:
                    ghost.move_random(self.map)
                elif ghost.mode == Mode.EAT:
                    if ghost.move_to_start_pos(self.map):
                        ghost.mode = Mode.NORMAL
                        if not self.freeze_cheat:
                            ghost.speed = 1

        else:
            for ghost in self.ghosts.values():
                if ghost.mode == Mode.NORMAL:
                    if (
                        ghost.name == "blinky"
                        and self.pac_man.mode != Mode.INVINCIBLE
                    ):
                        ghost.move(
                            self.map, self.pac_man.grid_x, self.pac_man.grid_y
                        )
                    else:
                        ghost.move_random(self.map)
                    # Rajouter un if pac_man.mode == Mode.INVINCIBLE
                    # else avec le vrai algo des fantomes ghost.move()
                elif ghost.mode == Mode.EAT:
                    if ghost.move_to_start_pos(self.map):
                        ghost.mode = Mode.NORMAL
                        if not self.freeze_cheat:
                            ghost.speed = 2
                        else:
                            ghost.speed = 0

    def _eat_pac_gums(self) -> bool:
        cell_size = self.pac_man.cell_size

        pac_cx = self.pac_man.pixel_x + cell_size // 2
        pac_cy = self.pac_man.pixel_y + cell_size // 2

        y = pac_cy // cell_size
        x = pac_cx // cell_size

        if (y, x) in self.pac_gums_coord:
            self.pac_gums_coord.remove((y, x))

            return True

        return False

    def _eat_super_pac_gums(self) -> bool:
        cell_size = self.pac_man.cell_size

        pac_cx = self.pac_man.pixel_x + cell_size // 2
        pac_cy = self.pac_man.pixel_y + cell_size // 2

        y = pac_cy // cell_size
        x = pac_cx // cell_size

        if (y, x) in self.super_pac_gums_coord:
            self.super_pac_gums_coord.remove((y, x))

            return True

        return False

    def _draw_score_eating(self) -> None:
        current_time = pygame.time.get_ticks()

        if current_time < self.time_score_eating + 1000:
            y, x = self.score_eating_coord

            points_str = self.font_basic.render(
                str(self.score_eating), True, self.NEON_PINK
            )
            points_h = points_str.get_height()
            points_x, points_y = (
                self.game_offset_x + x,
                (self.game_offset_y + y) + points_h // 2,
            )
            self.virtual_screen.blit(points_str, (points_x, points_y))

    def _is_pac_man_catch(self) -> None:
        if self.playing_state == PlayingState.LEVEL_PASS:
            return

        cell_size = self.pac_man.cell_size

        pac_rect = self._get_hitbox(
            self.pac_man.pixel_x, self.pac_man.pixel_y, cell_size
        )

        current_time = pygame.time.get_ticks()

        for ghost in self.ghosts.values():
            ghost_rect = self._get_hitbox(
                ghost.pixel_x, ghost.pixel_y, cell_size
            )
            if pac_rect.colliderect(ghost_rect):
                if (
                    ghost.mode == Mode.NORMAL
                    and self.pac_man.mode != Mode.INVINCIBLE
                    and self.playing_state != PlayingState.POWER
                ):
                    self.playing_state = PlayingState.DEATH
                    self.pac_man.speed = 0
                    self.music_load = False
                    self.death_time = current_time
                    self.lives -= 1

                elif ghost.mode == Mode.SCARED:
                    self._play_sound(None, self.sound["eat_ghost"], False, 0.5)
                    ghost.mode = Mode.EAT
                    ghost.speed = 2
                    self.score_eating = self.config.points_per_ghost * (
                        1 + self.ghosts_eat
                    )
                    self.score += self.score_eating
                    self.ghosts_eat += 1
                    self.time_score_eating = pygame.time.get_ticks()
                    self.score_eating_coord = (
                        ghost.pixel_y,
                        ghost.pixel_x,
                    )

    def _load_pause_info(self) -> None:
        current_time = pygame.time.get_ticks()

        self.pause_info["time_left"] = (
            self.config.level_max_time
            - ((current_time - self.level_starting_time) // 1000)
            - 1
        )

        if self.pac_man.mode == Mode.INVINCIBLE:
            self.pause_info["pac_man_dying_elapsed_time"] = (
                current_time - self.pac_man.dying_time
            )

        if self.playing_state == PlayingState.POWER:
            self.pause_info["power_elapsed_time"] = (
                current_time - self.power_time
            )

        for name, ghost in self.ghosts.items():
            self.pause_info[name] = ghost.speed
            ghost.speed = 0

        self.pac_man.speed = 0

    def _render_starting_level(self) -> None:

        blur_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        blur_surface.fill((0, 0, 0, 160))

        time_left_text = self.font_basic.render(
            str(self.config.level_max_time), True, self.NEON_PINK
        )

        time_left_w, time_left_h = time_left_text.get_size()
        time_x, time_y = (
            self.WIDTH - time_left_w
        ) // 2, self.HEIGHT - time_left_h - 20

        self.virtual_screen.blit(time_left_text, (time_x, time_y))
        self.virtual_screen.blit(blur_surface, (0, 0))

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.countdown_start_time

        count_down = max(1, 4 - (elapsed_time // 1000))

        if count_down == 1:
            text = "GO"
        else:
            text = str(count_down - 1)

        text_1 = self.font_back_countdown.render(text, True, self.GRAY)
        text_2 = self.font_front_countdown.render(text, True, self.NEON_BLUE)

        text_x = (self.WIDTH - text_1.get_width()) // 2
        text_y = (self.HEIGHT - text_1.get_height()) // 2

        self.virtual_screen.blit(text_1, (text_x, text_y))
        self.virtual_screen.blit(text_2, (text_x, text_y))

    def _render_paused_game(self, mouse_x: int, mouse_y: int) -> None:
        blur_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        blur_surface.fill((0, 0, 0, 160))

        time_left = self.pause_info["time_left"]

        time_left_text = self.font_basic.render(
            str(time_left), True, self.NEON_PINK
        )

        time_left_w, time_left_h = time_left_text.get_size()
        time_x, time_y = (
            self.WIDTH - time_left_w
        ) // 2, self.HEIGHT - time_left_h - 20

        self.virtual_screen.blit(time_left_text, (time_x, time_y))

        self.virtual_screen.blit(blur_surface, (0, 0))

        width, height = self.WIDTH // 3, int(self.HEIGHT / 2.4)
        x, y = (self.WIDTH - width) // 2, (self.HEIGHT - height) // 2

        paused_surface = pygame.Surface((width, height))
        paused_surface.fill(self.BLACK)

        color = self.NEON_PURPLE

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, width + 2, height + 2),
            2,
        )

        text_1 = self.font_back.render("PAUSE", True, self.GRAY)
        text_2 = self.font_front.render("PAUSE", True, color)

        text_x = (width - text_1.get_width()) // 2

        paused_surface.blit(text_1, (text_x, 2))
        paused_surface.blit(text_2, (text_x, 2))

        exit_text_1 = self.font_back_game_over.render("EXIT", True, self.GRAY)

        exit_text_w, exit_text_h = exit_text_1.get_size()

        exit_text_x = (width - exit_text_w) // 2
        exit_text_y = height - exit_text_h - 4

        exit_text_front_color = self.NEON_PURPLE
        if (
            x + exit_text_x <= mouse_x <= x + exit_text_x + exit_text_w
            and y + exit_text_y <= mouse_y <= y + exit_text_y + exit_text_h
        ):
            exit_text_front_color = self.NEON_PINK
            if not self.interface["Exit_paused"][2]:
                self._play_sound(None, self.sound["munch_2"], False, 0.5)
                self.interface["Exit_paused"][2] = True
        else:
            self.interface["Exit_paused"][2] = False

        exit_text_2 = self.font_front_game_over.render(
            "EXIT", True, exit_text_front_color
        )

        self.interface["Exit_paused"][0] = (
            x + exit_text_x,
            x + exit_text_x + exit_text_w,
        )
        self.interface["Exit_paused"][1] = (
            y + exit_text_y,
            y + exit_text_y + exit_text_h,
        )

        paused_surface.blit(exit_text_1, (exit_text_x, exit_text_y))
        paused_surface.blit(exit_text_2, (exit_text_x, exit_text_y))

        volume_img = (
            pygame.transform.scale(self.img["volume_up"], (40, 40))
            if self.music_on
            else pygame.transform.scale(self.img["volume_off"], (40, 40))
        )

        volume_w, volume_h = volume_img.get_size()
        volume_x, volume_y = (
            width - volume_w
        ) // 2, text_1.get_height() + volume_h - 20

        paused_surface.blit(volume_img, (volume_x, volume_y))

        self.interface["volume"] = (
            (x + volume_x, x + volume_x + volume_w),
            (y + volume_y, y + volume_y + volume_h),
        )

        hover_music_color = self.NEON_GREEN if self.music_on else self.NEON_RED

        if (
            x + volume_x <= mouse_x <= x + volume_x + volume_w
            and y + volume_y <= mouse_y <= y + volume_y + volume_h
        ):
            pygame.draw.rect(
                paused_surface,
                hover_music_color,
                pygame.Rect(
                    volume_x - 1, volume_y - 1, volume_w + 2, volume_h + 2
                ),
                1,
            )

        score_text_1 = self.font_basic.render("Score ", True, self.GRAY)
        score_text_2 = self.font_basic.render(str(self.score), True, color)

        score_text_w, score_text_h = score_text_1.get_size()
        value_text_w = score_text_2.get_width()

        total_w = score_text_w + value_text_w
        score_text_x, score_text_y = (
            width - total_w
        ) // 2, volume_y + volume_h + 40

        paused_surface.blit(score_text_1, (score_text_x, score_text_y))
        paused_surface.blit(
            score_text_2, (score_text_x + score_text_w, score_text_y)
        )

        resume_text = self.font_basic.render("RESUME", True, self.NEON_PURPLE)
        resume_w, resume_h = resume_text.get_size()

        resume_x, resume_y = (
            width - resume_w
        ) // 2, score_text_y + score_text_h + resume_h + 40

        if (
            x + resume_x <= mouse_x <= x + resume_x + resume_w
            and y + resume_y <= mouse_y <= y + resume_y + resume_h
        ):
            resume_text = self.font_basic.render(
                "RESUME", True, self.NEON_PINK
            )

        paused_surface.blit(resume_text, (resume_x, resume_y))

        self.interface["resume_paused"] = (
            (x + resume_x, x + resume_x + resume_w),
            (y + resume_y, y + resume_y + resume_h),
        )

        self.virtual_screen.blit(paused_surface, (x, y))

    def _depause_game(self) -> None:
        current_time = pygame.time.get_ticks()

        for name, ghost in self.ghosts.items():
            ghost.speed = self.pause_info[name]

        if self.speed_cheat:
            self.pac_man.speed = 4
        else:
            self.pac_man.speed = 2

        self.level_starting_time = (
            current_time
            - (self.config.level_max_time - self.pause_info["time_left"])
            * 1000
        ) + 1000

        if self.pac_man.mode == Mode.INVINCIBLE:
            self.pac_man.dying_time = (
                current_time - self.pause_info["pac_man_dying_elapsed_time"]
            )

        if self.playing_state == PlayingState.POWER:
            self.power_time = (
                current_time - self.pause_info["power_elapsed_time"]
            )
            if not self.music_load:
                self._play_sound(
                    "assets/media/power_pellet.wav", None, True, 0.5
                )
                self.music_load = True

    def _render_pac_man_dying(self) -> bool:
        x, y = self.pac_man.pixel_x, self.pac_man.pixel_y
        cell_size = self.pac_man.cell_size

        current_time = pygame.time.get_ticks()

        if self.death_time + 1200 <= current_time:
            self.pac_man.reset_pos()
            self.playing_state = PlayingState.RETREATE
            if self.speed_cheat:
                self.pac_man.speed = 4
            else:
                self.pac_man.speed = 2

            return True

        elapsed = current_time - self.death_time
        frame_index = min(elapsed * 12 // 1200, 11)

        death_frame = pygame.transform.scale(
            self.img[str(frame_index + 1)],
            (int(cell_size / 1.5), int(cell_size / 1.5)),
        )

        px = (
            self.game_offset_x
            + x
            + ((cell_size - death_frame.get_width()) // 2)
        )
        py = (
            self.game_offset_y
            + y
            + ((cell_size - death_frame.get_height()) // 2)
        )

        self.virtual_screen.blit(death_frame, (px, py))

        return False

    def _render_input_user(
        self,
        surface: pygame.Surface,
        surface_pos_x: int,
        surface_pos_y: int,
        input_window_y: int,
    ) -> None:
        w, h = surface.get_size()

        basic_text = self.font_basic.render(
            "Enter your name ..", True, self.BLACK
        )

        basic_text_w, basic_text_h = basic_text.get_size()

        input_window_w, input_window_h = basic_text_w + 14, basic_text_h + 14
        input_window_x = (w - input_window_w) // 2

        input_window = pygame.Surface((input_window_w, input_window_h))
        input_window.fill(self.WHITE)

        color = self.NEON_PURPLE

        if not self.in_typing and not self.pseudo:
            input_window.blit(basic_text, (4, 8))
        else:
            self.input_cursor_i += 1
            input_txt = (
                self.pseudo + "|"
                if len(self.pseudo) < 12 and (self.input_cursor_i // 20) % 2
                else self.pseudo
            )

            text = self.font_basic.render(input_txt, True, self.BLACK)
            input_window.blit(text, (4, 8))
            color = self.NEON_PINK

            if len(self.pseudo) >= 1:
                self.pseudo_valid = True
                inst_text = self.font_basic_small.render(
                    "Press enter to valid", True, self.NEON_PINK
                )
                inst_text_w = inst_text.get_width()

                inst_text_x, inst_text_y = (
                    input_window_x + (input_window_w - inst_text_w) // 2,
                    input_window_y + input_window_h + 10,
                )
                surface.blit(inst_text, (inst_text_x, inst_text_y))
            else:
                self.pseudo_valid = False

        surface.blit(input_window, (input_window_x, input_window_y))

        pygame.draw.rect(
            surface,
            color,
            pygame.Rect(
                input_window_x - 1,
                input_window_y - 1,
                input_window_w + 2,
                input_window_h + 2,
            ),
            2,
        )

        self.interface["input_window"] = (
            (
                surface_pos_x + input_window_x,
                surface_pos_x + input_window_x + input_window_w,
            ),
            (
                surface_pos_y + input_window_y,
                surface_pos_y + input_window_y + input_window_h,
            ),
        )

    def _render_game_over(self, mouse_x: int, mouse_y: int) -> None:
        blur_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        blur_surface.fill((0, 0, 0, 160))

        self.virtual_screen.blit(blur_surface, (0, 0))

        pop_up_surface = pygame.Surface(
            (int(self.WIDTH / 1.5), self.HEIGHT // 3), pygame.SRCALPHA
        )

        w, h = pop_up_surface.get_size()

        x, y = (self.WIDTH - w) // 2, (self.HEIGHT - h) // 2

        pop_up_surface.fill(self.BLACK)

        color = self.NEON_PURPLE

        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, w + 2, h + 2),
            2,
        )
        text_1 = self.font_back.render("GAME OVER", True, self.GRAY)
        text_2 = self.font_front.render("GAME OVER", True, color)

        text_x = (w - text_1.get_width()) // 2
        text_h = text_1.get_height()

        pop_up_surface.blit(text_1, (text_x, 2))
        pop_up_surface.blit(text_2, (text_x, 2))

        back_text_1 = self.font_back_game_over.render("BACK", True, self.GRAY)

        back_text_w, back_text_h = back_text_1.get_size()

        back_text_x = (w - back_text_w) // 2
        back_text_y = h - back_text_h - 4

        back_text_front_color = self.NEON_PURPLE

        self.interface["Back_game_over"][0] = (
            x + back_text_x,
            x + back_text_x + back_text_w,
        )
        self.interface["Back_game_over"][1] = (
            y + back_text_y,
            y + back_text_y + back_text_h,
        )

        if (
            x + back_text_x <= mouse_x <= x + back_text_x + back_text_w
            and y + back_text_y <= mouse_y <= y + back_text_y + back_text_h
        ):
            back_text_front_color = self.NEON_PINK
            if not self.interface["Back_game_over"][2]:
                self._play_sound(None, self.sound["munch_2"], False, 0.5)
                self.interface["Back_game_over"][2] = True
        else:
            self.interface["Back_game_over"][2] = False

        back_text_2 = self.font_front_game_over.render(
            "BACK", True, back_text_front_color
        )

        pop_up_surface.blit(back_text_1, (back_text_x, back_text_y))
        pop_up_surface.blit(back_text_2, (back_text_x, back_text_y))

        score_text_1 = self.font_basic.render("Score ", True, self.GRAY)
        score_text_2 = self.font_basic.render(str(self.score), True, color)

        score_text_w, score_text_h = score_text_1.get_size()
        value_text_w = score_text_2.get_width()

        total_w = score_text_w + value_text_w
        score_text_x, score_text_y = (w - total_w) // 2, 2 + text_h + 40

        pop_up_surface.blit(score_text_1, (score_text_x, score_text_y))
        pop_up_surface.blit(
            score_text_2, (score_text_x + score_text_w, score_text_y)
        )

        input_window_y = score_text_y + score_text_h + 40

        self._render_input_user(pop_up_surface, x, y, input_window_y)

        self.virtual_screen.blit(pop_up_surface, (x, y))

    def _render_level_pass(self) -> None:
        pygame.mixer.music.stop()

        if self.level_pass_animation:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.level_pass_animation_time

            if elapsed_time > 1000:
                self.current_level += 1
                self.countdown_start_time = current_time

                if self.current_level > 10:
                    self.state = GameState.WIN
                else:
                    self.state = GameState.STARTING_LEVEL
                    self.playing_state = PlayingState.RETREATE
                    self.countdown_play = False
                    self._generate_map()
                return
            else:
                w, h = self.WIDTH * (
                    (elapsed_time // 10) / 100
                ), self.HEIGHT * ((elapsed_time // 10) / 100)

                x, y = (self.WIDTH - w) // 2, (self.HEIGHT - h) // 2

                pygame.draw.rect(
                    self.virtual_screen, self.BLACK, pygame.Rect(x, y, w, h)
                )

        else:
            cell_size = self.pac_man.cell_size

            key_pixel_x, key_pixel_y = (
                self.pac_man.starting_x * cell_size,
                self.pac_man.starting_y * cell_size,
            )

            key_w, key_h = self.game_img["key"].get_size()
            key_x, key_y = self.game_offset_x + key_pixel_x + (
                cell_size - key_w
            ) // 2, (
                self.game_offset_y + key_pixel_y + (cell_size - key_h) // 2
            )

            self.virtual_screen.blit(self.game_img["key"], (key_x, key_y))

            key_hitbox = self._get_hitbox(key_pixel_x, key_pixel_y, cell_size)
            pac_man_hitbox = self._get_hitbox(
                self.pac_man.pixel_x, self.pac_man.pixel_y, cell_size
            )

            if pac_man_hitbox.colliderect(key_hitbox):
                self.level_pass_animation = True
                self.level_pass_animation_time = pygame.time.get_ticks()

    def _render_game(self, mouse_x: int, mouse_y: int) -> None:
        self.virtual_screen.blit(self.map_surface, (0, 0))
        self._draw_game_status()
        self._draw_pac_gums()
        self._draw_entities()

        current_time = pygame.time.get_ticks()

        if self.state == GameState.STARTING_LEVEL:
            pygame.mixer.music.stop()
            if not self.countdown_play:
                self.countdown_play = True
                self._play_sound(None, self.sound["start"], False, 0.2)
            self._render_starting_level()

            return

        if self.state == GameState.GAME_OVER:
            self._render_game_over(mouse_x, mouse_y)
            return

        elif self.state == GameState.PAUSED:
            self._render_paused_game(mouse_x, mouse_y)
            return

        elif self.state == GameState.PLAYING:

            self._move_entities()

            if self.playing_state == PlayingState.LEVEL_PASS:
                self._render_level_pass()
                return

            if not self._draw_time_left():
                self.state = GameState.GAME_OVER
                pygame.mixer.music.stop()
                self.music_load = False
                return

            if self.playing_state == PlayingState.DEATH:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    self._play_sound(
                        None, self.sound["pacman_death"], False, 0.5
                    )
                    self.music_load = True

                if self._render_pac_man_dying():
                    self.pac_man.dying_time = current_time
                    self.pac_man.mode = Mode.INVINCIBLE

                    self.music_load = False

                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                        pygame.mixer.music.stop()
                return

            if self.playing_state == PlayingState.POWER:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    self._play_sound(
                        "assets/media/power_pellet.wav", None, True, 0.5
                    )
                    self.music_load = True

                self._draw_score_eating()

                if current_time > self.power_time + 6000:
                    self.music_load = False
                    self.playing_state = PlayingState.RETREATE
                    self.ghosts_eat = 0

                    for ghost in self.ghosts.values():
                        if ghost.mode != Mode.EAT:
                            ghost.mode = Mode.NORMAL
                            if not self.freeze_cheat:
                                ghost.speed = 2
                            else:
                                ghost.speed = 0
            else:
                pygame.mixer.music.stop()

            if self.pac_man.mode == Mode.INVINCIBLE:
                if current_time > self.pac_man.dying_time + 3000:
                    self.pac_man.mode = Mode.NORMAL

            if self._eat_pac_gums():
                self.score += self.config.points_per_pacgum

                if len(self.pac_gums_coord) % 2:
                    self._play_sound(None, self.sound["munch_1"], False, 0.5)
                else:
                    self._play_sound(None, self.sound["munch_2"], False, 0.5)

            if self._eat_super_pac_gums():
                self.score += self.config.points_per_super_pacgum

                self.playing_state = PlayingState.POWER
                self.music_load = False
                self.power_time = current_time

                for ghost in self.ghosts.values():
                    if ghost.mode != Mode.EAT:
                        ghost.mode = Mode.SCARED
                        if not self.freeze_cheat:
                            ghost.speed = 1

            if not self.pac_gums_coord:
                self.playing_state = PlayingState.LEVEL_PASS
                self.freeze_cheat = False
                self.speed_cheat = False
                return

            self._is_pac_man_catch()

    def _render_win(self, mouse_x: int, mouse_y: int) -> None:
        # ratio = (
        #     self.img["firework"].get_width()
        #     / self.img["firework"].get_height()
        # )

        # new_w = 300
        # new_h = int(new_w / ratio)

        # new_firework_img = pygame.transform.scale(
        #     self.img["firework"], (new_w, new_h)
        # )

        # self.virtual_screen.blit(new_firework_img, (60, 20))
        # self.virtual_screen.blit(
        #     new_firework_img, (self.WIDTH - new_w - 60, 20)
        # )

        pop_up_surface = pygame.Surface(
            (int(self.WIDTH / 1.5), self.HEIGHT // 3), pygame.SRCALPHA
        )

        w, h = pop_up_surface.get_size()

        x, y = (self.WIDTH - w) // 2, (self.HEIGHT - h) // 2

        pop_up_surface.fill(self.BLACK)

        color = self.NEON_PURPLE

        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, w + 2, h + 2),
            2,
        )
        text_1 = self.font_back.render("YOU WIN", True, self.GRAY)
        text_2 = self.font_front.render("YOU WIN", True, color)

        text_x = (w - text_1.get_width()) // 2
        text_h = text_1.get_height()

        pop_up_surface.blit(text_1, (text_x, 2))
        pop_up_surface.blit(text_2, (text_x, 2))

        back_text_1 = self.font_back_game_over.render("BACK", True, self.GRAY)

        back_text_w, back_text_h = back_text_1.get_size()

        back_text_x = (w - back_text_w) // 2
        back_text_y = h - back_text_h - 4

        back_text_front_color = self.NEON_PURPLE

        self.interface["Back_game_over"][0] = (
            x + back_text_x,
            x + back_text_x + back_text_w,
        )
        self.interface["Back_game_over"][1] = (
            y + back_text_y,
            y + back_text_y + back_text_h,
        )

        if (
            x + back_text_x <= mouse_x <= x + back_text_x + back_text_w
            and y + back_text_y <= mouse_y <= y + back_text_y + back_text_h
        ):
            back_text_front_color = self.NEON_PINK
            if not self.interface["Back_game_over"][2]:
                self._play_sound(None, self.sound["munch_2"], False, 0.5)
                self.interface["Back_game_over"][2] = True
        else:
            self.interface["Back_game_over"][2] = False

        back_text_2 = self.font_front_game_over.render(
            "BACK", True, back_text_front_color
        )

        pop_up_surface.blit(back_text_1, (back_text_x, back_text_y))
        pop_up_surface.blit(back_text_2, (back_text_x, back_text_y))

        score_text_1 = self.font_basic.render("Score ", True, self.GRAY)
        score_text_2 = self.font_basic.render(str(self.score), True, color)

        score_text_w, score_text_h = score_text_1.get_size()
        value_text_w = score_text_2.get_width()

        total_w = score_text_w + value_text_w
        score_text_x, score_text_y = (w - total_w) // 2, 2 + text_h + 40

        pop_up_surface.blit(score_text_1, (score_text_x, score_text_y))
        pop_up_surface.blit(
            score_text_2, (score_text_x + score_text_w, score_text_y)
        )

        input_window_y = score_text_y + score_text_h + 40

        self._render_input_user(pop_up_surface, x, y, input_window_y)

        self.virtual_screen.blit(pop_up_surface, (x, y))

    def _draw_command(
        self, mouse_x: int, mouse_y: int, height_available: int
    ) -> None:
        width, height = (self.WIDTH / 1.2), (height_available - 40) // 3

        x, y = (self.WIDTH - width) // 2, (
            self.HEIGHT - height_available
        ) // 2 + 60

        color = self.NEON_PURPLE

        blinky_x, blinky_y = x + 40, y - 20
        clyde_x, clyde_y = x + width - 40, y - 20

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            color = self.NEON_PINK
            blinky_y, clyde_y = y - 25, y - 25

        self.virtual_screen.blit(self.img["blinky_down"], (blinky_x, blinky_y))
        self.virtual_screen.blit(self.img["clyde_down"], (clyde_x, clyde_y))

        pygame.draw.rect(
            self.virtual_screen,
            self.BLACK,
            pygame.Rect(x, y, width, height),
        )

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, width + 2, height + 2),
            1,
        )

        pygame.draw.line(
            self.virtual_screen,
            color,
            (self.WIDTH // 2, y + 14),
            (self.WIDTH // 2, y + height - 14),
            2,
        )

        basic_instructions_text_1 = self.font_back_game_over.render(
            "Basic commands", True, self.GRAY
        )
        basic_instructions_text_2 = self.font_front_game_over.render(
            "Basic commands", True, color
        )

        cheat_instructions_text_1 = self.font_back_game_over.render(
            "Cheat commands", True, self.GRAY
        )
        cheat_instructions_text_2 = self.font_front_game_over.render(
            "Cheat commands", True, color
        )

        basic_w, basic_h = basic_instructions_text_1.get_size()
        spe_w = cheat_instructions_text_1.get_width()

        basic_x = x + (width // 2 - basic_w) // 2
        spe_x = x + width // 2 + (width // 2 - spe_w) // 2

        self.virtual_screen.blit(basic_instructions_text_1, (basic_x, y + 10))
        self.virtual_screen.blit(basic_instructions_text_2, (basic_x, y + 10))

        self.virtual_screen.blit(cheat_instructions_text_1, (spe_x, y + 10))
        self.virtual_screen.blit(cheat_instructions_text_2, (spe_x, y + 10))

        offset_y = 20

        commands = {
            "up": self.font_basic.render("↑  up", True, color),
            "down": self.font_basic.render("↓  down", True, color),
            "left": self.font_basic.render("←  left", True, color),
            "right": self.font_basic.render("→  right", True, color),
        }

        command_w, command_h = commands["right"].get_size()
        command_x, command_y = (
            x + (width // 2 - command_w) // 2,
            y + basic_h + 30,
        )

        for text in commands.values():
            self.virtual_screen.blit(text, (command_x, command_y))
            command_y += offset_y + command_h

        cheats = {
            "speed": self.font_basic.render("s:  Speed * 2", True, color),
            "freeze": self.font_basic.render("f:  Freeze ghosts", True, color),
            "next": self.font_basic.render("l:  Level skip", True, color),
            "power": self.font_basic.render("p:  Instant power", True, color),
        }

        cheat_w, cheat_h = cheats["freeze"].get_size()
        cheat_x, cheat_y = (
            x + width // 2 + (width // 2 - cheat_w) // 2,
            y + basic_h + 30,
        )

        for text in cheats.values():
            self.virtual_screen.blit(text, (cheat_x, cheat_y))
            cheat_y += offset_y + cheat_h

    def _draw_rules(
        self, mouse_x: int, mouse_y: int, height_available: int
    ) -> None:
        width, height = int(self.WIDTH / 1.2), height_available // 2 + 20

        x, y = (self.WIDTH - width) // 2, (
            self.HEIGHT - height_available
        ) // 3 + height - 10

        color = self.NEON_PURPLE

        inky_x, inky_y = x + 40, y - 20
        pinky_x, pinky_y = x + width - 40, y - 20

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            color = self.NEON_PINK
            inky_y, pinky_y = y - 25, y - 25

        self.virtual_screen.blit(self.img["inky_down"], (inky_x, inky_y))
        self.virtual_screen.blit(self.img["pinky_down"], (pinky_x, pinky_y))

        pygame.draw.rect(
            self.virtual_screen,
            self.BLACK,
            pygame.Rect(x, y, width, height),
        )

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, width + 2, height + 2),
            1,
        )

        title_text_1 = self.font_back_game_over.render(
            "Rules", True, self.GRAY
        )
        title_text_2 = self.font_front_game_over.render("Rules", True, color)

        title_w, title_h = title_text_1.get_size()
        title_x, title_y = (self.WIDTH - title_w) // 2, y + 10

        self.virtual_screen.blit(title_text_1, (title_x, title_y))
        self.virtual_screen.blit(title_text_2, (title_x, title_y))

        rules = (
            "- Objective: Eat all pacgums to win the level.\n\n"
            "- Victory: Complete all 10 levels to win the \n"
            "  game.\n\n"
            f"- Lives: You start with {self.config.lives} lives.\n\n"
            "- Danger: Losing a life if touched by a ghost.\n\n"
            "- Power-up: Super-pacgums make ghosts edible \n  "
            "for a short time.\n\n"
            f"- Time: You have a {self.config.level_max_time}-second limit "
            "per level.\n\n"
            "- Controls: Use Arrow keys to move.\n\n"
            "- Pause: Press space to pause or resume at \n  any time."
        )

        text_rules = self.font_basic.render(rules, True, color)

        text_rules_w = text_rules.get_width()
        text_rules_x, text_rules_y = (
            x + (width - text_rules_w) // 2,
            y + title_h + 15,
        )

        self.virtual_screen.blit(text_rules, (text_rules_x, text_rules_y))

    def _draw_command_instructions(self, mouse_x: int, mouse_y: int) -> None:
        title_text_1 = self.font_back.render("Instructions", True, self.GRAY)
        title_text_2 = self.font_front.render(
            "Instructions", True, self.NEON_PINK
        )

        coord = ((self.WIDTH - title_text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(title_text_1, coord)
        self.virtual_screen.blit(title_text_2, coord)

        back_text_1 = self.font_back_game_over.render("Back", True, self.GRAY)
        back_text_2 = self.font_front_game_over.render(
            "Back", True, self.NEON_PURPLE
        )
        text_width, text_height = back_text_1.get_size()

        coord = (
            (self.WIDTH - back_text_1.get_width()) // 2,
            self.HEIGHT - back_text_1.get_height() - 20,
        )

        (
            self.interface["Back_instructions"][0],
            self.interface["Back_instructions"][1],
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
            back_text_2 = self.font_front_game_over.render(
                "Back", True, self.NEON_PINK
            )
            if not self.interface["Back_instructions"][2]:
                self._play_sound(None, self.sound["munch_2"], False, 0.5)
                self.interface["Back_instructions"][2] = True

        else:
            self.interface["Back_instructions"][2] = False

        self.virtual_screen.blit(back_text_1, coord)
        self.virtual_screen.blit(back_text_2, coord)

        height_available = (
            int(self.HEIGHT) - title_text_1.get_height() - text_height - 60
        )

        self._draw_command(mouse_x, mouse_y, height_available)
        self._draw_rules(mouse_x, mouse_y, height_available)

    def _render_instructions(self, mouse_x: int, mouse_y: int) -> None:
        self._draw_command_instructions(mouse_x, mouse_y)

    def _render_highscores(self, mouse_x: int, mouse_y: int) -> None:
        title_text_1 = self.font_back.render("Highscores", True, self.GRAY)
        title_text_2 = self.font_front.render(
            "Highscores", True, self.NEON_PINK
        )

        coord = ((self.WIDTH - title_text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(title_text_1, coord)
        self.virtual_screen.blit(title_text_2, coord)

        text = self.font_basic.render(
            "Available soon ...", True, self.NEON_PURPLE
        )
        self.virtual_screen.blit(
            text,
            (
                (self.WIDTH - text.get_width()) // 2,
                (self.HEIGHT - text.get_height()) // 2,
            ),
        )

        back_text_1 = self.font_back_game_over.render("Back", True, self.GRAY)
        back_text_2 = self.font_front_game_over.render(
            "Back", True, self.NEON_PURPLE
        )
        text_width, text_height = back_text_1.get_size()

        coord = (
            (self.WIDTH - back_text_1.get_width()) // 2,
            self.HEIGHT - back_text_1.get_height() - 20,
        )

        (
            self.interface["Back_highscores"][0],
            self.interface["Back_highscores"][1],
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
            back_text_2 = self.font_front_game_over.render(
                "Back", True, self.NEON_PINK
            )
            if not self.interface["Back_highscores"][2]:
                self._play_sound(None, self.sound["munch_2"], False, 0.5)
                self.interface["Back_highscores"][2] = True

        else:
            self.interface["Back_highscores"][2] = False

        self.virtual_screen.blit(back_text_1, coord)
        self.virtual_screen.blit(back_text_2, coord)

    def _draw_home_text(self, mouse_x: int, mouse_y: int) -> int:
        title_img = self.img["title"]

        w, h = title_img.get_size()
        x, y = (self.WIDTH - w) // 2, -40

        offset_y = 0

        hover = False

        for key in self.interface["text"].keys():
            coord = (40, h + 120 + offset_y)

            text_1 = self.font_back.render(key, True, self.GRAY)
            text_2 = self.font_front.render(key, True, self.PACMAN_YELLOW)

            text_width, text_height = (
                text_1.get_width(),
                text_1.get_height(),
            )

            self.interface["text"][key][0], self.interface["text"][key][1] = (
                coord[0],
                coord[0] + text_width,
            ), (coord[1], coord[1] + text_height)

            if (coord[0] <= mouse_x <= coord[0] + text_width) and (
                coord[1] <= mouse_y <= coord[1] + text_height
            ):
                text_1 = self.font_back.render(key, True, self.NEON_BLUE)
                if key == "Exit" and not self.interface["text"][key][2]:
                    self._play_sound(None, self.sound["munch_2"], False, 0.5)
                    self.interface["text"][key][2] = True
                else:
                    if not self.interface["text"][key][2]:
                        self._play_sound(
                            None, self.sound["munch_1"], False, 0.5
                        )
                        self.interface["text"][key][2] = True
                hover = True

            self.virtual_screen.blit(text_1, coord)
            self.virtual_screen.blit(text_2, coord)

            offset_y += 80

        self.virtual_screen.blit(title_img, (x, y))

        if not hover:
            for value in self.interface["text"].values():
                value[2] = False

        volume_img = (
            pygame.transform.scale(self.img["volume_up"], (40, 40))
            if self.music_on
            else pygame.transform.scale(self.img["volume_off"], (40, 40))
        )

        volume_w, volume_h = volume_img.get_size()

        self.interface["volume_home"] = (
            (40, 40 + volume_w),
            (120 + h + offset_y, 120 + h + offset_y + volume_h),
        )

        self.virtual_screen.blit(volume_img, (40, 120 + h + offset_y))

        hover_music_color = self.NEON_GREEN if self.music_on else self.NEON_RED

        if (
            40 <= mouse_x <= 40 + volume_w
            and 120 + h + offset_y <= mouse_y <= 120 + h + offset_y + volume_h
        ):
            pygame.draw.rect(
                self.virtual_screen,
                hover_music_color,
                pygame.Rect(
                    40 - 1, 120 + h + offset_y - 1, volume_w + 2, volume_h + 2
                ),
                1,
            )

        return h

    def _draw_home_animation(self, h: int) -> None:
        offset_x = 0

        if not self.interface["counter"] % 2:
            width, height = self.interface[1]["ghosts"][0].get_size()

            for ghost in self.interface[1]["ghosts"]:
                if isinstance(ghost, pygame.Surface):
                    x, y = self.interface["pos_x"] + offset_x, h - height
                    self.virtual_screen.blit(ghost, (x, y))

                    offset_x += width + 10

            self.interface["anim_counter"] += 1
            anim_frame = self.interface["anim_counter"]
            pac_man_img = self.interface[1]["pac_man"][(anim_frame // 4) % 4]

            pac_man = pygame.transform.scale(pac_man_img, (width, height))

            self.virtual_screen.blit(
                pac_man,
                (self.interface["pos_x"] + offset_x + 20, h - height),
            )
            self.interface["pos_x"] += 2

            if self.interface["pos_x"] == self.virtual_screen.get_width():
                self.interface["counter"] += 1
                self.interface["pos_x"] = -self.interface["start_x"]
        else:
            width, height = self.interface[1]["ghosts"][0].get_size()

            self.interface["anim_counter"] += 1
            anim_frame = self.interface["anim_counter"]
            pac_man_img = self.interface[1]["pac_man"][(anim_frame // 4) % 4]

            pac_man = pygame.transform.scale(pac_man_img, (width, height))

            self.virtual_screen.blit(
                pac_man,
                (self.interface["pos_x"], h - height),
            )

            offset_x = width + 20

            for i in range(4):
                ghost_scared = pygame.transform.scale(
                    self.interface[2]["scared"][(anim_frame // 8) % 2],
                    (width, height),
                )
                self.virtual_screen.blit(
                    ghost_scared,
                    (self.interface["pos_x"] + offset_x, h - height),
                )

                offset_x += width + 10

            self.interface["pos_x"] += 2

            if self.interface["pos_x"] == self.virtual_screen.get_width():
                self.interface["counter"] += 1
                self.interface["pos_x"] = -self.interface["start_x"]

    def _render_home(self, mouse_x: int, mouse_y: int) -> None:
        h = self._draw_home_text(mouse_x, mouse_y)
        self._draw_home_animation(h)

    def _render(self, mouse_x: int, mouse_y: int) -> None:
        self.virtual_screen.fill(self.BLACK)

        if self.state == GameState.MENU:
            self._render_home(mouse_x, mouse_y)
        elif self.state == GameState.INFO:
            self._render_instructions(mouse_x, mouse_y)
        elif self.state == GameState.SCORE:
            self._render_highscores(mouse_x, mouse_y)
        elif self.state == GameState.WIN:
            self._render_win(mouse_x, mouse_y)
        else:
            self._render_game(mouse_x, mouse_y)

    def _manage_events(
        self, events: List[Event], mouse_x: int, mouse_y: int
    ) -> bool:
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                if not self.home_page_sound_play:
                    self._play_sound(
                        "assets/media/game_start.wav", None, False, 0.5
                    )
                    self.home_page_sound_play = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for key, value in self.interface["text"].items():
                            x_min, x_max = value[0]
                            y_min, y_max = value[1]

                            if (x_min <= mouse_x <= x_max) and (
                                y_min <= mouse_y <= y_max
                            ):
                                if key == "Start Game":
                                    self.state = GameState.STARTING_LEVEL
                                    self.playing_state = PlayingState.RETREATE
                                    self.current_level = 1
                                    self.score = 0
                                    self.lives = self.config.lives
                                    self.pseudo = ""
                                    self.countdown_play = False
                                    self._generate_map()
                                    self.home_page_sound_play = False
                                    self.speed_cheat = False
                                    self.freeze_cheat = False

                                elif key == "View Highscores":
                                    self.state = GameState.SCORE
                                elif key == "Instructions":
                                    self.state = GameState.INFO
                                elif key == "Exit":
                                    return False
                        x_min_volume, x_max_volume = self.interface[
                            "volume_home"
                        ][0]
                        y_min_volume, y_max_volume = self.interface[
                            "volume_home"
                        ][1]

                        if (x_min_volume <= mouse_x <= x_max_volume) and (
                            y_min_volume <= mouse_y <= y_max_volume
                        ):
                            if not self.music_on:
                                self.music_on = True
                            else:
                                self.music_on = False
                                pygame.mixer.music.stop()

            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.pac_man.set_direction(Directions.UP)
                    elif event.key == pygame.K_RIGHT:
                        self.pac_man.set_direction(Directions.RIGHT)
                    elif event.key == pygame.K_LEFT:
                        self.pac_man.set_direction(Directions.LEFT)
                    elif event.key == pygame.K_DOWN:
                        self.pac_man.set_direction(Directions.DOWN)
                    elif event.key == pygame.K_SPACE:
                        self._load_pause_info()
                        self.state = GameState.PAUSED
                        pygame.mixer.music.stop()
                        self.music_load = False
                    elif event.key == pygame.K_l:
                        self.pac_gums_coord = []
                    elif event.key == pygame.K_s:
                        if not self.speed_cheat:
                            self.speed_cheat = True
                            self.pac_man.speed *= 2
                        else:
                            self.speed_cheat = False
                            self.pac_man.speed //= 2
                    elif event.key == pygame.K_p:
                        self.playing_state = PlayingState.POWER
                        self.music_load = False
                        self.power_time = pygame.time.get_ticks()

                        for ghost in self.ghosts.values():
                            if ghost.mode != Mode.EAT:
                                ghost.mode = Mode.SCARED
                                if not self.freeze_cheat:
                                    ghost.speed = 1
                    elif event.key == pygame.K_f:
                        if not self.freeze_cheat:
                            self.freeze_cheat = True
                            for ghost in self.ghosts.values():
                                if ghost.mode != Mode.EAT:
                                    ghost.speed = 0
                        else:
                            self.freeze_cheat = False
                            for ghost in self.ghosts.values():
                                if self.playing_state == PlayingState.POWER:
                                    ghost.speed = 1
                                else:
                                    ghost.speed = 2

            elif self.state == GameState.PAUSED:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min_exit, x_max_exit = self.interface["Exit_paused"][
                            0
                        ]
                        y_min_exit, y_max_exit = self.interface["Exit_paused"][
                            1
                        ]

                        x_min_resume, x_max_resume = self.interface[
                            "resume_paused"
                        ][0]
                        y_min_resume, y_max_resume = self.interface[
                            "resume_paused"
                        ][1]

                        x_min_volume, x_max_volume = self.interface["volume"][
                            0
                        ]
                        y_min_volume, y_max_volume = self.interface["volume"][
                            1
                        ]

                        if (x_min_exit <= mouse_x <= x_max_exit) and (
                            y_min_exit <= mouse_y <= y_max_exit
                        ):
                            self.state = GameState.MENU

                        elif (x_min_resume <= mouse_x <= x_max_resume) and (
                            y_min_resume <= mouse_y <= y_max_resume
                        ):
                            self.state = GameState.PLAYING
                            self._depause_game()
                        elif (x_min_volume <= mouse_x <= x_max_volume) and (
                            y_min_volume <= mouse_y <= y_max_volume
                        ):
                            if not self.music_on:
                                self.music_on = True
                            else:
                                self.music_on = False
                                pygame.mixer.music.stop()

            elif self.state == GameState.SCORE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.interface["Back_highscores"][0]
                        y_min, y_max = self.interface["Back_highscores"][1]

                        if (x_min <= mouse_x <= x_max) and (
                            y_min <= mouse_y <= y_max
                        ):
                            self.state = GameState.MENU

            elif (
                self.state == GameState.GAME_OVER
                or self.state == GameState.WIN
            ):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.interface["Back_game_over"][0]
                        y_min, y_max = self.interface["Back_game_over"][1]

                        x_min_input, x_max_input = self.interface[
                            "input_window"
                        ][0]
                        y_min_input, y_max_input = self.interface[
                            "input_window"
                        ][1]

                        if (x_min <= mouse_x <= x_max) and (
                            y_min <= mouse_y <= y_max
                        ):
                            self.state = GameState.MENU
                            self.in_typing = False

                        elif (x_min_input <= mouse_x <= x_max_input) and (
                            y_min_input <= mouse_y <= y_max_input
                        ):
                            self.in_typing = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pass
                    elif event.key == pygame.K_BACKSPACE:
                        if self.pseudo:
                            self.pseudo = self.pseudo[:-1]
                    else:
                        if len(self.pseudo) < 12:
                            self.pseudo += event.unicode

            elif self.state == GameState.INFO:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.interface["Back_instructions"][0]
                        y_min, y_max = self.interface["Back_instructions"][1]

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
                self.pac_man.speed = 2

                for ghost in self.ghosts.values():
                    ghost.speed = 2

                self.level_pass_animation = False
                self.state = GameState.PLAYING
                self.playing_state = PlayingState.RETREATE
                self.pac_man.set_direction(Directions.UP)
                self.level_starting_time = pygame.time.get_ticks()
        return True

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

        self._play_sound("assets/media/game_start.wav", None, False, 0.5)
        self.home_page_sound_play = True

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

            pygame.display.flip()
