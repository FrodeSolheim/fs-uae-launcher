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
FSGS Game Driver for Atari ST (Atari).

TODO:

* Support saving disk changes.
* Support (persistent) save states.
* Check and/or fix support for vsync.
* NTSC vs PAL?.
* Joystick support and keyboard joystick emulation.
* Mouse in port 0.
* Multiple floppies and floppy swapping.
* Screenshots are saved to the (temp) current working directory, not the
  global screenshots directory.

"""
import os
import traceback

from fsgs.runner import GameRunner

ATARI_WIDTH = 832
ATARI_HEIGHT = 552  # ATARI_HEIGHT = 576

# TOS v1.02 (1987)(Atari Corp)(Mega ST)(GB)[MEGA TOS].img, tos102uk.bin
# noinspection SpellCheckingInspection
TOS_102_UK = "87900a40a890fdf03bd08be6c60cc645855cbce5"

# TOS v1.04 (1989)(Atari Corp)(Mega ST)(GB)[Rainbow TOS].img, tos104uk.bin
# noinspection SpellCheckingInspection
TOS_104_UK = "9526ef63b9cb1d2a7109e278547ae78a5c1db6c6"

# TOS v1.62 (1990)(Atari)(GB)[STE TOS, Rev 2][STE].img
# noinspection SpellCheckingInspection
TOS_106_2_UK = "70db24a7c252392755849f78940a41bfaebace71"


class AtariDriver(GameRunner):

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator = "hatari-fs"

    def prepare(self):
        floppies_dir = self.temp_dir("Disks").path
        original_floppies = self.prepare_floppies()
        floppies = []
        for p in original_floppies:
            dest_path = os.path.join(floppies_dir, os.path.basename(p))
            self.fsgs.file.copy_game_file(p, dest_path)
            floppies.append(dest_path)
        sorted_floppies = floppies

        config_file = self.temp_file("hatari.cfg").path
        with open(config_file, "w", encoding="UTF-8") as f:
            self.configure(f, sorted_floppies)
        self.args.extend(["--configfile", config_file])
        # noinspection SpellCheckingInspection
        self.args.extend(["--statusbar", "0"])
        self.args.extend(["--drive-led", "0"])

    def prepare_floppies(self):
        floppies = []
        if self.config["floppy_drive_0"]:
            floppies.append(self.config["floppy_drive_0"])
        return floppies

    def configure(self, f, sorted_floppies):
        num_floppy_drives = 2
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
        f.write("bPatchTOS = FALSE\n")

        f.write("[System]\n")
        # don't patch Timer-D to reduce number of interrupts
        f.write("bPatchTimerD = FALSE\n")
        f.write("bFastBoot = FALSE\n")
        f.write("bBlitter = FALSE\n")

        f.write("[Sound]\n")
        if self.use_audio_frequency():
            f.write("nPlaybackFreq = {0}\n".format(self.use_audio_frequency()))

        if self.use_fullscreen():
            self.configure_fullscreen_scaling()

        model = self.atari_model()

        f.write("[Memory]\n")
        if model.startswith("1040"):
            f.write("nMemorySize = 1\n")
        else:
            f.write("nMemorySize = 0\n")

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
        print("horizontal zoom:", hz / 100000000.0)
        print("vertical zoom:", vz / 100000000.0)
        self.env["FILTER_VERT_OFFSET"] = str(offset_y)
        self.env["FILTER_HORIZ_OFFSET"] = str(offset_x)
        self.env["FILTER_VERT_ZOOM"] = str(vz)
        self.env["FILTER_HORIZ_ZOOM"] = str(hz)

    def atari_model(self):
        # FIXME: 520ST - or perhaps 520STF(M) -512 KB RAM
        # FIXME: 1040ST - 1MB - 1040STF(M)
        # FIXME: 520STE
        # FIXME: 1040STE
        return "520ST"

    def prepare_tos(self):
        model = self.atari_model()
        if "STE" in model:
            tos_sha1 = TOS_106_2_UK
        else:
            tos_sha1 = TOS_102_UK

        uri = self.fsgs.file.find_by_sha1(tos_sha1)
        stream = self.fsgs.file.open(uri)
        bios_temp = self.temp_file("tos.img")
        with open(bios_temp.path, "wb") as f:
            f.write(stream.read())
        return bios_temp.path
