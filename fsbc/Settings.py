import os
import shutil
from .signal import Signal
from configparser import ConfigParser, NoSectionError
# noinspection PyUnresolvedReferences
from typing import Dict, Tuple


class Settings(object):

    def __init__(self, app=None, path: str=None) -> None:
        self.app = app
        self.path = path
        self.values = {}  # type: Dict[str, str]
        self.load()

    def get(self, key: str) -> str:
        return self.values.get(key, "")

    def set(self, key: str, value: str) -> None:
        if self[key] == value:
            print("set {0} to {1} (no change)".format(key, value))
            return
        _log_key_value(key, value)
        self.values[key] = value
        Signal("setting").notify(key, value)

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: str) -> None:
        self.set(key, value)

    def load(self):
        cp = ConfigParser(interpolation=None)
        path = self.path or self.app.get_settings_path()
        if os.path.exists(path):
            print("loading settings from", path)
        else:
            print("settings file", path, "does not exist")
        try:
            cp.read([path], encoding="UTF-8")
        except Exception as e:
            print(repr(e))
            return
        try:
            keys = cp.options("settings")
        except NoSectionError:
            return

        for key in keys:
            value = cp.get(""
                           "settings", key)
            print(key, value)
            self.values[key] = value

    def save(self, extra: Dict[str, str]=None) -> None:
        partial_path = self.path + ".partial"
        print("writing settings to", partial_path)

        save_values = {}  # type: Dict[Tuple[str, str], str]
        for key, value in self.values.items():
            save_values[("settings", str(key))] = str(value)
        if extra is not None:
            for key, value in extra.items():
                try:
                    section, key = key.split("/")
                except ValueError:
                    section = "settings"
                save_values[(section, key)] = value

        cp = ConfigParser(interpolation=None)
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

        with open(partial_path, "w", encoding="UTF-8", newline="\n") as f:
            cp.write(f)
        print("moving settings file to", self.path)
        shutil.move(partial_path, self.path)


_path = ""
_settings = None  # type: Settings


def get(key: str) -> str:
    load()
    return _settings.get(key)


def set(key: str, value: str) -> None:
    load()
    _settings.set(key, value)


def load() -> None:
    global _settings
    if not _settings:
        assert _path
        _settings = Settings(path=_path)


def save() -> None:
    assert _path
    _settings.save()


def unload() -> None:
    global _settings
    _settings = None


def set_path(path: str) -> None:
    global _path
    _path = path


def _log_key_value(key, value):
    if "username" in key or "password" in key or "auth" in key \
            or "email" in key:
        print("set {0} to *CENSORED*".format(key))
    else:
        print("set {0} to {1}".format(key, value))
