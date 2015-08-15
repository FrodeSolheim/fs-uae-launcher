import os
import threading
import traceback
import weakref
import subprocess
from io import TextIOWrapper
from fsbc.Application import Application
from configparser import ConfigParser
from fsbc.system import platform
from fs_uae_launcher.DeviceManager import DeviceManager
from fsgs.amiga.FSUAEDeviceHelper import FSUAEDeviceHelper
from fsgs.input.inputdevice import InputDevice
import fsui
from fsgs.FSGSDirectories import FSGSDirectories
from fs_uae_workspace.shell import register_window, raise_window
from fs_uae_launcher.I18N import gettext


class JoystickConfigWindow(fsui.Window):

    def __init__(self, device_name):
        fsui.Window.__init__(self, None, "Configure {device_name}".format(
            device_name=device_name))

        self.layout = fsui.VerticalLayout()

        self.image = fsui.Image("fs_uae_workspace:res/gamepad-config.png")
        self.joystick_panel = fsui.ImageView(self, self.image)
        self.layout.add(self.joystick_panel)

        panel = fsui.Panel(self)
        self.layout.add(panel, fill=True)

        panel.layout = fsui.HorizontalLayout()
        panel.layout.padding = 20

        self.device_type_ids = [
            "",
            "gamepad",
            "joystick",
            # "flightstick",
            "other",
        ]
        self.device_type_labels = [
            gettext("Choose Type"),
            gettext("Gamepad"),
            gettext("Digital Joystick"),
            # gettext("Flight Stick"),
            gettext("Other Device"),
        ]

        self.type_field = fsui.Choice(panel, self.device_type_labels)
        self.type_field.changed.connect(self.on_change)
        panel.layout.add(self.type_field)

        panel.layout.add(fsui.PlainLabel(
            panel, gettext("Make:")), margin_left=20)
        self.make_field = fsui.TextField(panel)
        self.make_field.set_min_width(100)
        self.make_field.changed.connect(self.on_change)
        panel.layout.add(self.make_field, margin_left=10)

        panel.layout.add(fsui.PlainLabel(
            panel, gettext("Model:")), margin_left=20)
        self.model_field = fsui.TextField(panel)
        self.model_field.changed.connect(self.on_change)
        panel.layout.add(self.model_field, expand=True, margin_left=10)

        self.save_button = fsui.Button(panel, gettext("Save"))
        self.save_button.activated.connect(self.on_save_button)
        panel.layout.add(self.save_button, margin_left=20)

        self.close_button = fsui.Button(panel, gettext("Close"))
        self.close_button.activated.connect(self.on_close_button)
        panel.layout.add(self.close_button, margin_left=10)

        self.device_name = device_name
        existing_config = self.read_existing_config()

        self.button_panels = []
        for x, y, direction, name in BUTTONS:
            b = MappingButton(self.joystick_panel, (x, y + 4), direction, name)
            self.button_panels.append(b)
            if name in existing_config:
                b.event_name = existing_config[name]

        self.save_button.disable()
        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        self.stopped = False
        self.current_state = {}
        self.initial_state = {}
        self.map_key_name = None

        fsui.call_later(100, self.on_timer_callback)
        thread = threading.Thread(
            target=event_thread, name="JoystickConfigEventThread",
            args=(self.device_name, weakref.ref(self),))
        thread.start()

    def __del__(self):
        print("JoystickConfigWindow.__del__")

    def on_change(self):
        self.save_button.enable()

    def on_close(self):
        print("on_close")
        self.stopped = True

    def on_save_button(self):
        self.save_config()
        self.save_button.disable()

    def on_close_button(self):
        self.close()

    def set_information(self, device_type, device_make, device_model):
        print("set_information", repr(device_type), repr(device_make),
              repr(device_model))
        for i, d_type in enumerate(self.device_type_ids):
            print(d_type, device_type)
            if d_type == device_type:
                self.type_field.set_index(i)
                break
        else:
            self.type_field.set_index(0)
        self.make_field.set_text(device_make)
        self.model_field.set_text(device_model)

    def read_existing_config(self):
        config_file = self.get_load_path()
        if config_file is not None:
            with open(config_file, "r", encoding="UTF-8") as f:
                return self.read_existing_config_from_stream(f)
        try:
            stream = InputDevice.get_builtin_config_for_device_guid(
                self.get_joystick_guid())
            print("found builtin config for", self.get_joystick_guid())
        except LookupError:
            return {}
        else:
            with TextIOWrapper(stream, "UTF-8") as f:
                return self.read_existing_config_from_stream(f)

    def read_existing_config_from_stream(self, f):
        existing_config = {}
        parser = ConfigParser()
        try:
            parser.read_file(f)
            if parser.has_section("default"):
                for key in parser.options("default"):
                    value = parser.get("default", key)
                    existing_config[value] = key
            if parser.has_section("device"):
                device_type = parser.get("device", "type", fallback="")
                device_make = parser.get("device", "make", fallback="")
                device_model = parser.get("device", "model", fallback="")
                self.set_information(device_type, device_make, device_model)
        except Exception:
            # ignore failures loading the config
            traceback.print_exc()
        return existing_config

    # def __closed(self):
    #     print("JoystickConfigWindow.__closed")
    #     self.stopped = True
    #     # self.destroy()
    #     # self.button_panels = []

    def map_event(self, name):
        self.map_key_name = name
        for panel in self.button_panels:
            if self.map_key_name == panel.key_name:
                panel.text = "use joystick"
                panel.refresh()
            elif panel.text:
                panel.text = ""
                panel.refresh()
        self.initial_state = self.get_state()

    def get_state(self):
        return self.current_state.copy()

    def set_result(self, event_name):
        for panel in self.button_panels:
            if self.map_key_name == panel.key_name:
                panel.event_name = event_name
            elif panel.event_name == event_name:
                # remove event from other panel(s)
                panel.event_name = None
            panel.text = ""
            panel.refresh()

        self.map_key_name = None
        self.on_change()

    def on_timer_callback(self):
        if self.map_key_name:
            state = self.get_state()
            for key, value in self.initial_state.items():
                # we check initial state because some axes may have non-zero
                # rest values... (i.e. full negative)
                if state[key] and state[key] != self.initial_state[key]:
                    self.set_result(key)
        if self.stopped:
            return
        # continue timer
        fsui.call_later(100, self.on_timer_callback)

    def get_joystick_id(self):
        device_name = self.device_name.rsplit("#", 1)[0]
        buttons = DeviceManager.joystick_buttons(self.device_name)
        axes = DeviceManager.joystick_axes(self.device_name)
        hats = DeviceManager.joystick_hats(self.device_name)
        balls = DeviceManager.joystick_balls(self.device_name)
        name_lower = device_name.lower()
        name = ""
        for c in name_lower:
            if c in "abcdefghijklmnopqrstuvwxyz0123456789":
                name = name + c
            else:
                if not name.endswith("_"):
                    name += "_"
        name = name.strip("_")
        return "{0}_{1}_{2}_{3}_{4}_{5}".format(
            name, buttons, axes, hats, balls, platform)

    def get_joystick_guid(self):
        return DeviceManager.joystick_guid(self.device_name)

    def get_load_path(self):
        path = self.get_save_path(
            self.get_joystick_guid() + ".fs-uae-controller")
        if os.path.exists(path):
            print("JoystickConfigWindow.get_load_path found", path)
            return path
        path = self.get_save_path(self.get_joystick_id() + ".conf")
        if os.path.exists(path):
            print("JoystickConfigWindow.get_load_path found", path)
            return path
        return None

    def get_save_path(self, file_name):
        dest = FSGSDirectories.get_controllers_dir()
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest = os.path.join(dest, file_name)
        return dest

    def save_config(self):
        device_name = self.device_name.rsplit("#", 1)[0]
        device_type = self.device_type_ids[self.type_field.get_index()]
        device_make = self.make_field.get_text().strip()
        device_model = self.model_field.get_text().strip()
        guid = DeviceManager.joystick_guid(self.device_name)
        buttons = DeviceManager.joystick_buttons(self.device_name)
        axes = DeviceManager.joystick_axes(self.device_name)
        hats = DeviceManager.joystick_hats(self.device_name)
        balls = DeviceManager.joystick_balls(self.device_name)
        config = [
            "[fs-uae-controller]",
            "name = {}".format(device_name),
            "platform = {}".format(platform),
            "",
            "[device]",
            "make = {}".format(device_make),
            "model = {}".format(device_model),
            "type = {}".format(device_type),
            "",
            "[sdl]",
            "guid = {}".format(guid),
            "buttons = {}".format(buttons),
            "hats = {}".format(hats),
            "axes = {}".format(axes),
            "balls = {}".format(balls),
            "",
            "[default]",
            "include = universal_gamepad"
        ]
        button_config = []
        for i, button in enumerate(BUTTONS):
            panel = self.button_panels[i]
            if panel.event_name:
                button_config.append("{0} = {1}".format(
                    panel.event_name, button[3]))
        config.extend(sorted(button_config))
        with open(self.get_save_path(self.get_joystick_id() + ".conf"),
                  "w", encoding="UTF-8") as f:
            for line in config:
                f.write(line)
                f.write("\n")
        if len(guid) == 32:
            with open(self.get_save_path(guid + ".fs-uae-controller"),
                      "w", encoding="UTF-8") as f:
                for line in config:
                    f.write(line)
                    f.write("\n")


