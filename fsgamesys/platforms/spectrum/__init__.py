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
from fsgamesys.knownfiles import KnownFile
from fsgamesys.platforms import PLATFORM_ID_SPECTRUM

from fsgamesys.platforms.zxspectrum.zxspectrum import ZXSpectrum
SPECTRUM_MODEL_48K = ZXSpectrum.MODEL_48K
# ZXS_MODEL_48K_IF2 = "spectrum/if2"
SPECTRUM_MODEL_128 = ZXSpectrum.MODEL_128
SPECTRUM_MODEL_PLUS2 = ZXSpectrum.MODEL_PLUS2
SPECTRUM_MODEL_PLUS2A = ZXSpectrum.MODEL_PLUS2A
SPECTRUM_MODEL_PLUS3 = ZXSpectrum.MODEL_PLUS3

SPECTRUM_48_ROM = KnownFile(
    "5ea7c2b824672e914525d1d5c419d71b84a426a2", PLATFORM_ID_SPECTRUM, "48.rom"
)
SPECTRUM_128_0_ROM = KnownFile(
    "4f4b11ec22326280bdb96e3baf9db4b4cb1d02c5",
    PLATFORM_ID_SPECTRUM,
    "128-0.rom",
)
SPECTRUM_128_1_ROM = KnownFile(
    "80080644289ed93d71a1103992a154cc9802b2fa",
    PLATFORM_ID_SPECTRUM,
    "128-1.rom",
)

SPECTRUM_PLUS2_0_ROM = KnownFile(
    "72703f9a3e734f3c23ec34c0727aae4ccbef9a91",
    PLATFORM_ID_SPECTRUM,
    "plus2-0.rom",
)
SPECTRUM_PLUS2_1_ROM = KnownFile(
    "de8b0d2d0379cfe7c39322a086ca6da68c7f23cb",
    PLATFORM_ID_SPECTRUM,
    "plus2-1.rom",
)

# SPECTRUM_PLUS3_0_ROM = KnownFile(
#     "e319ed08b4d53a5e421a75ea00ea02039ba6555b", PLATFORM_ID_SPECTRUM, "plus3-0.rom"
# )
# SPECTRUM_PLUS3_1_ROM = KnownFile(
#     "c9969fc36095a59787554026a9adc3b87678c794", PLATFORM_ID_SPECTRUM, "plus3-1.rom"
# )
# SPECTRUM_PLUS3_2_ROM = KnownFile(
#     "22e50c6ba4157a3f6a821bd9937cd26e292775c6", PLATFORM_ID_SPECTRUM, "plus3-2.rom"
# )
# SPECTRUM_PLUS3_3_ROM = KnownFile(
#     "65f031caa8148a5493afe42c41f4929deab26b4e", PLATFORM_ID_SPECTRUM, "plus3-3.rom"
# )

SPECTRUM_PLUS2A_0_ROM = KnownFile(
    "62ec15a4af56cd1d206d0bd7011eac7c889a595d",
    PLATFORM_ID_SPECTRUM,
    "p2a41_0.rom",
)
SPECTRUM_PLUS2A_1_ROM = KnownFile(
    "1a7812c383a3701e90e88d1da086efb0c033ac72",
    PLATFORM_ID_SPECTRUM,
    "p2a41_1.rom",
)
SPECTRUM_PLUS2A_2_ROM = KnownFile(
    "8df145d10ff78f98138682ea15ebccb2874bf759",
    PLATFORM_ID_SPECTRUM,
    "p2a41_2.rom",
)
SPECTRUM_PLUS2A_3_ROM = KnownFile(
    "65f031caa8148a5493afe42c41f4929deab26b4e",
    PLATFORM_ID_SPECTRUM,
    "p2a41_3.rom",
)

SPECTRUM_PLUS3_0_ROM = KnownFile(
    "e319ed08b4d53a5e421a75ea00ea02039ba6555b",
    PLATFORM_ID_SPECTRUM,
    "plus3-0.rom",
)
SPECTRUM_PLUS3_1_ROM = KnownFile(
    "c9969fc36095a59787554026a9adc3b87678c794",
    PLATFORM_ID_SPECTRUM,
    "plus3-1.rom",
)
SPECTRUM_PLUS3_2_ROM = KnownFile(
    "22e50c6ba4157a3f6a821bd9937cd26e292775c6",
    PLATFORM_ID_SPECTRUM,
    "plus3-2.rom",
)
SPECTRUM_PLUS3_3_ROM = KnownFile(
    "65f031caa8148a5493afe42c41f4929deab26b4e",
    PLATFORM_ID_SPECTRUM,
    "plus3-3.rom",
)

SPECTRUM_KEMPSTON_JOYSTICK_TYPE = "kempston"
SPECTRUM_KEMPSTON_JOYSTICK = {
    "type": SPECTRUM_KEMPSTON_JOYSTICK_TYPE,
    "description": "Kempston Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
SPECTRUM_SINCLAIR_JOYSTICK_TYPE = "sinclair"
SPECTRUM_SINCLAIR_JOYSTICK = {
    "type": SPECTRUM_SINCLAIR_JOYSTICK_TYPE,
    "description": "Sinclair Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
SPECTRUM_CURSOR_JOYSTICK_TYPE = "cursor"
SPECTRUM_CURSOR_JOYSTICK = {
    "type": SPECTRUM_CURSOR_JOYSTICK_TYPE,
    "description": "Sinclair Joystick",
    "mapping_name": "zx-spectrum-joystick",
}
NO_CONTROLLER_TYPE = "none"
NO_CONTROLLER = {
    "type": NO_CONTROLLER_TYPE,
    "description": "None",
    "mapping_name": "",
}
SPECTRUM_PORTS = [
    {
        "description": "Joystick Port 1",
        "types": [
            NO_CONTROLLER,
            SPECTRUM_KEMPSTON_JOYSTICK,
            SPECTRUM_SINCLAIR_JOYSTICK,
            SPECTRUM_CURSOR_JOYSTICK,
        ],
        "type_option": "spectrum_port_1_type",
        "device_option": "spectrum_port_1",
    },
    {
        "description": "Joystick Port 2",
        "types": [NO_CONTROLLER, SPECTRUM_SINCLAIR_JOYSTICK],
        "type_option": "spectrum_port_2_type",
        "device_option": "spectrum_port_2",
    },
]

from fsgamesys.platforms.spectrum.spectrumplatform import SpectrumPlatform
