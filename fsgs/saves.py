import os
import shutil
import warnings
from configparser import ConfigParser

from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.GameChangeHandler import GameChangeHandler
from fsgs.util.gamenameutil import GameNameUtil

"""
TODO: Snapshots support. Create a Snapshots/TimeTDate/ directory with a 
copy of the state dir!
"""


class SaveHandler(object):
    def __init__(
        self,
        fsgc,
        name="",
        platform="Unknown",
        uuid=None,
        options=None,
        emulator="",
    ):
        self.fsgc = fsgc
        # FIXME: SaveHandler(fsgc, options=options) is new usage?
        self._options = options
        self._emulator_specific = False
        self._emulator_name = emulator

        self.uuid = uuid
        self.change_handlers = []

        self.config_name = name
        if "(" in name:
            parts = name.split("(", 1)
            self.name, self.variant = parts
            self.name = self.name.strip()
            self.variant = self.variant.strip()
            if self.variant.endswith(")"):
                self.variant = self.variant[:-1]
            self.variant = self.variant.replace(") (", ", ")
            self.variant = self.variant.replace(")(", ", ")
        else:
            self.name = name
            self.variant = ""
        self.platform = platform

    def set_save_data_is_emulator_specific(self, emulator_specific=True):
        self._emulator_specific = emulator_specific

    def get(self, name):
        if self._options is not None:
            return self._options.get(name, "")
        value = self.fsgc.config.get(name, "")
        if not value:
            value = self.fsgc.settings.get(name, "")
        return value

    def register_changes(self, original_dir, changes_dir):
        self.change_handlers.append(
            (GameChangeHandler(original_dir), changes_dir)
        )

    def prepare(self):
        self.create_save_ini()
        for change_handler, changes_dir in self.change_handlers:
            change_handler.init(changes_dir)

    def create_save_ini(self):
        save_dir = self.base_save_dir()
        save_ini_path = os.path.join(save_dir, "Save.ini")

        cp = ConfigParser()
        if os.path.exists(save_ini_path):
            with open(save_ini_path, "r", encoding="UTF-8") as f:
                cp.read(f)

        if not cp.has_section("fsgs-save"):
            cp.add_section("fsgs-save")
        cp.set("fsgs-save", "version", "2")
        cp.set("fsgs-save", "platform", self.get("platform"))
        cp.set("fsgs-save", "game_uuid", self.get("game_uuid"))
        cp.set("fsgs-save", "game_name", self.get("game_name"))
        cp.set("fsgs-save", "variant_uuid", self.get("variant_uuid"))
        cp.set("fsgs-save", "variant_name", self.get("variant_name"))

        with open(save_ini_path + ".partial", "w", encoding="UTF-8") as f:
            cp.write(f)
        os.replace(save_ini_path + ".partial", save_ini_path)

    def base_save_dir(self):
        save_dir = self.save_dir_path()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        return save_dir

    def save_dir(self):
        return self.base_save_dir()

    def emulator_state_dir(self, name=""):
        emulator = name or self._emulator_name
        assert emulator
        save_state_directory = os.path.join(self.base_save_dir(), emulator)
        if not os.path.exists(save_state_directory):
            os.makedirs(save_state_directory)
        return save_state_directory

    def emulator_save_dir(self, name=""):
        emulator = name or self._emulator_name
        if self._emulator_specific:
            return self.emulator_state_dir(emulator)
        else:
            return self.base_save_dir()

    def uuid_save_dir_path(self):
        saves_dir = FSGSDirectories.saves_dir()
        # FIXME: Correct?
        variant_uuid = self.get("variant_uuid")
        if variant_uuid:
            save_dir = os.path.join(
                saves_dir, "UUID", variant_uuid[:2], variant_uuid
            )
            return save_dir
        return None

    def save_dir_path(self):
        save_dir = self.uuid_save_dir_path()
        if save_dir:
            return save_dir
        # saves_dir = FSGSDirectories.saves_dir()
        assert False, "save_dir_path not implemented for this case"

    def finish(self):
        for change_handler, changes_dir in self.change_handlers:
            change_handler.update(changes_dir)
        self.cleanup()

    def cleanup(self):
        save_dir = self.save_dir_path()
        print("[SAVES] Cleanup", save_dir)
        if not os.path.exists(save_dir):
            print("[SAVES] Save dir does not exist, no need to clean up")
            return
        erase = True
        for dir_path, dir_name, file_names in os.walk(save_dir):
            for file_name in file_names:
                if file_name != "Save.ini":
                    erase = False
        if not erase:
            print("[SAVES] Save data found, will not erase save dir")
            for item in os.listdir(save_dir):
                sub_dir = os.path.join(save_dir, item)
                if os.path.isdir(sub_dir):
                    self.cleanup_sub_dir(sub_dir)
            return
        print("[SAVES] No save data found, erasing save dir!")
        shutil.rmtree(save_dir)
        # FIXME: Remove UUID/XX dir if empty?

    def cleanup_sub_dir(self, sub_dir):
        """Check if there are any files in this directory sub tree. If not,
        then remove the directory."""
        for dir_path, dir_name, file_names in os.walk(sub_dir):
            for _ in file_names:
                # At least one file was found
                return
        print("[SAVES] Removing empty dir:", sub_dir)
        shutil.rmtree(sub_dir)

    # -------------------------------------------------------------- legacy ---

    @property
    def fsgs(self):
        warnings.warn("Use .fsgc instead", DeprecationWarning)
        return self.fsgc

    def get_name(self):
        # warnings.warn("Use .name instead", DeprecationWarning)
        return self.name

    def get_variant(self):
        # warnings.warn("Use .variant instead", DeprecationWarning)
        return self.variant

    def _get_state_dir(self):
        config_name = self.config_name
        if not config_name:
            config_name = "Default"

        # Use a temporary state dir, for now, to avoid problems with
        # floppy overlays etc interfering with net play.
        if self.fsgc.netplay.enabled:
            # It is possible to manually specify the state dir.
            config_name = self.fsgc.config.get("__netplay_state_dir_name")
            if not config_name:
                # This is the default behavior, create a clean state
                # dir for the net play session.
                netplay_game = self.fsgc.config.get("__netplay_game")
                if netplay_game:
                    config_name = "Net Play ({0})".format(netplay_game)

        # Convert the config name to a name which can be represented on
        # the file system (really all/most filesystems).
        config_name = GameNameUtil.create_fs_name(config_name)

        letter = self.get_letter(config_name)
        if not letter:
            config_name = "Default"
            letter = self.get_letter(config_name)
        # We use an existing state dir in a "letter" dir if it already
        # exists (legacy support).
        path = os.path.join(
            FSGSDirectories.get_save_states_dir(), letter, config_name
        )
        if os.path.exists(path):
            return path
        # If not, we use a direct sub-folder of save states dir.
        path = os.path.join(FSGSDirectories.get_save_states_dir(), config_name)
        return path

    def get_state_dir(self):
        state_dir = self._get_state_dir()
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        return state_dir

    @staticmethod
    def get_letter(name):
        letter_name = name.upper()
        if letter_name.startswith("THE "):
            letter_name = letter_name[4:]
        if letter_name.startswith("A "):
            letter_name = letter_name[2:]
        for i in range(len(letter_name)):
            letter = letter_name[i]
            if letter in "01234567890":
                letter = "0"
                break
            if letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                break
        else:
            return None
        return letter
