import logging
import time
from typing import Dict, List, Optional, Tuple

from typing_extensions import Literal

import fsui
from fscore.memoize import memoize
from fscore.system import System
from fsgamesys.input.gamecontroller import (
    GameControllerBind,
    GameControllerBindType,
    GameControllerItem,
    GameControllerMapping,
)
from fsgamesys.input.inputdevice import InputDeviceState, InputDeviceWithState
from fsgamesys.input.inputservice import (
    DeviceConnectedEvent,
    DeviceDisconnectedEvent,
    useInputService,
)
from fswidgets.widget import Widget
from launcher.fswidgets2.flexcontainer import VerticalFlexContainer
from launcher.fswidgets2.label import Label
from launcher.fswidgets2.style import Style
from launcher.i18n import gettext
from workspace.ui.theme import WorkspaceTheme

log = logging.getLogger(__name__)


class MappingButton(fsui.Panel):
    def __init__(
        self,
        parent: Widget,
        position: Tuple[int, int],
        direction: Literal[-1, 1],
        name: str,
    ) -> None:
        super().__init__(parent)

        size = (150, 22)
        self.set_size(size)
        if direction < 0:
            position = (position[0] - size[0], position[1])
        self.set_position(position)

        self.key_name = name
        self.event_name: Optional[str] = None
        self.text = ""
        self.direction = direction

        self.set_hand_cursor()
        # self.set_background_color(fsui.Color(0xFF, 0xFF, 0xFF))
        self.set_background_color(fsui.Color(0xFF, 0xFF, 0xFF, 0x00))

    def on_left_down(self) -> None:
        print("on_left_down")
        # self.get_window().map_event(self.key_name)
        self.getParent().getParent().map_event(self.key_name)
        self.getParent().getParent().getParent().startMapping()

    def on_paint(self) -> None:
        dc = self.create_dc()
        dc.set_font(self.get_font())
        if self.text:
            text = self.text
            dc.set_text_color(fsui.Color(0x00, 0x80, 0x00))
        elif self.event_name:
            text = self.event_name
            dc.set_text_color(fsui.Color(0x80, 0x80, 0x80))
        else:
            text = "click to configure"
            dc.set_text_color(fsui.Color(0xFF, 0x00, 0x00))
        tw, th = dc.measure_text(text)
        y = (self.get_size()[1] - th) / 2
        if self.direction > 0:
            x = 4
        else:
            x = self.get_size()[0] - 4 - tw
        dc.draw_text(text, x, y)


class DisconnectedPanel(VerticalFlexContainer):
    def __init__(self, parent: Widget) -> None:
        super().__init__(
            parent=parent,
            style={
                "backgroundColor": "#ffcc00",
                "position": "absolute",
                "left": 10,
                "top": 10,
            },
        )
        # FIXME: Show a warning icon to the left of the text
        with self:
            Label(
                "DEVICE IS DISCONNECTED",
                style={"margin": 10},  # , "marginLeft": 20, "marginRight": 20
            )

        # FIXME: Remove later, when no longer needed. Right now, it is needed
        # because the widget size is not updated since it is not part of the
        # parent layout
        self.setSize(self.getMinSize())


class NormalizedInputDeviceState(InputDeviceState):
    """Subclassed to get type safety (plus timeStamp field)."""

    timeStamp: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalizedInputDeviceState):
            raise NotImplementedError()
        # Mypy didn't understand this without explicitly assigning to a
        # temporary variable declared bool - not sure why.
        result: bool = (
            self.axes == other.axes
            and self.balls == other.balls
            and self.buttons == other.buttons
            and self.hats == other.hats
        )
        return result