class MappingButton(fsui.Panel):

    def __init__(self, parent, position, direction, name):
        fsui.Panel.__init__(self, parent)

        size = (120, 22)
        self.set_size(size)
        if direction < 0:
            position = (position[0] - size[0], position[1])
        self.set_position(position)

        self.key_name = name
        self.event_name = None
        self.text = ""
        self.direction = direction

        self.set_hand_cursor()
        self.set_background_color(fsui.Color(0xff, 0xff, 0xff))

    def on_left_down(self):
        print("on_left_down")
        self.get_window().map_event(self.key_name)

    def on_paint(self):
        dc = self.create_dc()
        dc.set_font(self.get_font())  # SetFont(self.GetFont())
        if self.text:
            text = self.text
            dc.set_text_color(fsui.Color(0x00, 0x80, 0x00))
        elif self.event_name:
            text = self.event_name
            dc.set_text_color(fsui.Color(0x80, 0x80, 0x80))
        else:
            text = "click to configure"
            dc.set_text_color(fsui.Color(0xff, 0x00, 0x00))
        tw, th = dc.measure_text(text)
        y = (self.get_size()[1] - th) / 2
        if self.direction > 0:
            x = 4
        else:
            x = self.get_size()[0] - 4 - tw
        dc.draw_text(text, x, y)


