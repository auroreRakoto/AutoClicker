import threading
import tkinter as tk

from pynput import keyboard

from config import MACROS_DIR

from macros import MacroManager
from recorder import Recorder
from player import MacroPlayer
from screenshots import ScreenshotManager
from ui import MacroUI


class MacroRecorderApp:

    def __init__(self, root):

        self.root = root

        # ====================================================
        # SERVICES
        # ====================================================

        self.macro_manager = MacroManager(
            MACROS_DIR
        )

        self.recorder = Recorder(
            on_status=self.set_status
        )

        self.player = MacroPlayer(
            root=self.root,
            on_status=self.set_status,
            on_checkpoint=self.on_playback_checkpoint
        )

        self.screenshot_manager = ScreenshotManager(
            root=self.root,
            recorder=self.recorder,
            ask_name=self.ask_screenshot_name,
            on_status=self.set_status
        )

        # ====================================================
        # INTERFACE
        # ====================================================

        self.ui = MacroUI(
            root=self.root,
            app=self
        )

        # ====================================================
        # CALLBACKS
        # ====================================================

        self.recorder.set_stop_callback(
            self.on_recording_stopped
        )

        # ====================================================
        # RACCOURCIS GLOBAUX
        # ====================================================

        self.hotkey_listener = keyboard.Listener(
            on_press=self.global_key_press
        )

        self.hotkey_listener.start()

        # ====================================================
        # LISTENERS ENREGISTREMENT
        # ====================================================

        self.recorder.start_listeners()

        # ====================================================
        # MACROS
        # ====================================================

        self.ui.refresh_macros()

        # ====================================================
        # FERMETURE
        # ====================================================

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text,
        color="#aaaaaa"
    ):
        self.root.after(
            0,
            lambda: self.ui.set_status(
                text,
                color
            )
        )

    # ========================================================
    # ENREGISTREMENT
    # ========================================================

    def start_recording(self):

        if self.recorder.recording:
            return

        if self.player.playing:

            self.ui.warning(
                "Lecture en cours",
                "Arrête la lecture avant de commencer un enregistrement."
            )

            return

        self.screenshot_manager.clear()

        self.recorder.start()

        self.ui.record_button.config(
            state="disabled"
        )

        self.ui.stop_record_button.config(
            state="normal"
        )

    def stop_recording(self):

        if not self.recorder.recording:
            return

        self.recorder.stop()

        self.ui.record_button.config(
            state="normal"
        )

        self.ui.stop_record_button.config(
            state="disabled"
        )

    def on_recording_stopped(
        self,
        actions
    ):

        if not actions:

            self.set_status(
                "● Aucune action enregistrée",
                "#ff9800"
            )

            return

        self.save_current_macro(
            actions
        )

    # ========================================================
    # SAUVEGARDE
    # ========================================================

    def save_current_macro(
        self,
        actions
    ):

        name = self.ui.ask_macro_name()

        if not name:

            self.set_status(
                "● Macro non sauvegardée",
                "#ff9800"
            )

            return

        name = self.macro_manager.sanitize_name(
            name
        )

        if not name:

            self.ui.warning(
                "Nom invalide",
                "Le nom de la macro est invalide."
            )

            return

        existing = (
            self.macro_manager.load_macro(name)
        )

        if existing:

            overwrite = self.ui.confirm(
                "Macro existante",
                (
                    f"La macro « {name} » existe déjà.\n\n"
                    "Voulez-vous la remplacer ?"
                )
            )

            if not overwrite:
                return

        try:

            self.macro_manager.save_macro(
                name=name,
                actions=actions,
                screenshots=self.screenshot_manager.screenshots
            )

        except Exception as error:

            self.ui.error(
                "Erreur",
                (
                    "Impossible de sauvegarder "
                    f"la macro.\n\n{error}"
                )
            )

            return

        self.ui.refresh_macros()

        self.set_status(
            (
                f"● Macro sauvegardée : {name}"
                f" — "
                f"{len(self.screenshot_manager.screenshots)} "
                f"screenshot"
            ),
            "#4caf50"
        )

    # ========================================================
    # SCREENSHOT
    # ========================================================

    def take_screenshot(self):

        if not self.recorder.recording:
            return

        try:

            self.screenshot_manager.capture()

        except Exception as error:

            self.ui.error(
                "Erreur screenshot",
                str(error)
            )

    def ask_screenshot_name(self):

        return self.ui.ask_screenshot_name()

    def on_playback_checkpoint(self, screenshot):
        """Affiche le checkpoint au moment prévu pendant le PLAY."""
        self.ui.show_playback_checkpoint(
            screenshot
        )

    # ========================================================
    # LECTURE
    # ========================================================

    def play_selected_macro(self):

        if self.recorder.recording:

            self.ui.warning(
                "Enregistrement en cours",
                "Arrête l'enregistrement avant de lancer une macro."
            )

            return

        if self.player.playing:
            return

        name = self.ui.get_selected_macro()

        if not name:

            self.ui.warning(
                "Aucune macro",
                "Sélectionne une macro dans la liste."
            )

            return

        macro = self.macro_manager.load_macro(
            name
        )

        if not macro:

            self.ui.error(
                "Erreur",
                "Impossible de charger la macro."
            )

            return

        repeat_count = self.ui.get_repeat_count()

        if repeat_count is None:
            return

        thread = threading.Thread(
            target=self.player.play,
            args=(macro, repeat_count),
            daemon=True
        )

        thread.start()

    def stop_playback(self):

        self.player.stop()

    # ========================================================
    # RENOMMER
    # ========================================================

    def rename_macro(self):

        old_name = self.ui.get_selected_macro()

        if not old_name:

            self.ui.warning(
                "Aucune macro",
                "Sélectionne une macro."
            )

            return

        new_name = self.ui.ask_macro_name()

        if not new_name:
            return

        try:

            self.macro_manager.rename_macro(
                old_name,
                new_name
            )

        except FileExistsError:

            self.ui.warning(
                "Nom déjà utilisé",
                "Une macro porte déjà ce nom."
            )

            return

        except Exception as error:

            self.ui.error(
                "Erreur",
                str(error)
            )

            return

        self.ui.refresh_macros()

        self.ui.clear_screenshots()

        self.set_status(
            f"● Macro renommée : {new_name}",
            "#4caf50"
        )

    # ========================================================
    # SUPPRIMER
    # ========================================================

    def delete_macro(self):

        name = self.ui.get_selected_macro()

        if not name:

            self.ui.warning(
                "Aucune macro",
                "Sélectionne une macro."
            )

            return

        confirmation = self.ui.confirm(
            "Supprimer",
            f"Supprimer la macro « {name} » ?"
        )

        if not confirmation:
            return

        try:

            self.macro_manager.delete_macro(
                name
            )

        except Exception as error:

            self.ui.error(
                "Erreur",
                str(error)
            )

            return

        self.ui.refresh_macros()

        self.ui.clear_screenshots()

        self.set_status(
            f"● Macro supprimée : {name}",
            "#ff9800"
        )

    # ========================================================
    # RACCOURCIS GLOBAUX
    # ========================================================

    def global_key_press(self, key):

        try:

            # ------------------------------------------------
            # ESC → STOP LECTURE
            # ------------------------------------------------

            if key == keyboard.Key.esc:

                if self.player.playing:

                    self.root.after(
                        0,
                        self.stop_playback
                    )

                return

            # ------------------------------------------------
            # F8 → RECORD
            # ------------------------------------------------

            if key == keyboard.Key.f8:

                if self.recorder.recording:

                    self.root.after(
                        0,
                        self.stop_recording
                    )

                else:

                    self.root.after(
                        0,
                        self.start_recording
                    )

                return

            # ------------------------------------------------
            # + → SCREENSHOT
            # ------------------------------------------------

            try:

                value = key.char

                if (
                    value == "+"
                    and self.recorder.recording
                ):

                    self.root.after(
                        0,
                        self.take_screenshot
                    )

            except AttributeError:
                pass

        except Exception:
            pass

    # ========================================================
    # FERMETURE
    # ========================================================

    def close(self):

        self.player.stop()

        self.recorder.stop_listeners()

        if self.hotkey_listener:
            self.hotkey_listener.stop()

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    MacroRecorderApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
