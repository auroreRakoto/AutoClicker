import os
import re

from PIL import ImageGrab


class ScreenshotManager:
    """
    Gère les screenshots associés aux macros.
    """

    def __init__(
        self,
        root,
        recorder,
        ask_name,
        on_status=None
    ):
        self.root = root
        self.recorder = recorder
        self.ask_name = ask_name
        self.on_status = on_status

        self.screenshots = []

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, text, color="#aaaaaa"):
        if self.on_status:
            self.on_status(text, color)

    # ========================================================
    # RESET
    # ========================================================

    def clear(self):
        self.screenshots = []

    # ========================================================
    # CAPTURE
    # ========================================================

    def capture(self):
        """
        Pause l'enregistrement,
        capture l'écran,
        demande une description,
        puis reprend.
        """

        if not self.recorder.recording:
            return

        if self.recorder.paused:
            return

        # ----------------------------------------------------
        # TEMPS AVANT LA PAUSE
        # ----------------------------------------------------

        timestamp = self.recorder.get_elapsed_time()

        # ----------------------------------------------------
        # PAUSE
        # ----------------------------------------------------

        self.recorder.pause()

        self.set_status(
            "⏸ Pause — capture du screenshot...",
            "#ff9800"
        )

        # ----------------------------------------------------
        # CAPTURE
        # ----------------------------------------------------

        try:
            image = ImageGrab.grab()

        except Exception as error:

            self.recorder.resume()

            self.set_status(
                "● Enregistrement en cours...",
                "#ff5252"
            )

            raise RuntimeError(
                f"Impossible de capturer l'écran : {error}"
            )

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        name = self.ask_name()

        if name is None:
            name = ""

        name = name.strip()

        if not name:
            self.recorder.resume()
            self.set_status(
                "● Screenshot annulé — enregistrement en cours...",
                "#ff9800"
            )
            return

        # ----------------------------------------------------
        # STOCKAGE
        # ----------------------------------------------------

        self.screenshots.append({
            "image": image,
            "name": name,
            "time": timestamp
        })

        # ----------------------------------------------------
        # REPRISE
        # ----------------------------------------------------

        self.recorder.resume()

        count = len(self.screenshots)

        self.set_status(
            (
                "● Enregistrement en cours... "
                f"({count} screenshot"
                f"{'s' if count > 1 else ''})"
            ),
            "#ff5252"
        )

    # ========================================================
    # SAUVEGARDE
    # ========================================================

    @staticmethod
    def sanitize_filename(name):
        """Transforme le nom du checkpoint en nom de fichier sûr."""
        name = re.sub(r'[<>:"/\\|?*]', "_", name)
        name = re.sub(r"\s+", "_", name.strip())
        name = re.sub(r"_+", "_", name)
        return name.strip("._") or "screenshot"

    # ========================================================
    # SAUVEGARDE
    # ========================================================

    def save_to_folder(self, folder):
        """
        Sauvegarde les screenshots avec leur nom de checkpoint.

        Retourne les métadonnées JSON contenant le nom, le fichier
        et le timestamp utilisé pendant la lecture.
        """

        screenshot_dir = os.path.join(
            folder,
            "screenshots"
        )

        os.makedirs(
            screenshot_dir,
            exist_ok=True
        )

        metadata = []
        used_filenames = set()

        for screenshot in self.screenshots:

            base_name = self.sanitize_filename(
                screenshot.get("name", "screenshot")
            )

            filename = f"{base_name}.png"
            suffix = 2

            while filename.lower() in used_filenames:
                filename = f"{base_name}_{suffix}.png"
                suffix += 1

            used_filenames.add(filename.lower())

            path = os.path.join(
                screenshot_dir,
                filename
            )

            screenshot["image"].save(
                path,
                "PNG"
            )

            metadata.append({
                "filename": filename,
                "name": screenshot.get("name", ""),
                "time": screenshot.get("time", 0)
            })

        return metadata
