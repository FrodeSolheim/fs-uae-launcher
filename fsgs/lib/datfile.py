import io
import os
import sys
import xml.etree.cElementTree as ElementTree
from typing import Any, List, Optional, TextIO, TypedDict, Union, cast
from xml.etree.ElementTree import Element


class DatFileFile(TypedDict):
    name: str
    size: int
    crc32: Optional[str]
    md5: Optional[str]
    sha1: Optional[str]


class DatFileGame(TypedDict):
    name: str
    files: List[DatFileFile]


class DatFile(object):
    def __init__(self, file: Optional[Union[str, TextIO]] = None):
        self.games: List[DatFileGame] = []
        self.description = ""

        self.extensions: List[str] = []
        if file is not None:
            self.load(file)

    def reset(self):
        self.games = []
        self.description = ""

    def load(self, file: Union[str, TextIO]):
        if hasattr(file, "read"):
            self._load_file(cast(TextIO, file))
        else:
            self._load_path(cast(str, file))

    def _load_path(self, path: str):
        with io.open(path, "r", encoding="UTF-8") as f:
            self._load_file(f)

    def _load_file(self, f: TextIO):
        self.load_data(f.read())

    def load_data(self, data: str):
        if data.startswith("<") or data.startswith("\uFEFF"):
            # assume XML
            self._load_xml(data)
        else:
            self._load_dat(data)

    def _add_game_rom(self, game: DatFileGame, rom_node: Any):
        if rom_node.attrib.get("status", "") == "nodump":
            print("WARINING: status=nodump")
            return
        if "size" not in rom_node.attrib:
            print("WARNING: No size in", rom_node.attrib, file=sys.stderr)
            return
        if rom_node.attrib["size"] == "":
            print("WARNING: No size in", rom_node.attrib, file=sys.stderr)
            return
        rom: DatFileFile = {
            "name": rom_node.attrib["name"],
            "size": int(rom_node.attrib["size"]),
            "crc32": None,
            "md5": None,
            "sha1": None,
        }
        if "crc" in rom_node.attrib:
            rom["crc32"] = rom_node.attrib["crc"].lower()
        elif rom["size"] == 0:
            rom["crc32"] = "00000000"
        if "md5" in rom_node.attrib:
            rom["md5"] = rom_node.attrib["md5"].lower()
        elif rom["size"] == 0:
            rom["md5"] = "d41d8cd98f00b204e9800998ecf8427e"
        if "sha1" in rom_node.attrib:
            rom["sha1"] = rom_node.attrib["sha1"].lower()
        elif rom["size"] == 0:
            rom["sha1"] = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        game["files"].append(rom)

    def _add_game(self, node: Element):
        game: DatFileGame = {"name": node.attrib["name"], "files": []}
        for rom_node in node.findall("rom"):
            self._add_game_rom(game, rom_node)
        self.games.append(game)

    def _load_mame(self, root: Element):
        for machine_node in root.findall("machine"):
            self._add_game(machine_node)

    def _load_software_list(self, root: Element):
        for softwarelist_node in root.findall("softwarelist"):
            # FIXME: software list name
            for software_node in softwarelist_node.findall("software"):
                # FIXME: software list name + software name?
                name = software_node.attrib["name"]
                game: DatFileGame = {"name": name, "files": []}
                for rom_node in software_node.iter("rom"):
                    if rom_node.attrib.get("name", ""):
                        self._add_game_rom(game, rom_node)
                self.games.append(game)

    def _load_xml(self, data: str):
        self.reset()

        root = ElementTree.fromstring(data)
        if root.tag == "mame":
            return self._load_mame(root)
        if root.tag == "datafile" and root.find("machine") is not None:
            return self._load_mame(root)
        if root.tag == "softwarelists":
            return self._load_software_list(root)

        header_node = root.find("header")
        if header_node is None:
            raise Exception("header not not found in dat XML")
        description_node = header_node.find("description")
        if description_node is not None:
            self.description = (description_node.text or "").strip()
        for game_node in root.findall("game"):
            self._add_game(game_node)

    def _load_dat(self, data: str):
        self.reset()

        # this is a very quick-and-dirty/hackish parser...
        game: DatFileGame = {"name": "", "files": []}
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
                parts = line.split('"')
                rom_name: str
                if len(parts) == 3:
                    rom_name = parts[1]
                else:
                    parts = line.split(" ")
                    rom_name = parts[3]

                _, ext = os.path.splitext(rom_name)
                if self.extensions and ext.lower() not in self.extensions:
                    continue
                parts = line.split(" size ")
                rom_size = int(parts[1].strip().split(" ")[0].strip())
                parts = line.split(" crc ")
                rom_crc32 = parts[1].strip().split(" ")[0].strip().lower()
                parts = line.split(" md5 ")
                rom_md5 = parts[1].strip().split(" ")[0].strip().lower()
                parts = line.split(" sha1 ")
                rom_sha1: Optional[str]
                if len(parts) > 1:
                    rom_sha1 = parts[1].strip().split(" ")[0].strip().lower()
                else:
                    rom_sha1 = None
                game["files"].append(
                    {
                        "name": rom_name,
                        "size": rom_size,
                        "crc32": rom_crc32,
                        "md5": rom_md5,
                        "sha1": rom_sha1,
                    }
                )
