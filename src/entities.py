import pygame
import random
import heapq
from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod
from .enums_class import Directions, PlayingState, Mode


class Entity(ABC):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
    ) -> None:
        self.name = name

        self.mode = Mode.NORMAL

        self.starting_x = grid_x
        self.starting_y = grid_y

        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * cell_size
        self.pixel_y = grid_y * cell_size
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.cell_size = cell_size

        self.img = img

        self.speed = speed
        self.direction: Directions | None = None
        self.next_direction: Directions | None = None

        self.moving = False
        self.j = 0

    def _is_wall(
        self,
        map: List[List[List[int]]],
        grid_x: int,
        grid_y: int,
        direction: Directions,
    ) -> bool:
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

    @abstractmethod
    def draw_on_surface(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        playing_state: PlayingState,
    ) -> None:
        pass


class Ghost(Entity, ABC):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
        scared_img: List[pygame.Surface],
        eaten_img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(name, grid_x, grid_y, speed, cell_size, img)
        self.scared_img = scared_img
        self.eaten_img = eaten_img
        self.path_to_start: List[Tuple[int, int]] | None = None

    def _calculate_f(
        self, target_grid_x: int, target_grid_y: int, x: int, y: int, g: int
    ) -> int:
        h = abs(target_grid_x - x) + abs(target_grid_y - y)

        return h + g

    def _find_fastest_way_to(
        self,
        map: List[List[List[int]]],
        target_grid_x: int,
        target_grid_y: int,
    ) -> Any:

        f_init = self._calculate_f(
            target_grid_x, target_grid_y, self.grid_x, self.grid_y, 0
        )

        queue: List[Any] = [(f_init, 0, (self.grid_y, self.grid_x), [])]

        directions = {
            Directions.UP: (-1, 0),
            Directions.DOWN: (1, 0),
            Directions.RIGHT: (0, 1),
            Directions.LEFT: (0, -1),
        }

        visited = set()

        while queue:
            node = heapq.heappop(queue)

            node_y, node_x = node[2]

            if (node_y, node_x) == (target_grid_y, target_grid_x):
                return node[3][::-1]

            g = node[1]

            visited.add((node_y, node_x))

            for direction, coord in directions.items():

                if not self._is_wall(map, node_x, node_y, direction):
                    dy, dx = coord
                    py, px = node_y + dy, node_x + dx

                    if (py, px) in visited:
                        continue

                    f = self._calculate_f(
                        target_grid_x, target_grid_y, px, py, g + 1
                    )
                    heapq.heappush(
                        queue, (f, g + 1, (py, px), node[3] + [(py, px)])
                    )

        return []

    def move_to_start_pos(self, map: List[List[List[int]]]) -> bool:
        if self.path_to_start is None:
            self.path_to_start = self._find_fastest_way_to(
                map, self.starting_x, self.starting_y
            )

            if not self.path_to_start:
                return True

            self.target_y, self.target_x = (
                self.path_to_start[-1][0] * self.cell_size,
                self.path_to_start[-1][1] * self.cell_size,
            )

        if (
            self.pixel_x == self.starting_x * self.cell_size
            and self.pixel_y == self.starting_y * self.cell_size
        ):
            self.path_to_start = None
            return True

        directions = {
            (-1, 0): Directions.UP,
            (1, 0): Directions.DOWN,
            (0, 1): Directions.RIGHT,
            (0, -1): Directions.LEFT,
        }

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            ny, nx = self.path_to_start.pop()
            d = (ny - self.grid_y, nx - self.grid_x)

            self.direction = directions[d]
            self.grid_x = nx
            self.grid_y = ny
            self.target_x = self.grid_x * self.cell_size
            self.target_y = self.grid_y * self.cell_size

        else:
            if self.pixel_x < self.target_x:
                self.pixel_x = min(
                    self.pixel_x + (self.speed * 2), self.target_x
                )
            elif self.pixel_x > self.target_x:
                self.pixel_x = max(
                    self.pixel_x - (self.speed * 2), self.target_x
                )
            elif self.pixel_y < self.target_y:
                self.pixel_y = min(
                    self.pixel_y + (self.speed * 2), self.target_y
                )
            elif self.pixel_y > self.target_y:
                self.pixel_y = max(
                    self.pixel_y - (self.speed * 2), self.target_y
                )
        return False

    def move_random(self, map: List[List[List[int]]]) -> None:
        if self.speed == 0:
            return

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

            directions = list(Directions)
            if self.direction == Directions.UP:
                directions.remove(Directions.DOWN)
            elif self.direction == Directions.DOWN:
                directions.remove(Directions.UP)
            elif self.direction == Directions.RIGHT:
                directions.remove(Directions.LEFT)
            else:
                directions.remove(Directions.RIGHT)

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
                    self.target_x = self.grid_x * self.cell_size
                    self.target_y = self.grid_y * self.cell_size
                    break

            if not self.moving:
                next_x, next_y = 0, 0

                if self.direction == Directions.UP:
                    direction = Directions.DOWN
                    next_y = 1
                elif self.direction == Directions.DOWN:
                    direction = Directions.UP
                    next_y = -1
                elif self.direction == Directions.RIGHT:
                    direction = Directions.LEFT
                    next_x = -1
                else:
                    direction = Directions.RIGHT
                    next_x = 1

                next_gx, next_gy = self.grid_x + next_x, self.grid_y + next_y
                self.moving = True
                self.grid_x = next_gx
                self.grid_y = next_gy
                self.next_direction = None
                self.direction = direction
                self.target_x = self.grid_x * self.cell_size
                self.target_y = self.grid_y * self.cell_size

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

    def draw_on_surface(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        playing_state: PlayingState,
    ) -> None:

        directions_str = ["up", "down", "right", "left"]

        if self.mode == Mode.EAT:
            if isinstance(self.direction, Directions):
                current_img = self.eaten_img[
                    "eaten_" + directions_str[self.direction.value - 1]
                ]
            else:
                current_img = self.eaten_img["eaten_up"]
        else:
            if self.mode == Mode.SCARED:
                if (
                    self.direction == Directions.UP
                    or self.direction == Directions.DOWN
                ):
                    i = (self.pixel_y // 6) % 2
                else:
                    i = (self.pixel_x // 6) % 2

                current_img = self.scared_img[i]
            else:
                if playing_state == PlayingState.POWER:
                    self.j += 1
                    if (self.j // 8) % 2:
                        return

                if self.direction is None:
                    current_img = (
                        self.img[self.name + "_right"]
                        if self.grid_x == 0
                        else self.img[self.name + "_left"]
                    )
                else:
                    current_img = self.img[
                        self.name
                        + "_"
                        + directions_str[self.direction.value - 1]
                    ]

        px = (
            offset_x
            + self.pixel_x
            + ((self.cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((self.cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))

    def move(
        self, map: List[List[List[int]]], pac_grid_x: int, pac_grid_y: int
    ) -> None:
        pass


class Blinky(Ghost):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
        scared_img: List[pygame.Surface],
        eaten_img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(
            name, grid_x, grid_y, speed, cell_size, img, scared_img, eaten_img
        )
        self.path_to_pac_man: List[Tuple[int, int]] | None = None

    def move(
        self, map: List[List[List[int]]], pac_grid_x: int, pac_grid_y: int
    ) -> None:
        if self.path_to_pac_man is None:
            self.path_to_pac_man = self._find_fastest_way_to(
                map, pac_grid_x, pac_grid_y
            )

            if not self.path_to_pac_man:
                return

            y, x = self.path_to_pac_man[-1][0], self.path_to_pac_man[-1][1]

            self.target_y, self.target_x = (
                y * self.cell_size,
                x * self.cell_size,
            )

            directions = {
                (-1, 0): Directions.UP,
                (1, 0): Directions.DOWN,
                (0, 1): Directions.RIGHT,
                (0, -1): Directions.LEFT,
            }

            dy, dx = y - self.grid_y, x - self.grid_x
            self.direction = directions[(dy, dx)]

        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.path_to_pac_man = None
            self.grid_x = int(self.target_x // self.cell_size)
            self.grid_y = int(self.target_y // self.cell_size)
            return

        if self.pixel_x < self.target_x:
            self.pixel_x = min(self.pixel_x + self.speed, self.target_x)
        elif self.pixel_x > self.target_x:
            self.pixel_x = max(self.pixel_x - self.speed, self.target_x)
        elif self.pixel_y < self.target_y:
            self.pixel_y = min(self.pixel_y + self.speed, self.target_y)
        elif self.pixel_y > self.target_y:
            self.pixel_y = max(self.pixel_y - self.speed, self.target_y)


class Clyde(Ghost):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
        scared_img: List[pygame.Surface],
        eaten_img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(
            name, grid_x, grid_y, speed, cell_size, img, scared_img, eaten_img
        )

    def move(
        self, map: List[List[List[int]]], pac_grid_x: int, pac_grid_y: int
    ) -> None:
        pass


class Inky(Ghost):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
        scared_img: List[pygame.Surface],
        eaten_img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(
            name, grid_x, grid_y, speed, cell_size, img, scared_img, eaten_img
        )

    def move(
        self, map: List[List[List[int]]], pac_grid_x: int, pac_grid_y: int
    ) -> None:
        pass


class Pinky(Ghost):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
        scared_img: List[pygame.Surface],
        eaten_img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(
            name, grid_x, grid_y, speed, cell_size, img, scared_img, eaten_img
        )

    def move(
        self, map: List[List[List[int]]], pac_grid_x: int, pac_grid_y: int
    ) -> None:
        pass


class PacMan(Entity):
    def __init__(
        self,
        name: str,
        grid_x: int,
        grid_y: int,
        speed: int,
        cell_size: int,
        img: Dict[str, pygame.Surface],
    ) -> None:
        super().__init__(name, grid_x, grid_y, speed, cell_size, img)
        self.dying_time: int = 0

        self.rotation = {
            Directions.UP: 90,
            Directions.DOWN: -90,
            Directions.RIGHT: 0,
            Directions.LEFT: 180,
        }

    def set_direction(self, direction: Directions) -> None:
        self.next_direction = direction

    def reset_pos(self) -> None:
        self.grid_x = self.starting_x
        self.grid_y = self.starting_y

        self.pixel_x = self.grid_x * self.cell_size
        self.pixel_y = self.grid_y * self.cell_size

        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.direction = None

    def move(self, map: List[List[List[int]]]) -> None:
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
                    self.target_x = self.grid_x * self.cell_size
                    self.target_y = self.grid_y * self.cell_size
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

    def draw_on_surface(
        self,
        surface: pygame.Surface,
        offset_x: int,
        offset_y: int,
        playing_state: PlayingState,
    ) -> None:

        current_img: pygame.Surface | pygame.surface.Surface = self.img[
            "pac_2"
        ]

        if self.mode == Mode.INVINCIBLE:
            self.j += 1

            if (self.j // 8) % 2:
                return

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
            else:
                i = 0

            current_img = self.img["pac_" + str(i + 1)]

        if self.direction:
            current_img = pygame.transform.rotate(
                current_img, self.rotation[self.direction]
            )

        px = (
            offset_x
            + self.pixel_x
            + ((self.cell_size - current_img.get_width()) // 2)
        )
        py = (
            offset_y
            + self.pixel_y
            + ((self.cell_size - current_img.get_height()) // 2)
        )

        surface.blit(current_img, (px, py))
