import weakref
from launcher.launcher_settings import LauncherSettings


class SettingsBehavior:
    def __init__(self, parent, names):
        parent.__settings_enable_behavior = self
        self._parent = weakref.ref(parent)
        self._names = set(names)
        LauncherSettings.add_listener(self)
        try:
            parent.destroyed.connect(self.on_parent_destroyed)
        except AttributeError:
            print(
                "WARNING: SettingsBehavior without remove_listener "
                "implementation"
            )
        for name in names:
            # Broadcast initial value
            self.on_setting(name, LauncherSettings.get(name))

    def on_parent_destroyed(self):
        print("SettingsBehavior: remove_listener", self._parent())
        LauncherSettings.remove_listener(self)

    def on_setting(self, key, value):
        if key in self._names:
            widget = self._parent()
            try:
                func = getattr(widget, "on_{0}_setting".format(key))
            except AttributeError:
                func = getattr(widget, "on_settings".format(key))
                func(key, value)
            else:
                func(value)
