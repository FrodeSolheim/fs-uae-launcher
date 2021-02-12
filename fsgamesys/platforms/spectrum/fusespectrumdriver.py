import os
from fsgamesys.drivers.gamedriver import GameDriver
from fsgamesys.platforms.spectrum import SPECTRUM_PORTS
from fsgamesys.platforms.spectrum.spectrumhelper import SpectrumHelper
from fsgamesys.platforms.spectrum import (
    SPECTRUM_MODEL_48K,
    SPECTRUM_MODEL_PLUS2,
    SPECTRUM_MODEL_PLUS2A,
    SPECTRUM_MODEL_PLUS3,
    SPECTRUM_MODEL_128,
    SPECTRUM_CURSOR_JOYSTICK_TYPE,
    SPECTRUM_SINCLAIR_JOYSTICK_TYPE,
    SPECTRUM_KEMPSTON_JOYSTICK_TYPE
)
from fsgamesys.options.option import Option


def log_heading(heading):
    print("")
    print("=" * 79)
    # print("=" * 79)
    print(heading.upper())
    # print("-" * 79)


class FuseSpectrumDriver(GameDriver):
    PORTS = SPECTRUM_PORTS

    def __init__(self, fsgs, fsemu=False):
        super().__init__(fsgs)
        self.fsemu = fsemu
        if fsemu:
            self.emulator.name = "FS-Fuse"
            self.emulator.exe_name = "fs-fuse"
            self.emulator.allow_home_access = True
        else:
            self.emulator.name = "Fuse"
            self.emulator.exe_name = "fuse"
        self.helper = SpectrumHelper(self.options)
        # self.emulator.allow_system_emulator = True
        self.media_dir = self.temp_dir("Media")
        self.roms_dir = self.temp_dir("ROMs")
        # self.options_file = self.temp_file("hatari.cfg")
        # self.floppies = []
        self.fuse_options = {}
        self.fs_fuse_options = {}

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
        self.set_model_name(self.helper.model_name(model))
        fuse_machine = {
            SPECTRUM_MODEL_48K: "48",
            SPECTRUM_MODEL_128: "128",
            SPECTRUM_MODEL_PLUS2: "plus2",
            SPECTRUM_MODEL_PLUS2A: "plus2a",
            SPECTRUM_MODEL_PLUS3: "plus3"
        }[model]
        self.fuse_options["machine"] = fuse_machine

        # self.emulator.args.extend(["--machine", fuse_machine])

        # elif self.helper.model() == SPECTRUM_MODEL_48K_IF2:
        #     self.emulator.args.extend(["--machine", "48"])
        #     self.set_model_name("ZX Spectrum 48K")
        # elif model == SPECTRUM_MODEL_128:
        #     self.emulator.args.extend(["--machine", "128"])
        # elif model == SPECTRUM_MODEL_PLUS2:
        #     self.emulator.args.extend(["--machine", "plus2"])
        # elif model == SPECTRUM_MODEL_PLUS2A:
        #     self.emulator.args.extend(["--machine", "plus2a"])
        # elif model == SPECTRUM_MODEL_PLUS3:
        #     self.emulator.args.extend(["--machine", "plus3"])
        # else:
        #     raise Exception("Unrecognized ZX Spectrum model")

        if self.options.get(Option.SNAPSHOT_FILE):
            source = self.options.get(Option.SNAPSHOT_FILE)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # elf.emulator.args.extend(["--snapshot", path])
            self.fuse_options["snapshot"] = path

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
        # self.emulator.args.extend(["--no-printer"])
        self.fuse_options["printer"] = "0"
        self.fuse_options["zxprinter"] = "0"
        # self.emulator.args.extend(["--no-zxprinter"])

        # ROMs are now bundled with Fuse-FS. Also, it appears Fuse
        # misbehaves when explicitly specifying (at least) the 48 rom.
        # def install_rom(name, rom):
        #     path = os.path.join(self.roms_dir.path, name + ".rom")
        #     self.files.add(path, sha1=rom.sha1, description=name + ".rom")
        #     self.emulator.args.extend(["--rom-{}".format(name), path])
        # if self.helper.model() == SPECTRUM_MODEL_48K:
        #     install_rom("48", SPECTRUM_48_ROM)
        # elif self.helper.model() == SPECTRUM_MODEL_128:
        #     install_rom("128-0", SPECTRUM_128_0_ROM)
        #     install_rom("128-1", SPECTRUM_128_1_ROM)
        # elif self.helper.model() == SPECTRUM_MODEL_PLUS3:
        #     install_rom("plus3-0", SPECTRUM_PLUS3_0_ROM)
        #     install_rom("plus3-1", SPECTRUM_PLUS3_1_ROM)
        #     install_rom("plus3-2", SPECTRUM_PLUS3_2_ROM)
        #     install_rom("plus3-3", SPECTRUM_PLUS3_3_ROM)

        if self.fsemu:
            config_file = self.temp_file(".fs-fuse")
            with open(config_file.path, "w") as f:
                f.write("[fs-fuse]\n")
                for key, value in self.fs_fuse_options.items():
                    f.write("{0} = {1}\n".format(key, value))
                for key, value in self.fuse_options.items():
                    f.write("fuse_{0} = {1}\n".format(key, value))
            self.emulator.args.append(config_file.path)
        else:
            # FIXME: Call it self.fakehome_dir.path?
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
        # args = []
        # args.append("--loading-sound")
        # args.append("--no-loading-sound")
        # print(args)
        # self.emulator.args.extend(args)
        self.fuse_options["loadingsound"] = "1"

    def configure_input(self):
        if self.fsemu:
            self.configure_input_fsemu()
        else:
            self.configure_input_fuse()

    def configure_input_fsemu(self):
        pass

    def configure_input_fuse(self):

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
            if port.type == SPECTRUM_KEMPSTON_JOYSTICK_TYPE:
                kempston = True
            if port.type == SPECTRUM_SINCLAIR_JOYSTICK_TYPE:
                sinclair = True

            print("port", i, port.type, port)
            print("device", port.device)
            if port.device:
                print(port.device.index)
                if port.device.index >= 2:
                    raise Exception(
                        "Fuse only works with the first two "
                        "connected joysticks :(. This will be fixed later."
                    )
                if port.type == SPECTRUM_CURSOR_JOYSTICK_TYPE:
                    joystickoutput[port.device.index] = 1
                if port.type == SPECTRUM_KEMPSTON_JOYSTICK_TYPE:
                    kempston = True
                    joystickoutput[port.device.index] = 2
                if port.type == SPECTRUM_SINCLAIR_JOYSTICK_TYPE:
                    sinclair = True
                    joystickoutput[port.device.index] = 3 if i == 0 else 4

        # self.emulator.args.extend(
        #     ["--joystick-1-output", str(joystickoutput[0])]
        # )
        # self.emulator.args.extend(
        #     ["--joystick-2-output", str(joystickoutput[1])]
        # )

        self.fuse_options["joystick1output"] = joystickoutput[0]
        self.fuse_options["joystick2output"] = joystickoutput[1]

        # FIXME: interface 2 is probably also needed when using cartridges
        # FIXME: This option might be only relevant for cartridge?
        if sinclair:
            self.fuse_options["interface2"] = "1"
            # self.emulator.args.extend(["--interface2"])
        else:
            self.fuse_options["interface2"] = "0"
            # self.emulator.args.extend(["--no-interface2"])

        if kempston:
            self.fuse_options["kempston"] = "1"
            # self.emulator.args.extend(["--kempston"])
        else:
            self.fuse_options["kempston"] = "0"
            # self.emulator.args.extend(["--no-kempston"])

        # if self.helper.has_interface_2():
        #     self.emulator.args.extend(["--interface2"])
        # else:
        #     self.emulator.args.extend(["--no-interface2"])

        # self.emulator.args.extend(["--kempston-mouse"])
        # self.emulator.args.extend(["--no-kempston-mouse"])
        self.fuse_options["kempstonmouse"] = "0"

    def configure_media(self):
        log_heading("Configure_media")

        if self.options.get(Option.TAPE_DRIVE_0):
            source = self.options.get(Option.TAPE_DRIVE_0)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # self.emulator.args.extend(["--tape", path])
            if self.fsemu:
                self.fs_fuse_options["tape_drive_0"] = path
            else:
                self.fuse_options["tape"] = path

        if self.options.get(Option.FLOPPY_DRIVE_0):
            source = self.options.get(Option.FLOPPY_DRIVE_0)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # +3 Drive A Defaults to a single - sided 40 track drive.
            # self.emulator.args.extend(["--plus3disk", path])
            # self.emulator.args.extend(["--drive-plus3b-type", "Disabled"])
            self.fuse_options["plus3disk"] = path
            self.fuse_options["driveplus3btype"] = "Disabled"

        if self.options.get(Option.CARTRIDGE_SLOT):
            source = self.options.get(Option.CARTRIDGE_SLOT)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # elf.emulator.args.extend(["--if2cart", path])
            self.fuse_options["if2cart"] = path

        # The multi-load aspect of SLT files requires a trap instruction
        # to be supported. Always disable in case normal programs use it.
        # self.emulator.args.extend(["--no-slt"])
        self.fuse_options["slt"] = "0"

        # if self.helper.accuracy() == 1:
        #     traps = False
        # else:
        #     traps = True
        # if traps:
        #     self.emulator.args.extend(["--traps"])
        # else:
        #     self.emulator.args.extend(["--no-traps"])

        if self.use_auto_load():
            # self.emulator.args.extend(["--auto-load"])
            # self.emulator.args.extend(["--detect-loader"])
            self.fuse_options["autoload"] = "1"
            # Detect when tape is accessed and automatically start/stop tape.
            self.fuse_options["detectloader"] = "1"
        else:
            # self.emulator.args.extend(["--no-auto-load"])
            # self.emulator.args.extend(["--no-detect-loader"])
            self.fuse_options["autoload"] = "0"
            self.fuse_options["detectloader"] = "0"

        if self.use_turbo_load():
            # self.emulator.args.extend(["--accelerate-loader"])
            # self.emulator.args.extend(["--fastload"])
            # self.emulator.args.extend(["--traps"])
            self.fuse_options["accelerateloader"] = "1"
            self.fuse_options["fastload"] = "1"
            self.fuse_options["traps"] = "1"
        else:
            # self.emulator.args.extend(["--no-accelerate-loader"])
            # self.emulator.args.extend(["--no-fastload"])
            # self.emulator.args.extend(["--no-traps"])
            self.fuse_options["accelerateloader"] = "0"
            self.fuse_options["fastload"] = "0"
            self.fuse_options["traps"] = "0"

    def configure_video(self):
        log_heading("Configure video")

        if self.use_fullscreen():
            self.emulator.args.extend(["--full-screen"])
        # if self.effect() == self.CRT_EFFECT:
        #     graphics_filter = "paltv2x"
        # elif self.effect() == self.SCALE2X_EFFECT:
        #     graphics_filter = "advmame2x"
        # elif self.effect() == self.HQ2X_EFFECT:
        #     graphics_filter = "hq2x"
        # else:
        graphics_filter = "2x"
        # self.emulator.args.extend(["--graphics-filter", graphics_filter])
        self.fuse_options["graphicsfilter"] = graphics_filter

    def install(self):
        super().install()

    def run(self):
        super().run()

    def finish(self):
        super().finish()

    def get_game_refresh_rate(self):
        return self.helper.refresh_rate()
