import os
import tkinter as tk
from tkinter import messagebox, simpledialog


from config import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    PANEL_COLOR,
    ITEM_COLOR,
    TEXT_COLOR,
    SECONDARY_TEXT_COLOR,
    GREEN,
    RED,
    BLUE,
    ORANGE,
    DARK_BUTTON
)


class MacroUI:

    def __init__(
        self,
        root,
        app
    ):
        self.root = root
        self.app = app

        self.root.title(
            APP_NAME
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.resizable(True, True)
        self.root.minsize(650, 480)

        self.root.configure(
            bg=BACKGROUND_COLOR
        )

        self.build()

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text,
        color=SECONDARY_TEXT_COLOR
    ):
        self.status_label.config(
            text=text,
            fg=color
        )

    # ========================================================
    # BUILD
    # ========================================================

    def build(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )

        header.pack(
            fill="x",
            pady=(20, 5)
        )

        title = tk.Label(
            header,
            text="Macro Recorder",
            font=("Segoe UI", 23, "bold"),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )

        title.pack()

        subtitle = tk.Label(
            header,
            text="Enregistre et documente tes procédures",
            font=("Segoe UI", 10),
            bg=BACKGROUND_COLOR,
            fg="#8a8a8a"
        )

        subtitle.pack(
            pady=(3, 0)
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = tk.Label(
            self.root,
            text="● Prêt",
            font=("Segoe UI", 11),
            bg=BACKGROUND_COLOR,
            fg=SECONDARY_TEXT_COLOR
        )

        self.status_label.pack(
            pady=(10, 10)
        )

        # ----------------------------------------------------
        # RECORD BUTTONS
        # ----------------------------------------------------

        record_frame = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )

        record_frame.pack()

        self.record_button = tk.Button(
            record_frame,
            text="🔴  Enregistrer",
            command=self.app.start_recording,
            font=("Segoe UI", 11, "bold"),
            bg=RED,
            fg="white",
            activebackground="#c62828",
            width=18,
            height=2,
            relief="flat",
            cursor="hand2"
        )

        self.record_button.grid(
            row=0,
            column=0,
            padx=5
        )

        self.stop_record_button = tk.Button(
            record_frame,
            text="⏹  Arrêter",
            command=self.app.stop_recording,
            font=("Segoe UI", 11, "bold"),
            bg="#4a4a4a",
            fg="white",
            activebackground="#333333",
            width=18,
            height=2,
            relief="flat",
            state="disabled",
            cursor="hand2"
        )

        self.stop_record_button.grid(
            row=0,
            column=1,
            padx=5
        )

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        content = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )

        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(20, 0)
        )

        # ----------------------------------------------------
        # MACROS
        # ----------------------------------------------------

        left = tk.Frame(
            content,
            bg=BACKGROUND_COLOR
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        label = tk.Label(
            left,
            text="Mes macros",
            font=("Segoe UI", 13, "bold"),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )

        label.pack(
            anchor="w",
            pady=(0, 8)
        )

        list_frame = tk.Frame(
            left,
            bg=PANEL_COLOR
        )

        list_frame.pack(
            fill="both",
            expand=True
        )

        self.macro_list = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            selectbackground=BLUE,
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            activestyle="none"
        )

        self.macro_list.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0),
            pady=5
        )

        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.macro_list.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.macro_list.config(
            yscrollcommand=scrollbar.set
        )

        # ----------------------------------------------------
        # ACTION BUTTONS
        # ----------------------------------------------------

        actions = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )

        actions.pack(
            pady=10
        )
        # ----------------------------------------------------
        # REPEAT
        # ----------------------------------------------------

        repeat_frame = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )

        repeat_frame.pack(
            pady=(5, 0)
        )

        tk.Label(
            repeat_frame,
            text="Répétitions :",
            font=("Segoe UI", 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).pack(
            side="left",
            padx=(0, 6)
        )

        self.repeat_entry = tk.Entry(
            repeat_frame,
            width=6,
            justify="center",
            font=("Segoe UI", 10)
        )

        self.repeat_entry.insert(
            0,
            "1"
        )

        self.repeat_entry.pack(
            side="left"
        )

        tk.Label(
            repeat_frame,
            text="  (0 = ∞)",
            font=("Segoe UI", 9),
            bg=BACKGROUND_COLOR,
            fg=SECONDARY_TEXT_COLOR
        ).pack(
            side="left"
        )

        self.play_button = tk.Button(
            actions,
            text="▶  Jouer",
            command=self.app.play_selected_macro,
            font=("Segoe UI", 10, "bold"),
            bg=GREEN,
            fg="white",
            activebackground="#238b49",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2"
        )

        self.play_button.grid(
            row=0,
            column=0,
            padx=4
        )

        self.stop_play_button = tk.Button(
            actions,
            text="⏹  Stop",
            command=self.app.stop_playback,
            font=("Segoe UI", 10, "bold"),
            bg="#4a4a4a",
            fg="white",
            activebackground="#333333",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2"
        )

        self.stop_play_button.grid(
            row=0,
            column=1,
            padx=4
        )

        self.rename_button = tk.Button(
            actions,
            text="✏  Renommer",
            command=self.app.rename_macro,
            font=("Segoe UI", 10),
            bg=DARK_BUTTON,
            fg="white",
            activebackground="#505050",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2"
        )

        self.rename_button.grid(
            row=1,
            column=0,
            padx=4,
            pady=(7, 0)
        )

        self.delete_button = tk.Button(
            actions,
            text="🗑  Supprimer",
            command=self.app.delete_macro,
            font=("Segoe UI", 10),
            bg=DARK_BUTTON,
            fg="white",
            activebackground="#505050",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2"
        )

        self.delete_button.grid(
            row=1,
            column=1,
            padx=4,
            pady=(7, 0)
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        footer = tk.Label(
            self.root,
            text=(
                "F8  Enregistrer / arrêter"
                "     •     "
                "ESC  Arrêter la lecture"
            ),
            font=("Segoe UI", 9),
            bg=BACKGROUND_COLOR,
            fg="#777777"
        )

        footer.pack(
            pady=(0, 12)
        )

    # ========================================================
    # MACROS
    # ========================================================

    def refresh_macros(self):

        self.macro_list.delete(
            0,
            tk.END
        )

        for name in self.app.macro_manager.get_macros():

            self.macro_list.insert(
                tk.END,
                name
            )

    def get_selected_macro(self):

        selection = self.macro_list.curselection()

        if not selection:
            return None

        return self.macro_list.get(
            selection[0]
        )

    # ========================================================
    # DIALOGUES
    # ========================================================

    def ask_macro_name(self):

        return simpledialog.askstring(
            "Sauvegarder la macro",
            "Nom de la macro :",
            parent=self.root
        )

    def confirm(self, title, message):

        return messagebox.askyesno(
            title,
            message,
            parent=self.root
        )

    def warning(self, title, message):

        messagebox.showwarning(
            title,
            message,
            parent=self.root
        )

    def error(self, title, message):

        messagebox.showerror(
            title,
            message,
            parent=self.root
        )

    def get_repeat_count(self):

        try:
            value = int(
                self.repeat_entry.get().strip()
            )

            if value < 0:
                raise ValueError

            return value

        except ValueError:

            self.warning(
                "Nombre invalide",
                "Entre un nombre entier positif.\n\n"
                "Exemple : 5 = 5 lectures\n"
                "0 = lecture infinie"
            )

            return None
