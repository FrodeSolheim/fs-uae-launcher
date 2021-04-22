from fsgamesys.platforms.zxspectrum.zxspectrum import ZXSpectrum
from fsgamesys.options.option import Option


class SpectrumHelper:
    def __init__(self, options):
        self.options = options

    def model(self):
        return ZXSpectrum.getModelFromConfig(self.options)

    def has_interface_2(self):
        return ZXSpectrum.hasModelInterface2(
            self.options[Option.SPECTRUM_MODEL]
        )

    def refresh_rate(self):
        return ZXSpectrum.getDisplayRefreshRateFromModel(
            self.options[Option.SPECTRUM_MODEL]
        )

    def model_name(self, model):
        return ZXSpectrum.getModelNameFromModel(model)
