import weakref

# from launcher.launcher_config import LauncherConfig
from launcher.context import get_config

AMIGA_PLATFORMS = ["", "amiga", "cd32", "cdtv"]
FLOPPY_PLATFORMS = AMIGA_PLATFORMS + ["atari"]
CD_PLATFORMS = AMIGA_PLATFORMS + ["psx"]


class PlatformBehavior:
    def __init__(self, parent, platforms):
        self._widget = parent
        self.platforms = set(platforms)
        # self._parent = weakref.ref(parent)
        parent.__platform_behavior = self
        config = get_config(self.widget())
        self.on_config("platform", config.get("platform"))
        config.add_listener(self)
        parent.destroyed.connect(self.__on_parent_destroy)

    def on_config(self, key, value):
        if key == "platform":
            platform = value.lower()
            self.perform(platform in self.platforms)

    def __on_parent_destroy(self, *_):
        print("PlatformBehavior: remove_listener", self)
        config = get_config(self.widget())
        config.remove_listener(self)

    def perform(self, match):
        pass

    def widget(self):
        return self._widget


class PlatformEnableBehavior(PlatformBehavior):
    def __init__(self, parent, platforms):
        super().__init__(parent, platforms)

    def perform(self, match):
        widget = self.widget()
        widget.set_enabled(bool(match))


class AmigaEnableBehavior(PlatformEnableBehavior):
    def __init__(self, parent):
        super().__init__(parent, platforms=AMIGA_PLATFORMS)


class FloppyEnableBehavior(PlatformEnableBehavior):
    def __init__(self, parent):
        super().__init__(parent, platforms=FLOPPY_PLATFORMS)


class CDEnableBehavior(PlatformEnableBehavior):
    def __init__(self, parent):
        super().__init__(parent, platforms=CD_PLATFORMS)


class PlatformShowBehavior(PlatformBehavior):
    def __init__(self, parent, platforms):
        super().__init__(parent, platforms)

    def perform(self, match):
        # FIXME: Temporarily disabled due to having to handle layout
        # updates when widgets are shown/hidden
        widget = self.widget()
        # if hasattr(widget, "_init_stack"):
        #     print(widget._init_stack)
        if match:
            widget.show()
            # Workaround for (possibly) a bug where the widget is still
            # disabled if it was enabled while hidden?
            # if widget.is_enabled():
            #     widget.set_enabled(False)
            #     widget.set_enabled()
        else:
            widget.hide()
        # FIXME: Disabling/enabling instead, for now
        # widget = self.widget()
        # if match:
        #     widget.set_enabled()
        # else:
        #     widget.set_enabled(False)
        # pass


class AmigaShowBehavior(PlatformShowBehavior):
    def __init__(self, parent):
        super().__init__(parent, platforms=AMIGA_PLATFORMS)
