import json
import os

from fsbc.paths import Paths
from fsgs.Archive import Archive
from fsgs.mednafen.mednafen import MednafenRunner
from fsgs.platforms.psx import PSX_CONTROLLER, PSX_SCPH5501_BIN_SHA1


class MednafenPlayStationDriver(MednafenRunner):
    PORTS = [
        {
            "description": "1st Controller",
            "types": [PSX_CONTROLLER]
        }, {
            "description": "2nd Controller",
            "types": [PSX_CONTROLLER]
        },
    ]

    def __init__(self, fsgs):
        super().__init__(fsgs)

    @staticmethod
    def expand_default_path(src, default_dir):
        if "://" in src:
            return src, None
        src = Paths.expand_path(src, default_dir)
        archive = Archive(src)
        return src, archive

    def get_game_file(self, config_key=None):

        # FIXME: Move somewhere else
        bios_path = os.path.join(self.home.path, ".mednafen", "scph5501.bin")
        if not os.path.exists(os.path.dirname(bios_path)):
            os.makedirs(os.path.dirname(bios_path))
        # FIXME: This is for US region
        src = self.fsgs.file.find_by_sha1(PSX_SCPH5501_BIN_SHA1)
        self.fsgs.file.copy_game_file(src, bios_path)

        temp_dir = self.temp_dir("media").path
        game_file = None
        # cdrom_drive_0 = self.config.get("cdrom_drive_0", "")
        # if cdrom_drive_0.startswith("game:"):
        if True:
            # scheme, dummy, game_uuid, name = cdrom_drive_0.split("/")
            # file_list = self.get_file_list_for_game_uuid(game_uuid)
            file_list = json.loads(self.config["file_list"])
            for file_item in file_list:
                src = self.fsgs.file.find_by_sha1(file_item["sha1"])

                src, archive = self.expand_default_path(src, None)
                dst_name = file_item["name"]
                # current_task.set_progress(dst_name)

                dst = os.path.join(temp_dir, dst_name)
                self.fsgs.file.copy_game_file(src, dst)

            # cue_sheets = self.get_cue_sheets_for_game_uuid(game_uuid)
            cue_sheets = json.loads(self.config["cue_sheets"])
            for i, cue_sheet in enumerate(cue_sheets):
                # FIXME: Try to get this to work with the PyCharm type checker
                path = os.path.join(temp_dir, cue_sheet["name"])
                if i == 0:
                    game_file = path
                # noinspection PyTypeChecker
                with open(path, "wb") as f:
                    # noinspection PyTypeChecker
                    f.write(cue_sheet["data"].encode("UTF-8"))
        return game_file

    def mednafen_input_mapping(self, port):
        if port == 0:
            return {
                "CIRCLE": "psx.input.port1.gamepad.circle",
                "CROSS": "psx.input.port1.gamepad.cross",
                "TRIANGLE": "psx.input.port1.gamepad.triangle",
                "SQUARE": "psx.input.port1.gamepad.square",
                "L1": "psx.input.port1.gamepad.l1",
                "L2": "psx.input.port1.gamepad.l2",
                "R1": "psx.input.port1.gamepad.r1",
                "R2": "psx.input.port1.gamepad.r2",
                "UP": "psx.input.port1.gamepad.up",
                "DOWN": "psx.input.port1.gamepad.down",
                "LEFT": "psx.input.port1.gamepad.left",
                "RIGHT": "psx.input.port1.gamepad.right",
                "SELECT": "psx.input.port1.gamepad.select",
                "START": "psx.input.port1.gamepad.start",
            }
        elif port == 1:
            return {
                "CIRCLE": "psx.input.port2.gamepad.circle",
                "CROSS": "psx.input.port2.gamepad.cross",
                "TRIANGLE": "psx.input.port2.gamepad.triangle",
                "SQUARE": "psx.input.port2.gamepad.square",
                "L1": "psx.input.port2.gamepad.l1",
                "L2": "psx.input.port2.gamepad.l2",
                "R1": "psx.input.port2.gamepad.r1",
                "R2": "psx.input.port2.gamepad.r2",
                "UP": "psx.input.port2.gamepad.up",
                "DOWN": "psx.input.port2.gamepad.down",
                "LEFT": "psx.input.port2.gamepad.left",
                "RIGHT": "psx.input.port2.gamepad.right",
                "SELECT": "psx.input.port2.gamepad.select",
                "START": "psx.input.port2.gamepad.start",
            }

    def mednafen_system_prefix(self):
        return "psx"

    # def mednafen_video_size(self):
    #     # FIXME
    #     if self.is_pal():
    #         size = (320, 240)
    #     else:
    #         size = (320, 224)
    #     return size
