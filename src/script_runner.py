import os
import sys
import re
import shlex
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageGrab

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import MACROS_DIR
from macros import MacroManager
from player import MacroPlayer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
IMAGES_DIR = os.path.join(BASE_DIR, "script_images")
DEFAULT_MODULE = "Conduite en vue extérieure"
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


def safe_name(name):
    name = re.sub(r'[<>:"/\\|?*]', "_", name.strip())
    return name.strip(" .")


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


class ScriptRunnerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker V2.3 — Script Runner")
        self.root.geometry("1100x700")
        self.root.minsize(900, 580)
        self.root.configure(bg="#202124")

        self.manager = MacroManager(MACROS_DIR)
        self.player = MacroPlayer(root=root)
        self.status = tk.StringVar(value="Prêt")
        self.module_var = tk.StringVar(value=DEFAULT_MODULE)
        self.current_script_path = None

        header = tk.Frame(root, bg="#202124")
        header.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(header, text="Script Runner", font=("Segoe UI", 17, "bold"),
                 bg="#202124", fg="white").pack(anchor="w")
        tk.Label(header, text='Commandes : JOUER "Exo 1" • JOUER "Skip" * 5 • ATTENDRE 2 • SCREENSHOT "nom de la capture"',
                 bg="#202124", fg="#bdbdbd", font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        body = tk.Frame(root, bg="#202124")
        body.pack(fill="both", expand=True, padx=14, pady=6)

        # Left sidebar: modules and saved scripts.
        sidebar = tk.Frame(body, bg="#303134", width=270)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="MODULES", bg="#303134", fg="#aaaaaa",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(12, 4))
        self.module_list = tk.Listbox(sidebar, height=7, exportselection=False,
                                      bg="#202124", fg="white", selectbackground="#4c8bf5",
                                      relief="flat", font=("Segoe UI", 10))
        self.module_list.pack(fill="x", padx=8)
        module_buttons = tk.Frame(sidebar, bg="#303134")
        module_buttons.pack(fill="x", padx=8, pady=6)
        tk.Button(module_buttons, text="+ Module", command=self.add_module).pack(side="left", fill="x", expand=True)
        tk.Button(module_buttons, text="Renommer", command=self.rename_module).pack(side="left", padx=(5, 0))

        tk.Label(sidebar, text="SCRIPTS DU MODULE", bg="#303134", fg="#aaaaaa",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        self.script_list = tk.Listbox(sidebar, exportselection=False, bg="#202124", fg="white",
                                      selectbackground="#4c8bf5", relief="flat", font=("Segoe UI", 10))
        self.script_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.script_list.bind("<<ListboxSelect>>", self.on_script_selected)
        script_buttons = tk.Frame(sidebar, bg="#303134")
        script_buttons.pack(fill="x", padx=8, pady=(0, 10))
        tk.Button(script_buttons, text="Nouveau", command=self.new_script).pack(side="left", fill="x", expand=True)
        tk.Button(script_buttons, text="Supprimer", command=self.delete_script).pack(side="left", padx=(5, 0))

        # Main editor.
        main = tk.Frame(body, bg="#202124")
        main.pack(side="left", fill="both", expand=True)
        self.editor = tk.Text(main, wrap="none", font=("Consolas", 11), undo=True,
                              bg="#f7f7f7", fg="#111111", insertbackground="#111111")
        self.editor.pack(fill="both", expand=True)
        self.editor.insert("1.0", '# Une commande par ligne\nJOUER "Exo 1"\nATTENDRE 2\nJOUER "Skip" * 5\n# Capture automatiquement l’écran à cette étape\nSCREENSHOT "Après les skips"\nJOUER "Quitter exo"\n')

        buttons = tk.Frame(main, bg="#202124")
        buttons.pack(fill="x", pady=(8, 0))
        tk.Button(buttons, text="▶ Lancer le script", command=self.start_script, width=16).pack(side="left", padx=(0, 5))
        tk.Button(buttons, text="⏹ Arrêter", command=self.stop_script, width=10).pack(side="left", padx=5)
        tk.Button(buttons, text="📸 Ajouter capture auto", command=self.insert_screenshot_command, width=19).pack(side="left", padx=5)
        tk.Button(buttons, text="Enregistrer", command=self.save_script, width=12).pack(side="left", padx=5)
        tk.Button(buttons, text="Ouvrir fichier…", command=self.open_external_script, width=14).pack(side="left", padx=5)
        tk.Label(root, textvariable=self.status, anchor="w", bg="#202124", fg="#bdbdbd").pack(fill="x", padx=14, pady=(6, 10))

        self.runner = ScriptRunner(root, self.manager, self.player, self.set_status)
        self.refresh_modules(select=DEFAULT_MODULE)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def set_status(self, text, color="#42a5f5"):
        self.root.after(0, lambda: self.status.set(text))

    def module_path(self, module):
        return os.path.join(SCRIPTS_DIR, safe_name(module))

    def refresh_modules(self, select=None):
        os.makedirs(SCRIPTS_DIR, exist_ok=True)
        names = sorted(
            d for d in os.listdir(SCRIPTS_DIR)
            if os.path.isdir(os.path.join(SCRIPTS_DIR, d))
        )
        if DEFAULT_MODULE not in names:
            os.makedirs(self.module_path(DEFAULT_MODULE), exist_ok=True)
            names.append(DEFAULT_MODULE)
            names.sort()
        self.module_list.delete(0, tk.END)
        for name in names:
            self.module_list.insert(tk.END, name)
        wanted = select or self.module_var.get() or DEFAULT_MODULE
        if wanted not in names:
            wanted = DEFAULT_MODULE if DEFAULT_MODULE in names else names[0]
        idx = names.index(wanted)
        self.module_list.selection_set(idx)
        self.module_list.activate(idx)
        self.module_var.set(wanted)
        self.refresh_scripts()

    def selected_module(self):
        sel = self.module_list.curselection()
        return self.module_list.get(sel[0]) if sel else DEFAULT_MODULE

    def refresh_scripts(self, select=None):
        module = self.selected_module()
        folder = self.module_path(module)
        os.makedirs(folder, exist_ok=True)
        names = sorted(f for f in os.listdir(folder) if f.endswith(".acscript"))
        self.script_list.delete(0, tk.END)
        for filename in names:
            self.script_list.insert(tk.END, os.path.splitext(filename)[0])
        if select and select in [os.path.splitext(n)[0] for n in names]:
            idx = [os.path.splitext(n)[0] for n in names].index(select)
            self.script_list.selection_set(idx)
            self.script_list.activate(idx)

    def on_script_selected(self, event=None):
        sel = self.script_list.curselection()
        if not sel:
            return
        name = self.script_list.get(sel[0])
        path = os.path.join(self.module_path(self.selected_module()), name + ".acscript")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.current_script_path = path
            self.status.set(f"Script chargé : {name}")
        except OSError as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.root)

    def add_module(self):
        name = simpledialog.askstring("Nouveau module", "Nom du module :", parent=self.root)
        if not name:
            return
        name = safe_name(name)
        if not name:
            return
        path = self.module_path(name)
        if os.path.exists(path):
            messagebox.showwarning("Module existant", "Ce module existe déjà.", parent=self.root)
            return
        os.makedirs(path, exist_ok=True)
        self.refresh_modules(select=name)

    def rename_module(self):
        old = self.selected_module()
        new = simpledialog.askstring("Renommer le module", "Nouveau nom :", initialvalue=old, parent=self.root)
        if not new:
            return
        new = safe_name(new)
        if not new or new == old:
            return
        old_path, new_path = self.module_path(old), self.module_path(new)
        if os.path.exists(new_path):
            messagebox.showwarning("Module existant", "Un module porte déjà ce nom.", parent=self.root)
            return
        os.rename(old_path, new_path)
        self.refresh_modules(select=new)

    def new_script(self):
        name = simpledialog.askstring("Nouveau script", "Nom du script :", parent=self.root)
        if not name:
            return
        name = safe_name(name)
        if not name:
            return
        self.current_script_path = os.path.join(self.module_path(self.selected_module()), name + ".acscript")
        if os.path.exists(self.current_script_path):
            messagebox.showwarning("Script existant", "Ce script existe déjà.", parent=self.root)
            return
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", '# Nouveau script\n')
        self.save_script()
        self.refresh_scripts(select=name)

    def save_script(self):
        if not self.current_script_path:
            name = simpledialog.askstring("Enregistrer le script", "Nom du script :", parent=self.root)
            if not name:
                return
            name = safe_name(name)
            if not name:
                return
            self.current_script_path = os.path.join(self.module_path(self.selected_module()), name + ".acscript")
        os.makedirs(os.path.dirname(self.current_script_path), exist_ok=True)
        try:
            with open(self.current_script_path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.refresh_scripts(select=os.path.splitext(os.path.basename(self.current_script_path))[0])
            self.status.set(f"Script enregistré : {os.path.basename(self.current_script_path)}")
        except OSError as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.root)

    def delete_script(self):
        sel = self.script_list.curselection()
        if not sel:
            messagebox.showinfo("Sélectionne un script", "Choisis un script dans la liste.", parent=self.root)
            return
        name = self.script_list.get(sel[0])
        path = os.path.join(self.module_path(self.selected_module()), name + ".acscript")
        if not messagebox.askyesno("Supprimer", f"Supprimer le script « {name} » ?", parent=self.root):
            return
        try:
            os.remove(path)
            if self.current_script_path == path:
                self.current_script_path = None
                self.editor.delete("1.0", tk.END)
            self.refresh_scripts()
        except OSError as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.root)

    def insert_screenshot_command(self):
        name = simpledialog.askstring(
            "Ajouter une capture automatique",
            "Nom de la capture (elle sera prise pendant l'exécution) :",
            initialvalue="Checkpoint",
            parent=self.root
        )
        if name is None:
            return
        name = name.strip() or "Capture"
        self.editor.insert(tk.INSERT, f'SCREENSHOT "{name}"\\n')
        self.editor.focus_set()
        self.status.set(f"Capture automatique ajoutée : {name}")

    def open_external_script(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Ouvrir un script",
            filetypes=[("Scripts AutoClicker", "*.acscript *.txt"), ("Tous les fichiers", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())
            self.current_script_path = path
            self.status.set(f"Fichier ouvert : {os.path.basename(path)}")
        except OSError as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.root)

    def start_script(self):
        text = self.editor.get("1.0", "end-1c")
        try:
            ScriptRunner.parse(text)
        except Exception as exc:
            messagebox.showerror("Script invalide", str(exc), parent=self.root)
            return
        if self.runner.running or self.player.playing:
            messagebox.showwarning("En cours", "Une lecture est déjà en cours.", parent=self.root)
            return

        def run():
            try:
                self.runner.run_text(text)
            except Exception as exc:
                self.root.after(0, lambda error=exc: messagebox.showerror("Erreur du script", str(error), parent=self.root))
                self.root.after(0, lambda error=exc: self.status.set(f"Erreur : {error}"))
        threading.Thread(target=run, daemon=True).start()

    def stop_script(self):
        self.runner.stop()

    def close(self):
        self.runner.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    ScriptRunnerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
