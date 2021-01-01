import weakref


class OptionsBehavior:
    def __init__(self, parent, options, names):
        """

        :param parent:
        :param options: LauncherConfig or LauncherSettings, or similar.
        :param names:
        """
        self.options = options
        parent.__options_enable_behavior = self
        self._parent = weakref.ref(parent)
        self._names = set(names)
        self.options.add_listener(self)

        # FIXME: We need to disconnect the listener
        parent.destroyed.connect(self.__on_parent_destroyed)

        # signal call for initial value
        for name in names:
            self.on_config(name, self.options.get(name))

    def on_config(self, key, value):
        self.on_option(key, value)

    def on_option(self, key, value):
        if key in self._names:
            widget = self._parent()
            func = getattr(widget, "on_{0}_option".format(key))
            func(value)

    def __on_parent_destroyed(self, *_):
        self.options.remove_listener(self)

    def on_settings(self, key, value):
        self.on_option(key, value)
