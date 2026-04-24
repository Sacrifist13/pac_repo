# Project Management & Implementation Log

## 1. Project Overview
This document tracks the implementation phases, encountered problems, and resolved bugs for the Pac-Man project. It serves as a central hub for development tracking, architectural decisions, and project health management.

## 2. Implementation Phases

### Phase 1: Core Architecture & Setup
- **Engine Initialization:** Bootstrapped the main game loop and display rendering using Pygame (`pac-man.py` & `src/game_engine.py`).
- **Asset Management:** Centralized the loading of sprites, fonts, and sound effects in `src/assets_manager.py` to optimize memory allocation and ensure resources are cached efficiently.
- **Entity Modeling:** Designed the foundational object-oriented classes and data structures for dynamic game entities (`src/models.py`, `src/entities.py`, `src/enums_class.py`).

### Phase 2: Gameplay Mechanics
- **Environment Generation:** Developed the grid-based maze system, wall rendering, and bounding-box collision detection mechanisms (`src/map_generator.py`).
- **Player Controller:** Implemented Pac-Man's movement logic, animation state machine (death sequences, eating), and smooth input handling.
- **Ghost AI & Pathfinding:** Programmed distinct targeting behaviors for all four ghosts (Blinky, Pinky, Inky, Clyde). Integrated the complex state machine for Chase, Scatter, Frightened, and Eaten modes.
- **Progression & Scoring:** Added pellet consumption logic, point multipliers for eating ghosts consecutively, and a persistent highscore tracker (`src/highscores.py`).

### Phase 3: Polish & Build Configuration
- **Audio Integration:** Bound Pygame mixer events to specific gameplay actions to trigger sound effects (munching, power pellets, game start, death) precisely on time.
- **Packaging & Dependency Management:** Configured `pyproject.toml` and `pac-man.spec` for standardized building, dependency locking (via `uv.lock`), and easy distribution of the executable.

## 3. Encountered Problems

During the development lifecycle, the engineering team faced several technical hurdles that required significant refactoring:

- **Performance Bottlenecks in Pathfinding:** *Problem:* Initially, calculating A* pathfinding and target vectors for all four ghosts on every single frame caused severe framerate drops, especially on lower-end machines.
  *Resolution:* Optimized the movement logic so that ghosts only recalculate their target paths when they reach the exact center of a grid tile, drastically reducing the number of calculations per second.

## 4. Fixed Bugs

- **[BUG-014] Texture Memory Leak:** Fixed a critical memory leak where returning to the main menu and restarting the game would reload all `.png` assets from disk instead of fetching them from the initialized dictionary in `assets_manager.py`.
- **[BUG-027] Corner Clipping Glitch:** Resolved a collision detection glitch where rapid directional inputs allowed Pac-Man to clip through wall corners. Fixed by clamping the turn threshold to strict tile alignment and requiring a clear path ahead before allowing the velocity vector to change.
- **[BUG-033] Frightened Timer Desync (Pause Menu):** Fixed a bug where pausing the game did not pause the active Power Pellet timer. This caused ghosts to revert back to "Chase" mode instantly upon unpausing the game. Deltas are now strictly tied to the active game state.
- **[BUG-041] Highscore File Corruption:** Addressed an issue where closing the game window abruptly during a highscore save would corrupt the JSON tracking file. Implemented an atomic save operation (writing to a temporary file first, then safely replacing the original file).