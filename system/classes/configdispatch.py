from fsgamesys.config.configevent import ConfigEvent
from launcher.context import get_config


class ConfigDispatch:
    def __init__(self, parent, mapping):
        self.parent = parent
        self.mapping = mapping
        config = get_config(self.parent)
        config.attach(self)
        self.parent.destroyed.connect(self.__parent_destroyed)
        # Broadcast existing state as updates to make life easier for
        # observers.
        for key in mapping:
            self.mapping[key](ConfigEvent(key, config.get(key)))
        # Keep this dispatcher alive by storing a reference on the parent.
        setattr(self.parent, f"_config_dispatch_{id(self)}", self)

    def __parent_destroyed(self):
        get_config(self.parent).detach(self)
        delattr(self.parent, f"_config_dispatch_{id(self)}")
        self.parent = None

    def update(self, event):
        try:
            function = self.mapping[event.key]
        except LookupError:
            pass
        else:
            function(event)
