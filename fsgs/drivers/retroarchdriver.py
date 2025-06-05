import os
import shutil
from typing import Optional

from fsgs import Option
from fsgs.drivers.gamedriver import Emulator, GameDriver
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.input.mapper import InputMapper
from fsgs.plugins.pluginmanager import PluginManager
from fsgs.saves import SaveHandler


class RetroArchDriver(GameDriver):
    def __init__(self, fsgc, libretro_core, retroarch_state_dir):
        super().__init__(fsgc)
        self.emulator = Emulator("retroarch-fs")
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

    def prepare(self):
        self.erase_old_config()

        # if not os.path.exists(config_dir):
        #     os.makedirs(config_dir)
        # config_file = os.path.join(config_dir, "retroarch.cfg")

        # FIXME: Do not use /etc/retroarch.cfg as template.. how to prevent?

        self.save_handler.prepare()

        with open(self.retroarch_config_file.path, "w", encoding="UTF-8") as f:
            self.write_retroarch_config(f)
            self.write_retroarch_input_config(f)
            self.write_retroarch_video_config(f)

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

    def run(self):
        with open(self.retroarch_config_file.path, "a", encoding="UTF-8") as f:
            for key, value in self.retroarch_config.items():
                f.write('{} = "{}"\n'.format(key, value))
        super().run()

    def finish(self):
        self.save_handler.finish()

    @staticmethod
    def find_libretro_core(name):
        # return "/usr/lib/x86_64-linux-gnu/libretro/{}.so".format(name)
        return PluginManager.instance().find_library_path(name)

    @staticmethod
    def find_retroarch_shader(name):
        # FIXME: Better to find data file based on path/provides rather than
        # hardcoding plugin name, but...
        plugin = PluginManager.instance().plugin("RetroArch-FS")
        return plugin.data_file_path("shaders/shaders_glsl/" + name + ".glslp")

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

    def open_retroarch_core_options(self):
        config_dir = os.path.join(self.home.path, ".config", "retroarch")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "retroarch-core-options.cfg")
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

        # FIXME: Maybe enable autosave to save .srm while running the emulator
        # and not only on shutdown?
        # f.write("autosave_interval = 60\n")

        f.write("pause_nonactive = false\n")
        f.write("video_font_enable = false\n")
        f.write("rgui_show_start_screen = false\n")
        f.write("all_users_control_menu = true\n")
        f.write("video_gpu_screenshot = false\n")

        if self.g_sync():
            # Without timed frame limiting, there will be stuttering (probably)
            # due to (some) audio driver sync not being stable enough to give
            # a stable frame rate.

            # FIXME: Implement better G-SYNC method in RetroArch
            f.write("fastforward_ratio = 1.000000\n")

            # FIXME: It's possible the above "fix" would be better for
            # non-v-sync as well, if the audio sync is not stable.

            # f.write("audio_max_timing_skew = 0.0\n")
            # f.write("audio_rate_control_delta = 0.0\n")
            # f.write("video_refresh_rate = 144.0\n")
            # f.write("audio_sync = false\n")

        default_buffer_size = 40
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
        f.write("audio_latency = {}\n".format(buffer_size))

    def write_retroarch_input_config(self, f):
        f.write('input_driver = "sdl2"\n')
        f.write('input_enable_hotkey = "alt"\n')
        f.write('input_exit_emulator = "q"\n')
        f.write('input_toggle_fast_forward = "w"\n')
        f.write('input_screenshot = "s"\n')
        # f.write("input_toggle_fullscreen = \"enter\"\n")
        f.write('input_toggle_fullscreen = "f"\n')
        f.write('input_audio_mute = "m"\n')
        f.write('input_menu_toggle = "f12"\n')
        f.write('input_pause_toggle = "p"\n')

        for i, port in enumerate(self.ports):
            if port.device is None:
                continue
            input_mapping = self.retroarch_input_mapping(i)
            # FIXME: EXCLUDE DUPLICATE ITEMS IN INPUT MAPPING???
            mapper = RetroArchInputMapper(port, input_mapping)

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
                postfixes = ["", "_btn", "_axis"]
                postfixes.remove(postfix)
                for postfix in postfixes:
                    f.write('{}{} = "{}"\n'.format(key, postfix, "nul"))

    def write_retroarch_video_config(self, f):
        # f.write("video_driver = \"gl\"\n")
        # FIXME
        if self.fullscreen_window_mode():
            f.write("video_windowed_fullscreen = true\n")
        else:
            f.write("video_windowed_fullscreen = false\n")

        # FIXME: 1 or 0?
        f.write("video_max_swapchain_images = 1\n")

        if self.effect() == self.CRT_EFFECT:
            video_shader = "crt/crt-aperture"
            video_scale = 2
        elif self.effect() == self.DOUBLE_EFFECT:
            if self.smoothing() == self.NO_SMOOTHING:
                video_shader = ""
            else:
                video_shader = "retro/sharp-bilinear-2x-prescale"
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
                f.write('video_shader = "{}"\n'.format(video_shader_path))
                f.write("video_shader_enable = true\n")

        # FIXME: video_monitor_index = 0
        # FIXME: video_disable_composition = true
        if self.use_vsync():
            f.write("video_vsync = true\n")
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
                f.write("aspect_ratio_index = 19\n")
                f.write("video_aspect_ratio = {:f}\n".format(aspect_ratio))
                # f.write("video_force_aspect = \"true\"\n")
                # f.write("video_aspect_ratio_auto = \"false\"\n")
        elif self.stretching() == self.STRETCH_FILL_SCREEN:
            screen_w, screen_h = self.screen_size()
            display_aspect = screen_w / screen_h
            f.write("aspect_ratio_index = 19\n")
            f.write("video_aspect_ratio = {:f}\n".format(display_aspect))
        else:
            f.write("aspect_ratio_index = 20\n")

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
""".format(overlay=overlay_png_file)
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


class RetroArchSaveHandler(SaveHandler):
    def __init__(self, fsgc, options, emulator):
        super().__init__(fsgc, options, emulator=emulator)

    def prepare(self):
        super().prepare()

    def finish(self):
        super().finish()
