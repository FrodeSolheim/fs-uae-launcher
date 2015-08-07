import weakref
from fs_uae_launcher.Config import Config


class AmigaEnableBehavior:

    def __init__(self, parent):
        parent.__amiga_enable_behavior = self
        self._parent = weakref.ref(parent)
        Config.add_listener(self)
        # FIXME
        parent.destroyed.connect(self.on_destroy)

    def on_destroy(self, *args):
        Config.remove_listener(self)

    def on_config(self, key, value):
        if key == "platform":
            widget = self._parent()
            platform = value.lower()
            if platform in ["", "amiga", "cd32", "cdtv"]:
                widget.enable()
            else:
                widget.disable()
