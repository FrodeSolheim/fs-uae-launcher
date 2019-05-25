import traceback
import weakref

import fsui
from fsbc.util import unused
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.ui.config.expand import expand_config, AbstractExpandFunctions
from launcher.ui.config.model import ImplicitConfig, normalize


class ImplicitConfigHandler:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)
        LauncherConfig.add_listener(self)
        LauncherSettings.add_listener(self)
        self.dirty = True
        self.do_update()
        parent.destroyed.connect(self.on_parent_destroyed)

    def on_parent_destroyed(self):
        print("ImplicitConfigHandler.on_parent_destroyed")
        LauncherConfig.remove_listener(self)
        LauncherSettings.remove_listener(self)

    def update(self):
        self.dirty = True
        fsui.call_after(self.do_update)

    def do_update(self):
        if not self.dirty:
            return
        self.dirty = False
        # print("ImplicitConfigHandler.do_update")
        implicit = ImplicitConfig(ConfigProxy(), SettingsProxy())
        # failed = False
        try:
            expand_config(implicit, ExpandFunctions())
        except Exception:
            traceback.print_exc()
            print("expand_config failed")
            # failed = True
        implicit_config = {
            key: ""
            for key in LauncherConfig.keys()
            if key.startswith("__implicit_")
        }
        for key, value in implicit.items():
            implicit_config["__implicit_" + key] = value
        LauncherConfig.set_multiple(list(implicit_config.items()))

        if self.parent().config_browser:
            self.parent().config_browser.update_from_implicit(implicit)

    def on_config(self, key, value):
        if key.startswith("__implicit_"):
            # The implicit key/values are already set by us.
            return
        unused(value)
        self.update()

    def on_setting(self, key, value):
        unused(key)
        unused(value)
        self.update()


class SettingsProxy:
    @staticmethod
    def get(key):
        return LauncherSettings.get(key)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        LauncherSettings.set(key, value)


class ConfigProxy:
    @staticmethod
    def get(key):
        return LauncherConfig.get(key)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        LauncherConfig.set(key, value)


class ExpandFunctions(AbstractExpandFunctions):
    @staticmethod
    def matches(a, b):
        a = normalize(a)
        if isinstance(b, list):
            for b_item in b:
                if a == normalize(b_item):
                    return True
            return False
        return a == normalize(b)

    @staticmethod
    def fail(message):
        pass

    @staticmethod
    def warning(message):
        # warnings.append(message)
        pass

    @staticmethod
    def lower(s):
        return s.lower()
