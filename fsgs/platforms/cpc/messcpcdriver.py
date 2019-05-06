from fsgs.drivers.messdriver import MessDriver


class MessCpcDriver(MessDriver):
    CONTROLLER = {
        "type": "controller",
        "description": "Controller",
        "mapping_name": "cpc",
    }

    PORTS = [
        {"description": "1st Controller", "types": [CONTROLLER]},
        {"description": "2nd Controller", "types": [CONTROLLER]},
    ]

    def mess_configure(self):
        self.mess_configure_floppies(["flop1", "flop2"])
        if self.config["command"]:
            # pass
            # self.inject_fake_input_string(60, "{0}\n".format(
            #     self.config["command"]))
            # self.args.extend(["-autoboot_delay", ""])
            self.args.extend(
                ["-autoboot_command", self.config["command"] + r"\n"]
            )

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
        model = self.config["model"].lower()
        if model in ["6128", "cpc6128"]:
            return "cpc6128", CPC6128_ROMS
        elif model in ["664", "cpc664"]:
            return "cpc664", CPC664_ROMS
        elif model in ["464", "cpc464", ""]:
            return "cpc464", CPC464_ROMS
        raise Exception("Unexpected CPC model " + repr(model))


# noinspection SpellCheckingInspection
CPC464_ROMS = {
    "56d39c463da60968d93e58b4ba0e675829412a20": "cpc464.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}

# noinspection SpellCheckingInspection
CPC664_ROMS = {
    "073a7665527b5bd8a148747a3947dbd3328682c8": "cpc664.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}

# noinspection SpellCheckingInspection
CPC6128_ROMS = {
    "5977adbad3f7c1e0e082cd02fe76a700d9860c30": "cpc6128.rom",
    "39102c8e9cb55fcc0b9b62098780ed4a3cb6a4bb": "cpcados.rom",
}
