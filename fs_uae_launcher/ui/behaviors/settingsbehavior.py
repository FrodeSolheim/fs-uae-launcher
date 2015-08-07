import weakref
from fs_uae_launcher.Settings import Settings


class SettingsBehavior:

    def __init__(self, parent, names):
        parent.__amiga_enable_behavior = self
        self._parent = weakref.ref(parent)
        self._names = set(names)
        Settings.add_listener(self)
        # FIXME
        # parent.destroyed.connect(self.on_destroy)

        # signal call for initial value
        for name in names:
            self.on_setting(name, Settings.get(name))

    def on_destroy(self, *args):
        Settings.remove_listener(self)

    def on_setting(self, key, value):
        if key in self._names:
            widget = self._parent()
            func = getattr(widget, "on_{0}_setting".format(key))
            func(value)
