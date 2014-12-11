# FSGS - Common functionality for Fengestad Game System.
# Copyright (C) 2013  Frode Solheim <frode-code@fengestad.no>
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

import os
import json
from fsgs.platform import PlatformHandler
from fsgs.mess.zx_spectrum import ZXSpectrumRunner
from .loader import SimpleLoader


class ZXSpectrumPlatformHandler(PlatformHandler):

    PLATFORM_NAME = "ZX Spectrum"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return ZXSpectrumLoader(fsgs)

    def get_runner(self, fsgs):
        return ZXSpectrumRunner(fsgs)


class ZXSpectrumLoader(SimpleLoader):

    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        assert len(file_list) == 1

        name = file_list[0]["name"]
        sha1 = file_list[0]["sha1"]
        _, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext in [".z80"]:
            key = "snapshot"
        elif ext in [".tap", ".tzx"]:
            key = "tape_drive"
        elif ext in [".dsk"]:
            key = "floppy_drive"
        else:
            return
        self.config[key] = "sha1://{0}/{1}".format(sha1, name)