def event_thread(device_name, window_ref):
    process = FSUAEDeviceHelper.start_with_args(
        [device_name], stdout=subprocess.PIPE)

    # while not self.stopped and \
    while not Application.instance().stopping():
        # print("stopping?", Application.instance().stopping())
        window = window_ref()
        if window is None:
            print("window was None")
            break

        line = process.stdout.readline()
        line = line.decode("UTF-8", errors="replace")
        line = line.strip()
        parts = line.split(" ")
        if len(parts) < 2:
            continue
        type = parts[1]
        states = parts[2:]
        update = window.current_state

        if type == "buttons":
            for i, state in enumerate(states):
                state = int(state)
                update["button_{0}".format(i)] = state

        elif type == "axes":
            for i, state in enumerate(states):
                state = int(state)
                update["axis_" + str(i) + "_pos"] = state > 20000
                update["axis_" + str(i) + "_neg"] = state < -20000

        elif type == "hats":
            for i, state in enumerate(states):
                state = int(state)
                update["hat_" + str(i) + "_left"] = state & HAT_LEFT
                update["hat_" + str(i) + "_right"] = state & HAT_RIGHT
                update["hat_" + str(i) + "_up"] = state & HAT_UP
                update["hat_" + str(i) + "_down"] = state & HAT_DOWN

        # make sure references are freed in every loop iteration, so the
        # Window will get refcount 0 when it is closed.
        del update
        del window

    process.kill()


HAT_UP = 0x01
HAT_RIGHT = 0x02
HAT_DOWN = 0x04
HAT_LEFT = 0x08
BUTTONS = [
    (160, 240, -1, "dpad_left"),
    (160, 160, -1, "dpad_right"),
    (160, 200, -1, "dpad_up"),
    (160, 280, -1, "dpad_down"),

    (160, 400, -1, "lstick_left"),
    (320, 400, -1, "lstick_right"),
    (160, 360, -1, "lstick_up"),
    (160, 440, -1, "lstick_down"),
    (320, 440, -1, "lstick_button"),

    (480, 400, 1, "rstick_left"),
    (640, 400, 1, "rstick_right"),
    (640, 360, 1, "rstick_up"),
    (640, 440, 1, "rstick_down"),
    (480, 440, 1, "rstick_button"),

    (640, 160, 1, "west_button"),
    (640, 200, 1, "north_button"),
    (640, 240, 1, "east_button"),
    (640, 280, 1, "south_button"),

    (320, 80, -1, "select_button"),
    (480, 80, 1, "start_button"),
    (480, 40, 1, "menu_button"),

    (160, 40, -1, "left_shoulder"),
    (160, 80, -1, "left_trigger"),
    (640, 40, 1, "right_shoulder"),
    (640, 80, 1, "right_trigger"),
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


def application(uri, args):
    fake_uri = uri + repr(args)
    if not raise_window(fake_uri):
        window = JoystickConfigWindow(args[0])
        window.show()
        register_window(fake_uri, window)
