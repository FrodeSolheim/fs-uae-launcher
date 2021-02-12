from fsgamesys.options.option import Option
from fsgamesys.platforms.spectrum import (
    SPECTRUM_MODEL_48K,
    SPECTRUM_MODEL_PLUS2,
    SPECTRUM_MODEL_PLUS2A,
    SPECTRUM_MODEL_PLUS3,
    SPECTRUM_MODEL_128,
)


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
        if self.options[Option.SPECTRUM_MODEL] == SPECTRUM_MODEL_128:
            return SPECTRUM_MODEL_128
        if self.options[Option.SPECTRUM_MODEL] == SPECTRUM_MODEL_PLUS2:
            return SPECTRUM_MODEL_PLUS2
        if self.options[Option.SPECTRUM_MODEL] == SPECTRUM_MODEL_PLUS2A:
            return SPECTRUM_MODEL_PLUS2A
        if self.options[Option.SPECTRUM_MODEL] == SPECTRUM_MODEL_PLUS3:
            return SPECTRUM_MODEL_PLUS3
        # FIXME: Deprecated
        # if self.options[Option.SPECTRUM_MODEL] == "spectrum/if2":
        #     # return SPECTRUM_MODEL_48K_IF2
        #     return SPECTRUM_MODEL_48K
        return SPECTRUM_MODEL_48K

    def has_interface_2(self):
        # return self.model() == SPECTRUM_MODEL_48K_IF2
        return False

    def refresh_rate(self):
        # Refresh rate values retrieved from MESS.
        if self.options[Option.SPECTRUM_MODEL] == "spectrum128":
            return 50.021084
        else:
            return 50.080128

    def model_name(self, model):
        if model == SPECTRUM_MODEL_48K:
            return "ZX Spectrum 48K"
        # elif self.helper.model() == SPECTRUM_MODEL_48K_IF2:
        #     self.emulator.args.extend(["--machine", "48"])
        #     self.set_model_name("ZX Spectrum 48K")
        elif model == SPECTRUM_MODEL_128:
            return "ZX Spectrum 128"
        elif model == SPECTRUM_MODEL_PLUS2:
            return "ZX Spectrum +2"
        elif model == SPECTRUM_MODEL_PLUS2A:
            return "ZX Spectrum +2A"
        elif model == SPECTRUM_MODEL_PLUS3:
            return "ZX Spectrum +3"
        else:
            raise Exception("Unrecognized ZX Spectrum model")
