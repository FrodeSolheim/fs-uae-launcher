import os
import shutil
import sys
import atexit
from configparser import ConfigParser, NoSectionError

import fsboot
from .signal import Signal
# noinspection PyUnresolvedReferences
from typing import Dict, Tuple


class Settings(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Settings()
        return cls._instance

    def __init__(self, app=None, path: str = None) -> None:
        self.app = app
        self.path = path
        self.values = {}  # type: Dict[str, str]
        self._provider = SettingsProvider()
        self._loaded = False
        self._loading = False
        self._atexit_registered = False
        self.verbose = True

    def set_path(self, path):
        self.path = path

    def set_provider(self, provider):
        self._provider = provider

    def get(self, key: str, default="") -> str:
        if not self._loading:
            self.load()
        return self.values.get(key, default)

    def set(self, key: str, value: str) -> None:
        if not self._loading:
            self.load()
        if self[key] == value:
            self.log_key_value(key, value, extra="(unchanged)")
            return
        if not self._loading and not self._atexit_registered:
            if self.verbose:
                print("[SETTINGS] Register atexit save path =", self.path)
            atexit.register(self.save)
            self._atexit_registered = True
        self.log_key_value(key, value)
        self.values[key] = value
        Signal("setting").notify(key, value)

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: str) -> None:
        self.set(key, value)

    def load(self, force=False):
        # print("[SETTINGS] Load", self)
        if (not self._loaded) or force:
            try:
                self._loading = True
                self._provider.load(self, verbose=self.verbose)
            finally:
                self._loading = False
        self._loaded = True
        # print("[SETTINGS] Loaded, path is", self.path)

    def save(self, extra: Dict[str, str] = None) -> None:
        if self.verbose:
            print("[SETTINGS] Save", self)
        self._provider.save(self, extra)

    def log_key_value(self, key, value, extra=""):
        if "username" in key or "password" in key or "auth" in key \
                or "email" in key:
            value = "*CENSORED*"
        if extra:
            extra = " " + extra
        if self.verbose:
            print("[SETTINGS] Set {} = {}{}".format(key, value, extra))


class SettingsProvider:
    """Provides default load and save behavior for Settings. You can subclass
    this and replace the provider on the Settings instance if you want
    customized loading/saving."""

    def load(self, settings, verbose=True):
        cp = ConfigParser(interpolation=None)
        cp.optionxform = str
        path = settings.path
        if settings.app and not path:
            path = settings.app.get_settings_path()
        if not path:
            if verbose:
                print("[SETTINGS] No settings path specified")
            path = os.path.join(fsboot.base_dir(), "Data", "Settings.ini")
            if verbose:
                print("[SETTINGS] Using default", path)
        if os.path.exists(path):
            if verbose:
                print("[SETTINGS] Loading from", path)
        else:
            if verbose:
                print("[SETTINGS] File", path, "does not exist")
        # Write current settings path back to Settings instance
        settings.path = path
        try:
            cp.read([path], encoding="UTF-8")
        except Exception as e:
            if verbose:
                print("[SETTINGS] Error loading", repr(e))
            return
        try:
            keys = cp.options("settings")
        except NoSectionError:
            return

        values = {}
        for key in sorted(keys):
            if key.startswith("__"):
                if verbose:
                    print("[SETTINGS] Ignoring", key)
                continue
            value = cp.get("settings", key)
            values[key] = value

        for arg in sys.argv:
            if arg.startswith("--settings:"):
                arg = arg[11:]
                key, value = arg.split("=", 1)
                key = key.replace("-", "_")
                values[key] = value

        for key in sorted(values.keys()):
            value = values[key]
            key = self.rewrite_key(key)
            settings.set(key, value)

    def rewrite_key(self, key):
        # FIXME: Should be moved to subclass
        try:
            return key_replacement_table[key]
        except KeyError:
            return key

    def save(self, settings, extra=None):
        partial_path = settings.path + ".partial"
        print("[SETTINGS] Writing to", partial_path)

        save_values = {}  # type: Dict[Tuple[str, str], str]
        for key, value in settings.values.items():
            if key.startswith("__"):
                # Temporary setting, do not save
                continue
            save_values[("settings", str(key))] = str(value)
        if extra is not None:
            for key, value in extra.items():
                try:
                    section, key = key.split("/")
                except ValueError:
                    section = "settings"
                save_values[(section, key)] = value

        cp = ConfigParser(interpolation=None)
        cp.optionxform = str
        # We want the settings section to be listed first.
        cp.add_section("settings")

        for (section, key) in sorted(save_values.keys()):
            value = save_values[(section, key)]
            if not value:
                # We do not need to write empty values, as non-existing
                # keys have an implicit empty value.
                continue
            if not cp.has_section(section):
                cp.add_section(section)
            cp.set(section, key, value)

        if not os.path.exists(os.path.dirname(partial_path)):
            os.makedirs(os.path.dirname(partial_path))
        with open(partial_path, "w", encoding="UTF-8", newline="\n") as f:
            cp.write(f)
        print("[SETTINGS] Moving to", settings.path)
        shutil.move(partial_path, settings.path)


def get(key: str) -> str:
    return Settings.instance().get(key)


def set(key: str, value: str) -> None:
    Settings.instance().set(key, value)


def load() -> None:
    Settings.instance().load()


def save() -> None:
    Settings.instance().save()


def unload() -> None:
    raise NotImplementedError("settings.unload")


def set_path(path: str) -> None:
    Settings.instance().set_path(path)


key_replacement_table = {
    "database_arcade": "arcade_database",
    "database_atari": "atari_database",
    "database_c64": "c64_database",
    "database_cpc": "cpc_database",
    "database_dos": "dos_database",
    "database_gb": "gb_database",
    "database_gba": "gba_database",
    "database_gbc": "gbc_database",
    "database_nes": "nes_database",
    "database_psx": "psx_database",
    "database_snes": "snes_database",
}
