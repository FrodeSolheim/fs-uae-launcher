from fsgamesys.options.option import Option

from .newgamedriver import GameDriver2


class ZXSpectrum:

    MODEL_48K = "48k"
    # ZXS_MODEL_48K_IF2 = "spectrum/if2"
    MODEL_128 = "128"
    MODEL_PLUS2 = "plus2"
    MODEL_PLUS2A = "plus2a"
    MODEL_PLUS3 = "plus3"

    KEMPSTON_JOYSTICK_TYPE = "kempston"
    SINCLAIR_JOYSTICK_TYPE = "sinclair"
    CURSOR_JOYSTICK_TYPE = "cursor"
    NO_CONTROLLER_TYPE = "none"

    @staticmethod
    def createDriver() -> GameDriver2:
        emulator = self.findEmulator("fs-fuse")
        return ZXSpectrumFsFuseDriver(emulator)

    @staticmethod
    def getDisplayRefreshRateFromModel(model):
        # Refresh rate values retrieved from MESS.
        if model == ZXSpectrum.MODEL_128:
            return 50.021084
        else:
            return 50.080128

    @staticmethod
    def getModelFromConfig(config):
        return {
            "": ZXSpectrum.MODEL_48K,
            ZXSpectrum.MODEL_48K: ZXSpectrum.MODEL_48K,
            ZXSpectrum.MODEL_128: ZXSpectrum.MODEL_128,
            ZXSpectrum.MODEL_PLUS2: ZXSpectrum.MODEL_PLUS2,
            ZXSpectrum.MODEL_PLUS2A: ZXSpectrum.MODEL_PLUS2A,
            ZXSpectrum.MODEL_PLUS3: ZXSpectrum.MODEL_PLUS3,
        }[config[Option.SPECTRUM_MODEL]]

    @staticmethod
    def getModelNameFromModel(model: str):
        if model == ZXSpectrum.MODEL_48K:
            return "ZX Spectrum 48K"
        # elif self.helper.model() == SPECTRUM_MODEL_48K_IF2:
        #     self.emulator.args.extend(["--machine", "48"])
        #     self.set_model_name("ZX Spectrum 48K")
        elif model == ZXSpectrum.MODEL_128:
            return "ZX Spectrum 128"
        elif model == ZXSpectrum.MODEL_PLUS2:
            return "ZX Spectrum +2"
        elif model == ZXSpectrum.MODEL_PLUS2A:
            return "ZX Spectrum +2A"
        elif model == ZXSpectrum.MODEL_PLUS3:
            return "ZX Spectrum +3"
        else:
            raise Exception("Unrecognized ZX Spectrum model")

    @staticmethod
    def hasModelInterface2(model):
        # return model == SPECTRUM_MODEL_48K_IF2
        return False
