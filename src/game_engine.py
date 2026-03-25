import os
import pygame
import sys
from mazegen import MazeGenerator
from pygame.event import Event
from enum import Enum, auto
from typing import List, Dict, Any
from pathlib import Path
from .loader import Loader


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SCORE = auto()
    INFO = auto()


class GameEngine:

    WIDTH = 800
    HEIGHT = 800
    BLACK = (0, 0, 0)
    GRAY = (155, 155, 155)
    PACMAN_YELLOW = (255, 255, 0)
    NEON_BLUE = (33, 33, 255)

    def _init(self) -> None:
        self.state = GameState.MENU
        self.img: Dict[str, pygame.Surface] = {}
        self.sound: Dict[str, Any] = {}

        loader = Loader()
        self.config = loader.load_config(sys.argv)

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
                "View HighScores": [(0, 0), (0, 0), False],
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
                                    self.state = GameState.PLAYING
                                elif key == "View Highscores":
                                    self.state = GameState.SCORE
                                elif key == "Instructions":
                                    self.state = GameState.INFO
                                else:
                                    return False

            elif self.state == GameState.PLAYING:
                pass

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
        return True

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

        pygame.init()
        pygame.mixer.init()

        self.real_screen = pygame.display.set_mode(
            (800, 800), pygame.RESIZABLE
        )

        self.virtual_screen = pygame.Surface((800, 800))

        self._init()

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
