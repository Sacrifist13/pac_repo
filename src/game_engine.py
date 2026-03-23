import pygame
import sys
from pygame.event import Event
from enum import Enum, auto
from typing import List
from pathlib import Path
from .loader import Loader


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SCORE = auto()


class GameEngine:

    def _init(self) -> None:
        self.state = GameState.MENU
        self.img = {}

        loader = Loader()
        self.config = loader.load_config(sys.argv)

        assets_dir = Path("assets")

        for img in assets_dir.rglob("*.png"):
            img_name = img.name.split(".")[0]
            self.img[img_name] = pygame.image.load(img).convert_alpha()

        print(self.img)

    def _manage_events(self, events: List[Event]) -> bool:
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                pass

            elif self.state == GameState.PLAYING:
                pass

            elif self.state == GameState.PAUSED:
                pass

            elif self.state == GameState.SCORE:
                pass

            elif self.state == GameState.GAME_OVER:
                pass

    def run(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((800, 800))

        self._init()
        running = True

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
