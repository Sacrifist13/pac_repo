import pygame
import random
from .enums_class import Directions, PlayingState


class PacMan:
    def __init__(self, x, y, img, speed, cell_size, sound) -> None:
        self.grid_x = x
        self.grid_y = y

        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.img = img
        self.speed = speed
        self.cell_size = cell_size
        self.direction = None
        self.next_direction = None
        self.moving = False

        self.sound = sound
        self.munch_toggle = False

        self.current_img = self.img["pac_2"]

        self.rotation = {
            Directions.UP: 90,
            Directions.DOWN: -90,
            Directions.RIGHT: 0,
            Directions.LEFT: 180,
        }

    def _set_grid_x(self, pac_x, cell_size) -> None:
        self.grid_x = pac_x
        self.pixel_x = self.grid_x * cell_size
        self.target_x = self.pixel_x

    def _set_grid_y(self, pac_y, cell_size) -> None:
        self.grid_y = pac_y
        self.pixel_y = self.grid_y * cell_size
        self.target_y = self.pixel_y

    def _is_wall(self, map, grid_x, grid_y, direction):
        cell = map[grid_y][grid_x][0]

        if direction == Directions.UP:
            return bool(cell & 1)
        if direction == Directions.RIGHT:
            return bool(cell & 2)
        if direction == Directions.DOWN:
            return bool(cell & 4)
        if direction == Directions.LEFT:
            return bool(cell & 8)
        return False

    def set_direction(self, direction):
        self.next_direction = direction

    def move(self, map, cell_size, pac_gums, super_pac_gums):
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            for direction in [self.next_direction, self.direction]:

                if direction is None:
                    continue

                next_x, next_y = 0, 0

                if direction == Directions.UP:
                    next_y = -1
                elif direction == Directions.RIGHT:
                    next_x = 1
                elif direction == Directions.DOWN:
                    next_y = 1
                elif direction == Directions.LEFT:
                    next_x = -1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y

                if not self._is_wall(map, self.grid_x, self.grid_y, direction):
                    self.moving = True
                    self.grid_x = next_gx
                    self.grid_y = next_gy
                    self.next_direction = (
                        self.next_direction
                        if self.direction == direction
                        else None
                    )
                    self.direction = direction
                    self.target_x = self.grid_x * cell_size
                    self.target_y = self.grid_y * cell_size
                    break
        else:
            self.moving = True

            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_y)

            for y, x in pac_gums:
                if (
                    self.pixel_x == x * cell_size
                    and self.pixel_y == y * cell_size
                ):
                    pac_gums.remove((y, x))
                    if not self.munch_toggle:
                        self.sound["munch_1"].play()
                        self.munch_toggle = True
                    else:
                        self.sound["munch_2"].play()
                        self.munch_toggle = False
                    break

            for y, x in super_pac_gums:
                if (
                    self.pixel_x == x * cell_size
                    and self.pixel_y == y * cell_size
                ):
                    super_pac_gums.remove((y, x))
                    break

    def draw(self, surface, offset_x, offset_y, cell_size):

        if self.moving:
            if (
                self.direction == Directions.UP
                or self.direction == Directions.DOWN
            ):
                i = (self.pixel_y // 8) % 4
            elif (
                self.direction == Directions.RIGHT
                or self.direction == Directions.LEFT
            ):
                i = (self.pixel_x // 8) % 4

            self.current_img = self.img["pac_" + str(i + 1)]

        if self.direction:
            current_img = pygame.transform.rotate(
                self.current_img, self.rotation[self.direction]
            )
        else:
            current_img = self.current_img

        px = (
            offset_x
            + self.pixel_x
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))


class Blinky:
    def __init__(self, x, y, img, speed, cell_size) -> None:
        self.grid_x: int = x
        self.grid_y: int = y
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size
        self.img = img
        self.speed: int = speed

        self.direction = None
        self.next_direction = None

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.frame_directions = ["up", "down", "right", "left"]

    def _is_wall(self, map, grid_x, grid_y, direction):
        cell = map[grid_y][grid_x][0]

        if direction == Directions.UP:
            return bool(cell & 1)
        if direction == Directions.RIGHT:
            return bool(cell & 2)
        if direction == Directions.DOWN:
            return bool(cell & 4)
        if direction == Directions.LEFT:
            return bool(cell & 8)
        return False

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["blinky_right"]

        if self.speed != 0 and self.direction:
            current_img = self.img[
                "blinky_" + self.frame_directions[self.direction.value - 1]
            ]

        px = (
            offset_x
            + self.pixel_x
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))

    def move(self, map, cell_size) -> None:
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            directions = list(Directions)
            random.shuffle(directions)

            for direction in directions:

                if direction is None:
                    continue

                next_x, next_y = 0, 0

                if direction == Directions.UP:
                    next_y = -1
                elif direction == Directions.RIGHT:
                    next_x = 1
                elif direction == Directions.DOWN:
                    next_y = 1
                elif direction == Directions.LEFT:
                    next_x = -1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y

                if not self._is_wall(map, self.grid_x, self.grid_y, direction):
                    self.moving = True
                    self.grid_x = next_gx
                    self.grid_y = next_gy
                    self.next_direction = None
                    self.direction = direction
                    self.target_x = self.grid_x * cell_size
                    self.target_y = self.grid_y * cell_size
                    break
        else:
            self.moving = True

            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_y)


