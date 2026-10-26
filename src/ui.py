import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from PIL import Image, ImageTk

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

        self.root.resizable(
            False,
            False
        )

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

        self.macro_list.bind(
            "<<ListboxSelect>>",
            self.on_macro_selected
        )

        # ----------------------------------------------------
        # SCREENSHOTS
        # ----------------------------------------------------

        right = tk.Frame(
            content,
            bg=BACKGROUND_COLOR
        )

        right.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        screenshot_label = tk.Label(
            right,
            text="Screenshots / Checkpoints",
            font=("Segoe UI", 13, "bold"),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )

        screenshot_label.pack(
            anchor="w",
            pady=(0, 8)
        )

        self.playback_checkpoint_label = tk.Label(
            right,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg=BACKGROUND_COLOR,
            fg=BLUE,
            anchor="w",
            justify="left"
        )

        screenshot_frame = tk.Frame(
            right,
            bg=PANEL_COLOR
        )

        screenshot_frame.pack(
            fill="both",
            expand=True
        )

        self.screenshot_canvas = tk.Canvas(
            screenshot_frame,
            bg=PANEL_COLOR,
            highlightthickness=0
        )

        self.screenshot_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        screenshot_scrollbar = tk.Scrollbar(
            screenshot_frame,
            orient="vertical",
            command=self.screenshot_canvas.yview
        )

        screenshot_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.screenshot_canvas.configure(
            yscrollcommand=screenshot_scrollbar.set
        )

        self.screenshot_content = tk.Frame(
            self.screenshot_canvas,
            bg=PANEL_COLOR
        )

        self.screenshot_canvas.create_window(
            (0, 0),
            window=self.screenshot_content,
            anchor="nw"
        )

        self.screenshot_content.bind(
            "<Configure>",
            lambda event:
                self.screenshot_canvas.configure(
                    scrollregion=
                    self.screenshot_canvas.bbox("all")
                )
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
                "     •     "
                "+  Screenshot"
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
    # SELECTION
    # ========================================================

    def on_macro_selected(self, event=None):

        name = self.get_selected_macro()

        if not name:
            return

        self.show_screenshots(
            name
        )

    # ========================================================
    # SCREENSHOTS
    # ========================================================

    def clear_screenshots(self):

        self.playback_checkpoint_label.pack_forget()
        self.playback_checkpoint_label.config(text="")

        for widget in (
            self.screenshot_content
            .winfo_children()
        ):
            widget.destroy()

    def show_screenshots(self, name):

        self.clear_screenshots()

        macro = self.app.macro_manager.load_macro(
            name
        )

        if not macro:
            return

        screenshots = macro.get(
            "screenshots",
            []
        )

        if not screenshots:

            label = tk.Label(
                self.screenshot_content,
                text="Aucun screenshot associé",
                font=("Segoe UI", 10),
                bg=PANEL_COLOR,
                fg="#777777"
            )

            label.pack(
                pady=30
            )

            return

        screenshot_dir = os.path.join(
            self.app.macro_manager.get_macro_folder(name),
            "screenshots"
        )

        for index, screenshot in enumerate(
            screenshots,
            start=1
        ):

            item = tk.Frame(
                self.screenshot_content,
                bg=ITEM_COLOR
            )

            item.pack(
                fill="x",
                padx=8,
                pady=6
            )

            filename = screenshot.get(
                "filename",
                ""
            )

            image_path = os.path.join(
                screenshot_dir,
                filename
            )

            try:

                image = Image.open(
                    image_path
                )

                image.thumbnail(
                    (300, 160)
                )

                photo = ImageTk.PhotoImage(
                    image
                )

                image_label = tk.Label(
                    item,
                    image=photo,
                    bg=ITEM_COLOR
                )

                image_label.image = photo

                image_label.pack(
                    padx=8,
                    pady=(8, 5)
                )

            except Exception:

                tk.Label(
                    item,
                    text="Screenshot introuvable",
                    bg=ITEM_COLOR,
                    fg=RED
                ).pack(
                    pady=20
                )

            name = screenshot.get(
                "name",
                screenshot.get("description", "")
            )

            if not name:
                name = f"Screenshot {index}"

            tk.Label(
                item,
                text=name,
                font=("Segoe UI", 9, "bold"),
                bg=ITEM_COLOR,
                fg=BLUE,
                wraplength=300,
                justify="left"
            ).pack(
                padx=10,
                pady=(3, 5)
            )

            timestamp = screenshot.get(
                "time",
                0
            )

            tk.Label(
                item,
                text=f"⏱ {timestamp:.2f} s",
                font=("Segoe UI", 8),
                bg=ITEM_COLOR,
                fg="#888888"
            ).pack(
                pady=(0, 8)
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

    def ask_screenshot_name(self):

        return simpledialog.askstring(
            "Nom du checkpoint",
            "Nom du screenshot / checkpoint :",
            parent=self.root
        )

    # ========================================================
    # PLAYBACK CHECKPOINT
    # ========================================================

    def show_playback_checkpoint(self, screenshot):

        name = screenshot.get(
            "name",
            screenshot.get("description", "Screenshot")
        )

        timestamp = screenshot.get(
            "time",
            0
        )

        self.playback_checkpoint_label.config(
            text=f"▶ CHECKPOINT  •  {name}  •  ⏱ {timestamp:.2f} s"
        )

        self.playback_checkpoint_label.pack(
            anchor="w",
            fill="x",
            pady=(0, 8)
        )

        # Le checkpoint atteint est ajouté visuellement en tête
        # de la liste pour qu'on voie immédiatement où le PLAY en est.
        item = tk.Frame(
            self.screenshot_content,
            bg=ITEM_COLOR,
            highlightthickness=2,
            highlightbackground=BLUE
        )

        item.pack(
            fill="x",
            padx=8,
            pady=6,
            before=self.screenshot_content.winfo_children()[0]
            if self.screenshot_content.winfo_children()
            else None
        )

        screenshot_dir = os.path.join(
            self.app.macro_manager.get_macro_folder(
                self.get_selected_macro() or ""
            ),
            "screenshots"
        )

        filename = screenshot.get(
            "filename",
            ""
        )

        image_path = os.path.join(
            screenshot_dir,
            filename
        )

        try:
            image = Image.open(
                image_path
            )

            image.thumbnail(
                (300, 160)
            )

            photo = ImageTk.PhotoImage(
                image
            )

            image_label = tk.Label(
                item,
                image=photo,
                bg=ITEM_COLOR
            )

            image_label.image = photo
            image_label.pack(
                padx=8,
                pady=(8, 5)
            )

        except Exception:
            tk.Label(
                item,
                text="Screenshot introuvable",
                bg=ITEM_COLOR,
                fg=RED
            ).pack(
                pady=20
            )

        tk.Label(
            item,
            text=name,
            font=("Segoe UI", 10, "bold"),
            bg=ITEM_COLOR,
            fg=BLUE,
            wraplength=300
        ).pack(
            padx=10,
            pady=(3, 2)
        )

        tk.Label(
            item,
            text=f"⏱ {timestamp:.2f} s  •  checkpoint atteint",
            font=("Segoe UI", 8),
            bg=ITEM_COLOR,
            fg="#aaaaaa"
        ).pack(
            pady=(0, 8)
        )

        self.screenshot_canvas.update_idletasks()
        self.screenshot_canvas.yview_moveto(0)

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
