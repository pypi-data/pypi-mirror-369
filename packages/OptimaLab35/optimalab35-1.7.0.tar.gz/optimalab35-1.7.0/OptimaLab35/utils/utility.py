import yaml
import os

class Utilities:
    def __init__(self, app_folder_path):
        self.folder_path = os.path.expanduser(app_folder_path)
        self._ensure_program_folder_exists()
        self.exif_path = os.path.expanduser(f"{app_folder_path}/exif.yaml")
        self.settings_path = os.path.expanduser(f"{app_folder_path}/settings.yaml")
        self._prepear_exif_config()

    def read_yaml(self, yaml_file):
        try:
            with open(yaml_file, "r") as file:
                data = yaml.safe_load(file)
                return data
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error loading settings file: {e}")
            return None

    def write_yaml(self, yaml_file, data):
        try:
            with open(yaml_file, "w") as file:
                yaml.dump(data, file)
            return True
        except PermissionError as e:
            print(f"Error saving setings: {e}")
            return False

    def _prepear_exif_config(self):
        """Prepear folder for config and generate default exif if non aviable"""
        if not os.path.isfile(self.exif_path):
            self.default_exif()

    def _ensure_program_folder_exists(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def load_settings(self):
            """Loads settings from file, or creates default settings if missing."""
            if os.path.exists(self.settings_path):
                settings = self.read_yaml(self.settings_path)
                return settings if settings else self._default_settings()
            return self._default_settings()

    def save_settings(self, settings):
        if not self.write_yaml(self.settings_path, settings):
            print("Error writing file")

    def adjust_exif_after_update(self):
        """Adds new info the exif file after an update if needed"""
        new_lst = ["developer", "time"] # for update from 1.5 to 1.6

        current_lst = []
        exif = self.read_yaml(self.exif_path)
        for key in exif:
            current_lst.append(key)

        if all(item in current_lst for item in new_lst):
            return
        else:
            print("Adding new exif data after update from 1.5")
            exif["time"] = ["NA", "7:30", "10:00"]
            exif["developer"] = ["NA", "Kodac HC-110 1:31", "Kodac HC-110 1:63"]
            self.write_yaml(self.exif_path, exif)

    def default_exif(self):
        """Makes a default exif file."""
        print("Making default")
        def_exif = {
            "artist": [
                "Mr Finchum",
                "John Doe"
            ],
            "copyright_info": [
                "All Rights Reserved",
                "CC BY-NC 4.0",
                "No Copyright"
            ],
            "image_description": [
                "ILFORD DELTA 3200",
                "ILFORD ILFOCOLOR",
                "LomoChrome Turquoise",
                "Kodak 200"
            ],
            "iso": [
                "200",
                "400",
                "1600",
                "3200"
            ],
            "lens": [
                "Nikon LENS SERIES E 50mm",
                "AF NIKKOR 35-70mm",
                "Canon FD 50mm f/1.4 S.S.C"
            ],
            "make": [
                "Nikon",
                "Canon"
            ],
            "model": [
                "FG",
                "F50",
                "AE-1"
            ],
            "user_comment": [
                "Scanner: NORITSU-KOKI",
                "Scanner: NA"
            ],
            "developer": [
                "Kodak HC-110 1:31",
                "Kodak HC-110 1:63"
            ],
            "time": [
                "NA",
                "7:00",
                "10:00"
            ]
        }
        self.write_yaml(self.exif_path, def_exif)

    def _default_settings(self):
            """Returns default settings and writes them if the settings file does not exist."""
            settings = {
                "theme": {
                    "theme_pkg": False,
                    "use_custom_theme": False,
                    "mode": "Auto"
                }
            }
            self.write_yaml(self.settings_path, settings)
            return settings

    def append_number_to_name(self, base_name: str, current_image: int, total_images: int, invert: bool):
            """"Returns name, combination of base_name and ending number."""
            total_digits = len(str(total_images))
            if invert:
                ending_number = total_images - (current_image - 1)
            else:
                ending_number = current_image
            ending = f"{ending_number:0{total_digits}}"
            return f"{base_name}_{ending}"
