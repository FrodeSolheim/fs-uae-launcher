# FSGS - Common functionality for FS Game System.
# Copyright (c) 2013-2017  Frode Solheim <frode@openretro.org>
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

from fsgs.option import Option

product = "FS-UAE"
openretro = False

OPENRETRO_DEFAULT_DATABASES = [
    Option.ARCADE_DATABASE,
    Option.A7800_DATABASE,
    Option.ATARI_DATABASE,
    Option.C64_DATABASE,
    Option.CPC_DATABASE,
    Option.DOS_DATABASE,
    Option.GB_DATABASE,
    Option.GBA_DATABASE,
    Option.GBC_DATABASE,
    Option.NEOGEO_DATABASE,
    Option.NES_DATABASE,
    Option.PSX_DATABASE,
    Option.SMD_DATABASE,
    Option.SNES_DATABASE,
    Option.TG16_DATABASE,
    Option.TGCD_DATABASE,
    Option.ZXS_DATABASE,
]
