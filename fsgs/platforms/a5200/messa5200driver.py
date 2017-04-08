from fsgs.drivers.messdriver import MessDriver


class MessA5200Driver(MessDriver):
    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "atari5200",
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

    def get_game_refresh_rate(self):
        # no PAL version of Atari 5200
        return 59.94

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, port):
        return {
            "START": 'type="P#_START"',
            "PAUSE": 'tag="keypad_2" type="KEYPAD" mask="1" defvalue="0"',
            "RESET": 'tag="keypad_1" type="KEYPAD" mask="1" defvalue="0"',
            "RIGHT": ('type="P#_AD_STICK_X"', 'increment'),
            "LEFT": ('type="P#_AD_STICK_X"', 'decrement'),
            "UP": ('type="P#_AD_STICK_Y"', 'decrement'),
            "DOWN": ('type="P#_AD_STICK_Y"', 'increment'),
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
            "PAD#": 'tag="keypad_0" type="KEYPAD" mask="2" defvalue="0"',
            "PAD0": 'tag="keypad_0" type="KEYPAD" mask="4" defvalue="0"',
            "PAD*": 'tag="keypad_0" type="KEYPAD" mask="8" defvalue="0"',
            "PAD9": 'tag="keypad_1" type="KEYPAD" mask="2" defvalue="0"',
            "PAD8": 'tag="keypad_1" type="KEYPAD" mask="4" defvalue="0"',
            "PAD7": 'tag="keypad_1" type="KEYPAD" mask="8" defvalue="0"',
            "PAD6": 'tag="keypad_2" type="KEYPAD" mask="2" defvalue="0"',
            "PAD5": 'tag="keypad_2" type="KEYPAD" mask="4" defvalue="0"',
            "PAD4": 'tag="keypad_2" type="KEYPAD" mask="8" defvalue="0"',
            "PAD3": 'tag="keypad_3" type="KEYPAD" mask="2" defvalue="0"',
            "PAD2": 'tag="keypad_3" type="KEYPAD" mask="4" defvalue="0"',
            "PAD1": 'tag="keypad_3" type="KEYPAD" mask="8" defvalue="0"',
        }

    def mess_romset(self):
        return "a5200", A5200_ROMS


# noinspection SpellCheckingInspection
A5200_ROMS = {
    "6ad7a1e8c9fad486fbec9498cb48bf5bc3adc530": "5200.rom",
    "1d2a3f00109d75d2d79fecb565775eb95b7d04d5": "5200a.rom",
}
