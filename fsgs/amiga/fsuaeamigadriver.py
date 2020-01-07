import os

from fsbc.application import app
from fsbc.settings import Settings
from fsgs import Option
from fsgs.amiga.amiga import Amiga
from fsgs.amiga.fsuae import FSUAE
from fsgs.amiga.launchhandler import LaunchHandler
from fsgs.drivers.gamedriver import GameDriver, Emulator
from launcher.version import VERSION

AMIGA_JOYSTICK = {
    "type": "joystick",
    "description": "Joystick",
    "mapping_name": "amiga",
}
AMIGA_MOUSE = {
    "type": "mouse",
    "description": "Mouse",
    "mapping_name": "amiga_mouse",  # FIXME ...
}
CD32_CONTROLLER = {
    "type": "cd32 gamepad",
    "description": "CD32 Gamepad",
    "mapping_name": "cd32",
}
# FIXME: NO_DEVICE
AMIGA_PORTS = [
    {
        "description": "Joystick Port",
        "types": [AMIGA_JOYSTICK, AMIGA_MOUSE, CD32_CONTROLLER],
        "type_option": "joystick_port_1_mode",
        "device_option": "joystick_port_1",
    },
    {
        "description": "Mouse Port",
        "types": [AMIGA_JOYSTICK, AMIGA_MOUSE, CD32_CONTROLLER],
        "type_option": "joystick_port_0_mode",
        "device_option": "joystick_port_0",
    },
    # FIXME: ADDITIONAL PORTS...
]


