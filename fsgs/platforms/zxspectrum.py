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

import json
import os

from fsbc import settings
from fsgs.drivers.gamedriver import GameDriver
from fsgs.drivers.messdriver import MessDriver
from fsgs.options.option import Option
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader

# from fsgs.platforms.zxs.fusespectrumdriver import FuseSpectrumDriver
# from fsgs.platforms.zxs.messspectrumdriver import MessSpectrumDriver
# from fsgs.platforms.zxs.spectrumplatform import SpectrumLoader
from fsgs.spectrum import (
    ZXS_48_ROM,
    ZXS_128_0_ROM,
    ZXS_128_1_ROM,
    ZXS_PLUS2_0_ROM,
    ZXS_PLUS2_1_ROM,
    ZXS_PLUS2A_0_ROM,
    ZXS_PLUS2A_1_ROM,
    ZXS_PLUS2A_2_ROM,
    ZXS_PLUS2A_3_ROM,
    ZXS_PLUS3_0_ROM,
    ZXS_PLUS3_1_ROM,
    ZXS_PLUS3_2_ROM,
    ZXS_PLUS3_3_ROM,
)

# ZXS_MODEL_48K = "spectrum"
# ZXS_MODEL_48K_IF2 = "spectrum/if2"
# ZXS_MODEL_128 = "spectrum128"
# ZXS_MODEL_PLUS2 = "spectrum+2"
# ZXS_MODEL_PLUS2A = "spectrum+2a"
# ZXS_MODEL_PLUS3 = "spectrum+3"

ZXS_MODEL_48K = "48k"
# ZXS_MODEL_48K_IF2 = "spectrum/if2"
ZXS_MODEL_128 = "128"
ZXS_MODEL_PLUS2 = "+2"
ZXS_MODEL_PLUS2A = "+2a"
ZXS_MODEL_PLUS3 = "+3"

MESS_SPECTRUM = "spectrum"  # ZX Spectrum
MESS_SPEC128 = "spec128"  # ZX Spectrum 128
MESS_SPECPLS2 = "specpls2"  # ZX Spectrum +2
MESS_SPECPL2A = "specpl2a"  # ZX Spectrum +2a
MESS_SPECPLS3 = "specpls3"  # ZX Spectrum +3


# MESS_sp3e8bit = "sp3e8bit"  # ZX Spectrum +3e 8bit IDE
# noinspection SpellCheckingInspection
# MESS_sp3eata = "sp3eata"  # ZX Spectrum +3e 8bit ZXATASP
# noinspection SpellCheckingInspection
# MESS_sp3ezcf = "sp3ezcf"  # ZX Spectrum +3e 8bit ZXCF
# MESS_spec80k = "spec80k"  # ZX Spectrum 80K
# MESS_specide = "specide"  # ZX Spectrum IDE
# MESS_specpl3e = "specpl3e"  # ZX Spectrum +3e

# from fsgs.spectrum import ZXS_48_ROM, ZXS_128_0_ROM, ZXS_128_1_ROM, \
#     ZXS_PLUS3_0_ROM, ZXS_PLUS3_1_ROM, ZXS_PLUS3_2_ROM, ZXS_PLUS3_3_ROM

# ZXS_MODEL_48K = "spectrum"

# ZXS_MODEL_128 = "spectrum128"
# ZXS_MODEL_PLUS3 = "spectrum+3"


def log_heading(heading):
    print("")
    print("=" * 79)
    # print("=" * 79)
    print(heading.upper())
    # print("-" * 79)


class SpectrumPlatform(Platform):
    PLATFORM_NAME = "ZX Spectrum"

    @staticmethod
    def driver(fsgc):
        driver = settings.get(Option.ZXS_EMULATOR)
        if not driver:
            driver = "fuse-fs"

        if driver == "fuse":
            return FuseSpectrumDriver(fsgc)
        elif driver == "fuse-fs":
            return FuseFsSpectrumDriver(fsgc)
        if driver == "mame":
            return MessSpectrumDriver(fsgc)
        elif driver == "mame-fs":
            return MessFsSpectrumDriver(fsgc)

    @staticmethod
    def loader(fsgc):
        return SpectrumLoader(fsgc)


