# FSGS - Common functionality for FS Game System.
# Copyright (C) 2013-2019  Frode Solheim <frode@solheim.dev>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
FSGS Game Driver for Commodore 64 (C64).

TODO:

* Handle V-SYNC
* Gamepad select button -> toggle status bar?
* Cleanup temp files
* Consider gamepad mappings for tape control
* Ability to select input devices, and control device type via database config
* Config key to set C64 model
* Gamepad button to open attack disk / tape menu?
* Handle save games properly (did C64 games save to tape? disk only?)
* Alt+S for screenshot and store screenshots to Screenshots dir
* Mouse support (need a use case / test game)

FIXME:

* FIXME: Positional keyboard support
  Keyboard: Error - Cannot load keymap `sdl_pos.vkm'.

"""
import json
import os

import shutil

from fsbc.system import windows, macosx
from fsgs.drivers.gamedriver import GameDriver
from fsgs.input.mapper import InputMapper
from fsgs.util import sdl2
from fsgs.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

C64_MODEL_C64 = "c64"
C64_MODEL_C64C = "c64c"
C64_MODEL_C64C_1541_II = "c64c/1541-ii"
C64_JOYSTICK = {
    "type": "joystick",
    "description": "Joystick",
    "mapping_name": "c64",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
C64_PORTS = [
    {
        "description": "Port 2",
        "types": [NO_CONTROLLER, C64_JOYSTICK],
        "type_option": "c64_port_2_type",
        "device_option": "c64_port_2",
    },
    {
        "description": "Port 1",
        "types": [NO_CONTROLLER, C64_JOYSTICK],
        "type_option": "c64_port_1_type",
        "device_option": "c64_port_1",
    },
]
C64_VIDEO_WIDTH = 384
C64_VIDEO_HEIGHT = 272
VICE_KEY_SET_A = 2
VICE_KEY_SET_B = 3
VICE_JOYSTICK = 4


class Commodore64Platform(Platform):
    PLATFORM_NAME = "Commodore 64"

    def __init__(self):
        super().__init__(Commodore64Loader, Commodore64ViceDriver)

    def driver(self, fsgc):
        return Commodore64ViceDriver(fsgc)

    def loader(self, fsgc):
        return Commodore64Loader(fsgc)


class Commodore64Loader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        # assert len(file_list) == 1
        for i, item in enumerate(file_list):
            _, ext = os.path.splitext(item["name"])
            ext = ext.upper()
            if ext in [".TAP", ".T64"]:
                if i == 0:
                    self.config["tape_drive_0"] = "sha1://{}/{}".format(
                        item["sha1"], item["name"]
                    )
                self.config[
                    "tape_image_{0}".format(i)
                ] = "sha1://{}/{}".format(item["sha1"], item["name"])
            elif ext in [".D64"]:
                if i == 0:
                    self.config["floppy_drive_0"] = "sha1://{}/{}".format(
                        item["sha1"], item["name"]
                    )
                self.config[
                    "floppy_image_{}".format(i)
                ] = "sha1://{0}/{1}".format(item["sha1"], item["name"])

    def load_extra(self, values):
        model = values["c64_model"]

        # FIXME: Legacy
        if not model:
            model = values["model"]
        # FIXME: Remove?
        self.config["model"] = ""

        if not model:
            model = C64_MODEL_C64C
        self.config[Option.C64_MODEL] = model

        self.config["c64_port_1_type"] = values["c64_port_1_type"]
        self.config["c64_port_2_type"] = values["c64_port_2_type"]


class Commodore64ViceDriver(GameDriver):
    PORTS = C64_PORTS

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.fsemu = True
        self.emulator.name = "x64sc-fs"
        self.helper = Commodore64Helper(self.options)

    def prepare(self):
        dot_vice_dir = os.path.join(self.home.path, ".vice")
        if os.path.exists(dot_vice_dir):
            shutil.rmtree(dot_vice_dir)
        os.makedirs(dot_vice_dir)
        dot_vice_dir = os.path.join(self.home.path, ".config", ".vice")
        if os.path.exists(dot_vice_dir):
            shutil.rmtree(dot_vice_dir)
        os.makedirs(dot_vice_dir)

        # noinspection SpellCheckingInspection
        joymap_file = self.temp_file("joymap.vjm").path
        with open(joymap_file, "w", encoding="UTF-8") as f:
            self.create_joymap_file(f)
        # noinspection SpellCheckingInspection
        if windows:
            # Not using normpath because os.sep can be "/" on MSYS2,
            # and Vice on Windows really requires backslashes here.
            joymap_file = joymap_file.replace("/", "\\")
        self.emulator.args.extend(["-joymap", joymap_file])

        hotkey_file = self.temp_file("hotkey.vkm").path
        with open(hotkey_file, "w", encoding="UTF-8") as f:
            self.create_hotkey_file(f)
        # noinspection SpellCheckingInspection
        if windows:
            hotkey_file = hotkey_file.replace("/", "\\")
        self.emulator.args.extend(["-hotkeyfile", hotkey_file])

        config_file = self.temp_file("vice.cfg").path
        with open(config_file, "w", encoding="UTF-8") as f:
            self.create_vice_cfg(f)
            self.configure_audio(f)
            self.configure_input(f)
            self.configure_video(f)
        self.emulator.args.extend(["-config", config_file])

        # self.emulator.args.extend(["-model", "c64"])
        if self.helper.model() == C64_MODEL_C64:
            self.set_model_name("Commodore C64")
            self.emulator.args.extend(["-model", "c64"])
        elif self.helper.model() == C64_MODEL_C64C_1541_II:
            self.set_model_name("Commodore C64C 1541-II")
            self.emulator.args.extend(["-model", "c64c"])
        else:
            self.set_model_name("Commodore C64C")
            self.emulator.args.extend(["-model", "c64c"])

        media_keys = ["floppy_drive_0", "tape_drive_0"]
        for i in range(20):
            media_keys.append("floppy_image_{0}".format(i))
            media_keys.append("tape_image_{0}".format(i))
        unique_uris = set()
        for key in media_keys:
            if self.options[key]:
                unique_uris.add(self.options[key])
        # media_dir = self.temp_dir("media")
        # VICE uses CWD as default directory for media files
        media_dir = self.cwd
        for file_uri in unique_uris:
            input_stream = self.fsgc.file.open(file_uri)
            game_file = os.path.join(media_dir.path, file_uri.split("/")[-1])
            with open(game_file, "wb") as f:
                f.write(input_stream.read())

        if self.options[Option.TAPE_DRIVE_0]:
            file_uri = self.options[Option.TAPE_DRIVE_0]
        else:
            file_uri = self.options[Option.FLOPPY_DRIVE_0]

        autostart_file = os.path.join(media_dir.path, file_uri.split("/")[-1])
        self.emulator.args.extend(["-autostart", autostart_file])

    def finish(self):
        pass

    def create_vice_cfg(self, f):
        f.write("[C64SC]\n")
        f.write("ConfirmOnExit=0\n")
        # f.write("KeepAspectRatio=1\n")
        f.write("VICIIDoubleScan=1\n")
        f.write("HwScalePossible=1\n")
        # 0 means SDL_FULLSCREEN_DESKTOP - 1 means SDL_FULLSCREEN
        f.write("VICIISDLFullscreenMode=0\n")
        f.write("AutostartWarp=0\n")
        f.write("\n")

        if self.helper.has_floppy_drive():
            f.write("Drive8Type=1541\n")
        else:
            # f.write("FileSystemDevice8=0\n")
            f.write("Drive8Type=None\n")
        f.write("\n")

        # Virtual device traps?
        # f.write("VirtualDevices=1\n")

        # print("set_media_options")
        # media_list = self.create_media_list()
        # print("sort media list")
        # # FIXME: SORT ON name (lowercase) ONLY, not whole path, because
        # # some files may have moved to another dir (temp dir)
        # media_list = sorted(media_list)
        # print(media_list)
        # if media_list[0].lower()[-4:] == ".crt":
        #     f.write("CartridgeFile=\"{path}\"\n".format(path=media_list[0]))
        #     f.write("CartridgeType={type}\n".format(type=0))
        #     f.write("CartridgeMode={mode}\n".format(mode=0))
        #     f.write("CartridgeReset={reset}\n".format(reset=1))
        # #    #self.args.extend(["-autostart", media_list[0]])
        # else:
        #     #f.write('AutostartPrgMode=2\n') # disk image
        #     #f.write('AutostartPrgDiskImage="{path}"\n'.format(
        #     #        path=media_list[0]))
        #     self.add_arg("-autostart", media_list[0])

        # # FIXME: Floppies?
        # print(media_list)
        # if media_list[0].lower()[-4:] == ".d64":
        #     f = self.context.temp.file('fliplist')
        #     f.write("# Vice fliplist file\n\n")
        #     f.write("UNIT 8\n")
        #     print("FLIP LIST:")
        #     # Make sure first disk is added to the end of the fliplist
        #     for floppy in (media_list[1:] + [media_list[:1]]):
        #         print("%s\n" % (floppy,))
        #         print
        #         f.write("%s\n" % (floppy,))
        #     f.close()
        #     self.add_arg("-flipname", self.context.temp.file("fliplist"))
        #
        # media_dir = os.path.dirname(media_list[0])
        # print(media_dir)
        # f.write("InitialDefaultDir=\"{dir}\"\n".format(dir=media_dir))
        # f.write("InitialTapeDir=\"{dir}\"\n".format(dir=media_dir))
        # f.write("InitialCartDir=\"{dir}\"\n".format(dir=media_dir))
        # f.write("InitialDiskDir=\"{dir}\"\n".format(dir=media_dir))
        # f.write("InitialAutostartDir=\"{dir}\"".format(dir=media_dir))

    # def vice_prepare_floppies(self):
    #     floppies = []
    #     #media_dir = os.path.dirname(self.context.game.file)
    #     #base_match = self.extract_match_name(os.path.basename(
    #     #        self.context.game.file))
    #     #for name in os.listdir(media_dir):
    #     #    dummy, ext = os.path.splitext(name)
    #     #    if ext.lower() not in ['.st']:
    #     #        continue
    #     #    match = self.extract_match_name(name)
    #     #    if base_match == match:
    #     #        floppies.append(os.path.join(media_dir, name))
    #     #        #floppies.append(name)
    #     if self.config["floppy_drive_0"]:
    #         floppies.append(self.config["floppy_drive_0"])
    #     return floppies

    def configure_audio(self, f):
        # Seems to be some issues with sound in VICE (buffers filling up,
        # slowing down the emulation?). Using defaults for now (uses big
        # buffers by default, only seems to delay the problem).
        # return
        if self.fsemu:
            audio_driver = "fsemu"
        else:
            audio_driver = self.options[Option.VICE_AUDIO_DRIVER]
            audio_driver = "sdl"
            f.write("SoundBufferSize={0}\n".format(50))
        if audio_driver:
            print("[VICE] Using audio driver", repr(audio_driver))
            f.write("SoundDeviceName={0}\n".format(audio_driver))
        # else:
        #     audio_driver = self.config.get("audio_driver", "")
        #     if audio_driver == "sdl":
        #         f.write("SoundDeviceName={0}\n".format(audio_driver))

        if self.use_audio_frequency():
            f.write("SoundSampleRate={0}\n".format(self.use_audio_frequency()))
        # default buffer size for vice is 100ms, that's far too much...
        # EDIT: Lowering the sound buffer size seems to cause FPS problems
        # Maybe due to buffer filling up and emu running slower (??)
        # f.write("SoundBufferSize={0}\n".format(50))
        if self.options[Option.FLOPPY_DRIVE_VOLUME] == 0:
            f.write("DriveSoundEmulation=0\n")
        else:
            # f.write("DriveSoundEmulationVolume=1200\n")
            f.write("DriveSoundEmulation=1\n")
        f.write("\n")

    def configure_input(self, f):
        # FIXME: Enable when ready
        f.write("KeymapIndex=1\n")  # Use positional keys

        for i, port in enumerate(self.ports):
            vice_port = [2, 1, 3, 4][i]
            # vice_port = i + 1
            if port.type == "joystick":
                vice_port_type = 1
            else:
                vice_port_type = 0

            if port.device is None:
                vice_device_type = 0
            elif port.device.type == "joystick":
                vice_device_type = VICE_JOYSTICK
            elif port.device.type == "keyboard":
                vice_device_type = VICE_KEY_SET_A + i
                # assert False
            else:
                vice_port_type = 0
            f.write("JoyPort{0}Device={1}\n".format(vice_port, vice_port_type))
            f.write("JoyDevice{0}={1}\n".format(vice_port, vice_device_type))
            print(
                "[INPUT] Port",
                port.type_option,
                "VicePort",
                vice_port,
                port.type,
                port.device,
            )

            if port.device is None:
                continue
            if port.device.type != "keyboard":
                continue
            input_mapping = {
                "1": "KeySet{0}Fire".format(i + 1),
                "UP": "KeySet{0}North".format(i + 1),
                "DOWN": "KeySet{0}South".format(i + 1),
                "LEFT": "KeySet{0}West".format(i + 1),
                "RIGHT": "KeySet{0}East".format(i + 1),
            }
            mapper = ViceInputMapper(port, input_mapping)
            for key, value in mapper.items():
                f.write("{0}={1}\n".format(key, value))
        f.write("\n")

    def configure_video(self, f):
        # Enable the "Pepto" palette (http://www.pepto.de/projects/colorvic/)
        # f.write("VICIIPaletteFile=\"vice\"\n")
        palette_file = self.options[Option.C64_PALETTE]
        if not palette_file:
            # palette_file = "pepto-ntsc-sony"
            # palette_file = "vice"
            # palette_file = "community-colors"
            palette_file = "0"
        if palette_file != "0":
            f.write("VICIIExternalPalette=1\n")
            f.write('VICIIPaletteFile="{}"\n'.format(palette_file))

        f.write("VICIIAudioLeak=1\n")

        if self.effect() == self.CRT_EFFECT:
            f.write("VICIIFilter=1\n")
        elif self.effect() == self.DOUBLE_EFFECT:
            f.write("VICIIFilter=0\n")
        elif self.effect() == self.HQ2X_EFFECT:
            # HQ2X is not supported
            f.write("VICIIFilter=0\n")
        elif self.effect() == self.SCALE2X_EFFECT:
            f.write("VICIIFilter=2\n")
        else:
            f.write("VICIIFilter=0\n")
            f.write("VICIIDoubleSize=0\n")

        screen_w, screen_h = self.screen_size()

        if self.use_fullscreen():
            f.write("VICIIFullscreen=1\n")

        f.write("SDLWindowWidth={w}\n".format(w=960))
        f.write("SDLWindowHeight={h}\n".format(h=540))
        f.write("SDLCustomWidth={w}\n".format(w=screen_w))
        f.write("SDLCustomHeight={h}\n".format(h=screen_h))

        if self.scaling() == self.MAX_SCALING:
            f.write("VICIIHwScale=1\n")
        elif self.scaling() == self.INTEGER_SCALING:
            # FIXME: Does not support this yet, disabling scaling
            f.write("VICIIHwScale=0\n")
        else:
            f.write("VICIIHwScale=0\n")

        if self.stretching() == self.STRETCH_FILL_SCREEN:
            f.write("SDLGLAspectMode=0\n")
        elif self.stretching() == self.STRETCH_ASPECT:
            f.write("SDLGLAspectMode=2\n")
        else:
            f.write("SDLGLAspectMode=1\n")

        # if self.border() == self.LARGE_BORDER:
        #     f.write("VICIIBorderMode=1\n")
        # elif self.border() == self.SMALL_BORDER:
        #     # Value 4 is an FSGS extension in Vice-FS.
        #     f.write("VICIIBorderMode=4\n")
        # else:
        #     f.write("VICIIBorderMode=3\n")

        # Experimental "540 border mode"
        f.write("VICIIBorderMode=5\n")

        # # Disable scanlines in CRT mode
        # f.write("VICIIPALScanLineShade=1000\n")
        # Disable scanlines in CRT mode
        f.write("VICIIPALScanLineShade=850\n")

        # Can this be used to set fullscreen desktop, etc?
        # f.write("VICIISDLFullscreenMode = 1\n")

        f.write("\n")

    def create_joymap_file(self, f):
        # VICE joystick mapping file
        #
        # A joystick map is read in as patch to the current map.
        #
        # File format:
        # - comment lines start with '#'
        # - keyword lines start with '!keyword'
        # - normal line has 'joynum inputtype inputindex action'
        #
        # Keywords and their lines are:
        # '!CLEAR'    clear all mappings
        #
        # inputtype:
        # 0      axis
        # 1      button
        # 2      hat
        # 3      ball
        #
        # Note that each axis has 2 inputindex entries and each hat has 4.
        #
        # action [action_parameters]:
        # 0               none
        # 1 port pin      joystick (pin: 1/2/4/8/16 = u/d/l/r/fire)
        # 2 row col       keyboard
        # 3               map
        # 4               UI activate
        # 5 path&to&item  UI function
        #
        f.write("!CLEAR\n")
        for i, port in enumerate(self.ports):
            if port.device is None:
                continue
            if port.device.type != "joystick":
                continue
            if i == 0:
                input_mapping = {
                    "1": "1 1 16 ",
                    "UP": "1 1 1",
                    "DOWN": "1 1 2",
                    "LEFT": "1 1 4",
                    "RIGHT": "1 1 8",
                    "MENU": "4",
                }
            elif i == 1:
                input_mapping = {
                    "1": "1 0 16 ",
                    "UP": "1 0 1",
                    "DOWN": "1 0 2",
                    "LEFT": "1 0 4",
                    "RIGHT": "1 0 8",
                    "MENU": "4",
                }
            else:
                raise Exception("Invalid port")
            mapper = ViceInputMapper(port, input_mapping)
            for key, value in mapper.items():
                f.write("{0} {1}\n".format(value, key))

    def create_hotkey_file(self, f):
        # noinspection SpellCheckingInspection
        hotkeys = [
            (sdl2.SDLK_i, "Statusbar"),
            # (112, "Pause"),  # Mod+Pause
            # (113, "Quit emulator"),  # Mod+Q
            # ALT+S
            # (115, "Snapshot&Save snapshot image"),
            # (115, "Screenshot&Save PNG screenshot"),  # Mod+S
            (
                sdl2.SDLK_s,
                "Save media file&Create screenshot&Save PNG screenshot",
            ),
            (sdl2.SDLK_RETURN, "Video settings&Size settings&Fullscreen"),
            # (119, "Speed settings&Warp mode"),  # Mod+W
        ]
        if macosx:
            mod = 8  # Cmd key
        else:
            mod = 2  # Left alt key
        # f.write("!CLEAR\n")
        for key, action in hotkeys:
            f.write(
                "{0} {1}\n".format(sdl2.SDL_NUM_SCANCODES * mod + key, action)
            )


class ViceInputMapper(InputMapper):
    def axis(self, axis, positive):
        offset = 0 if positive else 1
        return "{0} 0 {1}".format(self.device.index, axis * 2 + offset)

    def hat(self, hat, direction):
        offset = {"left": 2, "right": 3, "up": 0, "down": 1}[direction]
        return "{0} 2 {1}".format(self.device.index, hat * 4 + offset)

    def button(self, button):
        return "{0} 1 {1}".format(self.device.index, button)

    def key(self, key):
        return "{0}".format(key.sdl1_key_code)


class Commodore64Helper:
    def __init__(self, options):
        self.options = options

    def accuracy(self):
        try:
            accuracy = int(self.options.get(Option.ACCURACY, "1"))
        except ValueError:
            accuracy = 1
        return accuracy

    def has_floppy_drive(self):
        if self.model() == C64_MODEL_C64C_1541_II:
            return "1541-II"
        return None

    def model(self):
        if self.options[Option.C64_MODEL] == "c64":
            return C64_MODEL_C64
        elif self.options[Option.C64_MODEL] == "c64c":
            return C64_MODEL_C64C
        elif self.options[Option.C64_MODEL] == "c64c/1541-ii":
            return C64_MODEL_C64C_1541_II
        return C64_MODEL_C64C
