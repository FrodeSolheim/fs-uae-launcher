from fscore.settings import Settings
from fsgamesys.options.option import Option
from fsgamesys.platforms.platform import Platform
from fsgamesys.platforms.spectrum.spectrumloader import SpectrumLoader
from fsgamesys.platforms.spectrum.fsfusespectrumdriver import (
    FsFuseSpectrumDriver,
)


class SpectrumPlatform(Platform):
    PLATFORM_NAME = "ZX Spectrum"

    @staticmethod
    def driver(gscontext):
        driver = Settings.get(Option.SPECTRUM_EMULATOR)
        if not driver:
            driver = "fs-fuse"

        if driver == "fuse":
            return FuseSpectrumDriver(gscontext)
        elif driver == "fs-fuse":
            return FsFuseSpectrumDriver(gscontext)
        if driver == "mame":
            return MessSpectrumDriver(gscontext)
        elif driver == "mame-fs":
            return MessFsSpectrumDriver(gscontext)
        else:
            raise Exception('Unrecognized spectrum driver "{}"'.format(driver))

    @staticmethod
    def loader(gscontext):
        return SpectrumLoader(gscontext)
