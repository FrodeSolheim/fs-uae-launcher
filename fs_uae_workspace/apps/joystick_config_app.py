import os
import io
import threading
import traceback
import weakref
import subprocess
from fsbc.Application import Application
from configparser import ConfigParser
from fsbc.system import platform
from fs_uae_launcher.DeviceManager import DeviceManager
from fsgs.amiga.FSUAEDeviceHelper import FSUAEDeviceHelper
import fsui
from fsgs.FSGSDirectories import FSGSDirectories
from fs_uae_workspace.shell import register_window, raise_window

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


class Button(fsui.Panel):

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


class JoystickConfigWindow(fsui.Window):

    def __init__(self, device_name):
        fsui.Window.__init__(
            self, None, "Configure {device_name}".format(
                device_name=device_name))
        # self.set_destroy_on_close()

        self.layout = fsui.VerticalLayout()
        self.device_name = device_name

        self.image = fsui.Image("fs_uae_workspace:res/gamepad-config.png")
        self.joystick_panel = fsui.ImageView(self, self.image)
        self.layout.add(self.joystick_panel)

        # self.status_label = fsui.Label(self, "")
        # self.layout.add(self.status_label, fill=True)

        parser = ConfigParser()
        config_file = self.get_load_path()
        existing_config = {}
        if config_file is not None:
            try:
                with open(config_file, "r", encoding="UTF-8") as f:
                    parser.read_file(f)
                if parser.has_section("default"):
                    for key in parser.options("default"):
                        value = parser.get("default", key)
                        existing_config[value] = key
            except Exception:
                # ignore failures loading the config
                traceback.print_exc()

        self.button_panels = []
        for x, y, direction, name in BUTTONS:
            b = Button(self.joystick_panel, (x, y + 4), direction, name)
            self.button_panels.append(b)
            if name in existing_config:
                b.event_name = existing_config[name]

        self.map_key_name = None
        fsui.call_later(100, self.on_timer_callback)

        self.stopped = False
        self.current_state = {}

        # self.closed.connect(self.__closed)
        # return

        thread = threading.Thread(
            target=event_thread, name="JoystickConfigEventThread",
            args=(self.device_name, weakref.ref(self),))
        thread.start()

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

    def __del__(self):
        print("JoystickConfigWindow.__del__")

    def on_close(self):
        print("on_close")
        self.stopped = True

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
        # self.status_label.set_text(
        #     "Perform a joystick action to map {name}".format(
        #         name=self.map_key_name))

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

        # self.status_label.set_text("")
        self.map_key_name = None
        self.save_config()

    def on_timer_callback(self):
        if self.map_key_name:
            state = self.get_state()
            # print(state)
            for key, value in self.initial_state.items():
                # we check initial state because some axes may have non-zero
                # rest values... (i.e. full negative)
                if state[key] and state[key] != self.initial_state[key]:
                    self.set_result(key)

        # if not self.is_shown():
        if self.stopped:
            return
        # continue timer
        fsui.call_later(100, self.on_timer_callback)

    def get_joystick_id(self):
        # if "#" in self.device_name:
        device_name = self.device_name.rsplit("#", 1)[0]
        # else:
        #     device_name = self.device_name

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

    def get_load_path(self):
        path = self.get_save_path()
        if os.path.exists(path):
            return path
        # FIXME: return bundled config path (fallback)

        # returning None if no config could be found
        return None

    def get_save_path(self):
        file_name = self.get_joystick_id() + ".conf"
        dest = FSGSDirectories.get_controllers_dir()
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest = os.path.join(dest, file_name)
        return dest

    def save_config(self):
        device_name = self.device_name.rsplit("#", 1)[0]

        config = ["# {0}".format(device_name),
                  "",
                  "[device]",
                  "name = {0}".format(device_name),
                  "type = unspecified",
                  "",
                  "[default]",
                  "include = universal_gamepad"]

        # config.append("# buttons: {0}".format(
        #     current_joystick.get_numbuttons()))
        # config.append("# axes: {0}".format(
        #     current_joystick.get_numaxes()))
        # config.append("# hats: {0}".format(current_joystick.get_numhats()))
        # config.append("# balls: {0}".format(current_joystick.get_numballs()))
        # config.append("# platform: {0}".format(platform))

        button_config = []
        for i, button in enumerate(BUTTONS):
            panel = self.button_panels[i]
            if panel.event_name:
                button_config.append("{0} = {1}".format(
                    panel.event_name, button[3]))
        config.extend(sorted(button_config))

        f = io.open(self.get_save_path(), "w", encoding="UTF-8")
        for line in config:
            f.write(line)
            f.write("\n")
        f.close()


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


help_text = """
INSTRUCTIONS

The joysticks listed are those connected when you started the program. If you connect more, you must restart the program!

Your gamepad may not look exactly like this, so just try to map the buttons as closely as possibly.

Some gamepads do not have a "menu" button or similar, in which case you can skip configuring this.

Some gamepads have the d-pad and left stick physically swapped. This is not a problem, just map the d-pad buttons against the d-pad etc.

Left and right trigger buttons are located *below* left and right shoulder buttons.

"""


def application(uri, args):
    fake_uri = uri + repr(args)
    if not raise_window(fake_uri):
        window = JoystickConfigWindow(args[0])
        window.show()
        register_window(fake_uri, window)
