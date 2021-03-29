from fsgamesys.context import default_context
from fsui import Button, Color, Label, Panel
from fsui.common.layout import HorizontalLayout
from launcher.helpers.implicitconfighandler import ImplicitConfigHandler
from launcher.i18n import gettext
from launcher.settings import get_launcher_window_title
from launcher.system.classes.window import Window
from launcher.system.classes.windowresizehandle import WindowResizeHandle
from launcher.system.exceptionhandler import exceptionhandler
from launcher.system.special.logout import AsyncTaskRunner
from launcher.system.utilities.updater import (
    CheckForUpdatesTask,
    Updater,
    findUpdates,
)
from launcher.ui2.launcher2panel import Launcher2Panel
from launcher.ui2.mainmenu import MainMenu
from launcher.ui.imageloader import ImageLoader
from launcher.version import VERSION


class UpdatesAvailablePanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_background_color(Color.from_hex("#cccc88"))
        label = Label(self, gettext("Updates are available"))
        showButton = Button(self, "Show")
        dismissButton = Button(self, "Dismiss")
        self.layout = HorizontalLayout()
        self.layout.set_padding(20)
        self.layout.add(label)
        self.layout.add(showButton, margin_left=20)
        self.layout.add(dismissButton, margin_left=10)
        self.updatePositionAndSize()
        parent.resized.connect(self.onResizeParent)

        showButton.activated.connect(self.onShowButton)
        dismissButton.activated.connect(self.onDismissButton)

    def onShowButton(self):
        Updater.open(window=self.getWindow())

    def onDismissButton(self):
        self.hide()

    def onResizeParent(self):
        self.updatePositionAndSize()

    def updatePositionAndSize(self):
        size = self.layout.get_min_size()
        parentSize = self.parent().get_size()
        self.set_position_and_size(
            (parentSize[0] - size[0], parentSize[1] - size[1]), size
        )


from fscore.settings import Settings


class Launcher2Window(Window):
    def __init__(self, parent):
        title = get_launcher_window_title()
        title = f"{title}  {VERSION}"
        super().__init__(parent, title=title, menu=True)

        # FIXME: Create new context instead - later
        self.gscontext = default_context()

        self.image_loader = ImageLoader()

        self.panel = Launcher2Panel(self)
        self.layout.add(self.panel, fill=True, expand=True)

        WindowResizeHandle(self)
        self.implicit_config_handler = ImplicitConfigHandler(self)

        print("[LAUNCHER] Setting initial window size to 1280x760")
        self.set_size((1280, 760))

        if not Settings.get("check_for_updates") == "0":
            self.checkForUpdates()

    def on_destroy(self):
        self.image_loader.stop()
        super().on_destroy()

    @exceptionhandler
    def on_menu(self):
        return MainMenu(self)

    def checkForUpdates(self):
        task = CheckForUpdatesTask()

        def onResult(result):
            if len(findUpdates(result)) > 0:
                print("Updates are available!")
                UpdatesAvailablePanel(self).show()

        self.addDestroyListener(AsyncTaskRunner(onResult).run(task).cancel)

    # FIXME: Move to widget
    def addDestroyListener(self, listener):
        self.destroyed.connect(listener)
