from fsgs.mednafen.mednafen import MednafenRunner


class GameBoyRunner(MednafenRunner):

    CONTROLLER = {
        "type": "gamepad",
        "description": "Built-in Controller",
        "mapping_name": "gameboy",
    }

    PORTS = [
        {
            "description": "Controller",
            "types": [CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    def get_game_refresh_rate(self):
        return 59.73

    def mednafen_input_mapping(self, port):
        return {
            "A": "gb.input.builtin.gamepad.a",
            "B": "gb.input.builtin.gamepad.b",
            "UP": "gb.input.builtin.gamepad.up",
            "DOWN": "gb.input.builtin.gamepad.down",
            "LEFT": "gb.input.builtin.gamepad.left",
            "RIGHT": "gb.input.builtin.gamepad.right",
            "SELECT": "gb.input.builtin.gamepad.select",
            "START": "gb.input.builtin.gamepad.start",
        }

    def mednafen_rom_extensions(self):
        return [".gb"]

    def mednafen_scanlines_setting(self):
        return 0

    def mednafen_special_filter(self):
        return "nn2x"

    def mednafen_system_prefix(self):
        return "gb"

    # def mednafen_video_size(self):
    #     return 160, 144
