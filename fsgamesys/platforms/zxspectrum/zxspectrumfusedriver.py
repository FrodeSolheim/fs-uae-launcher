from .newgamedriver import NewGameDriver


class ZXSpectrumFuseDriver(NewGameDriver):
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
