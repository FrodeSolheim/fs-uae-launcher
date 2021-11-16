from typing import List, Optional, Tuple

from typing_extensions import Literal

import fsui
from fsgamesys.input.gamecontroller import GameControllerItem
from fswidgets.widget import Widget
from launcher.fswidgets2.style import Style
from launcher.i18n import gettext
from system.tools.controllerconfig.mappingbutton import MappingButton
from workspace.ui.theme import WorkspaceTheme


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
