from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


from .mess import MESSRunner


class Atari2600Runner(MESSRunner):

    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "atari2600",
    }

    PORTS = [
        {
            "description": "1st Controller",
            "types": [CONTROLLER]
        }, {
            "description": "2nd Controller",
            "types": [CONTROLLER]
        },
    ]

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, port):
        return {
            "SELECT": 'tag=":SWB" type="OTHER" mask="2" defvalue="2"',
            "RESET": 'tag=":SWB" type="OTHER" mask="1" defvalue="1"',
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
            "3": "P#_BUTTON3",
        }

    def mess_romset(self):
        if self.is_pal():
            return "a2600p", {}
        else:
            return "a2600", {}
