# FSGS - Common functionality for Fengestad Game System.
# Copyright (C) 2013  Frode Solheim <frode-code@fengestad.no>
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
Game Runner for Commodore 64.
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import io
from fsgs.runner import GameRunner
from fsgs.input.mapper import InputMapper


VIDEO_WIDTH = 384
VIDEO_HEIGHT = 272


#noinspection PyAttributeOutsideInit
class Commodore64Runner(GameRunner):

    def prepare(self):
        self.temp_dir = self.create_temp_dir("vice")
        config_file = os.path.join(self.temp_dir.path, "vice.cfg")
        with io.open(config_file, "w", encoding="UTF-8") as f:
            self.vice_configure(f)
            #self.configure_input(f)
        self.add_arg("-config", config_file)

    def run(self):
        # return self.start_emulator("fs-vice/x64sc")
        return self.start_emulator_from_plugin_resource("x64sc")

    def finish(self):
        pass

    def vice_configure(self, f):
        f.write("[C64SC]\n")
        f.write("ConfirmOnExit=0\n")
        #f.write("KeepAspectRatio=1\n")
        f.write("VICIIHwScale=1\n")
        f.write("HwScalePossible=1\n")
        f.write("VICIIDoubleScan=1\n")
        f.write("VICIISDLFullscreenMode=1\n")
        f.write("AutostartWarp=0\n")
        f.write("Drive8Type=1541\n")
        f.write("VICIIFilter=0\n")
        f.write("\n")

        screen_w, screen_h = self.screen_size()
        f.write("SDLCustomWidth={w}\n".format(w=screen_w))
        f.write("SDLCustomHeight={h}\n".format(h=screen_h))

        original_aspect = VIDEO_WIDTH / VIDEO_HEIGHT
        #original_aspect = 4 / 3
        #original_aspect = 320 / 272
        #original_aspect = 384 / 272
        #original_aspect = 1.0

        if self.use_fullscreen():
            f.write("VICIIFullscreen=1\n")

            if self.use_stretching():
                screen_aspect = screen_w / screen_h
                custom_aspect = screen_aspect / original_aspect
                print("custom aspect is", custom_aspect)
                f.write("AspectRatio={0}\n".format(custom_aspect))
                f.write("SDLGLAspectMode=1\n")

            #f.write("FullscreenEnabled=1\n")
            #if fs.linux:
            #    self.args.append("-VICIIhwscale")
            #    hwscoords = self.set_hwscale_coords()
            #else:
            #    pass
            #    #if self.options["zoom"]:
            #    #    logger.warning("zoom is not supported on this platform")
            #    #if self.options["stretch"]:
            #    #    logger.warning("stretch is not supported on this platform")
            #    #if self.options["border"]:
            #    #    logger.warning("border is not supported on this platform")
            #if fs.macosx:
            #    #logger.warning("Fullscreen not supported on Mac OS X")
            #    pass
            #else:
            #self.add_arg("-fullscreen")

        if self.use_audio_frequency():
            f.write("SoundSampleRate={0}\n".format(self.use_audio_frequency()))
        # default buffer size for vice is 100ms, that's far too much...
        # f.write("SoundBufferSize={0}\n".format(20))

        #print("set_media_options")
        #media_list = self.create_media_list()
        #print("sort media list")
        ## FIXME: SORT ON name (lowercase) ONLY, not whole path, because
        ## some files may have moved to another dir (temp dir)
        #media_list = sorted(media_list)
        #print(media_list)
        #if media_list[0].lower()[-4:] == ".crt":
        #    f.write("CartridgeFile=\"{path}\"\n".format(path=media_list[0]))
        #    f.write("CartridgeType={type}\n".format(type=0))
        #    f.write("CartridgeMode={mode}\n".format(mode=0))
        #    f.write("CartridgeReset={reset}\n".format(reset=1))
        ##    #self.args.extend(["-autostart", media_list[0]])
        #else:
        #    #f.write('AutostartPrgMode=2\n') # disk image
        #    #f.write('AutostartPrgDiskImage="{path}"\n'.format(
        #    #        path=media_list[0]))
        #    self.add_arg("-autostart", media_list[0])

        self.media_dir = self.create_temp_dir("vice-media")

        file_uri = self.config["tape_drive"]
        input_stream = self.fsgs.file.open(file_uri)
        tape_file = os.path.join(self.media_dir.path, file_uri.split("/")[-1])
        with open(tape_file, "wb") as tape_f:
            tape_f.write(input_stream.read())
        self.add_arg("-autostart", tape_file)

        ## FIXME: Floppies?
        #print(media_list)
        #if media_list[0].lower()[-4:] == ".d64":
        #    f = self.context.temp.file('fliplist')
        #    f.write("# Vice fliplist file\n\n")
        #    f.write("UNIT 8\n")
        #    print("FLIP LIST:")
        #    # Make sure first disk is added to the end of the fliplist
        #    for floppy in (media_list[1:] + [media_list[:1]]):
        #        print("%s\n" % (floppy,))
        #        print
        #        f.write("%s\n" % (floppy,))
        #    f.close()
        #    self.add_arg("-flipname", self.context.temp.file("fliplist"))
        #
        #media_dir = os.path.dirname(media_list[0])
        #print(media_dir)
        #f.write("InitialDefaultDir=\"{dir}\"\n".format(dir=media_dir))
        #f.write("InitialTapeDir=\"{dir}\"\n".format(dir=media_dir))
        #f.write("InitialCartDir=\"{dir}\"\n".format(dir=media_dir))
        #f.write("InitialDiskDir=\"{dir}\"\n".format(dir=media_dir))
        #f.write("InitialAutostartDir=\"{dir}\"".format(dir=media_dir))

    #def vice_prepare_floppies(self):
    #    floppies = []
    #    #media_dir = os.path.dirname(self.context.game.file)
    #    #base_match = self.extract_match_name(os.path.basename(
    #    #        self.context.game.file))
    #    #for name in os.listdir(media_dir):
    #    #    dummy, ext = os.path.splitext(name)
    #    #    if ext.lower() not in ['.st']:
    #    #        continue
    #    #    match = self.extract_match_name(name)
    #    #    if base_match == match:
    #    #        floppies.append(os.path.join(media_dir, name))
    #    #        #floppies.append(name)
    #    if self.config["floppy_drive_0"]:
    #        floppies.append(self.config["floppy_drive_0"])
    #    return floppies


class ViceInputMapper(InputMapper):

    def axis(self, axis, positive):
        axis_start = self.device.buttons
        offset = 1 if positive else 0
        return "input.1.joystick.{0}.button.{1}".format(
            self.device.index, axis_start + axis * 2 + offset)

    def hat(self, hat, direction):
        hat_start = self.device.buttons + self.device.axes * 2
        offset = {
            "left": 0,
            "right": 1,
            "up": 2,
            "down": 3,
        }[direction]
        return "input.1.joystick.{0}.button.{1}".format(
            self.device.index, hat_start + hat * 4 + offset)

    def button(self, button):
        return "input.1.joystick.{0}.button.{1}".format(
            self.device.index, button)

    def key(self, key):
        return "input.1.keyboard.0.button.{0}.{1}".format(
            key.dinput_code, key.dinput_name[4:])
