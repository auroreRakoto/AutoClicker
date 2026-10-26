import json
import os
import re
import shutil


class MacroManager:

    def __init__(self, macros_dir):
        self.macros_dir = macros_dir

        os.makedirs(
            self.macros_dir,
            exist_ok=True
        )

    # ========================================================
    # NOM DE FICHIER
    # ========================================================

    @staticmethod
    def sanitize_name(name):
        invalid_chars = '<>:"/\\|?*'

        for char in invalid_chars:
            name = name.replace(
                char,
                "_"
            )

        return name.strip()

    # ========================================================
    # CHEMINS
    # ========================================================

    def get_json_path(self, name):
        return os.path.join(
            self.macros_dir,
            f"{name}.json"
        )

    def get_macro_folder(self, name):
        return os.path.join(
            self.macros_dir,
            name
        )

    # ========================================================
    # LISTE
    # ========================================================

    def get_macros(self):
        macros = []

        for filename in os.listdir(
            self.macros_dir
        ):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(
                self.macros_dir,
                filename
            )

            try:
                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    macro = json.load(file)

                name = macro.get("name")

                if name:
                    macros.append(name)

            except Exception:
                continue

        return sorted(macros)

    # ========================================================
    # SAUVEGARDER
    # ========================================================

    def save_macro(
        self,
        name,
        actions,
        screenshots
    ):
        name = self.sanitize_name(
            name
        )

        if not name:
            raise ValueError(
                "Nom de macro invalide."
            )

        json_path = self.get_json_path(
            name
        )

        macro_folder = self.get_macro_folder(
            name
        )

        os.makedirs(
            macro_folder,
            exist_ok=True
        )

        # ----------------------------------------------------
        # SAUVEGARDER LES SCREENSHOTS
        # ----------------------------------------------------

        screenshot_dir = os.path.join(
            macro_folder,
            "screenshots"
        )

        os.makedirs(
            screenshot_dir,
            exist_ok=True
        )

        screenshot_metadata = []
        used_filenames = set()

        for screenshot in screenshots:

            raw_name = screenshot.get(
                "name",
                screenshot.get("description", "screenshot")
            )

            filename_base = self.sanitize_name(
                raw_name
            )

            filename_base = re.sub(
                r"\s+",
                "_",
                filename_base
            )

            filename_base = re.sub(
                r"_+",
                "_",
                filename_base
            )

            filename_base = filename_base.strip("._")

            if not filename_base:
                filename_base = "screenshot"

            filename = f"{filename_base}.png"
            suffix = 2

            while filename.lower() in used_filenames:
                filename = f"{filename_base}_{suffix}.png"
                suffix += 1

            used_filenames.add(filename.lower())

            image_path = os.path.join(
                screenshot_dir,
                filename
            )

            screenshot["image"].save(
                image_path,
                "PNG"
            )

            screenshot_metadata.append({
                "filename": filename,
                "name": raw_name,
                "time": screenshot.get("time", 0)
            })

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        macro = {
            "version": 2,
            "name": name,
            "actions": actions,
            "screenshots": screenshot_metadata
        }

        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                macro,
                file,
                indent=4,
                ensure_ascii=False
            )

        return macro

    # ========================================================
    # CHARGER
    # ========================================================

    def load_macro(self, name):

        path = self.get_json_path(
            name
        )

        if not os.path.exists(path):
            return None

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:
            return None

    # ========================================================
    # RENOMMER
    # ========================================================

    def rename_macro(
        self,
        old_name,
        new_name
    ):
        new_name = self.sanitize_name(
            new_name
        )

        if not new_name:
            raise ValueError(
                "Nom invalide."
            )

        if old_name == new_name:
            return

        old_json = self.get_json_path(
            old_name
        )

        new_json = self.get_json_path(
            new_name
        )

        old_folder = self.get_macro_folder(
            old_name
        )

        new_folder = self.get_macro_folder(
            new_name
        )

        if os.path.exists(new_json):
            raise FileExistsError(
                "Une macro porte déjà ce nom."
            )

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        os.rename(
            old_json,
            new_json
        )

        # ----------------------------------------------------
        # DOSSIER SCREENSHOTS
        # ----------------------------------------------------

        if os.path.exists(old_folder):

            os.rename(
                old_folder,
                new_folder
            )

        # ----------------------------------------------------
        # METTRE À JOUR LE JSON
        # ----------------------------------------------------

        macro = self.load_macro(
            new_name
        )

        if macro:

            macro["name"] = new_name

            with open(
                new_json,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    macro,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

    # ========================================================
    # SUPPRIMER
    # ========================================================

    def delete_macro(self, name):

        json_path = self.get_json_path(
            name
        )

        macro_folder = self.get_macro_folder(
            name
        )

        if os.path.exists(json_path):
            os.remove(json_path)

        if os.path.exists(macro_folder):
            shutil.rmtree(
                macro_folder
            )
