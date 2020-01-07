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

CPC_MODEL_464 = "464"
CPC_MODEL_664 = "664"
CPC_MODEL_6128 = "6128"

CPC_JOYSTICK_TYPE = "joystick"
CPC_NO_CONTROLLER_TYPE = "none"

CPC_JOYSTICK = {
    "type": CPC_JOYSTICK_TYPE,
    "description": "Joystick",
    "mapping_name": "cpc",
}

CPC_NO_CONTROLLER = {
    "type": CPC_NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}

CPC_PORTS = [
    {
        "description": "Joystick Port 1",
        "types": [CPC_NO_CONTROLLER, CPC_JOYSTICK,],
        "type_option": "cpc_port_1_type",
        "device_option": "cpc_port_1",
    },
]

# noinspection SpellCheckingInspection
CPC_MAME_ROMS_464 = {
    "56d39c463da60968d93e58b4ba0e675829412a20": "cpc464.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}

# noinspection SpellCheckingInspection
CPC_MAME_ROMS_664 = {
    "073a7665527b5bd8a148747a3947dbd3328682c8": "cpc664.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}

# noinspection SpellCheckingInspection
CPC_MAME_ROMS_6128 = {
    "5977adbad3f7c1e0e082cd02fe76a700d9860c30": "cpc6128.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}
