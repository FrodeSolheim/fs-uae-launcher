import logging
import logging.config
from typing import Callable, List, Optional, Set

import fsui
from launcher.fswidgets2.button import Button
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.fswidgets2.imageview import ImageView
from launcher.fswidgets2.label import Label
from launcher.fswidgets2.spacer import Spacer
from launcher.fswidgets2.textarea import TextArea
from launcher.fswidgets2.window import Window
from launcher.i18n import gettext
from system.prefs.updates import Updates
from system.special.login import WidgetSizeSpinner
from system.utilities.updater.checkforupdatestask import (
    CheckForUpdatesResult,
    CheckForUpdatesTask,
    Update,
)
from system.utilities.updater.updatetask import UpdateResult, UpdateTask

# from autologging import TRACE, traced


log = logging.getLogger(__name__)

# @traced
class UpdaterWindow(Window):
    def __init__(self) -> None:
        super().__init__(
            title=gettext("Updater"),
            minimizable=False,
            maximizable=False,
            style={"backgroundColor": "#bbbbbb"},
        )

        self.updates: Optional[List[Update]] = None

        with FlexContainer(
            parent=self,
            style={
                "gap": 20,
                "padding": 20,
                "paddingBottom": 10,
            },
        ):
            with VerticalFlexContainer(style={"flexGrow": 1, "gap": 5}):
                Label(
                    gettext("Software updater"),
                    style={"fontWeight": "bold"},
                )
                Label(gettext("Updates the Launcher and plugins for you"))
            ImageView(fsui.Image("workspace:/data/48/plugins.png"))
        self.textArea = TextArea(
            parent=self,
            readOnly=True,
            style={
                "margin": 20,
                "marginTop": 10,
                "marginBottom": 10,
                "width": 600,
                "height": 200,
            },
        )
        with FlexContainer(
            parent=self,
            style={
                "gap": 10,
                "padding": 20,
                "paddingTop": 10,
            },
        ):
            self.preferencesButton = Button(
                gettext("Preferences"), onClick=self.onPreferences
            )
            Spacer(style={"flexGrow": 1})
            # self.errorLabel = Label(style={"flexGrow": 1})
            # FIXME: Set visible via stylesheet instead?
            self.spinner = WidgetSizeSpinner(visible=False)
            self.checkForUpdatesButton = Button(
                gettext("Check for updates"), onClick=self.checkForUpdates
            )
            self.updateAllButton = Button(
                gettext("Update all"), onClick=self.updateAll
            )

        self.updateAllButton.disable()
        # self.textArea.appendText("Heisann")
        # self.textArea.appendText("Hopsann")

    def onPreferences(self) -> None:
        Updates.open(openedFrom=self.getWindow())

    def appendLogLine(self, line: str) -> None:
        self.textArea.appendLine(line)

    # # FIXME: Move to widget
    # def addEventListener(self, eventName, listener) -> None:
    #     if eventName == "destroy":
    #         self.destroyed.connect(listener)

    # FIXME: Move to widget
    # def addDestroyListener(self, listener: Callable[[], None]) -> None:
    #     self.destroyed.connect(listener)

    # FIXME: Move to widget
    # def onDestroy(self, listener):
    #     self.destroyed.connect(listener)

    def setRunning(self, running: bool) -> None:
        if running:
            self.checkForUpdatesButton.disable()
            self.updateAllButton.disable()

    def checkForUpdates(self) -> None:
        self.setRunning(True)

        # @traced
        def onResult(result: CheckForUpdatesResult) -> None:
            self.checkForUpdatesButton.enable()

            self.appendLogLine("Got result, doing calculations...")
            updates = CheckForUpdatesTask.findUpdates(result)

            self.appendLogLine("")
            if len(updates) > 0:
                self.appendLogLine("Available updates:")
            else:
                self.appendLogLine("No updates!")

            for update in updates:
                systems: Set[str] = set()
                for archive in update["archives"]:
                    systems.update(archive["systems"])
                    # for osName in archive.get("operatingSystems", []):
                    #     for archName in archive.get("architectures", []):
                    #         systems.add(f"{osName}_{archName}")
                    # operatingSystems.update(
                    #     archive.get("operatingSystems", [])
                    # )
                    # operatingSystems.update(
                    #     archive.get("operatingSystems", [])
                    # )
                installedVersion = update["installedVersion"]
                self.appendLogLine(
                    "{}: {} => {} ({})".format(
                        update["packageName"],
                        installedVersion
                        if installedVersion != "0"
                        else "(not installed)",
                        update["availableVersion"],
                        ", ".join(sorted(systems)),
                    )
                )
            self.updateAllButton.setEnabled(len(updates) > 0)
            self.updates = updates

            # if self.updateAllButton.isEnabled():
            #     self.updateAll()

        # @traced
        def onError(error: Exception) -> None:
            self.checkForUpdatesButton.enable()
            # self.setRunning(False)
            self.appendLogLine(f"Error: {str(error)}")
            # self.errorLabel.setText(f"Error: {str(error)}")

        # @traced
        def onProgress(progress: str) -> None:
            # self.errorLabel.setText(progress)
            self.appendLogLine(progress)
            # task.cancel()

        # self.addDestroyListener(
        #     AsyncTaskRunner(onResult, onError, onProgress)
        #     .run(CheckForUpdatesTask())
        #     .cancel,
        # )

        self.runTask(CheckForUpdatesTask(), onResult, onError, onProgress)

        # FIXME: Add support for (also) inheriting from AsyncTaskRunner?
        # self.runTask(LogoutTask(authToken), onResult, onError, onProgress)

    def updateAll(self) -> None:
        if self.updates is None:
            log.warning("updateAll: self.updates was None")
            return
        self.appendLogLine("")
        self.setRunning(True)

        # @traced
        def onResult(result: UpdateResult) -> None:
            self.checkForUpdatesButton.enable()
            self.appendLogLine("")
            if result["restartRequired"]:
                self.appendLogLine(
                    "Update complete, but a restart of the Launcher is required"
                )
                self.appendLogLine("PLEASE RESTART NOW")
            else:
                self.appendLogLine("Update complete")
            self.appendLogLine("")

        # @traced
        def onError(error: Exception) -> None:
            self.checkForUpdatesButton.enable()
            # self.setRunning(False)
            self.appendLogLine(f"Error: {str(error)}")
            # self.errorLabel.setText(f"Error: {str(error)}")

        # @traced
        def onProgress(progress: str) -> None:
            # self.errorLabel.setText(progress)
            self.appendLogLine(progress)
            # task.cancel()

        # self.addDestroyListener(
        #     AsyncTaskRunner(onResult, onError, onProgress)
        #     .run(UpdateTask(self.updates))
        #     .cancel,
        # )
        # self.addDestroyListener(
        #     AsyncSingleTaskRunner(
        #         UpdateTask(self.updates), onResult, onError, onProgress
        #     )
        #     .start().cancel,
        # )

        self.runTask(UpdateTask(self.updates), onResult, onError, onProgress)