class FSUAEAmigaDriver(GameDriver):
    PORTS = AMIGA_PORTS

    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.temp_config_file = None
        self.launch_handler = None

        emulator = self.options[Option.AMIGA_EMULATOR]
        if emulator == "fs-uae-3.0":
            self.emulator = Emulator("fs-uae-3.0")
        elif emulator == "fs-uae-2.8":
            self.emulator = Emulator("fs-uae-2.8")
        else:
            self.emulator = Emulator("fs-uae")

    def prepare(self):
        print("FSUAEAmigaDriver.prepare")

        if not self.options["joystick_port_0_mode"]:
            self.options["joystick_port_0_mode"] = "mouse"
        if not self.options["joystick_port_1_mode"]:
            if self.options["amiga_model"].startswith("CD32"):
                self.options["joystick_port_1_mode"] = "cd32 gamepad"
            else:
                self.options["joystick_port_1_mode"] = "joystick"
        if not self.options["joystick_port_2_mode"]:
            self.options["joystick_port_2_mode"] = "none"
        if not self.options["joystick_port_3_mode"]:
            self.options["joystick_port_3_mode"] = "none"

        from launcher.devicemanager import DeviceManager

        devices = DeviceManager.get_devices_for_ports(self.options)
        for port in range(4):
            key = "joystick_port_{0}".format(port)
            if not self.options[key]:
                # key not set, use calculated default value
                self.options[key] = devices[port].id

        for remove_key in [
            "database_username",
            "database_password",
            "database_username",
            "database_email",
            "database_auth",
            "device_id",
        ]:
            if remove_key in self.options:
                del self.options[remove_key]

        # overwrite netplay config

        if self.options["__netplay_host"]:
            self.options["netplay_server"] = self.options["__netplay_host"]
        if self.options["__netplay_password"]:
            self.options["netplay_password"] = self.options[
                "__netplay_password"
            ]
        if self.options["__netplay_port"]:
            self.options["netplay_port"] = self.options["__netplay_port"]

        # copy actual kickstart options from x_ options

        self.options["kickstart_file"] = self.options["x_kickstart_file"]
        self.options["kickstart_ext_file"] = self.options[
            "x_kickstart_ext_file"
        ]

        if not self.options["kickstart_file"]:
            # Warning will have been shown on the status bar
            self.options["kickstart_file"] = "internal"

        # Copy default configuration values from model defaults. The main
        # purpose of this is to let the launch code know about implied defaults
        # so it can for example configure correct ROM files for expansions.

        model_config = Amiga.get_current_config(self.options)
        for key, value in model_config["defaults"].items():
            if not self.options[key]:
                self.options[key] = value

        # make sure FS-UAE does not load other config files (Host.fs-uae)
        self.options["end_config"] = "1"
        # Make FS-UAE check that version matches (except for development)
        if VERSION != "9.8.7dummy":
            self.options[Option.EXPECT_VERSION] = VERSION

        if self.options["__netplay_game"]:
            print("\nfixing config for netplay game")
            for key in [x for x in config.keys() if x.startswith("uae_")]:
                print("* removing option", key)
                del self.options[key]

        # self.temp_dir = self.fsgc.temp_dir("amiga")

        # self.change_handler = GameChangeHandler(self.temp_dir)

        # self.firmware_dir = self.prepare_firmware("Amiga Firmware")
        # config = self.fsgc.config.copy()

        model = self.options[Option.AMIGA_MODEL]
        if model.startswith("CD32"):
            platform = "CD32"
        elif model == "CDTV":
            platform = "CDTV"
        else:
            platform = "Amiga"
        # name = Settings.get("config_name")
        # name = self.fsgc.game.name

        # uuid = Config.get("x_game_uuid")
        # uuid = None

        from fsgs.saves import SaveHandler

        # save_state_handler = SaveHandler(self.fsgc, self.get_name(), platform)
        save_state_handler = SaveHandler(
            self.fsgc,
            app.settings.get("config_name"),
            platform,
            options=self.options,
        )

        print(
            "[INPUT] joystick_port_1",
            self.options["joystick_port_1"],
            "->",
            self.ports[0].device_id or "none",
        )
        print(
            "[INPUT] joystick_port_0",
            self.options["joystick_port_0"],
            "->",
            self.ports[1].device_id or "none",
        )
        # self.options["joystick_port_1"] = self.ports[0].device_id or "none"
        # self.options["joystick_port_0"] = self.ports[1].device_id or "none"

        self.launch_handler = LaunchHandler(
            self.fsgc,
            self.get_name(),
            self.options,
            save_state_handler,
            temp_dir=self.cwd.path,
        )

        # self.change_handler.init(self.fsgc.get_game_state_dir(),
        #         ignore=["*.uss", "*.sdf"])

        # self.launch_handler.config["joystick_port_0"] = \
        #         self.inputs[1].device_id
        # self.launch_handler.config["joystick_port_1"] = \
        #         self.inputs[0].device_id

        if self.use_fullscreen():
            self.launch_handler.config["fullscreen"] = "1"
            if not self.launch_handler.config.get("fullscreen_mode", ""):
                # Check if fullscreen mode is overridden by temporary setting.
                if Settings.instance()["__fullscreen_mode"]:
                    self.launch_handler.config[
                        "fullscreen_mode"
                    ] = Settings.instance()["__fullscreen_mode"]
            if Settings.instance()["__arcade"]:
                # Remove window border when launched from FS-UAE Arcade in
                # order to reduce flickering
                self.launch_handler.config["window_border"] = "0"
                # Set fade out duration to 500, if not already specified.
                if not self.launch_handler.config.get("fade_out_duration", ""):
                    self.launch_handler.config["fade_out_duration"] = "500"
        else:
            self.launch_handler.config["fullscreen"] = "0"

        self.launch_handler.prepare()

        config = self.launch_handler.create_config()
        config_file = self.temp_file("config.fs-uae").path
        with open(config_file, "w", encoding="UTF-8") as f:
            for line in config:
                print(line)
                f.write(line + "\n")
        self.emulator.args.extend([config_file])

    # def configure(self):
    #     print("AmigaGameHandler.configure")
    #
    #     #temp_dir = self.fsgc.temp.dir("amiga-config")
    #     #config_file = os.path.join(temp_dir, "amiga-config.fs-uae")
    #     #with open(config_file, "wb") as f:
    #     #    #self._configure_emulator(f)
    #     #    self.launch_handler.write_config(f)
    #     #    self.write_additional_config(f)#
    #     #
    #     ##self.args.extend(["--config", config_file])
    #     #self.args.extend([config_file])

    # def write_additional_config(self, f):
    #     #if self.get_option("fullscreen"):
    #     #    f.write("fullscreen = 1\n")
    #
    #     #if self.configure_vsync():
    #     #    f.write("video_sync = full\n")
    #     #else:
    #     #    f.write("video_sync = none\n")
    #
    #     if self.get_option("fsaa"):
    #         f.write("fsaa = {0}\n".format(str(self.get_option("fsaa"))))

    # def run(self):
    #     print("FSUAEAmigaDriver.run, cwd =", self.cwd.path)
    #     config = self.launch_handler.create_config()
    #     self.emulator.process, self.temp_config_file = FSUAE.start_with_config(
    #         config, cwd=self.cwd.path
    #     )
    #     self.write_emulator_pid_file(
    #         self.emulator_pid_file(), self.emulator.process
    #     )

    def finish(self):
        print("FSUAEAmigaDriver.finish: Removing", self.temp_config_file)
        if self.temp_config_file is not None:
            try:
                os.remove(self.temp_config_file)
            except Exception:
                print("Could not remove config file", self.temp_config_file)

        self.launch_handler.update_changes()
        self.launch_handler.cleanup()
        # self.change_handler.update(self.fsgc.get_game_state_dir())

    def get_game_refresh_rate(self):
        # FIXME: Now assuming that all games are PAL / 50 Hz
        # - make configurable?
        return 50.0

    def get_supported_filters(self):
        supported = []
        # supported = [{
        #         "name": "2x",
        #         "gfx_filter": "none",
        #         "line_double": True,
        #         "lores": False,
        #     }, {
        #         "name": "none",
        #         "gfx_filter": "none",
        #         "line_double": False,
        #         "lores": False,
        #     }, {
        #         "name": "pal",
        #         "gfx_filter": "pal",
        #         "line_double": True,
        #         "lores": False,
        #     }, {
        #         "name": "scale2x",
        #         "gfx_filter": "scale2x",
        #         "line_double": False,
        #         "lores": True,
        #     }, {
        #         "name": "hq2x",
        #         "gfx_filter": "hq2x",
        #         "line_double": False,
        #         "lores": True,
        #     }
        # ]
        return supported

    # def set_input_options(self, f):
    #     # FIXME
    #     input_mapping = [{
    #         "1": "JOY2_FIRE_BUTTON",
    #         "2": "JOY2_2ND_BUTTON",
    #         "3": "JOY2_3RD_BUTTON",
    #         "left": "JOY2_LEFT",
    #         "right": "JOY2_RIGHT",
    #         "up": "JOY2_UP",
    #         "down": "JOY2_DOWN",
    #     }, {
    #         "1": "JOY1_FIRE_BUTTON",
    #         "2": "JOY1_2ND_BUTTON",
    #         "3": "JOY1_3RD_BUTTON",
    #         "left": "JOY1_LEFT",
    #         "right": "JOY1_RIGHT",
    #         "up": "JOY1_UP",
    #         "down": "JOY1_DOWN",
    #     }]
    #
    #     f.write("\n[input]\n")
    #
    #     for i, port in enumerate(self.ports):
    #         if not port.device:
    #             continue
    #         if i == 0:
    #             key = "joystick_port_1"
    #         else:
    #             key = "joystick_port_0"
    #         if port.type == "amiga_mouse":
    #             value = "mouse"
    #         else:
    #             value = port.device.id
    #         print("[INPUT] Configure device:", key, value)
    #         f.write("{0} = {1}\n".format(key, value))

    # def find_kickstart(self, bios_patterns):
    #     print("find_kickstart", bios_patterns)
    #     for name in os.listdir(self.firmware_dir):
    #         for bios in bios_patterns:
    #             if bios in name:
    #                 return os.path.join(self.firmware_dir, name)
    #     raise Exception("Could not find Amiga bios/kickstart " +
    #                     repr(bios_patterns))
