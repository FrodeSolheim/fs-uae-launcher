from fsui import Image
from launcher.context import get_config
from launcher.i18n import gettext
from launcher.ui.statusbar.StatusElement import StatusElement


class ProtectionElement(StatusElement):
    def __init__(self, parent):
        StatusElement.__init__(self, parent)
        # self.set_min_width(140)
        # self.layout = HorizontalLayout()
        self.protection_icon = Image("launcher:/data/16x16/lock.png")
        # self.unknown_icon = self.icon.grey_scale()
        self.disabled_icon = Image("launcher:/data/16x16/lock_open_green.png")
        # self.disabled_icon = self.disabled_icon.grey_scale()
        self.icon = self.protection_icon

        self.na_text = " "
        self.protection = ""
        self.text = self.na_text
        self.active = False

        config = get_config(self)
        config.add_listener(self)
        self.on_config("protection", config.get("protection"))

    def onDestroy(self):
        config = get_config(self)
        config.remove_listener(self)
        super().onDestroy()

    def on_config(self, key, value):
        if key == "protection":
            print(" -- protection --", value)
            if value != self.protection:
                self.protection = value
                if not value:
                    self.icon = self.protection_icon
                    self.active = False
                    self.text = self.na_text
                elif value.lower() == "none":
                    # self.icon = self.disabled_icon
                    # self.active = True
                    self.icon = self.protection_icon
                    self.active = False
                    self.text = gettext("No Protection")
                elif value.lower() in ["dongle"]:
                    # self.icon = self.disabled_icon
                    # self.active = True
                    self.icon = self.protection_icon
                    self.active = False
                    self.text = gettext("Dongle")
                else:
                    self.icon = self.protection_icon
                    self.active = True
                    self.text = value
                self.refresh()
