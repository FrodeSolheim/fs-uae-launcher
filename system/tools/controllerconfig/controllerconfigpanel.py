import logging
import time
from typing import Dict, Optional

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
from system.tools.controllerconfig.mappingbutton import MappingButton
from system.tools.controllerconfig.oldcontrollerconfigpanel import (
    OldControllerConfigPanel,
)

log = logging.getLogger(__name__)


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
