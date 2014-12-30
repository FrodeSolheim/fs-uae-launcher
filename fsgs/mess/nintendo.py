from .mess import MESSRunner


class NintendoRunner(MESSRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "nintendo",
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

    def mess_input_mapping(self, _):
        return {
            "START": "P#_START",
            "SELECT": "P#_SELECT",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "A": "P#_BUTTON2",
            "B": "P#_BUTTON1",
        }

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_offset_and_scale(self):
        #if self.get_romset() == "nespal":
        #    return 0.0, 0.0, 1.082, 1.250
        #return 0.0, 0.0, 1.072, 1.164
        return 0.0, 0.0, 1.072, 1.100

    def mess_romset(self):
        if self.get_game_refresh_rate() == 50:
            return "nespal", {}
        else:
            return "nes", {}
