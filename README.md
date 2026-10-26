# AutoClicker

A Python desktop tool to record, manage, and replay macros, with screenshot annotations and scripted macro sequences.

## Requirements

- Python 3.13 or newer
- Windows/macOS/Linux with a graphical desktop session
- `pynput` and `Pillow`

## Run

From the project directory:

```bash
python -m venv .venv
```

Activate the environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

Install dependencies and launch:

```bash
python -m pip install --upgrade pip
python -m pip install pynput pillow
python main.py
```

The app stores macros in `macros/`. Existing macro JSON files are included in this repository.

## Scripted sequences

To run a scripted sequence, use:

```bash
python script_runner.py
```

Check the commands and macro names in `script_runner.py` before running it. Macro playback can control the mouse and keyboard, so review a sequence before execution.

## Project structure

- `main.py` — application entry point
- `config.py` — application settings
- `macros.py` — macro storage and management
- `recorder.py` — input recording
- `player.py` — macro playback
- `screenshots.py` — screenshot handling
- `ui.py` — desktop interface
- `macros/` — saved macro definitions
- `scripts/` — scenario scripts
- `script_images/` — images used by scenarios
