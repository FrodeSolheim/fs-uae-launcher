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

from fsgs.options.option import Option

product = "FS-UAE"
openretro = False


def fsgs_product():
    return product


OPENRETRO_DEFAULT_DATABASES = [
    Option.ARCADE_DATABASE,
    Option.A7800_DATABASE,
    Option.C64_DATABASE,
    Option.CPC_DATABASE,
    Option.DOS_DATABASE,
    Option.GB_DATABASE,
    Option.GBA_DATABASE,
    Option.GBC_DATABASE,
    Option.NEOGEO_DATABASE,
    Option.NES_DATABASE,
    Option.PSX_DATABASE,
    Option.SGG_DATABASE,
    Option.SMD_DATABASE,
    Option.SMS_DATABASE,
    Option.SNES_DATABASE,
    Option.ST_DATABASE,
    Option.TG16_DATABASE,
    Option.TGCD_DATABASE,
    Option.ZXS_DATABASE,
]
