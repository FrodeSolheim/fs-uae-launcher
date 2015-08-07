import weakref
from fs_uae_launcher.Config import Config


class ConfigBehavior:

    def __init__(self, parent, names):
        parent.__amiga_enable_behavior = self
        self._parent = weakref.ref(parent)
        self._names = set(names)
        Config.add_listener(self)
        # FIXME
        # parent.destroyed.connect(self.on_destroy)

        # signal call for initial value
        for name in names:
            self.on_config(name, Config.get(name))

    def on_destroy(self, *args):
        Config.remove_listener(self)

    def on_config(self, key, value):
        if key in self._names:
            widget = self._parent()
            func = getattr(widget, "on_{0}_config".format(key))
            func(value)
