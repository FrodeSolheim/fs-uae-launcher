from fsgs.drivers.messdriver import MessDriver


class MessSmsDriver(MessDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Gamepad",
        "mapping_name": "mastersystem",
    }

    PORTS = [
        {"description": "1st Controller", "types": [CONTROLLER]},
        {"description": "2nd Controller", "types": [CONTROLLER]},
    ]

    def mess_configure(self):
        self.mess_configure_cartridge()

    def mess_input_mapping(self, _):
        return {
            # "START": "P#_START",
            "UP": "P#_JOYSTICK_UP",
            "DOWN": "P#_JOYSTICK_DOWN",
            "LEFT": "P#_JOYSTICK_LEFT",
            "RIGHT": "P#_JOYSTICK_RIGHT",
            "1": "P#_BUTTON1",
            "2": "P#_BUTTON2",
        }

    def mess_offset_and_scale(self):
        if self.is_pal():
            return 0.0, 0.0, 1.082, 1.250
        return 0.0, 0.0, 1.082, 1.164

    def mess_romset(self):
        if self.is_pal():
            return "smspal", SMSPAL_ROMS
        else:
            return "sms", SMS_ROMS

    # def get_game_refresh_rate(self):
    #     # refresh rate retrieved from MESS
    #     return 59.922743


# noinspection SpellCheckingInspection
SMS_ROMS = {"3af7b66248d34eb26da40c92bf2fa4c73a46a051": "mpr-12808.ic2"}

# FIXME...
# noinspection SpellCheckingInspection
SMSPAL_ROMS = {
    "3af7b66248d34eb26da40c92bf2fa4c73a46a051": "mpr-12808.ic2",
    "6aca0e3dffe461ba1cb11a86cd4caf5b97e1b8df": "sonbios.rom",
}
