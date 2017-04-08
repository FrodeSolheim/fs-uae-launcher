import os

from fsgs.drivers.gamedriver import GameDriver
from fsgs.option import Option
# from fsgs.spectrum import ZXS_48_ROM, ZXS_128_0_ROM, ZXS_128_1_ROM, \
#     ZXS_PLUS3_0_ROM, ZXS_PLUS3_1_ROM, ZXS_PLUS3_2_ROM, ZXS_PLUS3_3_ROM

ZXS_MODEL_48K = "spectrum"
ZXS_MODEL_48K_IF2 = "spectrum/if2"
ZXS_MODEL_128 = "spectrum128"
ZXS_MODEL_PLUS3 = "spectrum+3"


class FuseSpectrumDriver(GameDriver):
    JOYSTICK = {
        "type": "joystick",
        "description": "Joystick",
        "mapping_name": "zx-spectrum-joystick",
    }

    PORTS = [
        {
            "description": "Joystick Port",
            "types": [JOYSTICK]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)
        self.emulator.name = "fuse-fs"
        self.helper = SpectrumHelper(self.options)
        # self.emulator.allow_system_emulator = True
        self.media_dir = self.temp_dir("Media")
        self.roms_dir = self.temp_dir("ROMs")
        self.tos_file = self.temp_file("tos.img")
        # self.options_file = self.temp_file("hatari.cfg")
        # self.floppies = []

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

        if self.helper.model() == ZXS_MODEL_48K:
            self.emulator.args.extend(["--machine", "48"])
            self.set_model_name("ZX Spectrum 48K")
        elif self.helper.model() == ZXS_MODEL_48K_IF2:
            self.emulator.args.extend(["--machine", "48"])
            self.set_model_name("ZX Spectrum 48K")
        elif self.helper.model() == ZXS_MODEL_128:
            self.emulator.args.extend(["--machine", "128"])
            self.set_model_name("ZX Spectrum 128")
        elif self.helper.model() == ZXS_MODEL_PLUS3:
            self.emulator.args.extend(["--machine", "plus3"])
            self.set_model_name("ZX Spectrum +3")
        else:
            raise Exception("Unrecognized ZX Spectrum model")

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

        if self.options.get(Option.SNAPSHOT_FILE):
            source = self.options.get(Option.SNAPSHOT_FILE)
            name = os.path.basename(source)
            path = os.path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            self.emulator.args.extend(["--snapshot", path])

        if self.helper.has_interface_2():
            self.emulator.args.extend(["--interface2"])
        else:
            self.emulator.args.extend(["--no-interface2"])

        # self.emulator.args.extend(["--kempston"])
        self.emulator.args.extend(["--no-kempston"])

        # self.emulator.args.extend(["--kempston-mouse"])
        self.emulator.args.extend(["--no-kempston-mouse"])

        # self.emulator.args.extend(["--printer"])
        self.emulator.args.extend(["--no-printer"])

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

        # If this option is enabled, then Fuse will attempt to accelerate
        # tape loaders by "short circuiting" the loading loop. This will
        # in general speed up loading, but may cause some loaders to fail.
        # FS: The speed improvement seems minor, so disable it always.
        # self.emulator.args.extend(["--no-accelerate-loader"])

        self.configure_audio()
        self.configure_input()
        self.configure_video()

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

    def configure_audio(self):
        self.emulator.args.extend(["--loading-sound"])
        # self.emulator.args.extend(["--no-loading-sound"])

    def configure_input(self):
        pass

    def configure_video(self):
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
        if self.options[Option.ZXS_MODEL] == "spectrum/if2":
            return ZXS_MODEL_48K_IF2
        if self.options[Option.ZXS_MODEL] == "spectrum128":
            return ZXS_MODEL_128
        if self.options[Option.ZXS_MODEL] == "spectrum+3":
            return ZXS_MODEL_PLUS3
        return ZXS_MODEL_48K

    def has_interface_2(self):
        return self.model() == ZXS_MODEL_48K_IF2

    def refresh_rate(self):
        # Refresh rate values retrieved from MESS.
        if self.options[Option.ZXS_MODEL] == "spectrum128":
            return 50.021084
        else:
            return 50.080128
