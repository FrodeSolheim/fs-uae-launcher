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

from fsgamesys.drivers.messdriver import MessDriver
from fsgamesys.options.option import Option
from fsgamesys.platforms.cpc.cpcconstants import (
    CPC_JOYSTICK_TYPE,
    CPC_MAME_ROMS_464,
    CPC_MAME_ROMS_664,
    CPC_MAME_ROMS_6128,
    CPC_PORTS,
)

# <port tag=":controller_type" type="CONFIG" mask="3" defvalue="0" value="1" />
# <port tag=":green_display" type="CONFIG" mask="1" defvalue="0" value="1" />
# <port tag=":solder_links" type="CONFIG" mask="7" defvalue="7" value="6" />
# <port tag=":solder_links" type="CONFIG" mask="16" defvalue="16" value="0" />


class CpcMameDriver(MessDriver):
    PORTS = CPC_PORTS

    def __init__(self, fsgc, fsemu=False):
        super().__init__(fsgc, fsemu=fsemu)

    def mess_configure(self):
        self.mess_configure_floppies(["flop1", "flop2"])
        if self.use_auto_load() and self.config[Option.COMMAND]:
            # self.inject_fake_input_string(60, "{0}\n".format(
            #     self.config["command"]))

            # We need to wait a bit; otherwise the command is entered before
            # basic prompt is ready, cutting of the first part of the command.
            self.args.extend(["-autoboot_delay", "1"])
            self.args.extend(
                ["-autoboot_command", self.config["command"] + r"\n"]
            )

    def configure_input(self):
        extra_port_config = []
        # CONFIG_2_BUTTON_JOYSTICK = 0
        # CONFIG_AMX_MOUSE_INTERFACE = 1
        # CONFIG_NOTHING = 2
        if self.ports[0].type == CPC_JOYSTICK_TYPE:
            controller_type = 0  # 2-button Joystick
        # elif self.ports[0].type == amx mouse interface ...
        #     controller_type = 1
        else:
            controller_type = 2  # Nothing
        green_display = 0  # CTM640 Colour Monitor
        manufacturer = 7  # Amstrad
        pal_refresh_rate = 1

        extra_port_config.append(
            '<port tag=":controller_type" type="CONFIG" mask="3" defvalue="0" value="{}" />\n'.format(
                controller_type
            )
        )
        extra_port_config.append(
            '<port tag=":green_display" type="CONFIG" mask="1" defvalue="0" value="{}" />\n'.format(
                green_display
            )
        )
        extra_port_config.append(
            '<port tag=":solder_links" type="CONFIG" mask="7" defvalue="7" value="{}" />\n'.format(
                manufacturer
            )
        )
        extra_port_config.append(
            '<port tag=":solder_links" type="CONFIG" mask="16" defvalue="16" value="{}" />\n'.format(
                16 if pal_refresh_rate else 0
            )
        )
        super().configure_input(extra_port_config=extra_port_config)

    # def mess_full_keyboard(self):
    #     return True

    def mess_input_mapping(self, port):
        return {
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
        }

    def get_game_refresh_rate(self):
        # PAL video according to MAME: 768 x 272 (H) 60.080128 Hz
        return 50.080128

    def mess_romset(self):
        model = self.config["cpc_model"].lower()
        if model == "6128":
            return "cpc6128", CPC_MAME_ROMS_6128
        elif model == "664":
            return "cpc664", CPC_MAME_ROMS_664
        elif model in ["464", ""]:
            return "cpc464", CPC_MAME_ROMS_464
        raise Exception("Unexpected CPC model " + repr(model))


class CpcMameFsDriver(CpcMameDriver):
    def __init__(self, fsgc):
        super().__init__(fsgc, fsemu=True)
