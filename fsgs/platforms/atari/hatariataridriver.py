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
FSGS Game driver for Atari ST family.

TODO:

* Fullscreen stretching with SDL2 version.
* Multi-monitor awareness with SDL2 version?
* Support saving disk changes.
* Support (persistent) save states.
* Check and/or fix support for vsync.
* NTSC vs PAL?.
* Proper joystick support and keyboard joystick emulation.
* Mouse in port 0.
* Multiple floppies and floppy swapping.
* Screenshots are saved to the (temp) current working directory, not the
  global screenshots directory.

"""
import os
import traceback

from fsgs.drivers.gamedriver import GameDriver
from fsgs.knownfiles import KnownFile
from fsgs.option import Option
from fsgs.platforms import PLATFORM_ATARI

ATARI_MODEL_520ST = "520st"
ATARI_MODEL_1040ST = "1040st"
ATARI_WIDTH = 832
# ATARI_HEIGHT = 576
ATARI_HEIGHT = 552
# noinspection SpellCheckingInspection
ATARI_TOS_102_UK = KnownFile(
    "87900a40a890fdf03bd08be6c60cc645855cbce5", PLATFORM_ATARI,
    "TOS v1.02 (1987)(Atari Corp)(Mega ST)(GB)[MEGA TOS].img")
# noinspection SpellCheckingInspection
ATARI_TOS_104_UK = KnownFile(
    "9526ef63b9cb1d2a7109e278547ae78a5c1db6c6", PLATFORM_ATARI,
    "TOS v1.04 (1989)(Atari Corp)(Mega ST)(GB)[Rainbow TOS].img")
# noinspection SpellCheckingInspection
ATARI_TOS_1062_UK = KnownFile(
    "70db24a7c252392755849f78940a41bfaebace71", PLATFORM_ATARI,
    "TOS v1.62 (1990)(Atari)(GB)[STE TOS, Rev 2][STE].img")


class HatariAtariDriver(GameDriver):
    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator.name = "hatari-fs"
        self.floppies_dir = self.temp_dir("Media")
        self.tos_file = self.temp_file("tos.img")
        self.config_file = self.temp_file("hatari.cfg")
        self.helper = AtariHelper(self.config)
        self.floppies = []

    def prepare(self):
        super().prepare()
        self.prepare_tos()
        self.prepare_floppies()
        with open(self.config_file.path, "w", encoding="UTF-8") as f:
            self.write_config_file(f)
        self.emulator.args.extend(["--configfile", self.config_file.path])

    def install(self):
        super().install()

    def run(self):
        super().run()

    def finish(self):
        super().finish()

    def prepare_floppies(self):
        original_floppies = []
        if self.config["floppy_drive_0"]:
            original_floppies.append(self.config["floppy_drive_0"])
        floppies = []
        for p in original_floppies:
            dest_path = os.path.join(
                self.floppies_dir.path, os.path.basename(p))
            self.files.add(dest_path, source=p)
            floppies.append(dest_path)
        self.floppies = floppies

    def prepare_tos(self):
        tos_file = self.helper.tos_file()
        self.files.add(self.tos_file.path, sha1=tos_file.sha1,
                       description=tos_file.name)

    def write_config_file(self, f):
        f.write("[Screen]\n")
        # f.write("nMonitorType = 1\n")
        # f.write("nFrameSkips = 5\n")
        if self.use_fullscreen():
            f.write("bFullScreen = TRUE\n")
        else:
            f.write("bFullScreen = FALSE\n")
        # f.write("bKeepResolution = TRUE\n")
        f.write("bAllowOverscan = FALSE\n")
        # f.write("nSpec512Threshold = 1\n")
        # f.write("nForceBpp = 0\n")
        # f.write("bAspectCorrect = TRUE\n")
        # f.write("bAspectCorrect = FALSE\n")
        # f.write("bUseExtVdiResolutions = FALSE\n")
        # f.write("nVdiWidth = 640\n")
        # f.write("nVdiHeight = 480\n")
        # f.write("nVdiColors = 2\n")
        # f.write("bMouseWarp = TRUE\n")
        f.write("bShowStatusbar = FALSE\n")
        f.write("bShowDriveLed = FALSE\n")
        # f.write("bCrop = FALSE\n")
        # f.write("bForceMax = FALSE\n")
        # f.write("nMaxWidth = 832\n")
        # f.write("nMaxHeight = 588\n")
        f.write("nRenderScaleQuality = 1\n")
        f.write("bUseVsync = 0\n")

        f.write("[Sound]\n")
        if self.use_audio_frequency():
            f.write("nPlaybackFreq = {0}\n".format(self.use_audio_frequency()))

        f.write("[Floppy]\n")
        num_floppy_drives = 2
        inserted_floppies = self.floppies[:num_floppy_drives]
        if len(inserted_floppies) > 0:
            f.write("szDiskAFileName = {path}\n".format(
                path=inserted_floppies[0]))
        if len(inserted_floppies) > 1:
            f.write("szDiskBFileName = {path}\n".format(
                path=inserted_floppies[1]))

        f.write("[ROM]\n")
        f.write("szTosImageFileName = {}\n".format(self.tos_file.path))
        f.write("bPatchTOS = FALSE\n")

        f.write("[System]\n")
        if self.helper.model_family() == "ST":
            f.write("nModelType = 0\n")
        elif self.helper.model_family() == "STE":
            f.write("nModelType = 2\n")
        else:
            print("WARNING: UNKNOWN ST MODEL FAMILY")
        accuracy = self.helper.accuracy()
        if accuracy == 1:
            f.write("bCycleExactCpu = TRUE\n")
            f.write("bCompatibleCpu = TRUE\n")
            f.write("bPatchTimerD = FALSE\n")
        elif accuracy == 0:
            f.write("bCycleExactCpu = FALSE\n")
            f.write("bCompatibleCpu = TRUE\n")
            f.write("bPatchTimerD = TRUE\n")
        else:
            f.write("bCycleExactCpu = FALSE\n")
            f.write("bCompatibleCpu = FALSE\n")
            f.write("bPatchTimerD = TRUE\n")
        f.write("bFastBoot = FALSE\n")
        f.write("bBlitter = FALSE\n")

        if self.use_stretching():
            self.env["FSGS_STRETCH"] = "1"
        else:
            self.env["FSGS_STRETCH"] = "0"

        f.write("[Memory]\n")
        memory = self.helper.memory()
        if memory == 1024:
            f.write("nMemorySize = 1\n")
        elif memory == 512:
            f.write("nMemorySize = 0\n")
        else:
            print("WARNING: UNKNOWN ST MEMORY SIZE")

    def configure_fullscreen_scaling(self):
        """Configure scaling for the SDL 1.x version of Hatari-FS.

        Not (currently) used with the SDL 2.x version of Hatari-FS.
        """
        sx, sy, sw, sh = 0, 0, ATARI_WIDTH, ATARI_HEIGHT
        try:
            viewport = self.config["viewport"]
            if viewport:
                sx, sy, sw, sh = viewport.rsplit(
                    "=", 1)[-1].strip().split(" ")
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
        offset_x = \
            -(sx + (sw / 2.0) - ATARI_WIDTH / 2.0) / (ATARI_WIDTH / 2.0)
        offset_y = \
            -(sy + (sh / 2.0) - ATARI_HEIGHT / 2.0) / (ATARI_HEIGHT / 2.0)
        hz = scale_x / orig_scale_x
        vz = scale_y / orig_scale_y
        print("horizontal zoom:", hz / 100000000.0)
        print("vertical zoom:", vz / 100000000.0)
        self.env["FILTER_VERT_OFFSET"] = str(offset_y)
        self.env["FILTER_HORIZ_OFFSET"] = str(offset_x)
        self.env["FILTER_VERT_ZOOM"] = str(vz)
        self.env["FILTER_HORIZ_ZOOM"] = str(hz)


class AtariHelper:
    def __init__(self, config):
        self.config = config

    def accuracy(self):
        try:
            accuracy = int(self.config.get(Option.ACCURACY, "1"))
        except ValueError:
            accuracy = 1
        return accuracy

    def model(self):
        model = self.config.get(Option.ATARI_MODEL)
        if not model:
            model = ATARI_MODEL_520ST
        return model

    def model_family(self):
        model = self.config.get(Option.ATARI_MODEL, "").upper()
        if model.endswith("ST"):
            return "ST"
        elif model.endswith("STE"):
            return "STE"
        return ""

    def tos_file(self):
        model = self.model().upper()
        if "STE" in model:
            return ATARI_TOS_1062_UK
        else:
            return ATARI_TOS_102_UK

    def memory(self):
        model = self.model().upper()
        if model.startswith("1040"):
            return 1024
        else:
            return 512
