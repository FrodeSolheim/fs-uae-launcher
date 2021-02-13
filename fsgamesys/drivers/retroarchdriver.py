import logging
import os
import shutil
from typing import Optional

import fsboot
from fsgamesys import Option
from fsgamesys.drivers.gamedriver import Emulator, GameDriver
from fsgamesys.FSGSDirectories import FSGSDirectories
from fsgamesys.input.mapper import InputMapper
from fsgamesys.plugins.pluginmanager import PluginManager
from fsgamesys.saves import SaveHandler

logger = logging.getLogger("retroarchdriver")


class RetroArchDriver(GameDriver):
    def __init__(self, fsgc, libretro_core, retroarch_state_dir):
        super().__init__(fsgc)
        # self.temp_root.root = TempRoot("/home/frode/Temp2")
        # self.emulator = Emulator("retroarch-fs")
        self.emulator = Emulator(
            "retroarch", path=self.options[Option.RETROARCH_PATH]
        )
        # self.emulator.allow_home_access = True
        # self.emulator.allow_system_emulator = True
        # self.libretro_core = "no_core_specified"
        self.system_dir = self.temp_dir("system")
        self.save_handler = RetroArchSaveHandler(
            self.fsgc, options=self.options, emulator=retroarch_state_dir
        )
        # self.retroarch_state_dir = None

        self.libretro_core = libretro_core
        self.retroarch_state_dir = retroarch_state_dir
        # Dictionary with key-values which will be written to retroarch.cfg
        self.retroarch_config_file = self.temp_file("retroarch.cfg")
        self.retroarch_config = {}
        # FIXME
        self.retroarch_core_config = {}
        self.retroarch_video_driver = None

        self.retroarch_remap_core = None

    def prepare(
        self, libretro_core_options=None, libretro_content_factory=None
    ):
        self.erase_old_config()

        # if not os.path.exists(config_dir):
        #     os.makedirs(config_dir)
        # config_file = os.path.join(config_dir, "retroarch.cfg")

        # FIXME: Do not use /etc/retroarch.cfg as template.. how to prevent?

        self.save_handler.prepare()

        # Clear old options
        f = self.open_retroarch_options()
        f.close()

        with open(self.retroarch_config_file.path, "w", encoding="UTF-8") as f:
            # with self.open_retroarch_options() as f:
            self.write_retroarch_config(f)
            self.write_retroarch_audio_config(f)
            self.write_retroarch_input_config(f)
            self.write_retroarch_video_config(f)

        if libretro_core_options:
            with self.open_retroarch_core_options() as f:
                for key, value in libretro_core_options.items():
                    f.write('{} = "{}"\n'.format(key, value))

        self.emulator.args.append(
            "--appendconfig=" + self.retroarch_config_file.path
        )
        if self.use_fullscreen():
            self.emulator.args.append("--fullscreen")

        libretro_core = self.find_libretro_core(self.libretro_core)
        if not libretro_core:
            raise Exception(
                "Could not find libretro core {0!r}".format(self.libretro_core)
            )
        self.emulator.args.extend(["-L", libretro_core])

        # Verbose logging
        self.emulator.args.extend(["-v"])

        if libretro_content_factory:
            self.emulator.args.append(libretro_content_factory())

    def run(self):
        with open(self.retroarch_config_file.path, "a", encoding="UTF-8") as f:
            for key, value in self.retroarch_config.items():
                f.write('{} = "{}"\n'.format(key, value))
        super().run()

    def finish(self):
        self.save_handler.finish()

    def retroarch_core_remap(self):
        return None, None

    def find_libretro_core_development(self, name):
        # FIXME: Move to pluginmanager?
        # See if we can find the core in a project dir side by side
        name = name + "_libretro"
        dll_name = name + ".so"
        path = os.path.join(fsboot.executable_dir(), "..", name, dll_name)
        logger.debug("Checking %s", path)
        # Try one additional level up
        if not os.path.exists(path):
            path = os.path.join(
                fsboot.executable_dir(), "..", "..", name, dll_name
            )
            logger.debug("Checking %s", path)
        if os.path.exists(path):
            # logger.debug("Found non-plugin library %s", path)
            return path
        return None

    def find_libretro_core(self, name):
        path = self.find_libretro_core_development(name)
        if path:
            return path
        # return "{}.so".format(name)
        if self.emulator.path == "/snap/bin/retroarch":
            # Hack, hardcoded for Debian/Ubuntu
            return os.path.expanduser(
                "~/snap/retroarch/current/.config/retroarch/"
                "cores/{}.so".format(name)
            )
        if self.emulator.path == "/usr/bin/retroarch":
            # Hack, hardcoded for Debian/Ubuntu
            return "/usr/lib/x86_64-linux-gnu/libretro/{}.so".format(name)
        if self.emulator.path == "/usr/local/bin/retroarch":
            base_path = os.path.expanduser("~/.config/retroarch/")
            core_path = os.path.join(base_path, "cores/{}.so".format(name))
            return core_path
        return PluginManager.instance().find_library_path(name)

    def find_libretro_shader_development(self, relative_path):
        path = os.path.join(
            fsboot.executable_dir(), "..", "retroarch", relative_path
        )
        # Try one additional level up
        if not os.path.exists(path):
            path = os.path.join(
                fsboot.executable_dir(), "..", "..", "retroarch", relative_path
            )
            # logger.debug("Checking %s", path)
        if os.path.exists(path):
            # logger.debug("Found non-plugin library %s", path)
            return path
        return None

    def find_retroarch_shader(self, name):
        relative_path = "shaders/shaders_glsl/" + name + ".glslp"
        path = self.find_libretro_shader_development(relative_path)
        if path:
            return path
        if self.emulator.path == "/snap/bin/retroarch":
            base_path = os.path.expanduser(
                "~/snap/retroarch/current/.config/retroarch/"
            )
            return os.path.join(base_path, relative_path)
        if self.emulator.path == "/usr/local/bin/retroarch":
            base_path = os.path.expanduser("~/.config/retroarch/")
            return os.path.join(base_path, relative_path)
        if self.emulator.path:
            # FIXME: ..
            return ""
        # FIXME: Better to find data file based on path/provides rather than
        # hardcoding plugin name, but...
        try:
            plugin = PluginManager.instance().plugin("RetroArch-FS")
        except LookupError:
            return ""
        else:
            return plugin.data_file_path(relative_path)

    def display_aspect_ratio(self) -> Optional[float]:
        return 4 / 3

    def game_video_size(self):
        # FIXME: Dummy values
        print("[DRIVER] Warning: Using dummy game video size (320, 240)")
        return 320, 240

    def erase_old_config(self):
        config_dir = os.path.join(self.home.path, ".config", "retroarch")
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)

    def open_retroarch_options(self):
        config_dir = os.path.join(self.home.path, ".config", "retroarch")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "retroarch.cfg")
        return open(config_file, "w", encoding="UTF-8")

    def open_retroarch_core_options(self):
        config_dir = os.path.join(self.home.path, ".config", "retroarch")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "retroarch-core-options.cfg")
        return open(config_file, "w", encoding="UTF-8")

    def open_core_remap_file(self, name):
        config_dir = os.path.join(
            self.home.path, ".config", "retroarch", "config", "remaps", name
        )
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, name + ".rmp")
        return open(config_file, "w", encoding="UTF-8")

    def write_retroarch_config(self, f):
        """
        joypad_autoconfig_dir = "~/.config/retroarch/autoconfig"
        """
        f.write(
            'screenshot_directory = "{}"\n'.format(
                FSGSDirectories.screenshots_output_dir()
            )
        )
        f.write('system_directory = "{}"\n'.format(self.system_dir.path))
        # noinspection SpellCheckingInspection

        f.write(
            'savefile_directory = "{}"\n'.format(
                self.save_handler.emulator_save_dir()
            )
        )
        f.write(
            'savestate_directory = "{}"\n'.format(
                self.save_handler.emulator_state_dir()
            )
        )
        assets_dir = ""
        f.write('assets_directory = "{}"\n'.format(assets_dir))

        # FIXME: Maybe enable autosave to save .srm while running the emulator
        # and not only on shutdown?
        # f.write("autosave_interval = 60\n")

        f.write("pause_nonactive = false\n")
        f.write("video_font_enable = false\n")
        f.write("rgui_show_start_screen = false\n")
        f.write("all_users_control_menu = true\n")
        f.write("video_gpu_screenshot = false\n")

        # f.write('frontend_log_level = "0"\n')
        # f.write('libretro_log_level = "0"\n')

    def write_retroarch_audio_config(self, f):
        # default_buffer_size = 40
        default_buffer_size = 64
        buffer_size = default_buffer_size
        if self.options[Option.RETROARCH_AUDIO_BUFFER]:
            try:
                buffer_size = int(self.options[Option.RETROARCH_AUDIO_BUFFER])
            except ValueError:
                print("WARNING: Invalid RetroArch audio buffer size specified")
            else:
                if buffer_size < 0 or buffer_size > 1000:
                    print("WARNING: RetroArch audio buffer size out of range")
                    buffer_size = default_buffer_size
        # f.write("audio_latency = {}\n".format(buffer_size))
        audio_driver = None
        # audio_driver = "sdl2"
        # audio_driver = "null"
        # audio_driver = "alsa"
        if audio_driver:
            f.write('audio_driver = "{}"\n'.format(audio_driver))
        if audio_driver == "null":
            f.write('audio_enable = "{}"\n'.format("false"))
        if audio_driver == "alsa":
            f.write('audio_device = "{}"\n'.format("hw:0"))

    def write_retroarch_input_config(self, f):
        # f.write('input_driver = "sdl2"\n')
        f.write('input_enable_hotkey = "alt"\n')
        f.write('input_exit_emulator = "q"\n')
        f.write('input_toggle_fast_forward = "w"\n')
        f.write('input_screenshot = "s"\n')
        # f.write("input_toggle_fullscreen = \"enter\"\n")
        f.write('input_toggle_fullscreen = "f"\n')
        f.write('input_audio_mute = "m"\n')
        f.write('input_menu_toggle = "f12"\n')
        f.write('input_pause_toggle = "p"\n')

        f.write('quit_press_twice = "false"\n')

        # f.write('joypad_input_driver = "sdl2"\n')

        # We want to configure devices ourselves, so disable autoconfig dir
        # At least for now. Later, it might make more sense to write
        # RetroArch-style autoconf files for devices
        f.write('joypad_autoconfig_dir = "/dummy"\n')

        remap_dict = {}

        for i, port in enumerate(self.ports):
            if port.device is None:
                continue
            input_mapping = self.retroarch_input_mapping(i)
            # FIXME: EXCLUDE DUPLICATE ITEMS IN INPUT MAPPING???
            # port = port.copy()
            if port.device.name == "Keyboard":
                pass
            else:
                port.mapping_name_override = "retropad"

                n = i + 1
                input_mapping = {
                    "A": "input_player{}_a".format(n),
                    "B": "input_player{}_b".format(n),
                    "X": "input_player{}_x".format(n),
                    "Y": "input_player{}_y".format(n),
                    "UP": "input_player{}_up".format(n),
                    "DOWN": "input_player{}_down".format(n),
                    "LEFT": "input_player{}_left".format(n),
                    "RIGHT": "input_player{}_right".format(n),
                    "SELECT": "input_player{}_select".format(n),
                    "START": "input_player{}_start".format(n),
                    "L": "input_player{}_l".format(n),
                    "L2": "input_player{}_l2".format(n),
                    "L3": "input_player{}_l3".format(n),
                    "R": "input_player{}_l".format(n),
                    "R2": "input_player{}_r2".format(n),
                    "R3": "input_player{}_r3".format(n),
                    "L_X_MINUS": "input_player{}_l_x_minus".format(n),
                    "L_X_PLUS": "input_player{}_l_x_plus".format(n),
                    "L_Y_MINUS": "input_player{}_l_y_minus".format(n),
                    "L_Y_PLUS": "input_player{}_l_y_plus".format(n),
                    "R_X_MINUS": "input_player{}_r_x_minus".format(n),
                    "R_X_PLUS": "input_player{}_r_x_plus".format(n),
                    "R_Y_MINUS": "input_player{}_r_y_minus".format(n),
                    "R_Y_PLUS": "input_player{}_r_y_plus".format(n),
                }

            mapper = RetroArchInputMapper(port, input_mapping)
            # FIXME: Device index
            f.write('input_player1_joypad_index = "0"\n')
            f.write('input_player1_analog_dpad_mode = "0"\n')
            if port.device.type == "joystick":
                pass
            else:
                pass

            for key, value in mapper.items():
                # print("---->", key, value)
                postfix, value = value
                f.write('{}{} = "{}"\n'.format(key, postfix, value))
                # Clear other postfix mappings
                postfixes = ["", "_btn", "_axis"]
                postfixes.remove(postfix)
                for postfix in postfixes:
                    f.write('{}{} = "{}"\n'.format(key, postfix, "nul"))

            if self.retroarch_remap_core:
                controller = self.controller_for_port(port)
                print("[RETROARCH] Got controller", controller)

                if port.device.type == "keyboard":
                    # Menu enter/confirm seems to be affecte by the input
                    # config here..., so we make sure to use the start item
                    # for the enter key
                    dummy_items = [
                        "start",
                        "a",
                        "b",
                        "x",
                        "y",
                        "select",
                        "up",
                        "left",
                        "right",
                        "down",
                        "l",
                        "l2",
                        "l3",
                        "r",
                        "r2",
                        "r3",
                    ]

                    keyboard_mapping = controller.keyboard_mapping(port)
                    retropad_mapping = self.retropad_mapping_for_port(port)
                    for keyboard_input, action in keyboard_mapping.items():
                        for remap_id, action_2 in retropad_mapping.items():
                            if action == action_2:

                                key_name = retroarch_key_from_sdl(
                                    keyboard_input
                                )
                                if key_name == "enter":
                                    dummy_items.remove("start")
                                    item = "start"
                                else:
                                    item = dummy_items.pop()
                                # dummy_index += 1
                                remap_name = "input_player{}_btn_{}".format(
                                    port.index + 1, item
                                )

                                f.write(
                                    'input_player{}_{} = "{}"\n'.format(
                                        port.index + 1, item, key_name
                                    )
                                )

                                # print(keyboard_input, action, remap_id)
                                # remap_name = self.retroarch_remap_name_for_port(
                                #     keyboard_input, port.index)

                                print(
                                    keyboard_input,
                                    action,
                                    remap_name,
                                    remap_id,
                                )

                                remap_dict[remap_name] = remap_id
                                break
                    # Clear remaining retropad items
                    for item in dummy_items:
                        f.write(
                            'input_player{}_{} = "nul"\n'.format(
                                port.index + 1, item
                            )
                        )
                else:
                    gamepad_mapping = controller.gamepad_mapping(port)
                    retropad_mapping = self.retropad_mapping_for_port(port)
                    for gamepad_input, action in gamepad_mapping.items():
                        for remap_id, action_2 in retropad_mapping.items():
                            if action == action_2:
                                remap_name = (
                                    self.retroarch_remap_name_for_port(
                                        gamepad_input, port.index
                                    )
                                )
                                print(remap_name, remap_id)
                                remap_dict[remap_name] = remap_id
                                break

        if self.retroarch_remap_core:
            self.write_retroarch_core_remap(
                self.retroarch_remap_core, remap_dict
            )

    # def retroarch_core_remap_2(self, core_name, max_controllers, controller_function, core_function):
    #     # remap_dict = {}
    #     # for port_index in range(max_controllers):
    #         # nes = nes_controller_gamepad_mapping(port_index)
    #         # nestopia = nestopia_retropad_mapping_for_port(port_index)
    #         # for controller_input, nes_action in nes.items():
    #         #     for remap_id, nes_action_2 in nestopia.items():
    #         #         if nes_action_2 == nes_action:
    #         #             remap_name = self.retroarch_remap_name_for_port(
    #         #                 controller_input, port_index)
    #         #             print(remap_name, remap_id)
    #         #             remap_dict[remap_name] = remap_id
    #     # self.write_retroarch_core_remap(core_name, remap_dict)

    def write_retroarch_core_remap(self, remap_file_name, remap_dict):
        with self.open_core_remap_file(remap_file_name) as f:
            for key, value in remap_dict.items():
                f.write("{} = {}\n".format(key, value))

    @staticmethod
    def retroarch_remap_name(input_event):
        # FIXME: rename input_event to something else...
        # sdl_controller_event? sdl_controller_input?
        mapping = {
            Controller.A: "btn_a",
            Controller.B: "btn_b",
            Controller.X: "btn_x",
            Controller.Y: "btn_y",
            Controller.START: "btn_start",
            Controller.GUIDE: "",
            Controller.BACK: "btn_select",
            Controller.DPUP: "btn_up",
            Controller.DPLEFT: "btn_left",
            Controller.DPRIGHT: "btn_right",
            Controller.DPDOWN: "btn_down",
            Controller.LEFTSHOULDER: "btn_l",
            Controller.RIGHTSHOULDER: "btn_r",
            Controller.LEFTSTICK: "btn_l3",
            Controller.RIGHTSTICK: "btn_r3",
            Controller.LEFTTRIGGER: "btn_l2",
            Controller.RIGHTTRIGGER: "btn_r2",
            Controller.LEFTXNEG: "stk_l_x-",
            Controller.LEFTXPOS: "stk_l_x+",
            Controller.LEFTYNEG: "stk_l_y-",
            Controller.LEFTYPOS: "stk_l_y+",
            Controller.RIGHTXNEG: "stk_r_x-",
            Controller.RIGHTXPOS: "stk_r_x+",
            Controller.RIGHTYNEG: "stk_r_y-",
            Controller.RIGHTYPOS: "stk_r_y+",
            # CONTROLLER_LEFTX: "",
            # CONTROLLER_LEFTY: "",
            # CONTROLLER_RIGHTX: "",
            # CONTROLLER_RIGHTY: "",
        }
        return mapping[input_event]

    @classmethod
    def retroarch_remap_name_for_port(cls, input_event, port_index):
        return "input_player{}_{}".format(
            port_index + 1, cls.retroarch_remap_name(input_event)
        )

    def write_retroarch_video_config(self, f):
        if self.retroarch_video_driver == "vulkan":
            f.write('video_driver = "vulkan"\n')
        else:
            f.write('video_driver = "gl"\n')
        # FIXME
        if self.fullscreen_window_mode():
            f.write("video_windowed_fullscreen = true\n")
        else:
            f.write("video_windowed_fullscreen = false\n")

        # FIXME: 1 or 0?
        f.write("video_max_swapchain_images = 1\n")

        f.write('settings_show_onscreen_display = "true"\n')
        f.write('fps_show = "true"\n')
        f.write('fps_update_interval = "256"\n')

        if self.effect() == self.CRT_EFFECT:
            video_shader = "crt/crt-aperture"
            video_scale = 2
        elif self.effect() == self.DOUBLE_EFFECT:
            if self.smoothing() == self.NO_SMOOTHING:
                video_shader = ""
            else:
                # video_shader = "retro/sharp-bilinear-2x-prescale"
                video_shader = "interpolation/sharp-bilinear-2x-prescale"
            video_scale = 2
        elif self.effect() == self.HQ2X_EFFECT:
            video_shader = "hqx/hq2x"
            video_scale = 2
        elif self.effect() == self.SCALE2X_EFFECT:
            video_shader = "scalenx/scale2x"
            video_scale = 2
        else:
            video_shader = ""
            video_scale = 1

        if self.smoothing() == self.NO_SMOOTHING or video_shader:
            f.write("video_smooth = false\n")

        if video_shader:
            print("[DRIVER] Video shader:", video_shader)
            video_shader_path = self.find_retroarch_shader(video_shader)
            print("[DRIVER] Video shader path:", video_shader_path)
            if video_shader_path:
                # f.write('video_shader = "{}"\n'.format(video_shader_path))
                f.write("video_shader_enable = true\n")
                self.emulator.args.extend(["--set-shader", video_shader_path])
        else:
            f.write("video_shader_enable = false\n")

        # FIXME: video_monitor_index = 0
        # FIXME: video_disable_composition = true
        if self.use_g_sync():
            # Without timed frame limiting, there will be stuttering (probably)
            # due to (some) audio driver sync not being stable enough to give
            # a stable frame rate.

            # FIXME: Implement better G-SYNC method in RetroArch
            f.write("fastforward_ratio = 1.000001\n")
            # f.write("video_vsync = false\n")
            f.write("audio_sync = false\n")
            f.write("vrr_runloop_enable = true\n")

            f.write("video_vsync = true\n")
            f.write("video_hard_sync = true\n")

            # FIXME: It's possible the above "fix" would be better for
            # non-v-sync as well, if the audio sync is not stable.

            # f.write("audio_max_timing_skew = 0.0\n")
            # f.write("audio_rate_control_delta = 0.0\n")
            # f.write("video_refresh_rate = 144.0\n")
            # f.write("audio_sync = false\n")
        elif self.use_vsync():
            f.write("video_vsync = true\n")
            f.write("video_hard_sync = true\n")
        else:
            f.write("video_vsync = false\n")

        # aspect_ratio_index = 22
        # custom_viewport_width = 0
        # custom_viewport_height = 0
        # custom_viewport_x = 0
        # custom_viewport_y = 0

        if self.stretching() == self.STRETCH_ASPECT:
            aspect_ratio = self.display_aspect_ratio()
            if aspect_ratio is not None:
                f.write("aspect_ratio_index = 20\n")
                f.write("video_aspect_ratio = {:f}\n".format(aspect_ratio))
                # f.write("video_force_aspect = \"true\"\n")
                # f.write("video_aspect_ratio_auto = \"false\"\n")
        elif self.stretching() == self.STRETCH_FILL_SCREEN:
            screen_w, screen_h = self.screen_size()
            display_aspect = screen_w / screen_h
            f.write("aspect_ratio_index = 20\n")
            f.write("video_aspect_ratio = {:f}\n".format(display_aspect))
        else:
            f.write("aspect_ratio_index = 21\n")

        if self.scaling() == self.NO_SCALING:
            # FIXME: Window size rounding issues? E.g. 897x672 for 4:3
            # NES 3x display. Maybe set window size manually instead
            f.write("video_scale = {}\n".format(video_scale))

        # f.write("input_osk_toggle = \"nul\"\n")
        overlay_path = self.create_retroarch_layout()
        if overlay_path:
            f.write('input_overlay = "{}"\n'.format(overlay_path))
            f.write('input_overlay_opacity = "1.000000"\n')

    def retroarch_input_mapping(self, port):
        return {}

    def display_rect_fullscreen(self):
        # FIXME: Check square pixels option!

        screen_w, screen_h = self.screen_size()
        screen_aspect = screen_w / screen_h

        if self.stretching() == self.STRETCH_ASPECT:
            display_aspect = self.display_aspect_ratio()
        elif self.stretching() == self.STRETCH_FILL_SCREEN:
            screen_w, screen_h = self.screen_size()
            display_aspect = screen_w / screen_h
        else:
            game_w, game_h = self.game_video_size()
            display_aspect = game_w / game_h

        # FIXME: round to nearest multiple of two?
        if screen_aspect >= display_aspect:
            game_h = screen_h
            game_w = round(game_h * display_aspect)
        else:
            game_w = screen_w
            game_h = round(game_w / display_aspect)
        game_x = round((screen_w - game_w) / 2)
        game_y = round((screen_h - game_h) / 2)
        return game_x, game_y, game_w, game_h

    def create_retroarch_layout(self):
        if self.stretching() == self.STRETCH_FILL_SCREEN or not self.bezel():
            return
        if not self.use_fullscreen():
            return

        # FIXME: file cmp?
        paths = self.prepare_emulator_skin()
        print(paths)

        # FIXME: SUPPORT frame = 0 ( bezel = 0) option

        # FIXME: With no bezel, we should still use a black bezel to
        # hide screen stretching

        screen_width, screen_height = self.screen_size()
        # dst_x = 0
        dst_y = 0
        # dst_w = 0
        # dst_w = 160
        dst_h = screen_height

        # Bezel size is normalized against 1080 (height)
        scale = screen_height / 1080
        # Bezel width: 160
        dst_w = round(160 * scale)

        game_x, game_y, game_w, game_h = self.display_rect_fullscreen()

        from fsui.qt import QImage, QPainter, QRect, QSize, Qt

        image = QImage(
            QSize(screen_width, screen_height), QImage.Format_RGBA8888
        )
        image.fill(Qt.transparent)
        # painter = image.paintEngine()
        painter = QPainter(image)

        dst_x = game_x - dst_w
        left = QImage(paths["left"])
        painter.drawImage(QRect(dst_x, dst_y, dst_w, dst_h), left)

        dst_x = game_x + game_w
        right = QImage(paths["right"])
        painter.drawImage(QRect(dst_x, dst_y, dst_w, dst_h), right)
        painter.end()

        overlay_png_file = self.temp_file("overlay.png").path
        image.save(overlay_png_file)

        # noinspection SpellCheckingInspection
        overlay_config = """overlays = 1
overlay0_overlay = {overlay}
overlay0_full_screen = true
overlay0_rect = "0.0,0.0,1.0,1.0"
overlay0_descs = 0
""".format(
            overlay=overlay_png_file
        )
        #         overlay_config = (
        #             """overlays = 2
        # overlay0_overlay = {left}
        # overlay0_full_screen = true
        # overlay0_rect = "0.0,0.0,0.12,1.0"
        # overlay0_descs = 0
        # overlay1_overlay = {right}
        # overlay1_full_screen = true
        # overlay1_rect = "0.8,0.0,0.2,1.0"
        # overlay1_descs = 0
        #
        # """.format(left=paths["left"], right=paths["right"]))
        overlay_config_file = self.temp_file("overlay.cfg")
        with open(overlay_config_file.path, "w") as f:
            f.write(overlay_config)
        return overlay_config_file.path

    def window_size(self):
        return 0, 0


