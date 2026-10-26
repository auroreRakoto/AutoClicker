PYTHON ?= python
APP_NAME := AutoClicker
SCRIPT_APP_NAME := AutoClickerScriptRunner
BUILD_DIR := build
DIST_DIR := dist

.PHONY: help install build build-script clean run script

help:
	@echo "Targets:"
	@echo "  make install        Install dependencies and PyInstaller"
	@echo "  make run            Run the AutoClicker recorder"
	@echo "  make script         Run the Script Runner"
	@echo "  make build          Build the AutoClicker executable"
	@echo "  make build-script   Build the Script Runner executable"
	@echo "  make clean          Remove build artifacts"

install:
	$(PYTHON) -m pip install pynput pillow pyinstaller

run:
	$(PYTHON) src/main.py

script:
	$(PYTHON) src/script_runner.py

build:
	$(PYTHON) -m PyInstaller --noconfirm --clean --windowed --onedir \
		--name $(APP_NAME) --paths src \
		--add-data "data;data" --add-data "scenario;scenario" \
		--distpath $(DIST_DIR) --workpath $(BUILD_DIR)/autoclicker \
		src/main.py

build-script:
	$(PYTHON) -m PyInstaller --noconfirm --clean --windowed --onedir \
		--name $(SCRIPT_APP_NAME) --paths src \
		--add-data "data;data" --add-data "scenario;scenario" \
		--distpath $(DIST_DIR) --workpath $(BUILD_DIR)/script-runner \
		src/script_runner.py

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in (Path('build'), Path('dist'))]"