class ControllerConfigPanel(VerticalFlexContainer):
    def __init__(self, deviceGuid: str, *, parent: Widget) -> None:
        log.info(
            "Creating controller configuration panel for controller with"
            "SDL device GUID %s",
            deviceGuid,
        )
        super().__init__(parent)
        # self.panel = WHDLoadSettingsPage(self)
        # self.layout.add(self.panel, fill=True, expand=True)

        # FIXME: BIND TO ESCAPE BUTTON

        self.deviceGuid = deviceGuid
        self.inputService = useInputService()
        # device = inputService.getDeviceByGuid(deviceGuid)

        # with self:
        #     Button("Heisann og hoppsann og fallerallera")
        #     Button(deviceGuid)
        #     Button("Heisann")

        self.buttonForItem: Dict[GameControllerItem, MappingButton] = {}
        self.oldPanel = OldControllerConfigPanel(self, deviceGuid)

        self.disconnectedPanel = DisconnectedPanel(parent=self)
        # panel.set_min_height(100)
        # panel.set_min_width(100)

        self.layout.add(self.oldPanel)

        # self.destroyEvent = EventHelper[DestroyEvent]()

        # FIXME: self.destroyEvent.addListener(
        # self.addDestroyListener(
        #     inputService.gamepadConnectedEvent.addListener(
        #         self.onGamepadConnected
        #     )
        # )
        # self.addDestroyListener(
        #     inputService.gamepadDisconnectedEvent.addListener(
        #         self.onGamepadDisconnected
        #     )
        # )

        # FIXME: Rename EventHelper -> EventSource!

        # self.listen(
        #     self.inputService.gamepadConnectedEvent, self.onGamepadConnected
        # )
        # self.listen(
        #     self.inputService.gamepadDisconnectedEvent,
        #     self.onGamepadDisconnected,
        # )

        self.listen(
            self.inputService.deviceConnectedEvent, self.onDeviceConnected
        )
        self.listen(
            self.inputService.deviceDisconnectedEvent,
            self.onDeviceDisconnected,
        )

        # self.initialState: Optional[InputDeviceState] = None
        self.initialStates: Dict[str, NormalizedInputDeviceState] = {}
        self.currentStates: Dict[str, NormalizedInputDeviceState] = {}

        # self.currentState: Optional[InputDeviceState] = None
        self.isMapping = False
        self.mapKey = ""
        # self.mapping: GameControllerMapping = {}
        self.mapping: GameControllerMapping
        self.setMapping(self.getExistingMapping())

        # Used to tell the input service more information about the device
        # when saving. It could be disconnected at that point, so we store
        # a reference to it.
        # self.lastDevice: Optional[InputDevice] = None

        # FIXME: Timer(1.0, onTimer=self.onTimer)
        # FIXME: How to keep alive? Global timers list?
        fsui.callLater(0.1, self.onTimer)

        self.updateButtons()
        self.updateMapping()

        self.deviceConnectedCheck()

        self.dirty = False
        self.setDirty(False)

        # self.oldPanel.save_button.disable()

        # self.listen([
        #     (inputService.gamepadConnectedEvent, self.onGamepadConnected),
        #     (inputService.gamepadDisconnectedEvent, self.onGamepadDisconnected)
        # ])

        # inputService.addEventListener(
        #     "gamepadconnected", self.onGamepadConnected
        # )
        # inputService.addEventListener(
        #     "gamepaddisconnected", self.onGamepadDisconnected
        # )

        # self.addEventListener(
        #     "destroy",
        #     inputService.addEventListener(
        #         "gamepadconnected", self.onGamepadConnected
        #     ),
        # )

        # self.addDestroyListener(
        #     inputService.addEventListener(
        #         "gamepadconnected", self.onGamepadConnected
        #     )
        # )

        # self.onDestroy(inputService.onGamepadConnected(self.onGamepadConnected))

    #     self.listen(inputService, "deviceconnected", self.onDeviceConnected)
    #     self.listen(inputService, "devicedisconnected", self.onDeviceDisconnected)

    #     self.listen(inputService, "gamepadconnected", self.onGamepadConnected)
    #     self.listen(inputService, "gamepaddisconnected", self.onGamepadDisconnected)

    # def listen(self, target: T, type, listener):
    #     target.addEventListener(type, listener)

    # self.inputService = useInputService()
    # self.listen(inputService, "")
    # inputService.addEventListener("devicedisconnected", self.onDeviceDisconnected)

    # def listen(
    #     self, event: EventHelper[T], listener: EventListener[T]
    # ) -> None:
    #     self.addDestroyListener(event.addListener(listener))

    # def onDestroy(self) -> None:
    #     # self.inputService.removeEventListener("devicedisconnected", self.onDeviceDisconnected)
    #     inputService = useInputService()
    #     inputService.removeEventListener(
    #         "gamepadconnected", self.onGamepadConnected
    #     )
    #     inputService.removeEventListener(
    #         "gamepaddisconnected", self.onGamepadDisconnected
    #     )

    def onDeviceConnected(self, event: DeviceConnectedEvent) -> None:
        log.debug("Device connected")
        self.deviceConnectedCheck()

    def onDeviceDisconnected(self, event: DeviceDisconnectedEvent) -> None:
        log.debug("Device disconnected")
        self.deviceConnectedCheck()

    # def onGamepadConnected(self, event: GamepadConnectedEvent) -> None:
    #     log.debug("Gamepad connected")

    # def onGamepadDisconnected(self, event: GamepadDisconnectedEvent) -> None:
    #     log.debug("Gamepad disconnected")

    def deviceConnectedCheck(self) -> None:
        # device = self.inputService.findDeviceByGuid(self.deviceGuid)
        # self.disconnectedPanel.setVisible(device is None)
        devices = self.inputService.findDevicesByGuid(self.deviceGuid)
        self.disconnectedPanel.setVisible(len(devices) == 0)

    def updateButtons(self) -> None:
        # items = list(self.buttonForItem.keys())
        # for item, binding in self.mapping.binds.items():
        #     self.buttonForItem[item].event_name = binding.toDescription()
        #     items.remove(item)
        # for item in items:
        #     self.buttonForItem[item].event_name = ""
        for item, button in self.buttonForItem.items():
            if item in self.mapping.binds:
                button.event_name = self.mapping.binds[item].toDescription()
            else:
                button.event_name = ""
            button.refresh()

    def updateMapping(self) -> None:
        if System.windows:
            self.mapping.platform = "Windows"
        elif System.macos:
            self.mapping.platform = "Mac OS X"
        elif System.linux:
            self.mapping.platform = "Linux"
        else:
            self.mapping.platform = "Unknown"
        self.oldPanel.mapping_field.setText(self.mapping.toString())
        # self.oldPanel.model_field.set_text(self.mapping.name)

    def onTimer(self) -> None:
        # FIXME: Only run timer when mapping
        # print("Timer")
        fsui.callLater(0.1, self.onTimer)
        # if self.oldPanel.map_key_name:
        if self.isMapping:
            self.checkMapping()
        # else:
        #     pass

    def checkMapping(self) -> None:
        # device = self.inputService.findDeviceByGuid(self.deviceGuid)
        # if device is None:
        #     return
        # print(device)

        devices = self.inputService.findDevicesByGuid(self.deviceGuid)
        if len(devices) == 0:
            self.stopMapping()
            return
        for device in devices:
            deviceState = self.getNormalizedDeviceState(device)
            initialState = self.initialStates.get(device.instanceId)
            if initialState is None:
                log.debug(
                    "initialState is None, setting initialState from current"
                )
                self.initialStates[device.instanceId] = deviceState
                initialState = deviceState
                # continue

            currentState = self.currentStates.get(device.instanceId)
            if currentState is None:
                self.currentStates[device.instanceId] = deviceState
                currentState = deviceState
                # continue

            if deviceState != currentState:
                self.currentStates[device.instanceId] = deviceState
                continue

            # if deviceState != currentState or deviceState.timeStamp < currentState.timeStamp + 1.0:
            THRESHOLD = 1 / 3
            if deviceState.timeStamp < currentState.timeStamp + THRESHOLD:
                continue
                # self.currentStates[device.instanceId] = deviceState
                # print("continue...", deviceState == currentState, deviceState != currentState)
                # print(currentState.timeStamp, deviceState.timeStamp, deviceState.timeStamp < currentState.timeStamp + 1.0)
                # continue

            # if deviceState.timeStamp < currentState.timeStamp

            bind = self.findActiveBind(self.mapItem, initialState, deviceState)
            if bind is not None:
                # self.lastDevice = device
                break
        else:
            return
        # FIXME: Handle missing device states

        # else:
        #     self.stopMapping()
        #     return

        # deviceState = self.getDeviceState()
        # if deviceState is None:
        #     self.stopMapping()
        #     return
        # print(deviceState)
        # assert self.initialState is not None
        # if not self.isComparableStates(self.initialState, deviceState):
        #     log.warning(
        #         "Device states are not comparable: inital %r vs. current %r",
        #         self.initialState,
        #         deviceState,
        #     )
        #     self.stopMapping()
        #     return
        # bind = self.findActiveBind(
        #     self.mapItem, self.initialState, deviceState
        # )
        print(bind)
        # if bind is None:
        #     return

        self.mapping.extra = f"{device.sdlName},axes:{device.numAxes},balls:{device.numBalls},buttons:{device.numButtons},hats:{device.numHats}"

        for existingItem, existingBind in list(self.mapping.binds.items()):
            if self.isConflictingBind(existingBind, bind):
                del self.mapping.binds[existingItem]
        self.mapping.binds[self.mapItem] = bind

        print("")
        print("Mapping:")
        from pprint import pprint

        pprint(self.mapping)
        print("")

        self.oldPanel.set_result(bind.toDescription())
        self.stopMapping()
        self.updateButtons()
        self.updateMapping()

        self.setDirty(True)

    def getExistingMapping(self) -> GameControllerMapping:
        mapping = self.inputService.getGameControllerMapping(self.deviceGuid)
        log.info("Existing mapping: %r", mapping)
        if mapping is None:
            mapping = GameControllerMapping()
            mapping.guid = self.deviceGuid
            device = self.inputService.findDeviceByGuid(self.deviceGuid)
            if device is not None:
                mapping.name = device.name
        return mapping

    def reloadMapping(self) -> None:
        # log.info("Reloaded mapping: %r", self.mapping)
        mapping = self.getExistingMapping()
        log.info("Reloaded mapping: %r", mapping)
        self.setMapping(mapping)

    def setMapping(self, mapping: GameControllerMapping) -> None:
        self.mapping = mapping
        self.oldPanel.model_field.set_text(self.mapping.name)

    def onClear(self) -> None:
        self.stopMapping()
        self.mapping.binds.clear()
        self.mapping.name = self.inputService.getJoystickNameByGuid(
            self.deviceGuid
        )
        self.setMapping(self.mapping)
        self.updateButtons()
        self.updateMapping()
        self.setDirty(True)

    def onReset(self) -> None:
        self.stopMapping()
        # self.mapping.binds.clear()
        self.reloadMapping()
        self.updateButtons()
        self.updateMapping()
        self.setDirty(False)

    def onDeleteUserConfig(self) -> None:
        self.inputService.deleteGameControllerMapping(self.deviceGuid)
        self.onReset()

    def onSave(self) -> None:
        self.stopMapping()
        self.updateMapping()
        self.mapping.source = "User"
        # self.inputService.saveGameControllerMapping(self.mapping, self.lastDevice)
        self.inputService.saveGameControllerMapping(self.mapping)
        self.setDirty(False)

    def onShowSDLMapping(self) -> None:
        self.oldPanel.mapping_field.setVisible(
            not self.oldPanel.mapping_field.isVisible()
        )
        self.layout.update()

    def setDirty(self, dirty: bool) -> None:
        self.dirty = dirty
        # self.oldPanel.reset_button.set_enabled(dirty)
        self.oldPanel.save_button.set_enabled(dirty)

    @staticmethod
    def isConflictingBind(
        oldBind: GameControllerBind, newBind: GameControllerBind
    ) -> bool:
        if oldBind.type != newBind.type:
            return False
        if (
            oldBind.type == GameControllerBindType.AXIS
            and oldBind.axis == newBind.axis
            and (
                newBind.axisDirection == 0
                or oldBind.axisDirection == 0
                or newBind.axisDirection == oldBind.axisDirection
            )
            # and (oldBind.axisDirection != 0 and newBind.axisDirection != oldBind.axisDirection)
            # and (newBind.axisDirection != 0 and newBind.axisDirection != oldBind.axisDirection)
        ):
            return True
        elif (
            oldBind.type == GameControllerBindType.BUTTON
            and oldBind.button == newBind.button
        ):
            return True
        elif (
            oldBind.type == GameControllerBindType.HAT
            and oldBind.hat == newBind.hat
            and oldBind.hatMask == newBind.hatMask
        ):
            return True
        return False

    @staticmethod
    def isComparableStates(
        oldState: InputDeviceState, newState: InputDeviceState
    ) -> bool:
        return (
            len(oldState.axes) == len(newState.axes)
            and len(oldState.balls) == len(newState.balls)
            and len(oldState.buttons) == len(newState.buttons)
            and len(oldState.hats) == len(newState.hats)
        )

    @staticmethod
    def preferButtonBindForItem(item: GameControllerItem) -> bool:
        return item in [
            GameControllerItem.A,
            GameControllerItem.B,
            GameControllerItem.BACK,
            GameControllerItem.DPAD_DOWN,
            GameControllerItem.DPAD_LEFT,
            GameControllerItem.DPAD_RIGHT,
            GameControllerItem.DPAD_UP,
            GameControllerItem.GUIDE,
            GameControllerItem.LEFTSHOULDER,
            GameControllerItem.LEFTSTICK,
            GameControllerItem.RIGHTSHOULDER,
            GameControllerItem.RIGHTSTICK,
            GameControllerItem.X,
            GameControllerItem.Y,
            GameControllerItem.START,
        ]

    @staticmethod
    def preferFullAxisBindForItem(item: GameControllerItem) -> bool:
        return item in [
            GameControllerItem.LEFTX,
            GameControllerItem.LEFTY,
            GameControllerItem.RIGHTX,
            GameControllerItem.RIGHTY,
        ]

    @classmethod
    def findActiveBind(
        cls,
        item: GameControllerItem,
        oldState: InputDeviceState,
        newState: InputDeviceState,
    ) -> Optional[GameControllerBind]:
        assert cls.isComparableStates(oldState, newState)
        for i, ostate in enumerate(oldState.hats):
            nstate = newState.hats[i]
            if nstate != ostate:
                return GameControllerBind(
                    type=GameControllerBindType.HAT,
                    hat=i,
                    # FIXME: Check if mask is same as enum value
                    hatMask=nstate,
                )
        buttonBind: Optional[GameControllerBind] = None
        axisBind: Optional[GameControllerBind] = None
        for i, ostate in enumerate(oldState.buttons):
            if newState.buttons[i] != ostate:
                buttonBind = GameControllerBind(
                    type=GameControllerBindType.BUTTON, button=i
                )
                break
        for i, ostate in enumerate(oldState.axes):
            nstate = newState.axes[i]
            os = 1 if ostate > 0.5 else -1 if ostate < -0.5 else 0
            ns = 1 if nstate > 0.5 else -1 if nstate < -0.5 else 0
            # FIXME: For axes, it would be nice to require that the axis state
            # has been stable for a short while, to avoid problems where the
            # state is polled mid-way.
            if ns != os:
                if cls.preferFullAxisBindForItem(item):
                    axisBind = GameControllerBind(
                        type=GameControllerBindType.AXIS, axis=i
                    )
                else:
                    if ns == 1:
                        if os == -1:
                            axisDirection, axisInverted = 0, False
                        else:  # os == 0
                            axisDirection, axisInverted = 1, False
                    elif ns == -1:
                        if os == 1:
                            axisDirection, axisInverted = 0, True
                        else:  # os == 0
                            axisDirection, axisInverted = -1, False
                    else:  # ns == 0
                        if os == 1:
                            axisDirection, axisInverted = 1, True
                        else:  # os == -1
                            axisDirection, axisInverted = -1, True
                    axisBind = GameControllerBind(
                        type=GameControllerBindType.AXIS,
                        axis=i,
                        axisDirection=axisDirection,
                        axisInverted=axisInverted,
                    )
                break

        if buttonBind is not None and axisBind is not None:
            if cls.preferButtonBindForItem(item):
                return buttonBind
            else:
                return axisBind
        elif buttonBind:
            return buttonBind
        elif axisBind:
            return axisBind
        else:
            return None

    # def getDeviceState(self, device: InputDevice) -> Optional[InputDeviceState]:
    #     device = self.inputService.findDeviceByGuid(self.deviceGuid)
    #     if device is None:
    #         return None
    #     return device.getState()

    def getNormalizedDeviceState(
        self, device: InputDeviceWithState
    ) -> NormalizedInputDeviceState:
        state = device.getState()
        normalizedState = NormalizedInputDeviceState(
            0, 0, 0, 0, copyFrom=state
        )
        for i in range(len(normalizedState.axes)):
            old = normalizedState.axes[i]
            new = 1.0 if old > 0.5 else -1.0 if old < -0.5 else 0.0
            normalizedState.axes[i] = new
        normalizedState.timeStamp = time.monotonic()
        return normalizedState

    def getMapItemFromLegacyName(self, name: str) -> GameControllerItem:
        assert name
        return {
            "south_button": GameControllerItem.A,
            "east_button": GameControllerItem.B,
            "select_button": GameControllerItem.BACK,
            "dpad_down": GameControllerItem.DPAD_DOWN,
            "dpad_left": GameControllerItem.DPAD_LEFT,
            "dpad_right": GameControllerItem.DPAD_RIGHT,
            "dpad_up": GameControllerItem.DPAD_UP,
            "menu_button": GameControllerItem.GUIDE,
            "left_shoulder": GameControllerItem.LEFTSHOULDER,
            "lstick_button": GameControllerItem.LEFTSTICK,
            "left_trigger": GameControllerItem.TRIGGERLEFT,
            "right_shoulder": GameControllerItem.RIGHTSHOULDER,
            "rstick_button": GameControllerItem.RIGHTSTICK,
            "right_trigger": GameControllerItem.TRIGGERRIGHT,
            "west_button": GameControllerItem.X,
            "north_button": GameControllerItem.Y,
            "start_button": GameControllerItem.START,
            # FIXME: Half-axes?
            "lstick_left": GameControllerItem.LEFTX,
            "lstick_right": GameControllerItem.LEFTX,
            "lstick_up": GameControllerItem.LEFTY,
            "lstick_down": GameControllerItem.LEFTY,
            # FIXME: Half-axes?
            "rstick_left": GameControllerItem.RIGHTX,
            "rstick_right": GameControllerItem.RIGHTX,
            "rstick_up": GameControllerItem.RIGHTY,
            "rstick_down": GameControllerItem.RIGHTY,
        }[name]

    def getItemLabel(self, item: GameControllerItem) -> str:
        return self.getItemLabels()[item]

    @memoize
    def getItemLabels(self) -> Dict[GameControllerItem, str]:
        """
        Memoized so translations are not looked up every time.
        """
        return {
            GameControllerItem.A: "South button",
            GameControllerItem.B: "East button",
            GameControllerItem.BACK: "Select/back",
            GameControllerItem.DPAD_DOWN: "D-pad down",
            GameControllerItem.DPAD_LEFT: "D-pad left",
            GameControllerItem.DPAD_RIGHT: "D-pad right",
            GameControllerItem.DPAD_UP: "D-pad up",
            GameControllerItem.GUIDE: "Menu/guide",
            GameControllerItem.LEFTSHOULDER: "Left shoulder",
            GameControllerItem.LEFTSTICK: "Left (press)",
            GameControllerItem.TRIGGERLEFT: "Left trigger",
            GameControllerItem.RIGHTSHOULDER: "Right shoulder",
            GameControllerItem.RIGHTSTICK: "Right (press)",
            GameControllerItem.TRIGGERRIGHT: "Right trigger",
            GameControllerItem.X: "West button",
            GameControllerItem.Y: "North button",
            GameControllerItem.START: "Start",
            GameControllerItem.LEFTX: "Left (horizontal)",
            GameControllerItem.LEFTY: "Left (vertical)",
            GameControllerItem.RIGHTX: "Right (horizontal)",
            GameControllerItem.RIGHTY: "Right (vertical)",
        }

    def startMapping(self) -> None:
        self.isMapping = True
        self.mapKey = self.oldPanel.map_key_name or ""
        self.mapItem = self.getMapItemFromLegacyName(self.mapKey)
        log.debug(
            "startMapping %r %r %r", self.deviceGuid, self.mapKey, self.mapItem
        )
        # self.initialState = self.getDeviceState()
        # if self.initialState == None:
        #     # Device is disconnected
        #     self.stopMapping()
        # print(self.initialState)
        self.initialStates.clear()
        self.currentStates.clear()
        for device in self.inputService.findDevicesByGuid(self.deviceGuid):
            self.initialStates[
                device.instanceId
            ] = self.getNormalizedDeviceState(device)

    def stopMapping(self) -> None:
        log.debug("stopMapping")
        self.isMapping = False
        self.mapKey = ""
        # self.initialState = None
        self.initialStates.clear()
        self.currentStates.clear()

        for panel in self.oldPanel.button_panels:
            panel.text = ""
            panel.refresh()


