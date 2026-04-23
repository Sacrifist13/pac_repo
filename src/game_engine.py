import os
import sys
import pygame
from pygame.event import Event
from typing import List, Dict, Any, Tuple
from .loader import Loader
from .assets_manager import AssetsManager
from .highscores import HighScoreManager
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
        """
        Initializes the GameEngine instance.

        This method configures the initial game state, instantiates
        external managers (map and assets), and prepares all tracking
        variables required for the gameplay loop (score, timers, interface,
        animations, and user input).

        Attributes:
            map_generator (MapGenerator): Instance responsible for map
                creation and generation.
            assets_manager (AssetsManager): Manager for graphic and audio
                resources.
            playing_state (PlayingState): Current gameplay state
                (initialized to RETREATE).
            death_time (int): Timestamp (in milliseconds) of Pac-Man's
                death.
            power_time (int): Timestamp (in milliseconds) of consuming a
                super pac-gum.
            time_score_eating (int): Timestamp for the temporary display of
                a consumed ghost's score.
            score_eating_coord (Tuple[int, int]): (y, x) coordinates for
                rendering the consumed ghost's score.
            score_eating (int): Point value of the last consumed ghost.
            current_level (int): The player's current level (starts at 1).
            score (int): Total score accumulated by the player.
            lives (int): Number of remaining lives for the player.
            ghosts_eat (int): Counter for consecutively eaten ghosts while
                powered up.
            pause_info (Dict[Any, Any]): Dictionary storing states (time,
                speeds) during gameplay pause.
            level_pass_animation (bool): Flag indicating if the level
                transition animation is currently active.
            level_pass_animation_time (int): Timestamp for the trigger of
                the level completion animation.
            home_page_sound_play (bool): Flag preventing the home screen
                music from continuously looping.
            in_typing (bool): Flag indicating whether the user currently
                has focus on the text input area.
            pseudo (str): Username entered by the player for high score
                recording.
            pseudo_valid (bool): Validation flag confirming if the username
                meets input criteria.
            input_cursor_i (int): Counter utilized to animate the blinking
                text input cursor.
            speed_cheat (bool): Activation flag for the cheat code that
                increases Pac-Man's movement speed.
            freeze_cheat (bool): Activation flag for the cheat code that
                immobilizes all ghosts.
            enter_pressed (bool): Flag indicating if the 'Enter' key was
                triggered during text input.
            input_done (bool): Flag confirming that the username input
                process is complete and saved.
        """
        self.map_generator = MapGenerator()
        self.assets_manager = AssetsManager()
        self.playing_state = PlayingState.RETREATE
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
        self.level_pass_animation = False
        self.level_pass_animation_time: int = 0
        self.home_page_sound_play: bool = False
        self.in_typing: bool = False
        self.pseudo = ""
        self.pseudo_valid: bool = False
        self.input_cursor_i: int = 0
        self.speed_cheat: bool = False
        self.freeze_cheat: bool = False
        self.enter_pressed: bool = False
        self.input_done: bool = False

    def _get_scale(self) -> Any:
        """
        Calculates screen scaling, centering offsets, and virtual mouse coords.

        This method scales the internal virtual screen to fit the physical
        display window while maintaining its aspect ratio. It calculates the
        necessary offsets to center the game view and translates the current
        raw mouse positions into the virtual coordinate system.

        Returns:
            tuple: A 6-element tuple containing the following values:
                - new_w (int): Scaled width of the virtual screen.
                - new_h (int): Scaled height of the virtual screen.
                - offset_x (int): Horizontal padding to center the screen.
                - offset_y (int): Vertical padding to center the screen.
                - virtual_mouse_x (float): Mouse X in virtual coordinates.
                - virtual_mouse_y (float): Mouse Y in virtual coordinates.
        """
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
        """
        Calculates and returns a centered collision bounding box.

        This method generates a smaller, centered hitbox relative to the
        entity's full cell size. This prevents frustrating collisions by
        giving the player a slight margin of error when turning corners or
        passing close to objects.

        Args:
            pixel_x (int): The top-left X coordinate of the entity's cell.
            pixel_y (int): The top-left Y coordinate of the entity's cell.
            cell_size (int): The width and height of the grid cell.
            ratio (float, optional): The size ratio of the hitbox relative
                to the cell size. Defaults to 0.5.

        Returns:
            pygame.Rect: A rectangle representing the centered hitbox for
                collision detection.
        """
        hitbox_size = int(cell_size * ratio)
        offset = (cell_size - hitbox_size) // 2
        return pygame.Rect(
            pixel_x + offset, pixel_y + offset, hitbox_size, hitbox_size
        )

    def _is_hover(
        self,
        mouse_x: int,
        mouse_y: int,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
    ) -> bool:
        """
        Determines if the mouse cursor is hovering over a rectangular area.

        This method checks if the provided mouse coordinates fall within the
        boundaries of a defined rectangle. It is commonly used for detecting
        user interactions with UI elements like buttons or menu options.

        Args:
            mouse_x (int): The current X coordinate of the mouse cursor.
            mouse_y (int): The current Y coordinate of the mouse cursor.
            x_min (int): The left boundary (minimum X) of the target area.
            x_max (int): The right boundary (maximum X) of the target area.
            y_min (int): The top boundary (minimum Y) of the target area.
            y_max (int): The bottom boundary (maximum Y) of the target area.

        Returns:
            bool: True if the mouse coordinates are inside the boundaries,
                False otherwise.
        """
        if x_min <= mouse_x <= x_max and y_min <= mouse_y <= y_max:
            return True
        return False

    def _init_game(self) -> None:
        """
        Initializes the core game components and user interface elements.

        This method sets the initial game state to the main menu, loads
        configuration settings via the Loader, and initializes the assets
        manager. It also constructs the primary interface dictionary, which
        stores animation counters, character sprites (Pac-Man and ghosts),
        and bounding box coordinates for menu text interactions.
        """
        self.state = GameState.MENU

        loader = Loader()
        self.config = loader.load_config(sys.argv)

        self.assets_manager.init_game()

        self.interface: Dict[Any, Any] = {
            "counter": 0,
            "anim_counter": 0,
            "pos_x": 0,
            1: {
                "ghosts": [
                    self.assets_manager.img["blinky_right"],
                    self.assets_manager.img["clyde_right"],
                    self.assets_manager.img["inky_right"],
                    self.assets_manager.img["pinky_right"],
                ],
                "pac_man": [
                    pac_img
                    for key, pac_img in self.assets_manager.img.items()
                    if key.startswith("pac_")
                    if "gum" not in key
                ],
            },
            2: {
                "pac_man": [
                    pac_img
                    for key, pac_img in self.assets_manager.img.items()
                    if "pac_" in key
                ],
                "scared": [
                    self.assets_manager.img["scared_basic"],
                    self.assets_manager.img["scared_white"],
                ],
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

    def _load_map_elements(
        self, logo: List[Tuple[int, int]], margin: int = 80
    ) -> None:
        """
        Loads map elements, initializes entities, and draws static walls.

        This method prepares the visual and logical foundation of the level.
        It calculates the optimal cell size to fit the screen, initializes
        Pac-Man and the ghosts at their starting positions, and iterates
        through the map grid to draw the maze walls using bitwise flags.
        It also generates the coordinates for standard and super pac-gums.

        Args:
            logo (List[Tuple[int, int]]): A list of (x, y) grid coordinates
                representing the central logo or restricted spawn area.
            margin (int, optional): The pixel margin around the outer edge
                of the game map. Defaults to 80.
        """
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

        self.assets_manager.load_game_img(cell_size)

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
            Blinky: ("blinky", 0, map_cols - 1),
            Clyde: ("clyde", 0, 0),
            Inky: ("inky", map_rows - 1, 0),
            Pinky: ("pinky", map_rows - 1, map_cols - 1),
        }

        self.pac_man = PacMan(
            "Pac-man",
            mid_x,
            mid_y,
            0,
            cell_size,
            self.assets_manager.game_img["pac_man"],
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
                self.assets_manager.game_img[name],
                self.assets_manager.game_img["scared"],
                self.assets_manager.game_img["eaten"],
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
        """
        Generates and loads the game map for the current level.

        This method checks if the current level exceeds the maximum limit
        (level 10). If within limits, it generates a new map layout, loads
        its visual and logical elements, and initializes the pre-level
        countdown timer.

        Returns:
            bool: True if the map was successfully generated, or False if
                the player has passed the final level (level > 10).
        """
        if self.current_level > 10:
            return False

        map, logo = self.map_generator.create_map(self.current_level)
        self.map = map
        self._load_map_elements(logo)
        self.countdown_start_time = pygame.time.get_ticks()
        self.countdown_duration = 5000

        return True

    def _draw_time_left(self) -> bool:
        """
        Calculates and renders the remaining time for the current level.

        This method computes the time left by comparing the current elapsed
        time against the level's starting time and maximum allowed duration.
        If time runs out, it signals the end of the game or level. Otherwise,
        it renders the remaining seconds at the bottom center of the screen.

        Returns:
            bool: True if there is time remaining and the text was successfully
                rendered, or False if the countdown has reached zero.
        """
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

        time_left_text = self.assets_manager.f_basic.render(
            str(time_left_s), True, self.NEON_PINK
        )

        time_left_w, time_left_h = time_left_text.get_size()
        time_x, time_y = (
            self.WIDTH - time_left_w
        ) // 2, self.HEIGHT - time_left_h - 20

        self.virtual_screen.blit(time_left_text, (time_x, time_y))

        return True

    def _draw_pac_gums(self) -> None:
        """
        Renders all regular and super pac-gums on the virtual screen.

        This method calculates the exact pixel coordinates for each pac-gum
        and super pac-gum based on their grid positions. It ensures they
        are properly centered within their respective cells, applies the
        current game offsets, and draws the corresponding asset images to
        the surface. It also updates the internal counts for both types.
        """
        c_size = self.pac_man.cell_size

        pac_gum_w, pac_gum_h = self.assets_manager.game_img[
            "pac_gum"
        ].get_size()
        super_pac_gum_w, super_pac_gum_h = self.assets_manager.game_img[
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

            self.virtual_screen.blit(
                self.assets_manager.game_img["super_pac_gum"], (px, py)
            )

        self.nb_pac_gums = len(self.pac_gums_coord)
        self.super_pac_gums = len(self.super_pac_gums_coord)

        for y, x in self.pac_gums_coord:

            px = self.game_offset_x + x * c_size + ((c_size - pac_gum_w) // 2)
            py = self.game_offset_y + y * c_size + ((c_size - pac_gum_h) // 2)

            self.virtual_screen.blit(
                self.assets_manager.game_img["pac_gum"], (px, py)
            )

    def _draw_game_status(self) -> None:
        """
        Renders the top HUD displaying the level, score, and lives.

        This method draws the current level text centered at the top, the
        player's current score on the left, and graphical icons representing
        remaining lives on the right. Lost lives are visually indicated by
        rendering a semi-transparent dark overlay over the life icons.
        """
        level_text_1 = self.assets_manager.f_back.render(
            "Level " + str(self.current_level), True, self.NEON_BLUE
        )
        level_text_2 = self.assets_manager.f_front.render(
            "Level " + str(self.current_level), True, self.PACMAN_YELLOW
        )

        level_text_w, level_text_h = level_text_1.get_size()
        level_text_x = (self.WIDTH - level_text_w) // 2
        level_text_y = (80 - level_text_h) // 2

        self.virtual_screen.blit(level_text_1, (level_text_x, level_text_y))
        self.virtual_screen.blit(level_text_2, (level_text_x, level_text_y))

        score_text_1 = self.assets_manager.f_basic.render(
            "Score ", True, self.GRAY
        )
        score_text_2 = self.assets_manager.f_basic.render(
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

        pac_img_life = pygame.transform.scale(
            self.assets_manager.img["pac_2"], (20, 20)
        )
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
        """
        Draws all dynamic game entities onto the virtual screen.

        This method iterates through the game's dynamic characters (Pac-Man
        and the ghosts) and triggers their internal rendering methods based
        on the current playing state. Pac-Man is hidden during his death
        animation, and ghosts are hidden during the level transition phase.
        """
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
        """
        Updates the positions and states of all dynamic game entities.

        This method dictates the movement logic for Pac-Man and the ghosts
        per frame. Pac-Man moves based on current directional inputs. Ghost
        behaviors are determined by the global playing state (e.g., POWER)
        and their individual current modes (NORMAL, SCARED, EAT).

        During normal play, Blinky actively targets Pac-Man (unless Pac-Man
        is invincible), while others currently move randomly. If a ghost is
        eaten, it navigates back to its starting position to respawn and
        resume its normal hunting state, adjusting speed accordingly.
        """
        self.pac_man.move(self.map)

        if self.playing_state == PlayingState.LEVEL_PASS:
            return

        blinky = self.ghosts.get("blinky")
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
                    elif (
                        ghost.name == "inky"
                        and self.pac_man.mode != Mode.INVINCIBLE
                    ):
                        if blinky:
                            ghost.move(
                                self.map,
                                self.pac_man.direction,
                                self.pac_man.grid_x,
                                self.pac_man.grid_y,
                                blinky.grid_x,
                                blinky.grid_y,
                            )
                    elif (
                        ghost.name == "clyde"
                        and self.pac_man.mode != Mode.INVINCIBLE
                    ):
                        ghost.move(
                            self.map, self.pac_man.grid_x, self.pac_man.grid_y
                        )
                    elif (
                        ghost.name == "pinky"
                        and self.pac_man.mode != Mode.INVINCIBLE
                    ):
                        ghost.move(
                            self.map,
                            self.pac_man.direction,
                            self.pac_man.grid_x,
                            self.pac_man.grid_y,
                        )
                    # Rajouter un if pac_man.mode == Mode.INVINCIBLE
                elif ghost.mode == Mode.EAT:
                    if ghost.move_to_start_pos(self.map):
                        ghost.mode = Mode.NORMAL
                        if not self.freeze_cheat:
                            ghost.speed = 2
                        else:
                            ghost.speed = 0

    def _eat_pac_gums(self) -> bool:
        """
        Checks for and processes the consumption of a standard pac-gum.

        This method calculates Pac-Man's center point in pixel
        coordinates and converts it to map grid coordinates. If a standard
        pac-gum exists at this specific grid location, it is removed from
        the active pac-gums list, indicating it has been eaten.

        Returns:
            bool: True if a pac-gum was successfully eaten during this
                frame, False otherwise.
        """
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
        """
        Checks for and processes the consumption of a super pac-gum.

        This method calculates Pac-Man's center point in pixel
        coordinates and converts it to map grid coordinates. If a super
        pac-gum exists at this specific grid location, it is removed from
        the active super pac-gums list, indicating it has been eaten and
        should trigger the game's power-up state.

        Returns:
            bool: True if a super pac-gum was successfully eaten during
                this frame, False otherwise.
        """
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
        """
        Renders the floating score text after a ghost is consumed.

        This method displays the point value of a recently eaten ghost
        at the exact coordinates where the ghost was caught. The text
        remains temporarily visible on the screen for exactly one second
        (1000 milliseconds) after the event before disappearing.
        """
        current_time = pygame.time.get_ticks()

        if current_time < self.time_score_eating + 1000:
            y, x = self.score_eating_coord

            points_str = self.assets_manager.f_basic.render(
                str(self.score_eating), True, self.NEON_PINK
            )
            points_h = points_str.get_height()
            points_x, points_y = (
                self.game_offset_x + x,
                (self.game_offset_y + y) + points_h // 2,
            )
            self.virtual_screen.blit(points_str, (points_x, points_y))

    def _is_pac_man_catch(self) -> None:
        """
        Evaluates collisions between Pac-Man and ghosts to update game states.

        This method retrieves the hitboxes for Pac-Man and all active ghosts,
        checking for any intersections. If a collision occurs, the outcome
        depends on the ghost's current mode. If the ghost is in a normal
        hunting state and Pac-Man is vulnerable, it triggers Pac-Man's death
        sequence. If the ghost is scared, it is eaten, awarding escalating
        points to the player and sending the ghost back to spawn.
        """
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
                    self.assets_manager.play_sound(
                        None,
                        self.assets_manager.sound["eat_ghost"],
                        False,
                        0.5,
                    )
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
        """
        Saves the current game state and freezes entities during a pause.

        This method calculates and stores the remaining level time, as well
        as the elapsed time for active temporary states like Pac-Man's
        invincibility or a power-up phase. It records the current speed
        of all ghosts before setting their speeds (and Pac-Man's) to zero,
        effectively halting all on-screen movement.
        """
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
        """
        Renders the visual countdown sequence before a level begins.

        This method applies a semi-transparent dark overlay to the screen
        and displays the initial maximum level time. It calculates the
        elapsed time since the countdown started and displays a descending
        timer (3, 2, 1) followed by "GO" in the center of the screen,
        indicating that gameplay is about to commence.
        """
        blur_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        blur_surface.fill((0, 0, 0, 160))

        time_left_text = self.assets_manager.f_basic.render(
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

        text_1 = self.assets_manager.f_back_countdown.render(
            text, True, self.GRAY
        )
        text_2 = self.assets_manager.f_front_countdown.render(
            text, True, self.NEON_BLUE
        )

        text_x = (self.WIDTH - text_1.get_width()) // 2
        text_y = (self.HEIGHT - text_1.get_height()) // 2

        self.virtual_screen.blit(text_1, (text_x, text_y))
        self.virtual_screen.blit(text_2, (text_x, text_y))

    def _render_paused_game(self, mouse_x: int, mouse_y: int) -> None:
        """
        Renders the pause menu overlay and handles its hover interactions.

        This method applies a dark, semi-transparent blur over the active
        gameplay to indicate the paused state. It draws a central modal
        window displaying the remaining level time, current score, a toggle
        for audio volume, and interactive buttons to either "RESUME" the
        game or "EXIT" back to the main menu. It also updates the interface
        dictionary with hitbox coordinates for these clickable elements.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
        blur_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA
        )
        blur_surface.fill((0, 0, 0, 160))

        time_left = self.pause_info["time_left"]

        time_left_text = self.assets_manager.f_basic.render(
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
        x_max, y_max = x + width, y + height

        if self._is_hover(mouse_x, mouse_y, x, x_max, y, y_max):
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, width + 2, height + 2),
            2,
        )

        text_1 = self.assets_manager.f_back.render("PAUSE", True, self.GRAY)
        text_2 = self.assets_manager.f_front.render("PAUSE", True, color)

        text_x = (width - text_1.get_width()) // 2

        paused_surface.blit(text_1, (text_x, 2))
        paused_surface.blit(text_2, (text_x, 2))

        exit_text_1 = self.assets_manager.f_back_over.render(
            "EXIT", True, self.GRAY
        )

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
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["munch_2"], False, 0.5
                )
                self.interface["Exit_paused"][2] = True
        else:
            self.interface["Exit_paused"][2] = False

        exit_text_2 = self.assets_manager.f_front_over.render(
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
            pygame.transform.scale(
                self.assets_manager.img["volume_up"], (40, 40)
            )
            if self.assets_manager.music_on
            else pygame.transform.scale(
                self.assets_manager.img["volume_off"], (40, 40)
            )
        )

        volume_w, volume_h = volume_img.get_size()
        volume_x, volume_y = (
            width - volume_w
        ) // 2, text_1.get_height() + volume_h - 20

        paused_surface.blit(volume_img, (volume_x, volume_y))

        x_min, x_max = x + volume_x, x + volume_x + volume_w
        y_min, y_max = y + volume_y, y + volume_y + volume_h

        self.interface["volume"] = ((x_min, x_max), (y_min, y_max))

        hover_music_color = (
            self.NEON_GREEN if self.assets_manager.music_on else self.NEON_RED
        )

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            pygame.draw.rect(
                paused_surface,
                hover_music_color,
                pygame.Rect(
                    volume_x - 1, volume_y - 1, volume_w + 2, volume_h + 2
                ),
                1,
            )

        score_text_1 = self.assets_manager.f_basic.render(
            "Score ", True, self.GRAY
        )
        score_text_2 = self.assets_manager.f_basic.render(
            str(self.score), True, color
        )

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

        resume_text = self.assets_manager.f_basic.render(
            "RESUME", True, self.NEON_PURPLE
        )
        resume_w, resume_h = resume_text.get_size()

        resume_x, resume_y = (
            width - resume_w
        ) // 2, score_text_y + score_text_h + resume_h + 40

        x_min, x_max = x + resume_x, x + resume_x + resume_w
        y_min, y_max = y + resume_y, y + resume_y + resume_h

        self.interface["resume_paused"] = ((x_min, x_max), (y_min, y_max))

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            resume_text = self.assets_manager.f_basic.render(
                "RESUME", True, self.NEON_PINK
            )

        paused_surface.blit(resume_text, (resume_x, resume_y))

        self.virtual_screen.blit(paused_surface, (x, y))

    def _depause_game(self) -> None:
        """
        Restores the game state and entity movements after a pause.

        This method recalculates critical timestamps (level duration,
        power-up time, and invincibility duration) to account for the time
        spent in the pause menu. It also restores the movement speeds of
        all ghosts and Pac-Man, applying any active cheat codes, and
        resumes background music if a specific state requires it.
        """
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
                self.assets_manager.play_sound(
                    "assets/media/power_pellet.wav", None, True, 0.5
                )
                self.music_load = True

    def _render_pac_man_dying(self) -> bool:
        """
        Renders the death animation and manages the respawn sequence.

        This method calculates the current frame of the 12-frame death
        animation based on the elapsed time since Pac-Man was caught. It
        draws the appropriately scaled frame to the screen. Once the 1200ms
        animation finishes, it resets Pac-Man's position and normal speed.

        Returns:
            bool: True if the animation has completed and Pac-Man is ready
                to respawn, False if the animation is still ongoing.
        """
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
            self.assets_manager.img[str(frame_index + 1)],
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
        """
        Renders and manages the username input field.

        This method draws the text input window allowing the player to
        enter their name after a game ends. It handles cursor animation,
        validates the input (preventing empty submissions), displays
        warning or success messages, and triggers the high score save
        process via HighScoreManager when Enter is pressed. It also
        updates the interface dictionary with the window's hitbox.

        Args:
            surface (pygame.Surface): The surface to draw the window on.
            surface_pos_x (int): The absolute X position of the surface.
            surface_pos_y (int): The absolute Y position of the surface.
            input_window_y (int): The relative Y position of the text box.
        """
        w, h = surface.get_size()

        if self.input_done:
            save_text = self.assets_manager.f_basic.render(
                "Input save successfully !", True, self.NEON_GREEN
            )
            text_w, text_h = save_text.get_size()
            text_x, text_y = (w - text_w) // 2, (h - text_h) // 2

            surface.blit(save_text, (text_x, text_y + 20))

            return

        basic_text = self.assets_manager.f_basic.render(
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

            text = self.assets_manager.f_basic.render(
                input_txt, True, self.BLACK
            )
            input_window.blit(text, (4, 8))
            color = self.NEON_PINK

            if len(self.pseudo) >= 1:

                if not self.pseudo_valid:
                    self.enter_pressed = False

                self.pseudo_valid = True
                inst_text = self.assets_manager.f_basic_s.render(
                    "Press enter to valid", True, self.NEON_PINK
                )
                inst_text_w = inst_text.get_width()

                inst_text_x, inst_text_y = (
                    input_window_x + (input_window_w - inst_text_w) // 2,
                    input_window_y + input_window_h + 10,
                )
                surface.blit(inst_text, (inst_text_x, inst_text_y))

                if self.enter_pressed:
                    HighScoreManager.update_highscores_file(
                        file=self.config.highscore_filename,
                        name=self.pseudo,
                        score=self.score,
                    )
                    self.input_done = True

            else:
                if self.enter_pressed:
                    warning_message = self.assets_manager.f_basic_s.render(
                        "Username cannot be empty.", True, self.NEON_RED
                    )
                    warning_message_w, warning_message_h = (
                        warning_message.get_size()
                    )
                    warning_message_x, warning_message_y = (
                        input_window_x
                        + (input_window_w - warning_message_w) // 2,
                        input_window_y - warning_message_h - 10,
                    )
                    surface.blit(
                        warning_message, (warning_message_x, warning_message_y)
                    )
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
        """
        Renders the game over screen and manages end-game UI components.

        This method applies a dark, semi-transparent blur over the gameplay
        area and displays a modal window. It presents the "GAME OVER"
        announcement, the final score, and an interactive "BACK" button
        that responds to mouse hover. It also integrates the user input
        field for high score recording by calling the specialized
        _render_input_user method.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
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

        x_max, y_max = x + w, y + h

        if self._is_hover(mouse_x, mouse_y, x, x_max, y, y_max):
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, w + 2, h + 2),
            2,
        )
        text_1 = self.assets_manager.f_back.render(
            "GAME OVER", True, self.GRAY
        )
        text_2 = self.assets_manager.f_front.render("GAME OVER", True, color)

        text_x = (w - text_1.get_width()) // 2
        text_h = text_1.get_height()

        pop_up_surface.blit(text_1, (text_x, 2))
        pop_up_surface.blit(text_2, (text_x, 2))

        back_text_1 = self.assets_manager.f_back_over.render(
            "BACK", True, self.GRAY
        )

        back_text_w, back_text_h = back_text_1.get_size()

        back_text_x = (w - back_text_w) // 2
        back_text_y = h - back_text_h - 4

        back_text_front_color = self.NEON_PURPLE

        x_min, x_max = x + back_text_x, x + back_text_x + back_text_w
        y_min, y_max = y + back_text_y, y + back_text_y + back_text_h

        self.interface["Back_game_over"][0] = (x_min, x_max)
        self.interface["Back_game_over"][1] = (y_min, y_max)

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            back_text_front_color = self.NEON_PINK
            if not self.interface["Back_game_over"][2]:
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["munch_2"], False, 0.5
                )
                self.interface["Back_game_over"][2] = True
        else:
            self.interface["Back_game_over"][2] = False

        back_text_2 = self.assets_manager.f_front_over.render(
            "BACK", True, back_text_front_color
        )

        pop_up_surface.blit(back_text_1, (back_text_x, back_text_y))
        pop_up_surface.blit(back_text_2, (back_text_x, back_text_y))

        score_text_1 = self.assets_manager.f_basic.render(
            "Score ", True, self.GRAY
        )
        score_text_2 = self.assets_manager.f_basic.render(
            str(self.score), True, color
        )

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
        """
        Handles the transition logic and animation when a level is cleared.

        This method manages two phases of level completion. First, it renders
        a collectible "key" at Pac-Man's starting position; if Pac-Man
        collides with this key, the exit animation is triggered. Second, it
        renders a scaling black rectangle animation that grows to cover the
        screen. Once the animation timer expires, it either advances the
        game to the next level's starting state or triggers the final win
        state if the maximum level (10) has been reached.
        """
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

            key_w, key_h = self.assets_manager.game_img["key"].get_size()
            key_x, key_y = self.game_offset_x + key_pixel_x + (
                cell_size - key_w
            ) // 2, (
                self.game_offset_y + key_pixel_y + (cell_size - key_h) // 2
            )

            self.virtual_screen.blit(
                self.assets_manager.game_img["key"], (key_x, key_y)
            )

            key_hitbox = self._get_hitbox(key_pixel_x, key_pixel_y, cell_size)
            pac_man_hitbox = self._get_hitbox(
                self.pac_man.pixel_x, self.pac_man.pixel_y, cell_size
            )

            if pac_man_hitbox.colliderect(key_hitbox):
                self.level_pass_animation = True
                self.level_pass_animation_time = pygame.time.get_ticks()

    def _render_game(self, mouse_x: int, mouse_y: int) -> None:
        """
        Orchestrates the main game rendering loop and state management.

        This method serves as the central hub for the game's visual output.
        It first clears the screen by blitting the map surface, then draws
        the UI status and static items. Depending on the current GameState
        (STARTING, PLAYING, PAUSED, or GAME_OVER), it triggers specific
        rendering logic, manages entity movement, processes collision
        events (eating gums or being caught), handles timers, and plays
        the appropriate sound effects for each game phase.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
        self.virtual_screen.blit(self.map_surface, (0, 0))
        self._draw_game_status()
        self._draw_pac_gums()
        self._draw_entities()

        current_time = pygame.time.get_ticks()

        if self.state == GameState.STARTING_LEVEL:
            pygame.mixer.music.stop()
            if not self.countdown_play:
                self.countdown_play = True
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["start"], False, 0.2
                )
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

            if not self.freeze_cheat:
                if not self._draw_time_left():
                    self.state = GameState.GAME_OVER
                    pygame.mixer.music.stop()
                    self.music_load = False
                    return
            else:
                time_left = self.pause_info["time_left"]

                time_left_text = self.assets_manager.f_basic.render(
                    str(time_left), True, self.NEON_PINK
                )

                time_left_w, time_left_h = time_left_text.get_size()
                time_x, time_y = (
                    self.WIDTH - time_left_w
                ) // 2, self.HEIGHT - time_left_h - 20

                self.virtual_screen.blit(time_left_text, (time_x, time_y))

            if self.playing_state == PlayingState.DEATH:
                if not self.music_load:
                    pygame.mixer.music.stop()
                    self.assets_manager.play_sound(
                        None,
                        self.assets_manager.sound["pacman_death"],
                        False,
                        0.5,
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
                    self.assets_manager.play_sound(
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
                    self.assets_manager.play_sound(
                        None, self.assets_manager.sound["munch_1"], False, 0.5
                    )
                else:
                    self.assets_manager.play_sound(
                        None, self.assets_manager.sound["munch_2"], False, 0.5
                    )

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
        """
        Renders the victory screen when the player completes the game.

        This method displays a celebratory modal window upon game completion.
        It renders the "YOU WIN" announcement, displays the player's final
        score, and provides an interactive "BACK" button to return to the
        main menu. Similar to the game over screen, it also includes the
        username input field via _render_input_user to allow the player to
        save their winning score to the high scores list.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
        pop_up_surface = pygame.Surface(
            (int(self.WIDTH / 1.5), self.HEIGHT // 3), pygame.SRCALPHA
        )

        w, h = pop_up_surface.get_size()

        x, y = (self.WIDTH - w) // 2, (self.HEIGHT - h) // 2

        pop_up_surface.fill(self.BLACK)

        color = self.NEON_PURPLE

        x_max, y_max = x + w, y + h

        if self._is_hover(mouse_x, mouse_y, x, x_max, y, y_max):
            color = self.NEON_PINK

        pygame.draw.rect(
            self.virtual_screen,
            color,
            pygame.Rect(x - 1, y - 1, w + 2, h + 2),
            2,
        )
        text_1 = self.assets_manager.f_back.render("YOU WIN", True, self.GRAY)
        text_2 = self.assets_manager.f_front.render("YOU WIN", True, color)

        text_x = (w - text_1.get_width()) // 2
        text_h = text_1.get_height()

        pop_up_surface.blit(text_1, (text_x, 2))
        pop_up_surface.blit(text_2, (text_x, 2))

        back_text_1 = self.assets_manager.f_back_over.render(
            "BACK", True, self.GRAY
        )

        back_text_w, back_text_h = back_text_1.get_size()

        back_text_x = (w - back_text_w) // 2
        back_text_y = h - back_text_h - 4

        back_text_front_color = self.NEON_PURPLE

        x_min, x_max = x + back_text_x, x + back_text_x + back_text_w
        y_min, y_max = y + back_text_y, y + back_text_y + back_text_h

        self.interface["Back_game_over"][0] = (x_min, x_max)
        self.interface["Back_game_over"][1] = (y_min, y_max)

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            back_text_front_color = self.NEON_PINK
            if not self.interface["Back_game_over"][2]:
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["munch_2"], False, 0.5
                )
                self.interface["Back_game_over"][2] = True
        else:
            self.interface["Back_game_over"][2] = False

        back_text_2 = self.assets_manager.f_front_over.render(
            "BACK", True, back_text_front_color
        )

        pop_up_surface.blit(back_text_1, (back_text_x, back_text_y))
        pop_up_surface.blit(back_text_2, (back_text_x, back_text_y))

        score_text_1 = self.assets_manager.f_basic.render(
            "Score ", True, self.GRAY
        )
        score_text_2 = self.assets_manager.f_basic.render(
            str(self.score), True, color
        )

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
        """
        Renders the command instructions section within the info menu.

        This method draws a categorized display of game controls, split
        into "Basic commands" (movement) and "Cheat commands" (gameplay
        modifiers). It handles the visual layout, including background
        rectangles, decorative ghost assets (Blinky and Clyde), and
        dynamic color changes based on mouse hover state. The section is
        centered horizontally and partitioned using a vertical separator.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
            height_available (int): Total vertical space allocated for
                the instructions UI.
        """
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

        self.virtual_screen.blit(
            self.assets_manager.img["blinky_down"], (blinky_x, blinky_y)
        )
        self.virtual_screen.blit(
            self.assets_manager.img["clyde_down"], (clyde_x, clyde_y)
        )

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

        basic_instructions_text_1 = self.assets_manager.f_back_over.render(
            "Basic commands", True, self.GRAY
        )
        basic_instructions_text_2 = self.assets_manager.f_front_over.render(
            "Basic commands", True, color
        )

        cheat_instructions_text_1 = self.assets_manager.f_back_over.render(
            "Cheat commands", True, self.GRAY
        )
        cheat_instructions_text_2 = self.assets_manager.f_front_over.render(
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
            "up": self.assets_manager.f_basic.render("↑  up", True, color),
            "down": self.assets_manager.f_basic.render("↓  down", True, color),
            "left": self.assets_manager.f_basic.render("←  left", True, color),
            "right": self.assets_manager.f_basic.render(
                "→  right", True, color
            ),
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
            "speed": self.assets_manager.f_basic.render(
                "s:  Speed * 2", True, color
            ),
            "freeze": self.assets_manager.f_basic.render(
                "f:  Freeze ghosts", True, color
            ),
            "next": self.assets_manager.f_basic.render(
                "l:  Level skip", True, color
            ),
            "power": self.assets_manager.f_basic.render(
                "p:  Instant power", True, color
            ),
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
        """
        Renders the game rules section within the instructions menu.

        This method displays a comprehensive list of game objectives,
        mechanics, and controls. It draws a stylized text box featuring
        ghost assets (Inky and Pinky) that react to mouse hover. The
        rules text is dynamically generated to include current
        configuration values, such as starting lives and level time
        limits, ensuring the documentation remains accurate to the
        game's settings.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
            height_available (int): The total vertical space allocated for
                the instructions interface.
        """
        width, height = int(self.WIDTH / 1.2), height_available // 2 + 20

        x, y = (self.WIDTH - width) // 2, (
            self.HEIGHT - height_available
        ) // 3 + height - 10

        color = self.NEON_PURPLE

        inky_x, inky_y = x + 40, y - 20
        pinky_x, pinky_y = x + width - 40, y - 20

        x_max, y_max = x + width, y + height

        if self._is_hover(mouse_x, mouse_y, x, x_max, y, y_max):
            color = self.NEON_PINK
            inky_y, pinky_y = y - 25, y - 25

        self.virtual_screen.blit(
            self.assets_manager.img["inky_down"], (inky_x, inky_y)
        )
        self.virtual_screen.blit(
            self.assets_manager.img["pinky_down"], (pinky_x, pinky_y)
        )

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

        title_text_1 = self.assets_manager.f_back_over.render(
            "Rules", True, self.GRAY
        )
        title_text_2 = self.assets_manager.f_front_over.render(
            "Rules", True, color
        )

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

        text_rules = self.assets_manager.f_basic.render(rules, True, color)

        text_rules_w = text_rules.get_width()
        text_rules_x, text_rules_y = (
            x + (width - text_rules_w) // 2,
            y + title_h + 15,
        )

        self.virtual_screen.blit(text_rules, (text_rules_x, text_rules_y))

    def _render_instructions(self, mouse_x: int, mouse_y: int) -> None:
        """
        Renders the main instructions screen and its sub-components.

        This method displays the overall "Instructions" menu, featuring a
        title and a "Back" button to return to the main menu. It manages
        the layout by calculating the available vertical space and
        delegating the rendering of specific sections to _draw_command
        and _draw_rules. It also handles mouse hover states for the navigation
        button and updates its hitbox coordinates in the interface mapping.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
        title_text_1 = self.assets_manager.f_back.render(
            "Instructions", True, self.GRAY
        )
        title_text_2 = self.assets_manager.f_front.render(
            "Instructions", True, self.NEON_PINK
        )

        coord = ((self.WIDTH - title_text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(title_text_1, coord)
        self.virtual_screen.blit(title_text_2, coord)

        back_text_1 = self.assets_manager.f_back_over.render(
            "Back", True, self.GRAY
        )
        back_text_2 = self.assets_manager.f_front_over.render(
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

        x_min, x_max = coord[0], coord[0] + text_width
        y_min, y_max = coord[1], coord[1] + text_height

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            back_text_2 = self.assets_manager.f_front_over.render(
                "Back", True, self.NEON_PINK
            )
            if not self.interface["Back_instructions"][2]:
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["munch_2"], False, 0.5
                )
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

    def _render_highscores(self, mouse_x: int, mouse_y: int) -> None:
        title_text_1 = self.assets_manager.f_back.render(
            "Highscores", True, self.GRAY
        )
        title_text_2 = self.assets_manager.f_front.render(
            "Highscores", True, self.NEON_PINK
        )

        coord = ((self.WIDTH - title_text_1.get_width()) // 2, 20)

        self.virtual_screen.blit(title_text_1, coord)
        self.virtual_screen.blit(title_text_2, coord)

        x_start = self.WIDTH // 2
        y_start = self.WIDTH // 2
        HighScoreManager.display_score(
            self.config.highscore_filename,
            self.virtual_screen,
            x_start,
            y_start,
            self.assets_manager,
        )
        back_text_1 = self.assets_manager.f_back_over.render(
            "Back", True, self.GRAY
        )
        back_text_2 = self.assets_manager.f_front_over.render(
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

        x_min, x_max = coord[0], coord[0] + text_width
        y_min, y_max = coord[1], coord[1] + text_height

        if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
            back_text_2 = self.assets_manager.f_front_over.render(
                "Back", True, self.NEON_PINK
            )
            if not self.interface["Back_highscores"][2]:
                self.assets_manager.play_sound(
                    None, self.assets_manager.sound["munch_2"], False, 0.5
                )
                self.interface["Back_highscores"][2] = True

        else:
            self.interface["Back_highscores"][2] = False

        self.virtual_screen.blit(back_text_1, coord)
        self.virtual_screen.blit(back_text_2, coord)

    def _draw_home_text(self, mouse_x: int, mouse_y: int) -> int:
        """
        Renders the home screen menu options and the game title.

        This method displays the main title image and iterates through the
        available menu text options (e.g., Start, Exit). It handles the
        visual hover effects, updates the interface dictionary with text
        hitboxes for click detection, and triggers sound effects when the
        mouse enters a menu item's area. Additionally, it renders the
        volume toggle icon and its interactive border.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.

        Returns:
            int: The height of the title image, used to calculate offsets
                for other home screen elements.
        """
        title_img = self.assets_manager.img["title"]

        w, h = title_img.get_size()
        x, y = (self.WIDTH - w) // 2, -40

        offset_y = 0

        hover = False

        for key in self.interface["text"].keys():
            coord = (40, h + 120 + offset_y)

            text_1 = self.assets_manager.f_back.render(key, True, self.GRAY)
            text_2 = self.assets_manager.f_front.render(
                key, True, self.PACMAN_YELLOW
            )

            text_width, text_height = (
                text_1.get_width(),
                text_1.get_height(),
            )

            self.interface["text"][key][0], self.interface["text"][key][1] = (
                coord[0],
                coord[0] + text_width,
            ), (coord[1], coord[1] + text_height)

            x_min, x_max = coord[0], coord[0] + text_width
            y_min, y_max = coord[1], coord[1] + text_height

            if self._is_hover(mouse_x, mouse_y, x_min, x_max, y_min, y_max):
                text_1 = self.assets_manager.f_back.render(
                    key, True, self.NEON_BLUE
                )
                if key == "Exit" and not self.interface["text"][key][2]:
                    self.assets_manager.play_sound(
                        None, self.assets_manager.sound["munch_2"], False, 0.5
                    )
                    self.interface["text"][key][2] = True
                else:
                    if not self.interface["text"][key][2]:
                        self.assets_manager.play_sound(
                            None,
                            self.assets_manager.sound["munch_1"],
                            False,
                            0.5,
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
            pygame.transform.scale(
                self.assets_manager.img["volume_up"], (40, 40)
            )
            if self.assets_manager.music_on
            else pygame.transform.scale(
                self.assets_manager.img["volume_off"], (40, 40)
            )
        )

        volume_w, volume_h = volume_img.get_size()

        self.interface["volume_home"] = (
            (40, 40 + volume_w),
            (120 + h + offset_y, 120 + h + offset_y + volume_h),
        )

        self.virtual_screen.blit(volume_img, (40, 120 + h + offset_y))

        hover_music_color = (
            self.NEON_GREEN if self.assets_manager.music_on else self.NEON_RED
        )

        x_max, y_max = 40 + volume_w, 120 + h + offset_y + volume_h

        if self._is_hover(
            mouse_x, mouse_y, 40, x_max, 120 + h + offset_y, y_max
        ):
            pygame.draw.rect(
                self.virtual_screen,
                hover_music_color,
                pygame.Rect(
                    40 - 1, 120 + h + offset_y - 1, volume_w + 2, volume_h + 2
                ),
                1,
            )

        return int(h)

    def _draw_home_animation(self, h: int) -> None:
        """
        Renders the looping cinematic animation on the home screen.

        This method manages a two-phase animation cycle:
        1. Ghosts chasing Pac-Man across the screen.
        2. Pac-Man chasing "scared" ghosts in the opposite direction.

        It calculates sprite positions, handles frame-based animations for
        character mouth movements and ghost textures, and manages the scaling
        of assets. When a character group exits the screen boundaries, the
        method resets their position and toggles the animation phase via
        internal counters.

        Args:
            h (int): The base vertical coordinate (usually the title height)
                used to anchor the animation on the Y-axis.
        """
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
        """
        Orchestrates the rendering of the game's main menu screen.

        This method serves as the primary assembly point for the home screen
        UI. it first triggers the rendering of interactive menu text and
        the title, retrieving the calculated title height. This height is
        then passed to the animation logic to ensure the decorative
        background cinematic is correctly positioned relative to the
        branding. It continuously updates based on the virtual mouse
        coordinates for menu interactivity.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
        h = self._draw_home_text(mouse_x, mouse_y)
        self._draw_home_animation(h)

    def _render(self, mouse_x: int, mouse_y: int) -> None:
        """
        The top-level rendering engine for the application.

        This method acts as the primary display controller, responsible for
        clearing the virtual screen and delegating drawing tasks based on
        the current global GameState. It ensures that only the relevant
        interface (Menu, Instructions, High Scores, Victory screen, or
        Active Gameplay) is processed and rendered for the current frame,
        passing mouse coordinates down to facilitate UI interaction.

        Args:
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.
        """
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
        """
        Processes all user inputs and updates game states accordingly.

        This central event handler interprets keyboard and mouse events
        based on the current GameState. In MENU or INFO states, it manages
        button clicks and navigation. During PLAYING, it translates key
        presses into Pac-Man movement or cheat activations. For GAME_OVER
        or WIN states, it facilitates text input for high scores. It also
        handles audio toggles, transition timers for level starts, and
        graceful application exits.

        Args:
            events (List[Event]): A list of pygame events to process.
            mouse_x (int): The current X coordinate of the virtual mouse.
            mouse_y (int): The current Y coordinate of the virtual mouse.

        Returns:
            bool: False if the game should quit, True otherwise.
        """
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                if not self.home_page_sound_play:
                    self.assets_manager.play_sound(
                        "assets/media/game_start.wav", None, False, 0.5
                    )
                    self.home_page_sound_play = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for key, value in self.interface["text"].items():
                            x_min, x_max = value[0]
                            y_min, y_max = value[1]

                            if self._is_hover(
                                mouse_x, mouse_y, x_min, x_max, y_min, y_max
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
                                    self.input_done = False

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

                        if self._is_hover(
                            mouse_x,
                            mouse_y,
                            x_min_volume,
                            x_max_volume,
                            y_min_volume,
                            y_max_volume,
                        ):
                            if not self.assets_manager.music_on:
                                self.assets_manager.music_on = True
                            else:
                                self.assets_manager.music_on = False
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
                            self.pause_info["time_left"] = (
                                self.config.level_max_time
                                - (
                                    (
                                        pygame.time.get_ticks()
                                        - self.level_starting_time
                                    )
                                    // 1000
                                )
                                - 1
                            )

                        else:
                            self.freeze_cheat = False
                            for ghost in self.ghosts.values():
                                if self.playing_state == PlayingState.POWER:
                                    ghost.speed = 1
                                else:
                                    ghost.speed = 2
                            self.level_starting_time = (
                                pygame.time.get_ticks()
                                - (
                                    self.config.level_max_time
                                    - self.pause_info["time_left"]
                                )
                                * 1000
                            ) + 1000

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

                        if self._is_hover(
                            mouse_x,
                            mouse_y,
                            x_min_exit,
                            x_max_exit,
                            y_min_exit,
                            y_max_exit,
                        ):
                            self.state = GameState.MENU

                        elif self._is_hover(
                            mouse_x,
                            mouse_y,
                            x_min_resume,
                            x_max_resume,
                            y_min_resume,
                            y_max_resume,
                        ):
                            self.state = GameState.PLAYING
                            self._depause_game()
                        elif self._is_hover(
                            mouse_x,
                            mouse_y,
                            x_min_volume,
                            x_max_volume,
                            y_min_volume,
                            y_max_volume,
                        ):
                            if not self.assets_manager.music_on:
                                self.assets_manager.music_on = True
                            else:
                                self.assets_manager.music_on = False
                                pygame.mixer.music.stop()

            elif self.state == GameState.SCORE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.interface["Back_highscores"][0]
                        y_min, y_max = self.interface["Back_highscores"][1]

                        if self._is_hover(
                            mouse_x, mouse_y, x_min, x_max, y_min, y_max
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

                        if self._is_hover(
                            mouse_x, mouse_y, x_min, x_max, y_min, y_max
                        ):
                            self.state = GameState.MENU
                            self.in_typing = False

                        elif self._is_hover(
                            mouse_x,
                            mouse_y,
                            x_min_input,
                            x_max_input,
                            y_min_input,
                            y_max_input,
                        ):
                            self.in_typing = True
                elif event.type == pygame.KEYDOWN and not self.input_done:
                    if event.key == pygame.K_RETURN:
                        self.enter_pressed = True
                    elif event.key == pygame.K_BACKSPACE:
                        if self.pseudo:
                            self.pseudo = self.pseudo[:-1]
                    elif event.unicode == " " or str(event.unicode).isalnum():
                        if len(self.pseudo) < 10:
                            self.pseudo += event.unicode

            elif self.state == GameState.INFO:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x_min, x_max = self.interface["Back_instructions"][0]
                        y_min, y_max = self.interface["Back_instructions"][1]

                        if self._is_hover(
                            mouse_x, mouse_y, x_min, x_max, y_min, y_max
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
        """
        Executes the main application loop and handles high-level setup.

        This method initializes the Pygame environment, sets up the display
        surfaces (both real and virtual for resolution independence), and
        starts the game's core execution loop. It maintains a consistent
        framerate of 60 FPS, coordinates the scaling of the virtual screen
        to the physical window, and continuously cycles through event
        handling, state updates, and rendering until the user exits.
        """
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        print("CHEMIN DE PYGAME :", pygame.__file__)

        pygame.init()
        pygame.mixer.init()

        self.real_screen = pygame.display.set_mode(
            (800, 800), pygame.RESIZABLE
        )

        self.virtual_screen = pygame.Surface((800, 800))

        self._init_game()
        pygame.display.set_icon(self.assets_manager.icon)
        clock = pygame.time.Clock()
        running = True

        self.assets_manager.play_sound(
            "assets/media/game_start.wav", None, False, 0.5
        )
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
