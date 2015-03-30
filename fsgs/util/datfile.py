from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import xml.etree.cElementTree as ElementTree


class DatFile(object):
    
    def __init__(self, file=None):
        self.games = []
        self.description = ""

        self.extensions = []
        if file is not None:
            self.load(file)

    def reset(self):
        self.games = []
        self.description = ""

    def load(self, file):
        if hasattr(file, "read"):
            self._load_file(file)
        else:
            self._load_path(file)

    def _load_path(self, path):
        with io.open(path, "r", encoding="UTF-8") as f:
            self._load_file(f)

    def _load_file(self, f):
        self.load_data(f.read())

    def load_data(self, data):
        if data.startswith("<"):
            # assume XML
            self._load_xml(data)
        else:
            self._load_dat(data)

    def _load_xml(self, data):
        self.reset()

        root = ElementTree.fromstring(data)
        header_node = root.find("header")
        self.description = header_node.find("description").text.strip()
        for game_node in root.findall("game"):
            game = {
                "name": game_node.attrib["name"],
                "files": [],
            }
            for rom_node in game_node.findall("rom"):
                rom = {"name": rom_node.attrib["name"],
                       "size": int(rom_node.attrib["size"]),
                       "crc32": rom_node.attrib["crc"],
                       "md5": rom_node.attrib["md5"],
                       "sha1": rom_node.attrib["sha1"]}
                game["files"].append(rom)
            self.games.append(game)

    def _load_dat(self, data):
        self.reset()

        # this is a very quick-and-dirty/hackish parser...
        game = None
        for line in data.split("\n"):
            line = line.strip()
            if line.startswith("game ("):
                game = {
                    "name": "",
                    "files": [],
                }
                self.games.append(game)
            if line.startswith("name "):
                if game is not None:
                    if '"' in line:
                        parts = line.split('"')
                        assert len(parts) == 3
                        game["name"] = parts[1]
                    else:
                        game["name"] = line[5:]
            elif line.startswith("description "):
                if game is None:
                    parts = line.split('"')
                    assert len(parts) == 3
                    self.description = parts[1]
            elif line.startswith("rom ("):
                rom = {}
                parts = line.split('"')
                if len(parts) == 3:
                    rom["name"] = parts[1]
                else:
                    parts = line.split(' ')
                    rom["name"] = parts[3]
                n, ext = os.path.splitext(rom["name"])
                if self.extensions and ext.lower() not in self.extensions:
                    continue
                parts = line.split(" size ")
                rom["size"] = int(parts[1].strip().split(" ")[0].strip())
                parts = line.split(" crc ")
                rom["crc32"] = parts[1].strip().split(" ")[0].strip()
                parts = line.split(" md5 ")
                rom["md5"] = parts[1].strip().split(" ")[0].strip()
                parts = line.split(" sha1 ")
                rom["sha1"] = parts[1].strip().split(" ")[0].strip()
                game["files"].append(rom)
