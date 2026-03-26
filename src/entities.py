import pygame
from enum import Enum


class Directions(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class PacMan:
    def __init__(self, x, y, img, speed, cell_size) -> None:
        self.x: int = x * cell_size
        self.y: int = y * cell_size
        self.img = img
        self.speed: int = speed
        self.directions = None

        self.rotation = {1: 90, 2: -90, 3: 0, 4: 180}

    def move(self, map, cell_size, offset_x, offset_y):
        if self.directions is None:
            return

        pass

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        img = self.img["pac_2"]

        if self.directions:
            current_img = pygame.transform.rotate(
                img, self.rotation[self.directions.value]
            )
        else:
            current_img = img

        px = offset_x + self.x + ((cell_size - current_img.get_width()) // 2)
        py = offset_y + self.y + ((cell_size - current_img.get_height()) // 2)

        surface.blit(current_img, (px, py))


class Blinky:
    def __init__(self, x, y, img, speed) -> None:
        self.x: int = x
        self.y: int = y
        self.img = img
        self.speed: int = speed

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["blinky_right"]

        px = (
            offset_x
            + (self.x * cell_size)
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + (self.y * cell_size)
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))


class Clyde:
    def __init__(self, x, y, img, speed) -> None:
        self.x: int = x
        self.y: int = y
        self.img = img
        self.speed: int = speed

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["clyde_right"]

        px = (
            offset_x
            + (self.x * cell_size)
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + (self.y * cell_size)
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))


class Inky:
    def __init__(self, x, y, img, speed) -> None:
        self.x: int = x
        self.y: int = y
        self.img = img
        self.speed: int = speed

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["inky_left"]

        px = (
            offset_x
            + (self.x * cell_size)
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + (self.y * cell_size)
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))


class Pinky:
    def __init__(self, x, y, img, speed) -> None:
        self.x: int = x
        self.y: int = y
        self.img = img
        self.speed: int = speed

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["pinky_left"]

        px = (
            offset_x
            + (self.x * cell_size)
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + (self.y * cell_size)
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))