class SpectrumLoader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        if len(file_list) == 0:
            self.config["x_variant_error"] = "Variant has empty file list"
        elif len(file_list) > 1:
            self.config["x_variant_error"] = "Unsupported multi-file variant"

        name = file_list[0]["name"]
        sha1 = file_list[0]["sha1"]
        _, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext in [".z80"]:
            key = Option.SNAPSHOT_FILE
        elif ext in [".tap", ".tzx"]:
            key = Option.TAPE_DRIVE_0
        elif ext in [".dsk", ".trd"]:
            key = Option.FLOPPY_DRIVE_0
        elif ext in [".rom"]:
            key = Option.CARTRIDGE_SLOT
        else:
            return
        self.config[key] = "sha1://{0}/{1}".format(sha1, name)

    def load_extra(self, values):
        print(values)

        model = values["zxs_model"]

        # FIXME: Remove legacy option
        if not model:
            model = values["model"]
        self.config["model"] = ""

        if not model:
            model = ZXS_MODEL_48K
        # # Aliases
        # elif model == "128":
        #     model = ZXS_MODEL_128
        # elif model == "+2":
        #     model = ZXS_MODEL_PLUS2
        # elif model == "+2A" or model == "+2a":
        #     model = ZXS_MODEL_PLUS2A
        # elif model == "+3":
        #     model = ZXS_MODEL_PLUS3
        # else:
        #     model = ZXS_MODEL_48K

        self.config[Option.ZXS_MODEL] = model


