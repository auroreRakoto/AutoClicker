"""Execution engine and parser for AutoClicker script sequences."""

import os
import re
import shlex
import threading
import time
import tkinter as tk
from PIL import ImageGrab

from config import MACROS_DIR
from macros import MacroManager
from player import MacroPlayer
from script_runner_paths import IMAGES_DIR


class ScriptRunner:
    """Séquenceur de macros avec checkpoints image manuels."""

    def __init__(self, root, macro_manager, player, on_status=None):
        self.root = root
        self.macro_manager = macro_manager
        self.player = player
        self.on_status = on_status
        self.stop_requested = threading.Event()
        self.running = False
        self._screenshot_continue = None
        self._screenshot_window = None

    def set_status(self, text):
        print(f"[SCRIPT] {text}")
        if self.on_status:
            self.root.after(0, lambda message=text: self.on_status(message, "#42a5f5"))

    @staticmethod
    def parse(text):
        commands = []
        for line_number, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            command, _, rest = line.partition(" ")
            command = command.upper()
            rest = rest.strip()

            if command == "ATTENDRE":
                try:
                    seconds = float(rest)
                except ValueError:
                    raise ValueError(f"Ligne {line_number}: utilise ATTENDRE secondes")
                if seconds < 0:
                    raise ValueError(f"Ligne {line_number}: délai négatif interdit")
                commands.append(("wait", seconds))
                continue

            if command == "SCREENSHOT":
                try:
                    parts = shlex.split(rest)
                except ValueError:
                    parts = []
                if len(parts) > 1:
                    raise ValueError(
                        f'Ligne {line_number}: utilise SCREENSHOT ou SCREENSHOT "nom de la capture"'
                    )
                screenshot_name = parts[0] if parts else "Capture"
                commands.append(("screenshot", screenshot_name))
                continue

            if command == "JOUER":
                if not rest:
                    raise ValueError(f"Ligne {line_number}: nom de macro manquant")
                repeat = 1
                if rest[0] in ('"', "'"):
                    quote = rest[0]
                    end = rest.find(quote, 1)
                    if end < 0:
                        raise ValueError(f"Ligne {line_number}: guillemets non fermés")
                    name = rest[1:end]
                    tail = rest[end + 1:].strip()
                    if tail:
                        if tail.startswith("*"):
                            tail = tail[1:].strip()
                        try:
                            repeat = int(tail)
                        except ValueError:
                            raise ValueError(f"Ligne {line_number}: répétition invalide")
                else:
                    match = re.fullmatch(r"(.+?)\s+(?:\*\s*)?(\d+)", rest)
                    if match:
                        name, repeat = match.group(1).strip(), int(match.group(2))
                    else:
                        name = rest
                if repeat < 1:
                    raise ValueError(f"Ligne {line_number}: répétition doit être >= 1")
                commands.append(("play", name.strip(), repeat))
                continue

            raise ValueError(
                f"Ligne {line_number}: commande inconnue '{command}'. "
                "Commandes : JOUER, ATTENDRE, SCREENSHOT."
            )
        return commands

    def stop(self):
        self.stop_requested.set()
        self.player.stop()
        event = self._screenshot_continue
        if event:
            event.set()
        if self._screenshot_window:
            self.root.after(0, self._close_screenshot_window)

    def _close_screenshot_window(self):
        window = self._screenshot_window
        self._screenshot_window = None
        if window is not None:
            try:
                window.grab_release()
            except tk.TclError:
                pass
            try:
                window.destroy()
            except tk.TclError:
                pass
        if self._screenshot_continue:
            self._screenshot_continue.set()

    def capture_screenshot(self, screenshot_name):
        """Capture automatiquement l'écran courant sans interrompre le script."""
        safe = re.sub(r'[<>:"/\\\\|?*]', "_", screenshot_name.strip()).strip(" .")
        if not safe:
            safe = "Capture"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe}.png"
        path = os.path.join(IMAGES_DIR, filename)
        suffix = 2
        while os.path.exists(path):
            filename = f"{timestamp}_{safe}_{suffix}.png"
            path = os.path.join(IMAGES_DIR, filename)
            suffix += 1

        try:
            image = ImageGrab.grab(all_screens=True)
            image.save(path, "PNG")
        except TypeError:
            # Pillow versions that do not support all_screens.
            image = ImageGrab.grab()
            image.save(path, "PNG")

        self.set_status(f"Capture enregistrée : {filename}")
        print(f"[SCREENSHOT] {screenshot_name} -> {path}")

    def run_text(self, text):
        if self.running or self.player.playing:
            raise RuntimeError("Une lecture est déjà en cours.")
        commands = self.parse(text)
        if not commands:
            raise ValueError("Le script est vide.")
        self.stop_requested.clear()
        self.running = True
        try:
            for index, command in enumerate(commands, start=1):
                if self.stop_requested.is_set():
                    break
                if command[0] == "wait":
                    seconds = command[1]
                    self.set_status(f"Étape {index}/{len(commands)} — attente {seconds:g}s")
                    deadline = time.monotonic() + seconds
                    while time.monotonic() < deadline and not self.stop_requested.is_set():
                        time.sleep(0.05)
                    continue
                if command[0] == "screenshot":
                    _, screenshot_name = command
                    self.set_status(f"Étape {index}/{len(commands)} — capture : {screenshot_name}")
                    self.capture_screenshot(screenshot_name)
                    continue
                _, name, repeat = command
                macro = self.macro_manager.load_macro(name)
                if not macro:
                    raise ValueError(f"Étape {index}: macro introuvable « {name} ». Vérifie le nom exact.")
                self.set_status(f"Étape {index}/{len(commands)} — {name} (x{repeat})")
                self.player.play(macro, repeat)
                if self.stop_requested.is_set() or not self.player.last_run_completed:
                    break
            self.set_status("Script terminé" if not self.stop_requested.is_set() else "Script arrêté")
        finally:
            self.running = False

