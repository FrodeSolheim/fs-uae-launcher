from os import path
from typing import Dict
from .newgamedriver import GameDriver2
from .zxspectrum import ZXSpectrum


class ZXSpectrumFsFuseDriver(GameDriver2):
    # emulatorName = "fs-fuse"

    def configure(self):
        model = ZXSpectrum.getModelFromConfig(self.config)
        self.setModelName(ZXSpectrum.getModelNameFromModel(model))

        # self.set_model_name(self.helper.model_name(model))

        # fuse_machine = {
        #     SPECTRUM_MODEL_48K: "48",
        #     SPECTRUM_MODEL_128: "128",
        #     SPECTRUM_MODEL_PLUS2: "plus2",
        #     SPECTRUM_MODEL_PLUS2A: "plus2a",
        #     SPECTRUM_MODEL_PLUS3: "plus3",
        # }[model]

        fsFuseOptions = {}

        fuseOptions = {
            "machine": self.getFuseMachineFromModel(model),
            "printer": "0",
            "zxprinter": "0",
        }

        mediaDirectory = self.runService.getTempDirectory("Media")

        fsemu = self.fsemu = True
        if self.fsemu:
            for key, value in self.config.items():
                if key.startswith("fuse_") and value != "":
                    # Add option but strip fuse_ prefix
                    fuseOptions[key[5:]] = value

        self.configureAudio(fuseOptions)
        if not fsemu:
            self.configureFuseInput(fuseOptions)
        
        self.configureMedia(fsFuseOptions, fuseOptions)
        self.configureVideo(fuseOptions)

        if fsemu:
            configFile = self.writeFsFuseConfig(fsFuseOptions, fuseOptions)
            self.args.append(configFile)
        else:
            configFile = self.writeFuseConfig(fuseOptions)
        print("Wrote config file", configFile)

    def configureAudio(self, fuseOptions):
        self.logHeading("Configure audio")
        # args = []
        # args.append("--loading-sound")
        # args.append("--no-loading-sound")
        # print(args)
        # self.emulator.args.extend(args)
        fuseOptions["loadingsound"] = "1"

    def configureMedia(self, fsFuseOptions, fuseOptions):
        self.logHeading("Configure media")

        if self.options.get(Option.SNAPSHOT_FILE):
            source = self.options.get(Option.SNAPSHOT_FILE)
            name = path.basename(source)
            path = path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # elf.emulator.args.extend(["--snapshot", path])
            fusePptions["snapshot"] = path

        if self.options.get(Option.TAPE_DRIVE_0):
            source = self.options.get(Option.TAPE_DRIVE_0)
            name = path.basename(source)
            path = path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # self.emulator.args.extend(["--tape", path])
            if self.fsemu:
                fsFuseOptions["tape_drive_0"] = path
            else:
                fuseOptions["tape"] = path

        if self.options.get(Option.FLOPPY_DRIVE_0):
            source = self.options.get(Option.FLOPPY_DRIVE_0)
            name = path.basename(source)
            path = path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # +3 Drive A Defaults to a single - sided 40 track drive.
            # self.emulator.args.extend(["--plus3disk", path])
            # self.emulator.args.extend(["--drive-plus3b-type", "Disabled"])
            fuseOptions["plus3disk"] = path
            fuseOptions["driveplus3btype"] = "Disabled"

        if self.options.get(Option.CARTRIDGE_SLOT):
            source = self.options.get(Option.CARTRIDGE_SLOT)
            name = path.basename(source)
            path = path.join(self.media_dir.path, name)
            self.files.add(path, source=source)
            # elf.emulator.args.extend(["--if2cart", path])
            fuseOptions["if2cart"] = path

        # The multi-load aspect of SLT files requires a trap instruction
        # to be supported. Always disable in case normal programs use it.
        # self.emulator.args.extend(["--no-slt"])
        fuseOptions["slt"] = "0"

        # if self.helper.accuracy() == 1:
        #     traps = False
        # else:
        #     traps = True
        # if traps:
        #     self.emulator.args.extend(["--traps"])
        # else:
        #     self.emulator.args.extend(["--no-traps"])

        if self.useAutoLoad():
            # self.emulator.args.extend(["--auto-load"])
            # self.emulator.args.extend(["--detect-loader"])
            fuseOptions["autoload"] = "1"
            # Detect when tape is accessed and automatically start/stop tape.
            fuseOptions["detectloader"] = "1"
        else:
            # self.emulator.args.extend(["--no-auto-load"])
            # self.emulator.args.extend(["--no-detect-loader"])
            fuseOptions["autoload"] = "0"
            fuseOptions["detectloader"] = "0"

        if self.useTurboLoad():
            # self.emulator.args.extend(["--accelerate-loader"])
            # self.emulator.args.extend(["--fastload"])
            # self.emulator.args.extend(["--traps"])
            fuseOptions["accelerateloader"] = "1"
            fuseOptions["fastload"] = "1"
            fuseOptions["slttraps"] = "1"
            fuseOptions["tapetraps"] = "1"
        else:
            # self.emulator.args.extend(["--no-accelerate-loader"])
            # self.emulator.args.extend(["--no-fastload"])
            # self.emulator.args.extend(["--no-traps"])
            fuseOptions["accelerateloader"] = "0"
            fuseOptions["fastload"] = "0"
            fuseOptions["slttraps"] = "0"
            fuseOptions["tapetraps"] = "0"

    def configureVideo(self, fuseOptions):
        self.logHeading("Configure video")

        if self.useFullscreen():
            self.args.append("--full-screen")
        # if self.effect() == self.CRT_EFFECT:
        #     graphics_filter = "paltv2x"
        # elif self.effect() == self.SCALE2X_EFFECT:
        #     graphics_filter = "advmame2x"
        # elif self.effect() == self.HQ2X_EFFECT:
        #     graphics_filter = "hq2x"
        # else:
        graphics_filter = "2x"
        # self.emulator.args.extend(["--graphics-filter", graphics_filter])
        fuseOptions["graphicsfilter"] = graphics_filter

    def configureFuseInput(self, fuseOptions):
        self.logHeading("Configure input")

        kempston = False
        sinclair = False
        # joystick1output 0 # none
        # joystick1output 1 # cursor
        # joystick1output 2 # kempston
        # joystick1output 3 # sinclair 1
        # joystick1output 4 # sinclair 2
        joystickoutput = [0, 0]

        for i, port in enumerate(self.ports):
            if port.type == ZXSpectrum.KEMPSTON_JOYSTICK_TYPE:
                kempston = True
            if port.type == ZXSpectrum.SINCLAIR_JOYSTICK_TYPE:
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
                if port.type == ZXSpectrum.CURSOR_JOYSTICK_TYPE:
                    joystickoutput[port.device.index] = 1
                if port.type == ZXSpectrum.KEMPSTON_JOYSTICK_TYPE:
                    kempston = True
                    joystickoutput[port.device.index] = 2
                if port.type == ZXSpectrum.SINCLAIR_JOYSTICK_TYPE:
                    sinclair = True
                    joystickoutput[port.device.index] = 3 if i == 0 else 4

        # self.emulator.args.extend(
        #     ["--joystick-1-output", str(joystickoutput[0])]
        # )
        # self.emulator.args.extend(
        #     ["--joystick-2-output", str(joystickoutput[1])]
        # )

        fuseOptions["joystick1output"] = joystickoutput[0]
        fuseOptions["joystick2output"] = joystickoutput[1]

        # FIXME: interface 2 is probably also needed when using cartridges
        # FIXME: This option might be only relevant for cartridge?
        if sinclair:
            fuseOptions["interface2"] = "1"
            # self.emulator.args.extend(["--interface2"])
        else:
            fuseOptions["interface2"] = "0"
            # self.emulator.args.extend(["--no-interface2"])

        if kempston:
            fuseOptions["kempston"] = "1"
            # self.emulator.args.extend(["--kempston"])
        else:
            fuseOptions["kempston"] = "0"
            # self.emulator.args.extend(["--no-kempston"])

        # if self.helper.has_interface_2():
        #     self.emulator.args.extend(["--interface2"])
        # else:
        #     self.emulator.args.extend(["--no-interface2"])

        # self.emulator.args.extend(["--kempston-mouse"])
        # self.emulator.args.extend(["--no-kempston-mouse"])
        fuseOptions["kempstonmouse"] = "0"

    def writeFsFuseConfig(self, fsFuseOptions, fuseOptions) -> str:
        config_file = self.runService.getTempFile(".fs-fuse")
        with open(config_file.path, "w") as f:
            f.write("[fs-fuse]\n")
            for key, value in fsFuseOptions.items():
                f.write("{0} = {1}\n".format(key, value))
            for key, value in fuseOptions.items():
                f.write("fuse_{0} = {1}\n".format(key, value))
        # self.emulator.args.append(config_file.path)
        return config_file.path

    def writeFuseConfig(self, fuseOptions) -> str:
        # FIXME: Call it self.fakehome_dir.path?
        fuse_rc_path = path.join(self.runService.getFakeHome(), ".fuserc")
        with open(fuse_rc_path, "w") as f:
            f.write('<?xml version="1.0"?>\n')
            f.write("<settings>\n")
            for key, value in fuseOptions.items():
                f.write("  <{0}>{1}</{0}>\n".format(key, value))
            f.write("</settings>\n")
        self.logHeading("Fuse config file")
        with open(fuse_rc_path, "r") as f:
            print(f.read())
        return fuse_rc_path

    @staticmethod
    def getFuseMachineFromModel(model):
        return {
            ZXSpectrum.MODEL_48K: "48",
            ZXSpectrum.MODEL_128: "128",
            ZXSpectrum.MODEL_PLUS2: "plus2",
            ZXSpectrum.MODEL_PLUS2A: "plus2a",
            ZXSpectrum.MODEL_PLUS3: "plus3",
        }[model]

    # def prepare(self):
    #     pass

    # # def run(self):
    # #     self.runEmulator(
    # #         emulator=self.findEmulator("fuse"),
    # #         args=self.args,
    # #         env=self.prepareEnvironment(self.env),
    # #     )

    # def cleanup(self):
    #     pass
