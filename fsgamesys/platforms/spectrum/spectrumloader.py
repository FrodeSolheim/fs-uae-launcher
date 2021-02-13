import json
import os

from fsgamesys.options.option import Option
from fsgamesys.platforms.loader import SimpleLoader
from fsgamesys.platforms.spectrum import SPECTRUM_MODEL_48K


class SpectrumLoader(SimpleLoader):
    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        if len(file_list) == 0:
            self.config["x_variant_error"] = "Variant has empty file list"
        elif len(file_list) > 1:
            self.config["x_variant_error"] = "Unsupported multi-file variant"

        name = file_list[0]["name"]
        sha1 = file_list[0]["sha1"]
        _, ext = os.path.splitext(name)
        ext = ext.lower()
        if ext in [".z80"]:
            key = Option.SNAPSHOT_FILE
        elif ext in [".tap", ".tzx"]:
            key = Option.TAPE_DRIVE_0
        elif ext in [".dsk", ".trd"]:
            key = Option.FLOPPY_DRIVE_0
        elif ext in [".rom"]:
            key = Option.CARTRIDGE_SLOT
        else:
            return
        self.config[key] = "sha1://{0}/{1}".format(sha1, name)

    def load_extra(self, values):
        print(values)

        model = values["spectrum_model"]

        # FIXME: Remove legacy option
        if not model:
            model = values["zxs_model"]
        if not model:
            model = values["model"]
        self.config["model"] = ""

        if not model:
            model = SPECTRUM_MODEL_48K
        if model == "+2":
            model = "plus2"
        elif model == "+2a":
            model = "plus2a"
        elif model == "+3":
            model = "plus3"

        # # Aliases
        # elif model == "128":
        #     model = ZXS_MODEL_128
        # elif model == "+2":
        #     model = ZXS_MODEL_PLUS2
        # elif model == "+2A" or model == "+2a":
        #     model = ZXS_MODEL_PLUS2A
        # elif model == "+3":
        #     model = ZXS_MODEL_PLUS3
        # else:
        #     model = ZXS_MODEL_48K

        self.config[Option.SPECTRUM_MODEL] = model

        # Overriding from zxs to spectrum!
        self.config["platform"] = "spectrum"

        self.load_port_config(values, "spectrum_port_1")
        self.load_port_config(values, "spectrum_port_2")

    def load_port_config(self, values, prefix):
        for key, value in values.items():
            if key.startswith(prefix):
                self.config[key] = value
