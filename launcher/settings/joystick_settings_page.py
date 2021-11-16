from logging import getLogger

import fsui
from fsgamesys.input.inputservice import useInputService
from fsgamesys.options.option import Option
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.settings.settings_page import SettingsPage
from system.wsopen import wsopen

log = getLogger(__name__)


class JoystickSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        icon = fsui.Icon("joystick-settings", "pkg:workspace")
        # gettext("Joystick Settings")
        title = gettext("Controllers")
        subtitle = gettext(
            "Configure joysticks and set preferred joystick " "devices"
        )
        self.add_header(icon, title, subtitle)

        label = fsui.Label(
            self, gettext("Double-click a controller to configure it:")
        )
        self.layout.add(label, margin_bottom=10)

        self.list_view = fsui.ListView(self)
        self.list_view.set_min_height(140)
        self.list_view.item_activated.connect(self.on_joystick_activated)
        self.image = fsui.Image("workspace:/data/16x16/gamepad.png")

        # for device_name in DeviceManager.get_joystick_names():
        #     if DeviceManager.is_joystick(device_name):
        #         self.list_view.add_item(device_name, icon=image)

        self.inputService = useInputService()
        # for device in inputService.getInputDevices():
        #     if device.type == "joystick":
        #         # devices.append(device.id)
        #         self.list_view.add_item(device.id, icon=image)
        #         # or devices.append(device.name) ?

        # for device in inputService.getJoysticks():
        #     self.list_view.add_item(device.uniqueName, icon=image)
        #     # or devices.append(device.name) ?

        self.updateDeviceList()

        self.listen(
            self.inputService.joystickConnectedEvent, self.onJoystickConnected
        )
        self.listen(
            self.inputService.joystickDisconnectedEvent,
            self.onJoystickDisconnected,
        )

        self.layout.add(self.list_view, fill=True, expand=True)

        self.layout.add_spacer(20)
        self.pref_group = PreferredJoysticksGroup(self)
        self.layout.add(self.pref_group, fill=True)

        # For reset to defaults function
        self.options_on_page.add(Option.PRIMARY_JOYSTICK)
        self.options_on_page.add(Option.SECONDARY_JOYSTICK)

    def updateDeviceList(self) -> None:
        self.list_view.clear()
        for device in self.inputService.getJoysticks():
            self.list_view.add_item(device.uniqueName, icon=self.image)

    def onJoystickConnected(self) -> None:
        log.debug("Got joystick connected event")
        self.updateDeviceList()

    def onJoystickDisconnected(self) -> None:
        log.debug("Got joystick disconnected event")
        self.updateDeviceList()

    def on_joystick_activated(self, index: int) -> None:
        deviceId = self.list_view.get_item(index)
        # shell_open("Workspace:Tools/JoystickConfig", [device_name],
        #            parent=self.get_window())
        # JoystickConfigWindow(self.window, device_name).show()
        # inputService = useInputService()
        # device = inputService.getDevice(deviceId)
        # if device is not None:
        #     JoystickConfigWindow(self.window, device).show()
        # else:
        #     # FIXME: Device disappeared...
        #     assert device

        for joystick in self.inputService.getJoysticks():
            if joystick.uniqueName == deviceId:
                guid = joystick.sdlGuid
                wsopen(
                    f"SYS:Tools/ControllerConfig?GUID={guid}",
                    parent=self.getWindow(),
                )


joystick_mode_values = ["nothing", "mouse", "joystick"]
joystick_values = ["none", "mouse", "keyboard"]


