import os


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "Macro Recorder V2"

MACROS_DIR = "macros"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 720

BACKGROUND_COLOR = "#202124"
PANEL_COLOR = "#303134"
ITEM_COLOR = "#3a3b3d"

TEXT_COLOR = "white"
SECONDARY_TEXT_COLOR = "#aaaaaa"

GREEN = "#2eaf5d"
RED = "#e53935"
BLUE = "#4c8bf5"
ORANGE = "#ff9800"
DARK_BUTTON = "#3d3d3d"


# ============================================================
# DOSSIERS
# ============================================================

os.makedirs(MACROS_DIR, exist_ok=True)
