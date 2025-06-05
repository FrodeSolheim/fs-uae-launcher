import weakref

from launcher.launcher_config import LauncherConfig

AMIGA_PLATFORMS = ["", "amiga", "cd32", "cdtv"]
FLOPPY_PLATFORMS = AMIGA_PLATFORMS + ["atari"]
CD_PLATFORMS = AMIGA_PLATFORMS + ["psx"]


class PlatformBehavior:
    def __init__(self, parent, platforms):
        self.platforms = set(platforms)
        parent.__platform_behavior = self
        self._parent = weakref.ref(parent)
        self.on_config("platform", LauncherConfig.get("platform"))
        LauncherConfig.add_listener(self)

        # FIXME: We need to disconnect the listener
        parent.destroyed.connect(self.on_destroy)

    def on_destroy(self, *_):
        LauncherConfig.remove_listener(self)

    def on_config(self, key, value):
        if key == "platform":
            platform = value.lower()
            self.perform(platform in self.platforms)

    def perform(self, match):
        pass


class PlatformEnableBehavior(PlatformBehavior):
    def __init__(self, parent, platforms):
        super().__init__(parent, platforms)

    def perform(self, match):
        widget = self._parent()
        if match:
            widget.enable()
        else:
            widget.disable()


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
        widget = self._parent()
        if match:
            widget.show()
            # Workaround for (possibly) a bug where the widget is still
            # disabled if it was enabled while hidden?
            # if widget.is_enabled():
            #     widget.disable()
            #     widget.enable()
        else:
            widget.hide()
        # FIXME: Disabling/enabling instead, for now
        # widget = self._parent()
        # if match:
        #     widget.enable()
        # else:
        #     widget.disable()
        # pass


class AmigaShowBehavior(PlatformShowBehavior):
    def __init__(self, parent):
        super().__init__(parent, platforms=AMIGA_PLATFORMS)
