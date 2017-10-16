from fsgs.drivers.messdriver import MessDriver


class MessA7800Driver(MessDriver):
    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "atari7800",
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

    def prepare(self):
        super().prepare()
        # self.emulator.args.extend(
        #     ["-lightgun", "-lightgun_device", "mouse"])

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, port):
        return {
            "START": "P#_START",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
        }

    def mess_romset(self):
        if self.is_pal():
            return "a7800p", A7800P_ROMS
        else:
            return "a7800", A7800_ROMS


# noinspection SpellCheckingInspection
A7800_ROMS = {
    "d9d134bb6b36907c615a594cc7688f7bfcef5b43": "7800.u7",
    "14584b1eafe9721804782d4b1ac3a4a7313e455f": "c300558-001a.u7",
}

# noinspection SpellCheckingInspection
A7800P_ROMS = {
    "5a140136a16d1d83e4ff32a19409ca376a8df874": "7800pal.rom",
}
