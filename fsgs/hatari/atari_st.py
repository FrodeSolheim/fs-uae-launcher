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
Game Runner for Atari ST.

TODO:
- support saving disk changes
- support (persistent) save states
- check and/or fix support for vsync
- NTSC vs PAL?
- joystick support and keyboard joystick emulation
- mouse in port 0
- multiple floppies and floppy swapping

"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import io
import traceback
from fsgs.runner import GameRunner


ATARI_WIDTH = 832
#ATARI_HEIGHT = 576
ATARI_HEIGHT = 552

# TOS v1.02 (1987)(Atari Corp)(Mega ST)(GB)[MEGA TOS].img
# tos102uk.bin
TOS_102_UK = "87900a40a890fdf03bd08be6c60cc645855cbce5"

# TOS v1.04 (1989)(Atari Corp)(Mega ST)(GB)[Rainbow TOS].img
# tos104uk.bin
TOS_104_UK = "9526ef63b9cb1d2a7109e278547ae78a5c1db6c6"


#noinspection PyAttributeOutsideInit
class AtariSTRunner(GameRunner):

    def prepare(self):
        self.temp_dir = self.create_temp_dir("hatari")
        config_file = os.path.join(self.temp_dir.path, "hatari.cfg")
        with io.open(config_file, "w", encoding="UTF-8") as f:
            self.configure(f)
        self.add_arg("--configfile", config_file)
        self.add_arg("--statusbar", "0")
        self.add_arg("--drive-led", "0")

    def configure(self, f):
        #floppies_dir = os.path.join(self.context.temp.dir('uae'), 'Disks')
        floppies_dir = os.path.join(self.temp_dir.path, "Disks")
        os.makedirs(floppies_dir)
        original_floppies = self.prepare_floppies()
        floppies = []
        for p in original_floppies:
            dest_path = os.path.join(floppies_dir, os.path.basename(p))
            self.fsgs.file.copy_game_file(p, dest_path)
            floppies.append(dest_path)

        #self.changes = ChangeHandler(floppies_dir)
        #self.changes.init(os.path.join(self.context.game.state_dir, 'Disks'))

        num_floppy_drives = 2
        #sorted_floppies = self.sort_floppies(floppies)
        sorted_floppies = floppies
        inserted_floppies = sorted_floppies[:num_floppy_drives]

        f.write("[Floppy]\n")
        f.write("szDiskAFileName = {path}\n".format(
                path=inserted_floppies[0]))
        if len(inserted_floppies) > 1:
            f.write("szDiskBFileName = {path}\n".format(
                    path=inserted_floppies[1]))

        bios_path = self.prepare_tos()
        f.write("[ROM]\n")
        f.write("szTosImageFileName = {path}\n".format(path=bios_path))

        f.write("[System]\n")
        # don't patch Timer-D to reduce number of interrupts
        f.write("bPatchTimerD = FALSE\n")
        # f.write("bFastBoot = FALSE\n")

        f.write("[Sound]\n")
        if self.use_audio_frequency():
            f.write("nPlaybackFreq = {0}\n".format(self.use_audio_frequency()))

        if self.use_fullscreen():
            self.configure_fullscreen_scaling()

    def prepare_floppies(self):
        floppies = []
        #media_dir = os.path.dirname(self.context.game.file)
        #base_match = self.extract_match_name(os.path.basename(
        #        self.context.game.file))
        #for name in os.listdir(media_dir):
        #    dummy, ext = os.path.splitext(name)
        #    if ext.lower() not in ['.st']:
        #        continue
        #    match = self.extract_match_name(name)
        #    if base_match == match:
        #        floppies.append(os.path.join(media_dir, name))
        #        #floppies.append(name)
        if self.config["floppy_drive_0"]:
            floppies.append(self.config["floppy_drive_0"])
        return floppies

    def configure_fullscreen_scaling(self):
        sx, sy, sw, sh = 0, 0, ATARI_WIDTH, ATARI_HEIGHT
        try:
            viewport = self.config["viewport"]
            if viewport:
                sx, sy, sw, sh = viewport.rsplit("=", 1)[-1].strip().split(" ")
                sx, sy, sw, sh = int(sx), int(sy), int(sw), int(sh)
        except Exception:
            traceback.print_exc("Could not get viewport information")

        screen_w, screen_h = self.screen_size()
        print("viewport is", sx, sy, sw, sh)
        if self.use_stretching():
            target_w = screen_w
            target_h = screen_h
        else:
            scale = min(screen_w / sw, screen_h / sh)
            target_w = sw * scale
            target_h = sh * scale
        scale_x = target_w / sw
        scale_y = target_h / sh
        print("scale", scale_x, scale_y)
        orig_scale_x = min(screen_w / ATARI_WIDTH, screen_h / ATARI_HEIGHT)
        orig_scale_y = orig_scale_x
        print("org_scale = ", orig_scale_x, orig_scale_y)
        offset_x = -(sx + (sw / 2.0) - ATARI_WIDTH / 2.0) / \
                    (ATARI_WIDTH / 2.0)
        offset_y = -(sy + (sh / 2.0) - ATARI_HEIGHT / 2.0) / \
                    (ATARI_HEIGHT / 2.0)

        hz = scale_x / orig_scale_x
        vz = scale_y / orig_scale_y
        #hz = int(round(scale_x / orig_scale_x * 100000000))
        #vz = int(round(scale_y / orig_scale_y * 100000000))
        print("horizontal zoom:", hz / 100000000.0)
        print("vertical zoom:", vz / 100000000.0)
        #ho = int(round(offset_x * 100000000))
        #vo = int(round(offset_y * 100000000))
        #print("horizontal offset:", ho / 100000000.0);
        #print("vertical offset:", vo / 100000000.0);
        self.set_env("FILTER_VERT_OFFSET", str(offset_y))
        self.set_env("FILTER_HORIZ_OFFSET", str(offset_x))
        self.set_env("FILTER_VERT_ZOOM", str(vz))
        self.set_env("FILTER_HORIZ_ZOOM", str(hz))

    def atari_model(self):
        return "ST"

    def prepare_tos(self):
        if self.atari_model() == "ST":
            tos_sha1 = TOS_102_UK
        else:
            raise Exception("unknown Atari model")

        uri = self.fsgs.file.find_by_sha1(tos_sha1)
        stream = self.fsgs.file.open(uri)
        self.bios_temp = self.create_temp_file("tos.img")
        with open(self.bios_temp.path, "wb") as f:
            f.write(stream.read())
        return self.bios_temp.path

    def run(self):
        # return self.start_emulator("fs-hatari/hatari")
        return self.start_emulator_from_plugin_resource("hatari")

    def finish(self):
        pass
