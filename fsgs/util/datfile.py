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
        if data.startswith("<") or data.startswith("\uFEFF"):
            # assume XML
            self._load_xml(data)
        else:
            self._load_dat(data)

    def _add_game(self, node):
        game = {"name": node.attrib["name"], "files": []}
        for rom_node in node.findall("rom"):
            rom = {
                "name": rom_node.attrib["name"],
                "size": int(rom_node.attrib["size"]),
            }
            if "crc" in rom_node.attrib:
                rom["crc32"] = rom_node.attrib["crc"].lower()
            if "md5" in rom_node.attrib:
                rom["md5"] = rom_node.attrib["md5"].lower()
            if "sha1" in rom_node.attrib:
                rom["sha1"] = rom_node.attrib["sha1"].lower()
            game["files"].append(rom)
        self.games.append(game)

    def _load_mame(self, root):
        for machine_node in root.findall("machine"):
            self._add_game(machine_node)

    def _load_xml(self, data):
        self.reset()

        root = ElementTree.fromstring(data)
        if root.tag == "mame":
            return self._load_mame(root)
        header_node = root.find("header")
        description_node = header_node.find("description")
        if description_node is not None:
            self.description = description_node.text.strip()
        for game_node in root.findall("game"):
            self._add_game(game_node)

    def _load_dat(self, data):
        self.reset()

        # this is a very quick-and-dirty/hackish parser...
        game = None
        for line in data.split("\n"):
            line = line.strip()
            if line.startswith("game ("):
                game = {"name": "", "files": []}
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
                    parts = line.split(" ")
                    rom["name"] = parts[3]
                n, ext = os.path.splitext(rom["name"])
                if self.extensions and ext.lower() not in self.extensions:
                    continue
                parts = line.split(" size ")
                rom["size"] = int(parts[1].strip().split(" ")[0].strip())
                parts = line.split(" crc ")
                rom["crc32"] = parts[1].strip().split(" ")[0].strip().lower()
                parts = line.split(" md5 ")
                rom["md5"] = parts[1].strip().split(" ")[0].strip().lower()
                parts = line.split(" sha1 ")
                rom["sha1"] = parts[1].strip().split(" ")[0].strip().lower()
                game["files"].append(rom)
