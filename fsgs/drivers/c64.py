# FSGS - Common functionality for FS Game System.
# Copyright (C) 2013-2016  Frode Solheim <frode@openretro.org>
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
import os

from fsbc.system import windows, macosx
from fsgs.input.sdlkeycodes import SDLK_LAST
from fsgs.runner import GameRunner
from fsgs.input.mapper import InputMapper

C64_VIDEO_WIDTH = 384
C64_VIDEO_HEIGHT = 272


class C64Driver(GameRunner):

    CONTROLLER = {
        "type": "joystick",
        "description": "Joystick",
        "mapping_name": "c64",
    }

    PORTS = [
        {
            "description": "Port 2",
            "types": [CONTROLLER]
        },
        {
            "description": "Port 1",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = "x64sc-fs"

    def prepare(self):
        dot_vice_dir = os.path.join(self.home.path, ".vice")
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
        self.args.extend(["-joymap", joymap_file])

        hotkey_file = self.temp_file("hotkey.vkm").path
        with open(hotkey_file, "w", encoding="UTF-8") as f:
            self.create_hotkey_file(f)
        # noinspection SpellCheckingInspection
        if windows:
            hotkey_file = hotkey_file.replace("/", "\\")
        self.args.extend(["-hotkeyfile", hotkey_file])

        config_file = self.temp_file("vice.cfg").path
        with open(config_file, "w", encoding="UTF-8") as f:
            self.create_vice_cfg(f)
            # self.configure_input(f)
        self.args.extend(["-config", config_file])

        media_keys = ["floppy_drive_0", "tape_drive_0"]
        for i in range(20):
            media_keys.append("floppy_image_{0}".format(i))
            media_keys.append("tape_image_{0}".format(i))
        unique_uris = set()
        for key in media_keys:
            if self.config[key]:
                unique_uris.add(self.config[key])
        # media_dir = self.temp_dir("media")
        # VICE uses CWD as default directory for media files
        media_dir = self.cwd
        for file_uri in unique_uris:
            input_stream = self.fsgs.file.open(file_uri)
            game_file = os.path.join(media_dir.path, file_uri.split("/")[-1])
            with open(game_file, "wb") as f:
                f.write(input_stream.read())

        if self.config["tape_drive_0"]:
            file_uri = self.config["tape_drive_0"]
        else:
            file_uri = self.config["floppy_drive_0"]
        autostart_file = os.path.join(media_dir.path, file_uri.split("/")[-1])
        self.args.extend(["-autostart", autostart_file])

    def finish(self):
        pass

    def create_vice_cfg(self, f):
        f.write("[C64SC]\n")
        f.write("ConfirmOnExit=0\n")
        # f.write("KeepAspectRatio=1\n")
        f.write("VICIIDoubleScan=1\n")
        f.write("HwScalePossible=1\n")
        f.write("VICIISDLFullscreenMode=1\n")
        f.write("AutostartWarp=0\n")
        f.write("Drive8Type=1541\n")
        f.write("\n")

        f.write("VICIIExternalPalette=1\n")
        # Enable the "Pepto" palette (http://www.pepto.de/projects/colorvic/)
        # f.write("VICIIPaletteFile=\"vice\"\n")
        f.write("VICIIPaletteFile=\"pepto-ntsc-sony\"\n")

        filter = ""
        if filter == "scale2x":
            f.write("VICIIFilter=2\n")
        elif filter == "crt":
            f.write("VICIIFilter=1\n")
        else:
            f.write("VICIIFilter=0\n")

        screen_w, screen_h = self.screen_size()
        f.write("SDLCustomWidth={w}\n".format(w=screen_w))
        f.write("SDLCustomHeight={h}\n".format(h=screen_h))

        if self.use_fullscreen():
            f.write("VICIIFullscreen=1\n")
            f.write("VICIIHwScale=1\n")
            if self.use_stretching():
                border = False
                if not border:
                    f.write("VICIIBorderMode=3\n")
                #     original_aspect = 320 / 200
                # else:
                #     original_aspect = C64_VIDEO_WIDTH / C64_VIDEO_HEIGHT
                # screen_aspect = screen_w / screen_h
                # custom_aspect = screen_aspect / original_aspect
                # print("custom aspect is", custom_aspect)
                # f.write("AspectRatio={0}\n".format(custom_aspect))
                # f.write("SDLGLAspectMode=1\n")
                f.write("SDLGLAspectMode=0\n")

            # f.write("FullscreenEnabled=1\n")
            # if fs.linux:
            #     self.args.append("-VICIIhwscale")
            #     hwscoords = self.set_hwscale_coords()
            # else:
            #     pass
            #     #if self.options["zoom"]:
            #     #    logger.warning("zoom is not supported on this platform")
            #     #if self.options["stretch"]:
            #     #    logger.warning("stretch not supported on this platform")
            #     #if self.options["border"]:
            #     #    logger.warning("border not supported on this platform")
            # if fs.macosx:
            #     #logger.warning("Fullscreen not supported on Mac OS X")
            #     pass
            # else:
            # self.add_arg("-fullscreen")
        else:
            f.write("VICIIHwScale=0\n")

        if self.use_audio_frequency():
            f.write("SoundSampleRate={0}\n".format(self.use_audio_frequency()))
        # default buffer size for vice is 100ms, that's far too much...
        # f.write("SoundBufferSize={0}\n".format(20))

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

        VICE_KEYSET_A = 2
        VICE_KEYSET_B = 3
        VICE_JOYSTICK = 4

        # FIXME: Enable when ready
        # f.write("KeymapIndex=1\n")  # Use positional keys

        for i, port in enumerate(self.ports):
            vice_port = [2, 1, 3, 4][i]
            if port.device is None:
                vice_port_type = 0
            elif port.device.type == "joystick":
                vice_port_type = VICE_JOYSTICK
            elif port.device.type == "keyboard":
                vice_port_type = VICE_KEYSET_A + i
                # assert False
            else:
                vice_port_type = 0
            f.write("JoyDevice{0}={1}\n".format(vice_port, vice_port_type))

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
            (105, "Statusbar"),
            (112, "Pause"),
            (113, "Quit emulator"),
            (115, "Screenshot&Save PNG screenshot"),
            (119, "Speed settings&Warp mode"),
        ]
        if macosx:
            mod = 8
        else:
            mod = 2
        f.write("!CLEAR\n")
        for key, action in hotkeys:
            f.write("{0} {1}\n".format(SDLK_LAST * mod + key, action))


class ViceInputMapper(InputMapper):

    def axis(self, axis, positive):
        offset = 0 if positive else 1
        return "{0} 0 {1}".format(self.device.index, axis * 2 + offset)

    def hat(self, hat, direction):
        offset = {
            "left": 2,
            "right": 3,
            "up": 0,
            "down": 1,
        }[direction]
        return "{0} 2 {1}".format(self.device.index, hat * 4 + offset)

    def button(self, button):
        return "{0} 1 {1}".format(self.device.index, button)

    def key(self, key):
        return "{0}".format(key.sdl_code)