class RetroArchInputMapper(InputMapper):
    def __init__(self, port, mapping):
        super().__init__(port, mapping, multiple=False)

    def axis(self, axis, positive):
        dir_str = "+" if positive else "-"
        return "_axis", dir_str + str(axis)

    def hat(self, hat, direction):
        return "_btn", "h{}{}".format(hat, direction)

    def button(self, button):
        return "_btn", button

    def key(self, key):
        # FIXME: Correct RetroArch key names
        name = key.sdl_name[5:].lower()
        if name == "return":
            # FIXME: HACK
            name = "enter"
        return "", name


def retroarch_key_from_sdl(name):
    if name == "return":
        # FIXME: HACK
        name = "enter"
    return name


class RetroArchSaveHandler(SaveHandler):
    def __init__(self, fsgc, options, emulator):
        super().__init__(fsgc, options, emulator=emulator)

    def prepare(self):
        super().prepare()

    def finish(self):
        super().finish()


# FIXME: Move to some common module
class Controller:
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    START = "start"
    GUIDE = "guide"
    BACK = "back"
    DPUP = "dpup"
    DPLEFT = "dpleft"
    DPRIGHT = "dpright"
    DPDOWN = "dpdown"
    LEFTSHOULDER = "leftshoulder"
    RIGHTSHOULDER = "rightshoulder"
    LEFTSTICK = "leftstick"
    RIGHTSTICK = "rightstick"
    LEFTX = "leftx"
    LEFTY = "lefty"
    RIGHTX = "rightx"
    RIGHTY = "righty"
    LEFTTRIGGER = "lefttrigger"
    RIGHTTRIGGER = "righttrigger"
    LEFTXNEG = "leftxneg"
    LEFTXPOS = "leftxpos"
    LEFTYNEG = "leftyneg"
    LEFTYPOS = "leftypos"
    RIGHTXNEG = "rightxneg"
    RIGHTXPOS = "rightxpos"
    RIGHTYNEG = "rightyneg"
    RIGHTYPOS = "rightypos"
