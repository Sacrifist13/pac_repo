<div align="center">
  <h1>👻 Pac-Man: The Python Rebirth 🕹️</h1>
  <p><i>This project has been created as part of the 42 curriculum by thsykas and kkraft.</i></p>
  <p>A modern, modular, and robust recreation of the classic 1980 arcade game in Python.</p>
</div>

---

## 📋 Table of Contents
* [Description](#-description)
* [Project Planning & Tasks](#-project-planning--tasks)
* [Technical Rules & Requirements](#-technical-rules--requirements)
* [Instructions & Usage](#-instructions--usage)
* [Configuration](#-configuration)
* [Maze Generation](#-maze-generation)
* [Highscores](#-highscores)
* [Implementation & Architecture](#-implementation--architecture)
* [Project Management](#-project-management)
* [Resources & AI Usage](#-resources--ai-usage)

---

## 📖 Description
This project aims to breathe new life into the cultural icon **Pac-Man**, originally released in 1980 by Namco. Built entirely in Python (3.10+), this iteration utilizes Object-Oriented Programming (OOP) and a modular graphical library (like MLX) to deliver a complete, playable arcade experience. It features persistent highscores, dynamic maze generation through external packages, customizable configurations, and a deployment-ready build for public gaming platforms.

---

## 📅 Project Planning & Tasks

To ensure smooth delivery, the project is divided into distinct phases. 

### Phase 1: Foundation & Setup
| Status | Task | Description |
| :---: | :--- | :--- |
| ⬜ | **Environment Setup** | Setup Python 3.10+, virtual environments, and `.gitignore`. |
| ⬜ | **Makefile Creation** | Implement `install`, `run`, `debug`, `clean`, `lint` (flake8 + mypy), `lint-strict`. |
| ⬜ | **Architecture Design** | Draft the OOP class structure (Game Engine, Entities, UI). |

### Phase 2: Core Mechanics
| Status | Task | Description |
| :---: | :--- | :--- |
| ⬜ | **Config Parser** | Read JSON files with comments, handle missing/invalid values gracefully (no traceback). |
| ⬜ | **Maze Integration** | Integrate the assigned `A-Maze-ing` package (Seed 42 for lvl 1, PERFECT=False). |
| ⬜ | **Entities Logic** | Implement Player (movement, lives) and Ghosts (chase/flee AI, respawn). |
| ⬜ | **Items & Scoring** | Add Pacgums (score X), Super-pacgums (score Y, invincibility), and ghost eating (score Z). |

### Phase 3: Game Flow & UI
| Status | Task | Description |
| :---: | :--- | :--- |
| ⬜ | **Game Loop** | Manage levels, time limits (e.g., 90s), winning/losing conditions, and pause functionality. |
| ⬜ | **User Interface** | Build Main Menu, In-Game HUD, Pause Menu, Game Over, and Victory screens. |
| ⬜ | **Highscore System** | Save/load top 10 scores persistently. Prompt for name (max 10 chars) at game end. |

### Phase 4: Polish & Deployment
| Status | Task | Description |
| :---: | :--- | :--- |
| ⬜ | **Cheat Mode** | Add invincibility, level skip, ghost freeze, extra lives, and speed boost for peer review. |
| ⬜ | **Packaging** | Create a functional package for deployment on Steam/Itch.io (unlisted/private). |
| ⬜ | **Documentation** | Finalize project management docs (Gantt, risk analysis) and README. |

---

## 🛑 Technical Rules & Requirements

* **Language:** Python 3.10 or later.
* **Typing & Linting:** * Code MUST adhere to `flake8` standards.
  * Strict type hinting is mandatory. `mypy` must pass without errors.
* **Documentation:** All functions and classes require PEP 257 compliant docstrings (Google or NumPy style).
* **Error Handling:** **NO CRASHES.** Exceptions must be handled gracefully. A Python traceback during evaluation means an automatic fail. Context managers (`with`) must be used for resource handling.
* **AI Policy:** AI can be used for drafting and brainstorming, but you must fully understand and be able to explain every line of code during peer review. 

---

## 🚀 Instructions & Usage

### Make Commands
Use the provided `Makefile` to manage the project:
* `make install`: Installs project dependencies.
* `make run`: Executes the game.
* `make debug`: Runs the game in debug mode (e.g., via pdb).
* `make clean`: Removes temporary files (pycache, mypy_cache).
* `make lint`: Runs `flake8` and `mypy` with required flags.
* `make lint-strict`: Runs strictly configured linting.

### Running the Game
Launch the game via the command line, providing a configuration file:
> python3 pac-man.py config.json

*Note: The program requires exactly one argument. If the config is faulty, the game will load safe default values and log a clear warning message rather than crashing.*

---

## ⚙️ Configuration
The game relies on a `.json` configuration file that supports comments (lines starting with `#`). 

**Default Configuration Fallbacks:**
* `highscore_filename`: "highscores.json"
* `lives`: 3
* `points_per_pacgum`: 10
* `points_per_super_pacgum`: 50
* `points_per_ghost`: 200
* `seed`: 42
* `level_max_time`: 90

If an unknown key is provided, it is ignored. If a value is missing or corrupted, the game clamps to these safe defaults.

---

## 🧩 Maze Generation
This project relies on an external `A-Maze-ing` package assigned by another peer group. 
* **Integration:** Used strictly as-is without internal modification.
* **Logic:** Level 1 uses a fixed seed (e.g., 42). Subsequent levels are fully randomized.
* **Pac-Man Parameters:** The `PERFECT` parameter is set to `False` to ensure interconnected corridors suitable for Pac-Man gameplay.

---

## 🏆 Highscores
The highscore system is persistent and robust:
* **Storage:** Saved locally as a JSON file.
* **Data:** Maintains the Top 10 players. Limits names to 10 alphanumeric characters.
* **Flow:** Loaded at game startup and displayed in the Main Menu. Saves automatically when a player enters their name upon Victory or Game Over.

---

## 🏗️ Implementation & Architecture

### Technical Summary
The game is built using a modular Object-Oriented approach. Pygame/MLX handles the display and event loops, while the game logic is decoupled into independent managers (StateManager, CollisionManager, EntityController).

### General Software Architecture
1. **Core Engine:** Handles the main game loop, delta time, and input broadcasting.
2. **Entity Module:** Contains the `Player` class and the `Ghost` base class (with specific AI behaviors extending it).
3. **World Module:** Wraps the `A-Maze-ing` package, manages the grid, wall collisions, and item placements (Pacgums/Super-pacgums).
4. **UI Module:** Manages view states (Menu, Playing, Paused, GameOver).

---

## 📂 Project Management
We utilize a structured Kanban/Agile approach to track progress. 
All management evidence (Gantt charts, risk analysis, task delegation, and acceptance testing plans) can be found in the dedicated `/project_management` directory within this repository. 

---

## 🧠 Resources & AI Usage
* **References:** * [Python 3.10 Documentation](https://docs.python.org/3/)
  * [PEP 257 Docstring Conventions](https://peps.python.org/pep-0257/)
  * [The Pac-Man Dossier (Ghost AI behaviors)](https://pacman.holenet.info/)
* **AI Usage:** * *ChatGPT / Claude:* Used for generating boilerplate code structure, reviewing Regex for the config parser, and generating this README documentation. All code was heavily refactored, peer-reviewed, and thoroughly tested to ensure complete comprehension.

https://github.com/TG922/pacman-game-assets