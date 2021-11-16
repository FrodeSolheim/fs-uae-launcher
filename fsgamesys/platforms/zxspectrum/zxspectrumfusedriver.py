from fsgamesys.platforms.zxspectrum.newgamedriver import GameDriver2


class ZXSpectrumFuseDriver(GameDriver2):
    emulatorName = "fuse"

    def configure(self):
        pass

    def prepare(self):
        pass

    # def run(self):
    #     self.runEmulator(
    #         emulator=self.findEmulator("fuse"),
    #         args=self.args,
    #         env=self.prepareEnvironment(self.env),
    #     )

    def cleanup(self):
        pass
