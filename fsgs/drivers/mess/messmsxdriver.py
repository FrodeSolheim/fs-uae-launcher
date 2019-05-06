from fsgs.drivers.messdriver import MessDriver


class MessMsxDriver(MessDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "msx",
    }

    PORTS = [{"description": "1st Controller", "types": [CONTROLLER]}]

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
        # if self.is_pal():
        #     return "msx", {}
        # else:
        return "msx", {}
