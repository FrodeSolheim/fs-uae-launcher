# FSGS - Common functionality for Fengestad Game System.
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
from fsgamesys.options.option import Option
from fsgamesys.platforms.cpc.cpcconstants import CPC_MODEL_464
from fsgamesys.platforms.cpc.cpcmamedriver import (
    CpcMameDriver,
    CpcMameFsDriver,
)
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.platform import Platform


class CpcPlatform(Platform):
    PLATFORM_NAME = "Amstrad CPC"

    @staticmethod
    def driver(fsgc):
        driver = settings.get(Option.CPC_EMULATOR)
        if not driver:
            driver = "mame"

        if driver == "mame":
            return CpcMameDriver(fsgc)
        elif driver == "mame-fs":
            return CpcMameFsDriver(fsgc)

    @staticmethod
    def loader(fsgc):
        return CpcLoader(fsgc)


class CpcLoader(SimpleLoader):
    def load_extra(self, values):
        print(values)

        model = values["cpc_model"]

        # FIXME: Remove legacy option
        if not model:
            model = values["model"]
        self.config["model"] = ""

        if not model:
            model = CPC_MODEL_464

        self.config[Option.CPC_MODEL] = model
