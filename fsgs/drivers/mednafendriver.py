import hashlib
import os
import struct
from functools import lru_cache

from fsbc.system import windows
from fsgs.drivers.gamedriver import GameDriver
from fsgs.input.enumeratehelper import EnumerateHelper
from fsgs.input.mapper import InputMapper
from fsgs.option import Option


class MednafenDriver(GameDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator.name = "mednafen-fs"

    def prepare(self):
        # self.temp_home = self.create_temp_dir("mednafen-home")
        with open(self.mednafen_cfg_path(), "w", encoding="UTF-8") as f:
            self.mednafen_configure(f)

    def finish(self):
        pass

    def get_supported_filters(self):
        supported = [
            {
                "name": "2x",
                "special": "nn2x",
            }, {
                "name": "none",
                "special": "none",
            }, {
                "name": "scale2x",
                "special": "scale2x",
            }, {
                "name": "hq2x",
                "special": "hq2x",
            }
        ]
        return supported

    def mednafen_input_mapping(self, port):
        raise NotImplementedError()

    def mednafen_system_prefix(self):
        raise NotImplementedError()

    def game_video_par(self):
        return 1.0

    def game_video_size(self):
        raise NotImplementedError("game_video_size must be implemented")

    def mednafen_rom_extensions(self):
        return []

    def mednafen_scanlines_setting(self):
        return None

    def mednafen_special_filter(self):
        return None

    def mednafen_viewport(self):
        viewport = self.config["viewport"]
        if viewport:
            src, dst = viewport.split("=")
            src = src.strip()
            dst = dst.strip()
            src_x, src_y, src_w, src_h = [int(v) for v in src.split(" ")]
            dst_x, dst_y, dst_w, dst_h = [int(v) for v in dst.split(" ")]
            return (src_x, src_y, src_w, src_h), (dst_x, dst_y, dst_w, dst_h)
        return None, None

    def mednafen_configure(self, f):
        pfx = self.mednafen_system_prefix()
        self.configure_audio(f)
        self.configure_input(f)
        self.configure_video(f)

        # screen_w, screen_h = self.screen_size()
        #
        # dest_w, dest_h = screen_w, screen_h
        # # a_ratio = self.force_aspect_ratio()
        # a_ratio = 0
        # # game_w, game_h = self.mednafen_video_size()
        # src, dst = self.mednafen_viewport()
        # if src is None:
        #     game_w, game_h = self.mednafen_video_size()
        # else:
        #     game_w, game_h = dst[2], dst[3]
        #
        # self.args.extend(["-{}.xres".format(pfx), str(screen_w)])
        # self.args.extend(["-{}.yres".format(pfx), str(screen_h)])
        #
        # integer_scaling = False
        # if self.use_fullscreen():
        #     self.emulator.args.extend(["-fs", "1"])
        # else:
        #     self.emulator.args.extend(["-fs", "0"])
        #
        # if True:
        #     if self.scaling() == self.MAX_SCALING:
        #         if self.stretching() == self.STRETCH_FILL_SCREEN:
        #             stretch = "full"
        #         else:
        #             stretch = "aspect"
        #         # FIXME: Calculate if we are using integer scaling
        #     elif self.scaling() == self.INTEGER_SCALING:
        #         stretch = "aspect_int"
        #         integer_scaling = True
        #     else:
        #         stretch = "0"
        #         integer_scaling = True
        #     self.emulator.args.extend(["-{}.stretch".format(pfx), stretch])
        #
        # if self.smoothing() == self.SMOOTHING:
        #     videoip = "1"
        # elif self.smoothing() == self.NON_INTEGER_SMOOTHING:
        #     if integer_scaling:
        #         videoip = "0"
        #     else:
        #         videoip = "1"
        # else:
        #     videoip = "0"
        #
        # self.emulator.args.extend(["-{}.videoip".format(pfx), videoip])

                # if game_w and game_h:
        #     real_game_size = (game_w, game_h)
        #     if self.use_stretching():
        #         x_scale = dest_w / game_w
        #         y_scale = dest_h / game_h
        #
        #         if src is not None and dst is not None:
        #             x_offset = dest_w * (
        #                 (src[2] - dst[2]) / 2 - dst[0]) / dst[2]
        #             y_offset = dest_h * (
        #                 (src[3] - dst[3]) / 2 - dst[1]) / dst[3]
        #             x_offset = int(round(x_offset))
        #             y_offset = int(round(y_offset))
        #             self.env["FSGS_OFFSET"] = "{0},{1}".format(
        #                 x_offset, y_offset)
        #             print("FSGS_OFFSET", self.env["FSGS_OFFSET"])
        #     else:
        #         if a_ratio:
        #             print("Forcing aspect ratio %f", a_ratio)
        #             game_h = game_w / a_ratio
        #         x_scale = min(dest_w / game_w, dest_h / game_h)
        #         if a_ratio:
        #             y_scale = (x_scale * real_game_size[0] /
        #                        real_game_size[1] / a_ratio)
        #         else:
        #             y_scale = x_scale
        #     print("Fullscreen scale factors: %f %f", x_scale, y_scale)
        #     self.args.extend(["-%s.xscalefs" % pfx, str(x_scale)])
        #     self.args.extend(["-%s.yscalefs" % pfx, str(y_scale)])
        #     self.args.extend(["-%s.stretch" % pfx, "0"])
        # else:
        #     if self.use_stretching():
        #         self.args.extend(["-%s.stretch" % pfx, "full"])
        #     else:
        #         self.args.extend(["-%s.stretch" % pfx, "aspect"])
        #
        # if self.use_fullscreen():
        #     pass
        # else:
        #     self.args.extend(["-%s.xscale" % pfx, "2"])
        #     self.args.extend(["-%s.yscale" % pfx, "2"])

            # self.args.extend(["-%s.scanlines" % pfx, "0"])
            # if gamew < 200:
            #     self.args.extend(["-%s.xscale" % pfx, "4"])
            #     self.args.extend(["-%s.yscale" % pfx, "4"])
            # else:
            #     self.args.extend(["-%s.xscale" % pfx, "3"])
            #     self.args.extend(["-%s.yscale" % pfx, "3"])
            # self.args.extend(["-%s.videoip" % pfx, "0"])
            #  FIXME:
            # self.options.smooth = False
            # self.options.filter = '2x'

        # if self.use_doubling():
        #     self.args.extend(["-%s.special" % pfx, "nn2x"])
        #
        # self.args.extend(self.mednafen_extra_graphics_options())

        # filter_data = self.configure_filter()
        # if filter_data["name"] == "ntsc":
        #     self.args.extend(["-{0}.ntscblitter".format(pfx), "1"])
        #     self.args.extend(["-{0}.ntsc.preset".format(pfx), "composite"])
        #     self.args.extend(["-{0}.ntsc.saturation".format(pfx), "0.5"])
        # else:
        #     self.args.extend(
        #         ["-{0}.special".format(pfx), filter_data["special"]])

        # self.args.extend(["-%s.special" % pfx,
        # self.mednafen_special_filter()])

        # if self.configure_vsync():
        #     self.args.extend(["-glvsync", "1"])
        # else:
        #     self.args.extend(["-glvsync", "0"])

        if self.config.get(Option.MEDNAFEN_AUDIO_DRIVER):
            if self.config.get(Option.MEDNAFEN_AUDIO_DRIVER) == "sdl":
                # Mednafen does not support PulseAudio directly, but using the
                # sdl driver will "often" result in PulseAudio being used
                # indirectly.
                self.args.extend(["-sound.driver", "sdl"])
        # FIXME: Deprecated?
        elif self.config.get("audio_driver", "") in ["sdl", "pulseaudio"]:
            # Mednafen does not support PulseAudio directly, but using the
            # sdl driver will "often" result in PulseAudio being used
            # indirectly.
            self.args.extend(["-sound.driver", "sdl"])

        self.args.extend(["-video.driver", "opengl"])

        print("\n" + "-" * 79 + "\n" + "CONFIGURE DIRS")

        state_dir = self.emulator_state_dir("mednafen")
        self.args.extend(["-path_sav", state_dir])
        self.args.extend(["-path_state", state_dir])
        self.args.extend(["-filesys.fname_state", "%M%X"])
        self.args.extend(["-filesys.fname_sav", "%M%x"])

        # docdir = pyapp.user.documents_dir()
        self.doc_dir = self.create_temp_dir("mednafen-docs")
        self.args.extend([
            "-path_movie", self.doc_dir.path,
            "-path_cheat", self.doc_dir.path,
            "-path_palette", self.home.path])

        self.args.extend(["-path_snap", self.screenshots_dir()])
        self.args.extend(["-filesys.fname_snap",
                          "{0}-%p.%x".format(self.screenshots_name())])

        self.args.append(self.get_game_file())
        self.mednafen_post_configure()

    def configure_audio(self, f):
        pfx = self.mednafen_system_prefix()

    def configure_input(self, f):
        print("\n" + "-" * 79 + "\n" + "CONFIGURE PORTS")
        for i, port in enumerate(self.ports):
            input_mapping = self.mednafen_input_mapping(i)
            mapper = MednafenInputMapper(port, input_mapping)
            keys = {}
            for key, value in mapper.items():
                keys.setdefault(key, []).append(value)
            for key, values in keys.items():
                print(repr(key), repr(values))
                f.write("{key} {value}\n".format(
                    key=key, value="~".join(values)))

    def configure_video(self, f):
        pfx = self.mednafen_system_prefix()

        screen_w, screen_h = self.screen_size()
        # screen_a = screen_w / screen_h
        if self.border() == self.NO_BORDER:
            border_h = 0
            border_w = 0
        else:
            border_w = screen_h * 32 / 1080
            border_h = screen_h * 32 / 1080
        dest_w, dest_h = screen_w - border_w, screen_h - border_h
        if not self.use_fullscreen():
            dest_w, dest_h = 960, 540
        # dest_a = dest_w /dest_h

        viewport_src, viewport = self.mednafen_viewport()
        if viewport is None:
            game_w, game_h = self.game_video_size()
        else:
            game_w, game_h = viewport[2], viewport[3]
        assert game_w
        assert game_h
        # game_a = game_w / game_h
        pixel_a = self.game_video_par()

        if self.scaling() == self.MAX_SCALING:
            if self.stretching() == self.STRETCH_FILL_SCREEN:
                scale_y = dest_h / game_h
                scale_x = dest_w / game_w
            elif self.stretching() == self.STRETCH_ASPECT:
                # FIXME: HANDLE TALL RESOLUTIONS
                scale_y = dest_h / game_h
                # scale_x = dest_w / (game_w * pixel_a)
                scale_x = scale_y * pixel_a
            else:  # Square pixels
                scale_y = dest_h / game_h
                scale_x = scale_y
        elif self.scaling() == self.INTEGER_SCALING:
            if self.stretching() == self.STRETCH_FILL_SCREEN:
                scale_y = dest_h // game_h
                scale_x = dest_w // game_w
            elif self.stretching() == self.STRETCH_ASPECT:
                # FIXME: HANDLE TALL RESOLUTIONS
                scale_y = dest_h // game_h
                scale_x = scale_y * pixel_a
            else:  # Square pixels
                scale_y = dest_h // game_h
                scale_x = scale_y
        else:
            scale_x = 1
            scale_y = 1

        if self.use_doubling():
            if scale_x == 1 and scale_y == 1:
                scale_x = 2
                scale_y = 2
        #     self.emulator.args.extend(["-{}.special".format(pfx), "nn2x"])

        if self.smoothing() == self.SMOOTHING:
            videoip = "1"
        elif self.smoothing() == self.NON_INTEGER_SMOOTHING:
            if abs(scale_x - scale_x // 1) < 0.01:
                videoip = "y"
            else:
                videoip = "1"
            if abs(scale_y - scale_y // 1) < 0.01:
                if videoip == "y":
                    videoip = "0"
                else:
                    videoip = "x"
        else:
            videoip = "0"
        self.emulator.args.extend(["-{}.videoip".format(pfx), videoip])

        self.emulator.args.extend(["-{}.xscale".format(pfx), str(scale_x)])
        self.emulator.args.extend(["-{}.yscale".format(pfx), str(scale_y)])
        self.emulator.args.extend(["-{}.xscalefs".format(pfx), str(scale_x)])
        self.emulator.args.extend(["-{}.yscalefs".format(pfx), str(scale_y)])
        self.emulator.args.extend(["-{}.stretch".format(pfx), "0"])

        # Only enable v-sync if game refresh matches screen refresh.
        if self.configure_vsync():
            self.emulator.args.extend(["-glvsync", "1"])
        else:
            self.emulator.args.extend(["-glvsync", "0"])

        # Specify fullscreen size and conditionally enable fullscreen mode.
        self.emulator.args.extend(["-{}.xres".format(pfx), str(screen_w)])
        self.emulator.args.extend(["-{}.yres".format(pfx), str(screen_h)])
        if self.use_fullscreen():
            self.emulator.args.extend(["-fs", "1"])
        else:
            self.emulator.args.extend(["-fs", "0"])

        if self.effect() == self.CRT_EFFECT:
            self.emulator.args.extend(["-{}.shader".format(pfx), "goat"])
            self.emulator.args.extend(["-{}.shader.goat.slen".format(pfx), "1"])
            self.emulator.args.extend(["-{}.tblur".format(pfx), "1"])
            special = "none"
        elif self.effect() == self.HQ2X_EFFECT:
            special = "hq2x"
        elif self.effect() == self.SCALE2X_EFFECT:
            special = "scale2x"
        else:
            special = "nn2x"
        self.emulator.args.extend(["-{}.special".format(pfx), special])
        self.emulator.args.extend(self.mednafen_extra_graphics_options())

    def set_mednafen_input_order(self):
        if windows:
            self.input_device_order = 'DINPUT8'
        self.input_mapping_multiple = False

    def mednafen_extra_graphics_options(self):
        return []

    def mednafen_post_configure(self):
        # can be overridden by subclasses
        pass

    # def mednafen_refresh_rate(self):
    #     return 0.0
    #
    # def get_game_refresh_rate(self):
    #     # can be overridden by subclasses
    #     return self.mednafen_refresh_rate()

    def mednafen_cfg_path(self):
        if not os.path.exists(os.path.join(self.home.path, ".mednafen")):
            os.makedirs(os.path.join(self.home.path, ".mednafen"))
        return os.path.join(self.home.path, ".mednafen", "mednafen-09x.cfg")

        # config_path = os.path.join(os.environ['HOME'], '.mednafen')

        # the SDL version (even on Windows) seems to read HOME, so
        # use environment instead of pyapp.user.home_dir

        # try:
        #     config_path = os.path.join(os.environ['HOME'], '.mednafen')
        # except KeyError:
        #     config_path = os.path.join(pyapp.user.home_dir(), '.mednafen')
        # self.config_temp = self.create_temp_file(".mednafen")
        #  self.config_temp = self.create_temp_file(".mednafen")
        #  config_path = os.path.join(self.context.temp.dir('mednafen'),
        #  '.mednafen')
        # if not os.path.isdir(config_path):
        #     os.makedirs(config_path)
        # return os.path.join(config_path, "mednafen.cfg")
        # return self.config_temp.path

        # elif fs.windows:
        #     config_path = os.path.join(pyapp.fs.data_dir_user_app(),
        #             "mednafen")
        #     os.putenv("HOME", str_path_path(config_path))
        #     if not os.path.exists(config_path):
        #         os.makedirs(config_path)
        #     config_path = os.path.join(config_path, ".mednafen")
        #     if not os.path.exists(config_path):
        #         os.makedirs(config_path)
        #     return os.path.join(config_path, "mednafen.cfg")
        # elif fs.macosx:
        #     config_path = os.path.join(pyapp.user.home_dir(), "Library",
        #             "Application Support", "ZSNES")
        #     if not os.path.isdir(config_path):
        #         os.makedirs(config_path)
        #     return os.path.join(config_path, "zsnesl.cfg")

    # def get_joystick_unique_ids(self, controllers):
    #     unique_ids = {}
    #     for i in range(len(controllers)):
    #         controller = controllers[i]
    #         unique_id = self.get_joystick_unique_id(controller)
    #         plusplus = unique_ids.values().count(unique_id)
    #         unique_id += plusplus
    #         unique_ids[controller.id] = unique_id
    #     return unique_ids

    def is_pal(self):
        # return self.config.get("ntsc_mode") != "1"
        # return False
        refresh_rate = self.get_game_refresh_rate()
        if refresh_rate:
            return int(round(refresh_rate)) == 50


class MednafenInputMapper(InputMapper):
    def __init__(self, input, mapping):
        InputMapper.__init__(self, input, mapping)
        helper = EnumerateHelper()
        helper.init()
        seen_ids = set()
        self.id_map = {}
        for device in helper.devices:
            uid = self.calculate_unique_id(device)
            while uid in seen_ids:
                uid += 1
            seen_ids.add(uid)
            self.id_map[device.id] = uid
            # self.id_map[device.id.upper()] = uid
        print("MednafenInputMapper device map")
        for id, uid in self.id_map.items():
            print(uid, id)

    def axis(self, axis, positive):
        if positive:
            offset = 0x8000
        else:
            offset = 0xc000
        joystick_id = self.unique_id(self.device, self.device.id)
        return "joystick {0:x} {1:08x}".format(
            joystick_id, axis + offset)

    def hat(self, _, direction):
        offset = {
            "left": 8,
            "right": 2,
            "up": 1,
            "down": 4,
        }[direction]
        joystick_id = self.unique_id(self.device, self.device.id)
        return "joystick {0:x} {1:08x}".format(
            joystick_id, 0x2000 + offset)

    def button(self, button):
        joystick_id = self.unique_id(self.device, self.device.id)
        return "joystick {0:x} {1:08x}".format(
            joystick_id, int(button))

    def key(self, key):
        # FIXME: Need other key codes on Windows ... ?
        return "keyboard {0}".format(key.sdl_code)

    @lru_cache()
    def unique_id(self, device, _):
        try:
            return self.id_map[device.id]
        except KeyError:
            print("id_map:", self.id_map)
            raise

    @lru_cache()
    def calculate_unique_id(self, device):
        """Implements the joystick ID algorithm in mednafen.
        Was src/drivers/joystick.cpp:GetJoystickUniqueID
        Now src/drivers/Joystick.cpp:CalcOldStyleID.
        """
        print("get_unique_id for", device.id)
        m = hashlib.md5()
        print(device.axes, device.balls, device.hats, device.buttons)
        # noinspection SpellCheckingInspection
        buffer = struct.pack("iiii", device.axes, device.balls,
                             device.hats, device.buttons)
        m.update(buffer)
        digest = m.digest()
        ret = 0
        for x in range(16):
            # ret ^= ord(digest[x]) << ((x & 7) * 8)
            ret ^= digest[x] << ((x & 7) * 8)
        return ret
