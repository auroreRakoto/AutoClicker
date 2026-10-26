"""Absolute, shared paths for the AutoClicker and Script Runner."""

from pathlib import Path

# Project layout:
#   project_root/data/       macro JSON files
#   project_root/scenario/   Script Runner modules and .acscript files
#   project_root/screenshots/ screenshots captured by the Script Runner
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scenario"
IMAGES_DIR = BASE_DIR / "screenshots"
DEFAULT_MODULE = "Conduite en vue extérieure"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
