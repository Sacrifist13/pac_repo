*This project has been created as part of the 42 curriculum by kkraft, thsykas.*

# Pacman: Ghosts! More ghosts!

## I. Description
This project is a modern recreation of the 1980 Namco arcade classic, **Pac-Man**, developed in Python 3.10+. The goal was to build a complete, playable game featuring modular architecture, robust error handling, and a polished user interface[cite: 102, 108].This version incorporates the iconic ghost AI behaviors (Blinky, Pinky, Inky, and Clyde), power-up mechanics via Super-pacgums, and a persistent highscore system.

---
## II. Instructions

### Installation
The project requires Python 3.10 or later. To install dependencies, use the provided `Makefile`:

```bash

make install
```
*This command uses pip, uv, or pipx to handle project requirements.*

### Execution
The program must be launched from the command line with exactly one configuration file argument:
```bash
python3 pac-man.py config.json
```
*Note: The configuration file must be a valid JSON file, though comments starting with `#` are supported.*

### Development Tools
* **Run**: `make run`
* **Debug**: `make debug` (launches with `pdb`)
* **Linting**: `make lint` (executes `flake8` and `mypy` with specific strictness flags)
* **Cleanup**: `make clean` (removes `__pycache__` and `mypy_cache`)

---

## III. Resources & AI Usage

### References
* **Python Documentation**: Official 3.10+ guides for type hinting and context managers.
* **PEP 257/8**: Guidelines for docstrings and coding standards.
* **Retro Game Mechanics**: Research into the original 1980 AI patterns and "kill screen" logic.

### AI Implementation Statement
In accordance with Chapter II[cite: 17], AI tools were utilized to:
1.  **Refine Prompting Skills**: Used to generate boilerplate for the `A-Maze-ing` package adapter.
2.  **Code Review**: Assisted in identifying potential edge cases for exception handling and resource management (ensuring no crashes or leaks).
3.  **Unit Test Ideas**: AI suggested testing strategies for the maze parsing logic, which were then peer-reviewed and implemented via `pytest`.
*All AI-generated logic was thoroughly checked and rewritten where necessary to ensure full understanding and maintainability.*

---

## IV. Configuration
The game is highly customizable via a JSON configuration file. Unknown keys are ignored, and invalid values are clamped to safe defaults.

| Key | Description | Default Example |
| :--- | :--- | :--- |
| `highscore_filename` | Path to the highscore storage file. | `"highscores.json"` |
| `level` | Array defining parameters for multiple levels. | `[{"width": 20, "height": 20}]` |
| `lives` | Number of starting lives. | `3` |
| `points_per_pacgum` | Score awarded for small pellets. | `10` |
| `seed` | RNG seed for the first level maze. | `42` |
| `level_max_time` | Time limit per level in seconds. | `90` |

---

## V. Highscore System
The system maintains a persistent record of the **Top 10** scores:
* **Storage**: Data is saved to a JSON file on disk, ensuring persistence between sessions.
* **Robustness**: The system handles missing or corrupted files gracefully.
* **User Input**: Players can enter alphanumeric names (max 10 characters) upon winning or losing.
* **Display**: Highscores are displayed in the main menu for competitive visibility.

---

## VI. Maze Generation
This project integrates an external **A-Maze-ing** package:
* **Interface**: Our loader adapts to the external package's specific API without modification.
* **Pac-Man Style**: The `PERFECT` parameter is set to `False` to ensure corridors are suitable for the game (allowing loops).
* **Structure**: The first level uses a fixed seed (`42`), while subsequent levels are randomized.
* **Layout**: Pacgums fill corridors, Super-pacgums occupy the 4 corners, and the player starts in the center.


---

## VII. Implementation & Game Logic

### Player Mechanics
* **Movement**: Controlled via arrow keys or WASD through corridors.
* **Progression**: Eating all pacgums completes a level; completing all 10+ levels wins the game.
* **Interactions**: Touching a ghost loses a life and triggers a respawn at the center.

### Ghost AI (Implemented by thsykas)
* **States**: Ghosts alternate between "Chase" (approaching the player) and "Flee" (running away when player eats a Super-pacgum).
* **Respawn**: Eaten ghosts return to their corners and respawn after 5-10 seconds.

### Cheat Mode
To facilitate peer review, a cheat mode is available:
* **Invincibility**: Player cannot be killed by ghosts.
* **Level Skip**: Instantly advance to the next level.
* **Ghost Freeze**: Stops all autonomous ghost movement.

---

## VIII. General Software Architecture
The project follows an Object-Oriented approach using a modular structure:
* **`Core`**: Manages the main game loop, level transitions, and the 90s timer.
* **`Entities`**: Contains classes for the `Player` and `Ghost` (Blinky, Pinky, Inky, Clyde logic).
* **`UI/Graphics`**: Handles the MLX-based rendering for the HUD, Main Menu, and Game Over screens.
* **`Config/IO`**: Manages JSON parsing and highscore persistence.

---


## IX. Project Management

### Team Roles
* **kkraft**: Primary focus on **visual assets**, UI design, and graphical rendering logic. []Responsible for the "look and feel" of the menus and the in-game HUD[cite: 108, 258].
* []**thsykas**: Responsible for **core algorithms**, specifically the ghost AI behaviors, the persistent highscore system, and workload distribution/management documentation[cite: 10, 158].

### Methodology
We utilized a dedicated subdirectory (`/management`) containing:
* **Gantt Chart**: Timeline of development phases.
* **Risk Analysis**: Mitigation strategies for unhandled exceptions and generator failures.
* **Acceptance Test Plan**: A log of features tested and bugs resolved (e.g., ghost movement through walls).

---

## X. Submission & Review
This project is prepared for deployment on public platforms (Itch.io/Steam) as a private build. During peer review, the code must pass `mypy` without errors and handle any requested "recode" modifications within minutes to verify understanding.