class OldControllerConfigPanel(fsui.Panel):
    # def __init__(self, parent: Optional[Widget], device: InputDevice):
    def __init__(self, parent: Widget, deviceGuid: str) -> None:
        # title = gettext("Configure {device_name}").format(
        #     device_name=device.name
        # )
        super().__init__(
            parent,
            # title=title,
            # minimizable=False,
            # maximizable=False,
            # separator=False,
        )

        self.style = Style(
            {
                "flewGrow": 1,
            }
        )

        # self.device = device
        self.deviceGuid = deviceGuid

        self.theme = WorkspaceTheme.instance()
        self.layout = fsui.VerticalLayout()

        self.image = fsui.Image("workspace:/data/gamepad-config.png")
        self.joystick_panel = fsui.ImageView(self, self.image)
        self.layout.add(self.joystick_panel)

        # if Skin.fws():
        #     from workspace.ui import TitleSeparator

        #     separator = TitleSeparator(self)
        #     self.layout.add(separator, fill=True)

        self.mapping_field = fsui.TextArea(
            self, read_only=True, line_wrap=False
        )
        self.mapping_field.setVisible(False)
        self.layout.add(
            self.mapping_field,
            fill=True,
            margin_left=20,
            margin_top=20,
            margin_right=20,
        )

        panel = fsui.Panel(self)
        self.layout.add(panel, fill=True)

        panel.layout = fsui.HorizontalLayout()
        panel.layout.padding = 20

        # self.device_type_ids = [
        #     "",
        #     "gamepad",
        #     "joystick",
        #     # "flightstick",
        #     "other",
        # ]
        # self.device_type_labels = [
        #     gettext("Choose Type"),
        #     gettext("Gamepad"),
        #     gettext("Digital Joystick"),
        #     # gettext("Flight Stick"),
        #     gettext("Other Device"),
        # ]

        # self.reset_button = fsui.Button(panel, gettext("Reset"))

        # self.clear_button = fsui.Button(panel, gettext("Clear"))
        # self.clear_button.activated.connect(self.on_clear_button)
        # panel.layout.add(self.clear_button)
        # self.clear_button.hide()

        # self.priority_type_ids = [
        #     "axis,hat,button",
        #     "hat,button,axis",
        # ]
        # self.priority_type_labels = [
        #     gettext("Axes, hats, buttons"),
        #     gettext("Hats, buttons, axes"),
        # ]
        # self.priority_choice = fsui.Choice(panel, self.priority_type_labels)
        # panel.layout.add(self.priority_choice, margin_left=20)

        # self.type_field = fsui.Choice(panel, self.device_type_labels)
        # panel.layout.add(self.type_field, margin_left=20)

        # panel.layout.add(
        #     fsui.PlainLabel(panel, gettext("Make:")), margin_left=20
        # )
        # self.make_field = fsui.TextField(panel)
        # self.make_field.set_min_width(140)
        # panel.layout.add(self.make_field, margin_left=10)

        panel.layout.add(
            fsui.PlainLabel(panel, gettext("Model:")), margin_left=0
        )
        self.model_field = fsui.TextField(panel)
        panel.layout.add(self.model_field, expand=True, margin_left=10)

        # self.reset_button = fsui.Button(panel, gettext("Revert"))
        # self.reset_button.activated.connect(self.on_reset_button)
        # panel.layout.add(self.reset_button, margin_left=20)
        # self.reset_button.hide()

        self.save_button = fsui.Button(panel, gettext("Save"))
        self.save_button.activated.connect(self.on_save_button)
        panel.layout.add(self.save_button, margin_left=20)

        # if self.window().theme.has_close_buttons:
        #     self.close_button = CloseButton(panel)
        #     panel.layout.add(self.close_button, margin_left=10)

        self.button_panels: List[MappingButton] = []
        for x, y, direction, name, item in BUTTONS:
            l = fsui.Label(
                self.joystick_panel, self.getParent().getItemLabel(item)
            )
            labelOffset = -16
            if direction < 0:
                # l.getMinSize
                l.set_position(x - 4 - l.getMinSize()[0], y + labelOffset)
            else:
                l.set_position(x + 4, y + labelOffset)
            b = MappingButton(self.joystick_panel, (x, y + 2), direction, name)
            self.button_panels.append(b)
            self.getParent().buttonForItem[item] = b
            # if name in existing_config:
            #     b.event_name = existing_config[name]

        # self.type_field.changed.connect(self.on_change)
        # self.make_field.changed.connect(self.on_change)
        # self.model_field.changed.connect(self.on_change)
        self.model_field.changed.connect(self.on_model_changed)

        self.map_key_name: Optional[str] = None

    def on_model_changed(self) -> None:
        self.getParent().mapping.name = self.model_field.get_text().strip()
        self.getParent().updateMapping()
        self.getParent().setDirty(True)

    # def on_clear_button(self):
    #     self.getParent().onClear()

    # def on_reset_button(self):
    #     self.getParent().onReset()

    def on_save_button(self) -> None:
        self.getParent().onSave()

    # def set_information(self, device_type, device_make, device_model):
    #     print(
    #         "set_information",
    #         repr(device_type),
    #         # repr(device_make),
    #         repr(device_model),
    #     )
    #     for i, d_type in enumerate(self.device_type_ids):
    #         print(d_type, device_type)
    #         if d_type == device_type:
    #             self.type_field.set_index(i)
    #             break
    #     else:
    #         self.type_field.set_index(0)
    #     # self.make_field.set_text(device_make)
    #     self.model_field.set_text(device_model)

    def map_event(self, name: str) -> None:
        self.map_key_name = name
        for buttonPanel in self.button_panels:
            if self.map_key_name == buttonPanel.key_name:
                # buttonPanel.text = "use joystick"
                buttonPanel.text = "use and hold"
                buttonPanel.refresh()
            elif buttonPanel.text:
                buttonPanel.text = ""
                buttonPanel.refresh()
        # self.initial_state = self.get_state()

    # def get_state(self) -> None:
    #     return self.current_state.copy()

    def set_result(self, event_name: str) -> None:
        for panel in self.button_panels:
            if self.map_key_name == panel.key_name:
                panel.event_name = event_name
            elif panel.event_name == event_name:
                # remove event from other panel(s)
                panel.event_name = None
            panel.text = ""
            panel.refresh()

        self.map_key_name = None
        # self.on_change()

    # def priority_order(self):
    #     priority_order = self.priority_type_ids[self.priority_choice.index()]
    #     k = 0
    #     result = {}
    #     for item in priority_order.split(","):
    #         item = item.strip()
    #         result[item] = k
    #         k += 1
    #     return result


