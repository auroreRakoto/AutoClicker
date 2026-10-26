"""Tkinter user interface for the AutoClicker Script Runner."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from player import MacroPlayer
from macros import MacroManager
from config import MACROS_DIR
from script_runner_engine import ScriptRunner
from script_runner_paths import BASE_DIR, SCRIPTS_DIR, IMAGES_DIR, DEFAULT_MODULE
from script_runner_utils import safe_name
from script_runner_help import show_commands_help
from status_overlay import StatusOverlay
from main import MacroRecorderApp


class ScriptRunnerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker V2.3 — Script Runner")
        self.root.geometry("1200x760")
        self.root.minsize(950, 600)
        self.root.resizable(True, True)
        self.root.configure(bg="#202124")

        self.manager = MacroManager(MACROS_DIR)
        self.player = MacroPlayer(root=root, on_action=self.on_playback_action)
        self.status = tk.StringVar(value="Prêt")
        self.module_var = tk.StringVar(value=DEFAULT_MODULE)
        self.current_script_path = None
        self.overlay = StatusOverlay(self.root, "Script Runner — État")

        header = tk.Frame(root, bg="#202124")
        header.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(header, text="Script Runner", font=("Segoe UI", 17, "bold"),
                 bg="#202124", fg="white").pack(anchor="w")
        header_info = tk.Frame(header, bg="#202124")
        header_info.pack(fill="x", pady=(3, 0))
        tk.Label(
            header_info,
            text='Commandes : JOUER "Exo 1" • JOUER "Skip" * 5 • ATTENDRE 2 • SCREENSHOT "nom de la capture"',
            bg="#202124", fg="#bdbdbd", font=("Segoe UI", 9)
        ).pack(side="left", anchor="w")
        tk.Button(
            header_info, text="📖 Commandes disponibles",
            command=lambda: show_commands_help(self.root, self.editor, self.status)
        ).pack(side="right", padx=(8, 0))

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
        tk.Button(sidebar, text="🔴 Enregistrer une macro", command=self.open_macro_recorder).pack(
            fill="x", padx=8, pady=(0, 10)
        )

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
        def update():
            self.status.set(text)
            lowered = text.lower()
            if any(word in lowered for word in ("étape", "lecture", "attente", "capture")):
                self.overlay.update(text)
            if "script terminé" in lowered or "script arrêté" in lowered:
                self.overlay.stop(text)
        self.root.after(0, update)

    def on_playback_action(self, action):
        action_type = action.get("type", "action")
        data = action.get("data", {})
        if action_type == "key_press":
            label = f"Touche : {data}"
        elif action_type == "mouse_click":
            label = f"Clic : {data.get('button', 'souris')}"
        elif action_type == "mouse_scroll":
            label = "Défilement souris"
        else:
            label = f"Action : {action_type}"
        self.overlay.update(label)

    def open_macro_recorder(self):
        """Open the AutoClicker recorder as a child window, sharing data/ macros."""
        child = tk.Toplevel(self.root)
        app = MacroRecorderApp(child)
        original_close = app.close

        def close_recorder():
            original_close()
            self.root.after(250, self.refresh_macro_availability)

        child.protocol("WM_DELETE_WINDOW", close_recorder)
        self.status.set("Enregistre une macro : elle sera disponible avec JOUER dans ce script.")

    def refresh_macro_availability(self):
        names = self.manager.get_macros()
        self.status.set(
            f"Macros disponibles : {len(names)} — " + (", ".join(names[:5]) if names else "aucune")
        )

    def module_path(self, module):
        return os.path.join(str(SCRIPTS_DIR), safe_name(module))

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

        self.overlay.start("Script en cours…")

        def run():
            try:
                self.runner.run_text(text)
            except Exception as exc:
                self.root.after(0, lambda error=exc: messagebox.showerror("Erreur du script", str(error), parent=self.root))
                self.root.after(0, lambda error=exc: self.status.set(f"Erreur : {error}"))
                self.root.after(0, lambda error=exc: self.overlay.stop(f"Erreur : {error}"))
        threading.Thread(target=run, daemon=True).start()

    def stop_script(self):
        self.runner.stop()

    def close(self):
        self.runner.stop()
        self.player.stop()
        self.overlay.destroy()
        self.root.destroy()

