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

from fsbc import settings
from fsgs.option import Option
from fsgs.platform import PlatformHandler
from fsgs.platforms.zxs.fusespectrumdriver import FuseSpectrumDriver
from fsgs.platforms.zxs.messspectrumdriver import MessSpectrumDriver
from fsgs.platforms.zxs.spectrumplatform import SpectrumLoader


class SpectrumPlatformHandler(PlatformHandler):
    PLATFORM_NAME = "ZX Spectrum"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return SpectrumLoader(fsgs)

    def get_runner(self, fsgs):
        if settings.get(Option.ZXS_DRIVER) == "mess":
            return MessSpectrumDriver(fsgs)
        else:
            return FuseSpectrumDriver(fsgs)