BUTTONS: List[Tuple[int, int, Literal[-1, 1], str, GameControllerItem]] = [
    (160, 240, -1, "dpad_left", GameControllerItem.DPAD_LEFT),
    (160, 160, -1, "dpad_right", GameControllerItem.DPAD_RIGHT),
    (160, 200, -1, "dpad_up", GameControllerItem.DPAD_UP),
    (160, 280, -1, "dpad_down", GameControllerItem.DPAD_DOWN),
    # (160, 400, -1, "lstick_left", GameControllerItem.LEFTX_NEG),
    # (320, 400, -1, "lstick_right", GameControllerItem.LEFTX_POS),
    # (160, 360, -1, "lstick_up", GameControllerItem.LEFTY_NEG),
    # (160, 440, -1, "lstick_down", GameControllerItem.LEFTY_POS),
    (350, 400, -1, "lstick_right", GameControllerItem.LEFTX),
    (350, 440, -1, "lstick_down", GameControllerItem.LEFTY),
    (190, 440, -1, "lstick_button", GameControllerItem.LEFTSTICK),
    # (480, 400, 1, "rstick_left", GameControllerItem.RIGHTX_NEG),
    # (640, 400, 1, "rstick_right", GameControllerItem.RIGHTX_POS),
    # (640, 360, 1, "rstick_up", GameControllerItem.RIGHTY_NEG),
    # (640, 440, 1, "rstick_down", GameControllerItem.RIGHTY_POS),
    (450, 400, 1, "rstick_right", GameControllerItem.RIGHTX),
    (450, 440, 1, "rstick_down", GameControllerItem.RIGHTY),
    (610, 440, 1, "rstick_button", GameControllerItem.RIGHTSTICK),
    (640, 160, 1, "west_button", GameControllerItem.X),
    (640, 200, 1, "north_button", GameControllerItem.Y),
    (640, 240, 1, "east_button", GameControllerItem.B),
    (640, 280, 1, "south_button", GameControllerItem.A),
    (350, 80, -1, "select_button", GameControllerItem.BACK),
    (450, 80, 1, "start_button", GameControllerItem.START),
    (450, 40, 1, "menu_button", GameControllerItem.GUIDE),
    (160, 40, -1, "left_shoulder", GameControllerItem.LEFTSHOULDER),
    (160, 80, -1, "left_trigger", GameControllerItem.TRIGGERLEFT),
    (640, 40, 1, "right_shoulder", GameControllerItem.RIGHTSHOULDER),
    (640, 80, 1, "right_trigger", GameControllerItem.TRIGGERRIGHT),
]
HELP_TEXT = """
INSTRUCTIONS

The joysticks listed are those connected when you started the program.
If you connect more, you must restart the program!

Your gamepad may not look exactly like this, so just try to map the buttons
as closely as possibly.

Some gamepads do not have a "menu" button or similar, in which case you can
skip configuring this.

Some gamepads have the d-pad and left stick physically swapped. This is not
a problem, just map the d-pad buttons against the d-pad etc.

Left and right trigger buttons are located *below* left and right shoulder
buttons.
"""
