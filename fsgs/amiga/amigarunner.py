import os

from fsbc.settings import Settings
from fsgs.runner import GameRunner
from fsgs.amiga.FSUAE import FSUAE
from fsgs.amiga.LaunchHandler import LaunchHandler


class AmigaRunner(GameRunner):

    JOYSTICK = {
        "type": "joystick",
        "description": "Joystick",
        "mapping_name": "amiga",
    }

    MOUSE = {
        "type": "mouse",
        "description": "Mouse",
        "mapping_name": "amiga_mouse",  # FIXME ...
    }

    PORTS = [
        {
            "description": "Joystick Port",
            "types": [JOYSTICK]
        }, {
            "description": "Mouse Port",
            "types": [MOUSE, JOYSTICK]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.temp_config_file = None
        self.launch_handler = None

    def prepare(self):
        print("AmigaRunner.prepare")

        # self.temp_dir = self.fsgs.temp_dir("amiga")

        # self.change_handler = GameChangeHandler(self.temp_dir)

        # self.firmware_dir = self.prepare_firmware("Amiga Firmware")
        # config = self.fsgs.config.copy()

        model = self.config["amiga_model"]
        if model.startswith("CD32"):
            platform = "CD32"
        elif model == "CDTV":
            platform = "CDTV"
        else:
            platform = "Amiga"
        # name = Settings.get("config_name")
        # name = self.fsgs.game.name

        # uuid = Config.get("x_game_uuid")
        # uuid = None

        from fsgs.SaveStateHandler import SaveStateHandler
        save_state_handler = SaveStateHandler(
            self.fsgs, self.get_name(), platform)

        self.config["joystick_port_0"] = self.ports[1].device_id or ""
        self.config["joystick_port_1"] = self.ports[0].device_id or ""

        self.launch_handler = LaunchHandler(
            self.fsgs, self.get_name(), self.config, save_state_handler,
            temp_dir=self.cwd.path)

        # self.change_handler.init(self.fsgs.get_game_state_dir(),
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
                    self.launch_handler.config["fullscreen_mode"] = \
                        Settings.instance()["__fullscreen_mode"]
        else:
            self.launch_handler.config["fullscreen"] = "0"

        self.launch_handler.prepare()

    # def configure(self):
    #     print("AmigaGameHandler.configure")
    #
    #     #temp_dir = self.fsgs.temp.dir("amiga-config")
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

    def run(self):
        print("AmigaGameHandler.run, cwd =", self.cwd.path)
        # self.on_progress(_("Starting FS-UAE..."))
        config = self.launch_handler.create_config()
        process, self.temp_config_file = FSUAE.start_with_config(
            config, cwd=self.cwd.path)
        # process.wait()
        # print("LaunchHandler.start is done")
        # print("removing", config_file)
        # try:
        #     os.remove(config_file)
        # except Exception:
        #     print("could not remove config file", config_file)
        return process

    def finish(self):
        print("removing", self.temp_config_file)
        if self.temp_config_file is not None:
            try:
                os.remove(self.temp_config_file)
            except Exception:
                print("could not remove config file", self.temp_config_file)

        self.launch_handler.update_changes()
        self.launch_handler.cleanup()
        # self.change_handler.update(self.fsgs.get_game_state_dir())

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

    def set_input_options(self, f):
        # FIXME

        input_mapping = [{
                "1": "JOY2_FIRE_BUTTON",
                "2": "JOY2_2ND_BUTTON",
                "3": "JOY2_3RD_BUTTON",
                "left": "JOY2_LEFT",
                "right": "JOY2_RIGHT",
                "up": "JOY2_UP",
                "down": "JOY2_DOWN",
            }, {
                "1": "JOY1_FIRE_BUTTON",
                "2": "JOY1_2ND_BUTTON",
                "3": "JOY1_3RD_BUTTON",
                "left": "JOY1_LEFT",
                "right": "JOY1_RIGHT",
                "up": "JOY1_UP",
                "down": "JOY1_DOWN",
            }]

        f.write("\n[input]\n")

        for i, input in enumerate(self.inputs):
            if not input.device:
                continue
            if i == 0:
                key = "joystick_port_1"
            else:
                key = "joystick_port_0"
            if input.type == "amiga_mouse":
                value = "mouse"
            else:
                value = input.device.id
            print("configure device:", key, value)
            f.write("{0} = {1}\n".format(key, value))

    def find_kickstart(self, bios_patterns):
        print("find_kickstart", bios_patterns)
        for name in os.listdir(self.firmware_dir):
            for bios in bios_patterns:
                if bios in name:
                    return os.path.join(self.firmware_dir, name)
        raise Exception("Could not find Amiga bios/kickstart " +
                repr(bios_patterns))

    def get_game_refresh_rate(self):
        # FIXME: Now assuming that all games are PAL / 50 Hz
        # - make configurable?
        return 50.0
