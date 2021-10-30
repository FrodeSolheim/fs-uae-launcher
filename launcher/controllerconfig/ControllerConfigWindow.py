import logging
from typing import Optional

from fsui import PopupMenu
from launcher.controllerconfig.ControllerConfigPanel import (
    ControllerConfigPanel,
)
from launcher.i18n import gettext
from system.classes.window import Window

log = logging.getLogger(__name__)

# FIXME: TODO: Ask about saving before closing the window with unsaved changes
# FIXME: TODO: Window isn't currently centered on parent (prefs) window


class ControllerConfigWindow(Window):
    def __init__(
        self, *, deviceGuid: str, parent: Optional[Window] = None
    ) -> None:
        log.info(
            "Creating controller configuration window for controller with SDL2"
            "device GUID %s",
            deviceGuid,
        )
        super().__init__(
            parent,
            title=gettext("Controller Configuration"),
            menu=True,
            maximizable=False,
        )
        self.panel = ControllerConfigPanel(deviceGuid, parent=self)
        self.deviceGuid = deviceGuid

    def onMenu(self) -> PopupMenu:
        # return ControllerConfigMenu(parent=self)
        dirty = self.panel.dirty
        mapping = self.panel.inputService.getGameControllerMapping(
            self.deviceGuid
        )
        if mapping is not None:
            print("mapping.source =", mapping.source)
            userModified = mapping.source == "User"  # FIXME: Magic value
        else:
            userModified = False
        showingSDLMapping = self.panel.oldPanel.mapping_field.isVisible()

        menu = PopupMenu()
        menu.add_item(gettext("New"), self.onClear)
        menu.add_separator()
        menu.add_item(gettext("Save"), self.onSave, enabled=dirty)
        menu.add_item(
            gettext("Revert to saved")
            if userModified
            else gettext("Revert to default"),
            self.onRevert,
            enabled=dirty,
        )
        menu.add_separator()
        menu.add_item(
            gettext("Hide SDL mapping")
            if showingSDLMapping
            else gettext("Show SDL mapping"),
            self.onShowSDLMapping,
        )
        menu.add_item(
            gettext("Delete user configuration"),
            self.onDeleteUserConfig,
            enabled=userModified,
        )
        return menu

    def onClear(self) -> None:
        log.debug("onClear")
        self.panel.onClear()

    def onDeleteUserConfig(self) -> None:
        log.debug("onDeleteUserConfig")
        self.panel.onDeleteUserConfig()

    def onRevert(self) -> None:
        log.debug("onRevert")
        self.panel.onReset()

    def onSave(self) -> None:
        log.debug("onSave")
        self.panel.onSave()

    def onShowSDLMapping(self) -> None:
        log.debug("onShowSDLMapping")
        self.panel.onShowSDLMapping()
        self.setSize(self.getMinSize())