ZXS_KEMPSTON_JOYSTICK_TYPE = "kempston"
ZXS_KEMPSTON_JOYSTICK = {
    "type": ZXS_KEMPSTON_JOYSTICK_TYPE,
    "description": "Kempston Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
ZXS_SINCLAIR_JOYSTICK_TYPE = "sinclair"
ZXS_SINCLAIR_JOYSTICK = {
    "type": ZXS_SINCLAIR_JOYSTICK_TYPE,
    "description": "Sinclair Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
ZXS_CURSOR_JOYSTICK_TYPE = "cursor"
ZXS_CURSOR_JOYSTICK = {
    "type": ZXS_CURSOR_JOYSTICK_TYPE,
    "description": "Sinclair Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
ZXS_PORTS = [
    {
        "description": "Joystick Port 1",
        "types": [
            NO_CONTROLLER,
            ZXS_KEMPSTON_JOYSTICK,
            ZXS_SINCLAIR_JOYSTICK,
            ZXS_CURSOR_JOYSTICK,
        ],
        "type_option": "zxs_port_1_type",
        "device_option": "zxs_port_1",
    },
    {
        "description": "Joystick Port 2",
        "types": [NO_CONTROLLER, ZXS_SINCLAIR_JOYSTICK],
        "type_option": "zxs_port_2_type",
        "device_option": "zxs_port_2",
    },
]


class FuseSpectrumDriver(GameDriver):
    PORTS = ZXS_PORTS

    def __init__(self, fsgs, fsemu=False):
        super().__init__(fsgs)
        if fsemu:
            self.emulator.name = "fuse-fs"
        else:
            self.emulator.name = "fuse"
        self.helper = SpectrumHelper(self.options)
        # self.emulator.allow_system_emulator = True
        self.media_dir = self.temp_dir("Media")
        self.roms_dir = self.temp_dir("ROMs")
        self.tos_file = self.temp_file("tos.img")
        # self.options_file = self.temp_file("hatari.cfg")
        # self.floppies = []
        self.fuse_options = {}

        # FIXME Fuse has been fixed to allow for stable frame rate, except
        # when doing turbo load, so allowing G-SYNC will slow down loading
        # a bit.
        # self.set_allow_gsync(False)

    def prepare(self):
        super().prepare()

        # if self.options.get(Option.FLOPPY_DRIVE_0):
        #     source = self.options.get(Option.FLOPPY_DRIVE_0)
        #     name = os.path.basename(source)
        #     path = os.path.join(self.media_dir.path, name)
        #     self.files.add(path, source=source)
        #     # +3 Drive A Defaults to a single - sided 40 track drive.
        #     # self.emulator.args.extend(["--plus3disk", path])
        #     # self.emulator.args.extend(["--drive-plus3b-type", "Disabled"])
        #     self.emulator.args.extend([path])
        #     self.emulator.args.extend(["--no-auto-load"])
        #     return

        model = self.helper.model()
        if model == ZXS_MODEL_48K:  # or model == ZXS_MODEL_48K_IF2:
            self.emulator.args.extend(["--machine", "48"])
            self.set_model_name("ZX Spectrum 48K")
        # elif self.helper.model() == ZXS_MODEL_48K_IF2:
        #     self.emulator.args.extend(["--machine", "48"])
        #     self.set_model_name("ZX Spectrum 48K")
        elif model == ZXS_MODEL_128:
            self.emulator.args.extend(["--machine", "128"])
            self.set_model_name("ZX Spectrum 128")
        elif model == ZXS_MODEL_PLUS2:
            self.emulator.args.extend(["--machine", "plus2"])
            self.set_model_name("ZX Spectrum +2")
        elif model == ZXS_MODEL_PLUS2A:
            self.emulator.args.extend(["--machine", "plus2a"])
            self.set_model_name("ZX Spectrum +2A")
        elif model == ZXS_MODEL_PLUS3:
            self.emulator.args.extend(["--machine", "plus3"])
            self.set_model_name("ZX Spectrum +3")
        else:
            raise Exception("Unrecognized ZX Spectrum model")

        if self.options.get(Option.SNAPSHOT_FILE):
            source = self.options.get(Option.SNAPSHOT_FILE)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            self.emulator.args.extend(["--snapshot", path])

        # If this option is enabled, then Fuse will attempt to accelerate
        # tape loaders by "short circuiting" the loading loop. This will
        # in general speed up loading, but may cause some loaders to fail.
        # FS: The speed improvement seems minor, so disable it always.
        # self.emulator.args.extend(["--no-accelerate-loader"])

        self.configure_audio()
        self.configure_input()
        self.configure_media()
        self.configure_video()

        # self.emulator.args.extend(["--printer"])
        self.emulator.args.extend(["--no-printer"])
        # self.fuse_options["zxprinter"] = 0
        self.emulator.args.extend(["--no-zxprinter"])

        # ROMs are now bundled with Fuse-FS. Also, it appears Fuse
        # misbehaves when explicitly specifying (at least) the 48 rom.
        # def install_rom(name, rom):
        #     path = os.path.join(self.roms_dir.path, name + ".rom")
        #     self.files.add(path, sha1=rom.sha1, description=name + ".rom")
        #     self.emulator.args.extend(["--rom-{}".format(name), path])
        # if self.helper.model() == ZXS_MODEL_48K:
        #     install_rom("48", ZXS_48_ROM)
        # elif self.helper.model() == ZXS_MODEL_128:
        #     install_rom("128-0", ZXS_128_0_ROM)
        #     install_rom("128-1", ZXS_128_1_ROM)
        # elif self.helper.model() == ZXS_MODEL_PLUS3:
        #     install_rom("plus3-0", ZXS_PLUS3_0_ROM)
        #     install_rom("plus3-1", ZXS_PLUS3_1_ROM)
        #     install_rom("plus3-2", ZXS_PLUS3_2_ROM)
        #     install_rom("plus3-3", ZXS_PLUS3_3_ROM)

        fuse_rc_path = os.path.join(self.home.path, ".fuserc")
        with open(fuse_rc_path, "w") as f:
            f.write('<?xml version="1.0"?>\n')
            f.write("<settings>\n")
            for key, value in self.fuse_options.items():
                f.write("  <{0}>{1}</{0}>\n".format(key, value))
            f.write("</settings>\n")

        log_heading("Fuse config file")
        with open(fuse_rc_path, "r") as f:
            print(f.read())

    def configure_audio(self):
        log_heading("Configure audio")
        args = []
        args.append("--loading-sound")
        # args.append("--no-loading-sound")
        print(args)
        self.emulator.args.extend(args)

    def configure_input(self):
        log_heading("Configure input")

        kempston = False
        sinclair = False
        # joystick1output 0 # none
        # joystick1output 1 # cursor
        # joystick1output 2 # kempston
        # joystick1output 3 # sinclair 1
        # joystick1output 4 # sinclair 2
        joystickoutput = [0, 0]

        for i, port in enumerate(self.ports):
            if port.type == ZXS_KEMPSTON_JOYSTICK_TYPE:
                kempston = True
            if port.type == ZXS_SINCLAIR_JOYSTICK_TYPE:
                sinclair = True

            print("port", i, port.type, port)
            print("device", port.device)
            if port.device:
                print(port.device.index)
                if port.device.index >= 2:
                    raise Exception(
                        "Fuse-FS currently only works with the first two "
                        "connected joysticks :(. This will be fixed later."
                    )
                if port.type == ZXS_CURSOR_JOYSTICK_TYPE:
                    joystickoutput[port.device.index] = 1
                if port.type == ZXS_KEMPSTON_JOYSTICK_TYPE:
                    kempston = True
                    joystickoutput[port.device.index] = 2
                if port.type == ZXS_SINCLAIR_JOYSTICK_TYPE:
                    sinclair = True
                    joystickoutput[port.device.index] = 3 if i == 0 else 4

        self.emulator.args.extend(
            ["--joystick-1-output", str(joystickoutput[0])]
        )
        self.emulator.args.extend(
            ["--joystick-2-output", str(joystickoutput[1])]
        )

        # self.fuse_options["joystick1output"] = joystickoutput[0]
        # self.fuse_options["joystick2output"] = joystickoutput[1]

        # FIXME: interface 2 is probably also needed when using cartridges
        # FIXME: THis option might be only relevant for cartridge?
        if sinclair:
            self.emulator.args.extend(["--interface2"])
        else:
            self.emulator.args.extend(["--no-interface2"])

        if kempston:
            self.emulator.args.extend(["--kempston"])
        else:
            self.emulator.args.extend(["--no-kempston"])

        # if self.helper.has_interface_2():
        #     self.emulator.args.extend(["--interface2"])
        # else:
        #     self.emulator.args.extend(["--no-interface2"])

        # self.emulator.args.extend(["--kempston-mouse"])
        self.emulator.args.extend(["--no-kempston-mouse"])

    def configure_media(self):
        log_heading("Configure_media")

        if self.options.get(Option.TAPE_DRIVE_0):
            source = self.options.get(Option.TAPE_DRIVE_0)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            self.emulator.args.extend(["--tape", path])

        if self.options.get(Option.FLOPPY_DRIVE_0):
            source = self.options.get(Option.FLOPPY_DRIVE_0)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # +3 Drive A Defaults to a single - sided 40 track drive.
            self.emulator.args.extend(["--plus3disk", path])
            self.emulator.args.extend(["--drive-plus3b-type", "Disabled"])

        if self.options.get(Option.CARTRIDGE_SLOT):
            source = self.options.get(Option.CARTRIDGE_SLOT)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            self.emulator.args.extend(["--if2cart", path])

        # The multi-load aspect of SLT files requires a trap instruction
        # to be supported. Always disable in case normal programs use it.
        self.emulator.args.extend(["--no-slt"])

        # if self.helper.accuracy() == 1:
        #     traps = False
        # else:
        #     traps = True
        # if traps:
        #     self.emulator.args.extend(["--traps"])
        # else:
        #     self.emulator.args.extend(["--no-traps"])

        if self.use_auto_load():
            self.emulator.args.extend(["--auto-load"])
            # Detect when tape is accessed and automatically start/stop tape.
            self.emulator.args.extend(["--detect-loader"])
        else:
            self.emulator.args.extend(["--no-auto-load"])
            self.emulator.args.extend(["--no-detect-loader"])

        if self.use_turbo_load():
            self.emulator.args.extend(["--accelerate-loader"])
            self.emulator.args.extend(["--fastload"])
            self.emulator.args.extend(["--traps"])
        else:
            self.emulator.args.extend(["--no-accelerate-loader"])
            self.emulator.args.extend(["--no-fastload"])
            self.emulator.args.extend(["--no-traps"])

    def configure_video(self):
        log_heading("Configure video")

        if self.use_fullscreen():
            self.emulator.args.extend(["--full-screen"])
        if self.effect() == self.CRT_EFFECT:
            graphics_filter = "paltv2x"
        elif self.effect() == self.SCALE2X_EFFECT:
            graphics_filter = "advmame2x"
        elif self.effect() == self.HQ2X_EFFECT:
            graphics_filter = "hq2x"
        else:
            graphics_filter = "2x"
        self.emulator.args.extend(["--graphics-filter", graphics_filter])

    def install(self):
        super().install()

    def run(self):
        super().run()

    def finish(self):
        super().finish()

    def get_game_refresh_rate(self):
        return self.helper.refresh_rate()


class FuseFsSpectrumDriver(FuseSpectrumDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class MessSpectrumDriver(MessDriver):
    JOYSTICK = {
        "type": "joystick",
        "description": "Joystick",
        "mapping_name": "zx-spectrum-joystick",
    }

    PORTS = [{"description": "Joystick Port", "types": [JOYSTICK]}]

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc)
        self.helper = SpectrumHelper(self.options)

    def mess_configure(self):
        # FIXME: hack
        # self.mess_configure_floppies(["cassette"])
        # self.emulator.args.extend(["-ui_active"])

        if self.config[Option.SNAPSHOT_FILE]:
            # snapshot loads automatically, no need to do anything special
            self.add_arg(
                "-{0}".format("snapshot"),
                self.get_game_file(Option.SNAPSHOT_FILE),
            )
        elif self.config[Option.FLOPPY_DRIVE_0]:
            # pressing enter to select "loader" in the menu
            self.inject_fake_input_string(160, "{0}\n".format(""))
            self.add_arg(
                "-{0}".format("floppydisk1"),
                self.get_game_file(Option.FLOPPY_DRIVE_0),
            )

        elif self.config[Option.TAPE_DRIVE_0]:
            self.emulator.args.extend(
                ["-cassette", self.get_game_file(Option.TAPE_DRIVE_0)]
            )
            if self.config[Option.ZXS_MODEL] == "spectrum128":
                self.inject_fake_input_string_list(
                    160,
                    [
                        "1040",
                        "0040",
                        "0000",  # Return
                        "0000",
                        "0000",
                        "0000",
                        "1059",
                        "0059",
                        "0000",  # F2 (Load tape)
                    ],
                )
            else:
                self.inject_fake_input_string_list(
                    160,
                    [
                        # Inject LOAD ""
                        "1013",
                        "0013",
                        "0000",  # J (LOAD)
                        "1229",
                        "0000",  # Right Shift (press)
                        "1019",
                        "0019",
                        "0000",  # P (with symbol shift = ")
                        "0229",
                        "0000",  # Right shift (release)
                        "1229",
                        "0000",  # Right shift (press)
                        "1019",
                        "0019",
                        "0000",  # P (with symbol shift = ")
                        "0299",
                        "0000",  # Right shift (release)
                        "1040",
                        "0040",
                        "0000",  # Return
                        # "0000", "0000", "0000",
                        # "1071", "0071", "0000",  # Scroll Lock
                        "0000",
                        "0000",
                        "0000",
                        "1059",
                        "0059",
                        "0000",  # F2 (Load tape)
                    ],
                )
            # self.args.extend(
            #     ["-autoboot_command", 'j" "\\n'])

    def mess_full_keyboard(self):
        return False

    def mess_input_mapping(self, port):
        return {
            "UP": 'tag=":KEMPSTON" type="KEYBOARD" mask="8" defvalue="0"',
            "DOWN": 'tag=":KEMPSTON" type="KEYBOARD" mask="4" defvalue="0"',
            "LEFT": 'tag=":KEMPSTON" type="KEYBOARD" mask="2" defvalue="0"',
            "RIGHT": 'tag=":KEMPSTON" type="KEYBOARD" mask="1" defvalue="0"',
            "1": 'tag=":KEMPSTON" type="KEYBOARD" mask="16" defvalue="0"',
        }

    def get_game_refresh_rate(self):
        # Refresh rate values retrieved from MESS
        if self.config[Option.ZXS_MODEL] == "spectrum128":
            return 50.021084
        else:
            return 50.080128

    def mame_romset(self):
        model = self.helper.model()
        if model == ZXS_MODEL_48K:
            return MESS_SPECTRUM, MESS_SPECTRUM_ROMS
        elif model == ZXS_MODEL_128:
            return MESS_SPEC128, MESS_SPEC128_ROMS
        elif model == ZXS_MODEL_PLUS2:
            return MESS_SPECPLS2, MESS_SPECPLS2_ROMS
        elif model == ZXS_MODEL_PLUS2A:
            return MESS_SPECPL2A, MESS_SPECPL2A_ROMS
        elif model == ZXS_MODEL_PLUS3:
            return MESS_SPECPLS3, MESS_SPECPLS3_ROMS
        else:
            return MESS_SPECTRUM, MESS_SPECTRUM_ROMS


class MessFsSpectrumDriver(MessSpectrumDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)


class SpectrumHelper:
    def __init__(self, options):
        self.options = options

    def accuracy(self):
        try:
            accuracy = int(self.options.get(Option.ACCURACY, "1"))
        except ValueError:
            accuracy = 1
        return accuracy

    def model(self):
        if self.options[Option.ZXS_MODEL] == ZXS_MODEL_128:
            return ZXS_MODEL_128
        if self.options[Option.ZXS_MODEL] == ZXS_MODEL_PLUS2:
            return ZXS_MODEL_PLUS2
        if self.options[Option.ZXS_MODEL] == ZXS_MODEL_PLUS2A:
            return ZXS_MODEL_PLUS2A
        if self.options[Option.ZXS_MODEL] == ZXS_MODEL_PLUS3:
            return ZXS_MODEL_PLUS3
        # FIXME: Deprecated
        # if self.options[Option.ZXS_MODEL] == "spectrum/if2":
        #     # return ZXS_MODEL_48K_IF2
        #     return ZXS_MODEL_48K
        return ZXS_MODEL_48K

    def has_interface_2(self):
        # return self.model() == ZXS_MODEL_48K_IF2
        return False

    def refresh_rate(self):
        # Refresh rate values retrieved from MESS.
        if self.options[Option.ZXS_MODEL] == "spectrum128":
            return 50.021084
        else:
            return 50.080128


# noinspection SpellCheckingInspection
MESS_SPECTRUM_ROMS = {
    "spectrum.rom": ZXS_48_ROM.sha1,
    # ("f9d23f25640c51bcaa63e21ed5dd66bb2d5f63d4", "1986es.rom"),
    # 9e535e2e24231ccb65e33d107f6d0ceb23e99477", "48e.rom"),
    # ("e62a431b0938af414b7ab8b1349a18b3c4407f70", "48turbo.rom"),
    # ("ab3c36daad4325c1d3b907b6dc9a14af483d14ec", "bsrom118.rom"),
    # ("2ee2dbe6ab96b60d7af1d6cb763b299374c21776", "bsrom140.rom"),
    # ("795c20324311dd5a56300e6e4ec49b0a694ac0b3", "deutsch.rom"),
    # ("51165cde68e218512d3145467074bc7e786bf307", "groot.rom"),
    # ("a701c3d4b698f7d2be537dc6f79e06e4dbc95929", "gw03.rom"),
    # ("2a9745ba3b369a84c4913c98ede66ec87cb8aec1", "hdt-iso.rom"),
    # ("dee814271c4d51de257d88128acdb324fb1d1d0d", "imc.rom"),
    # ("5752e6f789769475711b91e0a75911fa5232c767", "iso8bm.rom"),
    # ("04adbdb1380d6ccd4ab26ddd61b9ccbba462a60f", "isomoje.rom"),
    # ("d7f02ed66455f1c08ac0c864c7038a92a88ba94a", "jgh.rom"),
    # ("c103e89ef58e6ade0c01cea0247b332623bd9a30", "plus4.rom"),
    # ("0853e25857d51dd41b20a6dbc8e80f028c5befaa", "psycho.rom"),
    # ("c58ff44a28db47400f09ed362ca0527591218136", "sc01.rom"),
    # ("84ea64af06adaf05e68abe1d69454b4fc6888505", "turbo2_3.rom"),
    # ("21ad93ffe41a4458704c866cca2754f066f6a560", "turbo4_4.rom"),
}

# noinspection SpellCheckingInspection
MESS_SPEC128_ROMS = {
    "zx128_0.rom": ZXS_128_0_ROM.sha1,
    "zx128_1.rom": ZXS_128_1_ROM.sha1,
    # Spanish
    # ("968937b1c750f0ef6205f01c6db4148da4cca4e3", "zx128s0.rom"),
    # ("bea3f397cc705eafee995ea629f4a82550562f90", "zx128s1.rom"),
}

# noinspection SpellCheckingInspection
MESS_SPECPLS2_ROMS = {
    "zxp2_0.rom": ZXS_PLUS2_0_ROM.sha1,
    "zxp2_1.rom": ZXS_PLUS2_1_ROM.sha1,
}

# noinspection SpellCheckingInspection
MESS_SPECPL2A_ROMS = {
    "p2a41_0.rom": ZXS_PLUS2A_0_ROM.sha1,
    "p2a41_1.rom": ZXS_PLUS2A_1_ROM.sha1,
    "p2a41_2.rom": ZXS_PLUS2A_2_ROM.sha1,
    "p2a41_3.rom": ZXS_PLUS2A_3_ROM.sha1,
}

# noinspection SpellCheckingInspection
MESS_SPECPLS3_ROMS = {
    "pl3-0.rom": ZXS_PLUS3_0_ROM.sha1,
    "pl3-1.rom": ZXS_PLUS3_1_ROM.sha1,
    "pl3-2.rom": ZXS_PLUS3_2_ROM.sha1,
    "pl3-3.rom": ZXS_PLUS3_3_ROM.sha1,
    # ("4e5d114b72d464cefdde0566457f52a3c0c1cae2", "p3_01_4m.rom"),
    # ("4e5d114b72d464cefdde0566457f52a3c0c1cae2", "p3_01_cm.rom"),
    # ("752cdd6a083ab9910348995e483541d60bb6372b", "p3_23_4m.rom"),
    # ("d062765ceb1f3cd2c94ea51cb737cac7ad6151b4", "p3_23_cm.rom"),
    # ("500c0945760abeefcbd08bc22c0d07b14b336cf0", "plus341.rom"),
    # ("e9b0a60a1a8def511d59090b945d175bdc646346", "plus3sp0.rom"),
    # ("4e48f196427596c7990c175d135c15a039c274a4", "plus3sp1.rom"),
    # ("09fc005625589ef5992515957ce7a3167dec24b2", "plus3sp2.rom"),
    # ("ec8f644a81e2e9bcb58ace974103ea960361bad2", "plus3sp3.rom"),
}
