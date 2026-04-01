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
    GRAY = (155, 155, 155)
    PACMAN_YELLOW = (255, 255, 0)
    NEON_BLUE = (33, 33, 255)
    NEON_PINK = (255, 20, 147)
    PURPLE = (133, 76, 135)

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

        for ghost in self.ghosts.values():
            ghost.draw_on_surface(
                self.virtual_screen,
                self.game_offset_x,
                self.game_offset_y,
                self.playing_state,
            )

    def _move_entities(self) -> None:

        self.pac_man.move(self.map)

        if self.playing_state == PlayingState.POWER:
            for ghost in self.ghosts.values():
                if ghost.mode == Mode.NORMAL:
                    ghost.move_random(self.map)
                elif ghost.mode == Mode.EAT:
                    if ghost.move_to_start_pos(self.map):
                        ghost.mode = Mode.NORMAL
                        ghost.speed = 1

        else:
            # ghost.move() quand les algos des fantomes seront termines
            for ghost in self.ghosts.values():
                if ghost.mode == Mode.NORMAL:
                    ghost.move_random(self.map)
                elif ghost.mode == Mode.EAT:
                    if ghost.move_to_start_pos(self.map):
                        ghost.mode = Mode.NORMAL
                        ghost.speed = 2

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

    def _is_pac_man_catch(self) -> bool:
        if self.pac_man.mode == Mode.INVICIBLE:
            return False

        cell_size = self.pac_man.cell_size

        pac_rect = self._get_hitbox(
            self.pac_man.pixel_x, self.pac_man.pixel_y, cell_size
        )

        for ghost in self.ghosts.values():
            if ghost.mode == Mode.NORMAL:
                ghost_rect = self._get_hitbox(
                    ghost.pixel_x, ghost.pixel_y, cell_size
                )
                if pac_rect.colliderect(ghost_rect):
                    if self.playing_state == PlayingState.POWER:
                        self.sound["eat_ghost"].play()
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
                    return True

        return False

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

    def _render_pac_man_dying(self) -> bool:
        x, y = self.pac_man.pixel_x, self.pac_man.pixel_y
        cell_size = self.pac_man.cell_size

        current_time = pygame.time.get_ticks()

        if self.death_time + 1200 <= current_time:
            self.pac_man.reset_pos()
            self.playing_state = PlayingState.RETREATE
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

        color = self.PURPLE

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

        pop_up_surface.blit(text_1, (text_x, 2))
        pop_up_surface.blit(text_2, (text_x, 2))

        back_text_1 = self.font_back_game_over.render("BACK", True, self.GRAY)

        back_text_w, back_text_h = back_text_1.get_size()

        back_text_x = (w - back_text_w) // 2
        back_text_y = h - back_text_h - 4

        back_text_front_color = self.PURPLE
        if (
            x + back_text_x <= mouse_x <= x + back_text_x + back_text_w
            and y + back_text_y <= mouse_y <= y + back_text_y + back_text_h
        ):
            back_text_front_color = self.NEON_PINK

        back_text_2 = self.font_front_game_over.render(
            "BACK", True, back_text_front_color
        )

        self.home_page["back_game_over"] = (
            (x + back_text_x, x + back_text_x + back_text_w),
            (y + back_text_y, y + back_text_y + back_text_h),
        )

        pop_up_surface.blit(back_text_1, (back_text_x, back_text_y))
        pop_up_surface.blit(back_text_2, (back_text_x, back_text_y))

        self.virtual_screen.blit(pop_up_surface, (x, y))

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
                self.sound["start"].set_volume(0.2)
                self.sound["start"].play()
            self._render_starting_level()

            return

        if self.state == GameState.GAME_OVER:
            self._render_game_over(mouse_x, mouse_y)

        elif self.state == GameState.PLAYING:

            if not self._draw_time_left():
                self.state = GameState.GAME_OVER

            if self.playing_state == PlayingState.DEATH:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    self.sound["pacman_death"].set_volume(0.5)
                    self.sound["pacman_death"].play()
                    self.music_load = True

                if self._render_pac_man_dying():
                    self.pac_man.dying_time = current_time
                    self.pac_man.mode = Mode.INVICIBLE

                    self.music_load = False

                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                return

            if self.playing_state == PlayingState.POWER:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("assets/media/power_pellet.wav")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    self.music_load = True

                self._draw_score_eating()

                if current_time > self.power_time + 6000:
                    self.music_load = False
                    self.playing_state = PlayingState.RETREATE
                    self.ghosts_eat = 0

                    for ghost in self.ghosts.values():
                        if ghost.mode == Mode.NORMAL:
                            ghost.speed = 2
            else:
                pygame.mixer.music.stop()

            if self.pac_man.mode == Mode.INVICIBLE:
                if current_time > self.pac_man.dying_time + 3000:
                    self.pac_man.mode = Mode.NORMAL

            self._move_entities()

            if self._eat_pac_gums():
                self.score += self.config.points_per_pacgum

                if len(self.pac_gums_coord) % 2:
                    self.sound["munch_1"].play()
                else:
                    self.sound["munch_2"].play()

            if self._eat_super_pac_gums():
                self.score += self.config.points_per_super_pacgum

                self.playing_state = PlayingState.POWER
                self.music_load = False
                self.power_time = current_time

                for ghost in self.ghosts.values():
                    ghost.speed = 1

            if self._is_pac_man_catch():
                if self.playing_state == PlayingState.POWER:
                    pass
                else:
                    self.playing_state = PlayingState.DEATH
                    self.music_load = False
                    self.death_time = current_time
                    self.lives -= 1

    def _draw_command(
        self, mouse_x: int, mouse_y: int, height_available: int
    ) -> None:
        width, height = (self.WIDTH / 1.2), (height_available - 40) // 3

        x, y = (self.WIDTH - width) // 2, (
            self.HEIGHT - height_available
        ) // 2 + 60

        color = self.PURPLE

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x, y, width, height),
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
        spe_w, spe_h = cheat_instructions_text_1.get_size()

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
        ) // 3 + height - 20

        color = self.PURPLE

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x, y, width, height),
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

        text_rules_w, text_rules_h = text_rules.get_size()
        text_rules_x, text_rules_y = (
            x + (width - text_rules_w) // 2,
            y + title_h + 15,
        )

        self.virtual_screen.blit(text_rules, (text_rules_x, text_rules_y))

    def _draw_command_instructions(self, mouse_x: int, mouse_y: int) -> None:
        w, h = self.virtual_screen.get_size()

        title_text_1 = self.font_back.render("Instructions", True, self.GRAY)
        title_text_2 = self.font_front.render(
            "Instructions", True, self.NEON_PINK
        )

        coord = ((w - title_text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(title_text_1, coord)
        self.virtual_screen.blit(title_text_2, coord)

        back_text_1 = self.font_back_game_over.render("Back", True, self.GRAY)
        back_text_2 = self.font_front_game_over.render(
            "Back", True, self.PURPLE
        )
        text_width, text_height = back_text_1.get_size()

        coord = (
            (w - back_text_1.get_width()) // 2,
            h - back_text_1.get_height() - 20,
        )

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
            back_text_2 = self.font_front_game_over.render(
                "Back", True, self.NEON_PINK
            )

        else:
            self.home_page["Back"][2] = False

        self.virtual_screen.blit(back_text_1, coord)
        self.virtual_screen.blit(back_text_2, coord)

        height_available = (
            int(self.HEIGHT) - title_text_1.get_height() - text_height - 60
        )

        self._draw_command(mouse_x, mouse_y, height_available)
        self._draw_rules(mouse_x, mouse_y, height_available)

    def _render_instructions(self, mouse_x: int, mouse_y: int) -> None:
        self._draw_command_instructions(mouse_x, mouse_y)

    def _draw_home_text(self, mouse_x: int, mouse_y: int) -> int:
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

        return h

    def _draw_home_animation(self, h: int) -> None:
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

    def _render_home(self, mouse_x: int, mouse_y: int) -> None:
        h = self._draw_home_text(mouse_x, mouse_y)
        self._draw_home_animation(h)

    def _render(self, mouse_x: int, mouse_y: int) -> None:
        self.virtual_screen.fill(self.BLACK)

        if self.state == GameState.MENU:
            self._render_home(mouse_x, mouse_y)
        elif self.state == GameState.INFO:
            self._render_instructions(mouse_x, mouse_y)
        else:
            self._render_game(mouse_x, mouse_y)

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
                                    self.score = 0
                                    self.lives = self.config.lives
                                    self.countdown_play = False
                                    self._generate_map()

                                elif key == "View Highscores":
                                    self.state = GameState.SCORE
                                elif key == "Instructions":
                                    self.state = GameState.INFO
                                elif key == "Exit":
                                    return False

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

            elif self.state == GameState.PAUSED:
                pass

            elif self.state == GameState.SCORE:
                pass

            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.home_page["back_game_over"][0]
                        y_min, y_max = self.home_page["back_game_over"][1]

                        if (x_min <= mouse_x <= x_max) and (
                            y_min <= mouse_y <= y_max
                        ):
                            self.state = GameState.MENU

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
                self.pac_man.speed = 2

                for ghost in self.ghosts.values():
                    ghost.speed = 2

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

            pygame.display.flip()
