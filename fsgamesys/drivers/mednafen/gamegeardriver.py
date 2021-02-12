from fsgamesys.drivers.mednafendriver import MednafenDriver


class MednafenGameGearDriver(MednafenDriver):
    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gamegear",
    }

    PORTS = [{"description": "Controller", "types": [CONTROLLER]}]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def mednafen_system_prefix(self):
        return "gg"

    def mednafen_input_mapping(self, _):
        return {
            "1": "gg.input.builtin.gamepad.button1",
            "2": "gg.input.builtin.gamepad.button2",
            "UP": "gg.input.builtin.gamepad.up",
            "DOWN": "gg.input.builtin.gamepad.down",
            "LEFT": "gg.input.builtin.gamepad.left",
            "RIGHT": "gg.input.builtin.gamepad.right",
            "START": "gg.input.builtin.gamepad.start",
        }