class Clyde:
    def __init__(self, x, y, img, speed, cell_size) -> None:
        self.grid_x: int = x
        self.grid_y: int = y
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size
        self.img = img
        self.speed: int = speed

        self.direction = None
        self.next_direction = None

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.frame_directions = ["up", "down", "right", "left"]

    def _is_wall(self, map, grid_x, grid_y, direction):
        cell = map[grid_y][grid_x][0]

        if direction == Directions.UP:
            return bool(cell & 1)
        if direction == Directions.RIGHT:
            return bool(cell & 2)
        if direction == Directions.DOWN:
            return bool(cell & 4)
        if direction == Directions.LEFT:
            return bool(cell & 8)
        return False

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["clyde_right"]

        if self.speed != 0 and self.direction:
            current_img = self.img[
                "clyde_" + self.frame_directions[self.direction.value - 1]
            ]

        px = (
            offset_x
            + self.pixel_x
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))

    def move(self, map, cell_size) -> None:
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            directions = list(Directions)
            random.shuffle(directions)

            for direction in directions:

                if direction is None:
                    continue

                next_x, next_y = 0, 0

                if direction == Directions.UP:
                    next_y = -1
                elif direction == Directions.RIGHT:
                    next_x = 1
                elif direction == Directions.DOWN:
                    next_y = 1
                elif direction == Directions.LEFT:
                    next_x = -1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y

                if not self._is_wall(map, self.grid_x, self.grid_y, direction):
                    self.moving = True
                    self.grid_x = next_gx
                    self.grid_y = next_gy
                    self.next_direction = None
                    self.direction = direction
                    self.target_x = self.grid_x * cell_size
                    self.target_y = self.grid_y * cell_size
                    break
        else:
            self.moving = True

            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_y)


class Inky:
    def __init__(self, x, y, img, speed, cell_size) -> None:
        self.grid_x: int = x
        self.grid_y: int = y
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size
        self.img = img
        self.speed: int = speed

        self.direction = None
        self.next_direction = None

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.frame_directions = ["up", "down", "right", "left"]

    def _is_wall(self, map, grid_x, grid_y, direction):
        cell = map[grid_y][grid_x][0]

        if direction == Directions.UP:
            return bool(cell & 1)
        if direction == Directions.RIGHT:
            return bool(cell & 2)
        if direction == Directions.DOWN:
            return bool(cell & 4)
        if direction == Directions.LEFT:
            return bool(cell & 8)
        return False

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:

        current_img = self.img["inky_right"]

        if self.speed != 0 and self.direction:
            current_img = self.img[
                "inky_" + self.frame_directions[self.direction.value - 1]
            ]

        px = (
            offset_x
            + self.pixel_x
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))

    def move(self, map, cell_size) -> None:
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            directions = list(Directions)
            random.shuffle(directions)

            for direction in directions:

                if direction is None:
                    continue

                next_x, next_y = 0, 0

                if direction == Directions.UP:
                    next_y = -1
                elif direction == Directions.RIGHT:
                    next_x = 1
                elif direction == Directions.DOWN:
                    next_y = 1
                elif direction == Directions.LEFT:
                    next_x = -1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y

                if not self._is_wall(map, self.grid_x, self.grid_y, direction):
                    self.moving = True
                    self.grid_x = next_gx
                    self.grid_y = next_gy
                    self.next_direction = None
                    self.direction = direction
                    self.target_x = self.grid_x * cell_size
                    self.target_y = self.grid_y * cell_size
                    break
        else:
            self.moving = True

            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_y)


class Pinky:
    def __init__(self, x, y, img, speed, cell_size) -> None:
        self.grid_x: int = x
        self.grid_y: int = y
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size
        self.img = img
        self.speed: int = speed

        self.direction = None
        self.next_direction = None

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.frame_directions = ["up", "down", "right", "left"]

    def _is_wall(self, map, grid_x, grid_y, direction):
        cell = map[grid_y][grid_x][0]

        if direction == Directions.UP:
            return bool(cell & 1)
        if direction == Directions.RIGHT:
            return bool(cell & 2)
        if direction == Directions.DOWN:
            return bool(cell & 4)
        if direction == Directions.LEFT:
            return bool(cell & 8)
        return False

    def draw(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        cell_size: int,
        playing_state: PlayingState,
    ) -> None:

        current_img = self.img["pinky_right"]

        if (
            self.speed != 0
            and self.direction
            and playing_state != PlayingState.POWER
        ):
            current_img = self.img[
                "pinky_" + self.frame_directions[self.direction.value - 1]
            ]
        elif playing_state == PlayingState.POWER:
            if (self.pixel_x // 6) % 2:
                current_img = self.img["scared_1"]
            else:
                current_img = self.img["scared_2"]

        px = (
            offset_x
            + self.pixel_x
            + ((cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))

    def move(self, map, cell_size) -> None:
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            directions = list(Directions)

            random.shuffle(directions)

            for direction in directions:

                if direction is None:
                    continue

                next_x, next_y = 0, 0

                if direction == Directions.UP:
                    next_y = -1
                elif direction == Directions.RIGHT:
                    next_x = 1
                elif direction == Directions.DOWN:
                    next_y = 1
                elif direction == Directions.LEFT:
                    next_x = -1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y

                if not self._is_wall(map, self.grid_x, self.grid_y, direction):
                    self.moving = True
                    self.grid_x = next_gx
                    self.grid_y = next_gy
                    self.next_direction = None
                    self.direction = direction
                    self.target_x = self.grid_x * cell_size
                    self.target_y = self.grid_y * cell_size
                    break
        else:
            self.moving = True

            if self.pixel_x < self.target_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_y)