class PreferredJoysticksGroup(fsui.Panel):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()
        # self.layout.padding_left = 10
        # self.layout.padding_right = 10

        # image = fsui.Image("launcher:/data/joystick.png")
        # self.image_view = fsui.ImageView(self, image)
        # self.layout.add(self.image_view, valign=0.0)

        # self.layout.add_spacer(20)

        self.layout2 = fsui.VerticalLayout()
        self.layout.add(self.layout2, fill=True, expand=True)

        heading = gettext("Preferred Controllers")
        headingLabel = fsui.HeadingLabel(self, heading)
        self.layout2.add(headingLabel)

        self.layout2.add_spacer(20)
        label = fsui.Label(self, gettext("Preferred controller (if present):"))
        self.layout2.add(label)

        self.layout2.add_spacer(6)
        selector = PreferredJoystickSelector(self, 0)
        self.layout2.add(selector, fill=True)

        self.layout2.add_spacer(20)
        label = fsui.Label(
            self, gettext("Preferred device for secondary controller:")
        )
        self.layout2.add(label)

        self.layout2.add_spacer(6)
        selector = PreferredJoystickSelector(self, 1)
        self.layout2.add(selector, fill=True)


class PreferredJoystickSelector(fsui.Panel):
    def __init__(self, parent: Widget, index: int) -> None:
        self.index = index
        if index:
            self.key = Option.SECONDARY_JOYSTICK
        else:
            self.key = Option.PRIMARY_JOYSTICK

        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        # devices = ["", get_keyboard_title()]
        # for i, name in enumerate(DeviceManager.get_joystick_names()):
        #     devices.append(name)

        # for device_name in DeviceManager.get_joystick_names():
        #     if DeviceManager.is_joystick(device_name):
        #         devices.append(device_name)

        # inputService = useInputService()
        # for device in inputService.getInputDevices():
        #     if device.type == "joystick":
        #         devices.append(device.id)
        #         # or devices.append(device.name) ?
        # for device in inputService.getJoysticks():
        #     devices.append(device.uniqueName)

        self.device_choice = fsui.ComboBox(self)

        self.inputService = useInputService()
        # for device in inputService.getInputDevices():
        #     if device.type == "joystick":
        #         # devices.append(device.id)
        #         self.list_view.add_item(device.id, icon=image)
        #         # or devices.append(device.name) ?

        # for device in inputService.getJoysticks():
        #     self.list_view.add_item(device.uniqueName, icon=image)
        #     # or devices.append(device.name) ?

        self._updatingList = False
        self.updateDeviceList()
        self.listen(
            self.inputService.joystickConnectedEvent, self.onJoystickConnected
        )
        self.listen(
            self.inputService.joystickDisconnectedEvent,
            self.onJoystickDisconnected,
        )

        self.layout.add(self.device_choice, expand=True)

        # Config.add_listener(self)

        self.initialize_from_settings()
        self.set_settings_handlers()

    def updateDeviceList(self) -> None:
        # for device in self.inputService.getJoysticks():
        #     self.list_view.add_item(device.uniqueName, icon=self.image)
        devices = ["", get_keyboard_title()]
        for device in self.inputService.getJoysticks():
            devices.append(device.uniqueName)
        self._updatingList = True
        self.device_choice.setItems(devices)
        self.initialize_from_settings()
        self._updatingList = False

    def onJoystickConnected(self) -> None:
        self.updateDeviceList()

    def onJoystickDisconnected(self) -> None:
        self.updateDeviceList()

    def initialize_from_settings(self) -> None:
        self.on_setting(self.key, LauncherSettings.get(self.key))

    def set_settings_handlers(self) -> None:
        # FIXME: on_changed: "Cannot assign to a method" (mypy)
        self.device_choice.on_changed = self.on_device_changed  # type: ignore
        LauncherSettings.add_listener(self)

    def onDestroy(self) -> None:
        LauncherSettings.remove_listener(self)
        super().onDestroy()

    def on_device_changed(self) -> None:
        if self._updatingList:
            return
        value = self.device_choice.get_text()
        log.debug("on_device_change %r", value)
        if value == get_keyboard_title():
            value = "keyboard"
        LauncherSettings.set(self.key, value)

    def on_setting(self, key: str, value: str) -> None:
        if key == self.key:
            if value == "keyboard":
                value = get_keyboard_title()
            self.device_choice.set_text(value)


def get_keyboard_title() -> str:
    return gettext("Cursor Keys and Right Ctrl/Alt")
