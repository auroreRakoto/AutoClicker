"""Entry point for the AutoClicker Script Runner."""

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Support running with `python src/script_runner.py`.
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Run from the project root so relative data paths behave consistently.
os.chdir(PROJECT_ROOT)

import tkinter as tk
from script_runner_ui import ScriptRunnerUI


def main():
    root = tk.Tk()
    ScriptRunnerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
