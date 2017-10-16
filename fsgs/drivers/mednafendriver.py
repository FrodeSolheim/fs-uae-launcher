import hashlib
import json
import os
import struct
from functools import lru_cache

import shutil

from fsbc.paths import Paths
from fsbc.system import System
from fsgs.Archive import Archive
from fsgs.drivers.gamedriver import GameDriver, Emulator
from fsgs.input.enumeratehelper import EnumerateHelper
from fsgs.input.mapper import InputMapper
from fsgs.option import Option
from fsgs.saves import SaveHandler


class MednafenDriver(GameDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc)
        self.emulator = Emulator("mednafen-fs")
        self.save_handler = SaveHandler(self.fsgc, options=self.options)
        # self._game_files_added = False

    def prepare(self):
        if os.path.exists(os.path.join(self.home.path, ".mednafen")):
            shutil.rmtree(os.path.join(self.home.path, ".mednafen"))
        self.save_handler.prepare()
        # self.temp_home = self.create_temp_dir("mednafen-home")
        with open(self.mednafen_cfg_path(), "w", encoding="UTF-8") as f:
            self.mednafen_configure(f)
        # if not self._game_files_added:
        game_file = self.get_game_file()
        if game_file is not None:
            self.emulator.args.append(game_file)

    def finish(self):
        self.save_handler.finish()

    def set_mednafen_aspect(self, h, v):
        if self.stretching() == self.NO_STRETCHING:
            h, v = self.game_video_size()
        self.emulator.env["FSGS_ASPECT"] = "{}/{}".format(h, v)

    # FIXME: REPLACE BAD IMPLEMENTATION OF prepare cd images

    @staticmethod
    def expand_default_path(src, default_dir):
        if "://" in src:
            return src, None
        src = Paths.expand_path(src, default_dir)
        archive = Archive(src)
        return src, archive

    def prepare_mednafen_cd_images(self):
        # self._game_files_added = True

        temp_dir = self.temp_dir("media").path
        game_file = None
        # cdrom_drive_0 = self.config.get("cdrom_drive_0", "")
        # if cdrom_drive_0.startswith("game:"):
        if True:
            # scheme, dummy, game_uuid, name = cdrom_drive_0.split("/")
            # file_list = self.get_file_list_for_game_uuid(game_uuid)
            file_list = json.loads(self.options[Option.FILE_LIST])
            for file_item in file_list:
                src = self.fsgc.file.find_by_sha1(file_item["sha1"])

                src, archive = self.expand_default_path(src, None)
                dst_name = file_item["name"]
                # current_task.set_progress(dst_name)

                dst = os.path.join(temp_dir, dst_name)
                self.fsgc.file.copy_game_file(src, dst)

            # cue_sheets = self.get_cue_sheets_for_game_uuid(game_uuid)
            cue_sheets = json.loads(self.options[Option.CUE_SHEETS])
            for i, cue_sheet in enumerate(cue_sheets):
                # FIXME: Try to get this to work with the PyCharm type checker
                path = os.path.join(temp_dir, cue_sheet["name"])
                if i == 0:
                    game_file = path
                # noinspection PyTypeChecker
                with open(path, "wb") as f:
                    # noinspection PyTypeChecker
                    f.write(cue_sheet["data"].encode("UTF-8"))
        self.emulator.args.append(game_file)

    def prepare_mednafen_bios(self, known_file, name):
        bios_path = os.path.join(self.home.path, ".mednafen", name)
        if not os.path.exists(os.path.dirname(bios_path)):
            os.makedirs(os.path.dirname(bios_path))
        src = self.fsgc.file.find_by_sha1(known_file.sha1)
        if not src:
            raise Exception("Could not find {} (SHA-1: {}".format(
                known_file.name, known_file.sha1))
        self.fsgc.file.copy_game_file(src, bios_path)

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
        viewport = self.options["viewport"]
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

        cheats_file_name = self.mednafen_system_prefix() + ".cht"
        cheats_file_path = self.cheats_file(cheats_file_name)
        if cheats_file_path:
            self.emulator.args.extend(["-cheats", "0"])
            cheats_dir = self.temp_dir("cheats").path
            shutil.copy(
                cheats_file_path, os.path.join(cheats_dir, cheats_file_name))
            # self.emulator.args.extend(["-filesys.path_cheat", cheats_dir])
            self.emulator.args.extend(["-path_cheat", cheats_dir])

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
        # self.emulator.args.extend(["-{}.xres".format(pfx), str(screen_w)])
        # self.emulator.args.extend(["-{}.yres".format(pfx), str(screen_h)])
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
        #     self.emulator.args.extend(["-%s.xscalefs" % pfx, str(x_scale)])
        #     self.emulator.args.extend(["-%s.yscalefs" % pfx, str(y_scale)])
        #     self.emulator.args.extend(["-%s.stretch" % pfx, "0"])
        # else:
        #     if self.use_stretching():
        #         self.emulator.args.extend(["-%s.stretch" % pfx, "full"])
        #     else:
        #         self.emulator.args.extend(["-%s.stretch" % pfx, "aspect"])
        #
        # if self.use_fullscreen():
        #     pass
        # else:
        #     self.emulator.args.extend(["-%s.xscale" % pfx, "2"])
        #     self.emulator.args.extend(["-%s.yscale" % pfx, "2"])

        # self.emulator.args.extend(["-%s.scanlines" % pfx, "0"])
        # if gamew < 200:
        #     self.emulator.args.extend(["-%s.xscale" % pfx, "4"])
        #     self.emulator.args.extend(["-%s.yscale" % pfx, "4"])
        # else:
        #     self.emulator.args.extend(["-%s.xscale" % pfx, "3"])
        #     self.emulator.args.extend(["-%s.yscale" % pfx, "3"])
        # self.emulator.args.extend(["-%s.videoip" % pfx, "0"])
        #  FIXME:
        # self.options.smooth = False
        # self.options.filter = '2x'

        # if self.use_doubling():
        #     self.emulator.args.extend(["-%s.special" % pfx, "nn2x"])
        #
        # self.emulator.args.extend(self.mednafen_extra_graphics_options())

        # filter_data = self.configure_filter()
        # if filter_data["name"] == "ntsc":
        #     self.emulator.args.extend(["-{0}.ntscblitter".format(pfx), "1"])
        #     self.emulator.args.extend(["-{0}.ntsc.preset".format(pfx), "composite"])
        #     self.emulator.args.extend(["-{0}.ntsc.saturation".format(pfx), "0.5"])
        # else:
        #     self.emulator.args.extend(
        #         ["-{0}.special".format(pfx), filter_data["special"]])

        # self.emulator.args.extend(["-%s.special" % pfx,
        # self.mednafen_special_filter()])

        # if self.configure_vsync():
        #     self.emulator.args.extend(["-glvsync", "1"])
        # else:
        #     self.emulator.args.extend(["-glvsync", "0"])

        # # FIXME: Deprecated?
        # elif self.config.get("audio_driver", "") in ["sdl", "pulseaudio"]:
        #     # Mednafen does not support PulseAudio directly, but using the
        #     # sdl driver will "often" result in PulseAudio being used
        #     # indirectly.
        #     self.emulator.args.extend(["-sound.driver", "sdl"])

        print("\n" + "-" * 79 + "\n" + "CONFIGURE DIRS")

        state_dir = self.emulator_state_dir("mednafen")

        self.emulator.args.extend(["-path_sav", self.save_handler.save_dir()])
        self.emulator.args.extend([
            "-path_state", self.save_handler.emulator_state_dir("Mednafen")])

        # self.emulator.args.extend(["-filesys.fname_state", "%M%X"])
        # self.emulator.args.extend(["-filesys.fname_sav", "%M%x"])

        self.emulator.args.extend(["-filesys.fname_state", "%f.%X"])
        self.emulator.args.extend(["-filesys.fname_sav", "%f.%x"])

        # docdir = pyapp.user.documents_dir()
        self.doc_dir = self.temp_dir("mednafen-docs")
        self.emulator.args.extend([
            "-path_movie", self.doc_dir.path,
            # "-path_cheat", self.doc_dir.path,
            "-path_palette", self.home.path])

        self.emulator.args.extend(["-path_snap", self.screenshots_dir()])
        self.emulator.args.extend([
            "-filesys.fname_snap", "{0}-%p.%x".format(self.screenshots_name())])

        self.mednafen_post_configure()

    def configure_audio(self, _):
        # pfx = self.mednafen_system_prefix()
        audio_driver = self.options[Option.MEDNAFEN_AUDIO_DRIVER]
        if audio_driver in ["", "auto"]:
            if System.windows:
                pass
            elif System.macos:
                pass
            else:
                audio_driver = "sdl"
        if audio_driver == "sdl":
            # Mednafen does not support PulseAudio directly, but using the
            # sdl driver will "often" result in PulseAudio being used
            # indirectly.
            self.emulator.args.extend(["-sound.driver", "sdl"])
        elif audio_driver == "alsa":
            self.emulator.args.extend(
                ["-sound.device", "sexyal-literal-default"])
        else:
            # Use Mednafen default selection
            # self.emulator.args.extend(["-sound.device", "default"])
            pass

        default_buffer_size = 40
        buffer_size = default_buffer_size
        if self.options[Option.MEDNAFEN_AUDIO_BUFFER]:
            try:
                buffer_size = int(self.options[Option.MEDNAFEN_AUDIO_BUFFER])
            except ValueError:
                print("WARNING: Invalid Mednafen audio buffer size specified")
            else:
                if buffer_size < 0 or buffer_size > 1000:
                    print("WARNING: Mednafen audio buffer size out of range")
                    buffer_size = default_buffer_size
        self.emulator.args.extend(
            ["-sound.buffer_time", str(buffer_size)])

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
        self.emulator.args.extend(["-video.driver", "opengl"])

        screen_w, screen_h = self.screen_size()
        # screen_a = screen_w / screen_h
        border_w, border_h = 0, 0

        # if self.border() == self.NO_BORDER:
        #     pass
        # else:
        #     border_w = screen_h * 32 / 1080
        #     border_h = screen_h * 32 / 1080

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
        # self.emulator.args.extend(["-{}.special".format(pfx), "nn2x"])

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
            self.emulator.args.extend(["-video.glvsync", "1"])
        else:
            self.emulator.args.extend(["-video.glvsync", "0"])

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
            # self.emulator.args.extend(["-{}.tblur".format(pfx), "1"])
            special = "none"
            video_scale = 2
            min_video_scale = 2
        elif self.effect() == self.DOUBLE_EFFECT:
            special = "nn2x"
            video_scale = 2
            min_video_scale = 1
        elif self.effect() == self.HQ2X_EFFECT:
            special = "hq2x"
            video_scale = 2
            min_video_scale = 2
        elif self.effect() == self.SCALE2X_EFFECT:
            special = "scale2x"
            video_scale = 2
            min_video_scale = 2
        else:
            special = "none"
            video_scale = 1
            min_video_scale = 1

        if self.scaling() == self.MAX_SCALING:
            window_w, window_h = 960, 540
        elif self.scaling() == self.INTEGER_SCALING:
            window_w = game_w * min_video_scale
            window_h = game_h * min_video_scale
            s = min_video_scale + 1
            print(window_w, window_h)
            while game_w * s <= 900 and game_h * s <= 700:
                window_w = game_w * s
                window_h = game_h * s
                s += 1
        else:
            window_w = game_w * video_scale
            window_h = game_h * video_scale
        self.emulator.env["FSGS_WINDOW_SIZE"] = "{},{}".format(
            window_w, window_h)

        self.emulator.args.extend(["-{}.special".format(pfx), special])
        self.emulator.args.extend(self.mednafen_extra_graphics_options())

    def set_mednafen_input_order(self):
        if System.windows:
            self.input_device_order = "DINPUT8"
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
    def __init__(self, port, mapping):
        InputMapper.__init__(self, port, mapping)
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
