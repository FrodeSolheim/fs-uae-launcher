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

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from fsgs.platform import PlatformHandler
from fsgs.vice.commodore_64 import Commodore64Runner
from .loader import SimpleLoader


class Commodore64PlatformHandler(PlatformHandler):

    PLATFORM_NAME = "Commodore 64"

    def __init__(self):
        PlatformHandler.__init__(self)

    def get_loader(self, fsgs):
        return Commodore64Loader(fsgs)

    def get_runner(self, fsgs):
        return Commodore64Runner(fsgs)


class Commodore64Loader(SimpleLoader):

    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        #assert len(file_list) == 1
        if file_list[0]["name"].endswith(".tap"):
            self.config["tape_drive"] = "sha1://{0}/{1}".format(
                file_list[0]["sha1"], file_list[0]["name"])
