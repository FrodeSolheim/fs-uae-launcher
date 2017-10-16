import filecmp
import os

import shutil

from fsgs.drivers.messdriver import MessDriver
from fsgs.knownfiles import KnownFile
from fsgs.platform import Platform
from fsgs.platforms.loader import SimpleLoader
from fsgs.plugins.plugin_manager import PluginManager

# noinspection SpellCheckingInspection
A5200_ROM = KnownFile(
    "6ad7a1e8c9fad486fbec9498cb48bf5bc3adc530", "A5200", "5200.rom")
# noinspection SpellCheckingInspection
A5200_ROM_ALT = KnownFile(
    "1d2a3f00109d75d2d79fecb565775eb95b7d04d5", "A5200", "5200a.rom")
A5200_CONTROLLER = {
    "type": "controller",
    "description": "Controller",
    "mapping_name": "atari5200",
}


class Atari5200PlatformHandler(Platform):
    PLATFORM_ID = "A5200"
    PLATFORM_NAME = "Atari 5200"

    def driver(self, fsgs):
        return Atari5200MessDriver(fsgs)

    def loader(self, fsgs):
        return Atari5200Loader(fsgs)


class Atari5200Loader(SimpleLoader):
    pass


class Atari5200MessDriver(MessDriver):
    PORTS = [
        {
            "description": "Input Port 1",
            "types": [A5200_CONTROLLER]
        }, {
            "description": "Input Port 2",
            "types": [A5200_CONTROLLER]
        },
    ]

    def prepare(self):
        super().prepare()
        self.install_mame_hash_file("a5200.hsi")
        self.install_mame_hash_file("a5200.xml")

    def get_game_refresh_rate(self):
        # There were no PAL version of Atari 5200
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
        return "a5200", {
            A5200_ROM.sha1: "5200.rom",
            A5200_ROM_ALT.sha1: "5200a.rom",
        }
