"""Shared paths for the Script Runner."""

from pathlib import Path

# Project layout: project_root/src/*.py
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
IMAGES_DIR = BASE_DIR / "script_images"
DEFAULT_MODULE = "Conduite en vue extérieure"

SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
