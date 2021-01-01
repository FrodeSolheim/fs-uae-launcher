import weakref

from launcher.context import get_config


class ConfigBehavior:
    def __init__(self, parent, names):
        parent.__config_enable_behavior = self
        self._parent = weakref.ref(parent)
        self._names = set(names)
        get_config(parent).add_listener(self)
        try:
            parent.destroyed.connect(self.on_parent_destroyed)
        except AttributeError:
            print(
                "WARNING: ConfigBehavior without remove_listener "
                "implementation"
            )
        for name in names:
            # Broadcast initial value
            self.on_config(name, get_config(parent).get(name))

    def on_parent_destroyed(self):
        print("ConfigBehavior: remove_listener", self._parent())
        get_config(self._parent()).remove_listener(self)

    def on_config(self, key, value):
        if key in self._names:
            widget = self._parent()
            func = getattr(widget, "on_{0}_config".format(key))
            func(value)
