from fsgamesys.context import default_context
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle
from launcher.system.exceptionhandler import exceptionhandler
from launcher.ui2.launcher2panel import Launcher2Panel
from launcher.ui2.mainmenu import MainMenu
from launcher.helpers.implicitconfighandler import ImplicitConfigHandler
from launcher.ui.imageloader import ImageLoader
from launcher.settings import get_launcher_window_title


class Launcher2Window(Window):
    def __init__(self, parent):
        super().__init__(parent, title=get_launcher_window_title(), menu=True)

        # FIXME: Create new context instead - later
        self.gscontext = default_context()

        self.image_loader = ImageLoader()

        self.panel = Launcher2Panel(self)
        self.layout.add(self.panel, fill=True, expand=True)

        WindowResizeHandle(self)
        self.implicit_config_handler = ImplicitConfigHandler(self)

        print("[LAUNCHER] Setting initial window size to 1280x760")
        self.set_size((1280, 760))

    def on_destroy(self):
        self.image_loader.stop()
        super().on_destroy()

    @exceptionhandler
    def on_menu(self):
        return MainMenu(self)
