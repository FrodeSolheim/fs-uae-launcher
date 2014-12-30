from .mess import MESSRunner


class MegaDriveRunner(MESSRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "megadrive",
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

    # self.inputs.append(self.create_input(
    #         name='Controller {0}'.format(i + 1),
    #         type='megadrive',
    #         description='Gamepad'))

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, _):
        return {
            "START": "P#_START",
            "MODE": "P#_SELECT",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "A": "P#_BUTTON1",
            "B": "P#_BUTTON2",
            "C": "P#_BUTTON3",
            "X": "P#_BUTTON4",
            "Y": "P#_BUTTON5",
            "Z": "P#_BUTTON6",
        }

    def mess_romset(self):
        if self.is_pal():
            return "megadriv", {}
        else:
            return "genesis", {}

    # def mess_get_firmware_name(self):
    #     return None
