PYTHON_CMD  := uv run python3 pac-man.py config.json

BOLD   := \033[1m
RESET  := \033[0m
GREEN  := \033[32m

.PHONY: all install run debug clean lint lint-strict install

all: install run

install:
	@echo "$(BOLD)🚀 Initializing project environment and syncing dependencies...$(RESET)"
	@pip install uv
	@uv sync
	@echo "\n$(BOLD)$(GREEN)✅ Environment setup complete.$(RESET)"

run:
	@echo "$(BOLD)🕹️  Executing main script...$(RESET)"
	$(PYTHON_CMD)

debug:
	@echo "$(BOLD)⚙️ Executing main script with pdb...$(RESET)"
	$(PYTHON_CMD) -m pdb

clean:
	@echo "$(BOLD)🗑️  Cleaning up build artifacts and cache...$(RESET)"
	rm -rf .mypy_cache __pycache__ src/__pycache__ build dist
	@echo "\n$(BOLD)$(GREEN)🧹 Workspace is clean.$(RESET)"

package: install
	@echo "$(BOLD)📦 Creating game executable...$(RESET)"
	uv run pyinstaller --noconfirm --onedir --windowed --add-data "assets:assets" --add-data "config.json:." pac-man.py
	@echo "$(BOLD)📄 Integrating instructions...$(RESET)"
	cp INSTRUCTIONS.txt dist/pac-man/
	@echo "$(BOLD)🗜️ Compressing final archive...$(RESET)"
	cd dist && zip -r pacman_release.zip pac-man/
	@echo "\n$(BOLD)$(GREEN)✅ Game pack generated in dist/pacman_release.zip !$(RESET)"

lint:
	@echo "$(BOLD)🔎 Running static code analysis (src only + silent imports)...$(RESET)"
	flake8 --exclude=.venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs