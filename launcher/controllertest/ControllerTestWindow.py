import logging

from fsgamesys.input.inputservice import (
    GamepadConnectedEvent,
    GamepadDisconnectedEvent,
    JoystickConnectedEvent,
    JoystickDisconnectedEvent,
    useInputService,
)
from launcher.fswidgets2.flexcontainer import FlexContainer
from launcher.fswidgets2.panel import Panel
from launcher.fswidgets2.textarea import TextArea
from launcher.i18n import gettext
from system.classes.window import Window

log = logging.getLogger(__name__)


class ControllerTestWindow(Window):
    def __init__(self) -> None:
        log.info(
            "Creating controller test window",
        )
        super().__init__(parent=None, title=gettext("Controller Test"))
        # ControllerConfigPanel(deviceGuid, parent=self)
        self.setSize((800, 500))

        with FlexContainer(parent=self):
            self.controllersPanel = Panel()
            self.textArea = TextArea(style={"flexGrow": 1, "margin": 10})

        self.inputService = useInputService()

        self.listen(
            self.inputService.gamepadConnectedEvent, self.onGamepadConnected
        )
        self.listen(
            self.inputService.gamepadDisconnectedEvent,
            self.onGamepadDisconnected,
        )

        self.listen(
            self.inputService.joystickConnectedEvent, self.onJoystickConnected
        )
        self.listen(
            self.inputService.joystickDisconnectedEvent,
            self.onJoystickDisconnected,
        )

    def append(self, message: str) -> None:
        self.textArea.appendLine(message)

    def onGamepadConnected(self, event: GamepadConnectedEvent) -> None:
        self.append("Gamepad connected")

    def onGamepadDisconnected(self, event: GamepadDisconnectedEvent) -> None:
        self.append("Gamepad disconnected")

    def onJoystickConnected(self, event: JoystickConnectedEvent) -> None:
        self.append("Joystick connected")

    def onJoystickDisconnected(self, event: JoystickDisconnectedEvent) -> None:
        self.append("Joystick disconnected")
