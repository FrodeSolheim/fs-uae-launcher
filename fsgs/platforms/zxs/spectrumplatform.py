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

import json
import os

from fsgs.option import Option
from fsgs.platforms.loader import SimpleLoader

ZXS_MODEL_48K = "spectrum"
ZXS_MODEL_128 = "spectrum128"
ZXS_MODEL_PLUS3 = "spectrum+3"


class SpectrumLoader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        if len(file_list) == 0:
            self.config["x_variant_error"] = "Variant has empty file list"
        elif len(file_list) > 1:
            self.config["x_variant_error"] = "Unsupported multi-file variant"

        name = file_list[0]["name"]
        sha1 = file_list[0]["sha1"]
        _, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext in [".z80"]:
            key = Option.SNAPSHOT_FILE
        elif ext in [".tap", ".tzx"]:
            key = Option.TAPE_DRIVE_0
        elif ext in [".dsk", ".trd"]:
            key = Option.FLOPPY_DRIVE_0
        elif ext in [".rom"]:
            key = Option.CARTRIDGE_SLOT
        else:
            return
        self.config[key] = "sha1://{0}/{1}".format(sha1, name)

    def load_extra(self, values):
        self.config[Option.ZXS_MODEL] = values["model"]
        if not self.config[Option.ZXS_MODEL]:
            self.config[Option.ZXS_MODEL] = ZXS_MODEL_48K
        self.config["model"] = ""
