from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


from .mess import MESSRunner


class AmstradCPCRunner(MESSRunner):

    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "amstradcpc",
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
        self.mess_configure_floppies(["floppydisk1", "floppydisk2"])
        if self.config["command"]:
            pass
            self.inject_fake_input_string(60, "{0}\n".format(
                self.config["command"]))
            #self.inject_fake_input_string(60, "aaaaaaaaaaaaaaaaa")

    def mess_full_keyboard(self):
        return True

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
        return 50.080128

    def mess_romset(self):
        return "cpc464", CPC464_ROMS


CPC464_ROMS = {
    "56d39c463da60968d93e58b4ba0e675829412a20": "cpc464.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}
